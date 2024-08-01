from dash import Dash, dcc, html,dash_table,Input, Output,callback
# from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import psycopg2
from sqlalchemy import create_engine

app1 = Dash(__name__,requests_pathname_prefix='/dashboard/dashboard2/')
app1.title="全台交通事故資料"

# 配置PostgreSQL連接信息
DB_HOST = 'dpg-cqhfldt6l47c73fn0ffg-a.singapore-postgres.render.com'
DB_NAME = 'python_dash_flask'
DB_USER = 'tvdi_1t1e_user'
DB_PASS = 'rBEiLilhmGmOM5yYkkcujQtLHMaLZaQi'

# 連接PostgreSQL數據庫
engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')

# 從PostgreSQL讀取數據
def fetch_data(year):
    query = f'SELECT * FROM traffic{year}'
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df

# 初始讀取數據
df = fetch_data(2018)
df.columns = df.columns.str.strip()
df[['死亡人數', '受傷人數']] = df['死亡受傷人數'].str.extract('死亡(\d+);受傷(\d+)').astype(int)

# df = pd.read_csv(f"./data/2018.csv",encoding='utf-16')
# df.columns=df.columns.str.strip()
# df[['死亡人數', '受傷人數']] = df['死亡受傷人數'].str.extract('死亡(\d+);受傷(\d+)').astype(int)

# Define the app layout
app1.layout = html.Div([
    html.Div([
        html.H1("交通事故分析",style={"textAlign":"center"}),
        html.Div([
            dcc.DatePickerSingle(
                id='date-picker',
                date=df['發生日期'].min(),
                display_format='YYYY-MM-DD',
                placeholder="選擇日期",
            ),
            html.Hr(),
            dcc.Checklist(
                id='weather-filter',
                options=[{'label': weather, 'value': weather} for weather in df['天候名稱'].unique()],
                value=df['天候名稱'].unique().tolist(),
                labelStyle={'display': 'inline-block'}
            ),
            html.Hr(),
            dcc.Checklist(
                id='region-filter',
                options=[{'label': region, 'value': region} for region in df['發生地點'].unique()],
                value=df['發生地點'].unique().tolist(),
                labelStyle={'display': 'inline-block'}
            ),
            html.Hr(),
            dcc.Checklist(
                id='lights-filter',
                options=[{'label': light, 'value': light} for light in df['光線名稱'].unique()],
                value=df['光線名稱'].unique().tolist(),
                labelStyle={'display': 'inline-block'}
            )
            
        ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    html.Div([
        dcc.Graph(id='map', style={'height': '500px'})],
        style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dcc.Graph(id='bar-chart', style={'height': '500px'})],
        style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ], 
    style={'width': '80%', 'display': 'inline-block', 'vertical-align': 'top','margin-left':'10%','margin-right':'10%'}),
    
    html.Div([
        html.H3('事故資料表'),
        dash_table.DataTable(id='filtered-data-list',
                             columns=[{'name':col,'id':col} for col in ['發生日期','發生地點','事故類別名稱','天候名稱','光線名稱','速限_第1當事者','道路類別_第1當事者_名稱','死亡人數','受傷人數']],
                             data=df.to_dict('records'),
                             page_size=10,
                             style_cell_conditional=[{
                                 'if': {'column_id': '光線名稱'}, 'width': '250px'}])]),
    
    html.Div([
        dcc.Graph(id='bar-chart-2', style={'height': '500px'}),
    ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dcc.Graph(id='pie-chart', style={'height': '500px'})],
        style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dcc.Graph(id='line-chart', style={'height': '500px'})],
        style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'})
])

@app1.callback(
    [Output('filtered-data-list', 'data'),
     Output('map', 'figure'),
     Output('bar-chart', 'figure'),
     Output('bar-chart-2', 'figure'),
     Output('pie-chart', 'figure'),
     Output('line-chart','figure')],
    [Input('date-picker', 'date'),
     Input('weather-filter', 'value'),
     Input('region-filter', 'value'),
     Input('lights-filter', 'value')
     ]
)

def update_output(selected_date,selected_weathers, selected_regions, selected_lights):
    if selected_date is not None:
        year = selected_date.split('-')[0]
        df = fetch_data(year)
        df.columns = df.columns.str.strip()
        df[['死亡人數', '受傷人數']] = df['死亡受傷人數'].str.extract('死亡(\d+);受傷(\d+)').astype(int)

    filtered_df=df[(df['發生日期']==selected_date) &
                   (df['天候名稱'].isin(selected_weathers)) &
                   (df['發生地點'].isin(selected_regions)) &
                   (df['光線名稱'].isin(selected_lights))]
    
    # 計算累進事故次數
    filtered_df['time'] = pd.to_datetime(filtered_df['發生時間'], format='%H:%M:%S.%f')
    filtered_df = filtered_df.sort_values('time')
    filtered_df['cumulative_accidents'] = filtered_df.groupby('發生日期').cumcount() + 1
    total_accidents = len(filtered_df)
    filtered_df['percentage'] = filtered_df['cumulative_accidents'] / total_accidents * 100

    map_figure = px.scatter_mapbox(filtered_df,
                                   lat="緯度",
                                   lon="經度",
                                   hover_name="發生地點",
                                   color="天候名稱",
                                   zoom=6,
                                   labels="事故地圖")
    map_figure.update_layout(mapbox_style="open-street-map",
                             margin={"r":0,"t":80,"l":100,"b":50},
                             title={"text":"事故地圖",
                                    'x': 0.5,  # 標題居中
                                    "xanchor":"center",
                                    'y': 0.9,
                                    'font': {'size': 30}
                                    })
    location_counts = filtered_df['發生地點'].value_counts().reset_index()
    location_counts.columns = ['發生地點', '案件數量']
    bar_figure1=px.bar(location_counts,
                      x='發生地點',
                      y='案件數量',
                      labels={'發生地點': '發生地點', '案件數量': '案件數量'},
                      color='發生地點',
                      title=f'各縣市案件數量', 
                      height=500)
    
    weather_counts = filtered_df['天候名稱'].value_counts().reset_index()
    weather_counts.columns = ['天候名稱', '案件數量']
    bar_figure2=px.bar(weather_counts,
                      x='天候名稱',
                      y='案件數量',
                      labels={'天候名稱': '天候名稱', '案件數量': '案件數量'},
                      color='天候名稱',
                      title=f'各天氣案件數量', 
                      height=500)
    
    road_type_counts = filtered_df['道路類別_第1當事者_名稱'].value_counts().reset_index()
    road_type_counts.columns = ['道路類別_第1當事者_名稱', '案件數量']
    pie_figure=px.pie(road_type_counts,
                        names='道路類別_第1當事者_名稱',
                        values='案件數量',
                        title='各道路類別案件數量')
    
    line_figure = px.line(filtered_df,
                          x='time',
                          y='percentage',
                          labels={'time': '時間', 'percentage': '累進百分比'},
                          title='累進車禍事故發生次數（%)',
                          height=500)
    line_figure.update_layout(xaxis={'tickformat': '%H:%M'})

    return filtered_df.to_dict('records'), map_figure,bar_figure1,bar_figure2,pie_figure,line_figure
