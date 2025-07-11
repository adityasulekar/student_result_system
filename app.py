from flask import Flask ,render_template,request,redirect,session,url_for,flash
from modules.db_config import get_connection

app = Flask(__name__)
app.secret_key='your_secret_key'

@app.route('/')
def home():
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, role FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['role'] = user[1]
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username or password", "danger")
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template("dashboard.html", username=session['username'], role=session['role'])
    else:
        return redirect(url_for('home'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    message = ""

    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        student_class = request.form['class']

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO students (name, roll_no, class) VALUES (%s, %s, %s)", (name, roll_no, student_class))
            conn.commit()
            message = "Student added successfully!"
        except Exception as e:
            conn.rollback()
            message = "Error: " + str(e)

        conn.close()

    return render_template("add_student.html", message=message)
@app.route('/add_marks', methods=['GET', 'POST'])
def add_marks():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()

    # Get all students for the dropdown
    cursor.execute("SELECT id, name, roll_no FROM students")
    students = cursor.fetchall()
    message = ""

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        marks = request.form['marks']

        try:
            cursor.execute(
                "INSERT INTO results (student_id, subject, marks) VALUES (%s, %s, %s)",
                (student_id, subject, marks)
            )
            conn.commit()
            message = "Marks added successfully!"
        except Exception as e:
            conn.rollback()
            message = "Error: " + str(e)

    conn.close()
    return render_template("add_marks.html", students=students, message=message)
@app.route('/view_result', methods=['GET', 'POST'])
def view_result():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()
    result_data = []

    if request.method == 'POST':
        roll_no = request.form['roll_no']
        cursor.execute("SELECT id FROM students WHERE roll_no=%s", (roll_no,))
        student = cursor.fetchone()

        if student:
            student_id = student[0]
            cursor.execute("SELECT subject, marks FROM results WHERE student_id=%s", (student_id,))
            result_data = cursor.fetchall()

    conn.close()
    return render_template("view_results.html", results=result_data)
@app.route('/all_results')
def all_results():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.name, s.roll_no, s.class, r.subject, r.marks
        FROM students s
        LEFT JOIN results r ON s.id = r.student_id
        ORDER BY s.roll_no, r.subject
    """
    cursor.execute(query)
    all_data = cursor.fetchall()
    conn.close()

    return render_template("all_results.html", data=all_data)
@app.route('/manage_marks')
def manage_marks():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT r.id, s.name, s.roll_no, r.subject, r.marks
        FROM results r
        JOIN students s ON r.student_id = s.id
        ORDER BY s.roll_no
    """
    cursor.execute(query)
    marks_data = cursor.fetchall()
    conn.close()

    return render_template("manage_marks.html", data=marks_data)
@app.route('/edit_marks/<int:result_id>', methods=['GET', 'POST'])
def edit_marks(result_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_subject = request.form['subject']
        new_marks = request.form['marks']

        cursor.execute("UPDATE results SET subject=%s, marks=%s WHERE id=%s",
                       (new_subject, new_marks, result_id))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_marks'))

    # GET: show current data
    cursor.execute("SELECT subject, marks FROM results WHERE id=%s", (result_id,))
    result = cursor.fetchone()
    conn.close()

    return render_template("edit_marks.html", result=result, result_id=result_id)
@app.route('/delete_marks/<int:result_id>')
def delete_marks(result_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id=%s", (result_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('manage_marks'))


if __name__=='__main__':
    app.run(debug=True)