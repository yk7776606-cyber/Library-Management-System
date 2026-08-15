from flask import Flask, render_template, request, redirect, session
from database import get_connection

from flask import make_response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

import os

app = Flask(__name__)
app.secret_key = "library_secret_key"


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("login.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()

    cur.close()
    con.close()

    if user:
        session["username"] = username
        return redirect("/dashboard")

    return "Invalid Username or Password"


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/")

    con = get_connection()
    cur = con.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    # Total Staff
    cur.execute("SELECT COUNT(*) FROM staff")
    total_staff = cur.fetchone()[0]

    # Total Books
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    # Total Issued Books
    cur.execute("SELECT COUNT(*) FROM issue_books WHERE status='Issued'")
    total_issued = cur.fetchone()[0]

    cur.close()
    con.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_staff=total_staff,
        total_books=total_books,
        total_issued=total_issued
    )

# ---------------- STUDENT MODULE ----------------

@app.route("/students")
def students():

    con = get_connection()
    cur = con.cursor()

    search = request.args.get("search", "")

    if search:
        cur.execute("""
            SELECT * FROM students
            WHERE name LIKE %s
            OR department LIKE %s
            OR year LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))
    else:
        cur.execute("SELECT * FROM students")

    data = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "student.html",
        students=data,
        search=search
    )


# ---------------- ADD STUDENT ----------------

@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form["name"]
    department = request.form["department"]
    year = request.form["year"]
    email = request.form["email"]
    phone = request.form["phone"]

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO students
        (name, department, year, email, phone)
        VALUES(%s,%s,%s,%s,%s)
    """,(name, department, year, email, phone))

    con.commit()

    cur.close()
    con.close()

    return redirect("/students")


# ---------------- EDIT STUDENT ----------------

@app.route("/edit_student/<int:id>")
def edit_student(id):

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cur.fetchone()

    cur.close()
    con.close()

    return render_template("edit_student.html", student=student)


# ---------------- UPDATE STUDENT ----------------

@app.route("/update_student/<int:id>", methods=["POST"])
def update_student(id):

    name = request.form["name"]
    department = request.form["department"]
    year = request.form["year"]
    email = request.form["email"]
    phone = request.form["phone"]

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE students
        SET name=%s,
            department=%s,
            year=%s,
            email=%s,
            phone=%s
        WHERE id=%s
    """,(name, department, year, email, phone, id))

    con.commit()

    cur.close()
    con.close()

    return redirect("/students")


# ---------------- DELETE STUDENT ----------------

@app.route("/delete_student/<int:id>")
def delete_student(id):

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM students WHERE id=%s",
        (id,)
    )

    con.commit()

    cur.close()
    con.close()

    return redirect("/students")


# ---------------- STAFF MODULE ----------------

@app.route("/staff", methods=["GET", "POST"])
def staff():

    con = get_connection()
    cur = con.cursor()

    # Add Staff
    if request.method == "POST":

        staff_name = request.form["staff_name"]
        department = request.form["department"]
        phone = request.form["phone"]
        email = request.form["email"]

        cur.execute("""
            INSERT INTO staff
            (staff_name, department, phone, email)
            VALUES(%s,%s,%s,%s)
        """, (staff_name, department, phone, email))

        con.commit()

        cur.close()
        con.close()

        return redirect("/staff")

    # Search
    search = request.args.get("search", "")

    if search:

        cur.execute("""
            SELECT * FROM staff
            WHERE staff_name LIKE %s
            OR department LIKE %s
            OR email LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cur.execute("SELECT * FROM staff")

    data = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "staff.html",
        staff=data,
        search=search
    )
   
# ---------------- BOOK MODULE ----------------

@app.route("/books")
def books():

    con = get_connection()
    cur = con.cursor()

    search = request.args.get("search", "")

    if search:

        cur.execute("""
            SELECT * FROM books
            WHERE book_name LIKE %s
            OR author LIKE %s
            OR category LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cur.execute("SELECT * FROM books")

    data = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "books.html",
        books=data,
        search=search
    )

# ---------------- ADD BOOK ----------------

@app.route("/add_book")
def add_book():
    return render_template("add_book.html")


@app.route("/add_book", methods=["POST"])
def save_book():

    name = request.form["book_name"]
    author = request.form["author"]
    category = request.form["category"]
    quantity = request.form["quantity"]

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO books
        (book_name, author, category, quantity, available_quantity)
        VALUES(%s,%s,%s,%s,%s)
    """, (name, author, category, quantity, quantity))

    con.commit()

    cur.close()
    con.close()

    return redirect("/books")

