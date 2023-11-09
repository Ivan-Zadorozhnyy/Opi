import sqlite3
from main import app, setup_database
import json

def test_database_setup():
    setup_database()
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    tables = list(cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"))
    assert ('Users',) in tables
    assert ('UserActivity',) in tables
    assert ('ReportsConfiguration',) in tables
    conn.close()

def test_insert_and_retrieve_report_configuration():
    with app.test_client() as client:
        client.post('/api/report/weeklyActivity',
                    data=json.dumps({
                        "metrics": ["dailyAverage"],
                        "users": ["d580539f-9ee8-4300-b48e-0e8d0810f766"]
                    }),
                    content_type='application/json')

        conn = sqlite3.connect('reports.db')
        cursor = conn.cursor()
        config = cursor.execute('SELECT * FROM ReportsConfiguration WHERE report_name="weeklyActivity"').fetchone()
        assert config is not None
        conn.close()
