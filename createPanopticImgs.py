"""
This code is heavily inspired by the cityscapes script found in
https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/preparation/createPanopticImgs.py

Usage Example:
    python createPanopticImgs.py /path/to/images/folder/

This script will generate _panoptic.png images from _instanceIds.png images.
The generated _panoptic.png image is saved in teh same directory where _instanceIds.png lives.
Moreover, this script also generates an annotations JSON file in COCO format.
"""

from PIL import Image
from tqdm.auto import tqdm
from labels import labels, id2labels

import time
import sys
import pathlib
import numpy as np
import json
import os

def generatePanopticImages(dataPath):

    categories = []
    dataPath = pathlib.Path(dataPath)

    annotations_file = dataPath.parent.joinpath(f'annotations_{dataPath.name}_panoptic.json')
    outDir = dataPath.parent.joinpath(f"{dataPath.name}_panoptic")
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    
    for label in labels:
        if label.ignoreInEval:
            continue

        categories.append({'id': int(label.id),
                           'name': label.name,
                           'color': label.color,
                           'supercategory': label.category,
                           'isthing': 1 if label.hasInstances else 0})


    images = []
    annotations = []

    files = list(pathlib.Path(dataPath).glob("**/*_instanceIds.png"))

    for f in tqdm(files, desc="Generating Panoptic Images"):

        originalFormat = np.array(Image.open(f))

        imageId = f.name.replace("_instanceIds.png", "")
        inputFileName = f.name.replace("_instanceIds.png", ".png")
        inputFilePath = str(f).replace("_instanceIds.png", ".png")
        outputFilePath = str(outDir.joinpath(f.name.replace('_instanceIds.png', '_panoptic.png')))

        # image entry, id for image is its filename without extension
        images.append({"id": imageId,
                        "width": int(originalFormat.shape[1]),
                        "height": int(originalFormat.shape[0]),
                        "file_name": inputFileName})

        pan_format = np.zeros(
            (originalFormat.shape[0], originalFormat.shape[1], 3), dtype=np.uint8
        )

        segmentIds = np.unique(originalFormat)
        segmInfo = []
        for segmentId in segmentIds:
            
            labelId = segmentId
            if labelId > 1000:
                labelId = segmentId // 1000

            labelInfo = id2labels[labelId]

            if labelInfo.ignoreInEval:
                continue

            color = (segmentId % 256, segmentId // 256, segmentId // 256 // 256)                
            isCrowd = 0
            categoryId = labelInfo.id

            mask = originalFormat == segmentId
            # segmentation = list()
            # for i in range(mask.shape[0]):
            #     for j in range(mask.shape[1]):
            #         if mask[i][j]:
            #             segmentation.append(i)
            #             segmentation.append(j)

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
                                "category_id": int(categoryId),
                                "area": int(area),
                                "bbox": bbox,
                                "bbox_mode": 1, # XYWH_ABS=1 see https://detectron2.readthedocs.io/en/latest/modules/structures.html
                                # "segmentation": segmentation, # [x1, y1, x2, y2, ... , xn, yn] for each point in mask
                                "iscrowd": isCrowd})

        annotations.append({'image_id': imageId,
                            'file_name': inputFilePath,
                            'pan_seg_file_name': outputFilePath,
                            'segments_info': segmInfo})

        Image.fromarray(pan_format).save(outputFilePath)

    print("\nSaving the json file {}".format(annotations_file))

    d = {'images': images,
            'annotations': annotations,
            'categories': categories}

    with open(annotations_file, 'w') as f:
        json.dump(d, f, sort_keys=True, indent=4)


if __name__ == "__main__":


    args = sys.argv
    if len(args) < 2:
        print("Please pass directory path")
        exit()

    input_dir = args[1]

    start = time.time()

    generatePanopticImages(input_dir)

    end = time.time()
    print(f"TOOK {end-start} SECONDS!")
