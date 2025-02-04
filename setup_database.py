import mysql.connector

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234"
    )
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system;")
    cursor.execute("USE attendance_system;")

    # Create the students table with the attendance_count column
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        attendance_count INT DEFAULT 0  -- Column to track the attendance count
    );
    """)

    # Create the student_encodings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_encodings (
        student_id VARCHAR(20),
        encoding BLOB,
        FOREIGN KEY (student_id) REFERENCES students(id)
    );
    """)

    # Create the attendance table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20),
        attendance_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database setup completed.")

if __name__ == "__main__":
    setup_database()
