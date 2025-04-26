import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx
import plotly.graph_objects as go
import pandas as pd
import os

# 🎨 配色方案
COLOR_SCHEME = {
    "已完成": ["#2ECC71", "#27AE60"],
    "进行中": ["#E67E22", "#D35400"],
    "background": "#F8F9FA",
    "card": "#FFFFFF",
    "text": "#2C3E50",
    "highlight": "#3498DB"
}

# 📥 初始数据
initial_projects = [
    {"项目名称": "水果分拣(fruit sort)", "采集时间": "2025.04.03-2025.04.20", "采集数量": 23618, "状态": "已完成", "上传": "进行中"},
    {"项目名称": "扫码枪扫货(scanning gun)", "采集时间": "2025.04.21-2025.04.22", "采集数量": 6792, "状态": "已完成", "上传": "进行中"},
    {"项目名称": "桌面垃圾清理(cleaning)", "采集时间": "2025.04.23-", "采集数量": 1111, "状态": "进行中", "上传": "进行中"},
]

# 🏗 初始化 Dash 应用
app = dash.Dash(__name__, external_stylesheets=[
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap"
])
app.title = "智元A2项目"

# 使用 Store 保存全局数据
app.layout = html.Div(style={"backgroundColor": COLOR_SCHEME["background"], "minHeight": "100vh", "padding": "20px"}, children=[
    html.H1("A2项目数据采集看板", style={"textAlign": "center", "color": COLOR_SCHEME["text"], "marginBottom": "30px"}),

    dcc.Store(id="project-data", data=initial_projects),

    # 📈 图表
    html.Div(id="chart-container", style={"marginBottom": "30px"}),

    # ➕ ➖ 按钮
    html.Div([
        html.Button("➕ 添加新项目", id="add-row-btn", n_clicks=0,
                    style={"backgroundColor": "#2ECC71", "color": "white", "border": "none",
                           "padding": "10px 20px", "borderRadius": "8px", "fontSize": "16px"}),
    ], style={"textAlign": "right", "marginBottom": "10px"}),

    # 📋 表格
    dash_table.DataTable(
        id="editable-table",
        columns=[
            {"name": "项目名称", "id": "项目名称", "editable": True},
            {"name": "采集时间", "id": "采集时间", "editable": True},
            {"name": "采集数量", "id": "采集数量", "editable": True, "type": "numeric"},
            {"name": "状态", "id": "状态", "editable": True},
            {"name": "上传", "id": "上传", "editable": True},
            {"name": "操作", "id": "操作", "presentation": "markdown"},
        ],
        data=[],
        editable=True,
        row_deletable=False,
        style_table={"overflowX": "auto", "borderRadius": "10px"},
        style_header={"backgroundColor": COLOR_SCHEME["highlight"], "color": "white", "fontWeight": "bold"},
        style_cell={"textAlign": "center", "padding": "10px", "fontFamily": "Roboto", "minWidth": "100px"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#FAFAFA"},
            {"if": {"filter_query": "{状态} = '已完成'"}, "color": COLOR_SCHEME["已完成"][0]},
            {"if": {"filter_query": "{状态} = '进行中'"}, "color": COLOR_SCHEME["进行中"][0]}
        ],
        filter_action="native",
        sort_action="native",
        page_size=10
    )
])

# 📈 动态生成柱状图
@app.callback(
    Output("chart-container", "children"),
    Input("project-data", "data")
)
def update_chart(data):
    df = pd.DataFrame(data)

    fig = go.Figure()
    for status in df["状态"].unique():
        df_filtered = df[df["状态"] == status]
        fig.add_trace(go.Bar(
            x=df_filtered["项目名称"],
            y=df_filtered["采集数量"],
            name=status,
            marker=dict(
                color=COLOR_SCHEME[status][0],
                line=dict(color=COLOR_SCHEME[status][1], width=1.5)
            ),
            text=[f"{x:,}" for x in df_filtered["采集数量"]],
            textposition="outside",
            width=0.6,
            opacity=0.9
        ))

    avg_value = df["采集数量"].mean()
    fig.add_hline(y=avg_value, line_dash="dot", line_color="#7F8C8D",
                  annotation_text=f"平均值: {avg_value:,.0f}", annotation_position="top right",
                  annotation_font_color="#7F8C8D")

    fig.update_layout(
        plot_bgcolor=COLOR_SCHEME["card"],
        paper_bgcolor=COLOR_SCHEME["background"],
        font=dict(family="Roboto", size=12),
        xaxis=dict(tickangle=-30, gridcolor="#EDEDED"),
        yaxis=dict(gridcolor="#EDEDED", tickformat=","),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=30),
        hoverlabel=dict(bgcolor="white", font_size=12),
        height=450
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False})

# 📋 同步表格数据
@app.callback(
    Output("editable-table", "data"),
    Input("project-data", "data")
)
def update_table(data):
    table_data = []
    for row in data:
        new_row = row.copy()
        new_row["操作"] = "🗑️"  # 每行加上一个垃圾桶 emoji
        table_data.append(new_row)
    return table_data

# ➕➖ 新增/删除/编辑数据
@app.callback(
    Output("project-data", "data", allow_duplicate=True),
    Input("editable-table", "data"),
    Input("add-row-btn", "n_clicks"),
    State("project-data", "data"),
    prevent_initial_call=True
)
def modify_data(table_data, n_clicks, store_data):
    triggered_id = ctx.triggered_id

    if triggered_id == "add-row-btn":
        store_data.append({
            "项目名称": "新项目",
            "采集时间": "时间待定",
            "采集数量": 0,
            "状态": "进行中",
            "上传": "进行中"
        })
        return store_data

    elif triggered_id == "editable-table":
        cleaned_data = []
        for row in table_data:
            if row.get("操作") != "🗑️删除":
                row.pop("操作", None)
                cleaned_data.append(row)
        return cleaned_data

    return store_data

# 监听表格中的 "操作"列，删除行
@app.callback(
    Output("editable-table", "data", allow_duplicate=True),
    Input("editable-table", "data_previous"),
    State("editable-table", "data"),
    prevent_initial_call=True
)
def delete_row(previous, current):
    if previous is None:
        raise dash.exceptions.PreventUpdate
    if len(previous) > len(current):
        return current

    changed_idx = next((i for i in range(len(current)) if previous[i] != current[i]), None)
    if changed_idx is not None:
        current[changed_idx]["操作"] = "🗑️删除"
    return current

# 🚀 启动服务器
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
