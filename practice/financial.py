import dash
import json
from dash import html
from dash import dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd
import pandas_datareader as pdr
import numpy as np
from datetime import date

api_key = "SCHAV7R1JCQYPOX7"
stocks_df = pd.read_csv('nasdaq.csv')
colors = ["#606c38", "#219ebc", "#dda15e", "#ffb703", "#fb5607", "#8338ec"]
app = dash.Dash()

app.layout = html.Div([
    html.Div([dcc.Dropdown(id = 'input_company', options = [{'label':i, 'value':i} for i in stocks_df['Symbol']], value = "Choose stock...", multi = True, style = {'height': '15px', 'padding-top':'20px'})], 
            style = {'height':'50px', 'width':'30%', 'display':'inline-block', 'padding-left':'5%'}),
    html.Div([dcc.DatePickerRange(id = 'input_date',
                                  min_date_allowed=date(2015, 1, 1),
                                  max_date_allowed=date(2023, 1, 22),
                                  initial_visible_month=date(2015, 1, 1),
                                  end_date=date(2023, 1, 22))], 
            style = {'height':'50px','width':'30%', 'display': 'inline-block', 'padding-left':'5%'}),
    html.Div([html.Button(id = 'input_button', n_clicks = 0, children = 'Submit', style = {'fontSize':30})],
            style = {'height':'50px', 'width':'20%', 'display':'inline-block', 'padding-left':'5%'}),
    html.Div([dcc.Graph(id = 'output_graph', 
                        figure = {'data': [go.Scatter(x = pd.date_range("2015-1-1", "2023-1-22", freq='MS'),
                                                      y = [0] * len(pd.date_range("2015-1-1", "2023-1-22", freq='MS')),
                                                      mode = 'lines'
                                                     )],
                                  'layout': go.Layout(title = 'Stock Price over Time', 
                                                      height=400)})],
            style = {'height':'20%', 'width':'98%', 'display': 'inline-block', 'padding-top':'5%'})
])

@app.callback(Output("output_graph", "figure"),
             [Input('input_button', 'n_clicks')],
             [State("input_company", "value"),
              State("input_date", "start_date"),
              State("input_date", "end_date")])
def graph_update(num_clicks, companies, start_date, end_date):
    traces = []
    for i, company in enumerate(companies):
        out = pdr.av.time_series.AVTimeSeriesReader(symbols = company, 
                                                    start = start_date, 
                                                    end = end_date,
                                                    function = 'TIME_SERIES_MONTHLY',  
                                                    api_key=api_key)
        data = out.read()
        traces.append(go.Scatter(x = data.index,
                                 y = data['close'],
                                 name = company,
                                 mode = "lines",
                                 line = {'color': colors[i]}
        ))
    
    return {'data': traces,
            'layout': go.Layout(title = 'Stock Price over Time',
                                height = 400, 
                                xaxis = {'title':'Time'},
                                yaxis = {'title':'Price (USD)'})}

if __name__ == "__main__":
    app.run_server()