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


if __name__=='__main__':
    app.run(debug=True)