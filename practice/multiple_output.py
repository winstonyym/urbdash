import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('auto-mpg.csv')

app = dash.Dash()

features = df.columns

app.layout = html.Div([
  html.Div([
    dcc.Dropdown(id = 'xaxis',
                 options = [{'label':i, 'value':i} for i in features],
                 value='displacement')
  ], style = {'width':'48%', 'display':'inline-block', }),
  html.Div([
    dcc.Dropdown(id = 'yaxis',
                options = [{'label':i, 'value':i} for i in features],
                value='mpg')
  ], style = {'width':'48%', 'display':'inline-block'}),
  dcc.Graph(id='feature-graphic')
], style = {'padding':10})

@app.callback(Output('feature-graphic', 'figure'), 
[Input('xaxis', 'value'), Input('yaxis', 'value')])
def update_graph(xaxis_col, yaxis_col):
  return {'data': [go.Scatter(x = df[xaxis_col], 
                              y = df[yaxis_col], 
                              text = df['car name'], 
                              mode = 'markers',
                              marker = {'size':5, 'opacity':0.5})],
         'layout': go.Layout(
            title = "My Dashboard for MPG",
            xaxis = {'title': xaxis_col},
            yaxis = {'title': yaxis_col},
            hovermode = 'closest'
         )} 

if __name__ == '__main__':
    app.run_server()