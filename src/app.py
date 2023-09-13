import os
import requests
import flask
import traceback


import requests
import json
import pandas as pd

# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from dash_extensions import Download
from dash_extensions.snippets import send_file

# Plotly
import plotly.express as px

# import local modules
from config_settings import *
from datastore_loading import *
from enrollment_etl import * 
from layouts import *
from styling import *

# ----------------------------------------------------------------------------
# ENV Variables & DATA PARAMETERS
# ----------------------------------------------------------------------------
current_folder = os.path.dirname(__file__)
ASSETS_PATH = os.path.join(current_folder,'assets')

# Pointers to official files stored at github repository main branch
screening_sites_github_url = 'https://raw.githubusercontent.com/TACC/a2cps-datastore-weekly/main/src/assets/screening_sites.csv'
display_terms_github_url = 'https://raw.githubusercontent.com/TACC/a2cps-datastore-weekly/main/src/assets/A2CPS_display_terms.csv'

# load display terms and screening sites
screening_sites = pd.read_csv(screening_sites_github_url)
display_terms, display_terms_dict, display_terms_dict_multi = load_display_terms_from_github(display_terms_github_url)


# ----------------------------------------------------------------------------
# FUNCTIONS FOR DASH UI COMPONENTS
# ----------------------------------------------------------------------------
def store_multiindex_data(df):
    table_columns, table_data = datatable_settings_multiindex(df)
    data_dict = {}
    data_dict['columns'] = table_columns
    data_dict['data'] = table_data
    return data_dict

def build_datatable_multi(df, table_id, fill_width = False):
    table_columns, table_data = datatable_settings_multiindex(df)
    new_datatable = build_datatable(table_id, table_columns, table_data, fill_width)
    return new_datatable

def build_datatable(table_id, table_columns, table_data, fill_width = False):
    try:
        new_datatable =  dt.DataTable(
                id = table_id,
                columns=table_columns,
                data=table_data,
                css=[{'selector': '.row', 'rule': 'margin: 0; flex-wrap: nowrap'},
                     {'selector':'.export','rule':export_style }
                    # {'selector':'.export','rule':'position:absolute;right:25px;bottom:-35px;font-family:Arial, Helvetica, sans-serif,border-radius: .25re'}
                    ],
                # style_cell= {
                #     'text-align':'left',
                #     'vertical-align': 'top',
                #     'font-family':'sans-serif',
                #     'padding': '5px',
                #     'whiteSpace': 'normal',
                #     'height': 'auto',
                #     },
                # style_as_list_view=True,
                # style_header={
                #     'backgroundColor': 'grey',
                #     'whiteSpace': 'normal',
                #     'fontWeight': 'bold',
                #     'color': 'white',
                # },

                fill_width=fill_width,
                style_table={'overflowX': 'auto'},
                # export_format="csv",
                merge_duplicate_headers=True,
            )
        return new_datatable
    except Exception as e:
        traceback.print_exc()
        return None
    


# ---------------------------------
#   MOVE THIS TO ETL FILE
# ---------------------------------
consentedcols = ['age', 'consent_process_form_complete', 'date_and_time',
'date_of_contact', 'dem_race', 'dem_race_display', 'dem_race_original',
'ethnic', 'ethnic_display', 'ewcomments', 'ewdateterm', 'ewdisreasons',
'ewpireason', 'ewprimaryreason', 'ewprimaryreason_display', 'genident',
'genident_display', 'main_record_id', 'mcc', 'obtain_date',
'participation_interest', 'participation_interest_display',
'ptinterest_comment', 'reason_not_interested', 'record_id',
'record_id_end', 'record_id_start', 'redcap_data_access_group',
        'redcap_data_access_group_display', 'screening_age',
        'screening_ethnicity', 'screening_ethnicity_display',
        'screening_gender', 'screening_gender_display', 'screening_race',
'screening_race_display', 'screening_site', 'sex', 'sex_display',
'site', 'sp_data_site', 'sp_data_site_display', 'sp_exclarthkneerep',
'sp_exclbilkneerep', 'sp_exclinfdxjoint', 'sp_exclnoreadspkenglish',
'sp_exclothmajorsurg', 'sp_exclprevbilthorpro', 'sp_inclage1884',
'sp_inclcomply', 'sp_inclsurg', 'sp_mricompatscr', 'sp_surg_date',
'sp_v1_preop_date', 'sp_v2_6wk_date', 'sp_v3_3mo_date', 'start_12mo',
       'start_6mo', 'start_v1_preop', 'start_v2_6wk', 'start_v3_3mo',
'surgery_type', 'treatment_site', 'treatment_site_type']

