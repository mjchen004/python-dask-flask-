import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

app1 = dash.Dash(__name__,requests_pathname_prefix='/dashboard/dashboard2/')

data = {
    '日期': ['2023-01-01', '2023-01-02', '2023-01-03'],
    '天氣': ['晴天', '雨天', '陰天'],
    '地區': ['北部', '中部', '南部'],
    '經度': [121.5, 120.5, 121.0],
    '緯度': [25.0, 24.0, 23.5],
    '事故數': [10, 5, 8]
}
df = pd.DataFrame(data)

app1.layout = html.Div([
    dcc.Checklist(
        id='weather-filter',
        options=[{'label': weather, 'value': weather} for weather in df['天氣'].unique()],
        value=df['天氣'].unique().tolist(),
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Checklist(
        id='region-filter',
        options=[{'label': region, 'value': region} for region in df['地區'].unique()],
        value=df['地區'].unique().tolist(),
        labelStyle={'display': 'inline-block'}
    ),
    dcc.DatePickerRange(
        id='date-picker',
        start_date=df['日期'].min(),
        end_date=df['日期'].max(),
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='map'),
    html.Div(id='filtered-data')
])

@app1.callback(
    [Output('map', 'figure'),
     Output('filtered-data', 'children')],
    [Input('weather-filter', 'value'),
     Input('region-filter', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_output(selected_weathers, selected_regions, start_date, end_date):
    filtered_df = df[
        (df['天氣'].isin(selected_weathers)) &
        (df['地區'].isin(selected_regions)) &
        (df['日期'] >= start_date) &
        (df['日期'] <= end_date)
    ]
    
    fig = px.scatter_mapbox(filtered_df, lat='緯度', lon='經度', color='事故數',
                            hover_name='地區', hover_data=['日期', '天氣'],
                            zoom=5, height=500)
    fig.update_layout(mapbox_style="open-street-map")
    
    return fig, filtered_df.to_dict('records')