# ---------------- EDIT BOOK ----------------

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    con = get_connection()
    cur = con.cursor()

    if request.method == "POST":

        name = request.form["book_name"]
        author = request.form["author"]
        category = request.form["category"]
        quantity = request.form["quantity"]

        cur.execute("""
            UPDATE books
            SET book_name=%s,
                author=%s,
                category=%s,
                quantity=%s,
                available_quantity=%s
            WHERE book_id=%s
        """, (name, author, category, quantity, quantity, book_id))


        con.commit()

        cur.close()
        con.close()

        return redirect("/books")


    cur.execute(
        "SELECT * FROM books WHERE book_id=%s",
        (book_id,)
    )

    book = cur.fetchone()

    cur.close()
    con.close()

    return render_template("edit_book.html", book=book)

# ---------------- UPDATE BOOK ----------------

@app.route("/update_book/<int:book_id>", methods=["POST"])
def update_book(book_id):

    name = request.form["book_name"]
    author = request.form["author"]
    category = request.form["category"]

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE books
        SET book_name=%s,
            author=%s,
            category=%s
        WHERE book_id=%s
    """, (name, author, category, book_id))

    con.commit()

    cur.close()
    con.close()

    return redirect("/books")


# ---------------- DELETE BOOK ----------------

@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM books WHERE book_id=%s",
        (book_id,)
    )

    con.commit()

    cur.close()
    con.close()

    return redirect("/books")

# ---------------- ISSUE BOOK MODULE ----------------

@app.route("/issue_books")
def issue_books():

    if "username" not in session:
        return redirect("/")

    con = get_connection()
    cur = con.cursor()

    search = request.args.get("search", "")

    if search:

        cur.execute("""
            SELECT *
            FROM issue_books
            WHERE CAST(student_id AS TEXT) LIKE %s
            OR CAST(book_id AS TEXT) LIKE %s
            OR status LIKE %s
            ORDER BY issue_id
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cur.execute("""
            SELECT *
            FROM issue_books
            ORDER BY issue_id
        """)

    data = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "issue_books.html",
        issues=data,
        search=search
    )


# ---------------- ADD ISSUE ----------------

