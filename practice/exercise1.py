import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd

colors = ['red', 'yellow', 'blue']
wheels = [1,2,3]
df = pd.read_csv('wheels.csv')



app = dash.Dash()

app.layout = html.Div([
    html.Div([dcc.RadioItems(id = 'color_input',
                             options = [{'label':i, 'value':i} for i in colors],
                             value = colors[0]
                            )]
            ),
    html.Hr(),
    html.Div([dcc.RadioItems(id = 'wheel_input',
                             options = [{'label':i, 'value':i} for i in wheels],
                             value = wheels[0]
                             )]
            ),
    html.Hr(),
    html.Img(id = 'image_output', src = None)
])

@app.callback(Output(component_id='image_output', component_property = 'src'), 
                    [Input(component_id = 'wheel_input', component_property='value'),
                     Input(component_id = 'color_input', component_property='value')])
def update_image(wheel_input, color_input):
    path = df['image'].loc[(df['wheels']==wheel_input) & (df['color']==color_input)]
    return 'assets/' + path

if __name__ == '__main__':
    app.run_server()

