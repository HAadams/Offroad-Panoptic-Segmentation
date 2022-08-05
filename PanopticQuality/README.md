# Panoptic Quality Evaluation

## Overview

In order to assess the performance of our fine-tuned Detectron2 Panoptic Segmentation model on an off-road environment, we will be using the standard "panoptic evaluation metrics" (https://cocodataset.org/#panoptic-eval) used by COCO (Common Objects in Context).

Panoptic Quality (PQ) evaluates the performance for all the defined stuff and things categories in a single metric (whereas previous sematic segmentation or instance segmentation had their own specialized and individual metrics). 

The computation of PQ involves two components: 1) segmentation quality (SQ) and 2) recognition quality (RQ), as seen below:

![PQ1](images/PQ1.png)

![PQ2](images/PQ2.png)

The definitions that we use for the "things" and "stuff" classes (that will be evaluated by PQ in our notebook) are as follows:
- things: `[ rubble, puddle, picnic-table, log, bicycle, person, vehicle, pole ]`
- stuff: `[ dirt, sand, grass, tree, water, sky, generic-object, asphalt, gravel, building, mulch, rock-bed, fence, bush, sign, rock, bridge, concrete, barrier, mud ]`

---
## Workflow

The code in the python notebook "PanSeg_Detectron2_TrainEval.ipynb" contains the workflow for training and evaluating (with PQ) the Detectron2 panoptic segmentation models. We recommend running this notebook in Google Colab, since Detectron2 only works on Linux or MacOS runtimes, and the notebook downloads a lot of data. Zipped versions of the RUGD, RELLIS-3D, and Combined datasets are downloaded from a shared Google Drive folder and imported into this notebook.

The main steps for our workflow are:
1. Install necessary libraries and dependencies
2. Choose your training configuration (training dataset, model architecture, number of training iterations)
3. Download and unzip all 3 preprocessed datasets (via Google Drive)
4. Register each dataset with `register_coco_panoptic_separated` and update the metadata
5. Configure training parameters and load the pre-trained Detectron2 model
6. Train the model on the chosen training dataset
7. Use the `COCOPanopticEvaluator` to evaluate the model on all 3 test sets
* Optional: Display a predicted using the trained model on an image from the Combined test set
* Optional: Download all files from the `output` directory to load into other scripts
    * Only the `model_final.pth` and `last_checkpoint` files are required to load the model into another script / notebook

---
### Additional Notes:

Preprocessed datasets can be found separately at the following Google Drive links:
* RUGD: https://drive.google.com/file/d/1cuDAXrwG9NY4d4qsBy8h3OkzTmo2u3WE/view?usp=sharing
* RELLIS-3D: https://drive.google.com/file/d/1QVag_I9iAmpvCa-9EHYxnQsDKLJo0Y1D/view?usp=sharing
* Combined: https://drive.google.com/file/d/1nBapUf3t4N71YOFXHKmLpAGoyfmITJqc/view?usp=sharing

Model weights for models trained on the Combined dataset can be found here:
* 8k iterations: https://drive.google.com/file/d/1-MA0VNt6tz1_D-FuinETD836thKl_gRe/view?usp=sharing
* 16k iterations: https://drive.google.com/file/d/1eGNO61TrODX9IWryxrXrYz-a7tjHsgG9/view?usp=sharing

Please note that for all of these files, Google Drive can potentially restrict download access for a limited time if a file is downloaded too frequently in a short period of time. For this reason, we'd recommend downloading each file to your own Google Drive and either updating the links in the notebook or mounting the Drive directly.
