


import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table  # 添加 dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import pandas as pd
import os

# ===== 数据库配置 =====
# 替换原来的 DB_PATH
DB_PATH = "data.db"  # 改为当前目录下的相对路径

def init_db():
    """初始化数据库（去掉了目录创建）"""
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

# ===== 应用初始化 =====
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder="assets")
server = app.server  # 暴露server给gunicorn

# ===== 布局定义 =====
app.layout = html.Div([
    dbc.Toast(id="toast", is_open=False, duration=3000, style={"position": "fixed", "top": 10, "right": 10}),
    dbc.Row([
        dbc.Col(html.H1("生产数据看板", className="text-center my-4"))
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("+ 添加记录", id="add-btn", color="primary", className="me-2"), width="auto"),
        dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="success"), width="auto")
    ], justify="start", className="mb-4"),
    dcc.Store(id="storage", data=[]),
    dcc.Graph(id="chart", figure=go.Figure()),
    dash_table.DataTable(
        id="table",
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "8px"}
    )
])

# ===== 回调逻辑 =====
@app.callback(
    Output("storage", "data"),
    Input("add-btn", "n_clicks"),
    State("storage", "data")
)
def add_row(n_clicks, data):
    if n_clicks:
        new_row = {
            "项目名称": "",
            "采集数量": 0,
            "状态": "进行中",
            "上传": "",
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return data + [new_row]
    return data

if __name__ == "__main__":
    init_db()
    app.run_server(debug=False)
