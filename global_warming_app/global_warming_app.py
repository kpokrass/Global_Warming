#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 12:18:02 2019

@author: kpokrass_pro
"""

import pandas as pd
import numpy as np
import plotly.offline as pyo
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

sea = pd.read_csv('sea_forecast_datetime.csv', index_col=0, parse_dates=True, header=None, names=['date', 'GMSL'])
sea_obs = sea.loc[:'2014']
sea_fcast = sea.loc['2014':]

temp = pd.read_csv('temp_forecast_datetime.csv', index_col=0, parse_dates=True, header=None, names=['date', 'temp'])
temp_obs = temp.loc[:'2018']
temp_fcast = temp.loc['2018':]

drown = pd.read_csv('coastline_pop.csv')

total_by_elevation = []

for col in drown.columns[4:]:
    sum_col = round((sum(drown[col]) / 1000000), 2)
    total_by_elevation.append(sum_col)
    
lin_elev = np.linspace(0.1,2,20)
lin_elev_round = []

for num in lin_elev:
    lin_elev_round.append(round(num,2))
    
drown_df = pd.concat([pd.Series(lin_elev_round, name='elevation'), pd.Series(total_by_elevation, name='pop')], axis=1)

year_options = []
for yr in list(range(1880,2263)):
    year_options.append({'label':str(yr), 'value':yr})



trace_obs = go.Scatter(x=sea_obs.index, y=sea_obs.GMSL, mode='lines', marker={'color': 'seagreen'}, name='Observed Cumulative Sea Level Change (mm)')
trace_fcast = go.Scatter(x=sea_fcast.index, y=sea_fcast.GMSL, mode='lines', line={'color': 'aqua', 'width':0.5}, name='Predicted Cumulative Sea Level Change (mm)')
trace_year = go.Scatter(x=[2026, 2026], y=[-200, 1200], line={'color':'crimson', 'dash':'dash'}, name='Selected Year')

data_sea = [trace_obs, trace_fcast, trace_year]

layout_sea = go.Layout(title='Global Sea Level Change (mm)')

trace_obs_temp = go.Scatter(x=temp_obs.index, y=temp_obs.temp, mode='lines', marker={'color': 'crimson'}, name='Observed Temperature Anomaly (degrees C')
trace_fcast_temp = go.Scatter(x=temp_fcast.index, y=temp_fcast.temp, mode='lines', line={'color': 'red', 'width':0.5}, name='Predicted Temperature Anomaly (degrees C')
trace_year_temp = go.Scatter(x=[2026, 2026], y=[-1, 4], line={'color':'darkblue', 'dash':'dash'}, name='Selected Year')

data_temp = [trace_obs_temp, trace_fcast_temp, trace_year_temp]

layout_temp = go.Layout(title='Global Temperature Anomaly')

trace_drown = go.Scatter(x=lin_elev_round, y=total_by_elevation, fill='tozeroy')

layout_drown = go.Layout(title='Millions of People Displaced by Rising Sea Levels', xaxis={'title':'Sea Level Change (m)'},
                         yaxis={'title':'Millions of People'})



app = dash.Dash()

#app.layout = html.Div([html.Div([dcc.Slider(id='year-select', min=1880,max= 2262, step=1,value=2000, marks={i: i for i in range(1880,2262)}), dcc.Graph(id='temp', figure={'data':data_temp, 'layout':layout_temp})], style={'width':'100%', 'display':'inline-block'}),
#                     html.Div([dcc.Graph(id='sea', figure={'data':data_sea, 'layout':layout_sea})], style={'width':'100%', 'display':'inline-block'})])



#fig = go.Figure(data=data, layout=layout)

#pyo.plot(fig)
    

app.layout = html.Div([html.H1('Global Warming and Rising Sea Levels', style={'textAlign':'center'}),
                       html.H3('Select a Year to See the Effects of Global Warming'),
                       html.Div([dcc.Dropdown(id='year-select', options=year_options, value='2026', style={'width': '35%'})]),
                       html.Div([dcc.Graph(id='temp', figure={'data':data_temp, 'layout':layout_temp}, style={'height':500})]),
                       html.Div([dcc.Graph(id='sea', figure={'data':data_sea, 'layout':layout_sea}, style={'height':500})]),
                       html.Div([dcc.Graph(id='who-is-drowning', figure={'data': [trace_drown], 'layout': layout_drown}, style={'height':500})])])
    
@app.callback(Output('temp', 'figure'),
              [Input('year-select', 'value')])
def update_temp(year):
    trace_obs_temp = go.Scatter(x=temp_obs.index, y=temp_obs.temp, mode='lines', line={'color': 'crimson', 'width':2}, name='Observed Temperature Anomaly (degrees C)')
    trace_fcast_temp = go.Scatter(x=temp_fcast.index, y=temp_fcast.temp, mode='lines', line={'color': 'darkviolet', 'width':2}, name='Predicted Temperature Anomaly (degrees C')
    trace_year_temp = go.Scatter(x=[year, year], y=[-1, 5.5], line={'color':'darkblue', 'dash':'dash'}, name='Selected Year')

    data_temp = [trace_obs_temp, trace_fcast_temp, trace_year_temp]

    layout_temp = go.Layout(title='Global Temperature Anomaly', xaxis={'title':'Year'}, yaxis={'title':'Temperature Anomaly (degrees C)'})
    
    return {'data':data_temp, 'layout':layout_temp}

@app.callback(Output('sea', 'figure'),
              [Input('year-select', 'value')])
def update_sea(year):
    trace_obs = go.Scatter(x=sea_obs.index, y=sea_obs.GMSL, mode='lines', marker={'color': 'seagreen'}, name='Observed Cumulative Sea Level Change (mm)')
    trace_fcast = go.Scatter(x=sea_fcast.index, y=sea_fcast.GMSL, mode='lines', line={'color': 'aqua', 'width':0.5}, name='Predicted Cumulative Sea Level Change (mm)')
    trace_year = go.Scatter(x=[year, year], y=[-200, 1200], line={'color':'crimson', 'dash':'dash'}, name='Selected Year')

    data_sea = [trace_obs, trace_fcast, trace_year]

    layout_sea = go.Layout(title='Global Sea Level Change (mm)', xaxis={'title':'Year'}, yaxis={'title':'Cumulative Sea Level Change (mm)'})
    
    return {'data':data_sea, 'layout': layout_sea}

@app.callback(Output('who-is-drowning', 'figure'),
              [Input('year-select', 'value')])
def update_who_is_drowning(year):
    str_year = str(year)
    sea_level = round((sea.loc[str_year].mean().item() / 1000), 1)
    
    pop_year = drown_df.loc[drown_df.elevation <= sea_level]
    pop_safe = drown_df.loc[drown_df.elevation >= sea_level]
    
    pop_max = pop_year.elevation.max()
    
    pop_line = drown_df.loc[drown_df.elevation <= sea_level]['pop'].max()
    
    trace_drown = go.Scatter(x=pop_year.elevation, y=pop_year['pop'], mode='lines', line={'color':'navy'}, fill='tozeroy', name='Displaced People')
    trace_line = go.Scatter(x=[0, pop_max], y=[pop_line, pop_line], line={'color':'black', 'dash':'dash'}, name='')
    trace_safe = go.Scatter(x=pop_safe.elevation, y=pop_safe['pop'], mode='lines', line={'color':'palegreen'}, fill='tozeroy', name='Safe People')

    layout_drown = go.Layout(title='Millions of People Displaced by Rising Sea Levels', xaxis={'title':'Sea Level Change (m)'},
                         yaxis={'title':'Millions of People'})
    
    return {'data': [trace_drown, trace_safe, trace_line], 'layout':layout_drown}


if __name__ == '__main__':
    app.run_server()





