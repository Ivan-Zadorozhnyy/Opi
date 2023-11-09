import sqlite3
import uuid
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE_NAME = 'reports.db'

def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id TEXT PRIMARY KEY
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserActivity (
        user_id TEXT NOT NULL,
        online_time INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ReportsConfiguration (
        report_name TEXT PRIMARY KEY,
        metrics TEXT NOT NULL,
        user_ids TEXT NOT NULL
    )''')
    cursor.execute('DELETE FROM Users')
    user_ids = [str(uuid.uuid4()) for _ in range(30)]
    cursor.executemany('INSERT INTO Users (id) VALUES (?)', [(user_id,) for user_id in user_ids])
    cursor.execute('DELETE FROM UserActivity')
    today = datetime.now().date()
    for user_id in user_ids:
        for days_ago in range(30):
            date = today - timedelta(days=days_ago)
            online_time = random.randint(10, 86400)
            cursor.execute('INSERT INTO UserActivity (user_id, online_time, date) VALUES (?, ?, ?)', (user_id, online_time, date.isoformat()))
    conn.commit()
    conn.close()

@app.route("/api/report/<report_name>", methods=['POST'])
def create_report_configuration(report_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    metrics = request.json.get("metrics", [])
    users = request.json.get("users", [])
    cursor.execute('INSERT OR REPLACE INTO ReportsConfiguration (report_name, metrics, user_ids) VALUES (?, ?, ?)', (report_name, ','.join(metrics), ','.join(users)))
    conn.commit()
    conn.close()
    return jsonify({})

@app.route("/api/report/<report_name>", methods=['GET'])
def retrieve_report(report_name):
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT metrics, user_ids FROM ReportsConfiguration WHERE report_name = ?', (report_name,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": "Report not found."}), 404
    metrics, user_ids = row
    metrics = metrics.split(',')
    user_ids = user_ids.split(',')
    results = []
    for user_id in user_ids:
        metric_values = cursor.execute('''
            SELECT 
                AVG(online_time) as dailyAverage, 
                SUM(online_time) as total, 
                MIN(online_time) as min, 
                MAX(online_time) as max 
            FROM UserActivity WHERE user_id = ? AND date BETWEEN ? AND ?
        ''', (user_id, date_from, date_to)).fetchone()
        user_metrics = {
            "dailyAverage": metric_values[0],
            "total": metric_values[1],
            "min": metric_values[2],
            "max": metric_values[3],
            "weeklyAverage": metric_values[1] / 7 if metric_values[1] else 0
        }
        filtered_metrics = {k: v for k, v in user_metrics.items() if k in metrics}
        results.append({"userId": user_id, "metrics": filtered_metrics})
    conn.close()
    return jsonify(results)

@app.route("/api/users", methods=['GET'])
def list_users():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM Users')
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(user_ids)

if __name__ == '__main__':
    setup_database()
    app.run()
