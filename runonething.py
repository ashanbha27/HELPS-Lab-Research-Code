import os
import sys
import csv
import cv2


def runonething(dataPath,tempPath,outputPath):
        img = cv2.imread(dataPath)
#                img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        scale_percent = 55.85 # percent of original size
        sp = img.shape
        height = sp[0]  # height(rows) of image
        width = sp[1]  # width(colums) of image
        width = int(sp[1] * scale_percent / 100)
        height = int(sp[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        newsp = resized.shape
        cv2.imwrite('../resized/resized.jpg', resized)
        
        os.system("../build/bin/FaceLandmarkImg -f '../resized/resized.jpg'")
        confidence = 0;
#        for item in os.listdir('../processed/'):
            #identify all csvs and find the highest confidence
        with open('./processed/resized.csv', 'r') as f:
            data = list(csv.reader(f))
                #confidence in second column, second row of csv
            confidence = float(data[1][1])
                
        data =[confidence, newsp[1], newsp[0], scale_percent]
        #print confidence onto the final images
            
        img = cv2.imread("./processed/resized.jpg")
        cv2.putText(img, str(data), (0, len(img) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 255, 255), 1)
        #saves image
        cv2.imwrite('new55.85.jpg', img)
#        print('Resized Dimensions : ',resized.shape)
    

if __name__ == "__main__":
    
    #specify directory that input data is located
    dataPath = "../mydata/01/test_0033.jpg"
    #specify directory that output will be sent to
    tempPath ="../resized/"
    outputPath = "../processed/"
    runonething(dataPath,tempPath,outputPath)
    
   
