# Summary
This script contains the workflow to perform panoptic segmentation on a off-road navigation video. Configure the input config.json as desired in order to run this script to create a panoptic segmentation video of the off-road navigation video with 1) an untrained baseline Detectron2 panoptic segmentation model (panoptic_fpn_R_50_1x, panoptic_fpn_R_50_3x, or panoptic_fpn_R_101_3x) or 2) a fine tuned Detectron2 panoptic segmentation model.

## Inputs
The single argument passed to the script is the config.json file.

If running with an untrained baseline Detectron2 panoptic segmentation model, then the values as shown below should be specified.

![configFormat1](images/configFormat1.png)

If running with a fine-tuned baseline Detectron2 panoptic segmentation model, then the values a shown below should be specified.

![configFormat2](images/configFormat2.png)

## Outputs
In the specified folder_name, the "inVideoFrames" folder will contain the image frames of the specified video, the "outVideoFrames" folder will contain the image frames with the panoptic segmentation model's inference. The specified folder_name will contain the psVideo.avi video file (compiled outVideoFrames images).