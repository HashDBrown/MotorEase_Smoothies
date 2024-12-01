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

# def shorten_file_name(file_name):
# 	#parse name by '_' and concat [0] and [3]
# 	#return the shortened name
# 	name = file_name.split('_')
# 	return name[0] + '_' + name[3]

def plot_violating(x, y):
    """
    Plots the violations against screenshots as a bar graph and saves the plot to a file.
    
    Args:
    - x: List of screenshot names.
    - y: List of violating elements count corresponding to the screenshots.
    """
    print("\n>> Plotting Violating Elements Data")
    plt.figure(figsize=(12, 8))
    bars = plt.bar(x, y, color='skyblue', edgecolor='black', width=0.6)
    plt.xlabel('Screenshots', fontsize=12)
    plt.ylabel('Number of Elements', fontsize=12)
    plt.title('Violating Elements per Screenshot', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()

    plt.savefig('violating_graph.png')  # Save the graph as 'violations_graph.png'
    #plt.savefig('/MotorEase-main/violations_graph.png') # Docker method
    print("\nViolating Elements Graph Generated: violating_graph.png")

def plot_interactive(x, y):
    """
    Plots the violations against screenshots as a bar graph and saves the plot to a file.
    
    Args:
    - x: List of screenshot names.
    - y: List of interactive elements count corresponding to the screenshots.
    """
    print("\n>> Plotting Interactive Elements Data")
    plt.figure(figsize=(12, 8))
    bars = plt.bar(x, y, color='orange', edgecolor='black', width=0.6)
    plt.xlabel('Screenshots', fontsize=12)
    plt.ylabel('Number of Elements', fontsize=12)
    plt.title('Interactive Elements per Screenshot', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()

    plt.savefig('interactive_graph.png')  # Save the graph as 'violations_graph.png'
    #plt.savefig('/MotorEase-main/interactive_graph.png') # Docker method
    print("\nIneractive Elements Graph Generated: interactive_graph.png")

def plot_comparison(x, y1, y2):
    """
    Plots the violations against screenshots as a bar graph and saves the plot to a file.
    
    Args:
    - x: List of screenshot names.
    - y1: List of violating elements count corresponding to the screenshots.
	- y2: List of interactive elements count corresponding to the screenshots.
    """
    print("\n>> Plotting Both Data for comparison")
    plt.figure(figsize=(12, 8))

    bar_width = 0.4
    bar_positions_violations = range(len(x))  # Positions for violations bars
    bar_positions_interactive = [pos + bar_width for pos in bar_positions_violations]  # Offset positions for interactive elements

    # Plot bars
    bars_violations = plt.bar(bar_positions_violations, y1, color='skyblue', edgecolor='black', width=bar_width, label='Violating')
    bars_interactive = plt.bar(bar_positions_interactive, y2, color='orange', edgecolor='black', width=bar_width, label='Interactive')

    # Add labels, title, and legend
    plt.xlabel('Screenshots', fontsize=12)
    plt.ylabel('Number of Elements', fontsize=12)
    plt.title('Violations Vs. Interactive Elements per Screenshot', fontsize=14)
    plt.xticks([pos + bar_width / 2 for pos in bar_positions_violations], x, rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(fontsize=12)

    for bars in [bars_violations, bars_interactive]:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{int(height)}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    plt.savefig('violating_vs_interactive.png')  # Save the graph as 'violations_graph.png'
    #plt.savefig('/MotorEase-main/violating_vs_interactive.png') # Docker method
    print("\nComparison Graph Generated: violating_vs_interactive.png")

def RunDetectors(data_folder):
	files_list = []
	violating_values = []
	interactive_values = []
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
	#with open("/MotorEase-main/embeddings/glove.6B.100d.txt", 'r', encoding='utf-8') as file: #Docker method
	#with open("/ABSOLUTE/PATH/TO/glove.6B/glove.6B.100d.txt", 'r', encoding='utf-8') as file: #Python method
		for line in file:
			parts = line.split()
			word = parts[0]
			vector = [float(x) for x in parts[1:]]  # Convert string components to floats
			model[word] = vector

	glove_model_array = model

	counter = 0
	for i in range(0, len(files), 2):

		if "DS_S" not in files[i]:
			image = files[i] + ".png"
			xml = files[i] + ".xml"  
			txt.write("============================================\n")
			txt.write('FILENAME: ' + image.split('/')[-1] + "\n")
			files_list.append(image.split('/')[-1])

			print("_______Analyzing Next File______")

			print("===== Running Touch Target =====")
			touchTarget = checkTouchTarget(image, xml) #Format-> [25 (violations), 26 (elements), './Data/ca.mimic.apphangar_Bottom_Up_0.xml']
			touchText = "Touch Target Detector>> "  + "Interactive Elements: " + str(touchTarget[1]) + " | Violating Elements: " + str(touchTarget[0]) + "\n"
			print(touchText)  
			txt.write(touchText + '\n')  
			violating_values.append(touchTarget[0])
			interactive_values.append(touchTarget[1])

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

	plot_violating(files_list, violating_values)
	plot_interactive(files_list, interactive_values)
	plot_comparison(files_list, violating_values, interactive_values)

# set the path to the directory of the Miracle Project
MotorEase_PATH = "/"
#MotorEase_PATH = "/MotorEase-main/" #Docker method
#MotorEase_PATH = "/ABSOLUTE/PATH/TO/MotorEase_Smoothies/" #Python method
os.chdir(MotorEase_PATH)


AppPath = MotorEase_PATH + 'Data/'
RunDetectors(AppPath) 




















