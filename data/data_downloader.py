# -*- coding: utf-8 -*-
"""Data Downloader.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WahTWXaCqdL2-4OuScIkRuZK-oAaAtzT
"""

from google.colab import drive
try:
    drive.mount('/content/drive')
except Exception as e:
    print(e)
    pass

import os
dir = 'drive/Shareddrives/CS571 Project/Dataset Files'

if dir in os.getcwd():
    print(f"already in {dir}")
else:
    print(f"changing directory to {dir}")
    os.chdir(dir)

print("\n Files:")
os.listdir()

if "/content/drive/Shareddrives/" in os.getcwd():
    print("ok")

owid_link = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
oxford_link = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest_combined.csv'

# for column names, and for columns E3, E4, H4, H5
oxford_nice_link = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'

"""# Download the data"""

import pandas as pd

owid = pd.read_csv(owid_link)
oxford = pd.read_csv(oxford_link)
oxford_nice = pd.read_csv(oxford_nice_link)
print(f'owid shape: {owid.shape}')
print(f'oxford shape: {oxford.shape}')
print(f'oxford_nice shape: {oxford_nice.shape}')

"""# Examine column names and types"""

owid.dtypes

oxford.dtypes

oxford.query('CountryCode=="USA"')['RegionName'].unique()

### this is the unique key in oxford and oxford_combined
oxford[['CountryCode', 'RegionName', 'Date']].drop_duplicates().shape

### this is the unique key in Our World in Data (owid)
owid[['location', 'date']].drop_duplicates().shape

"""# lowercase all column names"""

owid.columns = [x.lower() for x in owid.columns]
oxford.columns = [x.lower() for x in oxford.columns]
oxford_nice.columns = [x.lower() for x in oxford_nice.columns]

"""# Get dates into same format"""

[min(owid['date']), max(owid['date'])]

[min(oxford['date']), max(oxford['date'])]

def parse_date(r):
    datestr = str(r['date'])
    return datestr[:4] + '-' + datestr[4:6] + '-' + datestr[-2:]

oxford['date'] = oxford.apply(parse_date, axis=1)
oxford_nice['date'] = oxford_nice.apply(parse_date, axis=1)

# now convert them all to pandas datatimes for alignment
owid['date'] = pd.to_datetime(owid['date'])
oxford['date'] = pd.to_datetime(oxford['date'])
oxford_nice['date'] = pd.to_datetime(oxford_nice['date'])

"""# Filter out dates to be in common window"""

# get the intersection window: LARGEST min, and SMALLEST max

min_date = max(owid['date'].min(), 
               oxford['date'].min())
max_date = min(owid['date'].max(), 
               oxford['date'].max())


# EDIT 4/12/2021: set max_date = 2 weeks ago
# Reason: there is sometimes a bit of a lag between the date and when data are finally updated. 
# This way we can reduce NAs at the end of the dataset
max_date = max_date - pd.to_timedelta(14, unit='d')

print(f'intersection window of dates: {min_date} to {max_date}')

max_date - pd.to_timedelta(7, unit='d')

print(f'OWID: {owid.shape[0]} rows')
print(f'Oxford: {oxford.shape[0]} rows')

rows_dropped_owid = owid.query('(date < @min_date) or (date > @max_date)').shape[0]
rows_dropped_oxford = oxford.query('(date < @min_date) or (date > @max_date)').shape[0]
rows_dropped_oxford_nice = oxford_nice.query('(date < @min_date) or (date > @max_date)').shape[0]

print('Dropping rows to align date windows----------------')
print(f'OWID: {rows_dropped_owid} rows')
print(f'Oxford: {rows_dropped_oxford} rows')
print(f'Oxford_nice: {rows_dropped_oxford_nice} rows')

owid = owid.query('(date >= @min_date) and (date <= @max_date)')
oxford = oxford.query('(date >= @min_date) and (date <= @max_date)')
oxford_nice = oxford_nice.query('(date >= @min_date) and (date <= @max_date)')

print('Done.')
print(f'OWID: {owid.shape[0]} rows')
print(f'Oxford: {oxford.shape[0]} rows')
print(f'Oxford_nice: {oxford_nice.shape[0]} rows')

"""# Filter out countries that don't exist in both datasets"""

owid_countries = owid['location'].unique()
oxford_countries = oxford['countryname'].unique()

# countries in oxford, but not in OWID
[x for x in oxford_countries if x not in owid_countries]

# countries in OWID, but not in oxford
[x for x in owid_countries if x not in oxford_countries]

intersect_countries = [x for x in owid_countries if x in oxford_countries]
len(intersect_countries)

