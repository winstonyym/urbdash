"""
Adapted from: https://pydeck.gl/gallery/h3_hexagon_layer.html

Plot of values for a particular hex ID in the H3 geohashing scheme.

This example is adapted from the deck.gl documentation.
"""
import os

import dash
import dash_deck
from dash import html
import pydeck as pdk
import pandas as pd

mapbox_api_token = "pk.eyJ1Ijoid2luc3Rvbnl5bSIsImEiOiJjbDZyb3UwanQwOXNrM2pxOWRvNTJ2YmRlIn0.i2i24ARrX48r-tK1tX-yrQ"

COUNTRIES = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"
H3_HEX_DATA = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf.h3cells.json"

df = pd.read_json(H3_HEX_DATA)

# Define a layer to display on a map
layer = [
    pdk.Layer(
        "GeoJsonLayer",
        id="base-map",
        data=COUNTRIES,
        stroked=False,
        filled=True,
        get_line_color=[60, 60, 60],
        get_fill_color=[200, 200, 200],
    ),
    pdk.Layer(
    "H3HexagonLayer",
    df,
    pickable=True,
    stroked=True,
    filled=True,
    extruded=False,
    get_hexagon="hex",
    get_fill_color="[255 - count, 255, count]",
    get_line_color=[255, 255, 255],
    line_width_min_pixels=2,
)]

# Set the viewport location
view_state = pdk.ViewState(
    latitude=37.7749295, longitude=-122.4194155, zoom=1
)

view = pdk.View(type="_GlobeView", controller=True, width=1000, height=800)

# Render
r = pdk.Deck(layers=[layer], views=[view], initial_view_state=view_state, parameters={"cull": True})


app = dash.Dash(__name__)

app.layout = html.Div(
    dash_deck.DeckGL(
        r.to_json(),
        id="deck-gl",
        tooltip={"text": "Count: {count}"},
    )
)


if __name__ == "__main__":
    app.run_server(debug=True)