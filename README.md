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

## Important Notes
Some notes about preprocessing the dataset that we needed to perform to get the model to train correctly.

### Labels IDs
Labels IDs need to be arranged in a way where things and stuff classes are separated clearly.
For example, if we have the following 4 thing classes, and 3 stuff classes:
```
Stuff: road, sky, barrier
Things: person, car, bike, sign
```
We have 7 classes + a void category for a total of 8 categories.
We found that the label IDs should be layed out as follows

```
ID      Category        Type
0        void           Stuff
1        road           Stuff
2        sky            Stuff
3        barrier        Stuff
4        person         Thing
5        car            Thing
6        bike           Thing
7        sign           Thing
```

This is because Detectron2 applies a label mapping for the instance/thing data, but not for the semantic/stuff data. This means that the thing classes (IDs 4, 5, 6, 7) will have ID mapping to (0, 1, 2, 3) automatically applied by Detectron2. However, this mapping is not applied to the stuff/semantic categories. The model will use whatever ID we provide it for stuff classes and attempt to access the respective neuron/unit in the semantic head layer. For example, road class with id=1, detectron2 might do something like semantic_head[1]. This makes it important to have the stuff classes to be the first n elements, and then the thing classes should appear after. Having the stuff classes appear first ensures a 0-n IDs which can map directly to the semantic head's layer size. This way, we're able to set the semantic head size directly to 4 and ensure that it doesn't try to access different labels. However, we'll need to set thing classes in the semantic images to some large number and tell the model to ignore it. We'll be doing thing/instance segmentation training in a separate head, so the semantic head can just ignore thing IDs. This ensures that the semantic head will not get a value outside of the 0-n IDs we provide it.

For example, when generating semantic segmentation images, the following script was used
```bash
!python panopticapi/converters/panoptic2semantic_segmentation.py \
--input_json_file RUGD_labels/annotations_val_panoptic.json \
--segmentations_folder RUGD_labels/val_panoptic/ \
--semantic_seg_folder RUGD_labels/val_semantic \
--categories_json_file RUGD_labels/categories.json \
--things_other \
```


This means the ROI (instance) head will have size 4 and the semantic head will have size 4 (3 stuff classes + void class)




We found that Detectron2 assigns ID mapping for instances. For example




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



