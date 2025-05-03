from dash import dash_table, html

def generate_table(data):
    return dash_table.DataTable(
        id='data-table',
        columns=[
            {"name": "项目名称", "id": "项目名称", "editable": True},
            {"name": "采集时间", "id": "采集时间", "editable": True},
            {"name": "采集数量", "id": "采集数量", "editable": True, "type": "numeric"},
            {"name": "状态", "id": "状态", "editable": True},
            {"name": "上传", "id": "上传", "editable": True},
        ],
        data=data,
        editable=True,
        row_deletable=True,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
    )
