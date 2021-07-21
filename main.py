import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import pandas_datareader.data as web
import datetime
import json
import urllib.request
import re
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np
from io import StringIO
from ftplib import FTP
import plotly.graph_objs as go
from collections import deque


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def update_data():
    with urllib.request.urlopen("https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json") as url:
        mag_data = json.loads(url.read().decode())

    mag_data_pandas = pd.DataFrame(mag_data)
    mag_data_pandas.columns = mag_data_pandas.iloc[0, :].values
    mag_data_pandas = mag_data_pandas.drop(0)
    mag_data_pandas.index = pd.to_datetime(mag_data_pandas['time_tag'])

    pd.to_numeric(mag_data_pandas.bx_gsm, downcast='float')
    pd.to_numeric(mag_data_pandas.by_gsm, downcast='float')
    pd.to_numeric(mag_data_pandas.bz_gsm, downcast='float')

    # Seems reasonably to separate different data calls into different functions
    with urllib.request.urlopen("https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json") as url:
        plasma_data = json.loads(url.read().decode())

    plasma_data_pandas = pd.DataFrame(plasma_data)
    plasma_data_pandas.columns = plasma_data_pandas.iloc[0, :].values
    plasma_data_pandas = plasma_data_pandas.drop(0)
    plasma_data_pandas.index = pd.to_datetime(plasma_data_pandas['time_tag'])

    pd.to_numeric(plasma_data_pandas.density, downcast='float')
    pd.to_numeric(plasma_data_pandas.speed, downcast='float')
    pd.to_numeric(plasma_data_pandas.temperature, downcast='float')

    return ([html.Div([
        html.Div([
            html.H3('Interplanetary Magnetic Field'),
            dcc.Graph(id='g1', figure={
                'data': [{'x': mag_data_pandas['time_tag'], 'y': mag_data_pandas['bx_gsm'], 'type': 'line', 'name': 'Bx'},
                         {'x': mag_data_pandas['time_tag'], 'y': mag_data_pandas['by_gsm'], 'type': 'line', 'name': 'By'},
                         {'x': mag_data_pandas['time_tag'], 'y': mag_data_pandas['bz_gsm'], 'type': 'line', 'name': 'Bz'},
                         ]})],
            className="six columns"),

        html.Div([
            html.H3('Solar Wind Speed'),
            dcc.Graph(id='g2', figure={
                'data': [{'x': plasma_data_pandas['time_tag'], 'y': plasma_data_pandas['speed'], 'type': 'line', 'name': 'SW Speed'},
                         ]})],
            className="six columns"),

        html.Div([
            html.H3('Solar Wind Density'),
            dcc.Graph(id='g3', figure={
                'data': [{'x': plasma_data_pandas['time_tag'], 'y': plasma_data_pandas['density'], 'type': 'line', 'name': 'SW Density'},
                         ]})],
            className="six columns"),

        html.Div([
            html.H3('Solar Wind Temperature'),
            dcc.Graph(id='g4', figure={
                'data': [{'x': plasma_data_pandas['time_tag'], 'y': plasma_data_pandas['temperature'], 'type': 'line', 'name': 'SW Temperature'},
                         ]})],
            className="six columns"),

    ], className="row")])


app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,
        n_intervals=0,
        interval=60000,
        max_intervals=-1,
    ),

    html.Div([
        html.Div(id="mag_field", children=update_data()
                 )
    ]),
])


@app.callback(Output("mag_field", "children"), [Input("my_interval", "n_intervals")])
def update_data_div():
    return update_data()


if __name__ == '__main__':
    app.run_server(debug=True)
