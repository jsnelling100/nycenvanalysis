## Use combined dataframe to understand most vulnerable DACs and indicators according to cumulative burden scoring, clustering, and correlation heatmap

#Import packages
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import os

#Set package parameters
scaler = StandardScaler()
plt.rcParams['figure.dpi'] = 300

#Read in combined DAC file and set 'Tract' as index
ejdf = pd.read_csv("dacejssvi.csv", index_col='Tract')


#%% Cumulative Burden Scoring


#Create a new data frame for burden scoring
cbsdf = pd.DataFrame()

cbsdf = ejdf[['Population', 'Households', 'Is_DAC', 'Vulnerability_Percentile']]

#Establish categories for different environmental indicators in 'ejdf' to make overall vulnerability comparison simpler
cbsdf['Pollution_Score'] = ejdf[['PM25', 'Ozone', 'Diesel_PM', 'Toxic_Air_Releases', 'NO2','WW_Discharge']].mean(axis=1)

cbsdf['Hazardprox_Score'] = ejdf[['Percent_HHLeadPaint', 'Superfund_Prox', 'RMP_Prox', 'HazWaste_Prox', 'DW_Noncomp']].mean(axis=1)

#Combine indicators with SVI vulnerability percentile
cbsdf['Cumulative_Burden_Score'] = cbsdf[['Pollution_Score', 'Hazardprox_Score', 'Vulnerability_Percentile']].mean(axis=1)

#Show top 10 burden scores and check whether they are DACs
burdentop10 = cbsdf.sort_values(by='Cumulative_Burden_Score', ascending=False).head(10)

print(burdentop10[['Cumulative_Burden_Score', 'Is_DAC']]) #All 10 considered a DAC


#Add in population to weight burden score and see where most people are vulnerable/affected by environmental hazards
cbsdf['Weighted_Burden'] = cbsdf['Cumulative_Burden_Score']*cbsdf['Population']

#Normalize burden score so weight column is more legible
cbsdf['Weighted_Burden_Norm'] = cbsdf['Weighted_Burden']/cbsdf['Weighted_Burden'].max()


#%% Clusters


#Identify features for clusters
clusterftrs = ['Population', 'Households', #Non-percentile demographic statistics
               'PM25', 'Ozone', 'Diesel_PM', 'NO2', 'Toxic_Air_Releases', #Air-related indicators
               'Superfund_Prox', 'RMP_Prox', 'HazWaste_Prox', 'Percent_HHLeadPaint', 'Traffic_Prox', #Environmental hazard proximity indicators
               'DW_Noncomp', 'WW_Discharge', #Water-related indicators
               'Socioecon_Percentile', 'HHVuln_Percentile', 'Minority_Percentile', 'HouseType_Percentile'] #Social vulnerability indicators

#Create a new data frame for clustering
clusterdf = ejdf[clusterftrs]

#Check and drop all missing values
print(clusterdf[clusterftrs][clusterdf[clusterftrs].isnull().any(axis=1)]) #Only 5 tracts, 4 for NaN in DW Compliance, 1 NaN for NO2

clusterdf = clusterdf.dropna()

#Use scikit learn scaler to standardize features
X = clusterdf[clusterftrs]

X_scaled = scaler.fit_transform(X)

#Perform clustering using simple K-means algorithm 
kmeans = KMeans(n_clusters=4, random_state=100)

clusterdf['cluster'] = kmeans.fit_predict(X_scaled)

#Overall summary for clusters
cluster_summary = clusterdf.groupby('cluster')[clusterftrs].mean().round(1)

print(cluster_summary)


#Add in DAC designation to see how much of a cluster is considered a DAC
clusterdf['Is_DAC'] = ejdf['Is_DAC']

#Aggregate count and sum of DAC tracts
dacsum = clusterdf.groupby('cluster').agg(Total_Tracts=('Is_DAC', 'count'), Number_DACs=('Is_DAC', 'sum'))

