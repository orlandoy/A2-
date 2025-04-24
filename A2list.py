import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import pandas as pd
import os

class ProjectDashboard:
    def __init__(self):
        self.COLOR_SCHEME = {
            "进行中": ["#E74C3C", "#C0392B"],
            "已完成": ["#2ECC71", "#27AE60"],
            "background": "#0E1A2B",
            "card": "#1C2C3C",
            "text": "#ECF0F1",
            "highlight": "#00BFFF"
        }

        self.app = dash.Dash(__name__, external_stylesheets=[
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
            'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap'
        ])

        self.app.title = "智元A2项目未来看板"
        self.projects = self.load_projects()
        self.df = pd.DataFrame(self.projects)
        self.app.layout = self.create_layout()

    def load_projects(self):
        return [
            {"项目名称": "水果分拣(fruit sort)", "采集时间": '2025.04.03-2025.04.20', "采集数量": 23618, "状态": "已完成", "上传": "进行中"},
            {"项目名称": "扫码枪扫货(Scanning gun to scan goods)", "采集时间": '2025.04.21-2025.04.22', "采集数量": 6792, "状态": "已完成", "上传": "进行中"},
            {"项目名称": "桌面垃圾清理(desktop junk cleaning)", "采集时间": '2025.04.23-', "采集数量": 0.0, "状态": "进行中", "上传": "进行中"},
        ]

    def create_bar_chart(self):
        fig = go.Figure()

        for status in self.df["状态"].unique():
            df_filtered = self.df[self.df["状态"] == status]
            fig.add_trace(go.Bar(
                x=df_filtered["项目名称"],
                y=df_filtered["采集数量"],
                name=status,
                marker=dict(
                    color=self.COLOR_SCHEME[status][0],
                    line=dict(color=self.COLOR_SCHEME[status][1], width=2.5),
                ),
                opacity=0.95,
                text=[f"{x:,}" for x in df_filtered["采集数量"]],
                textposition="outside",
                width=0.5
            ))

        avg_value = self.df["采集数量"].mean()

        fig.update_layout(
            plot_bgcolor=self.COLOR_SCHEME["card"],
            paper_bgcolor=self.COLOR_SCHEME["background"],
            font=dict(family="Roboto", size=13, color=self.COLOR_SCHEME["text"]),
            xaxis=dict(tickangle=-20, gridcolor="#34495E", showgrid=False),
            yaxis=dict(gridcolor="#34495E", tickformat=","),
            hoverlabel=dict(bgcolor="#2C3E50", font_size=12, font_color="white"),
            legend=dict(orientation="h", y=1.1, font=dict(color=self.COLOR_SCHEME["text"])),
            margin=dict(t=40),
            transition={"duration": 500}
        )

        fig.add_hline(
            y=avg_value,
            line_dash="dot",
            line_color="#BDC3C7",
            annotation_text=f"平均值: {avg_value:,.0f}",
            annotation_font_color=self.COLOR_SCHEME["text"]
        )

        return fig

    def create_card(self, title, value, icon, color):
        return html.Div(
            className="card",
            style={
                "backgroundColor": self.COLOR_SCHEME["card"],
                "borderRadius": "16px",
                "padding": "20px",
                "boxShadow": "0 8px 20px rgba(0,0,0,0.3)",
                "margin": "10px",
                "flex": 1,
                "minWidth": "220px",
                "transition": "transform 0.3s ease",
                ":hover": {"transform": "scale(1.05)"}
            },
            children=[
                html.Div([
                    html.I(className=f"fas fa-{icon}", 
                          style={"color": color, "fontSize": "26px"}),
                    html.H3(title, style={"marginLeft": "12px", "color": self.COLOR_SCHEME["text"]})
                ], style={"display": "flex", "alignItems": "center"}),
                html.H2(
                    f"{value:,}",
                    style={"color": color, "marginTop": "10px", "fontSize": "30px"}
                )
            ]
        )

    def create_data_table(self):
        return dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in self.df.columns],
            data=self.df.to_dict("records"),
            style_table={"overflowX": "auto", "borderRadius": "12px"},
            style_header={
                "backgroundColor": self.COLOR_SCHEME["highlight"],
                "color": "white",
                "fontWeight": "bold",
                "fontSize": "16px",
                "border": "none"
            },
            style_cell={
                "textAlign": "left",
                "padding": "14px",
                "fontFamily": "Roboto",
                "backgroundColor": self.COLOR_SCHEME["card"],
                "color": self.COLOR_SCHEME["text"]
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#243447"},
                {"if": {"filter_query": "{状态} = '已完成'"}, "color": self.COLOR_SCHEME["已完成"][0]},
                {"if": {"filter_query": "{状态} = '进行中'"}, "color": self.COLOR_SCHEME["进行中"][0]}
            ],
            filter_action="native",
            sort_action="native",
            page_size=10,
            style_as_list_view=True
        )

    def create_layout(self):
        return html.Div(
            style={
                "backgroundColor": self.COLOR_SCHEME["background"],
                "minHeight": "100vh",
                "padding": "30px",
                "fontFamily": "Roboto"
            },
            children=[
                html.H1(
                    "A2项目数据采集未来看板",
                    style={
                        "textAlign": "center",
                        "color": self.COLOR_SCHEME["text"],
                        "marginBottom": "40px"
                    }
                ),

                html.Div([
                    self.create_card("总采集量", self.df["采集数量"].sum(), 
                                   "database", self.COLOR_SCHEME["highlight"]),
                    self.create_card("已完成项目", len(self.df[self.df["状态"] == "已完成"]), 
                                   "check-circle", self.COLOR_SCHEME["已完成"][0]),
                    self.create_card("进行中项目", len(self.df[self.df["状态"] == "进行中"]), 
                                   "spinner", self.COLOR_SCHEME["进行中"][0])
                ], style={"display": "flex", "flexWrap": "wrap", "marginBottom": "40px"}),

                html.Div(
                    className="chart-card",
                    style={
                        "backgroundColor": self.COLOR_SCHEME["card"],
                        "borderRadius": "16px",
                        "padding": "20px",
                        "boxShadow": "0 8px 20px rgba(0,0,0,0.3)",
                        "marginBottom": "40px"
                    },
                    children=[
                        dcc.Graph(
                            id="collection-chart",
                            figure=self.create_bar_chart(),
                            config={"displayModeBar": False},
                            style={"height": "480px"}
                        )
                    ]
                ),

                html.Div(
                    className="table-card",
                    style={
                        "backgroundColor": self.COLOR_SCHEME["card"],
                        "borderRadius": "16px",
                        "padding": "20px",
                        "boxShadow": "0 8px 20px rgba(0,0,0,0.3)"
                    },
                    children=[self.create_data_table()]
                )
            ]
        )

    def run(self, debug=True):
        port = int(os.environ.get("PORT", 8050))
        self.app.run(debug=debug, host="0.0.0.0", port=port)

if __name__ == "__main__":
    dashboard = ProjectDashboard()
    dashboard.run(debug=True)
