import cv2
import os
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []

dataset_path = "dataset"

for student_id in os.listdir(dataset_path):
    student_folder = os.path.join(dataset_path, student_id)

    if not os.path.isdir(student_folder):
        continue

    for image_name in os.listdir(student_folder):
        image_path = os.path.join(student_folder, image_name)

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if image is not None:
            faces.append(image)
            labels.append(int(student_id))

if len(faces) == 0:
    print("No face images found!")
else:
    recognizer.train(faces, np.array(labels))
    os.makedirs("trainer", exist_ok=True)
    recognizer.save("trainer/face_model.yml")

    print("Face recognition model trained successfully!")