rows_dropped_owid = owid[~owid['location'].isin(intersect_countries)].shape[0]
rows_dropped_oxford = oxford[~oxford['countryname'].isin(intersect_countries)].shape[0]
rows_dropped_oxford_nice = oxford_nice[~oxford_nice['countryname'].isin(intersect_countries)].shape[0]

print("Dropping rows for countries that don't exist in both datasets----------------")
print(f'OWID: {rows_dropped_owid} rows')
print(f'Oxford: {rows_dropped_oxford} rows')
print(f'Oxford_nice: {rows_dropped_oxford_nice} rows')

owid = owid[owid['location'].isin(intersect_countries)]
oxford = oxford[oxford['countryname'].isin(intersect_countries)]
oxford_nice = oxford_nice[oxford_nice['countryname'].isin(intersect_countries)]

print('Done.')
print(f'OWID: {owid.shape[0]} rows')
print(f'Oxford: {oxford.shape[0]} rows')
print(f'Oxford_nice: {oxford_nice.shape[0]} rows')

"""# Filter out regional data in Oxford dataset"""

rows_dropped_owid = 0
rows_dropped_oxford = oxford[~oxford['regionname'].isna()].shape[0]
rows_dropped_oxford_nice = oxford_nice[~oxford_nice['regionname'].isna()].shape[0]

print('Dropping rows to remove regional data----------------')
print(f'OWID: {rows_dropped_owid} rows')
print(f'Oxford: {rows_dropped_oxford} rows')
print(f'Oxford_nice: {rows_dropped_oxford_nice} rows')

oxford = oxford[oxford['regionname'].isna()]
oxford_nice = oxford_nice[oxford_nice['regionname'].isna()]

print('Done.')
print(f'OWID: {owid.shape[0]} rows')
print(f'Oxford: {oxford.shape[0]} rows')
print(f'Oxford_nice: {oxford_nice.shape[0]} rows')

"""# Why are row counts so far apart?"""

oxford['countryname'].value_counts()

# a-ha. It's because the OWID data doesn't include filler rows for every country even when there were no data.

owid['location'].value_counts()

oxford.query('countryname == "Macao"').head()

"""# Combine the OWID and oxford datasets"""

df = pd.merge(oxford, owid, how="left", left_on=['countryname', 'date'], right_on=['location', 'date'])
df.shape

df = pd.merge(df,
              oxford_nice[['countryname', 'date', 'e3_fiscal measures', 'e4_international support', 'h4_emergency investment in healthcare', 'h5_investment in vaccines']],
              on=['countryname', 'date'])
df.shape

df[df['e3_fiscal measures']>0].head()

"""# Edit 4/11/2021: Update OWID variables' "filler" rows

More info: The Oxford dataset has rows for every country for the entire date range of the dataset, even if they don't have data for the country on the given date. The OWID data only has a row for a country if it has data for it. So when the datasets are joined, the columns that are constant in OWID (like median_age, extreme_poverty, etc.) are filled with missing values. Below we will populate those missing values with the non-missing values from other rows (since the values are constant anyway).
"""

# for the new "filler rows" in OWID, for the columns that don't change (e.g., median_age), update all NAs to be equal to the country's max/min/first value
filler_cols = ["continent","population","population_density","median_age","aged_65_older","aged_70_older","gdp_per_capita", 
               "extreme_poverty","cardiovasc_death_rate","diabetes_prevalence","female_smokers","male_smokers", 
               "handwashing_facilities","hospital_beds_per_thousand","life_expectancy","human_development_index"]

# replace missing values with "" before aggregating; otherwise string columns like "continent" will 
# cause an error when comparing strings with NaN, saying you can't compare a float and a string
str_cols = [x for x in df.columns if df[x].dtype == "object"]
tmp = df.fillna({x: "" for x in str_cols})

filler_values = tmp.groupby('countryname').agg({x: 'max' for x in filler_cols}).reset_index()
filler_values

# merge in the filler data!
sort_order = df.columns
data_cols = [x for x in df.columns if x not in filler_cols]
df = df[data_cols].merge(filler_values, how="left", on="countryname")[sort_order]
df

"""## Confirm cases and deaths match on both datasets (approximately)

Result: there are discrepancies in 5% of the dataset, but they don't seem too major.
"""

df[['confirmedcases', 'new_cases', 'total_cases', 'confirmeddeaths', 'new_deaths', 'total_deaths']]

x = df[['confirmedcases', 'total_cases', 'confirmeddeaths', 'total_deaths']].copy()
x = x.fillna(0)
x.query('confirmedcases != total_cases')

x.query('confirmeddeaths != total_deaths')

x['discrepancy_cases'] = abs(x['confirmedcases'] - x['total_cases'])
x['discrepancy_deaths'] = abs(x['confirmeddeaths'] - x['total_deaths'])

x[x['discrepancy_cases'] != 0]

