import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import pandas as pd
import os

# ===== 数据库配置 =====
DB_PATH = "data.db" if os.environ.get("ENV") != "production" else "/data/data.db"

def init_db():
    """初始化数据库（自动创建目录）"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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
    conn.close()
    print(f"数据库已初始化: {DB_PATH}")  # 日志输出

def load_data():
    """加载数据到前端"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM records", conn)
    conn.close()
    return df.to_dict('records')

# ===== 应用初始化 =====
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# ===== 布局定义 =====
app.layout = html.Div([
    dcc.Store(id='storage', data=load_data()),  # 初始加载数据
    dbc.Button("+ 添加记录", id="add-btn", className="me-2"),
    dbc.Button("💾 保存数据", id="save-btn", color="success"),
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
        style_table={'overflowX': 'auto'}
    )
])

# ===== 回调函数 =====
@app.callback(
    Output('storage', 'data'),
    Input('add-btn', 'n_clicks'),
    State('storage', 'data')
)
def add_row(n_clicks, data):
    if n_clicks:
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

if __name__ == '__main__':
    init_db()
    app.run_server(debug=True)
