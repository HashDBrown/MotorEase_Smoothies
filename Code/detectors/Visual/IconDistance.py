import xml.etree.ElementTree as ET
from PIL import Image
import cv2
import os
import importlib  
foobar = importlib.import_module("detectors.Visual.UIED-master.run_single")
import json
import numpy as np
from sklearn.cluster import KMeans
import pytesseract
def __init__(self):
	pass

def bbox_dimensions(bbox):
    # Assuming bbox is a tuple or list with 4 elements: (x1, y1, x2, y2)
    x1, y1, x2, y2 = bbox

    # Calculate the width and height of the bounding box
    width = x2 - x1
    height = y2 - y1

    # Return the width and height as a tuple
    return (width, height)

def BoundDistance(bbox_i, bbox_j):
	'''
    Computes the horizontal and vertical distances between two bounding boxes,
    along with a coordinate difference check.

    Parameters:
    bbox_i, bbox_j: list or tuple
    Bounding boxes in the format [x1, y1, x2, y2].

    Returns:
    list
        [horizontal_distance, vertical_distance, coordinate_difference]
    '''
	# Calculate horizontal and vertical distances
	horiz_dist = max(0, abs(min(bbox_i[2], bbox_j[2]) - max(bbox_i[0], bbox_j[0])))
	vert_dist = max(0, abs(min(bbox_i[3], bbox_j[3]) - max(bbox_i[1], bbox_j[1])))

	# Compute differences for all coordinates between the two bounding boxes
	result_list = [bbox_i[i] - bbox_j[i] for i in range(len(bbox_i))]
	 # Check if any coordinate difference is within the threshold (8 px)
	for i in result_list:
		if abs(i) <=8:
			return ([horiz_dist, vert_dist, i])
	# Return distances with a default difference of 10 if no match is found
	return ([horiz_dist, vert_dist, 10])

def check_no_matching_numbers(arr1, arr2):
	'''
    Checks if two lists have no matching numbers.
    Parameters:
    arr1 : list
        The first list of numbers.
    arr2 : list
        The second list of numbers.
    '''
	# Iterate through each number in the first list
	for num1 in arr1:
		# Compare it with each number in the second list
		for num2 in arr2:
			# Return False if a matching number is found
			if num1 == num2:
				return False	
	# If no matching numbers are found, return True
	return True
def is_overlapping(box1, box2):
	'''
    Determines if two bounding boxes overlap.

    Parameters:
    box1, box2 : list or tuple
        Bounding boxes defined as [x_min, y_min, x_max, y_max], where:
        - (x_min, y_min) represents the top-left corner.
        - (x_max, y_max) represents the bottom-right corner.
    '''
	# Unpack coordinates for the first bounding box
	x1_min, y1_min, x1_max, y1_max = box1
	# Unpack coordinates for the second bounding box
	x2_min, y2_min, x2_max, y2_max = box2

	# Check for non-overlapping conditions:
    # - One box is completely to the left of the other
    # - One box is completely above the other
	if (x1_max < x2_min) or (x2_max < x1_min) or (y1_max < y2_min) or (y2_max < y1_min):
		return False # Boxes do not overlap
	else:
		# If none of the above conditions are true, the boxes overlap
		return True
def getBounds(inText):
	'''
	Parses a string representation of bounding box coordinates and converts it into a usable format.
    Parameters:
    inText : str
        A string representing bounding box coordinates in the format '[x1,y1][x2,y2]'.
    Returns:
    list
        A list containing two lists:
        - The top-left coordinates [x1, y1].
        - The bottom-right coordinates [x2, y2].
    '''
	# Split the input string into two parts, separating the two coordinate pairs
	split = inText.split('][')
	# Remove the brackets from the first and second coordinate strings
	split[0] = split[0].strip('[')
	split[1] = split[1].strip(']')
	# Further split each coordinate string into x and y values
	split[0] = split[0].split(",")
	split[1] = split[1].split(",")
	# Convert the coordinate strings into integers
	split[0] = [int(split[0][0]), int(split[0][1])]
	split[1] = [int(split[1][0]), int(split[1][1])]
	 # Return the processed coordinates as a list of two lists
	return split
						
def is_single_color_image(image_path):
	"""
	Checks if an image is just a single solid color.
	"""
	# Open the image using Pillow
	img = Image.open(image_path)

	# Get the image dimensions
	width, height = img.size

	# Get the color of the top-left pixel
	pixel = img.getpixel((0, 0))

	# Check if all pixels in the image have the same color
	for x in range(width):
		for y in range(height):
			if img.getpixel((x, y)) != pixel:
				return False
	img.close()
	# If all pixels have the same color, return True
	return True


