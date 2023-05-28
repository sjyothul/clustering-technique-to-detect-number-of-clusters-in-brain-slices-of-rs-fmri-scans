import csv
import cv2
import glob
import numpy as np
import os
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image
from sklearn.cluster import DBSCAN


def brainExtraction():
    print("Brain Extraction Started")
    cwd = os.getcwd()
    pathToDataFolder = cwd+'\\testPatient'
    task1 = '\Slices'
    pathToTask1 = cwd+task1
    if not os.path.exists(pathToTask1):
        os.makedirs(pathToTask1)

    for globalImage in glob.glob('%s\*_thresh.png' % pathToDataFolder):
        words = globalImage.split('_')
        words_len = len(words)
        global_image_number = words[words_len-2]
        org_img = cv2.imread(globalImage)
        img_gray = cv2.cvtColor(org_img, cv2.COLOR_BGR2GRAY)
        template = cv2.imread('template.png',0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where( res >= threshold)
        xstart = -1
        xdiff = -10
        ystart = -1
        ydiff = -10

        for pt in zip(*loc[::-1]):
            xtemp = pt[0]
            ytemp = pt[1]+h
            if(xstart == -1):
                xstart = xtemp
            if(ystart == -1):
                ystart = ytemp
            if(xdiff == -10 and xstart != xtemp):
                xdiff = xtemp - xstart
            if(ydiff == -10 and ystart != ytemp):
                ydiff = ytemp - ystart
            if(xstart != -1 and ystart != -1 and xdiff != -10 and ydiff != -10):
                break

        pathToEachImageFolder = pathToTask1+"\\"+str(global_image_number)
        if not os.path.exists(pathToEachImageFolder):
            os.makedirs(pathToEachImageFolder)
        os.chdir(pathToEachImageFolder)

        img1 = Image.open(globalImage)
        width, height = img1.size
        loc_img_count = 0

        for y0 in range(ystart, height, ydiff):
            for x0 in range(xstart, width, xdiff):
                if(x0+xdiff < width and y0+ydiff < height):
                    box = (x0+5, y0,
                        x0+xdiff if x0+xdiff < width else  width,
                        y0+ydiff if y0+ydiff < height else height)
                    img2 = img1.crop(box)
                    extrema = img2.convert("L").getextrema()
                    if extrema != (0, 0):
                        loc_img_count = loc_img_count + 1
                        img1.crop(box).save('%d.png' % loc_img_count)
        os.chdir(cwd)
    print("Brain Extraction Ended")

def detectClusters():
    print("Detecting Clusters Started")
    cwd = os.getcwd()
    task1 = '\Slices'
    pathToTask1 = cwd+task1
    task2 = '\Clusters'
    pathToTask2 = cwd+task2
    if not os.path.exists(pathToTask2):
        os.makedirs(pathToTask2)

    folderNum = 0
    while 1:
        folderNum = folderNum+1
        pathToImageFolder = pathToTask1+"\\"+str(folderNum)
        if os.path.exists(pathToImageFolder):
            pathToEachImageFolder = pathToTask2+"\\"+str(folderNum)
            if not os.path.exists(pathToEachImageFolder):
                os.makedirs(pathToEachImageFolder)
            os.chdir(pathToEachImageFolder)

            if os.path.exists("CountReport.csv"):
                os.remove("CountReport.csv")
            f = open('CountReport.csv', 'w')
            writer = csv.writer(f, delimiter = ',')
            writer.writerow(["SliceNumber", "ClusterCount"])

            for images in glob.glob('%s\*.png' % pathToImageFolder):
                imageBaseName = os.path.basename(images)
                words = imageBaseName.split('.')
                imageNumber = words[0]
                
                img = cv2.imread(images)
                img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(img_hsv)
                cluster = cv2.threshold(s, 92, 255, cv2.THRESH_BINARY)[1]
                imageName = imageNumber + '.png'
                cv2.imwrite(imageName, cluster)

                Y, X = np.where(cluster == 255)
                zipped = np.column_stack((X,Y))
                cnt=0

                if len(zipped) > 0:
                    clustering = DBSCAN(eps = 5, min_samples = 5).fit(zipped)
                    labels=clustering.labels_
                    ls, cs = np.unique(labels, return_counts = True)
                    dic = dict(zip(ls, cs))
                    idx = [i for i, label in enumerate(labels) if dic[label] > 135 and label >= 0]
                    
                    counts = np.bincount(labels[labels >= 0])
                    for i in counts:
                        if i > 135:
                            cnt += 1
                    #print(imageNumber, cnt)
                    writer.writerow([imageNumber, cnt])
                else:
                    #print(imageNumber, cnt)
                    writer.writerow([imageNumber, cnt])
            f.close()
            df = pd.read_csv("CountReport.csv")
            df.sort_values(by=["SliceNumber"], axis = 0, ascending = True, inplace = True)
            os.remove("CountReport.csv")
            df.to_csv('CountReport.csv', index=False)
        else:
            break
        os.chdir(cwd)
    print("Detecting Clusters Ended")