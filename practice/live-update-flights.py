import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import requests

app = dash.Dash()

app.layout = html.Div([
             html.Div([
                html.Iframe(src="https://winstonyym.github.io/demo/",
                            height = 1000,
                            width = 1200)
             ]),
             html.Div([
                html.Pre(id = "counter",
                         children = "Active Flights Worldwide"),
                dcc.Interval(id = 'interval-component', interval = 10000, n_intervals=0)
             ]),
])

@app.callback(Output('live-update-text','children'),
              [Input('interval_component', 'n_intervals')])
def updater(n_intervals):
    return f"This page has been updated {n_intervals}th times."

if __name__ == '__main__':
    app.run_server()