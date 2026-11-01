import cv2
import os
import json

def register_face(student_id, name):
    folder = f"dataset/{student_id}"

    if os.path.exists(folder):
        return "Student ID already registered!"

    os.makedirs(folder, exist_ok=True)

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        os.rmdir(folder)
        return "Camera could not be opened!"

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    count = 0

    while count < 50:
        ret, frame = camera.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            if count >= 50:
                break

            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            count += 1
            cv2.imwrite(f"{folder}/{count}.jpg", face)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(
            frame, f"Images: {count}/50",
            (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (0, 255, 0), 2
        )

        cv2.imshow("Face Registration - ESC to stop", frame)

        if cv2.waitKey(1) == 27:
            break

    camera.release()
    cv2.destroyAllWindows()

    if count == 0:
        os.rmdir(folder)
        return "No face detected. Please try again."

    students_file = "students.json"

    with open(students_file, "r") as file:
        students = json.load(file)

    students[student_id] = name

    with open(students_file, "w") as file:
        json.dump(students, file, indent=4)

    return f"{name} registered successfully! {count} images captured."