@app.route("/add_issue", methods=["POST"])
def add_issue():

    if "username" not in session:
        return redirect("/")

    student_id = request.form["student_id"]
    book_id = request.form["book_id"]
    issue_date = request.form["issue_date"]
    return_date = request.form["return_date"]
    status = request.form["status"]

    con = get_connection()
    cur = con.cursor()

    try:

        # Check Student
        cur.execute(
            "SELECT * FROM students WHERE id=%s",
            (student_id,)
        )
        student = cur.fetchone()

        if not student:
            cur.close()
            con.close()
            return "Invalid Student ID"

        # Check Book
        cur.execute(
            "SELECT * FROM books WHERE book_id=%s",
            (book_id,)
        )
        book = cur.fetchone()

        if not book:
            cur.close()
            con.close()
            return "Invalid Book ID"

        # Check Available Quantity
        cur.execute(
            "SELECT available_quantity FROM books WHERE book_id=%s",
            (book_id,)
        )

        available = cur.fetchone()[0]

        if available <= 0:
            cur.close()
            con.close()
            return "Book Not Available"

        # Insert Issue
        cur.execute("""
            INSERT INTO issue_books
            (student_id, book_id, issue_date, return_date, status)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            student_id,
            book_id,
            issue_date,
            return_date,
            status
        ))

        # Reduce Available Quantity
        cur.execute("""
            UPDATE books
            SET available_quantity = available_quantity - 1
            WHERE book_id=%s
        """, (book_id,))

        con.commit()

    except Exception as e:
        con.rollback()
        cur.close()
        con.close()
        return str(e)

    cur.close()
    con.close()

    return redirect("/issue_books")

# ---------------- RETURN BOOK MODULE ----------------

@app.route("/return", methods=["GET", "POST"])
def return_book():

    con = get_connection()
    cur = con.cursor()

    if request.method == "POST":

        book_id = request.form["book_id"]
        return_date = request.form["return_date"]

        # Check issued book exists
        cur.execute("""
            SELECT * FROM issue_books
            WHERE book_id=%s AND status='Issued'
        """, (book_id,))

        issue = cur.fetchone()


        if issue:

            # Update issue status
            cur.execute("""
                UPDATE issue_books
                SET status='Returned',
                    return_date=%s
                WHERE book_id=%s
                AND status='Issued'
            """, (return_date, book_id))


            # Increase book quantity
            cur.execute("""
                UPDATE books
                SET available_quantity = available_quantity + 1
                WHERE book_id=%s
            """, (book_id,))


            con.commit()


            cur.close()
            con.close()

            return """
            <script>
            alert('Book Returned Successfully');
            window.location.href='/return';
            </script>
            """


        else:

            cur.close()
            con.close()

            return """
            <script>
            alert('Book ID Not Found or Already Returned');
            window.location.href='/return';
            </script>
            """


    cur.close()
    con.close()

    return render_template("return.html")


# ---------------- EDIT STAFF ----------------

@app.route("/edit_staff/<int:staff_id>", methods=["GET", "POST"])
def edit_staff(staff_id):

    con = get_connection()
    cur = con.cursor()

    if request.method == "POST":

        staff_name = request.form["staff_name"]
        department = request.form["department"]
        phone = request.form["phone"]
        email = request.form["email"]

        cur.execute("""
            UPDATE staff
            SET staff_name=%s,
                department=%s,
                phone=%s,
                email=%s
            WHERE staff_id=%s
        """, (staff_name, department, phone, email, staff_id))

        con.commit()

        cur.close()
        con.close()

        return redirect("/staff")

    cur.execute(
        "SELECT * FROM staff WHERE staff_id=%s",
        (staff_id,)
    )

    staff = cur.fetchone()

    cur.close()
    con.close()

    return render_template("edit_staff.html", staff=staff)


# ---------------- DELETE STAFF ----------------

@app.route("/delete_staff/<int:staff_id>")
def delete_staff(staff_id):

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM staff WHERE staff_id=%s",
        (staff_id,)
    )

    con.commit()

    cur.close()
    con.close()

    return redirect("/staff")

# ---------------- STAFF ISSUE MODULE ----------------

@app.route("/staff_issue", methods=["GET", "POST"])
def staff_issue():

    con = get_connection()
    cur = con.cursor()

    if request.method == "POST":

        staff_id = request.form["staff_id"].strip()
        book_id = request.form["book_id"].strip()
        issue_date = request.form["issue_date"]
        return_date = request.form["return_date"]
        status = request.form["status"]

        try:

            # Check Staff ID
            cur.execute(
                "SELECT * FROM staff WHERE staff_id=%s",
                (staff_id,)
            )
            staff = cur.fetchone()

            if not staff:
                cur.close()
                con.close()
                return "Invalid Staff ID"

            # Check Book ID
            cur.execute(
                "SELECT * FROM books WHERE book_id=%s",
                (book_id,)
            )
            book = cur.fetchone()

            if not book:
                cur.close()
                con.close()
                return "Invalid Book ID"

            # Insert Staff Issue
            cur.execute("""
                INSERT INTO staff_issue
                (staff_id, book_id, issue_date, return_date, status)
                VALUES(%s,%s,%s,%s,%s)
            """, (
                staff_id,
                book_id,
                issue_date,
                return_date,
                status
            ))

            # Reduce Available Quantity
            cur.execute("""
                UPDATE books
                SET available_quantity = available_quantity - 1
                WHERE book_id=%s
            """, (book_id,))

            con.commit()

            cur.close()
            con.close()

            return redirect("/staff_issue")

        except Exception as e:

            con.rollback()

            cur.close()
            con.close()

            return f"Error : {e}"

    # ---------- SEARCH ----------

    search = request.args.get("search", "")

    if search:

        cur.execute("""
            SELECT * FROM staff_issue
            WHERE CAST(staff_id AS CHAR) LIKE %s
            OR CAST(book_id AS CHAR) LIKE %s
            OR status LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cur.execute("SELECT * FROM staff_issue")

    issues = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "staff_issue.html",
        issues=issues,
        search=search
    )

# ---------------- REPORTS ----------------

