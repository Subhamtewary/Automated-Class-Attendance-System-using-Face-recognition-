import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
from database import log_attendance

# Initialize webcam
cap = cv2.VideoCapture(0)  # Default camera
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

# Load background image
imgBackground = cv2.imread('Resources/background.png')  # Ensure this file exists

# Load mode images into a list
folderModePath = 'Resources/Modes'  # Path to the modes folder
modePathList = os.listdir(folderModePath)  # List of images in Modes folder
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load the face encodings file
print("Loading encoded file...")
try:
    with open('EncodeFile.p', 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    encodeListKnown, validStudentIds, validStudentNames = encodeListKnownWithIds
    print("Encoded file successfully loaded.")
except FileNotFoundError:
    print("Error: Encoded file not found. Run encode.py to generate the file.")
    exit()

# Helper function to overlay smaller images onto the background
def overlay_image(background, overlay, x, y):
    h, w, _ = overlay.shape
    background[y:y + h, x:x + w] = overlay

while True:
    success, img = cap.read()  # Capture frame from webcam

    # Preprocess webcam frame for face detection
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Reduce size for faster processing
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces and encode them
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Overlay webcam feed onto background
    overlay_image(imgBackground, img, 55, 162)

    # Overlay a placeholder mode image (e.g., standby mode)
    overlay_image(imgBackground, imgModeList[2], 808, 44)

    for encodeFace, faceloc in zip(encodeCurFrame, faceCurFrame):
        # Compare current encodings with known encodings
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)  # Find closest match

        # If a known face is detected
        if matches[matchIndex] and faceDis[matchIndex] < 0.5:  # Threshold for matching
            studentId = validStudentIds[matchIndex]
            print(f"Detected: {studentId}")

            # Log attendance in the database
            log_attendance(studentId)

            # Draw bounding box
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale back to original size
            bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
            imgBackground = cvzone.cornerRect(imgBackground, bbox, 20, rt=0)

            # Display student name and attendance
            cv2.putText(imgBackground, f'Name: {validStudentNames[matchIndex]}', (x1 + 6, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(imgBackground, f'ID: {studentId}', (x1 + 6, y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show the final image
    cv2.imshow("Attendance System", imgBackground)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
