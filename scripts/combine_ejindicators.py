## Combine relevant data from EJScreen and SVI with DAC designations to create 'dacejssvi' data frame
## EJScreen data includes both raw average values and U.S. percentile rankings for variables, both formats are included in this file but percentiles are used for easier comparison in 'ejanalyze' script.

#Import pandas and os to set directory for new file
import pandas as pd
import os

#%% EJScreen


#Import CSV for EJScreen
ejsraw = pd.read_csv("EJScreen_2024_Tract_with_AS_CNMI_GU_VI.csv")

#Subset for New York State and New York City Counties
ejsnyc = ejsraw.query("STATE_NAME == 'NEW YORK'")

ejsnyc = ejsnyc[ejsnyc['CNTY_NAME'].isin(['New York County', 'Kings County', 'Bronx County', 'Queens County','Richmond County'])]

#Identify key environmental indicator columns for merge

#All unstandardized columns
#ejskeep = ['ID', 'ACSTOTPOP', 'ACSTOTHH', 
           #'PM25', 'OZONE', 'DSLPM', 
           #'RSEI_AIR', 'PRE1960PCT',
           #'PNPL', 'PRMP', 'PTSDF',
           #'PWDIS', 'NO2', 'DWATER',
           #'PTRAF']

#All percentile columns
ejskeep = ['ID', 'ACSTOTPOP', 'ACSTOTHH', 
           'P_PM25', 'P_OZONE', 'P_DSLPM', 
           'P_RSEI_AIR', 'P_LDPNT',
           'P_PNPL', 'P_PRMP', 'P_PTSDF',
           'P_PWDIS', 'P_NO2', 'P_DWATER',
           'P_PTRAF']

ejsfin = ejsnyc[ejskeep]


#%% SVI


#Import CSV for SVI
sviraw = pd.read_csv("SVI_2022_US.csv")

#Subset for New York State and New York City Counties
svinyc = sviraw.query("STATE == 'New York'")

svinyc = svinyc[svinyc['COUNTY'].isin(['New York County', 'Kings County', 'Bronx County', 'Queens County','Richmond County'])]

#Identify key social vulnerability index columns for merge
svikeep = ['FIPS', 'RPL_THEME1', 'RPL_THEME2',
           'RPL_THEME3', 'RPL_THEME4', 'RPL_THEMES']

svifin = svinyc[svikeep]

#Adjust index colums so they are consistent with EJScreen percentiles (0 to 100 format)
sviscalecol = ['RPL_THEME1', 'RPL_THEME2', 'RPL_THEME3', 'RPL_THEME4', 'RPL_THEMES']

svifin[sviscalecol] = svifin[sviscalecol] * 100


#%% NYS DAC


#Import CSV for DAC Designations
dacraw = pd.read_csv("Final_Disadvantaged_Communities__DAC__2023_20250502.csv")

#Subset for New York City
dacnyc = dacraw.query("NYC_Region == 'NYC'")

#Identify DAC designation
dackeep = ['GEOID', 'DAC_Designation'] 

dacfin = dacnyc[dackeep]


#%% NHGIS 2010 to 2020 Cross Walk Merge


#Import cross walk file for NYS for DAC_Designation adjustment and limit to mergepoints
tractcross = pd.read_csv("nhgis_tr2010_tr2020_36.csv")

tractcross = tractcross[['tr2010ge', 'tr2020ge']]

#Merge cross walk with DAC designations and check
mergeddac = dacfin.merge(tractcross, left_on='GEOID', right_on='tr2010ge', how='left', indicator=True)

print("\nMerged 'mergeddac' File Check:", mergeddac['_merge'].value_counts()) #All 'both'

#Ensure there's one record for designation for each tract
mergeddacfin = mergeddac.groupby('tr2020ge', as_index=False).agg({
    'DAC_Designation': lambda x: 'Designated as DAC' if 'Designated as DAC' in x.values else 'Not Designated as DAC'
})

print(mergeddacfin['DAC_Designation'].value_counts())

#Approximately 44% of tracts in NYC are designated as DAC with 2010 designations, value counts yields similar ratio


#%% EJScreen + DAC Merge


