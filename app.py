import argparse
import io
from PIL import Image

import torch
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, Response, render_template, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename, send_from_directory
import os
import time 

from ultralytics import YOLO 

app = Flask(__name__)

stop_detecting = False

@app.route("/")
def render_page():
    return render_template('index.html')

@app.route("/", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        if 'file[]' in request.files:
            files = request.files.getlist('file[]')
            for f in files:
                if f: 
                    basepath = os.path.dirname(__file__)
                    filepath = os.path.join(basepath, 'uploads', f.filename)    # store data in uploads folder
                    print("upload folder is ", filepath) 
                    f.save(filepath)
                    global imgpath
                    predict.imgpath = f.filename
                    print("printing predict :::::", predict)

                    file_extension = f.filename.rsplit('.', 1)[1].lower()
            
                    if file_extension == 'jpg':

# 1 # results will be stored in the runs folder
                        img = cv2.imread(filepath)
                        frame = cv2.imencode('.jpg', cv2.UMat(img))[1].tobytes()

                        image = Image.open(io.BytesIO(frame))

                        # Perform Detection
                        yolo = YOLO('my_model.pt')
                        detections = yolo.predict(image, save=True)
# 1 # 
                        return redirect(url_for('render_page'))
            
                    elif file_extension in ['avi', 'mov', 'mp4']:
                        video_path = filepath 
                        cap = cv2.VideoCapture(video_path)

                        # Get Video Dimensions
                        standard_width = 1280
                        standard_height = 720


# 2 # Output File
                        # Define the output directory
                        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads", "DetectedVideos")
                        os.makedirs(downloads_folder, exist_ok=True)

                        # Output Filename
                        input_name, _ = os.path.splitext(f.filename) 
                        output_extension = file_extension
                        output_filename = os.path.join(downloads_folder, f'{input_name}_detecting.{output_extension}')

                        # Choose codec and full output path with extension
                        if output_extension == 'avi':
                            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Common for AVI
                        elif file_extension == 'mov':
                            fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MOV-friendly on many systems
                        else:
                            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Default

                        out = cv2.VideoWriter(output_filename, fourcc, 30.0, (standard_width, standard_height))

# 2 #
                        # Initialize the YOLOv8 Model
                        model = YOLO('my_model.pt')

                        detection_made = False
                        detected_classes = set()

                        while cap.isOpened():
                            if stop_detecting:
                                print("Detection manually stopped")
                                break

                            ret, frame = cap.read()
                            if not ret: break

                            # YOLOv8 Detection on the Frame 
                            results = model(frame, save=True)
                            cv2.waitKey(1)

                            # Check for detections 
                            if results[0].boxes and len(results[0].boxes) > 0:
                                detection_made = True

                                for box in results[0].boxes:
                                    class_id = int(box.cls[0])
                                    class_name = model.names[class_id]
                                    detected_classes.add(class_name)

# 3 # Plot results
                            res_plotted = results[0].plot()
                            res_plotted = cv2.resize(res_plotted, (standard_width, standard_height))
                            cv2.imshow("results", res_plotted) # optional to show live results
# 3 #

# 2 #               # Write the Frame to the Output Video
                            out.write(res_plotted)

                            if cv2.waitKey(1) == ord('q'): break 

                            #for result in results:
                                #class_id, confidence, bbox = result
                                #boxes = result.boxes # boxes object for bbox output
                                #probs = result.probs # class probabilities for classification outputs
                                #cls = boxes.cls
                                #xyxy = boxes.xyxy
                                #xywh = boxes.xywh # box with xywh format, (N, 4)
                                #conf = boxes.conf
                                #print("boxes:", boxes)
                                #print("probs:", probs)
                                #print("cls - cls, (N, 1):", cls)
                                #print("conf - confidence score, (N, 1):", conf)
                                #print("box with xyxy format, (N, 4):", xyxy)
                                #print("box with xywh format, (N, 4):", xywh)

                        cap.release()
                        out.release()
                        cv2.destroyAllWindows()

                        if detection_made and detected_classes:
                            safe_classnames = [name.replace(" ", "_") for name in detected_classes]
                            combined_classnames = '-'.join(sorted(safe_classnames))  # sorted for consistency
                            new_filename = os.path.join(downloads_folder, f'{combined_classnames}-{input_name}.{output_extension}')
                        else : 
                            new_filename = os.path.join(downloads_folder, 'no-animals-detected-' + input_name + "." + output_extension)

                        os.rename(output_filename, new_filename)

            return redirect(url_for('render_page'))
    return render_template('index.html')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask app exposing yolov8 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=True) # Launch the app