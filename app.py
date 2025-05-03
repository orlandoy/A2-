import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import sqlite3  # Python内置库，无需安装
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# ===== 数据库配置 =====
BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = str(BASE_DIR / "data.db") if os.environ.get("ENV") != "production" else "/data/data.db"

def init_db():
    """初始化数据库（自动创建目录）"""
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
        print(f"✅ 数据库已初始化 | SQLite版本: {sqlite3.sqlite_version} | 路径: {DB_PATH}")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

# ===== 应用初始化 =====
init_db()  # 启动时自动初始化

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder="assets",
    serve_locally=True
)
server = app.server

# ===== 布局定义 =====
app.layout = html.Div([
    dcc.Store(id='storage', data=[]),
    dbc.Row([
        dbc.Col(dbc.Button("+ 添加记录", id="add-btn", color="primary", className="me-2", n_clicks=0)),
        dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="success"))
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
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        editable=True,
        row_deletable=True
    )
])

# ===== 回调函数 =====
@app.callback(
    Output('storage', 'data', allow_duplicate=True),
    Input('add-btn', 'n_clicks'),
    State('storage', 'data'),
    prevent_initial_call=True
)
def add_record(n_clicks, current_data):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    
    new_record = {
        '项目名称': f'新项目_{n_clicks}',
        '采集数量': 0,
        '状态': '进行中',
        '采集时间': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    print(f"添加记录: {new_record}")
    return current_data + [new_record] if current_data else [new_record]

@app.callback(
    Output('table', 'data'),
    Input('storage', 'data')
)
def update_table(data):
    return data or []

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)
