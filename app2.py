import dash
from dash import dcc
from dash import html
import dash_deck 
import pydeck
import scipy
import scipy.stats as stats
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from dash.dependencies import ClientsideFunction, Input, Output, State
import plotly.express as px
from ipywidgets import widgets
import urllib.request, json

mapbox_token = "pk.eyJ1Ijoid2luc3Rvbnl5bSIsImEiOiJjbDZyb3UwanQwOXNrM2pxOWRvNTJ2YmRlIn0.i2i24ARrX48r-tK1tX-yrQ"
mapbox_style = "mapbox://styles/mapbox/dark-v11"
# name mapper
with open("./data/urbanity_indicators.json", "r") as f:
    urban_indicators = json.load(f)

with open("./data/poly_columns.json", "r") as f:
    aggregated_indicators = json.load(f)

# Get dataframe
city_info_bin = pd.read_csv("./data/cities_location.csv")

# ! CHANGE THIS TO INDICATOR LIST
filters = []
for i in urban_indicators.keys():
    filters.append(dict(label=i, value=i))

aggregate_filters = []
for i in aggregated_indicators.keys():
    aggregate_filters.append(dict(label=i, value=i))


filters_layout = html.Div(
    [
        html.Div(
            [
                html.H3("Choose urban indicator", style={"display": "inline"}),
                html.Span(
                    [html.Span(className="Select-arrow", title="is_open")],
                    className="Select-arrow-zone",
                    id="select_filters_arrow",
                ),
            ],
        ),
        html.Div(
            [
                dcc.Dropdown(
                    placeholder="Selected indicators",
                    id="filters_drop",
                    options=filters,
                    value = "Footprint Proportion",
                    clearable=False,
                    className="dropdownMenu",
                    style = {'padding':'0px'}
                ),
            ],
            id="dropdown_menu_applied_filters",
        ),
    ],
    id="filters_container",
    style={"display": "block"},
    className="stack-top col-3",
)

##########################################################################################

# Popout
selected_location_layout = html.Div(
    [
        html.Div(
            [
                html.H2("", id="title_selected_location", style={'padding-left':'5px'}),
                html.Span("X", id="x_close_selection"),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div([
                            dcc.Dropdown(id = 'xaxis',
                                        options = aggregate_filters,
                                        value="Mean Building Complexity",
                                        clearable=False)
                                ], style = {'width':'50%', 'display':'inline-block'}),
                        html.Div([
                            dcc.Dropdown(id = 'yaxis',
                                        options = aggregate_filters,
                                        value="No. of Nodes",
                                        clearable=False)
                                ], style = {'width':'50%', 'display':'inline-block'}),
                        dcc.Graph(id='scatter-graph', style = {'height':'90%'})
                    ],
                    className="plots_container_child",
                ),
                html.Div(
                    [
                        html.H4("Subzone Statistics"),
                        html.Div(children = [], 
                                id='subzone-container',
                                style={"position":"relative", 'height':'85%'})
                    ],
                    className="plots_container_child",
                ),
            ],
            className="plots_container",
        ),
        html.Div(
            [
                html.H4("Benchmarking Indicators", style={'padding-left':'2%'}),
                html.Iframe(id="benchmark_scatter", src = "https://winstonyym.github.io/demo/", height="500px", width="100%"),
            ],
            className="plots_container_second",
        )
    ],
    id="selected_location",
    style={"display": "none"},
)

# Preview
hovered_location_layout = html.Div(
    [html.Div([html.H3("city", id="hover_title"), dcc.Graph("summary")]),],
    id="hovered_location",
    style={"display": "none"},
)

print(dcc.__version__)  # 0.6.0 or above is required

app = dash.Dash(__name__, title='Urbanity', update_title=None)

suppress_callback_exceptions = True

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(
            [
                html.Div(
                    id="width", style={"display": "none"}
                ),  # Just to retrieve the width of the window
                html.Div(
                    id="height", style={"display": "none"}
                ),  # Just to retrieve the height of the window
                html.Div(
                    [
                        dcc.Loading(
                            id="loading-1",
                            children=[dcc.Graph(
                            id="map",
                            clear_on_unhover=True,
                            config={"doubleClick": "reset"},
                        )],
                            type="circle"
                            )
                    ],
                    className="background-map-container",
                ),
            ],
            id="map_container",
            style={"display": "flex"},
        ),
        filters_layout,
        selected_location_layout,
        hovered_location_layout,
    ],
    id="page-content",
    style={"position": "relative"},
)

#################
#   Figures     #
#################
selections = set()

