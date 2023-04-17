
import dash
from dash import dcc, html, callback
import dash_deck 
import pydeck
import scipy
import scipy.stats as stats
import plotly.graph_objects as go
import plotly.figure_factory as ff
import geopandas as gpd
import pandas as pd
import numpy as np
from dash.dependencies import ClientsideFunction, Input, Output, State
import plotly.express as px
from ipywidgets import widgets
import json

mapbox_token = "pk.eyJ1Ijoid2luc3Rvbnl5bSIsImEiOiJjbDZyb3UwanQwOXNrM2pxOWRvNTJ2YmRlIn0.i2i24ARrX48r-tK1tX-yrQ"
mapbox_style = "mapbox://styles/mapbox/dark-v11"

# name mapper
with open("./data/urbanity_indicators.json", "r") as f:
    urban_indicators = json.load(f)

with open("./data/poly_columns.json", "r") as f:
    aggregated_indicators = json.load(f)

with open("./data/GUN.json", "r") as f:
    links = json.load(f)

datasets = {k.split('_')[0]:gpd.read_file(v) for k, v in links.items() if 'subzone' in k}

# Get dataframe
cities_df = pd.read_csv("./data/cities_location.csv")

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
                            html.H4(f"Linear Relationship", style={'margin-left':'1%'})], style = {'display':'inline-block', 'width':'100%'}),
                        html.Div([
                            dcc.Dropdown(id = 'xaxis',
                                        options = aggregate_filters,
                                        value="Mean Building Complexity",
                                        clearable=False)
                                ], style = {'width':'50%', 'display':'inline-block', 'padding-top':'0px'}),
                        html.Div([
                            dcc.Dropdown(id = 'yaxis',
                                        options = aggregate_filters,
                                        value="No. of Nodes",
                                        clearable=False)
                                ], style = {'width':'50%', 'display':'inline-block'}),
                        dcc.Graph(id='scatter-graph', style = {'height':'73.5%'})
                    ],
                    className="plots_container_child",
                ),
                html.Div([
                        html.Div([
                            html.H4("Subzone Statistics", style={'margin-left':'1%'})], style = {'display':'inline-block', 'width':'100%'}),
                        html.Div([
                            dcc.Dropdown(id = 'subzone-stats',
                                        options = aggregate_filters,
                                        value="PopSum",
                                        clearable=False)
                                ], style = {'width':'50%', 'display':'inline-block', 'padding-top':'0px'}),
                        html.Div(children = [], 
                                id='subzone-container',
                                style={"position":"relative", 'height':'75%'})
                    ],
                    className="plots_container_child",
                ),
            ],
            className="plots_container",
        ),
        html.Div(
            [
                html.H3("City Network", id = "city-label", style={'padding-left':'0%', 'margin-left':'1.5%', 'display':'inline-block'}),
                html.Div([dcc.RadioItems(['Grid', 'Network'], 'Grid', inline=True, id = 'grid-network')], style = {'font-size':'16px','display':'inline-block', 'float':'right', 'margin-right':'3%', 'margin-top':'1.5%'}),
                dcc.Loading(
                            id="loading-2",
                            children=[],
                            type="circle"
                            )
            ],
            className="plots_container_second",
        )
    ],
    id="selected_location",
    style={"display": "none"},
)

