from dash import Dash, Input, Output, State, ctx, callback, no_update
import dash_bootstrap_components as dbc
from datetime import datetime
import os

from components.layout import layout
from components.charts import generate_bar_chart
from components.table import generate_table
from database import init_db, load_data, save_data

# 初始化数据库
init_db()

# 创建 Dash 应用
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder="assets",
    suppress_callback_exceptions=True,
)

app.title = "生产级数据管理面板"
app.config.prevent_initial_callbacks = 'initial_duplicate'

app.config.prevent_initial_callbacks = 'initial_duplicate'
app.layout = layout

# 主回调：处理添加、保存、删除行与图表更新
@callback(
    Output('chart-container', 'children'),
    Output('table-container', 'children'),
    Output('stored-data', 'data'),
    Input('add-row-btn', 'n_clicks'),
    Input('save-btn', 'n_clicks'),
    Input('data-table', 'data'),
    Input('data-table', 'data_previous'),
    State('stored-data', 'data'),
    State('data-table', 'columns'),
    prevent_initial_call=True
)
def update_components(add_clicks, save_clicks, table_data, 
                     prev_data, stored_data, columns):
    trigger = ctx.triggered_id

    if trigger == 'add-row-btn':
        new_row = {col['id']: "" for col in columns}
        new_row.update({
            "采集数量": "0",
            "状态": "进行中",
            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        stored_data.append(new_row)
        return generate_bar_chart(stored_data), generate_table(stored_data), stored_data

    elif trigger == 'save-btn':
        save_data(table_data)
        return no_update, no_update, table_data

    elif trigger == 'data-table':
        if prev_data and len(prev_data) > len(table_data):
            save_data(table_data)
        return generate_bar_chart(table_data), no_update, table_data

    return no_update, no_update, no_update

# 页面首次加载：初始化数据
@callback(
    Output('stored-data', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call='initial_duplicate'
)
def load_initial_data(_):
    return load_data()

# 启动服务
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)

