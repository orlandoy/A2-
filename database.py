import sqlite3
import os
import pandas as pd

DB_PATH = "data.db"  # 保存在项目根目录

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            项目名称 TEXT,
            采集时间 TEXT,
            采集数量 TEXT,
            状态 TEXT,
            上传 TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_data():
    if not os.path.exists(DB_PATH):
        return []
    df = pd.read_sql_query("SELECT * FROM records", sqlite3.connect(DB_PATH))
    return df.to_dict("records")

def save_data(data):
    df = pd.DataFrame(data)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("records", conn, if_exists="replace", index=False)
    conn.close()
