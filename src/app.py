import os
import requests
import flask
import traceback

import requests
import json
import pandas as pd

# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

# import local modules
from config_settings import *
from datastore_loading import *
from data_processing import *
from layouts import *
from styling import *

# ---------------------------------
#   Page components
# ---------------------------------
def get_data():
    page_data = ['page_data']
    return page_data



# ---------------------------------
#   Serve layout
# ---------------------------------
def serve_layout():
    # Get data from API
    api_address = DATASTORE_URL + 'subjects'
    print(api_address)
    api_json = get_api_data(api_address)

    # Serializing json
    json_object = json.dumps(api_json, indent=4)
    

    layout = report_layout
    return layout

# ----------------------------------------------------------------------------
# APP Settings
# ----------------------------------------------------------------------------

external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                assets_folder=ASSETS_PATH,
                requests_pathname_prefix=os.environ.get("REQUESTS_PATHNAME_PREFIX", "/"),
                suppress_callback_exceptions=True
                )


app.layout = serve_layout

# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
# ---------------------------------
#   Callbacks
# ---------------------------------
