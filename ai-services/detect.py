import cv2
import requests
import numpy as np
import time
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
last_alert_time = 0
ALERT_COOLDOWN = 3  # seconds between alerts
aggression_streak = 0
STREAK_REQUIRED = 2  # consecutive aggressive frames needed

# Focus on arm landmarks (elbows & wrists) — most relevant for fights
# MediaPipe indices: 13=left elbow, 14=right elbow, 15=left wrist, 16=right wrist
ARM_LANDMARKS = [13, 14, 15, 16]

def detect_aggression(current_positions):
    if len(prev_positions) == 0 or len(current_positions) < 17:
        return False, 0.0

    movement = 0
    for idx in ARM_LANDMARKS:
        x1, y1 = prev_positions[idx]
        x2, y2 = current_positions[idx]
        movement += np.linalg.norm(np.array([x2 - x1, y2 - y1]))

    return movement > 0.3, movement  # threshold for arm movement only

try:
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
        is_aggressive, arm_movement = detect_aggression(current_positions)

        if is_aggressive:
            aggression_streak += 1
        else:
            aggression_streak = 0

        print(f"People: {people_count} | Arm movement: {arm_movement:.3f} | Streak: {aggression_streak}/{STREAK_REQUIRED}")

        if people_count >= 2 and aggression_streak >= STREAK_REQUIRED:
            now = time.time()
            if now - last_alert_time > ALERT_COOLDOWN:
                last_alert_time = now
                aggression_streak = 0
                print(">>> ALERT: Possible Fight Detected! Sending to backend...")

                try:
                    requests.post(BACKEND_URL, json={
                        "type": "fight",
                        "message": "Possible fight detected"
                    })
                except Exception as e:
                    print(f"Failed to send alert: {e}")

        prev_positions = current_positions

        cv2.imshow("Behavior Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    pose.close()
    cap.release()
    cv2.destroyAllWindows()