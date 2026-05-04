import cv2
import requests
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

cap=cv2.VideoCapture(0)

BACKEND_URL = "http://localhost:5000/alert"

while True:
    ret,frame=cap.read()
    if not ret:
        break
    results=model(frame)

    for r in results:
        for box in r.boxes:
            cls=int(box.cls[0])
            label=model.names[cls]
            print("Detected",label)

            if label in["person","knife","gun","cell phone"]:
                try:
                    requests.post(BACKEND_URL,json={
                        "type":label,
                        "message":f"Suspicious object detected {label}"
                    })
                    print("Alert sent to backend")
                except Exception as e:
                    print("Failed to send alert:",e)

    cv2.imshow("AI Detection",frame)
    if cv2.waitKey(1) & 0XFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
