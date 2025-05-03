from dash import html, dcc
import dash_bootstrap_components as dbc

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='stored-data'),

    html.Div(id='chart-container'),
    html.Br(),

    dbc.Button("+ 添加新行", id='add-row-btn', color="success", className="me-2"),
    dbc.Button("💾 保存数据", id='save-btn', color="primary"),
    html.Br(), html.Br(),

    html.Div(id='table-container'),
])
