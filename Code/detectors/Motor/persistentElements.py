import os
import xml.etree.ElementTree as ET  # For parsing XML files
import math
from PIL import Image  # For image processing

"""
This module, `persistentElements.py`, is part of the MotorEase accessibility detection tool. 
It focuses on identifying accessibility violations related to the consistency of persistent 
UI elements across multiple app screens. Persistent elements are UI components that appear 
in multiple screens (e.g., navigation buttons, headers) and are expected to maintain consistent 
positions, sizes, and appearance.

The script processes XML files (describing UI elements) and associated screenshots to:
1. Extract and analyze the bounds, sizes, and other attributes of persistent elements.
2. Detect violations where these elements deviate significantly in size or position across screens.
3. Return a list of screens with violations and those that are compliant.

This analysis helps developers ensure a consistent and accessible user experience for motor-impaired users by highlighting persistent elements that fail to follow UI accessibility guidelines.
"""

# Extracts the bounds from a string format in the XML (e.g., "[0,0][100,100]")
def getBounds(inText):
    split = inText.split('][')
    
    split[0] = split[0].strip('[')
    split[1] = split[1].strip(']')
    
    split[0] = split[0].split(",")
    split[1] = split[1].split(",")
    
    # Convert bounds to a list of integer coordinates
    split[0] = [int(split[0][0]), int(split[0][1])]
    split[1] = [int(split[1][0]), int(split[1][1])]
    return split

# Determines if an element is "small" based on its area relative to the screen size
def isSmall(bounds):
    screenBounds = [[0, 0], [1080, 1794]]  # Default screen dimensions
    h = bounds[1][0] - bounds[0][0]  # Height of the element
    w = bounds[1][1] - bounds[0][1]  # Width of the element
    area = h * w
    screenArea = 1080*1794
    if area < screenArea/10: # If the element occupies less than 10% of the screen area, consider it "small"
        return True
    else:
        return False

# Converts a bounding box to a simpler 4-element list for easier processing
def get4(box):
    return [box[0][0], box[0][1], box[1][0], box[1][1]]

# Calculates the difference between two bounding boxes
def subtractBounds(b1, b2):
    firstPair = abs(b1[0][0] - b2[0][0])  # Difference in x-coordinates (top-left)
    firstPair1 = abs(b1[0][1] - b2[0][1])  # Difference in y-coordinates (top-left)
    
    secondPair = abs(b1[1][0] - b2[1][0])  # Difference in x-coordinates (bottom-right)
    secondPair1 = abs(b1[1][1] - b2[1][1])  # Difference in y-coordinates (bottom-right)
    
    # (diff in first set of starting, diff in second set of ending bounds)
    totalDiff = (firstPair + secondPair, firstPair1 + secondPair1)
    return totalDiff

# Identifies violating persistent elements across multiple screens
def findViolations(dictionary, dataPath):
    allViolations = []  # List to store screens with violations
    noViolations = []  # List to store screens with no violations
    
    for i in dictionary:  # Iterate through the elements in the dictionary
        if len(dictionary[i]) > 1:  # If the element exists in multiple screens
            # Get the initial bounds of the element
            initBounds = get4(dictionary[i][0][0])
            imgPathinit = dataPath + "/" + str(dictionary[i][1][1][0:-3]) + "png"
            
            # Open the initial screenshot and crop the element based on its bounds
            initPixels1 = Image.open(imgPathinit)
            init = initPixels1.crop(initBounds)
            initPixels = list(init.getdata())  # Pixel data of the cropped element

            for j in dictionary[i]:  # Compare the element across all screens
                fourBox = get4(dictionary[i][0][0])
                imgPath = dataPath + "/" + str(j[1][0:-3]) + "png"
                im = Image.open(imgPath)
                im = im.crop(fourBox)
                pixels = list(im.getdata())

                # Compare the current element's pixels with the initial pixels
                if pixels == initPixels:
                    # Check if the bounds differ significantly between screens
                    if (dictionary[i][0][0][0][0] == j[0][0][0] and subtractBounds(dictionary[i][0][0], j[0])[0] != 0 and subtractBounds(dictionary[i][0][0], j[0])[1] != 0):
                        #print(subtractBounds(dictionary[i][0][0], j[0]))
                        if j[1].split("_B")[0] not in allViolations and j[1].split("_B")[0]:
                            allViolations.append(j[1].split("_B")[0])
                        elif j[1].split("_B")[0] not in noViolations and j[1].split("_B")[0] not in noViolations:
                            noViolations.append(j[1].split("_B")[0])
                initPixels1.close()
                im.close()
    
    # Return screens with violations and no violations
    return ([allViolations, noViolations])

# Main function to analyze persistent elements and detect violations
def PersistentDriver(dataPath):
    fullDictionary = {}  # Dictionary to store all UI elements and their attributes
    screenshots = []  # List of screenshots
    xmls = []  # List of XML files
    
    # Traverse the directory for screenshots and XML files
    for subdir1, dirs1, files1 in os.walk(dataPath):
        for file in files1:
            if ".png" in file:  # Collect screenshots
                screenshots.append(file)
            if ".xml" in file:  # Collect XML files and process them
                xmls.append(file)
                xmlPath = dataPath + "/" + file
                tree = ET.parse(xmlPath)
                for elem in tree.iter():  # Parse each element in the XML tree
                    obj = elem.items()
                    if len(obj) > 2:  # If the element has sufficient attributes
                        if obj[2][1] != '':  # Check if the element has bounds
                            objectBounds = getBounds(obj[len(obj)-1][1])
                            if isSmall(objectBounds):  # Ignore large elements
                                if 'frame_item_image' not in obj[2][1]:  # Exclude unwanted elements
                                    if obj[2][1] not in fullDictionary.keys():
                                        addList = [objectBounds, file]
										#print(obj[2][1])
                                        fullDictionary[obj[2][1]] = [addList]
                                        #print(obj[2])
										#print(obj[len(obj)-1])
                                    else:
                                        newl = fullDictionary[obj[2][1]]
                                        addList = [objectBounds, file]
                                        newl.append(addList)
                                        fullDictionary[obj[2][1]] = newl
    
    screenshots.sort()
    xmls.sort()
    res = findViolations(fullDictionary, dataPath)
	# results = open("PeristentEvaluationResults.txt", 'w')
	#print(noViolations)
	#print(allViolations)
    return(res)
	# for i in list(dict.fromkeys(noViolations)):
	#     results.write(i + "--0" + "\n")
	# for i in list(dict.fromkeys(allViolations)):
	#     results.write(i + "--1" + "\n")

    results.close()    
#print(fullDictionary)
		#print(xmls)
