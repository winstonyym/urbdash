from dash import Dash, dcc, html, Input, Output, dash_table
import json

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Dropdown(
            options=[
                {
                    "label": "Bangkok",
                    "value": "../data/bangkok.json",
                }
            ],
            value="../data/bangkok.json",
            id="data-select",
        ),
        html.Br(),
        dash_table.DataTable(id="my-table-promises", page_size=10, fixed_columns={'headers': True, 'data': 1}, style_table={'minWidth': '100%'},
        style_cell={
        # all three widths are needed
        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    }
    )])

@app.callback(Output("my-table-promises", "data"), [Input("data-select", "value")])
def update_table(value):
    with open(value, 'r') as openfile:
        json_object = json.load(openfile)
    return json_object


if __name__ == "__main__":
    app.run_server(debug=True)
