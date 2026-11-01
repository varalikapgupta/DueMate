
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG, SECRET_KEY
from datetime import date
from functools import wraps
import mysql.connector

app = Flask(__name__)

# Replace this with a newly generated secret key
app.secret_key = "b16bf9bc24ec628a196613b5463ab137e77b483a661c5a5d7ce67d162ec74377"


# DATABASE CONNECTION
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# LOGIN PROTECTION
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


# HOME
@app.route("/")
def home():
    if "student_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or len(password) < 6:
            flash("Please enter valid details.")
            return redirect("/register")

        db = get_db()
        cursor = db.cursor()

        try:
            hashed = generate_password_hash(password)

            cursor.execute(
                """INSERT INTO students(name,email,password)
                   VALUES(%s,%s,%s)""",
                (name, email, hashed)
            )

            db.commit()
            flash("Registration successful!")
            return redirect("/login")

        except mysql.connector.IntegrityError:
            flash("Email already registered!")

        finally:
            cursor.close()
            db.close()

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM students WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["student_id"] = user["student_id"]
            session["name"] = user["name"]
            return redirect("/dashboard")

        flash("Invalid email or password!")

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    student_id = session["student_id"]
    today = date.today()

    # SEARCH AND FILTER VALUES
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    subject_filter = request.args.get("subject", "").strip()
    sort = request.args.get("sort", "earliest").strip()

    sort_options = {
        "earliest": "a.due_date ASC",
        "latest": "a.due_date DESC",
        "alphabetical": "a.title ASC"
    }
    sort = sort if sort in sort_options else "earliest"

    query = """
        SELECT a.*, s.subject_name
        FROM assignments a
        JOIN subjects s ON a.subject_id = s.subject_id
        WHERE a.student_id = %s
    """

    params = [student_id]

    if search:
        query += " AND a.title LIKE %s"
        params.append("%" + search + "%")

    if status_filter in ["Pending", "In Progress", "Completed"]:
        query += " AND a.status = %s"
        params.append(status_filter)

    if subject_filter:
        query += " AND s.subject_name LIKE %s"
        params.append("%" + subject_filter + "%")

    query += " ORDER BY " + sort_options[sort]

    cursor.execute(query, tuple(params))
    assignments = cursor.fetchall()

    # DEADLINE ALERT SYSTEM
    for assignment in assignments:

        if assignment["status"] != "Completed":

            days_left = (assignment["due_date"] - today).days

            if days_left == 2:
                assignment["alert"] = "Reminder: Due in 2 days"

            elif days_left == 1:
                assignment["alert"] = "Due tomorrow"

            elif days_left == 0:
                assignment["alert"] = "Due today"

            elif days_left < 0:
                assignment["alert"] = "Overdue"

            else:
                assignment["alert"] = ""

        else:
            assignment["alert"] = ""

    # DASHBOARD STATISTICS
    total = len(assignments)

    completed = sum(
        a["status"] == "Completed" for a in assignments
    )

    pending = sum(
        a["status"] == "Pending" for a in assignments
    )

    in_progress = sum(
        a["status"] == "In Progress" for a in assignments
    )

    overdue = sum(
        a["due_date"] < today and a["status"] != "Completed"
        for a in assignments
    )

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        assignments=assignments,
        total=total,
        completed=completed,
        pending=pending,
        in_progress=in_progress,
        overdue=overdue,
        today=today.isoformat(),
        search=search,
        status_filter=status_filter,
        subject_filter=subject_filter,
        sort=sort
    )


# ADD ASSIGNMENT
@app.route("/add", methods=["POST"])
@login_required
def add_assignment():

    title = request.form["title"].strip()
    subject = request.form["subject"].strip()
    description = request.form.get("description", "").strip()
    due_date = request.form["due_date"]

    if not title or not subject or not due_date:
        flash("Please fill all required fields.")
        return redirect("/dashboard")

    try:
        deadline = date.fromisoformat(due_date)

        if deadline < date.today():
            flash("Deadline cannot be in the past.")
            return redirect("/dashboard")

    except ValueError:
        flash("Invalid deadline.")
        return redirect("/dashboard")

    db = get_db()
    cursor = db.cursor()

    student_id = session["student_id"]

    try:
        cursor.execute("""
            INSERT INTO subjects(subject_name, student_id)
            VALUES(%s, %s)
            ON DUPLICATE KEY UPDATE
            subject_id = LAST_INSERT_ID(subject_id)
        """, (subject, student_id))

        subject_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO assignments
            (title, description, subject_id, student_id, due_date)
            VALUES(%s, %s, %s, %s, %s)
        """, (
            title,
            description,
            subject_id,
            student_id,
            deadline
        ))

        db.commit()
        flash("Assignment added successfully!")

    except mysql.connector.Error:
        db.rollback()
        flash("Unable to add assignment.")

    finally:
        cursor.close()
        db.close()

    return redirect("/dashboard")


# UPDATE STATUS
@app.route("/update/<int:assignment_id>", methods=["POST"])
@login_required
def update_assignment(assignment_id):

    status = request.form["status"]

    if status not in ["Pending", "In Progress", "Completed"]:
        flash("Invalid status.")
        return redirect("/dashboard")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE assignments
        SET status = %s
        WHERE assignment_id = %s AND student_id = %s
    """, (
        status,
        assignment_id,
        session["student_id"]
    ))

    db.commit()
    cursor.close()
    db.close()

    flash("Assignment status updated!")
    return redirect("/dashboard")


# DELETE ASSIGNMENT
@app.route("/delete/<int:assignment_id>", methods=["POST"])
@login_required
def delete_assignment(assignment_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM assignments
        WHERE assignment_id = %s AND student_id = %s
    """, (
        assignment_id,
        session["student_id"]
    ))

    db.commit()
    cursor.close()
    db.close()

    flash("Assignment deleted!")
    return redirect("/dashboard")


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
