import sqlite3

# Connect database
conn = sqlite3.connect('facetrack.db')

cursor = conn.cursor()

# Create students table
cursor.execute('''

CREATE TABLE IF NOT EXISTS students (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    department TEXT

)

''')

# Create attendance table
cursor.execute('''

CREATE TABLE IF NOT EXISTS attendance (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    department TEXT,
    date TEXT,
    time TEXT

)

''')

conn.commit()

conn.close()

print("Database Created Successfully")