####
@app.callback(
    Output("dropdown_menu_applied_filters", "style"),
    Output("select_filters_arrow", "title"),
    Input("select_filters_arrow", "n_clicks"),
    State("select_filters_arrow", "title"),
)
def toggle_applied_filters(n_clicks, state):
    style = {"display": "none"}
    if n_clicks is not None:
        if state == "is_open":
            style = {"display": "none"}
            state = "is_closed"
        else:
            style = {"display": "block"}
            state = "is_open"

    return style, state


selected_location = ""
x_close_selection_clicks = -1

@app.callback(Output("scatter-graph", "figure"),
              [Input("map", "clickData"),
               Input("xaxis", "value"),
               Input("yaxis", "value")])
def update_scatter(clickData, xaxis_col, yaxis_col):
    if clickData is None:
        location = "Singapore"
    else:
        location = clickData["points"][0]["text"]
    df = pd.read_csv(f"./data/{location}_graph/{location}_subzone_attr.csv")
    return {'data': [go.Scatter(x = df[xaxis_col], 
                            y = df[yaxis_col], 
                            text = df.iloc[:,0], 
                            mode = 'markers',
                            hoverinfo="text",
                            marker = {'size':5, 'opacity':0.5})],
        'layout': go.Layout(
        title = f"Scatterplot of {xaxis_col} against {yaxis_col}",
        xaxis = {'title': xaxis_col},
        yaxis = {'title': yaxis_col},
        hovermode = 'closest'
        )} 

    # fig = px.scatter(df, x=xaxis_col, y=yaxis_col, trendline="ols", hover_name = df.iloc[:,0])
    # fig.update_layout(
    #     title = f"Scatterplot of {xaxis_col} against {yaxis_col}",
    #     xaxis = {'title': xaxis_col},
    #     yaxis = {'title': yaxis_col},
    #     hovermode = 'closest'
    #     )
    # return fig

# @app.callback(Output("globe", "clickData"), [Input("map", "clickData")])
# def update_bubble_selection(click_map):
#     point = click_map
#     return point


@app.callback(
    Output("selected_location", "style"),
    Output("title_selected_location", "children"),
    [Input("map", "clickData")],
    Input("x_close_selection", "n_clicks"),
    Input("width", "n_clicks"),
    Input("height", "n_clicks"),
    [State("filters_drop", "value")])
def update_selected_location(clickData,
                             n_clicks,
                             width,
                             height,
                             dims_selected):
    global selected_location
    global x_close_selection_clicks
    location = "Singapore"
    lat = 1.3139843
    lon = 103.5640535
    if clickData is not None or dims_selected is not None:
        if clickData is not None:
            location = clickData["points"][0]["text"]
            lat = clickData["points"][0]["lat"]
            lon = clickData["points"][0]["lon"]
        if len(location) != 0:
            selected_location = location
            style = {"display": "block"}
        else:
            selected_location = ""
            location = selected_location
            style = {"display": "none"}
    else:
        style = {"display": "none"}

    if n_clicks != x_close_selection_clicks:
        style = {"display": "none"}
        selected_location = ""
        x_close_selection_clicks = n_clicks
    

    return (
        style,
        location,
    )

@app.callback(
    Output("subzone-container", "children"),
    Output("map", "clickData"),
    [Input("map", "clickData")],
    [State("filters_drop", "value")]
    )
def update_graph_location(clickData,
                          dims_selected):

    location = "Singapore"
    lat = 1.3139843
    lon = 103.5640535

    if clickData is not None or dims_selected is not None:
        if clickData is not None:
            location = clickData["points"][0]["text"]
            lat = clickData["points"][0]["lat"]
            lon = clickData["points"][0]["lon"]
    return (
        dash_deck.DeckGL(
                    json.loads(get_subzone(lat,lon,location,dims_selected).to_json()),
                    id="subzone-chart",
                    mapboxKey = mapbox_token,
                    enableEvents=['dragRotate']
                ),
        None
    )

hovered_location = ""
location = ""

@app.callback(
    Output("hovered_location", "style"),
    Output("summary", "figure"),
    Output("hover_title", "children"),
    [Input("map", "hoverData"), 
    Input("filters_drop", "value")],
)
def update_hovered_location(hoverData, filter):
    global hovered_location
    location = ""
    if hoverData is not None:
        location = hoverData["points"][0]["text"]
        if location != hovered_location:
            hovered_location = location
            style = {"display": "block"}
        
        else:
            hovered_location = ""
            location = ""
            style = {"display": "none"}

    else:
        hovered_location = ""
        location = ""
        style = {"display": "none"}

    return style, update_summary(location, filter), location
    

