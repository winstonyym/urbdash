import dash
import json
from dash import html
from dash import dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd

df = pd.read_csv('wheels.csv')

app = dash.Dash()

app.layout = html.Div([
    html.Div([dcc.Graph(id = 'input_graph',
              figure = {'data': [go.Scatter(x = df['wheels'],
                                            y = df['color'],
                                            dx = 1,
                                            mode = 'markers',
                                            marker = {'size':10})],
                        'layout':  go.Layout(title='Colors and Wheels',
                              xaxis = {'title':'Wheels'},
                              yaxis = {'title':'Color'})})], 
            style = {'float':'left', 'width':'30%'}),
    html.Div([html.Pre(id = 'output_json')],  style = {'width':'30%', 'paddingTop':35})
])

@app.callback(Output('output_json', 'children'),
             [Input('input_graph', 'clickData')])
def update_json(hoverData):
    return json.dumps(hoverData, indent=2)

if __name__ == '__main__':
    app.run_server()