import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import pandas as pd
import os


class ProjectDashboard:
    def __init__(self):
        # 🎨 颜色方案
        self.COLOR_SCHEME = {
            "已完成": ["#2ECC71", "#27AE60"],
            "进行中": ["#E67E22", "#D35400"],
            "background": "#F8F9FA",
            "card": "#FFFFFF",
            "text": "#2C3E50",
            "highlight": "#3498DB"
        }

        # 🚀 初始化 Dash 应用
        self.app = dash.Dash(__name__, external_stylesheets=[
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
            "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap"
        ])
        self.app.title = "A2项目数据看板"

        # 📊 加载数据
        self.projects = self.load_projects()
        self.df = pd.DataFrame(self.projects)

        # 🏗 构建布局
        self.app.layout = self.create_layout()

    def load_projects(self):
        """📥 项目数据"""
        return [
            {"项目名称": "水果分拣(fruit sort)", "采集时间": "2025.04.03-2025.04.20",
             "采集数量": 23618, "状态": "已完成", "上传": "进行中"},
            {"项目名称": "扫码枪扫货(scanning gun)", "采集时间": "2025.04.21-2025.04.22",
             "采集数量": 6792, "状态": "已完成", "上传": "进行中"},
            {"项目名称": "桌面垃圾清理(cleaning)", "采集时间": "2025.04.23-",
             "采集数量": 1111, "状态": "进行中", "上传": "进行中"},
        ]

    def create_bar_chart(self):
        """📈 柱状图组件"""
        fig = go.Figure()

        for status in self.df["状态"].unique():
            df_filtered = self.df[self.df["状态"] == status]
            fig.add_trace(go.Bar(
                x=df_filtered["项目名称"],
                y=df_filtered["采集数量"],
                name=status,
                marker=dict(
                    color=self.COLOR_SCHEME[status][0],
                    line=dict(color=self.COLOR_SCHEME[status][1], width=1.5)
                ),
                text=[f"{x:,}" for x in df_filtered["采集数量"]],
                textposition="outside",
                width=0.6,
                opacity=0.9
            ))

        avg_value = self.df["采集数量"].mean()

        fig.add_hline(
            y=avg_value,
            line_dash="dot",
            line_color="#7F8C8D",
            annotation_text=f"平均值: {avg_value:,.0f}",
            annotation_position="top right",
            annotation_font_color="#7F8C8D"
        )

        fig.update_layout(
            plot_bgcolor=self.COLOR_SCHEME["card"],
            paper_bgcolor=self.COLOR_SCHEME["background"],
            font=dict(family="Roboto", size=12),
            xaxis=dict(tickangle=-30, gridcolor="#EDEDED"),
            yaxis=dict(gridcolor="#EDEDED", tickformat=","),
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=30),
            hoverlabel=dict(bgcolor="white", font_size=12)
        )

        return fig

    def create_card(self, title, value, icon, color):
        """📦 卡片组件"""
        return html.Div(
            className="card",
            style={
                "backgroundColor": self.COLOR_SCHEME["card"],
                "borderRadius": "10px",
                "padding": "20px",
                "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
                "margin": "10px",
                "flex": 1,
                "minWidth": "200px"
            },
            children=[
                html.Div([
                    html.I(className=f"fas fa-{icon}", style={
                        "color": color, "fontSize": "24px"}),
                    html.H3(title, style={
                        "marginLeft": "10px", "fontSize": "18px"})
                ], style={"display": "flex", "alignItems": "center"}),
                html.H2(f"{value:,}", style={
                    "color": color, "marginTop": "10px", "fontSize": "28px"})
            ]
        )

    def create_data_table(self):
        """📋 表格组件"""
        return dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in self.df.columns],
            data=self.df.to_dict("records"),
            style_table={"overflowX": "auto", "borderRadius": "8px"},
            style_header={
                "backgroundColor": self.COLOR_SCHEME["highlight"],
                "color": "white",
                "fontWeight": "bold"
            },
            style_cell={
                "textAlign": "left",
                "padding": "12px",
                "fontFamily": "Roboto"
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"},
                 "backgroundColor": "rgba(240, 240, 240, 0.5)"},
                {"if": {"filter_query": "{状态} = '已完成'"},
                 "color": self.COLOR_SCHEME["已完成"][0]},
                {"if": {"filter_query": "{状态} = '进行中'"},
                 "color": self.COLOR_SCHEME["进行中"][0]}
            ],
            filter_action="native",
            sort_action="native",
            page_size=10
        )

    def create_layout(self):
        """🖼 页面布局"""
        return html.Div(
            style={
                "backgroundColor": self.COLOR_SCHEME["background"],
                "minHeight": "100vh",
                "padding": "20px",
                "fontFamily": "Roboto"
            },
            children=[
                html.H1("A2项目数据采集看板", style={
                    "textAlign": "center",
                    "color": self.COLOR_SCHEME["text"],
                    "marginBottom": "30px"
                }),

                # 📊 指标卡片行
                html.Div([
                    self.create_card("总采集量", self.df["采集数量"].sum(),
                                     "database", self.COLOR_SCHEME["highlight"]),
                    self.create_card("已完成项目", len(self.df[self.df["状态"] == "已完成"]),
                                     "check-circle", self.COLOR_SCHEME["已完成"][0]),
                    self.create_card("进行中项目", len(self.df[self.df["状态"] == "进行中"]),
                                     "spinner", self.COLOR_SCHEME["进行中"][0])
                ], style={"display": "flex", "flexWrap": "wrap", "marginBottom": "30px"}),

                # 📉 图表卡片
                html.Div(
                    className="chart-card",
                    style={
                        "backgroundColor": self.COLOR_SCHEME["card"],
                        "borderRadius": "10px",
                        "padding": "20px",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
                        "marginBottom": "30px"
                    },
                    children=[dcc.Graph(
                        id="collection-chart",
                        figure=self.create_bar_chart(),
                        config={"displayModeBar": False},
                        style={"height": "450px"}
                    )]
                ),

                # 📂 表格卡片
                html.Div(
                    className="table-card",
                    style={
                        "backgroundColor": self.COLOR_SCHEME["card"],
                        "borderRadius": "10px",
                        "padding": "20px",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                    },
                    children=[self.create_data_table()]
                )
            ]
        )

    def run(self, debug=True):
        """🚀 启动服务器"""
        port = int(os.environ.get("PORT", 8050))
        self.app.run(debug=debug, host="0.0.0.0", port=port)


# 🟢 运行
if __name__ == "__main__":
    dashboard = ProjectDashboard()
    dashboard.run(debug=True)