@app.route("/reports")
def reports():

    if "username" not in session:
        return redirect("/")

    con = get_connection()
    cur = con.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    # Total Staff
    cur.execute("SELECT COUNT(*) FROM staff")
    total_staff = cur.fetchone()[0]

    # Total Books
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    # Available Books
    cur.execute("SELECT SUM(available_quantity) FROM books")
    result = cur.fetchone()
    available_books = result[0] if result[0] is not None else 0

    # Student Issued Books
    cur.execute("SELECT COUNT(*) FROM issue_books WHERE status='Issued'")
    issued_books = cur.fetchone()[0]

    # Returned Books
    cur.execute("SELECT COUNT(*) FROM issue_books WHERE status='Returned'")
    returned_books = cur.fetchone()[0]

    # Staff Issued Books
    cur.execute("SELECT COUNT(*) FROM staff_issue")
    staff_issued = cur.fetchone()[0]

    cur.close()
    con.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        total_staff=total_staff,
        total_books=total_books,
        available_books=available_books,
        issued_books=issued_books,
        returned_books=returned_books,
        staff_issued=staff_issued
    )

# ---------------- DOWNLOAD REPORT PDF ----------------

@app.route("/download_report")
def download_report():

    if "username" not in session:
        return redirect("/")

    con = get_connection()
    cur = con.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    # Total Staff
    cur.execute("SELECT COUNT(*) FROM staff")
    total_staff = cur.fetchone()[0]

    # Total Books
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    # Available Books
    cur.execute("SELECT SUM(available_quantity) FROM books")
    result = cur.fetchone()
    available_books = result[0] if result[0] else 0

    # Student Issued Books
    cur.execute("SELECT COUNT(*) FROM issue_books WHERE status='Issued'")
    issued_books = cur.fetchone()[0]

    # Returned Books
    cur.execute("SELECT COUNT(*) FROM issue_books WHERE status='Returned'")
    returned_books = cur.fetchone()[0]

    # Staff Issued Books
    cur.execute("SELECT COUNT(*) FROM staff_issue")
    staff_issued = cur.fetchone()[0]

    cur.close()
    con.close()

    # ==========================
    # CREATE PDF
    # ==========================

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter

    pdf.setTitle("Library Management Report")

    # ==========================
    # BORDER
    # ==========================

    pdf.setLineWidth(2)
    pdf.rect(20, 20, width - 40, height - 40)

    pdf.setLineWidth(1)
    pdf.rect(30, 30, width - 60, height - 60)

    # ==========================
    # TITLE
    # ==========================

    pdf.setFont("Helvetica-Bold", 22)

    pdf.drawCentredString(
        width / 2,
        730,
        "LIBRARY MANAGEMENT REPORT"
    )

    pdf.setLineWidth(1)
    pdf.line(150, 718, 462, 718)

    # ==========================
    # CONTENT
    # ==========================

    pdf.setFont("Helvetica", 14)

    y = 660

    pdf.drawString(
        80, y,
        f"Total Students : {total_students}"
    )
    y -= 45

    pdf.drawString(
        80, y,
        f"Total Staff : {total_staff}"
    )
    y -= 45

    pdf.drawString(
        80, y,
        f"Total Books : {total_books}"
    )
    y -= 45

    pdf.drawString(
        80, y,
        f"Available Books : {available_books}"
    )
    y -= 45

    pdf.drawString(
        80, y,
        f"Student Issued Books : {issued_books}"
    )
    y -= 45

    pdf.drawString(
        80, y,
        f"Returned Books : {returned_books}"
    )
    y -= 45

    pdf.drawString(
        80, y,
        f"Staff Issued Books : {staff_issued}"
    )

    # ==========================
    # LIBRARIAN SEAL
    # ==========================

    seal_path = os.path.join(
        os.path.dirname(__file__),
        "static",
        "images",
        "librarian_seal.png"
    )

    if os.path.exists(seal_path):

        seal_width = 110
        seal_height = 110

        seal_x = (width - seal_width) / 2 - 30
        seal_y = 75

        pdf.drawImage(
            seal_path,
            seal_x,
            seal_y,
            width=seal_width,
            height=seal_height,
            preserveAspectRatio=True,
            mask="auto"
        )

        pdf.setFont("Helvetica-Bold", 11)

        pdf.drawCentredString(
            width / 2,
            62,
            "Librarian Seal"
        )

    # ==========================
    # FOOTER
    # ==========================

    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawCentredString(
        width / 2,
        40,
        "Generated by Library Management System"
    )

    # ==========================
    # SAVE PDF
    # ==========================

    pdf.save()

    buffer.seek(0)

    response = make_response(buffer.getvalue())

    response.headers["Content-Type"] = "application/pdf"

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=Library_Report.pdf"

    return response

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)