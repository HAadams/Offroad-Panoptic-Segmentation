import time
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
import parallelbar

from labels import get_conflict_colormap


def _replace_label_colors(args: tuple) -> str:
    label_path, conflict_colormap = args
    label_path_str = str(label_path)

    image = cv2.imread(label_path_str)
    for input_color, output_color in conflict_colormap.items():
        image[np.all(image == input_color, axis=-1)] = output_color
    
    cv2.imwrite(label_path_str, image)
    return label_path_str


def convert_labels_to_rellis(labels_path: str, n_proc: int = 1):
    start = time.time()
    label_images = list(Path(labels_path).glob("**/*.png"))
    conflict_colormap = get_conflict_colormap()

    with Pool():
        results = parallelbar.progress_imap(
            func=_replace_label_colors,
            tasks=[(label_image, conflict_colormap) for label_image in label_images],
            n_cpu=n_proc,
            chunk_size=10,
        )
        print()
        print(f"{len(results)} files converted")

    end = time.time()
    print(f"TOOK {end - start} SECONDS!")
