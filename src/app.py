# ----------------------------------------------------------------------------
# PYTHON LIBRARIES
# ----------------------------------------------------------------------------
# Dash Framework
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate

# import local modules
from config_settings import *
from data_processing import *
from make_components import *
from styling import *


# ----------------------------------------------------------------------------
# APP Settings
# ----------------------------------------------------------------------------

external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                assets_folder=ASSETS_PATH,
                requests_pathname_prefix=REQUESTS_PATHNAME_PREFIX,
                )

# ----------------------------------------------------------------------------
# Page component Parts
# ----------------------------------------------------------------------------

header = html.Div(html.H1('A2CPS Blood Draw Report'))

if report_df.empty:
    data_check = "Can't access data"
else:
    data_check = "Data available"

content_tabs = html.Div([
                    dcc.Tabs(id='tabs_tables', children=[
                        dcc.Tab(label='Missing Values', children=[
                            html.Div(missing, id='tab_missing'),
                        ]),
                        dcc.Tab(label='Site Info', children=[
                            html.Div(site, id='tab_site'),
                        ]),
                        dcc.Tab(label='Timing', children=[
                            html.Div(timing, id='tab_timing'),
                        ]),
                        dcc.Tab(label='Hemolysis', children=[
                            html.Div(hemolysis, id='tab_hemolysis'),
                        ]),
                        dcc.Tab(label='Deviations', children=[
                            html.Div(deviations, id='tab_deviations'),
                        ]),
                    ]),
                    ])

# ----------------------------------------------------------------------------
# DASH APP LAYOUT FUNCTION
# ----------------------------------------------------------------------------
def create_content():
    content = html.Div([
        dbc.Row([
            dbc.Col(header),
        ],style={"margin":"10px"}),
        dbc.Row([
            dbc.Col(data_check),
        ],style={"margin":"10px"}),
        dbc.Row([
            dbc.Col(content_tabs),
        ],style={"margin":"10px"}),
    ])
    return content

def serve_layout():
    try:
        page_layout = html.Div(
            create_content()
        )
    except:
        page_layout = html.Div(['There has been a problem accessing the data for this application.'])
    return page_layout

app.layout = serve_layout


# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------

# Add callbacks to respond to user input here

# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server
