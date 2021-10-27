# Libraries
# Data
import pandas as pd # Dataframe manipulations
import math

# Dash App
# from jupyter_dash import JupyterDash # for running in a Jupyter Notebook
import dash_core_components as dcc
import dash_table

# Data Visualization
import plotly.express as px
from data_processing import *
from styling import *

# ----------------------------------------------------------------------------
# CUSTOM FUNCTIONS FOR DASH UI COMPONENTS
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Missing Data Section
# ----------------------------------------------------------------------------
missing = dcc.Markdown('''
**Missing values:**
Flag: Pull complete data for all samples with missing values for any of the variables queried in analyses below including variables relating to whether certain tubes were collected and counts of tubes, timing values, hemolysis levels, and protocol deviations.

Purpose: Reach back out to MCC to get missing data filled in if possible.
    '''
    ,style={"white-space": "pre"}),

# ----------------------------------------------------------------------------
# Sample counts by site
# ----------------------------------------------------------------------------

site = dcc.Markdown('''
**Sample Counts by Site**
* Barplot showing counts by site (parallel bars) and by timepoint (groups of bars) – DONE
* Barplot showing percent of samples by site/timepoint with PaxGene obtained
* Barplot showing percent of samples by site/timepoint with BuffyCoat obtained
* Barplot showing percent of samples by site/timepoint with at least one aliquot tube obtained
* Barplot showing percent of samples by site/timepoint with at least five aliquot tubes obtained
* Barplot showing distribution of counts of aliquot tubes, faceted by site/timepoint (e.g., num sites rows by num timepoints columns, similar to Aliquots Collected plot from current version, but I think I'd prefer sites on separate panels)

Flags: Pull complete data for all samples with no PaxGene OR no BuffyCoat OR no aliquot tubes

Purpose: Track number of samples by site, getting a full picture of the types of tubes collected, percent of samples with adequate data collected for analysis
    '''
    ,style={"white-space": "pre"}),

# ----------------------------------------------------------------------------
# Timing
# ----------------------------------------------------------------------------

timing =  dcc.Markdown('''
**Timing Data**
* Barplots of counts of samples by time to centrifuge, faceted by site (I think it is a little too hard to see easily with all sites on the same plot)
* Barplots of counts of samples by time to freezer, faceted by site

* Table with percent of samples by site/timepoint where time to centrifuge <= 30mins
* Table with percent of samples by site/timepoint where time to freezer <= 60mins

Flags: Pull complete data for all samples with time to centrifuge > 30mins OR time to freezer > 60 mins OR time to freezer < time to centrifuge

Purpose: Check that protocols are being followed to ensure high quality blood samples
    '''
    ,style={"white-space": "pre"}),

# ----------------------------------------------------------------------------
# Hemolysis
# ----------------------------------------------------------------------------
hemolysis = dcc.Markdown('''
**Hemolysis:**

* Barplots of counts of samples by hemolysis level, faceted by site
* Table with percent of samples by site/timepoint with hemolysis < 1

Flags: Pull complete data for all samples with hemolysis >= 1

Purpose: Get a feeling for quality of blood samples being collected
    '''
    ,style={"white-space": "pre"}),

# ----------------------------------------------------------------------------
# Protcol Deviations
# ----------------------------------------------------------------------------

deviations = dcc.Markdown('''
**Protocol Deviations**
Table of counts of protocol deviations by type, by site/timepoint

Flags: Pull complete data for all samples with any protocol deviation

Purpose: Track protocol issues to allow early intervention if recurring problems are occurring
    '''
    ,style={"white-space": "pre"}),
