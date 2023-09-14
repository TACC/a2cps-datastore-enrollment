# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

# ---------------------------------
#   No Data
# ---------------------------------

no_data_layout = html.Div([
    html.P('There has been a problem loading the data for this report.'),   
    html.P('Please try again later.')
])


# ---------------------------------
#   Report
# ---------------------------------

report_layout = html.Div([
    html.P('report layout here')


])