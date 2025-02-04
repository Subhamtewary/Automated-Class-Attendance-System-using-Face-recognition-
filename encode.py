import os
import cv2
import face_recognition
import pickle
import mysql.connector
from datetime import datetime

# Database connection setup
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="attendance_system"
    )

# Step 1: Load Images from Folder
folderPath = 'Images'  # Replace with your folder path
PathList = os.listdir(folderPath)

imgList = []
studentIds = []
studentNames = []

# Read each image and store it along with its ID and Name
for path in PathList:
    img = cv2.imread(os.path.join(folderPath, path))
    if img is None:
        continue
    imgList.append(img)
    studentId = os.path.splitext(path)[0].split("_")[0]
    studentName = os.path.splitext(path)[0].split("_")[1]
    studentIds.append(studentId)
    studentNames.append(studentName)

# Step 2: Define a Function to Encode Faces
def findEncodings(imagesList, idsList, namesList):
    encodeList = []
    validIds = []
    validNames = []
    for img, studentId, studentName in zip(imagesList, idsList, namesList):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
        face_locations = face_recognition.face_locations(img)  # Detect faces
        if face_locations:  # Check if any face is found
            encodes = face_recognition.face_encodings(img, face_locations)
            encodeList.append(encodes[0])  # Take the first face encoding
            validIds.append(studentId)  # Store the corresponding ID
            validNames.append(studentName)  # Store the corresponding Name
    return encodeList, validIds, validNames

# Step 3: Encode Faces
print("Encoding started...")
encodeListKnown, validStudentIds, validStudentNames = findEncodings(imgList, studentIds, studentNames)

# Step 4: Insert Student Data and Encodings into Database
def insert_student_data(student_id, student_name, encoding):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the student already exists in the database
        cursor.execute("SELECT COUNT(*) FROM students WHERE id = %s", (student_id,))
        result = cursor.fetchone()

        if result[0] == 0:
            # Insert student into the students table
            cursor.execute("INSERT INTO students (id, name) VALUES (%s, %s);", (student_id, student_name))
            print(f"Inserted {student_name} (ID: {student_id}) into the database.")
        else:
            print(f"Student {student_name} with ID {student_id} already exists. Skipping insertion.")

        # Insert the encoding into the database (convert encoding to string)
        encoding_str = ",".join(map(str, encoding))  # Convert numpy array to string
        cursor.execute("INSERT INTO student_encodings (student_id, encoding) VALUES (%s, %s);", (student_id, encoding_str))

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()  # Rollback in case of error

    finally:
        cursor.close()
        conn.close()

# Insert all students into the database
for student_id, student_name, encoding in zip(validStudentIds, validStudentNames, encodeListKnown):
    insert_student_data(student_id, student_name, encoding)

# Step 5: Save the Encodings to a File
filePath = 'EncodeFile.p'  # Path to save encodings
with open(filePath, 'wb') as file:
    pickle.dump([encodeListKnown, validStudentIds, validStudentNames], file)
print(f"Encodings saved to {filePath}.")


# Step 6: Record Attendance When Student is Recognized
def mark_attendance(student_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if the student has already been marked for attendance today
        today_date = datetime.today().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = %s AND DATE(attendance_time) = %s", (student_id, today_date))
        result = cursor.fetchone()

        if result[0] == 0:
            # Insert attendance record for the student
            cursor.execute("INSERT INTO attendance (student_id, attendance_time) VALUES (%s, NOW())", (student_id,))
            conn.commit()
            print(f"Attendance recorded for student ID: {student_id}")
        else:
            print(f"Attendance already recorded for student ID: {student_id} today.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()  # Rollback in case of error

    finally:
        cursor.close()
        conn.close()

# Example: Mark attendance for a recognized student
# Assuming `recognized_student_id` is the ID of the recognized student
recognized_student_id = "R001"  # Example student ID, replace with actual recognition logic
mark_attendance(recognized_student_id)
