import dash
from dash import Dash, Input, Output, State, ctx, callback, no_update, dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import pandas as pd
import os
import time

# ========================
# 数据库模块
# ========================
DB_PATH = "data.db"

def init_db():
    """初始化数据库表结构"""
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

def load_data():
    """从数据库加载数据"""
    try:
        if not os.path.exists(DB_PATH):
            init_db()
            return []
        
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql("SELECT * FROM records", conn)
            return df.to_dict("records")
    except Exception as e:
        print(f"数据加载失败: {e}")
        return []

def save_data(data):
    """增量保存数据到数据库"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            old_ids = pd.read_sql("SELECT id FROM records", conn)['id'].tolist()
            new_df = pd.DataFrame(data)
            
            conn.execute("BEGIN TRANSACTION")
            for _, row in new_df.iterrows():
                if pd.isna(row.get('id')) or row['id'] not in old_ids:  # 新增
                    conn.execute(
                        "INSERT INTO records (项目名称, 采集数量, 状态, 上传) VALUES (?, ?, ?, ?)",
                        (row['项目名称'], row['采集数量'], row['状态'], row['上传'])
                    )
                else:  # 更新
                    conn.execute(
                        "UPDATE records SET 项目名称=?, 采集数量=?, 状态=?, 上传=? WHERE id=?",
                        (row['项目名称'], row['采集数量'], row['状态'], row['上传'], row['id'])
                    )
            # 删除已移除的行
            current_ids = [x['id'] for x in data if 'id' in x and not pd.isna(x['id'])]
            to_delete = set(old_ids) - set(current_ids)
            for id_ in to_delete:
                conn.execute("DELETE FROM records WHERE id=?", (id_,))
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

# ========================
# 可视化组件
# ========================
def generate_bar_chart(data):
    """生成柱状图（带错误处理）"""
    if not data:
        return go.Figure().add_annotation(text="暂无数据", showarrow=False)

    try:
        names = [item.get("项目名称", "未命名") for item in data]
        values = [float(item.get("采集数量", 0)) for item in data]
    except (ValueError, TypeError):
        return go.Figure().add_annotation(text="数据格式错误", showarrow=False)

    fig = go.Figure(
        data=[go.Bar(x=names, y=values, marker_color='mediumseagreen')],
        layout=dict(
            title="采集数量分布图",
            xaxis_title="项目名称",
            yaxis_title="采集数量",
            autosize=True,
            margin=dict(l=50, r=50, b=100, t=50, pad=4)
        )
    )
    return fig

def generate_table(data):
    """生成可编辑表格（带分页和列控制）"""
    if not data:
        return dash_table.DataTable(id='data-table', columns=[], data=[])

    column_config = {
        "采集时间": {"editable": False},
        "状态": {
            "editable": True,
            "presentation": "dropdown",
            "dropdown_options": [{"label": s, "value": s} for s in ["进行中", "已完成", "已暂停"]]
        }
    }

    columns = [
        {
            "name": col.replace("_", " ").title(),
            "id": col,
            "editable": column_config.get(col, {}).get("editable", True),
            "presentation": column_config.get(col, {}).get("presentation")
        } for col in data[0].keys()
    ]

    return dash_table.DataTable(
        id='data-table',
        columns=columns,
        data=data,
        editable=True,
        row_deletable=True,
        page_size=10,
        sort_action="native",
        style_table={"overflowX": "auto", "minWidth": "100%"},
        style_cell={
            "textAlign": "center",
            "padding": "8px",
            "whiteSpace": "normal"
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "textTransform": "capitalize"
        },
        dropdown=column_config.get("状态")
    )

# ========================
# 应用布局
# ========================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder="assets",
    suppress_callback_exceptions=True,
)

app.title = "生产级数据管理面板"
app.layout = html.Div([
    # 通知组件
    dbc.Toast(
        id="save-notification",
        is_open=False,
        duration=3000,
        className="position-fixed top-0 end-0 m-3",
        header="系统提示",
        dismissable=True
    ),
    
    # 操作区
    dbc.Row([
        dbc.Col(dbc.Button(
            "+ 添加新行", 
            id="add-row-btn", 
            color="success", 
            className="me-2",
            n_clicks=0
        ), width="auto"),
        dbc.Col(dbc.Button(
            "💾 保存数据", 
            id="save-btn", 
            color="primary",
            n_clicks=0
        ), width="auto"),
    ], className="my-3 g-2", justify="start"),
    
    # 数据存储
    dcc.Store(id="stored-data", storage_type="memory"),
    dcc.Location(id="url", refresh=False),
    
    html.Hr(),
    
    # 图表区（带加载动画）
    dcc.Loading(
        id="loading-chart",
        children=html.Div(id="chart-container", className="my-3"),
        type="circle"
    ),
    
    # 表格区
    html.Div(id="table-container", className="my-3")
])

# ========================
# 回调逻辑
# ========================
@app.callback(
    Output("stored-data", "data"),
    Input("url", "pathname"),
    prevent_initial_call="initial_duplicate"
)
def load_initial_data(_):
    """初始化加载数据"""
    return load_data()

@app.callback(
    Output("chart-container", "children"),
    Output("table-container", "children"),
    Output("stored-data", "data", allow_duplicate=True),
    Input("add-row-btn", "n_clicks"),
    Input("save-btn", "n_clicks"),
    Input("data-table", "data"),
    Input("data-table", "data_previous"),
    State("stored-data", "data"),
    State("data-table", "columns"),
    prevent_initial_call=True
)
def update_components(add_clicks, save_clicks, table_data, prev_data, stored_data, columns):
    """处理所有交互逻辑"""
    trigger = ctx.triggered_id
    
    if trigger == "add-row-btn" and add_clicks:
        new_row = {
            "项目名称": "",
            "采集数量": 0,
            "状态": "进行中",
            "上传": "",
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        updated_data = stored_data + [new_row]
        return [dcc.Graph(figure=generate_bar_chart(updated_data))], generate_table(updated_data), updated_data
    
    elif trigger == "save-btn" and save_clicks:
        try:
            save_data(table_data)
            return no_update, no_update, table_data
        except Exception as e:
            print(f"保存失败: {e}")
            return no_update, no_update, no_update
    
    elif trigger == "data-table":
        if prev_data and len(prev_data) > len(table_data):
            try:
                save_data(table_data)
            except Exception as e:
                print(f"删除保存失败: {e}")
        return [dcc.Graph(figure=generate_bar_chart(table_data))], no_update, table_data
    
    return no_update, no_update, no_update

@app.callback(
    Output("save-notification", "is_open"),
    Output("save-notification", "children"),
    Input("save-btn", "n_clicks"),
    State("data-table", "data")
)
def show_notification(n_clicks, data):
    """显示保存通知"""
    if n_clicks and n_clicks > 0:
        return True, f"成功保存 {len(data)} 条记录"
    return no_update, no_update

# ========================
# 启动应用
# ========================
if __name__ == "__main__":
    init_db()  # 确保数据库存在
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
