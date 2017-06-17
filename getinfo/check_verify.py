import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt

img = cv2.imread('test.jpg',cv2.IMREAD_GRAYSCALE)
sp = img.shape
print(sp)
heigth = sp[0]
width = sp[1]
ret,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY_INV)
cv2.imshow('image',thresh)

def check_connect(region, x, y, result):
	for i in [-1, 0, 1]:
		for j in [-1, 0, 1]:
			if i == 0 and j == 0: continue
			x1 = x + i
			y1 = y + j
			if region[y1, x1] > 0:
				if (y1, x1) not in result:
					result.append((y1, x1))
					check_connect(region, x1, y1, result)

def calc_connect(image, min_area):
	connect_area = []
	for i in range(1, image.shape[1] - 1):
		for j in range(1, image.shape[0] - 1):
			if img2[j,i] > 0 and (j,i) not in connect_area:
				region_area = []
				if (j,i) not in region_area:
					region_area.append((j,i))
					check_connect(img2, i, j, region_area)
				if len(region_area) < min_area:
					for x in region_area:
						img2[x[0], x[1]] = 0
				else:
					connect_area.extend(region_area)

def filter_noise(image):
	for i in range(3, image.shape[1] - 3):
		for j in range(3, image.shape[0] - 3):
			pos = np.nonzero(image[j-3:j+3,i-3:i+3])
			if len(pos[0]) < 8:
				image[j,i] = 0

img2 = thresh.copy()
calc_connect(img2, 200)
pos = np.nonzero(img2)
start_x = min(pos[1])
start_y = min(pos[0])
end_x = max(pos[1])
end_y = max(pos[0])
img3 = thresh.copy()
img3 = img3[start_y:end_y, start_x:end_x]
calc_connect(img3, 20)
cv2.imshow('image3',img3)
cv2.waitKey(0)
cv2.destroyAllWindows()