from dash import html, dcc
import dash_bootstrap_components as dbc

layout = html.Div([
    dcc.Location(id='url'),  # 必需
    dcc.Store(id='stored-data', data=[]),  # 用于存储状态

    dbc.Button("➕ 添加新行", id="add-row-btn", color="success", className="me-2"),
    dbc.Button("💾 保存数据", id="save-btn", color="primary", className="me-2"),

    html.Br(), html.Br(),

    html.Div(id='chart-container'),  # 图表显示区域
    html.Div(id='table-container'),  # 表格显示区域
])
