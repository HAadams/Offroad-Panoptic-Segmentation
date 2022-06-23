"""

This script is used to generate instanceIds.png files for each colormap image according to the COCO format.
The instanceIds.png images are stored using 16bit percision (each pixel can have 16bit values)

This script will save the created instance id image in the same location as the input image.

Use this file in conjuction with labels.py to create instance id from image labels.
Usage Example
    python createInstanceImgs.py /content/RUGD-annotations

"""

import pathlib
import sys
import time
from collections import Counter
from multiprocessing import Pool

import cv2
import numpy as np
import parallelbar
from PIL import Image
from scipy.spatial.distance import cdist
from skimage.segmentation import flood_fill

from labels import get_color2labels, get_id2labels


def generateInstanceIds(image_array: np.ndarray, colors: np.ndarray, color_ids: np.ndarray, ids_to_labels) -> np.ndarray:
    # Initialize output array
    instance_ids = np.zeros((image_array.shape[0], image_array.shape[1]), dtype=np.int32)

    # Match colors to label ids
    R, C = np.where(cdist(image_array.reshape(-1, 3), colors) == 0)
    instance_ids.ravel()[R] = color_ids[C]

    # Make them negative (to determine which pixels have been visited)
    instance_ids = -instance_ids

    # Do flood fill to find instances
    segment_count = Counter()
    y_dim, x_dim = instance_ids.shape
    for x in range(x_dim):
        for y in range(y_dim):
            if instance_ids[y][x] < 0:
                label = ids_to_labels[-instance_ids[y][x]]
                if label.hasInstances:
                    # Keep track of unique instances
                    new_val = label.id * 1000 + segment_count[label.id]
                    segment_count[label.id] += 1
                else:
                    new_val = label.id
                flood_fill(instance_ids, (y, x), new_val, connectivity=1, in_place=True)
    
    return instance_ids.astype(np.uint16)


def target_process(args: tuple) -> str:
    image_path, colors, color_ids, ids_to_labels = args
    save_path = str(image_path).replace(".png", "") + "_instanceIds.png"
    image = np.array(Image.open(image_path))
    instance_image = generateInstanceIds(image, colors, color_ids, ids_to_labels)
    cv2.imwrite(save_path, instance_image)
    return save_path


def main(args):
    """
    We'll create N processes and delegate a portion of the images to each process.
    For example, if we have 10 images and 2 processes, this code will create two processes.
    Each process will be responsible for 5 separate images.
    """

    if len(args) < 1:
        print("Please pass directory path")
        exit()

    input_dir = args[0]

    is_rugd = True
    if len(args) > 1:
        if args[1] == "rellis":
            is_rugd = False

    n_proc = 2
    if len(args) > 2:
        try:
            n_proc = int(args[2])
        except:
            pass

    start = time.time()

    colormap_imgs = list(pathlib.Path(input_dir).glob("**/*.png"))
    label_imgs = []

    for file in colormap_imgs:
        if '_panoptic.png' in file.name:
            continue

        if '_instanceIds.png' in file.name:
            continue

        instance_path = pathlib.Path(str(file).replace('.png', '') + '_instanceIds.png')
        if not pathlib.Path.exists(instance_path):
            label_imgs.append(file)

    color2labels = get_color2labels(is_rugd)
    colors = np.array([k for k in color2labels.keys()])
    color_ids = np.array([v.id for v in color2labels.values()])
    ids_to_labels = get_id2labels(is_rugd)

    with Pool():
        results = parallelbar.progress_imap(
            func=target_process,
            tasks=[(label_image, colors, color_ids, ids_to_labels) for label_image in label_imgs],
            n_cpu=n_proc,
            chunk_size=10,
        )
        print(f"{len(results)} files generated")

    end = time.time()
    print(f"TOOK {end-start} SECONDS!")
    

if __name__ == "__main__":
    main(sys.argv[1:])
