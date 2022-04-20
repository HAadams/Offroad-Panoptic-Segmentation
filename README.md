# Offroad-Panoptic-Segmentation

This repo contains code for applying Panoptic Segmentation to a custom dataset in an off-roading environment.
The specific dataset used to build the labels.py file is RUGD (http://rugd.vision/)


  - `createInstances.py` is used to create the instance segmentation json annotations based on labels.py for RUGD according to the COCO format.
  - `createPanopticAnnotations.py` is used to create panoptic segmentation json annotations and panoptic image annotations according to the COCO format.
  - `createPanopticInstanceIds.py` is used to create the instance ids images from colormap labels.


### TODO:
  - Use shapely to speed-up the process of generating instance ids.
  - Add code to train a Detectron2 panoptic segmentation model on a custom dataset.
      - Use `register_coco_panoptic_separated` and modify `load_seg_files` to use png instead of jpg.
  - Add code to run evaluation using the panoptic quality metric.

