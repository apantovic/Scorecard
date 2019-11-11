import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table
import plotly.graph_objs as go
import plotly.figure_factory as ff

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
    [Output("df_select_div", "style"),
     Output("df_select", "options")],
    [Input("upload-data", "filename"), 
     Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    return {'display': 'block'}, [{'label': i, 'value': i} for i in files]

@app.callback(
    Output('target_select', 'children'),
    [Input("df_select", "value")])
def select_target(value):
    if value:
        df = read_df(value,'first')
        return [dcc.Dropdown(id='target_dropdown',placeholder="Select Target",options=[{'label':i, 'value':i} for i in df.columns])]

@app.callback(
    [Output('target_value', 'children'),
     Output('drop_list', 'children')],
    [Input('target_dropdown', 'value')],
    [State("df_select", "value")])
def select_target_value(target_value, df_value):
    if (target_value is not None) and (df_value is not None):
        df = read_df(df_value,'all')
        return [
                [dcc.Dropdown(id='target_value_dropdown',placeholder="Select Target value (0/1, Default/Performing)", options=[{'label':i, 'value':i} for i in df[target_value].unique()])],
                [dcc.Dropdown(id='drop_columns_dropdown',placeholder="Optional: Drop Columns", options=[{'label':i, 'value':i} for i in df.columns],multi=True)]
               ]
        
@app.callback(
        Output('create_model_button','disabled'),
        [Input('target_value_dropdown','value')]
        )
def create_model_button(value):
    if value:
        return False

@app.callback(
        Output('intermediate_value','children'),
        [Input('create_model_button','n_clicks'),
         Input('drop_columns_dropdown', 'value')],
         [State('target_value_dropdown', 'value'),
         State('target_dropdown', 'value'),
         State('df_select', 'value')]
        )
def intermediate_results(n_clicks, drop_columns, target_value, target_dropdown, df_value):
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

        return json.dumps(model)
  

@app.callback(Output('pie_count', 'children'),
              [Input('intermediate_value', 'children'),
               Input('create_model_button','n_clicks')])
def pie_chart(value,n_clicks):
    if n_clicks:
        datasets = json.loads(value)
        df_pie = pd.read_json(datasets['df_pie'], orient='split')
        df_coef=pd.read_json(datasets['df_model_coef'], orient='split').reset_index()  
        df_coef.columns = ['Variable','Parameters','Std Err','P-value']
        
        data = [{
                'values': [len(df_pie.index),df_pie.sum()[0]],
                'type': 'pie',
               },]
        
    
        return html.Div([
                dbc.Row([
                dbc.Col(html.H1('Model Coefficients'),md=6),
                dbc.Col(html.H1('Distribution of Event vs Non-Event'),md=6,align="center"),
                ]),
                dbc.Row([
                dbc.Col(dash_table.DataTable(
                        id='model_coef_table',
                        columns=[{"name": i, "id": i} for i in df_coef.columns],
                        data=df_coef.round({'Parameters': 4, 'Std Err': 4, 'P-value': 4}).to_dict('records'),
                        ),md=6),
                dbc.Col(dcc.Graph(id='pie_graph',figure={'data': data,'layout': {'legend': {'': 'Non-Event', 'y': 'Event'}}}),md=6),
                ],align="center", justify="center"),
]),



# =============================================================================
#         
# @app.callback(Output('histogram', 'children'),
#               [Input('intermediate_value', 'children'),
#                Input('create_model_button','n_clicks')])
# def create_hist(value,n_clicks):
#     datasets = json.loads(value)
#     df = pd.read_json(datasets['df_pie'], orient='split')
#     gb = df.columns[0]
#     
#     df[gb] = df[gb].fillna(0)
# 
#     x1 = df[df[gb]==1].to_numpy()
#     x2 = df[df[gb]==0].to_numpy()
# 
#     fig = ff.create_distplot([x1,x2], ['Bad','Good'], bin_size = .2)
#     return [dcc.Graph(
#     id='histogram', 
#     figure=fig
#     )]
# 
# =============================================================================


@app.callback(
    Output('correlation', 'children'),
    [Input('intermediate_value', 'children')])
def correlation_table(value):
    datasets = json.loads(value)
    
    df=pd.read_json(datasets['df_correlation_model'], orient='split')
    
    trace = go.Heatmap(x=df.index.values, y=df.columns.values, z=df.values, colorscale='Viridis', colorbar={"title": "Percentage"}, showscale=True)
    
    return html.Div([
            dbc.Row([
                dbc.Col(html.H1('Correlation Matrix'),md=6),
                ]),
            dbc.Row([
                    dcc.Graph(id='corr_graph',
                        figure={"data": [trace],
                              }),
            ],align="center"),]),



@app.callback(
    Output('model_perf', 'children'),
    [Input('intermediate_value', 'children')])
def model_perf(value):
    datasets = json.loads(value)
    df=pd.read_json(datasets['df_model_performance'], orient='split')
    df['Value']=round(df['Value'],3)
 
    return html.Div([
            html.H1('Model Performance'),
                dbc.Row([
                dbc.Col(daq.LEDDisplay(label='AUC',color="#FF5E5E", value=str(df['Value'][0])),md=2),
                dbc.Col(daq.LEDDisplay(label='GINI',color="#FF5E5E", value=str(df['Value'][1])),md=2),
                dbc.Col(daq.LEDDisplay(label='Kolmogorov-Smirnov',color="#FF5E5E", value=str(df['Value'][2])),md=2),
                dbc.Col(daq.Gauge(color={"gradient":True,"ranges":{"red":[0,40],"yellow":[40,70],"green":[70,100]}}, value=df['Value'][0]*100,label='Overall Model Quality', max=100, min=0),md=4),
                ],align="center"),]),
        

@app.callback(
    Output('div_model_auc', 'children'),
    [Input('intermediate_value', 'children')])
def model_auc(value):
    datasets = json.loads(value)
    tpr=pd.read_json(datasets['df_model_tpr'], orient='split').reset_index()
    fpr=pd.read_json(datasets['df_model_fpr'], orient='split').reset_index()
   
    return html.Div([
            html.H1('Model ROC curve'),
                dbc.Col(dcc.Graph(figure={'data': [{'x':fpr[0].tolist(),'y':tpr[0].tolist(),'type':'line','name':'ROC Curve'}, {'x':[0,1],'y':[0,1],'type':'line','name':'45 degrees line'}]}),md=6),
        ])

    
    

@app.callback(
    Output('gini_iv', 'children'),
    [Input('intermediate_value', 'children')])
def gini_iv(value):
    datasets = json.loads(value)
    df=pd.read_json(datasets['df_gini_iv'], orient='split').round(2).reset_index()
    df.columns=['Variable','Gini','IV']
                    
    return html.Div([
            dbc.Row([
                dbc.Col(dash_table.DataTable(
                        id='gini_iv_table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict('records'),
                        ),md=6),
                ],align="center", justify="center"),
])


@app.callback(
    [Output('x_finecoarse', 'display'),
     Output('x_finecoarse_dropdown','options')],
    [Input('intermediate_value', 'children')]
    )
def fine_coarse_dropdown(value):
    datasets = json.loads(value)
    df = pd.read_json(datasets['df_finecoarse_vars'], orient='split')
    df.columns = ['Variable']
    return [{'display': 'block'}], [{'label':i, 'value':i} for i in df['Variable']]
            

@app.callback(
    Output('fine_coarse_block', 'children'),
    [Input('intermediate_value', 'children')],
    [State('x_finecoarse_dropdown', 'value')],
      )

def fine_class_table(value,dropdown):
    datasets = json.loads(value)
    df_fine=pd.read_json(datasets['df_fine_class'], orient='split')
    df_fine=df_fine[df_fine['Variable']==dropdown].drop('Variable',axis=1).reset_index()
    df_fine = df_fine.rename(columns={ 'index' : 'Group'})
    
    df_coarse=pd.read_json(datasets['df_coarse'], orient='split')
    df_coarse=df_coarse[df_coarse['Variable_name']==dropdown].drop('Variable_name',axis=1).reset_index()
    df_coarse=df_coarse.drop(['WoE_lag','var_lag','index','group_pct','WoE_diff','yes'],axis=1)
    
    
    return html.Div([
            html.Li(),
# =============================================================================
#             dbc.Row([
#                 dbc.Col(dash_table.DataTable(
#                         id='fine_table',
#                         columns=[{"name": i, "id": i} for i in df_fine.columns],
#                         data=df_fine.to_dict('records'),
#                         ),md=6),
#                 dbc.Col(dcc.Graph(id='fine_graph',
#                         figure={"data": [{'x':df_fine['From/To'].values,
#                                          'y':df_fine['WoE'].values,
#                                          'type': 'bar',
#                                          'name':'Coarse Classing'}]}
#                                 ),md=6),
#                 ],align="center", justify="center"),
#             html.Li(),
#             dbc.Row([
#                 dbc.Col(dash_table.DataTable(
#                         id='coarse_table',
#                         columns=[{"name": i, "id": i} for i in df_coarse.columns],
#                         data=df_coarse.to_dict('records'),
#                         ),md=6),
#                 dbc.Col(dcc.Graph(id='coarse_graph',
#                         figure={"data": [{'x':df_coarse['From/To'].values,
#                                          'y':df_coarse['WoE'].values,
#                                          'type': 'bar',
#                                          'name':'Coarse Classing'}]}
#                                 ),md=6),
#                 ],align="center", justify="center"),
# =============================================================================
])


    
if __name__ == '__main__':
    app.run_server(debug=True)


