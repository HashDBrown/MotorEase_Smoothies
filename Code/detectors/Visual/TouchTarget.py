import xml.etree.ElementTree as ET
from PIL import Image
import cv2
import os
import importlib  
foobar = importlib.import_module("detectors.Visual.UIED-master.run_single")
import json

def __init__(self):
	pass

def getBounds(inText):
    split = inText.split('][')
    
    split[0] = split[0].strip('[')
    split[1] = split[1].strip(']')
    
    split[0] = split[0].split(",")
    split[1] = split[1].split(",")
    
    split[0] = [int(split[0][0]), int(split[0][1])]
    split[1] = [int(split[1][0]), int(split[1][1])]
    return split

def describeWidgetComponent(class_name):
    lower_class_name = class_name.lower()

    # Dictionary mapping class names to descriptions
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

    if lower_class_name in widget_map:
       return widget_map[lower_class_name]

    return "Unknown widget component"

def describeBounds(bounds, height, width):
	bounds_values = bounds.strip('[]').split(',')
	left = int(bounds_values[0])
	top = int(bounds_values[1].split('][')[0])
	right = int(bounds_values[-1])
	bottom = int(bounds_values[-1].split('][')[-1])

	center_x = (left + right) // 2
	center_y = (top + bottom) // 2

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

	position_description = "The element is positioned towards the {}-{} corner of the screen.".format(vertical_position, horizontal_position)

	return position_description

def describe(xml_element, violating_flag):
	bounds = xml_element.attrib.get('bounds', '')
	text = xml_element.attrib.get('text', '')
	component = xml_element.attrib.get('class', '')
	component_str = describeWidgetComponent(component)

	# Assuming the screen resolution
	screen_height = 1920
	screen_width = 1080
	position_description = describeBounds(bounds, screen_height, screen_width)

	if violating_flag:
		print("This violating component is a {} with text '{}'.".format(component_str, text))
	else:
		print("This interactive component is a {} with text '{}'.".format(component_str, text))

	print(position_description)

def checkTouchTarget(screenshot_path, xml_path, min_size=(48, 48)):
# Load the XML file
	if ".DS_S" not in xml_path:
		tree = ET.parse(xml_path)
		root = tree.getroot()
		bounding_boxes = []
		singleScreenViolations = []
		interactiveElements = []

		violations = 0
		nonViolations = 0

		for elem in root.iter():
			elements = elem.items()
			if len(elements) > 1:
				if elements[8][0] == 'clickable' and elements[8][1] =='true' and elements[16][1] != '[0,0][0,0]':
					# Find all bounding boxes in the XML file
					bounds = getBounds(elements[16][1])
					first = bounds[1][0] - bounds[0][0]
					second = bounds[1][1] - bounds[0][1]
					if first <48 or second <48:
						#print(elements)
						#print(bounds)
						interactiveElements.append([elements, 1])
						describe(elem, violating_flag=True)
						describe(elem, violating_flag=False)
						violations+=1
					else:
						
						im = Image.open(screenshot_path)
						
						im1 = im.crop((bounds[0][0]-15, bounds[0][1]-15, bounds[1][0]+15, bounds[1][1]+15))
						
						savePath = "/code/detectors/Visual/UIED-master/data/input/" + str(screenshot_path.split('/')[-1])
						im1 = im1.save(savePath)
						foobar.runSingle(savePath)
						os.remove(savePath)
						for root, dirs, files_in_dir in os.walk("/code/detectors/Visual/UIED-master/data/output/ip/"):
							for file_name in files_in_dir:
								if ".json" in file_name:
									data = []
									#print(file_name)
									with open("/code/detectors/Visual/UIED-master/data/output/ip/" + file_name, "r") as file:
										data = json.load(file)
									for i in range(len(data["compos"])):
										height = data["compos"][i]['height']
										width = data["compos"][i]['width']
										if height < 48 or width < 48:
											describe(elem, violating_flag=True)
											violations += 1
											interactiveElements.append([elements, 1])
										else:
											nonViolations += 1
											interactiveElements.append([elements, 0])

										describe(elem, violating_flag=False)
										#print(violations)
										#print(nonViolations)

									if "DS_Store" not in file_name:
										os.remove("/code/detectors/Visual/UIED-master/data/output/ip/" + file_name)
								else:
									os.remove("/code/detectors/Visual/UIED-master/data/output/ip/" +file_name)
		return([violations, violations+nonViolations, xml_path, interactiveElements])
									
										

						#return([bounds, screenshot_path, elements])













