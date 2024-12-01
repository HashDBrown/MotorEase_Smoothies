import xml.etree.ElementTree as ET  
from PIL import Image  
import cv2  
import os  
import importlib  
foobar = importlib.import_module("detectors.Visual.UIED-master.run_single")  # Dynamically import a specific module
import json  # Module for working with JSON data

def __init__(self):
    # Placeholder for class constructor, currently not used
    pass

def getBounds(inText):
    """
    Parses the bounds string and converts it into a list of coordinates.
    Args:
        inText (str): Bounds string in the format '[x1,y1][x2,y2]'.
    Returns:
        list: A list containing two coordinate pairs [[x1, y1], [x2, y2]].
    """
    split = inText.split('][')
    split[0] = split[0].strip('[')
    split[1] = split[1].strip(']')
    split[0] = split[0].split(",")
    split[1] = split[1].split(",")
    split[0] = [int(split[0][0]), int(split[0][1])]
    split[1] = [int(split[1][0]), int(split[1][1])]
    return split

def describeWidgetComponent(class_name):
    """
    Provides a description for a given Android widget class name.
    Args:
        class_name (str): Class name of the widget (e.g., 'android.widget.button').
    Returns:
        str: Description of the widget or 'Unknown widget component' if not found.
    """
    lower_class_name = class_name.lower()

    # Dictionary mapping Android widget class names to descriptions
    widget_map = {
        'android.widget.button': "Button",
        'android.widget.checkbox': "Checkbox",
        'android.widget.radiobutton': "Radio button",
        'android.widget.switch': "Switch",
        'android.widget.edittext': "Edit text",
        'android.widget.imageview': "Image view",
        'android.widget.progressbar': "Progress bar",
        'android.widget.seekbar': "Seekbar",
        'android.widget.spinner': "Spinner",
        'android.widget.listview': "List view",
        'android.widget.gridview': "Grid view",
        'android.widget.linearlayout': "Linear layout",
        'android.widget.framelayout': "Frame layout",
        'android.widget.relativelayout': "Relative layout",
        'android.widget.toolbar': "Toolbar",
        'android.widget.imagebutton': "Image button",
        'android.widget.scrollview': "Scroll view",
        'android.view.view': "View",
        'android.view.viewgroup': "View group",
    }
	#return Android widget class names to descriptions value if found in the list
    if lower_class_name in widget_map:
       return widget_map[lower_class_name]

    return "Unknown widget component"

def describeBounds(bounds, height, width):
    """
    Describes the position of an element on the screen based on its bounds.
    Args:
        bounds (str): Bounds string in the format '[x1,y1][x2,y2]'.
        height (int): Height of the screen.
        width (int): Width of the screen.
    """
    bounds_values = bounds.strip('[]').split(',')
    left = int(bounds_values[0])
    top = int(bounds_values[1].split('][')[0])
    right = int(bounds_values[-1])
    bottom = int(bounds_values[-1].split('][')[-1])

    center_x = (left + right) // 2
    center_y = (top + bottom) // 2
	#describing which position of the screen the element is 
    if center_x < width / 2:
        horizontal_position = "left"
    elif center_x > width / 2:
        horizontal_position = "right"
    else:
        horizontal_position = "center"

    if center_y < height / 2:
        vertical_position = "top"
    elif center_x > height / 2:
        vertical_position = "bottom"
    else:
        vertical_position = "center"

	#adding total description
    position_description = "The element is positioned towards the {}-{} corner of the screen.".format(vertical_position, horizontal_position)

    return position_description

def describe(xml_element, violating_flag):
    """
    Describes the interactive component of an XML element and its position.
    Args:
        xml_element: XML element containing attributes like 'bounds', 'text', and 'class'.
        violating_flag (bool): Whether the element violates the touch target size requirement.
    """
    bounds = xml_element.attrib.get('bounds', '')
    text = xml_element.attrib.get('text', '')
    component = xml_element.attrib.get('class', '')
    component_str = describeWidgetComponent(component)

    # Assuming the screen resolution
    screen_height = 1920
    screen_width = 1080
	# using describeBounds function we get the description properly
    position_description = describeBounds(bounds, screen_height, screen_width)

	# if violation flag is true we found the component as violating
    if violating_flag:
        print("This violating component is a {} with text '{}'.".format(component_str, text))
	# if violation flag is false  we found the component as interactive element only
    else:
        print("This interactive component is a {} with text '{}'.".format(component_str, text))

    print(position_description)

