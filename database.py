import sqlite3
import json
import os

DB_PATH = "data_store.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_data (
            id INTEGER PRIMARY KEY,
            json_data TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM dashboard_data")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO dashboard_data (json_data) VALUES (?)", [json.dumps([])])
    conn.commit()
    conn.close()

def save_data(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE dashboard_data SET json_data = ? WHERE id = 1", [json.dumps(data)])
    conn.commit()
    conn.close()

def load_data():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT json_data FROM dashboard_data WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []
