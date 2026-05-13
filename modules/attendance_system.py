import cv2
import face_recognition
import os
import numpy as np
import sqlite3
from datetime import datetime

# Path to student images
path = 'images/student_faces'

images = []
student_names = []

# Read student folders
for student in os.listdir(path):

    student_folder = os.path.join(path, student)

    for img_name in os.listdir(student_folder):

        img_path = os.path.join(
            student_folder,
            img_name
        )

        img = cv2.imread(img_path)

        # Ignore invalid images
        if img is not None:

            images.append(img)

            student_names.append(student)

print("Training faces...")

# Encode known faces
known_encodings = []
filtered_names = []

for img, student in zip(
    images,
    student_names
):

    rgb_img = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    encodings = face_recognition.face_encodings(
        rgb_img
    )

    # Ignore images without faces
    if len(encodings) > 0:

        known_encodings.append(
            encodings[0]
        )

        filtered_names.append(
            student
        )

print("Training completed!")

# Attendance function
def mark_attendance(name):

    now = datetime.now()

    time_string = now.strftime(
        '%H:%M:%S'
    )

    date_string = now.strftime(
        '%d-%m-%Y'
    )

    # Connect SQLite database
    conn = sqlite3.connect(
        'facetrack.db'
    )

    cursor = conn.cursor()

    # Check if attendance already exists
    cursor.execute(

        '''

        SELECT *

        FROM attendance

        WHERE
            student_name = ?
            AND date = ?

        ''',

        (
            name,
            date_string
        )

    )

    already_marked = cursor.fetchone()

    # Prevent duplicate attendance
    if already_marked:

        print(
            f"{name} already marked today"
        )

        conn.close()

        return

    # Insert attendance
    cursor.execute(

        '''

        INSERT INTO attendance
        (student_name, department, date, time)

        VALUES (?, ?, ?, ?)

        ''',

        (
            name,
            "CSE",
            date_string,
            time_string
        )

    )

    conn.commit()

    conn.close()

    print(f"{name} attendance marked")

# Open webcam
camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    # Resize frame for faster processing
    small_frame = cv2.resize(

        frame,

        (0, 0),

        fx=0.25,

        fy=0.25
    )

    rgb_small_frame = cv2.cvtColor(

        small_frame,

        cv2.COLOR_BGR2RGB
    )

    # Detect faces
    face_locations = face_recognition.face_locations(

        rgb_small_frame
    )

    # Encode detected faces
    face_encodings = face_recognition.face_encodings(

        rgb_small_frame,

        face_locations
    )

    # Compare faces
    for face_encoding, face_location in zip(

        face_encodings,

        face_locations
    ):

        matches = face_recognition.compare_faces(

            known_encodings,

            face_encoding
        )

        face_distances = face_recognition.face_distance(

            known_encodings,

            face_encoding
        )

        match_index = np.argmin(
            face_distances
        )

        # Better accuracy threshold
        if (

            matches[match_index]

            and face_distances[match_index] < 0.45
        ):

            name = filtered_names[
                match_index
            ].upper()

            # Mark attendance
            mark_attendance(name)

            color = (0, 255, 0)

        else:

            name = "UNKNOWN"

            color = (0, 0, 255)

        # Face coordinates
        top, right, bottom, left = face_location

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw rectangle
        cv2.rectangle(

            frame,

            (left, top),

            (right, bottom),

            color,

            2
        )

        # Display name
        cv2.putText(

            frame,

            name,

            (left, top - 10),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            color,

            2
        )

    # Show webcam
    cv2.imshow(

        "FaceTrack Attendance System",

        frame
    )

    # ESC key to exit
    if cv2.waitKey(1) == 27:

        break

camera.release()

cv2.destroyAllWindows()