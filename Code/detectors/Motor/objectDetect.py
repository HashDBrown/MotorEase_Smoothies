#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
from PIL import Image  # Library for image processing
from torchvision import transforms  # Module for image transformations
import os  
import numpy as np  
import torch  # PyTorch library for deep learning
import torch.nn as nn  # Module for defining neural network layers
import torchvision  # PyTorch's computer vision library
from torchvision import datasets, transforms, models  
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor  


os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Function for object detection
def objectDetect(imagePath):
    """
    Detects objects in an input image using a pretrained Faster R-CNN model.
    Args:
        imagePath (str): Path to the input image.
    Returns:
        list: A list indicating if the object is "closable" and the detected label.
    """
    
    # Load the input image and convert it to RGB format
    img = Image.open(imagePath).convert('RGB')

    # Define a set of image transformations: resizing, normalization, and center cropping
    tfms = transforms.Compose([
                transforms.Resize(227),  # Resize the image to 227x227 pixels
                transforms.ToTensor(),  # Convert the image to a PyTorch tensor
                transforms.Normalize([0.485, 0.456, 0.406],  # Normalize the tensor with mean and std values
                                     [0.229, 0.224, 0.225]),
                transforms.CenterCrop(227)  # Center crop the image to ensure a consistent size
                ])

    # Apply the transformations to the image and add a batch dimension
    img_tensor = tfms(img).to('cpu').unsqueeze(0)

    # Load the Faster R-CNN model pretrained on COCO dataset
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn()

    # Get the number of input features for the box predictor's classification layer
    in_features = model.roi_heads.box_predictor.cls_score.in_features

    # Set the number of classes (customized to the application)
    num_classes = 6

    # Replace the box predictor with a new one configured for the custom number of classes
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # Load the pre-trained model weights from the specified path
    model.load_state_dict(torch.load('./Code/detectors/Motor/model.pth'))

    # Set the model to evaluation mode
    model.eval()
    
    # Perform object detection on the input image tensor
    output = model(img_tensor)

    # Extract the detection scores and labels from the model output
    scores = output[0]['scores']
    labels = output[0]['labels']

    # Define a mapping from label indices to human-readable labels
    labelDict = {0: "x", 1: "left", 2: "right", 3: "down", 4: "ham", 5: "check"}

    # Check if there are any detected objects
    if len(scores) > 0 and len(labels) > 0:
        # Get the score and label for the top detection
        scores = output[0]['scores'][0].item()
        labels = output[0]['labels'][0].item()

        # If the detection score exceeds the threshold (0.5), return the label
        if scores > 0.5:
            return ["closable", labelDict[labels]]  # Return "closable" status and the label

    # If no valid detections are found, return "Not closable"
    else:
        return ["Not closable"]
