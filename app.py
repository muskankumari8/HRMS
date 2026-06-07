from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)
import os
import sqlite3
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Gemini API setup
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hrms_secret")

@app.route("/login", methods=["GET","POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        users = {

            "admin": {
                "password":"123",
                "role":"Admin"
            },

            "hr": {
                "password":"123",
                "role":"HR Recruiter"
            },

            "manager": {
                "password":"123",
                "role":"Senior Manager"
            },

            "employee": {
                "password":"123",
                "role":"Employee"
            }

        }

        if username in users:

            if (
                users[username]["password"] == password
                and
                users[username]["role"] == role
            ):

                session["role"] = role

                if role == "Admin":

                    return redirect("/")

                elif role == "HR Recruiter":

                    return redirect("/hr-dashboard")

                elif role == "Senior Manager":

                    return redirect("/manager-dashboard")

                else:

                    return redirect("/employee-dashboard")

        message = "Invalid Credentials"

    return render_template(
        "login.html",
        message=message
    )


@app.route("/hr-dashboard")
def hr_dashboard():

    return render_template(
        "hr_dashboard.html"
    )

@app.route("/manager-dashboard")
def manager_dashboard():

    return render_template(
        "manager_dashboard.html"
    )


@app.route("/employee-dashboard")
def employee_dashboard():

    return render_template(
        "employee_dashboard.html"
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")



@app.route("/employees", methods=["GET", "POST"])
def employees():
    if "role" not in session:

        return redirect("/login")

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        salary = request.form["salary"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO employees(name,email,department,salary) VALUES(?,?,?,?)",
            (name, email, department, salary)
        )

        conn.commit()
        conn.close()

        message = "Employee Added Successfully!"

    return render_template("employees.html", message=message)


@app.route("/resumes", methods=["GET", "POST"])
def resume_screening():
    if "role" not in session:

        return redirect("/login")

    result = ""

    if request.method == "POST":

        try:

            # Job Description from textarea
            job_description = request.form["job_description"]

            # Uploaded PDF file
            uploaded_file = request.files["resume"]

            # Read PDF
            reader = PdfReader(uploaded_file)

            resume_text = ""

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    resume_text += text

            # Gemini Prompt
            prompt = f"""
            You are an expert HR recruiter.

            Analyze the candidate resume against the job description.

            Job Description:
            {job_description}

            Resume:
            {resume_text}

            Provide:

            1. Match Score (0-100)
            2. Technical Skills Found
            3. Missing Skills
            4. Candidate Strengths
            5. Recommendation (Shortlist / Hold / Reject)
            6. Reasoning

            Return the response in plain text only.
            Do NOT use markdown formatting.
            Do NOT use *, **, #, or bullet symbols.
            """


            response = model.generate_content(prompt)

            result = response.text

        except Exception as e:

            result = f"Error: {str(e)}"

    return render_template(
        "resumes.html",
        result=result
    )

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if "role" not in session:

        return redirect("/login")

    answer = ""

    if request.method == "POST":

        question = request.form["question"]

        prompt = f"""
        You are an HR assistant.

        Answer the following HR-related question professionally.

        Question:
        {question}

        Return plain text only.
        Do not use markdown.
        """

        try:

            response = model.generate_content(prompt)

            answer = response.text.replace("*", "")

        except Exception as e:

            answer = f"Error: {str(e)}"

    return render_template(
        "chatbot.html",
        answer=answer
    )

@app.route("/interview", methods=["GET", "POST"])
def interview():
    if "role" not in session:

        return redirect("/login")

    skill = ""
    question = ""
    result = ""

    if request.method == "POST":

        action = request.form.get("action")

        if action == "generate":

            skill = request.form["skill"]

            prompt = f"""
            Generate one professional interview question
            for a candidate applying for a {skill} role.

            Return only the question.
            """

            try:

                response = model.generate_content(prompt)

                question = response.text.strip()

            except Exception as e:

                question = f"Error: {str(e)}"

        elif action == "evaluate":

            skill = request.form["skill"]

            question = request.form["question"]

            answer = request.form["answer"]

            prompt = f"""
            You are an expert interviewer.

            Question:
            {question}

            Candidate Answer:
            {answer}

            Evaluate the answer and provide:

            Technical Knowledge Score (0-100)

            Communication Score (0-100)

            Problem Solving Score (0-100)

            Overall Score (0-100)

            Recommendation:
            Hire / Consider / Reject

            Reasoning

            Return plain text only.
            Do not use markdown.
            """

            try:

                response = model.generate_content(prompt)

                result = (
                    response.text
                    .replace("*", "")
                    .strip()
                )

            except Exception as e:

                result = f"Error: {str(e)}"

    return render_template(
        "interview.html",
        skill=skill,
        question=question,
        result=result
    )


@app.route("/employee_list")
def employee_list():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM employees")

    employees = cur.fetchall()

    conn.close()

    return render_template(
        "employee_list.html",
        employees=employees
    )

@app.route("/delete-employee/<int:id>")
def delete_employee(id):

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM employees WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/employee_list")


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Fetch employee names
    cur.execute("SELECT name FROM employees")

    employees = cur.fetchall()

    message = ""

    if request.method == "POST":

        employee_name = request.form["employee_name"]
        date = request.form["date"]
        status = request.form["status"]

        cur.execute(
            """
            INSERT INTO attendance
            (employee_name,date,status)
            VALUES(?,?,?)
            """,
            (employee_name, date, status)
        )

        conn.commit()

        message = "Attendance Marked Successfully"

    conn.close()

    return render_template(
        "attendance.html",
        employees=employees,
        message=message
    )

@app.route("/attendance_list")
def attendance_list():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM attendance
        ORDER BY date DESC
    """)

    attendance_records = cur.fetchall()

    conn.close()

    return render_template(
        "attendance_list.html",
        attendance_records=attendance_records
    )

@app.route("/delete-attendance/<int:id>")
def delete_attendance(id):

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM attendance WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect("/attendance_list")

@app.route("/attendance_dashboard")
def attendances_dashboard():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Total Employees
    cur.execute("SELECT COUNT(*) FROM employees")
    total_employees = cur.fetchone()[0]

    # Present
    cur.execute(
        "SELECT COUNT(*) FROM attendance WHERE status='Present'"
    )
    present = cur.fetchone()[0]

    # Absent
    cur.execute(
        "SELECT COUNT(*) FROM attendance WHERE status='Absent'"
    )
    absent = cur.fetchone()[0]

    # Work From Home
    cur.execute(
        "SELECT COUNT(*) FROM attendance WHERE status='Work From Home'"
    )
    wfh = cur.fetchone()[0]

    # Leave
    cur.execute(
        "SELECT COUNT(*) FROM attendance WHERE status='Leave'"
    )
    leave = cur.fetchone()[0]

    conn.close()

    return render_template(
        "attendance_dashboard.html",
        total_employees=total_employees,
        present=present,
        absent=absent,
        wfh=wfh,
        leave=leave
    )

@app.route("/payroll", methods=["GET", "POST"])
def payroll():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT name,salary FROM employees")

    employees = cur.fetchall()

    message = ""

    if request.method == "POST":

        employee_name = request.form["employee_name"]

        basic_salary = float(
            request.form["basic_salary"]
        )

        bonus = float(
            request.form["bonus"]
        )

        deduction = float(
            request.form["deduction"]
        )

        net_salary = (
            basic_salary
            + bonus
            - deduction
        )

        cur.execute(
            """
            INSERT INTO payroll
            (
                employee_name,
                basic_salary,
                bonus,
                deduction,
                net_salary
            )
            VALUES(?,?,?,?,?)
            """,
            (
                employee_name,
                basic_salary,
                bonus,
                deduction,
                net_salary
            )
        )

        conn.commit()

        message = (
            f"Payroll Generated. "
            f"Net Salary = ₹{net_salary}"
        )

    conn.close()

    return render_template(
        "payroll.html",
        employees=employees,
        message=message
    )

@app.route("/payroll_list")
def payroll_list():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM payroll")

    payrolls = cur.fetchall()

    conn.close()

    return render_template(
        "payroll_list.html",
        payrolls=payrolls
    )

@app.route("/performance", methods=["GET","POST"])
def performance():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM employees"
    )

    employees = cur.fetchall()

    result = ""

    if request.method == "POST":

        employee_name = request.form["employee_name"]

        attendance = float(
            request.form["attendance"]
        )

        task = float(
            request.form["task"]
        )

        feedback = float(
            request.form["feedback"]
        )

        performance_score = (
            attendance * 0.4
            +
            task * 0.3
            +
            feedback * 0.3
        )

        if performance_score >= 85:

            level = "Excellent"

        elif performance_score >= 70:

            level = "Good"

        elif performance_score >= 50:

            level = "Average"

        else:

            level = "Poor"

        cur.execute(
            """
            INSERT INTO performance(

                employee_name,
                attendance_score,
                task_score,
                feedback_score,
                performance_score,
                performance_level

            )

            VALUES(?,?,?,?,?,?)
            """,
            (
                employee_name,
                attendance,
                task,
                feedback,
                performance_score,
                level
            )
        )

        conn.commit()

        result = (
            f"Performance Score: "
            f"{round(performance_score,2)} | "
            f"Level: {level}"
        )

    conn.close()

    return render_template(
        "performance.html",
        employees=employees,
        result=result
    )

@app.route("/performance_list")
def performance_list():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM performance"
    )

    records = cur.fetchall()

    conn.close()

    return render_template(
        "performance_list.html",
        records=records
    )

@app.route("/attrition", methods=["GET", "POST"])
def attrition():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM employees"
    )

    employees = cur.fetchall()

    result = ""

    if request.method == "POST":

        employee_name = request.form["employee_name"]

        overtime = request.form["overtime"]

        try:

            # Salary

            cur.execute(
                """
                SELECT salary
                FROM employees
                WHERE name=?
                """,
                (employee_name,)
            )

            salary_data = cur.fetchone()

            salary = (
                salary_data[0]
                if salary_data
                else 0
            )

            # Performance

            cur.execute(
                """
                SELECT performance_score
                FROM performance
                WHERE employee_name=?
                ORDER BY id DESC
                LIMIT 1
                """,
                (employee_name,)
            )

            performance_data = cur.fetchone()

            performance = (
                performance_data[0]
                if performance_data
                else 0
            )

            # Attendance %

            cur.execute(
                """
                SELECT COUNT(*)
                FROM attendance
                WHERE employee_name=?
                """,
                (employee_name,)
            )

            total = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*)
                FROM attendance
                WHERE employee_name=?
                AND status='Present'
                """,
                (employee_name,)
            )

            present = cur.fetchone()[0]

            if total > 0:

                attendance_score = (
                    present / total
                ) * 100

            else:

                attendance_score = 0

            prompt = f"""
            You are an HR Analytics Expert.

            Employee:
            {employee_name}

            Attendance Score:
            {attendance_score}

            Performance Score:
            {performance}

            Salary:
            {salary}

            Overtime Hours:
            {overtime}

            Provide:

            Attrition Risk (%)

            Prediction:
            Likely To Stay
            OR
            Likely To Leave

            Reason

            Return plain text only.
            """

            response = model.generate_content(prompt)

            result = (
                response.text
                .replace("*","")
                .strip()
            )

        except Exception as e:

            result = str(e)

    conn.close()

    return render_template(
        "attrition.html",
        employees=employees,
        result=result
    )

@app.route("/")
def dashboard():
    if "role" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Total Employees
    cur.execute(
        "SELECT COUNT(*) FROM employees"
    )
    total_employees = cur.fetchone()[0]

    # Attendance Records
    cur.execute(
        "SELECT COUNT(*) FROM attendance"
    )
    total_attendance = cur.fetchone()[0]

    # Payroll Records
    cur.execute(
        "SELECT COUNT(*) FROM payroll"
    )
    total_payroll = cur.fetchone()[0]

    # Performance Records
    cur.execute(
        "SELECT COUNT(*) FROM performance"
    )
    total_performance = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_attendance=total_attendance,
        total_payroll=total_payroll,
        total_performance=total_performance
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)