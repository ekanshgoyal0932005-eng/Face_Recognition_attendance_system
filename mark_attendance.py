import cv2
import pandas as pd
import os
import json
from datetime import datetime

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/face_model.yml")

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

with open("students.json", "r") as file:
    students = json.load(file)

camera = cv2.VideoCapture(0)
marked = set()

os.makedirs("attendance", exist_ok=True)

file_path = "attendance/attendance.csv"
today = datetime.now().strftime("%Y-%m-%d")

if os.path.exists(file_path):
    old_df = pd.read_csv(file_path)
    marked = set(
        old_df[old_df["Date"] == today]["Student ID"].astype(str)
    )

while True:
    ret, frame = camera.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        student_id, confidence = recognizer.predict(face)

        if confidence < 65 and str(student_id) in students:
            name = students[str(student_id)]
            label = name

            if str(student_id) not in marked:
                now = datetime.now()

                record = {
                    "Student ID": student_id,
                    "Name": name,
                    "Date": today,
                    "Time": now.strftime("%H:%M:%S")
                }

                df = pd.DataFrame([record])
                df.to_csv(
                    file_path,
                    mode="a",
                    header=not os.path.exists(file_path),
                    index=False
                )

                marked.add(str(student_id))
        else:
            label = "Unknown"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(
            frame, label, (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
        )

    cv2.imshow("Attendance System - Press ESC to Exit", frame)

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()