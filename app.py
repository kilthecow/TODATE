from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import calendar
from datetime import datetime, date

app = Flask(__name__)
DB_PATH = "todate.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content, done FROM todos WHERE todo_date = ? ORDER BY id DESC",
        (todo_date,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_month_calendar(year, month, selected_date):
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    month_days = cal.monthdatescalendar(year, month)

    calendar_data = []
    today = date.today()

    for week in month_days:
        week_data = []
        for day in week:
            week_data.append({
                "date_str": day.strftime("%Y-%m-%d"),
                "day": day.day,
                "is_current_month": (day.month == month),
                "is_today": (day == today),
                "is_selected": (day.strftime("%Y-%m-%d") == selected_date)
            })
        calendar_data.append(week_data)

    return calendar_data


@app.route("/", methods=["GET"])
def index():
    today = date.today()

    selected_date = request.args.get("date")
    month_str = request.args.get("month")

    if month_str:
        try:
            current_month_date = datetime.strptime(month_str, "%Y-%m").date()
        except ValueError:
            current_month_date = today.replace(day=1)
    else:
        if selected_date:
            try:
                current_month_date = datetime.strptime(selected_date, "%Y-%m-%d").date().replace(day=1)
            except ValueError:
                current_month_date = today.replace(day=1)
        else:
            current_month_date = today.replace(day=1)

    if not selected_date:
        selected_date = today.strftime("%Y-%m-%d")

    year = current_month_date.year
    month = current_month_date.month

    todos = get_todos(selected_date)
    calendar_data = get_month_calendar(year, month, selected_date)

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
        calendar_data=calendar_data,
        current_year=year,
        current_month=month,
        current_month_str=f"{year}-{month:02d}",
        prev_month_str=f"{prev_year}-{prev_month:02d}",
        next_month_str=f"{next_year}-{next_month:02d}"
    )


@app.route("/add", methods=["POST"])
def add():
    todo_date = request.form["todo_date"]
    content = request.form["content"].strip()

    if todo_date and content:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO todos (todo_date, content, done) VALUES (?, ?, 0)",
            (todo_date, content)
        )
        conn.commit()
        conn.close()

    month_str = todo_date[:7]
    return redirect(url_for("index", date=todo_date, month=month_str))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    todo_date = request.form["todo_date"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE todos
        SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (todo_id,))
    conn.commit()
    conn.close()

    month_str = todo_date[:7]
    return redirect(url_for("index", date=todo_date, month=month_str))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todo_date = request.form["todo_date"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()

    month_str = todo_date[:7]
    return redirect(url_for("index", date=todo_date, month=month_str))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
else:
    init_db()