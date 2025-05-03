import plotly.graph_objects as go

def generate_bar_chart(data):
    names = [item["项目名称"] for item in data]
    values = [int(item.get("采集数量", 0)) for item in data]
    fig = go.Figure(data=[go.Bar(x=names, y=values, marker_color='mediumseagreen')])
    fig.update_layout(
        title="采集数量分布图",
        xaxis_title="项目名称",
        yaxis_title="采集数量",
    )
    return fig
