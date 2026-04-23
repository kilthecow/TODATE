from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import calendar
from datetime import datetime

app = Flask(__name__)
DB_PATH = "todate.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo_date TEXT NOT NULL,
            content TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_todos(todo_date):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content, done FROM todos WHERE todo_date = ? ORDER BY id DESC",
        (todo_date,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_month_calendar(year, month):
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)
    return month_days

@app.route("/", methods=["GET"])
def index():
    today = datetime.today()

    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    selected_date = request.args.get("date", f"{year:04d}-{month:02d}-{today.day:02d}")
    
    todos = get_todos(selected_date) if selected_date else []
    month_days = get_month_calendar(year, month)

    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        "index.html", 
        selected_date=selected_date, 
        todos=todos,
        year=year,
        month=month,
        month_days=month_days,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month
    )


@app.route("/add", methods=["POST"])
def add():
    todo_date = request.form["todo_date"]
    content = request.form["content"]

    if todo_date and content.strip():
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO todos (todo_date, content, done) VALUES (?, ?, 0)",
            (todo_date, content)
        )
        conn.commit()
        conn.close()

    year, month, _ = todo_date.split("-")
    return redirect(url_for("index", date=todo_date, year=year, month=month))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    todo_date = request.form["todo_date"]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE todos
        SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (todo_id,))
    conn.commit()
    conn.close()
    
    year, month, _ = todo_date.split("-")
    return redirect(url_for("index", date=todo_date, year=year, month=month))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todo_date = request.form["todo_date"]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()

    year, month, _ = todo_date.split("-")
    return redirect(url_for("index", date=todo_date, year=year, month=month))

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
else:
    init_db()