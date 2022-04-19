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
from shapely.geometry import Polygon
from skimage import measure

def generatePanopticImages(dataPath):

    categories = []
    dataPath = pathlib.Path(dataPath)

    annotations_file = dataPath.parent.joinpath(f'annotations_{dataPath.name}_instances.json')
    categories_file = dataPath.parent.joinpath(f'categories.json')

    seen = set([0])
    for label in labels:
        if label.categoryId in seen:
          continue
        seen.add(label.categoryId)
        categories.append({'id': int(label.categoryId),
                           'name': label.name,
                           'color': label.color,
                           'supercategory': label.category,
                           'isthing': 1 if label.hasInstances else 0})


    images = []
    annotations = []

    files = list(pathlib.Path(dataPath).glob("**/*_instanceIds.png"))
    annotId = 1
    imageId = 1
    for f in tqdm(files, desc="Generating Panoptic Images"):

        originalFormat = np.array(Image.open(f))

        inputFileName = f.name.replace("_instanceIds.png", ".png")
        imageId += 1

        # image entry, id for image is its filename without extension
        images.append({"id": imageId,
                        "width": int(originalFormat.shape[1]),
                        "height": int(originalFormat.shape[0]),
                        "file_name": inputFileName
                        })

        segmentIds = np.unique(originalFormat)

        for segmentId in segmentIds:
            if segmentId == 0:
              continue 
            labelId = segmentId
            if labelId > 1000:
                labelId = segmentId // 1000

            labelInfo = id2labels[labelId]

            if not labelInfo.hasInstances:
                continue

            isCrowd = 0
            categoryId = labelInfo.categoryId

            mask = originalFormat == segmentId

            contours = measure.find_contours(mask, 0.5, positive_orientation='low')
            segmentations = list()
            if labelInfo.hasInstances:
                for contour in contours:
                    # Flip from (row, col) representation to (x, y)
                    # and subtract the padding pixel
                    for i in range(len(contour)):
                        row, col = contour[i]
                        contour[i] = (col - 1, row - 1)

                    # Make a polygon and simplify it
                    poly = Polygon(contour)
                    poly = poly.simplify(1.0, preserve_topology=False)
                    if not isinstance(poly, Polygon):
                        seg = [np.array(x.exterior.coords).ravel().tolist() for x in poly.geoms]
                        segmentations.extend(seg)
                    else:
                        seg = np.array(poly.exterior.coords).ravel().tolist()
                        segmentations.append(seg)

            if len(segmentations) == 0:
                continue

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

            annotations.append({"id": annotId,
                                "image_id": imageId,
                                "category_id": int(categoryId),
                                "segmentation": segmentations,
                                "area": int(area),
                                "bbox": bbox,
                                "bbox_mode": 1, # XYWH_ABS=1 see https://detectron2.readthedocs.io/en/latest/modules/structures.html
                                "iscrowd": isCrowd})

            annotId += 1

    print("\nSaving the json file {}".format(annotations_file))

    d = {'images': images,
            'annotations': annotations,
            'categories': categories}

    with open(annotations_file, 'w') as f:
        json.dump(d, f, sort_keys=True, indent=4)

    with open(categories_file, 'w') as f:
        json.dump(categories, f, indent=4)


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