#Merge EJScreen with DAC designations and check
dacejs = ejsfin.merge(mergeddacfin, left_on='ID', right_on='tr2020ge', how='left', indicator=True)

print("\nMerged 'dacejs' File Check:", dacejs['_merge'].value_counts()) #All 'both'

dacejs = dacejs.drop(columns=['tr2020ge', '_merge'])


#%% EJScreen + DAC + SVI Merge


#Merge DAC & EJScreen with SVI and check
dacejssvi = dacejs.merge(svifin, left_on='ID', right_on='FIPS', how='left', indicator=True)

print("\nMerged 'dacejssvi' File Check:", dacejssvi['_merge'].value_counts()) #3 tracts only included in EJScreen/DAC Designation ('left_only'), dropped in next cell (0 pop or HH)

dacejssvi = dacejssvi.drop(columns=['FIPS', '_merge'])


#%% Final Data Frame Clean-up


#Rename columns in final data frame so they are more readable/user-friendly

#With unstandardized EJScreen columns
#newcol = {'ID':'Tract', 'OZONE':'Ozone', 'DSLPM':'Diesel_PM', 'RSEI_AIR':'Toxic_Air_Releases',
          #'PRE1960PCT':'Percent_HHLeadPaint', 'PNPL':'Superfund_Prox',
          #'PRMP':'RMP_Prox', 'PTSDF':'HazWaste_Prox', 'PWDIS':'WW_Discharge',
          #'DWATER':'DW_Noncomp', 'RPL_THEME1':'Socioecon_Percentile', 'RPL_THEME2':'HHVuln_Percentile',
          #'RPL_THEME3':'Minority_Percentile', 'RPL_THEME4':'HouseType_Percentile', 'RPL_THEMES':'Vulnerability_Percentile',
          #'ACSTOTPOP':'Population', 'ACSTOTHH':'Households', 'DAC_Designation':'Is_DAC',
          #'PTRAF':'Traffic_Prox'}

#With percentile EJScreen columns
newcol = {'ID':'Tract', 'P_OZONE':'Ozone', 'P_DSLPM':'Diesel_PM', 'P_RSEI_AIR':'Toxic_Air_Releases',
          'P_LDPNT':'Percent_HHLeadPaint', 'P_PNPL':'Superfund_Prox',
          'P_PRMP':'RMP_Prox', 'P_PTSDF':'HazWaste_Prox', 'P_PWDIS':'WW_Discharge',
          'P_DWATER':'DW_Noncomp', 'RPL_THEME1':'Socioecon_Percentile', 'RPL_THEME2':'HHVuln_Percentile',
          'RPL_THEME3':'Minority_Percentile', 'RPL_THEME4':'HouseType_Percentile', 'RPL_THEMES':'Vulnerability_Percentile',
          'ACSTOTPOP':'Population', 'ACSTOTHH':'Households', 'DAC_Designation':'Is_DAC',
          'P_PTRAF':'Traffic_Prox', 'P_PM25':'PM25', 'P_NO2':'NO2'}

dacejssvi.rename(columns=newcol, inplace=True)

#Change DAC Designation to indicator variable (1 = DAC, 0 = Not DAC)
newdacobs = {'Designated as DAC':1, 'Not Designated as DAC':0}

dacejssvi['Is_DAC'] = dacejssvi['Is_DAC'].replace(newdacobs)

#Drop tracts with no population (parks, bodies of water, etc.)
dacejssvi = dacejssvi[dacejssvi['Population'] != 0]

#Drop tracts with no households (correctional facilities, industrial areas, etc.)
dacejssvi = dacejssvi[dacejssvi['Households'] != 0]


#%%Save CSV to New 'output_data' Folder in 'nycenvanalysis' Directory

#Move to greater project directory
nycenvdir = os.path.abspath(os.path.join(os.getcwd(), ".."))

#Define output folder 
outputdata_folder = os.path.join(nycenvdir, "output_data")

#Create output folder
os.makedirs(outputdata_folder, exist_ok=True)

#Create path for combined csv
csv_name = "dacejssvi.csv"
output_path = os.path.join(outputdata_folder, csv_name)

#Export CSV
dacejssvi.to_csv(output_path, index=False)



