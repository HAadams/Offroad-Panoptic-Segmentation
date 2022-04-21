# Panoptic Segmentation on Custom Datasets

This repo contains code for applying Panoptic Segmentation to a custom dataset.
The specific dataset used in this repo (to build the labels.py file) is RUGD (http://rugd.vision/)

    NOTE: Change the labels.py file (add your own labels names, and change which labels are instances (hasInstance field). Do not modify the void label.)


  - `createInstances.py` is used to create the instance segmentation json annotations based on labels.py for RUGD according to the COCO format. It is also used to generate the categories.json file. This file is used to genereate the semantic segmentaiton annotation png files.
  - `createPanopticAnnotations.py` is used to create panoptic segmentation json annotations and panoptic image annotations according to the COCO format.
  - `createPanopticInstanceIds.py` is used to create the instance ids images from colormap labels.


### Data Processing

In order to trian a Panoptic Segmentation model using Detectron2, I needed to use the `register_coco_panoptic_separated` function to register the dataset. This method expects the following data.

1. Images dataset in JPG format.
2. Panoptic Segmentation Image Annotations (createPanopticAnnotations.py)
3. Panoptic Segmentaiton JSON Annotations (createPanopticAnnotations.py)
4. Semantic Segmentation Images Annotaitons (used panopticapi)
5. Instance Segmentation JSON Annotations (createInstances.py)

An example of how each script was used on the RUGD dataset can be found here: [Data Preprocessing Colab Notebook](https://colab.research.google.com/drive/1tLUc4BVLRJPHlaa88c38XznxUrzY6ahq?usp=sharing)

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

### Model Training 

Use [This Colab notebook](https://colab.research.google.com/drive/1tLUc4BVLRJPHlaa88c38XznxUrzY6ahq?usp=sharing) for an example on how to train a Panoptic Segmentaiton model.

Here are the parameters used in the example link above. Make sure to change them to match your own needs. For example, the parameters below use 25 as the number of classes.

        NOTE: Detectron2 appends `_separated`  to your dataset name registered through register_coco_panoptic_separated. So, make sure to add it like the example below.

```python
cfg = get_cfg()
# cfg.MODEL.DEVICE='cpu' # Use CPU for debugging
cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_50_1x.yaml"))
cfg.DATASETS.TRAIN = ("RUGD_train_separated",) # detectron2 adds _separated to the  dataset name
cfg.DATASETS.TEST = (("RUGD_test_separated",))
cfg.DATALOADER.NUM_WORKERS = 2  # number of processes to load data
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_50_1x.yaml")  # Let training initialize from model zoo for fine tuning
cfg.SOLVER.IMS_PER_BATCH = 4  # batch size, num of images trained at the same time
cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
cfg.SOLVER.MAX_ITER = 30000
cfg.SOLVER.STEPS = []        # do not decay learning rate
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # faster, (default: 512)
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 25    # Number of Classes/Labels
cfg.MODEL.SEM_SEG_HEAD.NUM_CLASSES = 25 # Number of Classes/Labels

os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
trainer = DefaultTrainer(cfg) 
trainer.resume_or_load(resume=False)
trainer.train()

```


### TODO:
  - Use shapely to speed-up the process of generating instance ids.
  - Add code to train a Detectron2 panoptic segmentation model on a custom dataset.
      - Use `register_coco_panoptic_separated` and modify `load_seg_files` to use png instead of jpg.
  - Add code to run evaluation using the panoptic quality metric.

