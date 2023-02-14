"""
Adapted from: https://pydeck.gl/gallery/geojson_layer.html
Property values in Vancouver, Canada, adapted from the deck.gl example 
pages. Input data is in a GeoJSON format.
"""
import os

import dash
import dash_deck
from dash import html, dcc
import pydeck
import pandas as pd

mapbox_token = "pk.eyJ1Ijoid2luc3Rvbnl5bSIsImEiOiJjbDZyb3UwanQwOXNrM2pxOWRvNTJ2YmRlIn0.i2i24ARrX48r-tK1tX-yrQ"

DATA_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/geojson/vancouver-blocks.json"
LAND_COVER = [
    [[-123.0, 49.196], [-123.0, 49.324], [-123.306, 49.324], [-123.306, 49.196]]
]

INITIAL_VIEW_STATE = pydeck.ViewState(
    latitude=49.254, longitude=-123.13, zoom=11, max_zoom=16, pitch=45, bearing=0
)

polygon = pydeck.Layer(
    "PolygonLayer",
    LAND_COVER,
    stroked=False,
    # processes the data as a flat longitude-latitude pair
    get_polygon="-",
    get_fill_color=[0, 0, 0, 20],
)

geojson = pydeck.Layer(
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

r = pydeck.Deck(
    layers=[geojson],
    initial_view_state=INITIAL_VIEW_STATE,
)


app = dash.Dash(__name__)

app.layout = html.Div(
    dash_deck.DeckGL(r.to_json(), id="deck-gl", mapboxKey=mapbox_token)
)


if __name__ == "__main__":
    app.run_server(debug=True)
