from dash import dash_table

def generate_table(data):
    if not data:
        return dash_table.DataTable(
            id='data-table',
            columns=[],
            data=[]
        )

    return dash_table.DataTable(
        id='data-table',
        columns=[{"name": col, "id": col, "editable": True} for col in data[0].keys()],
        data=data,
        editable=True,
        row_deletable=True,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "center",
            "padding": "5px",
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold"
        },
    )
