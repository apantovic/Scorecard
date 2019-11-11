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

body = dbc.Container(
    [
       dbc.Row([
        html.H1("Score New Data"),
       ]),
       dbc.Row([ 
        html.H2("Upload data"),
        ]),
       dbc.Row([
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to select a file to upload."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        ]),
        html.Div([
                dbc.Row([
                    dbc.Col(html.Div([dcc.Dropdown( id='df_select', placeholder="Select model to work on",)]),md=3),
                    dbc.Col(html.Div(id='target_select'),md=3),
                    dbc.Col(html.Div(id='target_value'),md=3),
                    dbc.Col(html.Div(id='drop_list'),md=3),
                    ]),
                ]),
        html.Div([
                dbc.Row([
                        dbc.Col(
                        dbc.Button("Create Model", id='create_model_button', color="primary", disabled=True, block=True),
                        md=12),
                    ]),
                ]),
        html.Div(id='intermediate_value', style={'display': 'none'}),
        html.Div(id='pie_count'),  
        
        html.Div(id='model_coef'),
        html.Div(id='model_perf'),
        html.Div(id='div_model_auc'),
        
        
        ],className="mt-12")



def App():
    layout = html.Div([
        nav,
        body
        ])
    return layout




