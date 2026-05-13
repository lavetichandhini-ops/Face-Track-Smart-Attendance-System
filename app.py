from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file
)

import os
import sqlite3
import csv

app = Flask(__name__)

# ---------------- ADMIN LOGIN ---------------- #

USERNAME = "admin"
PASSWORD = "1234"

# ---------------- LOGIN PAGE ---------------- #

@app.route('/', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        # Check credentials
        if username == USERNAME and password == PASSWORD:

            return redirect(
                url_for('dashboard')
            )

        else:

            return render_template(

                'login.html',

                error="Invalid Username or Password"

            )

    return render_template('login.html')

# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')

def dashboard():

    return render_template('index.html')

# ---------------- START ATTENDANCE ---------------- #

@app.route('/start')

def start():

    os.system(
        'python modules/attendance_system.py'
    )

    return "Attendance System Started"

# ---------------- ATTENDANCE RECORDS ---------------- #

@app.route('/records')

def records():

    search = request.args.get('search')

    selected_date = request.args.get('date')

    # Connect SQLite database
    conn = sqlite3.connect('facetrack.db')

    cursor = conn.cursor()

    # ---------------- DATE FILTER ---------------- #

    if selected_date:

        cursor.execute(

            '''

            SELECT
                student_name,
                department,
                date,
                time

            FROM attendance

            WHERE date = ?

            ''',

            (selected_date,)

        )

    # ---------------- SEARCH ---------------- #

    elif search:

        cursor.execute(

            '''

            SELECT
                student_name,
                department,
                date,
                time

            FROM attendance

            WHERE
                student_name LIKE ?
                OR department LIKE ?
                OR date LIKE ?

            ''',

            (
                f'%{search}%',
                f'%{search}%',
                f'%{search}%'
            )

        )

    # ---------------- SHOW ALL RECORDS ---------------- #

    else:

        cursor.execute(

            '''

            SELECT
                student_name,
                department,
                date,
                time

            FROM attendance

            '''

        )

    data = cursor.fetchall()

    # ---------------- ANALYTICS ---------------- #

    total_present = len(data)

    students = set()

    departments = set()

    # Department chart data
    department_count = {}

    for row in data:

        students.add(row[0])

        departments.add(row[1])

        dept = row[1]

        if dept in department_count:

            department_count[dept] += 1

        else:

            department_count[dept] = 1

    total_students = len(students)

    total_departments = len(departments)

    # ---------------- ATTENDANCE PERCENTAGE ---------------- #

    attendance_percentage = {}

    # Total attendance days
    all_dates = set()

    for row in data:

        all_dates.add(row[2])

    total_days = len(all_dates)

    # Student attendance count
    student_count = {}

    for row in data:

        student = row[0]

        if student in student_count:

            student_count[student] += 1

        else:

            student_count[student] = 1

    # Calculate percentage
    for student, count in student_count.items():

        if total_days > 0:

            percentage = (
                count / total_days
            ) * 100

        else:

            percentage = 0

        attendance_percentage[student] = round(
            percentage,
            2
        )

    conn.close()

    return render_template(

        'records.html',

        data=data,

        total_present=total_present,

        total_students=total_students,

        total_departments=total_departments,

        department_labels=list(
            department_count.keys()
        ),

        department_values=list(
            department_count.values()
        ),

        attendance_percentage=attendance_percentage
    )

# ---------------- DOWNLOAD ATTENDANCE ---------------- #

@app.route('/download')

def download():

    # Connect database
    conn = sqlite3.connect('facetrack.db')

    cursor = conn.cursor()

    # Fetch attendance data
    cursor.execute(

        '''

        SELECT
            student_name,
            department,
            date,
            time

        FROM attendance

        '''

    )

    data = cursor.fetchall()

    conn.close()

    # Create CSV export
    with open(
        'attendance_export.csv',
        'w',
        newline=''
    ) as file:

        writer = csv.writer(file)

        # Header
        writer.writerow(

            [
                'Student Name',
                'Department',
                'Date',
                'Time'
            ]

        )

        # Data rows
        writer.writerows(data)

    return send_file(

        'attendance_export.csv',

        as_attachment=True
    )

# ---------------- REGISTER PAGE ---------------- #

@app.route('/register')

def register():

    return render_template('register.html')

# ---------------- CAPTURE STUDENT FACES ---------------- #

@app.route('/capture', methods=['POST'])

def capture():

    student_name = request.form['student_name']

    os.system(

        f'python modules/capture_faces.py {student_name}'

    )

    return f"{student_name} Registered Successfully"

# ---------------- RUN APP ---------------- #

if __name__ == '__main__':

    app.run(debug=True)