# Preview
hovered_location_layout = html.Div(
    [html.Div([html.H3("city", id="hover_title"), dcc.Graph("summary")])],
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
            [   dcc.Store(id='datasets', data={name: df.to_json() for name, df in datasets.items()}, storage_type='memory'),
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
        hovered_location_layout
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
x_close_selection_clicks = 1

@app.callback(Output("scatter-graph", "figure"),
              [Input("map", "clickData"),
               Input("xaxis", "value"),
               Input("yaxis", "value")],
               [State('datasets', 'data')])
def update_scatter(clickData, xaxis_col, yaxis_col, attr_datasets):
    global selected_location
    if clickData is None:
        raise dash.exceptions.PreventUpdate
    elif selected_location != "":
        df = gpd.read_file(attr_datasets[selected_location])
    return  {'data': [go.Scatter(x = df[xaxis_col], 
                            y = df[yaxis_col], 
                            text = df['index'], 
                            mode = 'markers',
                            hoverinfo="text",
                            marker = {'size':7, 'opacity':1, 'color':'#FFFFFF',
                                    'line':{'width':1, 'color':'#60D9D9'}})],
                        'layout': go.Layout(
                        title = f"{xaxis_col} against {yaxis_col}",
                        xaxis = {'title': xaxis_col, 'zeroline':True, 'showgrid':False, 'linewidth':1, 'linecolor':'#fefae0'},
                        yaxis = {'title': yaxis_col, 'zeroline':True, 'showgrid':False, 'linewidth':1, 'linecolor':'#fefae0'},
                        font_color = '#fefae0',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        hovermode = 'closest'
        )}


@app.callback(Output('loading-2', 'children'),
              [Input('map', 'clickData'),
               Input('grid-network', 'value')])
def update_network_graph(clickData, grid_network):
    global selected_location
    if clickData is None and selected_location == "":
        raise dash.exceptions.PreventUpdate  
    elif selected_location != "":
        return html.Iframe(id="network-graph", src = f"https://winstonyym.github.io/{selected_location}-{grid_network.lower()}/" , height="600px", width="100%")

@app.callback(Output("city-label", "children"),
              [Input("map", "clickData")])
def update_network_name(clickData):
    global selected_location
    if clickData is None and selected_location == "":
        raise dash.exceptions.PreventUpdate  
    elif selected_location != "":
        location = selected_location
    elif clickData is not None:
        location = clickData["points"][0]["text"]
    return (f"{location.title()} City Network")


@app.callback(
    Output("selected_location", "style"),
    Output("map", "clickData"),
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
    if clickData is None:
        raise dash.exceptions.PreventUpdate
    elif clickData is not None and n_clicks != x_close_selection_clicks:
        selected_location = clickData["points"][0]["text"]
        style = {"display": "block"}
        return style, clickData
    
    elif clickData is not None and n_clicks == x_close_selection_clicks:
        style = {"display": "none"}
        x_close_selection_clicks+=1
        clickData = None
        return style, clickData


@app.callback(
    Output("subzone-container", "children"),
    [Input("map", "clickData"),
     Input("subzone-stats", "value")],
    State('datasets', 'data')
    )
def update_graph_location(clickData,
                          dims_selected,
                          poly_datasets):
    global selected_location
    if selected_location == "":
        raise dash.exceptions.PreventUpdate
    elif selected_location != "":
        lat = cities_df['Lat'][cities_df['City']==selected_location].values[0]
        lon = cities_df['Long'][cities_df['City']==selected_location].values[0]
        dataset = gpd.read_file(poly_datasets[selected_location])
        max = dataset[dims_selected].max()
        dataset = dataset.reset_index()
        # subzone plot to benchmark cities
        view_state = pydeck.ViewState(latitude=lat, longitude=lon, zoom=10, max_zoom=16, pitch=40, bearing=0)
        geojson = pydeck.Layer(
            "GeoJsonLayer",
            dataset,
            opacity=0.9,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            pickable=True,
            auto_highlight=True,
            get_fill_color=[255, 255, 255],
            get_line_color=[0,0,0]
        )

        r = pydeck.Deck(
            layers=geojson,
            initial_view_state=view_state
        )
        tooltip_str = f"<b>{'{'}{'index'}{'}'}:</b> {'{'}{dims_selected}{'}'}"
        return (dash_deck.DeckGL(
                    r.to_json(),
                    id="subzone-chart",
                    tooltip={'html': tooltip_str,
                             "style": {"backgroundColor": "white", "color": "black"}
                             },
                    mapboxKey = mapbox_token,
                    enableEvents=['dragRotate']
                )
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
    

# radar plot to compare index values
def update_summary(location, filter):
    path  = f'./data/{location}_density/{urban_indicators[filter]}.json'
    
    try:
        df = pd.read_json(path)
        median = df.iloc[:,0].median()
        tenth_perc = df.iloc[:,0].quantile(0.1)
        ninetyth_perc = df.iloc[:,0].quantile(0.9)
        values = list(df.iloc[:,0].values)
        fig = ff.create_distplot([values],[None], colors=['#b2ff9e'], show_curve=True, curve_type='kde', show_hist=False, show_rug=False)
        fig.add_vline(x=median, line_width=3, line_color='#affc41')
        fig.update_layout(  
            title=filter,
            xaxis_range=[tenth_perc,ninetyth_perc],
            yaxis = dict(
                visible = False,
                zeroline = True,
                showgrid = True
            ),
            xaxis = dict(
                visible = True,
                zeroline = True,
                showgrid = True,
                linecolor = "grey"
            ),
            font_size=10,
            margin=dict(
                l=5,  # left margin
                r=5,  # right margin
                b=5,  # bottom margin
                t=20,  # top margin
            ),
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
            lat=cities_df.Lat,
            lon=cities_df.Long,
            text=cities_df.City,
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