# subzone plot to benchmark cities
def get_subzone(lat, lon, location, filter):
    INITIAL_VIEW_STATE = pydeck.ViewState(
    latitude=lat, longitude=lon, zoom=10, max_zoom=16, pitch=25, bearing=0
    )

    DATA_URL = f"./data/{str.lower(location)}_graph/{str.lower(location)}_subzone_prop.geojson"
    COLOR_URL = f"./data/{str.lower(location)}_graph/{str.lower(location)}_color_scaler.json"
    SCALE_URL = f"./data/{str.lower(location)}_graph/{str.lower(location)}_scale_scaler.json"

    with open(DATA_URL, 'r') as f:
        DATA = json.load(f)

    with open(COLOR_URL, 'r') as file:
        COLOR = json.load(file)

    with open(SCALE_URL, 'r') as file:
        SCALE = json.load(file)
    
    filter = filter.replace(" ", "")

    geojson = pydeck.Layer(
        "GeoJsonLayer",
        DATA,
        opacity=0.9,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation= f'properties.{filter} / {SCALE[filter]}',
        elevation_scale = 50,
        get_fill_color=f"[230, properties.{filter}/{COLOR[filter]}, properties.{filter}/{COLOR[filter]}]",
        get_line_color=f"[230, properties.{filter}/{COLOR[filter]}, properties.{filter}/{COLOR[filter]}]",
    )

    r2 = pydeck.Deck(
        layers=[geojson],
        initial_view_state=INITIAL_VIEW_STATE,
    )

    return r2


# globe plot to benchmark cities
def get_globe(lat, lon):
    view_state = pydeck.ViewState(latitude=lat, longitude=lon, zoom=2)

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

# radar plot to compare index values
def update_summary(location, filter):
    path  = f'./data/{str.lower(location)}_density/{urban_indicators[filter]}.json'
    try:
        df = pd.read_json(path)
        median = df.iloc[:,0].median()
        tenth_perc = df.iloc[:,0].quantile(0.1)
        ninetyth_perc = df.iloc[:,0].quantile(0.9)
        values = list(df.iloc[:,0].values)
        fig = ff.create_distplot([values], [None], colors=['#ccff33'], bin_size = 0.1, show_curve=True, show_hist=False, show_rug=False)
        fig.add_vline(x=median, line_width=3, line_color='#ccff33')
        fig.update_layout(  
            title=filter,
            xaxis_range=[tenth_perc,ninetyth_perc],
            font_size=10,
            margin=dict(
                l=5,  # left margin
                r=5,  # right margin
                b=5,  # bottom margin
                t=20,  # top margin
            ),
            yaxis = {'showgrid': False},
            height=150,
            width=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend = False
        )
        return fig
    except FileNotFoundError:
        return go.Figure()


@app.callback(
    Output("page-content", "style"),
    Input("width", "n_clicks"),
    Input("height", "n_clicks"),
)
def set_page_size(width, height):
    return {"width": width, "height": height}


@app.callback(
    Output("map", "figure"),
    Output("map", "style"),
    [Input("filters_drop", "value")],
    Input("width", "n_clicks"),
    Input("height", "n_clicks"),
)
def update_map(filter_list, width, height):
    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=city_info_bin.Lat,
            lon=city_info_bin.Long,
            text=city_info_bin.City,
            name="Compatible location",
            mode="markers",
            marker=go.scattermapbox.Marker(size=8, opacity=0.9, color="#fefae0",),
            hovertemplate="<extra></extra>",
        )
    )

    mapbox_token = "pk.eyJ1Ijoid2luc3Rvbnl5bSIsImEiOiJjbDZyb3UwanQwOXNrM2pxOWRvNTJ2YmRlIn0.i2i24ARrX48r-tK1tX-yrQ"
    all_plots_layout = dict(
        mapbox=dict(
            style=mapbox_style,
            accesstoken=mapbox_token,
            # bounds= {"west": -180, "east": 180, "south": -90, "north": 90}
        ),
        legend=dict(
            bgcolor="rgba(51,51,51,0.6)",
            yanchor="top",
            y=0.35,
            xanchor="left",
            x=0,
            font=dict(family="Muli", size=15, color="white",),
        ),
        autosize=False,
        width=width,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo_bgcolor="rgba(0,0,0,0)",
    )
    fig.layout = all_plots_layout

    return fig, {"width": "100%", "height": "100%", "display":"block"}

# Get window size
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="get_window_width"),
    Output("width", "n_clicks"),
    [Input("url", "href")],
)

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="get_window_height"),
    Output("height", "n_clicks"),
    [Input("url", "href")],
)

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="move_hover"),
    Output("hovered_location", "title"),
    [Input("map", "hoverData")],
)

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
