from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY,
            task TEXT,
            start_time TEXT,
            weekday TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()

    if request.method == 'POST':
        task = request.form['task']
        start_time = request.form['start_time']
        weekday = request.form['weekday']
        c.execute('INSERT INTO todos (task, start_time, weekday) VALUES (?, ?, ?)', (task, start_time, weekday))
        conn.commit()
        return redirect('/')

    c.execute('SELECT id, task, start_time, weekday, done FROM todos ORDER BY start_time')
    tasks = c.fetchall()
    conn.close()

    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    hours = [f"{h:02d}:00" for h in range(8, 24)]
    schedule = {h: {d: [] for d in weekdays} for h in hours}

    for task in tasks:
        h = task[2][:2] + ":00"
        d = task[3]
        if h in schedule and d in schedule[h]:
            schedule[h][d].append(task)

    return render_template('index.html', schedule=schedule, weekdays=weekdays, hours=hours)


@app.route('/done/<int:todo_id>')
def mark_done(todo_id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('UPDATE todos SET done = 1 - done WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)