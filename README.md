👁️ Smart Vision: Real-Time Object Detection with Depth Estimation

A real-time smart vision system for object detection and distance feedback, specially designed to assist visually impaired users. This system integrates YOLOv8 for object detection and MiDaS for depth estimation, providing auditory feedback on the proximity of detected objects using text-to-speech.

📸 Live Demo
Real-time video processing via IP Webcam with object zone feedback:

"Very close"

"Nearby"

"Far away"


🚀 Features
🎯 YOLOv8 (Nano) for real-time object detection

🧠 MiDaS_small for monocular depth estimation

🔊 Text-to-Speech feedback using pyttsx3

🖥️ Automatic window placement to bottom-right of screen

🧠 Zone Classification: Categorizes objects as Very Close, Nearby, or Far Away

📡 Supports IP Webcam input for mobile camera streaming

🧩 Modules Used
Module	Purpose
YOLOv8	Fast and efficient object detection
MiDaS_small	Lightweight depth estimation model
OpenCV	Real-time video capture and display
pyttsx3	Offline Text-to-Speech feedback
torch	Model inference and GPU acceleration
pyautogui	For placing window to the bottom-right of screen

📂 Folder Structure
.
├── object.py            # Main script with all modules

├── README.md            # Project documentation

├── requirements.txt     # Python dependencies

🖥️ Setup Instructions
1. Clone the Repository
git clone https://github.com/omkarmore003/Real-Time-Object-Detection-with-Depth-Estimation

3. Install Dependencies
Make sure you have Python 3.8+ installed.

pip install -r requirements.txt
3. Download Models
YOLOv8: yolov8n.pt is automatically downloaded by the ultralytics package

MiDaS: Automatically downloaded using torch.hub

No manual model download is required.

4. Configure IP Webcam (Mobile Camera)
Install IP Webcam Android app

Connect your phone and PC to the same Wi-Fi

Start the camera server on phone

Replace the following line in main.py with your IP:

ip_camera_url = "http://<your-phone-ip>:8080/video"
▶️ Run the Application

python object.py

📐 Distance Estimation Logic
Real-world distance is estimated using the depth map from MiDaS:

distance = k / depth_value
depth_value is the normalized depth from MiDaS

k = 0.8 is the focal scaling factor (adjustable)

Zones:

< 1.0 m → Very Close

< 3.0 m → Nearby

> 3.0 m → Far Away

🗣️ Voice Feedback Example
"person very close, 0.80 meters"

"bicycle nearby, 2.45 meters"

"car far away, 5.78 meters"

Voice messages are played asynchronously using threads.

✅ Requirements
Python 3.8+

PyTorch

OpenCV

Ultralytics

pyttsx3

numpy

pyautogui

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Ultralytics YOLOv8

Intel ISL MiDaS

IP Webcam App (Android)
