import os
import requests
import flask
import traceback
import logging


import requests
import json
import pandas as pd

# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

DATASTORE_URL = os.environ.get("DATASTORE_URL","url not found")
DATASTORE_URL = os.path.join(DATASTORE_URL, "api/")

AUTH_CHECK_URL = os.environ.get("AUTH_CHECK_URL","url not found")

logger = logging.getLogger(__name__)

server = flask.Flask('app')

# ---------------------------------
#   Get Data From datastore
# ---------------------------------

def get_api_data(api_address):
    api_json = {}
    try:
        try:
            auth_check = requests.get(AUTH_CHECK_URL, flask.request.cookies)

            if auth_check.status_code == 200:
                logger.info(f"User has successfully requested an authorization check")
                response = requests.get(api_address, auth_check)
            else:
                logger.warning(f"User has attempted an authorization check but something went wrong")
                raise Exception
        
        except Exception as e:
            return('error: {}'.format(e))
        
        request_status = response.status_code
        if request_status == 200:
            api_json = response.json()
            return api_json
        else:
            return str(request_status)
    except Exception as e:
        traceback.print_exc()
        api_json['json'] = 'error: {}'.format(e)
        return api_json


# ---------------------------------
#   Page components
# ---------------------------------
def serve_layout():

    layout = html.Div([
        dcc.Store(id='store_data'),
        html.H1('A2CPS Data from API'),
        dbc.Row([
            dbc.Col([
                html.P('Call for new data from APIs (if needed):'),
                dcc.Dropdown(
                    id='dropdown-api',
                   options=[
                        # {'label': 'APIs', 'value': 'apis'},
                        {'label': 'Consort', 'value': 'consort'},
                       {'label': 'Subjects', 'value': 'subjects'},
                       {'label': 'Imaging', 'value': 'imaging'},
                       {'label': 'Blood Draws', 'value': 'blood'},
                   ],
                ),
                html.Button('Reload API', id='submit-api', n_clicks=0),
                html.P('Available Data / DataFrames '),
                dcc.Loading(
                    id="loading-content",
                    type="default",
                    children = [
                        dcc.Dropdown(
                            id ='dropdown_datastores'
                        ),
                    ]
                ),

                html.Div(id='df-columns'),
            ],width=2),
            dbc.Col([
                dcc.Store(id='store-table'),
                html.Div(id='div-message'),
                html.Div(id='div-content')
            ], width=10),
        ]),


    ])
    return layout

# ---------------------------------
#   build app
# ---------------------------------
external_stylesheets_list = [dbc.themes.SANDSTONE, 'https://codepen.io/chriddyp/pen/bWLwgP.css'] #  set any external stylesheets

app = Dash('app', server=server,
                external_stylesheets=external_stylesheets_list,
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                requests_pathname_prefix=os.environ.get("REQUESTS_PATHNAME_PREFIX", "/"))

app.layout = serve_layout

if __name__ == '__main__':
    app.run_server()


# ---------------------------------
#   Callbacks
# ---------------------------------
@app.callback(
    Output('store_data', 'data'),
    Output('dropdown_datastores', 'options'),
    Input('submit-api', 'n_clicks'),
    State('dropdown-api', 'value'),
    State('store_data', 'data')
)
def update_datastore(n_clicks, api, datastore_dict):
    if n_clicks == 0:
        raise PreventUpdate
    div_message = []    
    if not datastore_dict:
        datastore_dict = {}
    api_json = {}
    print(api)
    if api:
        api_address = DATASTORE_URL + api
        print(api_address)
        api_json = get_api_data(api_address)
        if api_json:
            datastore_dict[api] = api_json  
            print('got api-json')
        else:
            print('no api-json')

    options = []
    if datastore_dict:
        for api in datastore_dict.keys():
            api_label = api + ' [' + datastore_dict[api]['date'] + ']'
            api_header_option = {'label': api_label, 'value': api_label, 'disabled': True}
            options.append(api_header_option)
            for dataframe in datastore_dict[api]['data'].keys():
                api_dataframe_option = {'label': '  -' + dataframe, 'value': api + ':' + dataframe}
                options.append(api_dataframe_option)

    else:
        print('no datastore_dict')
    return datastore_dict, options

@app.callback(
    Output('div-content','children'),
    Input('dropdown_datastores', 'value'),
    State('store_data', 'data')
)
def show_table(selected_dataframe, datastore_dict):
    if selected_dataframe:
        api, dataframe = selected_dataframe.split(':')
        print(api, dataframe )
        # print(datastore_dict[api]['data'][dataframe][0]) # Add this line if you want to see an example row of the data passed through to the table.
        div_table = dt.DataTable(
            data=datastore_dict[api]['data'][dataframe],
            virtualization=True,
                style_table={
                'overflowX': 'auto',
                'width':'100%',
                'margin':'auto'},
                page_current= 0,
                page_size= 15,
        )
        columns_list = list(datastore_dict[api]['data'][dataframe][0].keys())

        columns_div = html.Div([
            html.P('Table Columns:'), html.P(', '.join(columns_list))
            ])
        return html.Div([columns_div, div_table])
    else:
        return html.P('Please Select an API and Table to display data')