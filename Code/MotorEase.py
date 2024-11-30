print(">> Starting MotorEase\n")
import os
#from application.app.folder.file import func_name
from detectors.Visual.TouchTarget import checkTouchTarget
from detectors.Visual.IconDistance import getDistance
#from detectors.Visual.LabeledElements import checkLabeled
from detectors.Motor.Closure import *
from detectors.Motor.Closure import detectClosure
from detectors.Motor.patternMatching.pattern_matching import *
from detectors.Motor.persistentElements import *
from detectors.Motor.persistentElements import PersistentDriver
import matplotlib.pyplot as plt
import pickle
from numpy import asarray

import importlib  
pre = importlib.import_module("detectors.Visual.UIED-master.detect_compo.lib_ip.ip_preprocessing")
draw = importlib.import_module("detectors.Visual.UIED-master.detect_compo.lib_ip.ip_draw")
det = importlib.import_module("detectors.Visual.UIED-master.detect_compo.lib_ip.ip_detection")
file = importlib.import_module("detectors.Visual.UIED-master.detect_compo.lib_ip.file_utils")
Compo = importlib.import_module("detectors.Visual.UIED-master.detect_compo.lib_ip.Component")
ip = importlib.import_module("detectors.Visual.UIED-master.detect_compo.ip_region_proposal")
Congfig = importlib.import_module("detectors.Visual.UIED-master.config.CONFIG_UIED")

def shorten_file_name(file_name):
	#parse name by '_' and concat [0] and [3]
	#return the shortened name
	name = file_name.split('_')
	return name[0] + '_' + name[3]

def plot_violations(x, y):
    """
    Plots the violations against screenshots and saves the plot to a file.
    
    Args:
    - x: List of screenshot names.
    - y: List of violations corresponding to the screenshots.
    """
    print(">> Plotting Data")
    plt.figure(figsize=(10, 8))
    plt.plot(x, y, marker='o')
    plt.xlabel('Screenshots')
    plt.ylabel('Violations')
    plt.title('MotorEase Violations')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('violations_graph.png')  # Save the graph as 'violations_graph.png'
    #plt.savefig('/MotorEase-main/violations_graph.png') # Docker method

def RunDetectors(data_folder):
	x = []
	y = []
	print(">> Extracting Path\n")
	txt = open("AccessibilityReport.txt", "a")
	# txt = open("predictions2.txt", "a")
	file_extensions = ['.png', '.xml']
	files = []
	print(">> Getting Files and Screenshots\n")
	for root, dirs, files_in_dir in os.walk(data_folder):
		for file_name in files_in_dir:
			files.append(os.path.join(root, file_name[:-4]))
	print(">> Initializing Detectors\n")

	print(">> Initializing Embedding Model (may take some time)\n")
	# Load pre-trained GloVe embeddings
	# glove_model_array = ""
	# with open('./code/glove_model.pkl', 'rb') as f:
	# 	try:
	# 		glove_model_array = pickle.load(f)
	# 	except EOFError as e: 
	# 		print(f"EOFError: {e}")


	model = {}
	with open("/Code/glove.6B.100d.txt", 'r', encoding='utf-8') as file:
		for line in file:
			parts = line.split()
			word = parts[0]
			vector = [float(x) for x in parts[1:]]  # Convert string components to floats
			model[word] = vector

	# Docker Method
	# with open("/MotorEase-main/embeddings/glove.6B.100d.txt", 'r', encoding='utf-8') as file:
	# 	for line in file:
	# 		parts = line.split()
	# 		word = parts[0]
	# 		vector = [float(x) for x in parts[1:]]  # Convert string components to floats
	# 		model[word] = vector
	
	glove_model_array = model

	counter = 0
	for i in range(0, len(files), 2):

		if "DS_S" not in files[i]:
			image = files[i] + ".png"
			xml = files[i] + ".xml"  
			txt.write("============================================\n")
			txt.write('FILENAME: ' + image.split('/')[-1] + "\n")
			fileName = shorten_file_name(image.split('/')[-1])
			x.append(fileName)

			print("_______Analyzing Next File______")

			print("===== Running Touch Target =====")
			touchTarget = checkTouchTarget(image, xml) #Format-> [25 (violations), 26 (elements), './Data/ca.mimic.apphangar_Bottom_Up_0.xml']
			touchText = "Touch Target Detector>> "  + "Interactive Elements: " + str(touchTarget[1]) + " | Violating Elements: " + str(touchTarget[0]) + "\n"
			print(touchText)  
			txt.write(touchText + '\n')  
			y.append(touchTarget[0])

			print("===== Running Expanding Elements =====")
			expanding = detectClosure(image, xml, glove_model_array)
			expandingText = image + ":\n" + "Expanding Sections Detector>> " +"Expanding elements: " + str(expanding) + "\n"
			print(expandingText)
			txt.write(expandingText + '\n')
			print("\n")

			print("===== Running Icon Distances =====")
			distances = getDistance(image, xml)
			print(distances)
			txt.write(str(image.split('/')[-1]) + ', ' + str(distances) + "\n")
			print("\n")

			#for testing
			if counter > 1:
				continue
			counter += 1

	txt.write("============================================\n")
	txt.write("\nAll Screens \n")
	print("_______Analyzing All Screens_______")
	print("===== Running Persistent Elements =====")
	persistent = PersistentDriver(data_folder)
	persistentText = data_folder + ': \n' "Persisting Elements Detector>> " + "Violating Screens: " + str(persistent[1])
	print(persistentText)

	print("\n>> Generating Accessibility Report")

	txt.write(persistentText + '\n')
	print("\nAccessibility Report Generated: AccessibilityReport.txt")

	txt.close()

	plot_violations(x, y)

# set the path to the directory of the Miracle Project
MotorEase_PATH = "/"
#MotorEase_PATH = "/MotorEase-main/" #Docker method
os.chdir(MotorEase_PATH)


AppPath = MotorEase_PATH + 'Data/'
RunDetectors(AppPath) 




















