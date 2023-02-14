import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

colors = {'background':'#111111', 'text':'#7FDBFF'}

app.layout = html.Div(children=[
  dcc.Input(id='my_id', value='Initial Text', type='text'),
  html.Div(id='my-div', style={'border':'2px blue solid'})
])

@app.callback(Output(component_id='my-div', component_property = 'children'), 
                    [Input(component_id = 'my_id', component_property='value')])
def update_output_div(input_value):
  return f"You entered: {input_value} "


if __name__ == '__main__':
    app.run_server()