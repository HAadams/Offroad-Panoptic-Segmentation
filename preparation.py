import numpy as np
from PIL import Image
from labels import color2labels
from collections import Counter
import time

def generateInstanceIds(img:np.array):

    segs_count = Counter()

    x, y, _ = img.shape
    instance_ids = np.zeros(shape=(x,y))

    def floodFill(img, x, y, color, seg_id, hasInstances):

        visited = set()
        stack = [(x,y)]
        while stack:
            x, y = stack.pop()
            if x < 0 or x >= img.shape[0] or y < 0 or y >= img.shape[1]:
                continue

            if img[x][y][0] == 0 and img[x][y][1] == 0 and img[x][y][2] == 0:
                continue
            
            if not (img[x][y][0] == color[0] and img[x][y][1] == color[1] and img[x][y][2] == color[2]):
                continue
            
            if (x, y) in visited:
                continue

            if hasInstances:
                R,G,B = color
                seg_id = R+G*256+B*256^2
                seg_id += segs_count[color]

            instance_ids[x][y] = seg_id
            visited.add((x, y))
            img[x][y] = 0

            stack.append((x, y+1))
            stack.append((x, y-1))
            stack.append((x+1, y))
            stack.append((x-1, y))    

    for i in range(x):
        for j in range(y):

            if img[i][j][0] == 0 and img[i][j][1] == 0 and img[i][j][2] == 0:
                continue
            
            color = (img[i][j][0], img[i][j][1], img[i][j][2])
            has_instances = color2labels[color].hasInstances
            seg_id = color2labels[color].id

            floodFill(img, i, j, color, seg_id, has_instances)

            segs_count[color] += 1
            
    return instance_ids


if __name__ == "__main__":
    start = time.time()
    img = np.array(Image.open('creek_00001.png'))
    img = generateInstanceIds(img)
    end = time.time()
    print(f"TOOK {end-start} SECONDS!")
