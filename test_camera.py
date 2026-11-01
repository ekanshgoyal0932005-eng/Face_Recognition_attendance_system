import cv2

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print("Camera opened:", camera.isOpened())

if not camera.isOpened():
    print("Camera not detected!")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print("Unable to read camera!")
        break

    cv2.imshow("Webcam Test - Press ESC to Exit", frame)

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()