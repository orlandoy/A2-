import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

layout = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button("+ 添加新行", id="add-row-btn", color="success", className="me-2")),
        dbc.Col(dbc.Button("💾 保存数据", id="save-btn", color="primary")),
    ], className="my-2", justify="start"),

    dcc.Store(id="stored-data", data=[]),
    dcc.Location(id="url", refresh=False),

    html.Hr(),

    html.Div(id="chart-container", className="my-3"),
    html.Div(id="table-container", className="my-3")
])
