import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__)

colors = {'background':'#111111', 'text':'#7FDBFF'}
df = pd.read_csv('./life_expectancy_years.csv')
columns = df.columns[df.columns != 'country']
df = pd.melt(df, id_vars=['country'], value_vars=columns, var_name='years', value_name='lifeExp')

df_map = pd.read_csv('./country_map.csv')
df_map = df_map[['name','eight_regions']]
df_map.columns = ['country', 'continent']
df = df.merge(df_map, on='country', how='left')

# Define year_options
year_options = []
for year in df['years'].unique():
  year_options.append({'label': str(year), 'value':year})

app.layout = html.Div(children=[
  dcc.Graph(id='graph'),
  dcc.Dropdown(id = 'year-picker', options=year_options, value=df['years'].min())
])

@app.callback(Output(component_id='graph', component_property = 'figure'),
              [Input(component_id='year-picker', component_property = 'value')])
def update_figure(selected_year):
  filtered_df = df[df['years']==selected_year]
  traces = []
  for continent_name in filtered_df['continent'].unique():
    df_by_continent = filtered_df[filtered_df['continent'] == continent_name]
    traces.append(go.Scatter(
      x = df_by_continent['gdpPercap'],
      y = df_by_continent['lifeExp'],
      mode='markers',
      opacity=0.7,
      marker = {'size':15},
      name = continent_name
    ))
  return {'data': traces,
          'layout': go.Layout(title='GapMinder GDP and Life Expectancy',
                              xaxis = {'title':'GDP Per Cap', 'type':'log'},
                              yaxis = {'title':'Life Expectancy'})}

if __name__ == '__main__':
    app.run_server()