# this is 5% of our total dataset. Not too bad.
x.query('(confirmeddeaths != total_deaths) or (confirmedcases != total_cases)').shape[0]

"""# re-code 4 oxford variables

These variables don't have a flag, so are applied to the whole country. Let's apply a "G" to the end of the values to match the formatting of the other "combined" variables
"""

cols = ['e2_combined',
        'h2_combined',
        'h3_combined',
        'c8_combined',]

# EDIT 4/11/2021
# create a numeric version of these columns for consistency
for col in cols:
    df[col + "_numeric"] = df[col]

df[cols].tail(20)

for col in cols:
    print(df[col].value_counts())

df[cols].dtypes

import numpy as np

def add_g(x):
    if np.isnan(x):
        return x
    if x == 0:
        return "0"
    else:
        return str(int(x)) + "G"

df[cols].applymap(add_g).tail(20)

df[cols] = df[cols].applymap(add_g)

for col in cols:
    print(df[col].value_counts())

df[cols].dtypes

"""# Edit 4/4/2021: Re-code from "G"/"T" to "National"/"Local" so alphabetic ordering matches numeric ordering

e.g., 2.5 is "3-Local" (was "3T") and 3.0 is "3-National" (was "3G")
L = local
N = national
"""

[x for x in df.columns if x[-9:]=="_combined"]

# look at the "combined" columns to see if there are any codes other than "G" or "T"
# e1_combined and h7_combined are weird, so we'll treat them differentl
for x in [x for x in df.columns if x[-9:]=="_combined"]:
    #nrow = df[df[x]=="1A"].shape[0]
    #if nrow > 0:
        #print(f"{x}: {nrow} rows")
    print(df[x].value_counts())

df['e1_combined'].value_counts()

cols = [x for x in df.columns if x[-9:]=="_combined" and x not in ['e1_combined', 'h7_combined']]

cols

df[cols].dtypes

df["h8_combined"].value_counts()

def recode(x):
    try:
        if pd.isna(x) or x in ["0", "", "(missing)"]:
            return x
        if type(x) in [int, float]:  # h8_combined has 0.0
            return str(round(x))
        if x[-1:] == "G":
            return x[:-1] + "-National"
        elif x[-1:] == "T":
            return x[:-1] + "-Local"
        else:
            print(x)
            raise RuntimeError("oops")
    except:
        print(x)
        raise

# check to make sure it works with broke
df[cols] = df[cols].applymap(recode)

for col in cols:
    #nrow = df[df[x]=="1A"].shape[0]
    #if nrow > 0:
        #print(f"{x}: {nrow} rows")
    print(df[col].value_counts())

# make sure we see entries for "#-National" and "#-Local"
df[cols].tail(100)

# update h7_combined to set "1I" = "1G"; we will recode in a bit
df["h7_combined"].value_counts()

df.loc[df["h7_combined"]=="1I", "h7_combined"] = "1G"
df["h7_combined"].value_counts()

# update e1_combined to set "1A" = "1G", "2A" = "2G", "1F" = "1T", "2F" = "2T"; we will recode in a bit
df["e1_combined"].value_counts()

df.loc[df["e1_combined"].str.slice(1)=="F", "e1_combined"] = \
    df.loc[df["e1_combined"].str.slice(1)=="F", "e1_combined"].str.slice(0, 1) + "T"

df.loc[df["e1_combined"].str.slice(1)=="A", "e1_combined"] = \
    df.loc[df["e1_combined"].str.slice(1)=="A", "e1_combined"].str.slice(0, 1) + "G"

df["e1_combined"].value_counts()

# finally, recode e1_combined and h7_combined
cols = ["e1_combined", "h7_combined"]
df[cols] = df[cols].applymap(recode)

for col in cols:
    print(df[col].value_counts())

"""# Edit 4/4/2021: Add new_vaccinations per hundred"""

df['new_vaccinations_per_hundred'] = df['new_vaccinations'] / df['population'] * 100

"""# drop unnecessary columns, and rename others to nicer names"""

cols_to_drop = ['countrycode',  # this and below are from oxford
'regionname',
'regioncode',
'jurisdiction',
'confirmedcases',
'confirmeddeaths',
'stringencyindexfordisplay',
'stringencylegacyindex',
'stringencylegacyindexfordisplay',
'governmentresponseindexfordisplay',
'containmenthealthindexfordisplay',
'economicsupportindexfordisplay',
'location',  # this and the next one is from owid
'iso_code',
'stringency_index',

]

df.drop(columns=cols_to_drop, inplace=True)

