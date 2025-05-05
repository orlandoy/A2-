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
init_db()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    # 移除了可能导致问题的 assets_folder 参数
    suppress_callback_exceptions=True
)
server = app.server

# ===== 布局定义 =====
app.layout = html.Div([
    dcc.Store(id='storage', storage_type='memory'),
    dbc.Row([
        dbc.Col(dbc.Button("+ 添加记录", id="add-btn", color="primary", className="me-2", n_clicks=0)),
        dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="success", n_clicks=0)),
        dbc.Col(html.Div(id='save-status'))
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
        data=[],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        editable=True,
        row_deletable=True
    )
])

# ===== 回调函数 =====
@app.callback(
    [Output('storage', 'data', allow_duplicate=True),
     Output('table', 'data', allow_duplicate=True)],
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
    updated_data = current_data + [new_record] if current_data else [new_record]
    return updated_data, updated_data

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
        c = conn.cursor()
        c.execute("DELETE FROM records")
        
        for record in data:
            c.execute(
                "INSERT INTO records (项目名称, 采集数量, 状态, 采集时间) VALUES (?, ?, ?, ?)",
                (record['项目名称'], record['采集数量'], record['状态'], record.get('采集时间'))
            )
        conn.commit()
        return dbc.Alert("✅ 数据保存成功！", color="success", duration=3000)
    except Exception as e:
        return dbc.Alert(f"❌ 保存失败: {str(e)}", color="danger", duration=3000)
    finally:
        if 'conn' in locals():
            conn.close()

@app.callback(
    Output('storage', 'data'),
    Input('table', 'data'),
    State('storage', 'data'),
    prevent_initial_call=False
)
def load_data(_, current_data):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT 项目名称, 采集数量, 状态, 采集时间 FROM records", conn)
        return df.to_dict('records') if not df.empty else []
    except Exception as e:
        print(f"❌ 加载数据失败: {str(e)}")
        return current_data if current_data else []
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host='0.0.0.0', port=port, debug=True)
