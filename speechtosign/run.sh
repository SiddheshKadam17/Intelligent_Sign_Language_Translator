#!/bin/bash
cd "$(dirname "$0")"

# Install necessary packages using pip for Python 3
pip3 install opencv-python-headless cvzone numpy mediapipe tensorflow SpeechRecognition easygui gso

# Change to the directory containing the main Python script
cd Team-Akatsuki-main/speechtosign

# Run the main Python script
echo "Running main_script.py..."
python3 ashray.py