enrollment_cols = ['record_id','main_record_id','obtain_date','ewdateterm', 'mcc','screening_site','surgery_type']



# ---------------------------------
#   Serve layout
# ---------------------------------
def serve_layout():
    # Get data from API
    api_address = DATASTORE_URL + 'subjects'
    api_json = get_api_data(api_address)

    # Initate page components
    page_meta_dict, enrollment_dict = {'report_date_msg':''}, {}
    report_date = datetime.now()
    report_children = ['exception']

    # print('time parameters')
    today, start_report, end_report, report_date_msg, report_range_msg  = get_time_parameters(report_date)
    page_meta_dict['report_date_msg'] = report_date_msg
    page_meta_dict['report_range_msg'] = report_range_msg
    print_table_dict = {}
    # print(page_meta_dict)

    if api_json['date']:
        page_meta_dict['data_date'] = api_json['date']
    else:
        page_meta_dict['data_date'] = 'Data Date Unavailable'

    if api_json['data']['consented']:                
        consented = pd.DataFrame(api_json['data']['consented'])
        enrolled =  get_enrollment_dataframe(consented)
        
        enrollment_count = enrollment_rollup(enrolled, 'obtain_month', ['mcc','screening_site','surgery_type','Site'], 'Monthly')
        mcc1_enrollments = get_site_enrollments(enrollment_count, 1).reset_index()        
        print_table_dict['MCC 1 Site Enrollment'] = store_multiindex_data(mcc1_enrollments) # mcc1_enrollments.to_dict('records')
        
        mcc2_enrollments = get_site_enrollments(enrollment_count, 2).reset_index()
        print_table_dict['MCC 2 Site Enrollment']  = store_multiindex_data(mcc2_enrollments) #  mcc2_enrollments.to_dict('records'),


        
        enrollment_expectations_df = get_enrollment_expectations()
        monthly_expectations = get_enrollment_expectations_monthly(enrollment_expectations_df)
        summary_rollup = rollup_enrollment_expectations(enrolled, enrollment_expectations_df, monthly_expectations)
        summary_rollup_formatted = format_rollup_enrollment_expectations(summary_rollup)
        
        expected_plot_df = get_plot_date(enrolled, summary_rollup)
        summary_options_list = [(x, y) for x in summary_rollup.mcc.unique() for y in summary_rollup.surgery_type.unique()]
        tab_summary_content_children = []

        for tup in summary_options_list:
            tup_summary = summary_rollup[(summary_rollup.mcc == tup[0]) & (summary_rollup.surgery_type == tup[1])]
            plot_df = expected_plot_df[(expected_plot_df.mcc == tup[0]) & (expected_plot_df.surgery_type == tup[1])]

            if len(tup_summary) > 0:
                table_cols = ['Date: Year', 'Date: Month', 'Actual: Monthly', 'Actual: Cumulative',
                                'Expected: Monthly', 'Expected: Cumulative', 'Percent: Monthly','Percent: Cumulative']
                tup_df = tup_summary.set_index('Month')[table_cols].sort_index(ascending=True)
                tup_stup_table_df = convert_to_multindex(tup_df)
                table_id = 'table_mcc'+ str(tup[0])+'_'+tup[1]
                figure_id = 'figure_mcc'+ str(tup[0])+'_'+tup[1]
                tup_table = build_datatable_multi(tup_stup_table_df, table_id)
                plot_title = 'Cumulative enrollment: MCC' + str(tup[0])+' ('+tup[1] +')'
                tup_fig = px.line(plot_df, x="Month", y="Cumulative", title=plot_title, color = 'type')
                tup_fig_div = dcc.Graph(figure = tup_fig, id=figure_id)
            else:
                tup_message = 'There is currently no data for ' + tup[1] + ' surgeries at MCC' + str(tup[0])
                tup_table = html.Div(tup_message)
                tup_fig_div = html.Div()

            tup_section = html.Div([
                dbc.Row([
                    dbc.Col([html.H2('MCC' + str(tup[0]) + ': ' + tup[1]),])
                ]),
                dbc.Row([
                    dbc.Col([html.Div(tup_table)])
                ]),
                dbc.Row([
                    dbc.Col([html.Div(tup_fig_div)])
                ]),


            ], style={'margin-bottom':'20px'})

            tab_summary_content_children.append(tup_section)

    ### BUILD PAGE COMPONENTS
        # data_source = 'Data Source: ' + page_meta_dict['data_source']  # TO DO: ADD THIS BACK IN IF DATASTORE UPDATED TO PROVIDE IT
        data_date = 'Data Date: ' + page_meta_dict['data_date']

        tab_enrollments = html.Div([
            html.H2('MCC 1'),
            build_datatable_multi(mcc1_enrollments, 'mcc1_datatable'),
            html.H2('MCC 2'),
            build_datatable_multi(mcc2_enrollments, 'mcc2_datatable')
            ])

        tab_summary_content = html.Div(
            tab_summary_content_children
        )

        tabs = html.Div([
                    dcc.Tabs(id='tabs_tables', children=[
                        dcc.Tab(label='Site Enrollments', id='tab_1', children=[
                            html.Div([tab_enrollments], id='section_1'),
                        ]),
                        dcc.Tab(label="Site / Surgery Summary", id='tab_3', children=[
                            html.Div([tab_summary_content], id='section_3'),
                        ]),

                    ]),
                    ])
    else:
        # data_source = 'unavailable'
        data_date = 'unavailable'
        tabs = 'Data unavailable'
        print_table_dict['tables'] = {'None Found'}

    page_layout = html.Div([
        dcc.Store(id='store_meta', data = page_meta_dict),
        dcc.Store(id='store_tables', data = print_table_dict),
        Download(id="download-dataframe-xlxs"),
        dcc.Loading(
            id="loading-2",
            children=[
                html.Div(
            [
                dbc.Row([
                    dbc.Col([
                        html.H1('Enrollment Report', style={'textAlign': 'center'})
                    ], width={"size":6, "offset":3}),
                    dbc.Col([
                        html.P('Version date: 06/29/2023')
                    ], width=3),

                ]),

                dbc.Row([
                    dbc.Col([
                        # html.P(data_source),
                        html.P(data_date),
                    ], width=6),
                    dbc.Col([
                        html.Button("Download as Excel",n_clicks=0, id="btn_xlxs",style =EXCEL_EXPORT_STYLE ),
                        html.Div(id='test-div')
                    ], width=6, style={'text-align': 'right'}),
                ]),

                dbc.Row([
                    dbc.Col([
                        tabs,
                    ])
                    ]),

            ]
    ,id='report_content'
    , style =CONTENT_STYLE
    )
            ],
            type="circle",
        )
    ], style=TACC_IFRAME_SIZE
    )

    return page_layout

