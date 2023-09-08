 # Libraries
import traceback
# Data
# File Management
import os # Operating system library
import pathlib # file paths
import json
import requests
import math
import numpy as np
import pandas as pd # Dataframe manipulations
import sqlite3
import datetime
from datetime import datetime, timedelta

# import local modules
from config_settings import *

# ----------------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------------

def use_b_if_not_a(a, b):
    if not pd.isnull(a):
        x = a
    else:
        x = b
    return x

def create_multiindex(df, split_char):
    cols = df.columns
    multi_cols = []
    for c in cols:
        multi_cols.append(tuple(c.split(split_char)))
    multi_index = pd.MultiIndex.from_tuples(multi_cols)
    df.columns = multi_index
    return df

def convert_to_multindex(df, delimiter = ': '):
    cols = list(df.columns)
    cols_with_delimiter = [c for c in cols if delimiter in c]
    df_mi = df[cols_with_delimiter].copy()
    df_mi.columns = [tuple(x) for x in df_mi.columns.str.split(delimiter)]
    df_mi.columns = pd.MultiIndex.from_tuples(df_mi.columns)
    return df_mi

def datatable_settings_multiindex(df, flatten_char = '_'):
    ''' Plotly dash datatables do not natively handle multiindex dataframes.
    This function generates a flattend column name list for the dataframe,
    while structuring the columns to maintain their original multi-level format.

    Function returns the variables datatable_col_list, datatable_data for the columns and data parameters of
    the dash_table.DataTable'''
    datatable_col_list = []

    levels = df.columns.nlevels
    if levels == 1:
        for i in df.columns:
            datatable_col_list.append({"name": i, "id": i})
    else:
        columns_list = []
        for i in df.columns:
            col_id = flatten_char.join(i)
            datatable_col_list.append({"name": i, "id": col_id})
            columns_list.append(col_id)
        df.columns = columns_list

    datatable_data = df.to_dict('records')

    return datatable_col_list, datatable_data


# ----------------------------------------------------------------------------
# Get dataframes and parameters
# ----------------------------------------------------------------------------

def get_time_parameters(end_report, report_days_range = 7):
    today = datetime.now()
    start_report = end_report - timedelta(days=report_days_range)
    start_report_text = str(start_report.date()) #dt.strftime('%m/%d/%Y')
    end_report_text = str(end_report.date()) #dt.strftime('%m/%d/%Y')
    report_range_msg = 'This report generated on: ' + str(datetime.today().date()) + ' covering the previous ' + str(report_days_range) + ' days.'
    report_date_msg = 'This report generated on: ' + str(datetime.today().date())
    return today, start_report, end_report, report_date_msg, report_range_msg



# ----------------------------------------------------------------------------
# DATA DISPLAY DICTIONARIES
# ----------------------------------------------------------------------------

def load_display_terms_from_github(display_terms_gihub_raw_url):
    '''Load the data file that explains how to translate the data columns and controlled terms into the English language
    terms to be displayed to the user'''
    try:
        display_terms = pd.read_csv(display_terms_gihub_raw_url)

        # Get display terms dictionary for one-to-one records
        display_terms_uni = display_terms[display_terms.multi == 0]
        display_terms_dict = get_display_dictionary(display_terms_uni, 'api_field', 'api_value', 'display_text')

        # Get display terms dictionary for one-to-many records
        display_terms_multi = display_terms[display_terms.multi == 1]
        display_terms_dict_multi = get_display_dictionary(display_terms_multi, 'api_field', 'api_value', 'display_text')

        return display_terms, display_terms_dict, display_terms_dict_multi
    except Exception as e:
        traceback.print_exc()
        return None


def get_display_dictionary(display_terms, api_field, api_value, display_col):
    '''from a dataframe with the table display information, create a dictionary by field to match the database
    value to a value for use in the UI '''
    try:
        display_terms_list = display_terms[api_field].unique() # List of fields with matching display terms

        # Create a dictionary using the field as the key, and the dataframe to map database values to display text as the value
        display_terms_dict = {}
        for i in display_terms_list:
            term_df = display_terms[display_terms.api_field == i]
            term_df = term_df[[api_value,display_col]]
            term_df = term_df.rename(columns={api_value: i, display_col: i + '_display'})
            term_df = term_df.apply(pd.to_numeric, errors='ignore')
            display_terms_dict[i] = term_df
        return display_terms_dict

    except Exception as e:
        traceback.print_exc()
        return None

# ---------------------------------
#   Get Data From datastore
# ---------------------------------

# def get_api_data(api_address):
#     api_json = {}
#     try:
#         try:
#             response = requests.get(api_address)
#         except:
#             return('error: {}'.format(e))
#         request_status = response.status_code
#         if request_status == 200:
#             api_json = response.json()
#             return api_json
#         else:
#             return request_status
#     except Exception as e:
#         traceback.print_exc()
#         api_json['json'] = 'error: {}'.format(e)
#         return api_json

# ----------------------------------------------------------------------------
# DATA CLEANING
# ----------------------------------------------------------------------------


