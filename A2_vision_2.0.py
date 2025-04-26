import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State
import plotly.express as px
import pandas as pd

# 初始化应用
app = Dash(__name__)
server = app.server  # 如果后续要部署 Render 或其他平台需要这个

# 初始数据
initial_data = [
    {"项目名称": "水果分拣(fruit sort)", "采集时间": "2025.04.03-2025.04.20", "采集数量": 23618, "状态": "已完成", "上传": "进行中"},
    {"项目名称": "扫码枪扫货(scanning gun)", "采集时间": "2025.04.21-2025.04.22", "采集数量": 6792, "状态": "已完成", "上传": "进行中"},
    {"项目名称": "桌面垃圾清理(cleaning)", "采集时间": "2025.04.23-", "采集数量": 1111, "状态": "进行中", "上传": "进行中"},
]

# 应用布局
app.layout = html.Div(
    style={"padding": "20px", "fontFamily": "Arial, sans-serif", "backgroundColor": "#F4F6F9"},
    children=[
        html.H1("项目数据管理系统", style={"textAlign": "center", "marginBottom": "30px"}),
        
        dcc.Graph(id='bar-chart', style={"marginBottom": "40px"}),

        html.Div([
            dash_table.DataTable(
                id='editable-table',
                columns=[
                    {"name": "项目名称", "id": "项目名称", "editable": True},
                    {"name": "采集时间", "id": "采集时间", "editable": True},
                    {"name": "采集数量", "id": "采集数量", "editable": True, "type": "numeric"},
                    {"name": "状态", "id": "状态", "editable": True},
                    {"name": "上传", "id": "上传", "editable": True},
                ],
                data=initial_data,
                editable=True,
                row_deletable=True,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "backgroundColor": "white",
                    "border": "1px solid #dee2e6",
                },
                style_header={
                    "backgroundColor": "#007BFF",
                    "color": "white",
                    "fontWeight": "bold",
                    "textAlign": "center"
                },
            ),

            html.Button(
                '添加一行',
                id='add-row-button',
                n_clicks=0,
                style={
                    "marginTop": "15px",
                    "backgroundColor": "#28a745",
                    "color": "white",
                    "border": "none",
                    "padding": "10px 20px",
                    "borderRadius": "5px",
                    "cursor": "pointer",
                    "fontSize": "16px"
                }
            )
        ], style={"backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}),
    ]
)

# 回调：添加新行
@app.callback(
    Output('editable-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('editable-table', 'data'),
    State('editable-table', 'columns'),
    prevent_initial_call=True
)
def add_row(n_clicks, rows, columns):
    # 新增一行空数据
    rows.append({c['id']: '' for c in columns})
    return rows

# 回调：根据表格动态更新柱状图
@app.callback(
    Output('bar-chart', 'figure'),
    Input('editable-table', 'data')
)
def update_chart(data):
    df = pd.DataFrame(data)

    # 检查是否有有效数据
    if df.empty or "项目名称" not in df.columns or "采集数量" not in df.columns:
        fig = px.bar(title="暂无数据")
        fig.update_layout(
            plot_bgcolor="#F4F6F9",
            paper_bgcolor="#F4F6F9",
            font=dict(color="#343a40")
        )
        return fig

    # 创建柱状图
    fig = px.bar(
        df,
        x="项目名称",
        y="采集数量",
        text="采集数量",
        color="状态",
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="各项目采集数量统计",
        xaxis_tickangle=-30,
        plot_bgcolor="#F4F6F9",
        paper_bgcolor="#F4F6F9",
        font=dict(color="#343a40"),
        title_x=0.5
    )
    return fig

# 运行
if __name__ == '__main__':
    app.run(debug=True)
