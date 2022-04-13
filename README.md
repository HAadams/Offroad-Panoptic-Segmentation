# Offroad-Panoptic-Segmentation

This repo contains code for applying Panoptic Segmentation to a custom dataset in an off-roading environment.
The specific dataset used to build the labels.py file is RUGD (http://rugd.vision/)

When finished, this repo will have the following:
1. Simple code to generate COCO panoptic instance id .png images from an RGB label .png image. 
2. Simple code to generate COCO annotations .json file.
3. Code to fine-tune a Panoptic Segmentation model using Detectron2 (i.e. R101-FPN)
4. Code to evaluate a Panoptic Segmentation model performance using Panoptic Quality metric.
