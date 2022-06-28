"""
This code is heavily inspired by the cityscapes script found in
https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/preparation/createPanopticImgs.py

Usage Example:
    python createPanopticImgs.py /path/to/images/folder/

This script will generate _panoptic.png images from _instanceIds.png images.
The generated _panoptic.png image is saved in teh same directory where _instanceIds.png lives.
Moreover, this script also generates an annotations JSON file in COCO format.
"""

import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
import parallelbar
from PIL import Image

from labels import get_labels


def generate_panoptic_image(args) -> tuple:
    filepath, out_dir, index = args
    original_format = np.array(cv2.imread(str(filepath), flags=-1), dtype=np.uint16)
    input_filename = filepath.name.replace("_instanceIds.png", ".png")
    output_filepath = str(out_dir.joinpath(input_filename))

    y_dim, x_dim = original_format.shape[0:2]
    pan_format = np.zeros((y_dim, x_dim, 3), dtype=np.uint8)

    segment_ids = np.unique(original_format)
    segments_info = []
    for seg_id in segment_ids:
        if seg_id == 0:
            continue

        label_id = seg_id
        if label_id >= 1000:
            label_id //= 1000
        
        mask = original_format == seg_id
        new_color = (seg_id % 256, seg_id // 256, seg_id // 65536) # 65536 = 256^2
        pan_format[mask] = new_color

        # Segment area computation
        area = int(np.sum(mask))

        # Bounding-box computation
        horizontal = np.sum(mask, axis=0)
        horizontal_index = np.nonzero(horizontal)[0]
        x = horizontal_index[0]
        width = horizontal_index[-1] - x + 1

        vertical = np.sum(mask, axis=1)
        vertical_index = np.nonzero(vertical)[0]
        y = vertical_index[0]
        height = vertical_index[-1] - y + 1

        bbox = [int(x), int(y), int(width), int(height)]

        segments_info.append({
            "id": index,
            "category_id": int(label_id),
            "area": area,
            "bbox": bbox,
            "bbox_mode": 1, # XYWH_ABS=1 see https://detectron2.readthedocs.io/en/latest/modules/structures.html
            "iscrowd": 0
        })

    Image.fromarray(pan_format).save(output_filepath)
    
    image_entry = {
        "id": index,
        "width": x_dim,
        "height": y_dim,
        "file_name": input_filename,
    }
    annotation_entry = {
        "image_id": index,
        "id": index,
        "file_name": input_filename,
        "segments_info": segments_info,
    }

    return (image_entry, annotation_entry)


def generate_panoptic_images(input_dir: str, is_rugd: bool = True, n_proc: int = 1):
    # Generate Categories
    categories = []
    for label in get_labels(is_rugd):
        if label.id != 0:
            categories.append({
                'id': int(label.id),
                'name': label.name,
                'color': label.color,
                'supercategory': label.category,
                'isthing': 1 if label.hasInstances else 0
            })

    data_path = Path(input_dir)
    annotations_file = data_path.parent.joinpath(f'annotations_{data_path.name}_panoptic.json')
    out_dir = data_path.parent.joinpath(f"{data_path.name}_panoptic")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    else:
        print(f"Directory {str(out_dir)} already exists. Please delete and try again.")
        exit()

    input_files = list(Path(data_path).glob("**/*_instanceIds.png"))
    
    results = []
    with Pool():
        results = parallelbar.progress_imap(
            func=generate_panoptic_image,
            tasks=[(input_file, out_dir, index) for index, input_file in enumerate(input_files)],
            n_cpu=n_proc,
            chunk_size=1,
        )

    images, annotations = zip(*results)
    
    print("\nSaving the json file {}".format(annotations_file))
    annotation_data = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }
    with open(annotations_file, "w") as f:
        json.dump(annotation_data, f, sort_keys=True, indent=4)


def main(args):
    if len(args) < 1:
        print("Please pass directory path")
        exit()

    input_dir = args[0]

    is_rugd = True
    if len(args) > 1:
        if args[1] == "rellis":
            is_rugd = False

    n_proc = 1
    if len(args) > 2:
        try:
            n_proc = int(args[2])
        except:
            pass

    start = time.time()

    generate_panoptic_images(input_dir, is_rugd, n_proc)

    end = time.time()
    print(f"TOOK {end-start} SECONDS!")


if __name__ == "__main__":
    main(sys.argv[1:])