def get_enrollment_dataframe(consented_df):
    """Add period / datetime columns for enrollment report"""
    try:
        # Select Subset of columns
        enroll_cols = ['record_id','main_record_id','obtain_date','ewdateterm','mcc', 'screening_site', 'surgery_type']
        enrollment = consented_df[enroll_cols].copy()

        # Convert datetime colums and calculate new
        datetime_cols = ['obtain_date','ewdateterm']
        enrollment[datetime_cols] = enrollment[datetime_cols].apply(pd.to_datetime, errors='coerce')
        enrollment['obtain_month'] = enrollment['obtain_date'].dt.to_period('M')
        enrollment['Site'] = enrollment['screening_site'] + ' (' + enrollment['surgery_type'] + ')'
        return enrollment
    except Exception as e:
        traceback.print_exc()
        return None
# def get_centers(subjects, consented, display_terms):
#     ''' Get list of centers to use in the system '''
#     # screening centers
#     screening_centers_list = subjects.redcap_data_access_group_display.unique()
#     screening_centers_df = pd.DataFrame(screening_centers_list, columns = ['redcap_data_access_group_display'])
#     # treatment centers
#     # centers_list = consented.redcap_data_access_group_display.unique()
#     # Convert centers list to use ANY center, not just ones already used
#     centers_list = list(display_terms[display_terms['api_field']=='redcap_data_access_group']['data_dictionary_values'])


#     centers_df = pd.DataFrame(centers_list, columns = ['treatment_site'])
#     return screening_centers_df, centers_df


# # ----------------------------------------------------------------------------
# # Enrollment FUNCTIONS
# # ----------------------------------------------------------------------------

# def get_enrollment_data(consented):
#     enroll_cols = ['record_id','main_record_id','obtain_date','mcc', 'screening_site', 'surgery_type',]
#     enrolled = consented[consented['ewdateterm'].isna()][enroll_cols] # Do we want to do this?
#     enrolled['obtain_month'] = enrolled['obtain_date'].dt.to_period('M')
#     enrolled['Site'] = enrolled['screening_site'] + ' (' + enrolled['surgery_type'] + ')'
#     return enrolled

def enrollment_rollup(enrollment_df, index_col, grouping_cols, count_col_name, cumsum=True, fill_na_value = 0):
    """Roll up enrollment figures according to a varying set of columns to use as the groupings"""
    enrollment_count = enrollment_df.groupby([index_col] + grouping_cols).size().reset_index(name=count_col_name).fillna({count_col_name:fill_na_value})
    if cumsum:
        enrollment_count['Cumulative'] = enrollment_count.groupby(grouping_cols)[count_col_name].cumsum()

    return enrollment_count

## TOD: This function is throwing the following warning:
# PerformanceWarning: dropping on a non-lexsorted multi-index without a level parameter may impact performance.
#   site_enrollments = site_enrollments.set_index(['Month','Year']).drop(columns='obtain_month')
def get_site_enrollments(enrollment_count, mcc):
    """ Get enrollments by particular MCC and site """
    site_enrollments = enrollment_count[enrollment_count.mcc == mcc]
    site_enrollments = pd.pivot(site_enrollments, index=['obtain_month'], columns = 'Site', values=['Monthly','Cumulative'])
    site_enrollments = site_enrollments.swaplevel(0,1, axis=1).sort_index(axis=1).reindex(['Monthly','Cumulative'], level=1, axis=1).reset_index()
    site_enrollments['Month'] = site_enrollments['obtain_month'].dt.strftime("%B")
    site_enrollments['Year'] = site_enrollments['obtain_month'].dt.strftime("%Y")
    site_enrollments = site_enrollments.set_index(['Month','Year']).drop(columns='obtain_month')
    return site_enrollments

def get_enrollment_expectations():
    """Generate a pdf of enrollment expectations.  These are currently hardcoded here as a dictionary, but could be externalized"""
    enrollment_expectations_dict = {'mcc': ['1','1','2','2'],
                                'surgery_type':['TKA','Thoracic','Thoracic','TKA'],
                                'start_month': ['02/22','06/22','02/22','06/22'],
                                'expected_cumulative_start':[280,10,70,10], 'expected_monthly':[30,10,30,10]}

    enrollment_expectations_df = pd.DataFrame.from_dict(enrollment_expectations_dict)
    enrollment_expectations_df['start_month'] =  pd.to_datetime(enrollment_expectations_df['start_month'], format='%m/%y').dt.to_period('M')

    enrollment_expectations_df['mcc'] = enrollment_expectations_df['mcc'].astype(int)

    return enrollment_expectations_df

