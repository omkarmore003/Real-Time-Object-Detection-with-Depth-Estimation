import torch
import cv2
import numpy as np
from ultralytics import YOLO
import pyttsx3
import threading
import time
import pyautogui

# ----------------------------- Setup MiDaS (Depth Estimation) -----------------------------
model_type = "MiDaS_small"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.to("cuda" if torch.cuda.is_available() else "cpu").eval()

transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------------------- Setup YOLOv8 -----------------------------
yolo_model = YOLO("yolov8n.pt")

# ----------------------------- Text-to-Speech Feedback -----------------------------
def give_feedback(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()

def feedback_thread(message):
    threading.Thread(target=give_feedback, args=(message,)).start()

# ----------------------------- Real-World Distance Calculation -----------------------------
def calculate_real_distance(depth_map, bbox, frame_width, frame_height, k=0.8):
    x1, y1, w, h = bbox
    cx, cy = int(x1 + w / 2), int(y1 + h / 2)

    dm_h, dm_w = depth_map.shape
    scale_x = dm_w / frame_width
    scale_y = dm_h / frame_height

    cx_mapped = min(int(cx * scale_x), dm_w - 1)
    cy_mapped = min(int(cy * scale_y), dm_h - 1)

    depth_value = depth_map[cy_mapped, cx_mapped]
    distance_m = k / depth_value if depth_value > 0 else float('inf')

    return distance_m

# ----------------------------- Setup Video Capture -----------------------------
ip_camera_url = "http://172.27.117.69:8080/video"
cap = cv2.VideoCapture(ip_camera_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ----------------------------- Get Screen Size for Corner Placement -----------------------------
screen_width, screen_height = pyautogui.size()
window_name = "Object Detection + Real Distance"
window_width = 640
window_height = 480

corner_x = screen_width - window_width
corner_y = screen_height - window_height

# ----------------------------- Main Loop -----------------------------
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, window_width, window_height)
cv2.moveWindow(window_name, corner_x, corner_y)

with torch.no_grad():
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        input_image = cv2.resize(frame, (320, 240))
        input_rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        img_tensor = transform(input_rgb).to(device)

        depth_prediction = midas(img_tensor)
        depth_map = depth_prediction.squeeze().cpu().numpy()

        depth_min = depth_map.min()
        depth_max = depth_map.max()
        depth_map = (depth_map - depth_min) / (depth_max - depth_min + 1e-6)

        results = yolo_model(frame, conf=0.4)

        if results[0].boxes is not None:
            for box in results[0].boxes:
                bbox = box.xywh.cpu().numpy().flatten()
                class_id = int(box.cls.cpu().numpy())
                class_name = yolo_model.names[class_id]

                distance_m = calculate_real_distance(depth_map, bbox, frame.shape[1], frame.shape[0])

                if distance_m < 1.0:
                    zone = "very close"
                elif distance_m < 3.0:
                    zone = "nearby"
                else:
                    zone = "far away"

                feedback_msg = f"{class_name} {zone}, {distance_m:.2f} meters"
                feedback_thread(feedback_msg)

                x, y, w, h = bbox
                x1, y1 = int(x - w / 2), int(y - h / 2)
                x2, y2 = int(x + w / 2), int(y + h / 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{class_name} ({zone}) {distance_m:.2f}m", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
