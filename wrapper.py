import os
import sys
import csv
import math
import shutil
from itertools import islice
import cv2


def compareSingle(outputPath, dataPath):
    #run openface vectorization on each image in datapath and send output to outputpath
    os.system("..OpenFace/OpenFace/build/bin/FaceLandmarkImg -fdir " + dataPath + " -out_dir " + outputPath)
    maxconfidence = 0
    for item in os.listdir(outputPath):
        name = item.split('.')
        #identify all csvs and find the highest confidence
        if len(name) > 1 and name[1] == 'csv':
            with open(outputPath + item, 'r') as f:
                data = list(csv.reader(f))
            #confidence in second column, second row of csv
            confidence = float(data[1][1])
            if confidence > maxconfidence:
                maxconfidence = confidence
                maxname = name[0]

    #use opencv for analysis on the image associated with the highest confidence and print confidence onto the image and display
    img = cv2.imread(outputPath + maxname + '.jpg')
    cv2.putText(img, str(maxconfidence), (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 2.0, color=(0, 255, 255))
    #displays image
    cv2.imshow('image',img)
    #saves image
    cv2.imwrite('img.jpg', img)
    cv2.waitKey(1000)
    return


def compareFolder(outputPath, dataPath, finalPath, angleDict):
    #run openface vectorization on each image in datapath and send output to outputpath
    final = []
    imgs = set()
    print("Running OpenFace\n")
    for angle in os.listdir(dataPath):
        if os.path.isdir(dataPath + angle):
            os.system("../build/bin/FaceLandmarkImg -fdir " + dataPath + angle + " -out_dir " + outputPath + angle)
            for a in os.listdir(dataPath + angle):
                if os.path.isdir(dataPath + angle) and a != '.DS_Store':
                    imgs.add(a)
    print("Head Pose estimation complete\nAnalyzing output")
    
    for image in imgs:
        imagedata = []
        name = image.split('.')
        maxconfidence = 0
        #compare jpgs across folders at each timeframe (img0000 in folder 1, 2, 3)
        for folder in os.listdir(outputPath):
            #check whether it's a folder or not
            if os.path.isdir(outputPath + folder):
                if name[0] + ".csv" in os.listdir(outputPath + folder):
                    with open(outputPath + folder + "/" + name[0] + ".csv", 'r') as f:
                        data = list(csv.reader(f))
                    #confidence in second column, second row of csv
                    confidence = float(data[1][1])
                    if confidence > maxconfidence:
                        maxconfidence = confidence
                        maxname = folder
                        for index, d in enumerate(data[0]):
                        #search top row of CSV for pose_Ry, which is the angle we are analyzing for starters
                            if d == ' pose_Ry':
                                maxangle = (round(math.degrees(float(data[1][index])) + angleDict[folder], 4)) % 360

        #identifies image with highest confidence at each timeframe and adds it to finalPath, adds image ID, folder, confidence to final text file

        confangle = maxangle
        if maxconfidence < 0.7:
            confangle = 0
        imagedata = [name[0][-4:], maxname, maxconfidence, maxangle, confangle]
        final.append(imagedata)
        final = sorted(final)

        img = cv2.imread(outputPath + maxname + '/' + name[0] + '.jpg')
            
        cv2.putText(img, str(imagedata), (0, len(img) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.002 * len(img[0]), (100, 255, 255), 1)
        #saves image
        write_name = finalPath + '/' + name[0] + '.jpg'
        cv2.imwrite(write_name, img)
            
    print("Writing info to txt file")
    with open(finalPath + 'final.txt', 'w') as f:
        count = 0;
        countf = 0;
        countl = 0;
        num = 0;
        
        while count < len(final):
            a = final[count][4]
            if(a == 0):
                if (countf == 0):
                    countf = final[count-1][4]
                num += 1
                count += 1
                continue
            elif (final[count+1][4] == 0 or final[count-1][4] == 0):
                if (countf == 0 and final[count+1][4] == 0):
                    countf = a
                elif (countl == 0 and final[count-1][4] == 0):
                        countl = a
                        for i in range(1,num+1):
                            final[count-i][4] = countl -(i)*(countl -countf)/(num+1)
                        countf = 0
                        countl = 0
                        num = 0
            count += 1
        f.write("  image   camera   confidence   angle   confangle\n")
        for data in final:
            f.write(data[0].rjust(6) + "  " + data[1].rjust(6) + "  " + str(data[2]).rjust(10) + "  " + '{:.4f}'.format(round(data[3],4)).rjust(10) + "  " + '{:.4f}'.format(round(data[4],4)).rjust(8) +'\n')

    print("View final output images and data in " + str(finalPath))
    return
    

if __name__ == "__main__":
    #clear the outputPath and finalPath before running the code
    shutil.rmtree('../Output/')
    shutil.rmtree('../Final/')
    os.mkdir('../Output/')
    os.mkdir('../Final/')
    
    #specify directory that input data is located
    dataPath = "../testdata/"
    #specify directory that output will be sent to
    outputPath = "../Output/"
    finalPath = '../Final/'
    #hard coded angles (value) associated with the camera id (key)
    angleDict = {'00': 0, '01': 150, '02': 225}
    countDict = {}

#    compareSingle(outputPath, dataPath)
    #run the script on each person present in the data
    for person in os.listdir(dataPath):
        os.mkdir(finalPath + person + '/')
        os.mkdir(outputPath + person + '/')
        compareFolder(outputPath + person + '/', dataPath + person + '/', finalPath + person + '/', angleDict)
    #create final txt file that summarizes data across all people
    for angle in os.listdir(finalPath):
        with open(finalPath + angle + '/final.txt', 'r') as f:
            fdata = f.readlines()[1:]
        for line in fdata:
            val = line.split()[0]
            if val not in countDict:
                countDict[val] = 0
            #increment the dictionary value at the time if a person is present at that time
            countDict[val] += 1
    with open(finalPath + 'final.txt', 'w') as f:
        f.write("Image, # present\n")
        for i in sorted(countDict.items()):
            f.write(i[0] + ', ' + str(i[1]) + '\n')
