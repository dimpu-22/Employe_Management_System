
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection

from reportlab.platypus import SimpleDocTemplate, Table
from flask import send_file

import openpyxl
from flask import send_file

app = Flask(__name__)
app.secret_key = "employee_secret_key"


@app.route("/employees")
def employees():

    if "admin" not in session:
        return redirect("/")

    conn = get_connection()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return render_template("employees.html", employees=employees)

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        designation = request.form["designation"]
        salary = request.form["salary"]
        joining_date = request.form["joining_date"]
        
        if not all([name, email, phone, department, designation, salary, joining_date]):
            flash("All fields are required.")
            return redirect("/add_employee")
        
        conn = get_connection()

        conn.execute(
            """
            INSERT INTO employees
            (name,email,phone,department,designation,salary,joining_date)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                name,
                email,
                phone,
                department,
                designation,
                salary,
                joining_date,
            ),
        )

        conn.commit()
        conn.close()

        return redirect("/employees")

    return render_template("add_employee.html")

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()

        admin = conn.execute(
            "SELECT * FROM admin WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin"] = username
            return redirect("/dashboard")

        flash("Invalid Username or Password")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/")

    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    conn.close()

    return render_template("dashboard.html", total=total)

@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "admin" not in session:
        return redirect("/")

    conn = get_connection()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        designation = request.form["designation"]
        salary = request.form["salary"]
        joining_date = request.form["joining_date"]

        conn.execute("""
        UPDATE employees
        SET
        name=?,
        email=?,
        phone=?,
        department=?,
        designation=?,
        salary=?,
        joining_date=?
        WHERE id=?
        """,
        (
            name,
            email,
            phone,
            department,
            designation,
            salary,
            joining_date,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/employees")

    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )
    
@app.route("/delete_employee/<int:id>")
def delete_employee(id):

    if "admin" not in session:
        return redirect("/")

    conn = get_connection()

    conn.execute(
        "DELETE FROM employees WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/employees")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/export_excel")
def export_excel():

    if "admin" not in session:
        return redirect("/")

    conn = get_connection()

    employees = conn.execute("SELECT * FROM employees").fetchall()

    conn.close()

    workbook = openpyxl.Workbook()

    sheet = workbook.active

    sheet.title = "Employees"

    sheet.append([
        "ID",
        "Name",
        "Email",
        "Phone",
        "Department",
        "Designation",
        "Salary",
        "Joining Date"
    ])

    for employee in employees:

        sheet.append([
            employee["id"],
            employee["name"],
            employee["email"],
            employee["phone"],
            employee["department"],
            employee["designation"],
            employee["salary"],
            employee["joining_date"]
        ])

    workbook.save("employees.xlsx")

    return send_file(
        "employees.xlsx",
        as_attachment=True
    )
    
@app.route("/export_pdf")
def export_pdf():

    if "admin" not in session:
        return redirect("/")

    conn = get_connection()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    pdf = SimpleDocTemplate("employees.pdf")

    data = [["ID","Name","Email","Department"]]

    for emp in employees:
        data.append([
            emp["id"],
            emp["name"],
            emp["email"],
            emp["department"]
        ])

    table = Table(data)
    pdf.build([table])

    return send_file("employees.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)