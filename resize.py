import os
import sys
import csv
import cv2


def resize(dataPath,tempPath):
    for angle in os.listdir(dataPath):
        if os.path.isdir(dataPath + angle):
            for image in os.listdir(dataPath + angle):
                name = image.split('.')
                if len(name) > 1 and name[1] == 'jpg':
                    img = cv2.imread(dataPath + angle + '/' + name[0] + '.jpg')
    #                img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
                    scale_percent = 40 # percent of original size
                    sp = img.shape
                    height = sp[0]  # height(rows) of image
                    width = sp[1]  # width(colums) of image
                    width = int(sp[1] * scale_percent / 100)
                    height = int(sp[0] * scale_percent / 100)
                    dim = (width, height)
                    # resize image
                    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
#                    print('Resized Dimensions : ',resized.shape)
                    write_name = tempPath + angle + '/' + name[0] + '.jpg'
                    cv2.imwrite(write_name, resized)
            
    

if __name__ == "__main__":
    
    #specify directory that input data is located
    dataPath = "../mydata/"
    #specify directory that output will be sent to
    tempPath ="../resized/"
    
    resize(dataPath,tempPath)
