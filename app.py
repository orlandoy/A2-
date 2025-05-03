import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import pandas as pd
import os
from pathlib import Path

# ===== 数据库配置 =====
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = str(BASE_DIR / "data.db") if os.environ.get("ENV") != "production" else "/data/data.db"

def init_db():
    """安全的数据库初始化"""
    conn = None
    try:
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
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def load_data():
    """健壮的数据加载"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM records", conn)
        return df.to_dict('records') or []  # 确保返回列表
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            init_db()
            return []
        raise
    finally:
        if conn:
            conn.close()

# ===== 应用初始化 =====
app = Dash(__name__, 
          external_stylesheets=[dbc.themes.BOOTSTRAP],
          assets_folder="assets")
server = app.server

# ===== 布局定义 =====
app.layout = html.Div([
    dcc.Store(id='storage', data=load_data()),
    dbc.Row([
        dbc.Col(dbc.Button("+ 添加记录", id="add-btn", color="primary", className="me-2"), width="auto"),
        dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="success"), width="auto"),
    ], className="mb-3"),
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
    ),
    dcc.Location(id='url', refresh=False)
])

# ===== 回调函数 =====
@app.callback(
    Output('storage', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def on_page_load(_):
    return load_data()

@app.callback(
    Output('storage', 'data'),
    Input('add-btn', 'n_clicks'),
    State('storage', 'data')
)
def add_row(n_clicks, data):
    if n_clicks and n_clicks > 0:
        new_row = {
            '项目名称': '新项目',
            '采集数量': 0,
            '状态': '进行中',
            '上传': '',
            '采集时间': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return data + [new_row]
    return dash.no_update

@app.callback(
    Output('table', 'data'),
    Input('storage', 'data')
)
def update_table(data):
    return data

# ===== 启动应用 =====
if __name__ == '__main__':
    init_db()  # 开发环境初始化
    app.run_server(debug=True)
