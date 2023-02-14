import dash
import json
from dash import html
from dash import dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np

df = pd.read_csv('auto-mpg.csv')

app = dash.Dash()

app.layout = html.Div([
    html.Div([
        dcc.Graph(id = 'mpg-scatter',
                figure = {'data': [go.Scatter(
                                        x = df['model year'] + 1900,
                                        y = df['mpg'],
                                        text = df['car name'],
                                        hoverinfo = 'all',
                                        mode = 'markers')],
                            'layout' : go.Layout(title = 'MPG ScatterPlot', 
                                                 xaxis = {'title': 'Model Year'},
                                                 yaxis = {'title': 'MPG'},
                                                 hovermode = 'closest')})
    ], style = {'width':'33%', 'display':'inline-block'}),
    html.Div([
        dcc.Graph(id = 'output_mpg', 
                  figure = {'data' : [go.Line(
                                        x = [0,1],
                                        y = [0,1])],
                            'layout' : go.Layout(title = 'Acceleration')})
    ], style = {'width':'33%', 'display': 'inline-block', 'float':'middle'}),
    html.Div([
        html.Pre(id = 'output_text', children = "Null")
], style = {'width':'33%', 'display': 'inline-block', 'float':'right', 'padding-top':'5%'})
])


@app.callback(Output('output_mpg', 'figure'),
              [Input('mpg-scatter', 'hoverData')])
def plot_graph(hoverData):
    v_index = hoverData['points'][0]['pointIndex']
    figure = {'data' : [go.Scatter(x = [0,1], 
                                   y = [0,60/df.iloc[v_index]['acceleration']], 
                                   mode = 'lines',
                                   line = {'width':3*df.iloc[v_index]['cylinders']})],
              'layout' : go.Layout(title = df.iloc[v_index]['car name'], 
                                   xaxis = {'visible':False}, 
                                   yaxis={'visible':False, 'range':[0,60/df['acceleration'].min()]},
                                   height=400)
            }
    return figure

@app.callback(Output('output_text', 'children'),
              [Input('mpg-scatter', 'hoverData')])
def update_text(hoverData):
    v_index = hoverData['points'][0]['pointIndex']

    return f'''
    Cylinders: {df.iloc[v_index]['cylinders']}
    Displacement: {df.iloc[v_index]['displacement']}
    Acceleration: {df.iloc[v_index]['acceleration']}
    '''

if __name__ == '__main__':
    app.run_server()