def get_enrollment_expectations_monthly(enrollment_expectations_df):
    mcc_type_expectations = pd.DataFrame()
    for i in range(len(enrollment_expectations_df)):
        mcc = enrollment_expectations_df.iloc[i]['mcc']
        surgery_type = enrollment_expectations_df.iloc[i]['surgery_type']
        start_month = enrollment_expectations_df.iloc[i]['start_month']
        expected_start_count = enrollment_expectations_df.iloc[i]['expected_cumulative_start']
        expected_monthly = enrollment_expectations_df.iloc[i]['expected_monthly']

        months = pd.period_range(start_month,datetime.now(),freq='M').tolist()
        expected_monthly_series = [expected_start_count] + (len(months)-1) * [expected_monthly]

        for index, month in enumerate(months):
            new_row = {'mcc':mcc,
                       'surgery_type': surgery_type,
                       'Month': month,
                       'Expected: Monthly': expected_monthly_series[index],
                       'Expected: Cumulative': expected_start_count+index*expected_monthly}
            mcc_type_expectations = pd.concat([mcc_type_expectations, pd.DataFrame([new_row])], ignore_index=True)

    return mcc_type_expectations

def rollup_enrollment_expectations(enrollment_df, enrollment_expectations_df, monthly_expectations):
    enrollment_df = enrollment_df.merge(enrollment_expectations_df[['mcc','surgery_type','start_month']], how='left', on=['mcc','surgery_type'])

    # Determine if values in early months or should be broken out
    enrollment_df['expected_month'] = np.where(enrollment_df['obtain_month'] <= enrollment_df['start_month'], enrollment_df['start_month'], enrollment_df['obtain_month'] )

    # Rolll up data by month
    ee_rollup = enrollment_rollup(enrollment_df, 'expected_month', ['mcc','surgery_type'], 'Monthly').sort_values(by='mcc')
    ee_rollup_rename_dict={
        'expected_month':'Month',
        'Monthly': 'Actual: Monthly',
        'Cumulative': 'Actual: Cumulative'
    }
    ee_rollup.rename(columns=ee_rollup_rename_dict,inplace=True)

    # Merge on Monthly expectations
    ee_rollup = ee_rollup.merge(monthly_expectations, how='left', on=['mcc','surgery_type','Month'])

    # Calculate percent peformance actual vs expectations
    ee_rollup['Percent: Monthly'] = (100 * ee_rollup['Actual: Monthly'] / ee_rollup['Expected: Monthly']).round(1).astype(str) + '%'
    ee_rollup['Percent: Cumulative'] = (100 * ee_rollup['Actual: Cumulative'] / ee_rollup['Expected: Cumulative']).round(1).astype(str) + '%'
    ee_rollup.loc[ee_rollup['Actual: Monthly'] == 0, 'Percent: Monthly'] = ''

    # Add Site name column
    ee_rollup['Site'] = ee_rollup.apply(lambda x: 'MCC' + str(x['mcc']) + ' (' + x['surgery_type'] + ')',axis=1)

    # TODO: Put these in their own function to create table for 
    # ee_rollup_cols = ['Site','Month', 'Actual: Monthly', 'Actual: Cumulative',
    #    'Expected: Monthly', 'Expected: Cumulative', 'Percent: Monthly','Percent: Cumulative']

    # ee_rollup = ee_rollup[ee_rollup_cols]

    return ee_rollup

def format_rollup_enrollment_expectations(ee_rollup):
    """ Format for display: subset of columns in proper order"""
    ee_rollup_cols = ['Site','Month', 'Actual: Monthly', 'Actual: Cumulative',
       'Expected: Monthly', 'Expected: Cumulative', 'Percent: Monthly','Percent: Cumulative']

    ee_rollup = ee_rollup[ee_rollup_cols]
    return ee_rollup
# # ----------------------------------------------------------------------------
# # GET DATA FOR PAGE
# # ----------------------------------------------------------------------------

# def get_enrollment_tables(consented):
#     enrollment_df = get_enrollment_data(consented)

#     enrollment_df, index_col, grouping_cols, count_col_name = enrollment_df, 'obtain_month', ['mcc','screening_site','surgery_type','Site'], 'Monthly'
#     enrollment_count = enrollment_rollup(enrollment_df, index_col, grouping_cols, count_col_name)

#     mcc1_enrollments = get_site_enrollments(enrollment_count, 1)
#     mcc2_enrollments = get_site_enrollments(enrollment_count, 2)

#     enrollment_expectations_df = get_enrollment_expectations()
#     monthly_expectations = get_enrollment_expectations_monthly(enrollment_expectations_df)
#     summary_rollup = rollup_enrollment_expectations(enrollment_df, enrollment_expectations_df, monthly_expectations)

#     return mcc1_enrollments, mcc2_enrollments, summary_rollup


def get_plot_date(enrollment_df, summary_rollup):
    cols = ['Month', 'mcc', 'surgery_type', 'Expected: Monthly', 'Expected: Cumulative']
    expected_data = summary_rollup[cols].copy()
    expected_data.columns = [s.replace('Expected: ','') for s in list(expected_data.columns)]
    expected_data['type'] = 'Expected'
    ec= enrollment_rollup(enrollment_df, 'obtain_month', ['mcc','surgery_type'], 'Monthly').rename(columns={'obtain_month':'Month'})
    ec['type'] = 'Actual'

    # df = ec.append(expected_data, ignore_index=True )
    df = pd.concat([ec, expected_data], ignore_index=True )

    df['Month'] = df['Month'].apply(lambda x: x.to_timestamp())

    return df