rename_cols = {
'c1_combined': 'c1_school_closing',
'c1_combined_numeric': 'c1_school_closing_numeric',

'c2_combined': 'c2_workplace_closing',
'c2_combined_numeric': 'c2_workplace_closing_numeric',

'c3_combined': 'c3_cancel_public_events',
'c3_combined_numeric': 'c3_cancel_public_events_numeric',

'c4_combined': 'c4_restrictions_on_gatherings',
'c4_combined_numeric': 'c4_restrictions_on_gatherings_numeric',

'c5_combined': 'c5_close_public_transport',
'c5_combined_numeric': 'c5_close_public_transport_numeric',

'c6_combined': 'c6_stay_at_home_requirements',
'c6_combined_numeric': 'c6_stay_at_home_requirements_numeric',

'c7_combined': 'c7_restrictions_on_internal_movement',
'c7_combined_numeric': 'c7_restrictions_on_internal_movement_numeric',

'c8_combined': 'c8_international_travel_controls',
'c8_combined_numeric': 'c8_international_travel_controls_numeric',

'e1_combined': 'e1_income_support',
'e1_combined_numeric': 'e1_income_support_numeric',

'e2_combined': 'e2_debt_contract_relief',
'e2_combined_numeric': 'e2_debt_contract_relief_numeric',

'h1_combined': 'h1_public_information_campaigns',
'h1_combined_numeric': 'h1_public_information_campaigns_numeric',

'h2_combined': 'h2_testing_policy',
'h2_combined_numeric': 'h2_testing_policy_numeric',

'h3_combined': 'h3_contact_tracing',
'h3_combined_numeric': 'h3_contact_tracing_numeric',

'h6_combined': 'h6_facial_coverings',
'h6_combined_numeric': 'h6_facial_coverings_numeric',

'h7_combined': 'h7_vaccination_policy',
'h7_combined_numeric': 'h7_vaccination_policy_numeric',

'e3_fiscal measures': 'e3_fiscal_measures',
'e4_international support': 'e4_international_support',
'h4_emergency investment in healthcare': 'h4_emergency_investment_in_healthcare',
'h5_investment in vaccines': 'h5_investment_in_vaccines',

'stringencyindex': 'stringency_index',
'governmentresponseindex': 'government_response_index',
'containmenthealthindex': 'containment_health_index',
'economicsupportindex': 'economic_support_index'
}

df.rename(columns=rename_cols, inplace=True)

df.columns

"""# Edit 4/21/2021: Add ISO Codes (alpha-3)

This is for joining to mapbox vector data. ISO codes were taken from https://gist.github.com/tadast/8827699, and I merged them with our country names. There were some differences in country names, and a couple missing ISO codes in the github file (e.g., for Kosovo) which I filled in using google.
"""

df.shape

iso_codes = pd.read_csv("countries_iso.csv")
iso_codes.head()

# check that shape matches expectation
df.merge(iso_codes, how="inner", left_on="countryname", right_on="country").drop(columns=["country"]).shape

df = df.merge(iso_codes, how="inner", left_on="countryname", right_on="country").drop(columns=["country"])

df.head()

"""# Re-encode dates as string"""

df['date'] = df.apply(lambda x: x['date'].strftime('%Y-%m-%d'), axis=1)

"""# Export dataset to CSV"""

import csv
from datetime import datetime

the_date = datetime.now().strftime('%Y%m%d-%H%M%S')
df.to_csv(f'covid_oxford+owid_{the_date}.csv', index=False)

"""# Summarize dataset"""

def summarize_variables(df, return_df=True, output_summary=True, filename=None):
    """Univariate summary of all variables in a dataframe

    Args:
        df (pandas DataFrame): data to summarize
        return_df (bool, optional): Whether to return the summary as a DataFrame. Defaults to True.
        output_summary (bool, optional): Whether to export the summary to a file. Defaults to True.
        filename (str, optional): Filename to export. Defaults to None.
    
    Returns:
        pandas DataFrame: Summarized data
    """
    var_summary = df.describe(include="all").T
    var_summary["type"] = ['str' if str(x) == "object" else "date" if "date" in str(x) else str(x) for x in df.dtypes]
    var_summary["missing_pct"] = 1 - var_summary["count"] / len(df)
    var_summary["col_number"] = np.arange(1, df.shape[1] + 1)

    # move these columns to the front
    front_cols = ["col_number", "type", "count", "missing_pct", "unique"]
    var_summary = var_summary[[*front_cols, *[x for x in var_summary.columns if x not in front_cols]]]

    if output_summary:
        the_time = datetime.now().strftime("%Y%m%d")

        if filename is None:
            filename = os.path.join(os.getcwd(), "var_summary_" + the_time + ".csv")
        
        var_summary.to_csv(filename, index=True, index_label="variable", quoting=csv.QUOTE_ALL)

    if return_df:
        return var_summary

summarize_variables(df)

"""# Flush out data to google drive"""

# ensures files actually get written to shared drive
drive.flush_and_unmount()