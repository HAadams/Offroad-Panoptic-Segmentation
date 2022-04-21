"""

This script is used to generate instanceIds.png files for each colormap image according to the COCO format.
The instanceIds.png images are stored using 16bit percision (each pixel can have 16bit values)

This script will save the created instance id image in the same location as the input image.

Use this file in conjuction with labels.py to create instance id from image labels.
Usage Example
    python createInstanceImgs.py /content/RUGD-annotations

"""

from tqdm.auto import tqdm
from PIL import Image
from labels import color2labels
from collections import Counter
from multiprocessing import Process
import time
import cv2
import sys
import pathlib
import numpy as np


def generateInstanceIds(img:np.array):

    segs_count = Counter()

    X, Y, _ = img.shape
    instance_ids = np.zeros(shape=(X,Y), dtype=np.uint16)

    def floodFill(x, y, color, l_id, hasInstances):

        visited = np.zeros(shape=(X,Y), dtype=np.uint8)
        stack = [(x,y)]
        seg_id = l_id

        if hasInstances:
            seg_id = l_id*1000
            seg_id += segs_count[color]

        while stack:
            x, y = stack.pop()
            if x < 0 or x >= img.shape[0] or y < 0 or y >= img.shape[1]:
                continue

            if img[x][y][0] == 0 and img[x][y][1] == 0 and img[x][y][2] == 0:
                continue
            
            if not (img[x][y][0] == color[0] and img[x][y][1] == color[1] and img[x][y][2] == color[2]):
                continue
            
            if visited[x][y]:
                continue
            
            instance_ids[x][y] = seg_id
            visited[x][y] = 1
            img[x][y] = 0

            stack.append((x, y+1))
            stack.append((x, y-1))
            stack.append((x+1, y))
            stack.append((x-1, y))    

    for i in range(X):
        for j in range(Y):

            # skip marked/visited pixels
            if img[i][j][0] == 0 and img[i][j][1] == 0 and img[i][j][2] == 0:
                continue
            
            color = (img[i][j][0], img[i][j][1], img[i][j][2])

            if color not in color2labels:
                continue

            has_instances = color2labels[color].hasInstances
            seg_id = color2labels[color].id

            if not has_instances:
                instance_ids[i][j] = seg_id
            else:
                # mark all pixels of this single instance as visited and fill the instanceIds
                floodFill(i, j, color, seg_id, has_instances)

            # each instance of the same class (color) should be differentiated 
            segs_count[color] += 1
            
    return instance_ids

def target(imgs_list, proc_id):
    for  path in tqdm(imgs_list, desc=f"Process #{proc_id}", position=proc_id, leave=False):
        save_path = str(path).replace('.png', '') + '_instanceIds.png'
        img = np.array(Image.open(path))
        img = generateInstanceIds(img)
        cv2.imwrite(save_path, img)

if __name__ == "__main__":

    """
    We'll create N processes and delegate a portion of the images to each process.
    For example, if we have 10 images and 2 processes, this code will create two processes.
    Each process will be responsible for 5 separate images.
    """

    args = sys.argv
    if len(args) < 2:
        print("Please pass directory path")
        exit()

    input_dir = args[1]

    start = time.time()
    processes = list()
    n_proc = 2

    colormap_imgs = list(pathlib.Path(input_dir).glob("**/*.png"))
    label_imgs = list()

    for file in colormap_imgs:
        if '_panoptic.png' in file.name:
            continue

        if '_instanceIds.png' in file.name:
            continue

        instance_path = pathlib.Path(str(file).replace('.png', '') + '_instanceIds.png')
        if not pathlib.Path.exists(instance_path):
            label_imgs.append(file)
    
    label_step = len(label_imgs)//n_proc
    label_idx = 0

    for i in range(n_proc):
        
        proc = Process(target=target, args=[label_imgs[label_idx:label_idx+label_step], i])
        proc.start()
        processes.append(proc)
        label_idx += label_step
        
    for proc in processes:
        proc.join()

    end = time.time()
    print(f"TOOK {end-start} SECONDS!")
