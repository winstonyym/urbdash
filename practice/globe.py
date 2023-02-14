import os
import json

import dash
import dash_deck
from dash import html
import pydeck
import pandas as pd
json

mapbox_api_token = "pk.eyJ1Ijoid2luc3Rvbnl5bSIsImEiOiJjbDZyb3UwanQwOXNrM2pxOWRvNTJ2YmRlIn0.i2i24ARrX48r-tK1tX-yrQ"


COUNTRIES = "./practice/globe2.geojson"
DATA_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/geojson/vancouver-blocks.json"


view_state = pydeck.ViewState(latitude=49.254, longitude=-123.13, zoom=2)

layers = []
# Set height and width variables
view = pydeck.View(type="_GlobeView", controller=True, width=1000, height=800)

with open(COUNTRIES, 'r') as f:
    DATA = json.load(f)

layers = [
    pydeck.Layer(
        "GeoJsonLayer",
        id="base-map",
        data=DATA,
        stroked=False,
        filled=True,
        get_line_color=[60, 60, 60],
        get_fill_color=[200, 200, 200],
    ),
    pydeck.Layer(
        "GeoJsonLayer",
        DATA_URL,
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="properties.valuePerSqm / 20",
        get_fill_color="[255, 255, properties.growth * 255]",
        get_line_color=[255, 255, 255],
    )    
]

r = pydeck.Deck(
    views=[view],
    initial_view_state=view_state,
    layers=layers,
    # Note that this must be set for the globe to be opaque
    parameters={"cull": True},
)


app = dash.Dash(__name__)

app.layout = html.Div(
    dash_deck.DeckGL(
        json.loads(r.to_json()),
        id="deck-gl",
        style={"background-color": "black"},
        tooltip={"text": "Count: {count}"},
    )
)


if __name__ == "__main__":
    app.run_server(debug=True)