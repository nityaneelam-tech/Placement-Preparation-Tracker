from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- DATABASE CONNECTION ----------
def get_db():
    return sqlite3.connect("database.db")

# ---------- INITIALIZE DATABASE ----------
def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS dsa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem TEXT,
            platform TEXT,
            difficulty TEXT,
            status TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            topic TEXT,
            status TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS mocktests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT,
            score INTEGER,
            date TEXT
        )
    """)

    db.commit()
    db.close()

# ---------- DASHBOARD ----------
@app.route("/")
def index():
    db = get_db()

    # Total counts
    total_dsa = db.execute("SELECT COUNT(*) FROM dsa").fetchone()[0]
    total_subjects = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    total_mocks = db.execute("SELECT COUNT(*) FROM mocktests").fetchone()[0]

    # Completed counts
    completed_dsa = db.execute(
        "SELECT COUNT(*) FROM dsa WHERE status='Solved'"
    ).fetchone()[0]

    completed_subjects = db.execute(
        "SELECT COUNT(*) FROM subjects WHERE status='Completed'"
    ).fetchone()[0]

    # Progress calculation
    dsa_progress = int((completed_dsa / total_dsa) * 100) if total_dsa else 0
    subject_progress = int((completed_subjects / total_subjects) * 100) if total_subjects else 0

    db.close()

    return render_template(
        "index.html",
        dsa=total_dsa,
        subjects=total_subjects,
        mocks=total_mocks,
        dsa_progress=dsa_progress,
        subject_progress=subject_progress
    )

# ---------- DSA PAGE ----------
@app.route("/dsa", methods=["GET", "POST"])
def dsa_page():
    db = get_db()

    if request.method == "POST":
        db.execute(
            "INSERT INTO dsa (problem, platform, difficulty, status) VALUES (?,?,?,?)",
            (
                request.form["problem"],
                request.form["platform"],
                request.form["difficulty"],
                request.form["status"]
            )
        )
        db.commit()

    # Filtering logic
    difficulty = request.args.get("difficulty")
    status = request.args.get("status")

    query = "SELECT * FROM dsa"
    params = []

    if difficulty or status:
        query += " WHERE 1=1"
        if difficulty:
            query += " AND difficulty=?"
            params.append(difficulty)
        if status:
            query += " AND status=?"
            params.append(status)

    data = db.execute(query, params).fetchall()
    db.close()

    return render_template("dsa.html", data=data)

# ---------- DELETE DSA ----------
@app.route("/delete/dsa/<int:id>")
def delete_dsa(id):
    db = get_db()
    db.execute("DELETE FROM dsa WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/dsa")

# ---------- SUBJECTS PAGE ----------
@app.route("/subjects", methods=["GET", "POST"])
def subjects_page():
    db = get_db()

    if request.method == "POST":
        db.execute(
            "INSERT INTO subjects (subject, topic, status) VALUES (?,?,?)",
            (
                request.form["subject"],
                request.form["topic"],
                request.form["status"]
            )
        )
        db.commit()

    data = db.execute("SELECT * FROM subjects").fetchall()
    db.close()

    return render_template("subjects.html", data=data)

# ---------- MOCK TESTS PAGE ----------
@app.route("/mocktests", methods=["GET", "POST"])
def mocktests_page():
    db = get_db()

    if request.method == "POST":
        db.execute(
            "INSERT INTO mocktests (test_name, score, date) VALUES (?,?,?)",
            (
                request.form["test_name"],
                request.form["score"],
                request.form["date"]
            )
        )
        db.commit()

    data = db.execute("SELECT * FROM mocktests").fetchall()

    avg_score = db.execute(
        "SELECT AVG(score) FROM mocktests"
    ).fetchone()[0]

    db.close()

    return render_template(
        "mocktests.html",
        data=data,
        avg_score=round(avg_score, 2) if avg_score else None
    )

# ---------- RUN APP ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
