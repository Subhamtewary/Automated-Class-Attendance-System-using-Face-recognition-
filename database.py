import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="attendance_system"
    )

def log_attendance(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if attendance has already been logged today
    query = "SELECT * FROM attendance WHERE student_id = %s AND DATE(attendance_time) = CURDATE();"
    cursor.execute(query, (student_id,))
    if not cursor.fetchone():
        # Insert a new attendance record
        cursor.execute("INSERT INTO attendance (student_id) VALUES (%s);", (student_id,))
        conn.commit()

        # Update the attendance_count for the student in the students table
        cursor.execute("""
            UPDATE students
            SET attendance_count = attendance_count + 1
            WHERE id = %s;
        """, (student_id,))
        conn.commit()

        print(f"Attendance logged for ID: {student_id}")
    else:
        print(f"Attendance already logged for ID: {student_id} today.")
    
    cursor.close()
    conn.close()
