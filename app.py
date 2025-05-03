import numpy as np  # 新增的导入
print(f"NumPy版本: {np.__version__}")  # 确保这行没有缩进！

import dash
from dash import Dash, html, dcc, Input, Output, callback, dash_table
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

# ===== 强制初始化数据库 =====
if not init_db():
    raise RuntimeError("数据库初始化失败")

# ===== 应用初始化 =====
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder="assets",
    serve_locally=True,  # 强制本地加载资源
    assets_ignore=".*\.map$",  # 忽略sourcemap文件
    meta_tags=[{
        'http-equiv': 'cache-control',
        'content': 'no-cache'
    }]
)
server = app.server

# ===== 布局定义 =====
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='storage'),
    html.Div(id='page-content', children=[
        dbc.Container([
            dbc.Alert("数据看板已加载", color="success", className="mt-3"),
            dbc.Row([
                dbc.Col(dbc.Button("+ 添加记录", id="add-btn", className="me-2"), width="auto"),
                dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="primary"), width="auto")
            ], className="my-3"),
            dash_table.DataTable(
                id='table',
                columns=[
                    {'name': '项目名称', 'id': '项目名称', 'editable': True},
                    {'name': '采集数量', 'id': '采集数量', 'type': 'numeric', 'editable': True},
                    {'name': '状态', 'id': '状态', 'presentation': 'dropdown', 'editable': True},
                ],
                dropdown={
                    '状态': {
                        'options': [{'label': i, 'value': i} for i in ["进行中", "已完成", "已暂停"]]
                    }
                },
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '8px'}
            )
        ])
    ])
])

# ===== 回调函数 =====
def load_data():
    """安全加载数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
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

@app.callback(
    Output('storage', 'data'),
    Input('url', 'pathname')
)
def initial_load(_):
    return load_data()

@app.callback(
    Output('table', 'data'),
    Input('storage', 'data')
)
def update_table(data):
    return data

if __name__ == '__main__':
    app.run_server(debug=True)