# ----------------------------------------------------------------------------
# APP Settings
# ----------------------------------------------------------------------------

external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                assets_folder=ASSETS_PATH,
                requests_pathname_prefix=os.environ.get("REQUESTS_PATHNAME_PREFIX", "/"),
                suppress_callback_exceptions=False
                )


app.layout = serve_layout

# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server

# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------


# Create excel spreadsheel
@app.callback(
        Output("download-dataframe-xlxs", "data"),
        # Output('test-div','children'),
        Input("btn_xlxs", "n_clicks"), 
        State("store_tables","data")
        )
def click_excel(n_clicks, table_dict):
    if n_clicks == None:
        raise PreventUpdate
    if table_dict:
        try:
            today = datetime.now().strftime('%Y_%m_%d')
            download_filename = datetime.now().strftime('%Y_%m_%d') + '_a2cps_enrollment_report_data.xlsx'

            writer = pd.ExcelWriter(download_filename, engine='xlsxwriter')
            tables = list(table_dict.keys())
            for table in tables:
                excel_sheet_name = table
                df = pd.DataFrame(table_dict[table]['data'])
                # convert multiindex columns and remove the '_'
                new_cols = []
                for i in list(df.columns):
                    if i[0] == '_':
                        new_cols.append(i[1:])
                    else:
                        new_cols.append(i.replace('_',': '))
                df.columns = new_cols

                if len(df) == 0 :
                    df = pd.DataFrame(columns =['No data for this table'])
                df.to_excel(writer, sheet_name=excel_sheet_name, index = False)
            
            writer.save()
            excel_file =  send_file(writer, download_filename)
            return excel_file

        except Exception as e:
            traceback.print_exc()
            return None