def checkTouchTarget(screenshot_path, xml_path, min_size=(48, 48)):
    """
    Checks whether touch targets in the XML file meet the minimum size requirements.
    Args:
        screenshot_path (str): Path to the screenshot image.
        xml_path (str): Path to the XML file containing UI element bounds.
        min_size (tuple): Minimum width and height of touch targets.
    Returns:
        list: A summary of violations, total elements, XML path, and interactive elements.
    """
    if ".DS_S" not in xml_path:  # Skip processing if the XML path is a macOS system file.
        tree = ET.parse(xml_path)  # Parse the XML file into a tree structure.
        root = tree.getroot()  
		# Initialize an empty list to bounding_boxes,singleScreenViolations and interactiveElements
        bounding_boxes = []  
        singleScreenViolations = []  
        interactiveElements = []  

		#intialize counter value for violating elements and not violation ones
        violations = 0  
        nonViolations = 0  

        for elem in root.iter():  # Iterate through each element in the XML tree.
            elements = elem.items()  
            if len(elements) > 1:  # Process elements that have more than one attribute.
				# Check if the element is clickable and has valid bounds.
                if elements[8][0] == 'clickable' and elements[8][1] == 'true' and elements[16][1] != '[0,0][0,0]':
                    # Parse the bounds attribute into coordinate pairs.
                    bounds = getBounds(elements[16][1])  
					# Calculate the width of the element.
                    first = bounds[1][0] - bounds[0][0]  
					# Calculate the height of the element.
                    second = bounds[1][1] - bounds[0][1]  
					# Check if the width or height is meeting screen size requirments
                    if first < 48 or second < 48:  
						# Mark element as violating.
                        interactiveElements.append([elements, 1])  
						# Describe the violating element.
                        describe(elem, violating_flag=True)  
						# Describe the non-violating aspect.
                        describe(elem, violating_flag=False)  
                        violations += 1  
                    else:
                        im = Image.open(screenshot_path)  
						# Crop the screenshot to include the element with a 15-pixel margin.
                        im1 = im.crop((bounds[0][0]-15, bounds[0][1]-15, bounds[1][0]+15, bounds[1][1]+15))
                        
                        savePath = "/Code/detectors/Visual/UIED-master/data/input/" + str(screenshot_path.split('/')[-1])
                        #savePath = "/MotorEase-main/Code/detectors/Visual/UIED-master/data/input/" + str(screenshot_path.split('/')[-1]) #Docker method
						#savePath = "/ABSOLUTE/PATH/TO/MotorEase_Smoothies/Code/detectors/Visual/UIED-master/data/Input/" + str(screenshot_path.split('/')[-1]) #Python method
                        im1 = im1.save(savePath)  
						# Process the cropped image using an external function.
                        foobar.runSingle(savePath)  
						 # Remove the cropped image file after processing.
                        os.remove(savePath) 
                        for root, dirs, files_in_dir in os.walk("/Code/detectors/Visual/UIED-master/data/output/ip/"):
                        #for root, dirs, files_in_dir in os.walk("/MotorEase-main/Code/detectors/Visual/UIED-master/data/output/ip/"): #Docker method
						#for root, dirs, files_in_dir in os.walk("/ABSOLUTE/PATH/TO/MotorEase_Smoothies/Code/detectors/Visual/UIED-master/data/output/ip/"): #Python method
                        
                            # Traverse the output directory for processed files.
                            for file_name in files_in_dir:
                                if ".json" in file_name:  
                                    data = []  
                                    with open("/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name, "r") as file:
                                    #with open("/MotorEase-main/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name, "r") as file: #Docker method
									#with open("/ABSOLUTE/PATH/TO/MotorEase_Smoothies/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name, "r") as file: #Python method
                                        # Open the JSON file for reading.
                                        data = json.load(file)  
									# Iterate through detected components in JSON.
                                    for i in range(len(data["compos"])):  
                                        height = data["compos"][i]['height']  # Get the height of the component.
                                        width = data["compos"][i]['width']  # Get the width of the component.
										 # Check if the component violates size requirements
                                        if height < 48 or width < 48: 
                                            describe(elem, violating_flag=True)  
                                            violations += 1 
                                            interactiveElements.append([elements, 1])  # Mark component as violating.
                                        else:
                                            nonViolations += 1  
                                            interactiveElements.append([elements, 0])  # Mark component as non-violating.

                                        describe(elem, violating_flag=False)  # Describe the non-violating aspect.
                                    if "DS_Store" not in file_name:  
										# Remove the processed JSON file.
                                        os.remove("/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name)
                                        #os.remove("/MotorEase-main/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name) #Docker method
										#os.remove("/ABSOLUTE/PATH/TO/MotorEase_Smoothies/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name) #Python method
                                        
                                else:
									# Remove non-JSON files from the directory.
                                    os.remove("/Code/detectors/Visual/UIED-master/data/output/ip/" + file_name)
                                    #os.remove("/MotorEase-main/Code/detectors/Visual/UIED-master/data/output/ip/" +file_name) #Docker method
									#os.remove("/ABSOLUTE/PATH/TO/MotorEase_Smoothies/Code/detectors/Visual/UIED-master/data/output/ip/" +file_name) #Python method

          # Return the count of violations, total elements, XML path, and interactive elements.                      
        return [violations, violations+nonViolations, xml_path, interactiveElements]
      

