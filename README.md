# Panoptic Segmentation Training on Custom Datasets Using Detectron2

This repo contains code for applying Panoptic Segmentation to a custom dataset.
The specific dataset used in this repo (to build the labels.py file) is RUGD (http://rugd.vision/)

## Dataset Requirements
The dataset must have images and their annotations in colormap format. See example below.
![RUGD image & its colormap](https://github.com/HAadams/Offroad-Panoptic-Segmentation/blob/main/images/dataset_example.png)

---
**NOTE**
Change the labels.py file (add your own labels names, and change which labels are instances (hasInstance field). Do not modify the void label.)
---

  - `createInstances.py` is used to create the instance segmentation json annotations based on labels.py for RUGD according to the COCO format. It is also used to generate the categories.json file. This file is used to genereate the semantic segmentaiton annotation png files.
  - `createPanopticAnnotations.py` is used to create panoptic segmentation json annotations and panoptic image annotations according to the COCO format.
  - `createPanopticInstanceIds.py` is used to create the instance ids images from colormap labels. This script takes a very long time (~5 seconds per 560x600 image) However, it supports parallel processing. Specify the number of processes through the `n_proc` variable. 



## Data Processing ([Colab Notebook](https://colab.research.google.com/drive/1TZ6lfKbDVObNq3uiBm-0mf_z1wlj8ryf?usp=sharing))

In order to trian a Panoptic Segmentation model using Detectron2, I needed to use the `register_coco_panoptic_separated` function to register the dataset. This method expects the following data.

1. Images dataset in JPG format.
2. Panoptic Segmentation Image Annotations (createPanopticAnnotations.py)
3. Panoptic Segmentaiton JSON Annotations (createPanopticAnnotations.py)
4. Semantic Segmentation Images Annotaitons (used panopticapi)
5. Instance Segmentation JSON Annotations (createInstances.py)


The dataset registeration can simply then be done throug the following code

```python

from detectron2.data.datasets import register_coco_panoptic_separated

register_coco_panoptic_separated(
    "RUGD_train", 
    {}, 
    "RUGD_dataset_conv/train", 
    "RUGD_labels/panoptic_train", 
    "RUGD_labels/annotations_train_panoptic.json", 
    "RUGD_labels/train_semantic", 
    "RUGD_labels/annotations_train_instances.json")

```

## Model Training ([Colab notebook](https://colab.research.google.com/drive/16IrjUv5Gn2RinPO1jGe33s6N-EHMeEgb?usp=sharing))


Here are the parameters used in the example link above. Make sure to change them to match your own needs. For example, the parameters below use 25 as the number of classes.

---
**NOTE**
Detectron2 appends `_separated`  to your dataset name registered through register_coco_panoptic_separated. So, make sure to add it like the example below.
---

# TODO: HUSSEIN update the readme with new info about label ids requirements, processing the dataset, training the model, and evaluation.

