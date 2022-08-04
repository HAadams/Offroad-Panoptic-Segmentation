# detectron2 imports and setup. Make sure detectron2 is installed.
import torch, detectron2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.utils.video_visualizer import VideoVisualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.utils.visualizer import ColorMode
from detectron2.engine import DefaultTrainer
from detectron2.data.datasets import register_coco_panoptic_separated

from detectron2.utils.logger import setup_logger
setup_logger()

# other imports
import time
import numpy as np
import random
import os
import sys
import cv2
from natsort import natsorted
import json

class PSVideoApp:
  def __init__(self):
    print("Reading the config.json file...")

    #read the input config.json file
    inputJSONFile = sys.argv[1]
    inputJSON = open(inputJSONFile)
    configDict = json.load(inputJSON)
    
    inputJSON.close()
     
    self.useFineTunedModel = configDict["use_fine_tuned_model"]
    self.videoFile = configDict["video_file"]
    self.psModel = configDict["detectron2_ps_model"]
    self.weightsFile = configDict["fine_tuned_weights_file"]
    self.trainingDataset = configDict["training_dataset"]
    self.confidenceVal = configDict["confidence_val"]
    self.folderName = configDict["folder_name"]

    print("Finished reading the config.json file.")

  def makeOutputFolder(self):
    print("Making the specified output folders in 'folder_name'...")

    folderName = self.folderName
    inputFramesFolder = os.path.join(folderName, "inVideoFrames")
    outputFramesFolder = os.path.join(folderName, "outVideoFrames")

    if not os.path.exists(inputFramesFolder):
      os.makedirs(inputFramesFolder)

    if not os.path.exists(outputFramesFolder):
      os.makedirs(outputFramesFolder)

    print("Finished making the output folders.")
  
  def videoToFrames(self):
    print("Converting video to input frames in 'folder_name'/inVideoFrames...")

    videoFile = self.videoFile
    folderName = self.folderName

    # Opens the Video file
    cap = cv2.VideoCapture(videoFile)
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        frameImageName = str(i) + '.jpg'
        fullFramePath = os.path.join(folderName, 'inVideoFrames', frameImageName)

        cv2.imwrite(fullFramePath,frame)
        i+=1
    
    cap.release()
    cv2.destroyAllWindows()

    print("Finished converting video to input frames. Total frames: " + str(i))
  
  def updateMetadata(self, panopticDatasetName: str, categoriesJSON: str):
    print("Updating metadata for fine-tuned model...")

    #This will auto-set the things and things_dataset_id_to_contiguous_id in metadata
    datasetCatalog = DatasetCatalog.get(panopticDatasetName)

    with open(categoriesJSON) as jsonFile: 
      categories = json.load(jsonFile) 

    stuffsList = [f["name"] for f in categories if f["isthing"] == 0]
    stuffColors = [tuple(f["color"]) for f in categories if f["isthing"] == 0]
    numStuffClasses = len(stuffsList)

    thingsList = [f["name"] for f in categories if f["isthing"] == 1]
    thingColors = [tuple(f["color"]) for f in categories if f["isthing"] == 1]
    numThingClasses = len(thingsList)

    stuff_ids = {i : v for i, v in enumerate(range(numStuffClasses))}
    MetadataCatalog.get(panopticDatasetName).set(stuff_dataset_id_to_contiguous_id=stuff_ids, stuff_classes=stuffsList, stuff_colors=stuffColors, thing_colors=thingColors)

    metaData = MetadataCatalog.get(panopticDatasetName)

    print("Finished updating metadata.")

    return metaData, numStuffClasses, numThingClasses

  def inferenceOnFrames(self):
    print("Doing panoptic segmentation inference on input frames and storing in 'folder_name'/outVideoFrames...")

    folderName = self.folderName
    inputFramesFolder = os.path.join(folderName, "inVideoFrames")
    outputFramesFolder = os.path.join(folderName, "outVideoFrames")

    images = [img for img in os.listdir(inputFramesFolder) if img.endswith(".jpg")]
    sortedImages = natsorted(images)

    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(self.psModel))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.confidenceVal

    if(self.useFineTunedModel == True):
      #register dataset with cocopanoptic separated
      register_coco_panoptic_separated(
            name=self.trainingDataset["name"],
            metadata={},
            image_root=self.trainingDataset["image_root"],
            panoptic_root=self.trainingDataset["panoptic_root"],
            panoptic_json=self.trainingDataset["panoptic_json"],
            sem_seg_root=self.trainingDataset["sem_seg_root"],
            instances_json=self.trainingDataset["instances_json"],
      )
      datasetCatalog = DatasetCatalog.get(self.trainingDataset["name"] + "_separated")
      #update the metadata like with stuff classes, stuff id to contiguous id, and set the colors for things and stuffs. Retrieve the metadata.
      metaData, numStuffs, numThings = self.updateMetadata(self.trainingDataset["name"] + "_separated", self.trainingDataset["categories_json"])

      #Use weights file from fine-tuning the model. Set num things and stuff appropriately.
      cfg.MODEL.WEIGHTS = self.weightsFile

      cfg.MODEL.ROI_HEADS.NUM_CLASSES = numThings  # 8 thing classes 
      cfg.MODEL.SEM_SEG_HEAD.NUM_CLASSES = numStuffs  # 21 stuff classes 
    else:
      cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(self.psModel)
      metaData = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])

    predictor = DefaultPredictor(cfg)

    tracker = time.time()

    i = 0
    for image in sortedImages:
      inImageFullPath = os.path.join(folderName, "inVideoFrames", image)
      outImageFullPath = os.path.join(folderName, "outVideoFrames", image)

      im = cv2.imread(inImageFullPath)
      panoptic_seg, segments_info = predictor(im)["panoptic_seg"]
      v = Visualizer(im[:, :, ::-1], metaData, scale=1.0)
      out = v.draw_panoptic_seg_predictions(panoptic_seg.to("cpu"), segments_info)
        
      cv2.imwrite(outImageFullPath, out.get_image()[:, :, ::-1])

      i = i + 1

      if(i == 1000):
        i = 0
        newTime = time.time()
        elapsedTime = newTime - tracker
        tracker = time.time()
        print("It took this many seconds to process 1000 frames: " + str(elapsedTime))

    print("Finished doing inference.")

  def makeVideo(self):
    print("Compiling the video...")

    folderName = self.folderName
    outputFramesFolder = os.path.join(folderName, "outVideoFrames")
    videoName = os.path.join(folderName, "psVideo.avi")

    images = [img for img in os.listdir(outputFramesFolder) if img.endswith(".jpg")]
    sortedImages = natsorted(images)

    frame = cv2.imread(os.path.join(outputFramesFolder, sortedImages[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(videoName, fourcc, 30, (width,height))

    for image in sortedImages:
        video.write(cv2.imread(os.path.join(outputFramesFolder, image))) 

    cv2.destroyAllWindows()
    video.release()

    print("Finished making the video.")

def main():
  if len(sys.argv) != 2:
    print("Please run command with 1 arguments after the script name: config.json")
    sys.exit(0)

  psVideoApp = PSVideoApp()
  psVideoApp.makeOutputFolder()
  psVideoApp.videoToFrames()
  psVideoApp.inferenceOnFrames()
  psVideoApp.makeVideo()

  print("Done. Look in 'folder_name' for the constructed panoptic segmentation video.")

if __name__ == "__main__":
    main()