import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from new_model import App
from help_homepage import Homepage
from help_functions import save_file, uploaded_files, read_df, upload_directory

from flask import Flask
import base64
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory

from scorecard_builder import ScorecardBuilder
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from sklearn.metrics import roc_curve, auc
from scipy.optimize import curve_fit
from scipy.stats import binom
import json
from sklearn.preprocessing import LabelEncoder



if not os.path.exists(upload_directory()):
    os.makedirs(upload_directory())

## server and app initialization ##
server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.UNITED])
app.config.suppress_callback_exceptions = True

## app layout ##
app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])


@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/new_model':
        return App()
    elif pathname == '/score_data':
        return App()
    else:
        return Homepage()


@app.callback(
    Output("df_select", "options"),
    [Input("upload-data", "filename"), 
     Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    return [{'label': i, 'value': i} for i in files]

@app.callback(
    Output('target_select', 'children'),
    [Input("df_select", "value")])
def select_target(value):
    if value:
        df = read_df(value,'first')
        return [dcc.Dropdown(id='target_dropdown',options=[{'label':i, 'value':i} for i in df.columns])]

@app.callback(
    [Output('target_value', 'children'),
     Output('drop_list', 'children')],
    [Input('target_dropdown', 'value')],
    [State("df_select", "value")])
def select_target_value(target_value, df_value):
    if (target_value is not None) and (df_value is not None):
        df = read_df(df_value,'all')
        return [
                [dcc.Dropdown(placeholder="Select Target value (0/1, Default/Performing)", options=[{'label':i, 'value':i} for i in df[target_value].unique()])],
                [dcc.Dropdown(placeholder="Optional: Drop Columns", options=[{'label':i, 'value':i} for i in df.columns],multi=True)]
               ]
        
@app.callback(
        Output('create_model_button','disabled'),
        [Input('target_dropdown','value')]
        )
def create_model_button(value):
    if value:
        return False

@app.callback(
        Output('intermediate_value','children'),
        [Input('create_model_button','n_clicks'),
         Input('drop_list', 'value')],
         [State('target_dropdown', 'value'),
         State('target_value', 'value'),
         State('df_select', 'value')]
        )
def intermediate_results(n_clicks, drop_columns, target_dropdown, target_value, df_value):
    if n_clicks>0:
        df = read_df(df_value,'all')
        target = df[[target_dropdown]]
        gb = target.columns[0]
        
        if drop_columns:
            drop = [gb] + drop_columns
            df.drop(drop,axis=1,inplace=True)
        else:
            df.drop(gb,axis=1,inplace=True)
            
        target[target[gb]!=target_value]=0
        target[target[gb]==target_value]=1
        
        new=ScorecardBuilder(df, target)
        model = new.create_scorecard()

        return json.dumps(datasets)
  

@app.callback(Output('pie_count', 'children'),
              [Input('intermediate_value', 'children')])
def pie_chart(value):
    datasets = json.loads(value)
    df = pd.read_json(datasets['df_pie'], orient='split')
    
    data = [
        {
            'values': [len(df.index),df.sum()[0]],
            'type': 'pie',
        },
    ]

    return [dcc.Graph(id='pie_graph',figure={'data': data,'layout': {'legend': {'': 0, 'y': 1}}})]

    
    
    
if __name__ == '__main__':
    app.run_server(debug=True)