#Add percentage DAC column to cluster summary
cluster_summary['Percent_DAC'] = 100 * dacsum['Number_DACs'] / dacsum['Total_Tracts']


#%% Correlation Heat Map


#Identify indicators for heatmap
heatind = ['PM25', 'Ozone', 'Diesel_PM', 'NO2', 'Toxic_Air_Releases', #Air-related indicators
           'Superfund_Prox', 'RMP_Prox', 'HazWaste_Prox', 'Percent_HHLeadPaint', 'Traffic_Prox', #Environmental hazard proximity indicators
           'DW_Noncomp', 'WW_Discharge', #Water-related indicators
           'Socioecon_Percentile', 'HHVuln_Percentile', 'Minority_Percentile', 'HouseType_Percentile'] #Social vulnerability indicators

#Create better labels for indicators
betterlabels = {'PM25':'PM2.5', 'Ozone':'Ozone', 'NO2':'NO2', 'Percent_HHLeadPaint':'Lead Paint Percentage',
                'Diesel_PM':'Diesel PM', 'Toxic_Air_Releases':'Toxic Releases to Air', 
                'Superfund_Prox':'Superfund Proximity', 'RMP_Prox':'RMP Facility Proximity',
                'HazWaste_Prox':'Haz. Waste Proximity', 'Traffic_Prox':'Traffic Proximity',
                'DW_Noncomp':'Drinking Water Noncomp.', 'WW_Discharge':'Wastewater Discharge',
                'Socioecon_Percentile':'Socioeconomic Index', 'HHVuln_Percentile':'Household Vuln. Index',
                'Minority_Percentile':'Racial Minority Index', 'HouseType_Percentile':'Housing/Transport Index'}

maplabels = [betterlabels.get(col, col) for col in heatind]

#Create the heatmap
fig, ax = plt.subplots(figsize=(12, 8))

sns.heatmap(ejdf[heatind].corr(), annot=True, fmt=".1f", 
            vmin=-1, vmax=1, cmap='coolwarm', 
            linewidths=0.5, ax=ax, cbar_kws={'label': 'Correlation'})

ax.set_title("Correlation Matrix of Environmental/Vulnerability Indicators in NYC Census Tracts", fontsize=12)
ax.set_xticklabels(maplabels, rotation=45, ha='right')
ax.set_yticklabels(maplabels, rotation=0)
fig.tight_layout()


#%% Create a Condensed Data Frame for Use in Mapping (ejvisualize.py)


#Add in relevant cumulative burden score columns
mapdf = cbsdf[['Is_DAC', 'Pollution_Score', 'Hazardprox_Score', 
              'Vulnerability_Percentile','Cumulative_Burden_Score', 
              'Weighted_Burden_Norm']]

#Add in cluster column
mapdf['Cluster'] = clusterdf['cluster']


#%% Save Data Frames and Figure in Output Data and Output Figures Folders


#Move to greater project directory
nycenvdir = os.path.abspath(os.path.join(os.getcwd(), ".."))

#Define and check that output data folder exists/functions
outputdata_folder = os.path.join(nycenvdir, "output_data")
os.makedirs(outputdata_folder, exist_ok=True)

#Define and check that output figure folder exists/functions
fig_folder = os.path.join(nycenvdir, "output_figures")
os.makedirs(fig_folder, exist_ok=True)

#Define file paths and save cbsdf, clusterdf, and cluster summary as csv's
cbsdf.to_csv(os.path.join(outputdata_folder, "cumburdej.csv"), index=True)

clusterdf.to_csv(os.path.join(outputdata_folder, "clusteredej.csv"), index=True)

cluster_summary.to_csv(os.path.join(outputdata_folder, "clustersumm.csv"), index=True)

mapdf.to_csv(os.path.join(outputdata_folder, "mapej.csv"), index=True)

#Define file path and save heat map as png
fig_path = os.path.join(fig_folder, "ejcorrheatmap.png")
fig.savefig(fig_path)
