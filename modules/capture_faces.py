import cv2
import os
import sys

# Get student name from Flask
student_name = sys.argv[1]

# Create folder
path = f"images/student_faces/{student_name}"

os.makedirs(path, exist_ok=True)

# Open webcam
camera = cv2.VideoCapture(0)

count = 0

while True:

    ret, frame = camera.read()

    cv2.imshow("Face Capture", frame)

    key = cv2.waitKey(1)

    # SPACE to capture
    if key == 32:

        img_name = f"{path}/{count}.jpg"

        cv2.imwrite(img_name, frame)

        print(f"Image {count} saved")

        count += 1

    # ESC to exit
    elif key == 27:
        break

camera.release()
cv2.destroyAllWindows()