import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from help_navbar import Navbar

def Homepage():
    layout = html.Div([
    nav,
    body
    ])
    return layout

nav = Navbar()

body = dbc.Container(
    [
       dbc.Row([
               dbc.Col([
                     html.H2("Scorecard Builder"),
                     html.P('To utilize full potential and obtain meaningful results, please follow the guidelines pointed here.' ),
                   ],md=8,),
            ])
       ,dbc.Row([
               dbc.Col([
                   dbc.Jumbotron([
                    html.H1("Create New Model", className="display-4"),
                    html.P(
                        "If you want to create new model please click the button below.",
                        className="lead",
                    ),
                    html.Hr(className="my-2"),
                    html.P(
                        "This option will transfer you to our modeling platform. If you already created a model, keep scrolling"
                    ),
                    html.P(dbc.Button("Create New Model", color="primary",className="mr-1", href='/new_model'), className="lead"),
                                ])
                    ],md=6,),
               
              dbc.Col([
                   dbc.Jumbotron([
                    html.H1("Score Data", className="display-4"),
                    html.P(
                        "If model is already in production please click the button below.",
                        className="lead",
                    ),
                    html.Hr(className="my-2"),
                    html.P(
                        "This option will transfer you to our modeling platform where you can score new data with existing model"
                    ),
                    html.P(dbc.Button("Score data", color="primary", className="mr-1", href='/score_data'), className="lead"),
                ])
               ],md=6,),
            ])
        ],className="mt-4")


