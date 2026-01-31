# Tortoise Burrow Wildlife Detection (YOLO + Flask)

This project is a lightweight web application and ML pipeline for detecting and classifying wildlife species observed around tortoise burrow sites. It provides a simple UI to upload images, runs a trained YOLO computer-vision model for inference, and outputs labeled/annotated results to support faster review of multi-species burrow interactions.    
To see a demonstration and results of the application, go to the final_product folder. 

## Key Features
- Upload images through a Flask web interface
- Run object detection/classification using a trained YOLO model
- Save prediction outputs (e.g., annotated images/results) for analysis

![Demo](https://github.com/amandashohdy/Tortoise-Project/blob/main/final_product/application.png?raw=true)
https://github.com/amandashohdy/Tortoise-Project/raw/refs/heads/main/final_product/MAB_Results.mp4

## Tech Stack
- Python, Flask
- Ultralytics YOLO (PyTorch-based workflow)

## Local Instance Steps

### Initializing the Virtual Environment (commands)
- python -m venv yoloenv
- .\yoloenv\Scripts\activate (will need to run this command every time you close the virtual environmemt)
- pip install Flask
- pip install opencv-python flask pillow torch tensorflow ultralytics requests
- flask run

### Ensure you have: 
- uploads folder
- runs folder
- output folder 
