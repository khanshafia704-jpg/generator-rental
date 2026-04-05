import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__, template_folder="templates")
app.secret_key = "secretkey"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- DATABASE SETUP ---------------- #
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT
    )
    """)

    # BOOKINGS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        generator TEXT,
        days INTEGER,
        total INTEGER,
        status TEXT
    )
    """)

    # PAYMENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        generator TEXT,
        days INTEGER,
        total INTEGER,
        address TEXT,
        city TEXT,
        transaction_id TEXT,
        screenshot TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


# CALL FUNCTION
init_db()
# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("home.html")

# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            flash("Email already exists!", "error")
            conn.close()
            return redirect(url_for("register"))

        cursor.execute(
            "INSERT INTO users (name,email,phone,password) VALUES (?,?,?,?)",
            (name,email,phone,password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user[2]
            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid Credentials!", "error")

    return render_template("login.html")


@app.route("/admin")
def admin():
    import sqlite3
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
    except:
        users = []

    try:
        cur.execute("SELECT * FROM bookings")
        bookings = cur.fetchall()
    except:
        bookings = []

    try:
        cur.execute("SELECT * FROM payments")
        payments = cur.fetchall()
    except:
        payments = []

    conn.close()

    return render_template("admin.html", users=users, bookings=bookings, payments=payments)

@app.route("/delete_booking/<int:id>")
def delete_booking(id):
    import sqlite3
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM bookings WHERE id = ?", (id,))
    
    conn.commit()
    conn.close()

    return redirect("/admin")
        

   

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

# ---------------- CUSTOMER DETAILS ---------------- #

@app.route("/customer", methods=["GET","POST"])
def customer():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        session["address"] = request.form["address"]
        session["city"] = request.form["city"]

        return redirect(url_for("rent"))

    return render_template("customer-details.html")


# ---------------- RENT ---------------- #

@app.route("/rent", methods=["GET","POST"])
def rent():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        generator = request.form["generator"]
        days = int(request.form["days"])

        prices = {
            "5KVA":500,
            "10KVA":1000,
            "20KVA":2000,
            "30KVA":3000,
            "50KVA":4000,
            "75KVA":5500,
            "100KVA":7000,
            "150KVA":9000,
            "200KVA":12000
        }

        price_per_day = prices.get(generator,2000)
        total = price_per_day * days

        session["generator"] = generator
        session["days"] = days
        session["total"] = total

        return redirect(url_for("payment"))

    return render_template("rent.html")

# ---------------- PAYMENT ---------------- #
@app.route("/payment", methods=["GET","POST"])
def payment():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        transaction_id = request.form.get("payment_ref")
        screenshot = request.files.get("screenshot")

        status = "Success"

        if not transaction_id or len(transaction_id) < 8:
            status = "Failed"

        if not screenshot or screenshot.filename == "":
            status = "Failed"

        filename = ""

        if screenshot and screenshot.filename != "":
            ext = screenshot.filename.rsplit(".",1)[-1].lower()

            if ext not in ["jpg","jpeg","png"]:
                status = "Failed"

            filename = str(uuid.uuid4()) + "_" + screenshot.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            screenshot.save(filepath)

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # ✅ PAYMENT INSERT
        cursor.execute("""
        INSERT INTO payments
        (user_email,generator,days,total,address,city,transaction_id,screenshot,status)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,(session["user"],
            session.get("generator"),
            session.get("days"),
            session.get("total"),
            session.get("address"),
            session.get("city"),
            transaction_id,
            filename,
            status
        ))

        # ✅ BOOKING INSERT (MAIN FIX)
        cursor.execute("""
        INSERT INTO bookings (user, generator, days, total, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            session["user"],
            session.get("generator"),
            session.get("days"),
            session.get("total"),
            status
        ))

        conn.commit()
        conn.close()

        if status == "Success":
            flash("Payment Successful!", "success")
            return redirect(url_for("payment_success"))

        flash("Payment Failed!", "error")
        return redirect(url_for("payment"))

    return render_template("payment.html", amount=session.get("total"))

# ---------------- CONTACT ---------------- #

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------------- SUCCESS ---------------- #

@app.route("/payment_success")
def payment_success():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("success.html")

@app.route("/my_bookings")
def my_bookings():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT generator, days, total, status FROM payments WHERE user_email=?",
        (session["user"],)
    )

    bookings = cursor.fetchall()
    conn.close()

    return render_template("bookings.html", bookings=bookings)
# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()
    flash("Logged Out Successfully!", "success")

    return redirect(url_for("home"))

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
