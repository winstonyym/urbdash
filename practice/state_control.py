import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State

app = dash.Dash()

app.layout = html.Div([
    dcc.Input(id = 'input_num', value = 1, style = {'fontSize':30}),
    html.Button(id = 'input_button', n_clicks = 0, children = 'Submit', style = {'fontSize':30}),
    html.H1(id = 'output_num')
])

@app.callback(Output('output_num', 'children'),
             [Input('input_button', 'n_clicks')],
             State('input_num', 'value'))

def update_number(num_clicks, input_num):
    return f"{input_num} was typed and clicked {num_clicks} times."

if __name__ == '__main__':
    app.run_server()