def getDistance(screenshot_path, xml_path):
    """
    Processes an XML file and a screenshot to extract and analyze bounding boxes for UI elements,
    detecting specific distance and layout criteria.

    Parameters:
    screenshot_path : str
        Path to the screenshot image.
    xml_path : str
        Path to the XML file containing bounding box data.

    Returns:
    int
        1 if valid unique distances between bounding boxes are detected (meeting criteria), else 0.
    """
    # Load the XML file if it is valid (skip .DS_S files)
    if ".DS_S" not in xml_path:
        tree = ET.parse(xml_path)  # Parse the XML file
        root = tree.getroot()  # Get the root of the XML tree
        bounding_boxes = []  # Store adjusted bounding boxes
        singleScreenViolations = []  # Track UI violations for this screen

        violations = 0  # Counter for violations (not used in logic)
        nonViolations = 0  # Counter for non-violations (not used in logic)

        # Iterate over elements in the XML tree
        for elem in root.iter():
            elements = elem.items()  # Get attributes of the element
            if len(elements) > 1:  # Ensure valid elements with attributes
                # Identify 'clickable' elements with non-zero bounds
                if elements[8][0] == 'clickable' and elements[8][1] == 'true' and elements[16][1] != '[0,0][0,0]':
                    # Parse the bounding box coordinates
                    bounds = getBounds(elements[16][1])  # Extract coordinates from the "bounds" string
                    first = bounds[1][0] - bounds[0][0]  # Calculate width of the bounding box
                    second = bounds[1][1] - bounds[0][1]  # Calculate height of the bounding box
                    box_string = elements[16][1]  # Extract the bounding box string

                    try:
                        # Extract numerical values from the bounding box string
                        left = int(box_string[1:box_string.index(",")])  # Left coordinate (x1)
                        top = int(box_string[box_string.index(",")+1:box_string.index("]")])  # Top coordinate (y1)
                        right = int(box_string[box_string.index("[", 1)+1:box_string.index(",", box_string.index(",")+1)])  # Right coordinate (x2)
                        bottom = int(box_string.split(str(right))[1].strip(',').strip(']'))  # Bottom coordinate (y2)

                        # Create a bounding box [left, bottom, right, top]
                        bbox = [left, bottom, right, top]

                        # Open the screenshot image
                        im = Image.open(screenshot_path)

                        # Ensure bounds are ordered correctly (swap if necessary)
                        if bounds[0][0] > bounds[1][0]:
                            bounds[0][0], bounds[1][0] = bounds[1][0], bounds[0][0]
                        if bounds[0][1] > bounds[1][1]:
                            bounds[0][1], bounds[1][1] = bounds[1][1], bounds[0][1]

                        # Crop the image around the bounding box with padding
                        im1 = im.crop((bounds[0][0]-15, bounds[0][1]-15, bounds[1][0]+15, bounds[1][1]+15))

                        # Save the cropped image for further processing
                        savePath = "/Code/detectors/Visual/UIED-master/data/input/" + str(screenshot_path.split('/')[-1])
						#savePath = "/MotorEase-main/Code/detectors/Visual/UIED-master/data/input/" + str(screenshot_path.split('/')[-1]) #Docker method
                        im1.save(savePath)  # Save the cropped image
                        im1.close()  # Close the cropped image object

                        # Extract text from the cropped image
                        extractedText = pytesseract.image_to_string(savePath)  # Use OCR to extract text

                        # Analyze the cropped image if it contains significant text and is not a solid color
                        if len(extractedText) > 10 and is_single_color_image(savePath) == False:
                            foobar.runSingle(savePath)  # Run edge detection on the cropped image
                            os.remove(savePath)  # Remove the processed cropped image file

                            # Process extracted UI components from the analyzed image
                            for root, dirs, files_in_dir in os.walk("/Code/detectors/Visual/UIED-master/data/output/ip/"):
							#for root, dirs, files_in_dir in os.walk("/MotorEase-main/Code/detectors/Visual/UIED-master/data/output/ip/"): #Docker method
                                for file_name in files_in_dir:
                                    if ".json" in file_name:  # Look for JSON files
                                        data = []
                                        with open("/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name, "r") as file:
										#with open("/MotorEase-main/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name, "r") as file: #Docker method
                                            data = json.load(file)  # Load the JSON data

                                        # Adjust bounding boxes for each detected UI component
                                        for i in range(len(data["compos"])):
                                            height = data["compos"][i]['height']  # Component height
                                            width = data["compos"][i]['width']  # Component width
                                            ogBoxWidth, ogBoxHeight = bbox_dimensions(bbox)  # Original bounding box dimensions

                                            # Adjust height and width based on the detected component's dimensions
                                            subHeight = int((ogBoxHeight - height) / 2)
                                            subWidth = int((ogBoxWidth - width) / 2)

                                            # Adjusted bounding box for the component
                                            newBox = [bbox[0] + subWidth, bbox[3] + subHeight, bbox[2] - subWidth, bbox[1] - subHeight]
                                            if height > 55 and width > 55:  # Ignore small UI components
                                                bounding_boxes.append(newBox)
                                                break
                        im.close()  # Close the original screenshot image object
                    except Exception as e:
                        print('ERROR: ' + str(e))  # Handle and log errors, continue processing other elements
                        continue

        # Calculate unique distances between bounding boxes
        uniqueDistances = {}  # Dictionary to store unique distances
        for i in range(0, len(bounding_boxes)):  # Iterate over all bounding boxes
            for j in range(i+1, len(bounding_boxes)):  # Compare each pair of bounding boxes
                # Skip if bounding boxes overlap or have common coordinates
                if (bounding_boxes[i] != bounding_boxes[j] and 
                    check_no_matching_numbers(bounding_boxes[i], bounding_boxes[j]) and 
                    not is_overlapping(bounding_boxes[i], bounding_boxes[j])):
                    
                    distances = BoundDistance(bounding_boxes[i], bounding_boxes[j])  # Calculate distances
                    distT = tuple(distances)  # Convert the distance data into a tuple

                    # Check specific criteria for distances
                    if distT[2] < 10:  # Ensure the distance difference is below the threshold
                        if distT not in uniqueDistances:
                            uniqueDistances[distT] = [[bounding_boxes[i], bounding_boxes[j]]]  # Add unique distance
                            break
                        else:
                            del uniqueDistances[distT]  # Remove duplicates if found

        # Return 1 if unique distances meet criteria, else return 0
        if len(uniqueDistances.keys()) > 0 and len(uniqueDistances.keys()) < 50:
            print(screenshot_path)  # Log the screenshot path
            return 1  # Indicate valid unique distances detected
        else:
            return 0  # No valid unique distances detected or exceeded the threshold




		













