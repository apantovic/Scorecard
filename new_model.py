import pandas as pd
import pickle
### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
from help_functions import save_file, uploaded_files, read_df, upload_directory

from help_navbar import Navbar
nav = Navbar()

body = dbc.Container([
    html.Div([
       dbc.Row([
               dbc.Col(html.H1("Step 1:"),md=2),
               dbc.Col(html.P("Upload Data"),md=2),
               dbc.Col(dcc.Upload(
                               id="upload-data", children=html.Div(["Drag and drop or click to select a file to upload."]),
                               style={"lineHeight": "60px", "borderWidth": "1px", "borderStyle": "dashed", "borderRadius": "5px", "textAlign": "center", "margin": "10px"}, multiple=True,
                               ),
                       md=8)
               ],align="center", justify="center", style={"margin-top":"10px"}),
        dbc.Row([
                html.P("Upload .csv, .txt, .xlsx or .xls files with predictor columns and target one, that will be used for modeling purposes")
                ]),
            ]),
    html.Hr(),
        html.Div([ 
                dbc.Row([
                        dbc.Col(html.H1("Step 2:"),md=2),
                        dbc.Col(html.P("Select Relevant Data - Dataset to work on, target column, target value(in case when target is not 1/0 coded) and optionally columns that are extra and should not be used for modeling"),md=10),
                        ],align="left", justify="center", style={"margin-top":"10px"}),
                dbc.Row([
                    dbc.Col(html.Div([dcc.Dropdown( id='df_select', placeholder="Select database to work on")]),md=3),
                    dbc.Col(html.Div(id='target_select'),md=3),
                    dbc.Col(html.Div(id='target_value'),md=3),
                    dbc.Col(html.Div(id='drop_list'),md=3),
                    ],align="center", justify="center"),
                ],id='df_select_div',style={'display': 'none'}),
    html.Hr(),
        html.Div([
                dbc.Row([
                        dbc.Button("Create Model", id='create_model_button', color="primary", disabled=True, block=True),
                    ],style={"margin-top":"10px","margin-bottom":"20px"}),
                ]),
    html.Hr(),
        html.Div(id='intermediate_value', style={'display': 'none'}),
        html.Div(id='histogram'),
        html.Div(id='pie_count'),  
        html.Div(id='correlation'),
        html.Div(id='model_perf'),
        html.Div(id='div_model_auc'),
        html.Div(id='x_finecoarse', children=
                 [html.Li(),
                  dbc.Row([
                    dbc.Col(html.H1('Check Variable Groupping'),md=6),
                    dbc.Col(dcc.Dropdown(id='x_finecoarse_dropdown',placeholder="Select variable"), md=6),
                   ],align="center", justify="center"),]
                 ,style={'display': 'none'}),
        
        
        
        html.Div(id='fine_coarse_block'),
        html.Div(id='gini_iv'), 
        
        ],className="mt-12")



def App():
    layout = html.Div([
        nav,
        body
        ])
    return layout




