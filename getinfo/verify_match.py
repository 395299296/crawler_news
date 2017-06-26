import cv2
import scipy as sp
import numpy as np
import math

cv2.ocl.setUseOpenCL(False)

def sub_image(image, x0, theta, width, height):
    template = []
    for i in range(height):
        tmp = []
        for j in range(width):
            tmp.append(np.array((x0[0]+i-height/2, x0[1]+j-width/2)))
        template.append(tmp)

    template_r = []
    for i in range(height):
        tmp = []
        for j in range(width):
            x1 = template[i][j]
            a1 = np.array([x1[0] - x0[0], x1[1] - x0[1]])
            a2 = np.dot(a1, np.array([[np.cos(math.radians(theta)), -np.sin(math.radians(theta))],
                                      [np.sin(math.radians(theta)), np.cos(math.radians(theta))]]))
            a2 += x0
            tmp.append(a2)
        template_r.append(tmp)

    result = image[0:height,0:width].copy()
    for i in range(height):
        for j in range(width):
            x2 = template_r[i][j]
            try:
                result[i,j] = image[int(round(x2[0])), int(round(x2[1]))]
            except Exception as e:
                result[i,j] = 255

    return result

def hamming_distance(img1, img2):
    size = m1.shape
    img2 = cv2.resize(img2,size,interpolation=cv2.INTER_CUBIC)

    m1 = []
    m2 = []
    for i in range(size[1]):
        for j in range(size[0]):
            if img1[i,j] < 127:
            m1.append(img1[])


if __name__ == '__main__':
    img1 = cv2.imread('test/x1.jpg',cv2.IMREAD_GRAYSCALE) # queryImage
    img2 = cv2.imread('test/x2.jpg',cv2.IMREAD_GRAYSCALE) # trainImage

    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    similarities = []
    match_imgs = []
    for i in range(10,h2-10):
        for j in range(10,w2-10):
            for l in range(20,h2-20):
                if h1 > w1:
                    w = int(round(l * w1 / h1))
                    h = l
                else:
                    w = l
                    h = int(round(l * h1 / w1))
                x0 = np.array((i,j))
                for m in range(0,360):
                    img_s = sub_image(img2, x0, m, w, h)
                    match_imgs.append(img_s)
                    similarities.append(img1, img_s.copy())



    cv2.imshow("match", )
    cv2.waitKey()