"""
This demo shows how to interact with event callbacks 
like clickInfo, hoverInfo, dragStartInfo, etc.
"""
import os
import json

import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import dash_deck
import pydeck
import pandas as pd

# 2014 locations of car accidents in the UK
COUNTRIES = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"
POWER_PLANTS = "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/global_power_plant_database.csv"

df = pd.read_csv(POWER_PLANTS)
def is_green(fuel_type):
    if fuel_type.lower() in (
        "nuclear",
        "water",
        "wind",
        "hydro",
        "biomass",
        "solar",
        "geothermal",
    ):
        return [10, 230, 120]
    return [230, 158, 10]


df["color"] = df["primary_fuel"].apply(is_green)

city_info_bin = pd.read_csv("../data/cities_location.csv")


def get_globe(lat):
    view_state = pydeck.ViewState(latitude=lat, longitude=0.45, zoom=2)

    layers = []
    # Set height and width variables
    view = pydeck.View(type="_GlobeView", controller=True, width=1000, height=700)


    layers = [
        pydeck.Layer(
            "GeoJsonLayer",
            id="base-map",
            data=COUNTRIES,
            stroked=False,
            filled=True,
            get_line_color=[60, 60, 60],
            get_fill_color=[200, 200, 200],
        ),
        pydeck.Layer(
            "ColumnLayer",
            id="power-plant",
            data=df,
            get_elevation="capacity_mw",
            get_position=["longitude", "latitude"],
            elevation_scale=100,
            pickable=True,
            auto_highlight=True,
            radius=20000,
            get_fill_color="color",
        ),
    ]

    r = pydeck.Deck(
        views=[view],
        initial_view_state=view_state,
        layers=layers,
        # Note that this must be set for the globe to be opaque
        parameters={"cull": True},
    )
    return r


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [dcc.Slider(0, 20, 5,
               value=10,
               id='my-slider'
    ),
        html.Div(
            id='map-container',
            style = {'margin-top':'20%', 'padding-top':'20%', 'position':'relative'},
            children=[
            ],
        ),
    ]
)


@app.callback(
    Output('map-container','children'),[Input('my-slider', 'value')]
)
def update_graph(scale):
    return dash_deck.DeckGL(
                    json.loads(get_globe(scale).to_json()),
                    id="deck",
                    tooltip=True,
                )

if __name__ == "__main__":
    app.run_server(debug=True)