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

The reason for having the first n categories be stuff classes is because Detectron2 applies a label mapping for the instance/thing data, but not for the semantic/stuff data. This means that the thing classes (IDs 4, 5, 6, 7) will have ID mapping to (0, 1, 2, 3) automatically applied by Detectron2. The instance (ROI) head of the Panoptic FPN model can then know that the first index belongs to label 4, the second neuron/unit/index belongs to label 5...etc.

However, this mapping is not applied to the stuff/semantic categories. The model will use whatever ID we provide it for stuff classes and attempt to access the respective neuron/unit in the semantic head layer. For example, assuming road class has id=8, detectron2 might do something like semantic_head[8] which is incorrect if you only have 4 stuff classes. This makes it important to have the stuff classes to be the first n elements, and then the thing classes appear after. Having the stuff classes appear first ensures a 0-n IDs which can map directly to the semantic head's layer size AND the stuff classes label IDs. This way, we're able to set the semantic head size directly to 4 and ensure that it doesn't try to access different labels. 

Moreover, we'll need to set thing classes in the semantic images to some large number and tell the model to ignore it. We'll be doing thing/instance segmentation training in a separate head, so the semantic head can just ignore thing IDs. This ensures that the semantic head will not get a value outside of the 0-n IDs we provide it, and it will only have size=n where n=number of stuff classes.

For example, when generating semantic segmentation images, the following script was used
```bash
!python panopticapi/converters/panoptic2semantic_segmentation.py \
--input_json_file RUGD_labels/annotations_val_panoptic.json \
--segmentations_folder RUGD_labels/val_panoptic/ \
--semantic_seg_folder RUGD_labels/val_semantic \
--categories_json_file RUGD_labels/categories.json \
--things_other \
```
Note the --things_other keyword. This keyword tells the script to set all thing classes in the semantic image (which are defined in your categories.json file) to some number (183 as of August 5, 2022). The only valid numbers in the semantic images are then just the stuff classes IDs or 183.

Finally, when training the Panoptic FPN model, we have to tell the semantic head to ignore the --things_other label (183) set above. We can also set the ROI head size to the number of instances/things classes, and the semantic head size to the number of stuff classes + 1 (detectron2 ignores pixels with value 0)

```
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_50_1x_NO_WEIGHTS.yaml"))
cfg.DATASETS.TRAIN = (RUGD_train_separated,) 
cfg.DATASETS.TEST = ((RUGD_test_separated,))
cfg.DATALOADER.NUM_WORKERS = 2  # number of processes to load data
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_50_1x_NO_WEIGHTS.yaml")  # Let training initialize from model zoo for fine tuning
cfg.SOLVER.IMS_PER_BATCH = 6  # batch size, num of images trained at the same time
cfg.SOLVER.BASE_LR = 1e-3  # pick a good LR
cfg.SOLVER.MAX_ITER = 2000

# ignore things classes in semantic head
# when generating semantic images using panopticapi, use the --things_other argument
# it tells the converter script to set all things to 183 because they 
# are ignored in semantic training and evaluation
# and we tell the semantic segmentation head to ignore pixels in semantic images with value 183
cfg.MODEL.SEM_SEG_HEAD.IGNORE_VALUE = 183 

cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4
cfg.MODEL.SEM_SEG_HEAD.NUM_CLASSES = 4 # 3 stuff classes + 1 void class
```



### Dataset Registeration

The dataset registeration can simply be done through the following code. Note that detectron2 adds the _separated suffix to the name of your dataset (i.e. RUGD_train_separated)

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



