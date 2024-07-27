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

# Define the app layout
app1.layout = html.Div([
    html.Div([
        html.Div([
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
                display_format='YYYY-MM-DD',
                start_date_placeholder_text="選擇開始日期",
                end_date_placeholder_text="選擇結束日期",
            ),
            dcc.Graph(id='map', style={'height': '500px'}),
        ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    html.Div([
        html.H3('Filtered Data'),
        html.Ul(id='filtered-data-list'),
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    html.Div([
        dcc.Graph(id='scatter-plot', style={'height': '500px'}),
    ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}),
])

@app1.callback(
    [Output('map', 'figure'),
     Output('filtered-data-list', 'children'),
     Output('scatter-plot', 'figure')],
    [Input('weather-filter', 'value'),
     Input('region-filter', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)

def update_output(selected_weathers, selected_regions, start_date, end_date):
    # Filter data based on user inputs
    filtered_df = df[
        (df['天氣'].isin(selected_weathers)) &
        (df['地區'].isin(selected_regions)) &
        (df['日期'] >= start_date) &
        (df['日期'] <= end_date)
    ]
    
    print(filtered_df)  # Print filtered data for debugging
    
    # Convert filtered data to a list of html.Li elements
    filtered_data_list = [
        html.Li(f"日期: {row['日期']}, 天氣: {row['天氣']}, 事故數: {row['事故數']}")
        for idx, row in filtered_df.iterrows()
    ]
    
    # Update map figure
    if filtered_df.empty:
        fig_map = px.scatter_mapbox(lat=[0], lon=[0], zoom=1)
        fig_map.update_layout(mapbox_style="open-street-map")
    else:
        fig_map = px.scatter_mapbox(filtered_df, lat='緯度', lon='經度', color='事故數',
                                    hover_name='地區', hover_data=['日期', '天氣'],
                                    zoom=5, height=500)
        fig_map.update_layout(mapbox_style="open-street-map")
    
    # Update scatter plot figure (dummy data for illustration)
    fig_scatter = px.scatter(df, x='日期', y='事故數', color='天氣', hover_data=['地區'], title='Scatter Plot')
    
    print(fig_scatter)  # Print fig_scatter for debugging
    
    return fig_map, filtered_data_list, fig_scatter
