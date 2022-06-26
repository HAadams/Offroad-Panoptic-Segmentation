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
import pathlib
import sys
import time

import cv2
import numpy as np
from PIL import Image
from tqdm.auto import tqdm

from labels import get_id2labels, get_labels


def generatePanopticImages(dataPath, is_rugd: bool = True):

    categories = []
    dataPath = pathlib.Path(dataPath)

    annotations_file = dataPath.parent.joinpath(f'annotations_{dataPath.name}_panoptic.json')
    outDir = dataPath.parent.joinpath(f"{dataPath.name}_panoptic")
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    for label in get_labels(is_rugd):
        categories.append({
            'id': int(label.id),
            'name': label.name,
            'color': label.color,
            'supercategory': label.category,
            'isthing': 1 if label.hasInstances else 0
        })

    images = []
    annotations = []
    id2labels = get_id2labels(is_rugd)

    files = list(pathlib.Path(dataPath).glob("**/*_instanceIds.png"))
    annotId = 0
    imageId = 0
    for f in tqdm(files, desc="Generating Panoptic Images"):
        originalFormat = np.array(cv2.imread(str(f), flags=-1), dtype=np.uint16)
        inputFileName = f.name.replace("_instanceIds.png", ".png")
        outputFilePath = str(outDir.joinpath(f.name.replace('_instanceIds.png', '.png')))

        # image entry, id for image is its filename without extension
        images.append({"id": imageId,
                        "width": int(originalFormat.shape[1]),
                        "height": int(originalFormat.shape[0]),
                        "file_name": inputFileName
                        })
        pan_format = np.zeros(
            (originalFormat.shape[0], originalFormat.shape[1], 3), dtype=np.uint8
        )

        segmentIds = np.unique(originalFormat)
        segmInfo = []
        for segmentId in segmentIds:
            if segmentId == 0:
              continue
            labelId = segmentId
            if labelId > 1000:
                labelId = segmentId // 1000

            labelInfo = id2labels[labelId]

            color = (segmentId % 256, segmentId // 256, segmentId // 256 // 256)                
            isCrowd = 0

            mask = originalFormat == segmentId
            pan_format[mask] = color

            area = np.sum(mask) # segment area computation

            # bbox computation for a segment
            hor = np.sum(mask, axis=0)
            hor_idx = np.nonzero(hor)[0]
            x = hor_idx[0]
            width = hor_idx[-1] - x + 1
            vert = np.sum(mask, axis=1)
            vert_idx = np.nonzero(vert)[0]
            y = vert_idx[0]
            height = vert_idx[-1] - y + 1
            bbox = [int(x), int(y), int(width), int(height)]

            segmInfo.append({"id": int(segmentId),
                                "category_id": int(labelInfo.id),
                                "area": int(area),
                                "bbox": bbox,
                                "bbox_mode": 1, # XYWH_ABS=1 see https://detectron2.readthedocs.io/en/latest/modules/structures.html
                                "iscrowd": isCrowd})

        annotations.append({'image_id': imageId,
                            'id': annotId,
                            'file_name': inputFileName,
                            'segments_info': segmInfo})
        annotId += 1
        imageId += 1
        Image.fromarray(pan_format).save(outputFilePath)

    print("\nSaving the json file {}".format(annotations_file))

    d = {'images': images,
            'annotations': annotations,
            'categories': categories}

    with open(annotations_file, 'w') as f:
        json.dump(d, f, sort_keys=True, indent=4)


def main(args):
    if len(args) < 1:
        print("Please pass directory path")
        exit()

    input_dir = args[0]

    is_rugd = True
    if len(args) > 1:
        if args[1] == "rellis":
            is_rugd = False

    start = time.time()

    generatePanopticImages(input_dir, is_rugd)

    end = time.time()
    print(f"TOOK {end-start} SECONDS!")


if __name__ == "__main__":
    main(sys.argv[1:])
