import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# ===== 数据库配置 =====
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = str(BASE_DIR / "data.db") if os.environ.get("ENV") != "production" else "/data/data.db"

def init_db():
    """安全的数据库初始化"""
    try:
        # 确保目录存在（仅开发环境需要）
        if os.environ.get("ENV") != "production":
            os.makedirs(BASE_DIR, exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                项目名称 TEXT NOT NULL,
                采集时间 DATETIME DEFAULT CURRENT_TIMESTAMP,
                采集数量 REAL CHECK(采集数量 >= 0),
                状态 TEXT CHECK(状态 IN ("进行中", "已完成", "已暂停")),
                上传 TEXT
            )
        ''')
        conn.commit()
        print(f"✅ 数据库已初始化: {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
# 在应用启动前强制初始化数据库
def check_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
        if not cursor.fetchone():
            init_db()  # 如果表不存在则初始化
        conn.close()
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        raise

check_database()  # 启动应用前执行
# ===== 先初始化数据库再创建应用 =====
if not init_db():
    raise RuntimeError("数据库初始化失败")

# ===== 应用初始化 =====
app = Dash(__name__, 
          external_stylesheets=[dbc.themes.BOOTSTRAP],
          assets_folder="assets")
server = app.server

def load_data():
    """安全加载数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        # 检查表是否存在
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
        if not c.fetchone():
            return []
        
        df = pd.read_sql("SELECT * FROM records", conn)
        return df.to_dict('records') or []
    except Exception as e:
        print(f"❌ 数据加载失败: {str(e)}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

# ===== 布局定义 =====
app.layout = html.Div([
    dcc.Store(id='storage', data=[]),  # 初始为空，通过回调加载
    # ...（其余布局代码保持不变）
])

# ===== 回调函数 =====
@app.callback(
    Output('storage', 'data'),
    Input('url', 'pathname')
)
def on_page_load(_):
    """页面加载时初始化数据"""
    return load_data()

# ...（其余回调函数保持不变）

if __name__ == '__main__':
    app.run_server(debug=True)
