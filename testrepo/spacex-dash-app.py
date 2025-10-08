# spacex_dash_app.py
# ------------------
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# 数据
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# 唯一发射场（给下拉菜单）
# site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
#     {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
#     ]

# 应用
app = dash.Dash(__name__)

# ==========
# Layout（只放组件，不放回调！）
# ==========
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40},
        ),

        # Task 1: 下拉
        dcc.Dropdown(
            id='site-dropdown',
            # options=site_options,
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'}
            ],
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True,
        ),
        html.Br(),

        # Task 2: 饼图
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),

        html.P("Payload range (Kg):"),
        # Task 3: 载荷范围滑块
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
            value=[min_payload, max_payload],
        ),
        html.Br(),

        # Task 4: 散点图
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# ==========
# Callbacks（放在 layout 之后，顶层作用域）
# ==========

# Task 2: 下拉 -> 饼图
# @app.callback(
#     Output('success-pie-chart', 'figure'),
#     Input('site-dropdown', 'value')
# )
# def get_pie_chart(entered_site):
#     # 1) 选择“ALL” → 统计各发射场的成功次数（class=1），画饼图
#     if entered_site == 'ALL' or entered_site is None:
#         df_success = (
#             spacex_df[spacex_df['class'] == 1]
#             .groupby('Launch Site')['class']
#             .count()
#             .reset_index(name='success_count')
#         )
#         fig = px.pie(
#             df_success,
#             values='success_count',
#             names='Launch Site',
#             title='Total Successful Launches by Site'
#         )
#         return fig

#     # 2) 选择某个发射场 → 统计该场成功/失败次数（class=1 / class=0），画饼图
#     site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
#     outcome_counts = (
#         site_df['class']
#         .value_counts()
#         .rename({1: 'Success', 0: 'Failed'})
#         .reset_index()
#         .rename(columns={'index': 'Outcome', 'class': 'count'})
#     )
#     fig = px.pie(
#         outcome_counts,
#         values='count',
#         names='Outcome',
#         title=f'Success vs. Failed for {entered_site}'
#     )
#     return fig

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    # 情况 1：选择 "ALL" 时显示各发射场成功次数
    if entered_site == 'ALL' or not entered_site:
        df_success = (
            spacex_df[spacex_df['class'] == 1]
            .groupby('Launch Site', as_index=False)
            .size()  # 用 size() 代替 count() 避免重复列名
            .rename(columns={'size': 'success_count'})
        )
        fig = px.pie(
            df_success,
            values='success_count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig

    # 情况 2：选择单个发射场，显示该场成功/失败占比
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = (
            site_df['class']
            .value_counts()
            .rename_axis('class')
            .reset_index(name='num')  # 改为 'num' 避免重复 'count'
        )
        outcome_counts['Outcome'] = outcome_counts['class'].map({1: 'Success', 0: 'Failed'})
        fig = px.pie(
            outcome_counts,
            values='num',
            names='Outcome',
            title=f'Success vs Failed for {entered_site}'
        )
        return fig


# Task 4: 下拉 + 滑块 -> 散点图
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]
        title = f'Correlation between Payload and Success for {entered_site}'
    else:
        title = 'Correlation between Payload and Success for All Sites'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig


if __name__ == '__main__':
    app.run()
