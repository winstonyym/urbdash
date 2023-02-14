import dash 
from dash import dcc
from dash import html
import plotly.graph_objs as go
import numpy as np

app = dash.Dash(__name__)

colors = {'background':'#111111', 'text':'#7FDBFF'}
np.random.seed(42)
random_x = np.random.randint(1,101,100)
random_y = np.random.randint(1,101,100)

app.layout = html.Div(children=[
  dcc.Graph(id = 'scatterplot',
            figure = {'data':[go.Scatter(
              x = random_x,
              y = random_y,
              mode = 'markers',
              marker = {
                'size':12,
                'color':colors['text'],
                'symbol':'pentagon',
                'line': {'width':2}
              }
            )],
            'layout': go.Layout(title='My Scatterplot', xaxis={'title':'X Axis Label'})})
])

if __name__ == '__main__':
    app.run_server()