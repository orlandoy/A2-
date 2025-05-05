import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# ===== 数据库配置 =====
# ===== 数据库配置 =====
BASE_DIR = Path(__file__).parent.resolve()
# Render 环境使用 /tmp（临时）或持久化磁盘路径
DB_PATH = "/tmp/data.db" if os.environ.get("RENDER") else str(BASE_DIR / "data.db")

def init_db():
    """初始化数据库"""
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
        print(f"✅ 数据库已初始化 | 路径: {DB_PATH}")
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
    dcc.Store(id='storage', data=[], storage_type='memory'),
    dbc.Row([
        dbc.Col(dbc.Button("+ 添加记录", id="add-btn", color="primary", className="me-2", n_clicks=0)),
        dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="success", n_clicks=0)),
        dbc.Col(html.Div(id='save-status'))  # 保存状态提示
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

@app.callback(
    Output('save-status', 'children'),
    Input('save-btn', 'n_clicks'),
    State('storage', 'data'),
    prevent_initial_call=True
)
def save_data(n_clicks, data):
    if not n_clicks or not data:
        raise dash.exceptions.PreventUpdate
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.DataFrame(data)
        
        # 清空旧数据并写入新数据（根据需求调整）
        conn.cursor().execute("DELETE FROM records")
        df.to_sql('records', conn, if_exists='append', index=False)
        conn.commit()
        
        msg = f"✅ 保存成功：{len(data)} 条记录"
        print(msg)
        return dbc.Alert(msg, color="success", duration=3000)
    except Exception as e:
        msg = f"❌ 保存失败: {str(e)}"
        print(msg)
        return dbc.Alert(msg, color="danger", duration=3000)
    finally:
        if 'conn' in locals():
            conn.close()

@app.callback(
    Output('storage', 'data'),
    Input('table', 'data')  # 页面加载时触发
)
def load_data(_):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM records", conn)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 加载数据失败: {str(e)}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host='0.0.0.0', port=port, debug=False)
