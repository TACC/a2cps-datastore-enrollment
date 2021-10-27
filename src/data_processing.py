  # Libraries
# Data
# File Management
import os # Operating system library
import pathlib # file paths
import json
import requests
import math
import numpy as np
import pandas as pd # Dataframe manipulations
import datetime
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------------------

def dict_to_col(df, index_cols, dict_col, new_col_name = 'category', add_col_as_category=True):
    ''' Take a dataframe with index columns and a column containing a dictionary and convert
    the dictionary json into separate columns'''
    new_df = df[index_cols +[dict_col]].copy()
    new_df.dropna(subset=[dict_col], inplace=True)
    new_df.reset_index(inplace=True, drop=True)
    if add_col_as_category:
        new_df[new_col_name] = dict_col
    new_df = pd.concat([new_df, pd.json_normalize(new_df[dict_col])], axis=1)
    return new_df

def move_column_inplace(df, col, pos):
    ''' move a column position in df'''
    col = df.pop(col)
    df.insert(pos, col.name, col)

def calc_stacked_bar(df, flag_col):
    ''' Count and calculate pass/fail percents for columns that use 1 as a flag for failure.
    In this case these are: 'bscp_lav1_not_obt', 'bscp_sample_obtained', 'bscp_paxg_aliq_na'
    '''

    flag_df = df[['MCC','Visit','Screening Site',flag_col]].fillna(0)
    flag_df[flag_col] = flag_df[flag_col].astype(int)
    flag_df_count = flag_df.groupby(['MCC','Visit','Screening Site'])[flag_col].count().rename('count').reset_index()
    flag_df_fail = flag_df.groupby(['MCC','Visit','Screening Site'])[flag_col].sum().rename('fail').reset_index()
    flag_df_all = flag_df_count.merge(flag_df_fail, how='outer', on = ['MCC','Visit','Screening Site'])

    flag_df_all['Collected'] = 100 -100 * flag_df_all['fail'] / flag_df_all['count']
    flag_df_all['Fail'] = 100 - flag_df_all['Collected']

    flag_df_all.drop(columns=['count','fail'], inplace=True)

    flag_df_all = flag_df_all.set_index(['MCC','Visit','Screening Site']).stack().reset_index()
    flag_df_all.columns = ['MCC','Visit','Screening Site','Type','Percentage']

    return flag_df_all


# ----------------------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------------------

# Directions for locating file at TACC
file_url_root ='https://api.a2cps.org/files/v2/download/public/system/a2cps.storage.community/reports'
report = 'blood'
report_suffix = report + '-[mcc]-latest.json'
mcc_list=[1,2]
index_url = '/'.join([file_url_root, report,'index.json'])

def load_data():
    try:
        # Read files into json
        data_json = {}
        for mcc in mcc_list:
            json_url = '/'.join([file_url_root, report,report_suffix.replace('[mcc]',str(mcc))])
            r = requests.get(json_url)
            if r.status_code == 200:
                data_json[mcc] = r.json()

        # Convert JSON into dataframe with visit type as category column
        new_df = pd.DataFrame()
        dict_cols = ['Baseline Visit', '6-Wks Post-Op', '3-Mo Post-Op']

        for mcc in mcc_list:
            if mcc in data_json.keys():
                m = data_json[mcc]
                mdf = pd.DataFrame.from_dict(m, orient='index')
                mdf.dropna(subset=['screening_site'], inplace=True)
                mdf.reset_index(inplace=True)
                mdf['MCC'] = mcc
                for c in dict_cols:
                    if c in mdf.columns:
                        df = dict_to_col(mdf, ['index','MCC','screening_site'], c,'Visit')
                        new_df = pd.concat([new_df, df])
                        new_df.reset_index(inplace=True, drop=True)

        # move columns to beginning of DF, so it goes index, mcc, category, baseline dict, 6 week dict, 3 month dict
        move_column_inplace(new_df, 'Visit', 2)
        move_column_inplace(new_df, new_df.columns[-1], 4)
        move_column_inplace(new_df, new_df.columns[-1], 4)

        # Convert numeric columns
        numeric_cols = ['bscp_aliq_cnt','bscp_protocol_dev','bscp_protocol_dev_reason']
        new_df[numeric_cols] = new_df[numeric_cols].apply(pd.to_numeric,errors='coerce')

        # Convert datetime columns
        datetime_cols = ['bscp_time_blood_draw','bscp_aliquot_freezer_time','bscp_time_centrifuge']
        new_df[datetime_cols] = new_df[datetime_cols].apply(pd.to_datetime,errors='coerce')

        # Add calculated columns
        # Calculate time to freezer: freezer time - blood draw time
        new_df['time_to_freezer'] = new_df['bscp_aliquot_freezer_time'] -new_df['bscp_time_blood_draw']
        new_df['time_to_freezer_minutes'] = new_df['time_to_freezer'].dt.components['hours']*60 + new_df['time_to_freezer'].dt.components['minutes']

        # Calculate time to centrifuge: centrifuge time - blood draw time
        new_df['time_to_centrifuge'] = new_df['bscp_time_centrifuge'] -new_df['bscp_time_blood_draw']
        new_df['time_to_centrifuge_minutes'] = new_df['time_to_centrifuge'].dt.components['hours']*60 + new_df['time_to_centrifuge'].dt.components['minutes']

        # Calculate times exist in correct order
        # time_order = (new_df['bscp_aliquot_freezer_time'] > new_df['bscp_time_centrifuge']) & (new_df['bscp_time_centrifuge'] > new_df['bscp_time_blood_draw'])
        # time_limits = (new_df['time_to_centrifuge_minutes'] <= 30) & (new_df['time_to_freezer_minutes'] <= 60)
        # new_df['time_order'] = time_order
        # new_df['time_limits'] = time_limits
        new_df['time_values_check'] = (new_df['time_to_centrifuge_minutes'] < new_df['time_to_freezer_minutes'] ) & (new_df['time_to_centrifuge_minutes'] <= 30) & (new_df['time_to_freezer_minutes'] <= 60)

        # Get 'Site' column that combines MCC and screening site
        new_df['Site'] = 'MCC' + new_df['MCC'].astype(str) + ': ' + new_df['screening_site']

        # Convert Deviation Numeric Values to Text
        deviation_dict = {1:'Unable to obtain blood sample -technical reason',
                          2: 'Unable to obtain blood sample -patient related',
                          3: 'Sample handling/processing error'}
        deviation_df = pd.DataFrame.from_dict(deviation_dict, orient='index')
        deviation_df.reset_index(inplace=True)
        deviation_df.columns = ['bscp_protocol_dev_reason','Deviation Reason']
        new_df = new_df.merge(deviation_df, on='bscp_protocol_dev_reason', how='left')

        # Rename columns for report DF

        drop_cols = ['Baseline Visit', '6-Wks Post-Op', '3-Mo Post-Op']

        rename_dict = {'index':'ID',
                      'screening_site': 'Screening Site',
                      'bscp_deg_of_hemolysis': 'Degree of Hemolysis'
                      }
        report_df = new_df.drop(columns=drop_cols).rename(columns=rename_dict).copy()

        return report_df
    except:
        return pd.DataFrame()

report_df = load_data()
