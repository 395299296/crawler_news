import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt
import os

input_dir = 'verifies'
output_dir = 'verifies_gray'

def check_connect(region, x, y, result):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0: continue
            x1 = x + i
            y1 = y + j
            if x1 < 0 or y1 < 0: continue
            if x1 >= region.shape[1]: continue
            if y1 >= region.shape[0]: continue
            if region[y1, x1] > 0:
                if (y1, x1) not in result:
                    result.append((y1, x1))
                    check_connect(region, x1, y1, result)

def calc_connect(image, min_area):
    connect_area = []
    for i in range(1, image.shape[1] - 1):
        for j in range(1, image.shape[0] - 1):
            if image[j,i] > 0 and (j,i) not in connect_area:
                region_area = []
                if (j,i) not in region_area:
                    region_area.append((j,i))
                    check_connect(image, i, j, region_area)
                if len(region_area) < min_area:
                    for x in region_area:
                        image[x[0], x[1]] = 0
                else:
                    connect_area.extend(region_area)

def filter_noise(image):
    for i in range(3, image.shape[1] - 3):
        for j in range(3, image.shape[0] - 3):
            pos = np.nonzero(image[j-3:j+3,i-3:i+3])
            if len(pos[0]) < 8:
                image[j,i] = 0

def exchange_gray(imgfile):
    print("exchanging img:", imgfile)
    img = cv2.imread(imgfile,cv2.IMREAD_GRAYSCALE)
    sp = img.shape
    heigth = sp[0]
    width = sp[1]
    ret,thresh = cv2.threshold(img,220,255,cv2.THRESH_BINARY_INV)
    return thresh
    img2 = thresh.copy()
    calc_connect(img2, 200)
    pos = np.nonzero(img2)
    start_x = min(pos[1])
    start_y = min(pos[0])
    end_x = max(pos[1])
    end_y = max(pos[0])
    img3 = thresh.copy()
    img3 = img3[start_y:end_y, start_x:end_x]
    #calc_connect(img3, 20)
    return img3


if __name__ == '__main__':
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for parent, dirnames, filenames in os.walk(input_dir):
        for x in filenames:
            img = exchange_gray(os.path.join(parent, x))
            cv2.imwrite(os.path.join(output_dir, x), img)