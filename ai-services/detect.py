import cv2
import requests
import numpy as np
from ultralytics import YOLO
import mediapipe as mp

# YOLO
model = YOLO("yolov8n.pt")

# Pose detection
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
base_options = python.BaseOptions(model_asset_path='pose_landmarker_lite.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False)
pose = vision.PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

BACKEND_URL = "http://localhost:5000/alert"

prev_positions = []

def detect_aggression(current_positions):
    if len(prev_positions) == 0:
        return False

    movement = 0
    for (x1, y1), (x2, y2) in zip(prev_positions, current_positions):
        movement += np.linalg.norm(np.array([x2-x1, y2-y1]))

    return movement > 100  # threshold (tune later)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    people_count = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            if label == "person":
                people_count += 1

    # Pose detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    pose_results = pose.detect(mp_image)

    current_positions = []

    if pose_results.pose_landmarks:
        for lm in pose_results.pose_landmarks[0]:
            current_positions.append((lm.x, lm.y))

    # Detect aggression
    if people_count >= 2 and detect_aggression(current_positions):
        print("Possible Fight Detected")

        try:
            requests.post(BACKEND_URL, json={
                "type": "fight",
                "message": "Possible fight detected"
            })
        except:
            pass

    prev_positions = current_positions

    cv2.imshow("Behavior Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()