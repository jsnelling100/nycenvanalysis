## Use measures calculated with 'ejanalyze.py' to provide insight into different environmental and vulnerability indicators

#Import packages
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import os

#Set package parameters
plt.rcParams['figure.dpi'] = 300

#Import 'mapej' csv
mapdf = pd.read_csv('mapej.csv')

#Import TIGER zip file of New York Census Tracts (must be downloaded from link included in README.md)
tiger = gpd.read_file("tl_2024_36_tract.zip")


#%% Merge EJ File with Geometry for Maps


#Ensure typing is consistent for merge
mapdf['Tract'] = mapdf['Tract'].astype(str)
tiger['GEOID'] = tiger['GEOID'].astype(str)

#Merge mapej with TIGER geometry and check
merged = tiger.merge(mapdf, left_on="GEOID", right_on="Tract", how="left", indicator=True)

print("\nMerged 'merged' File Check:", merged['_merge'].value_counts()) #3,180 non-NYC tracts as 'left_only'

#Drop non-NYC tracts by identifying missing values in 'Tract' coluumn
merged = merged.dropna(subset=['Tract'])

#Drop some unnecessary columns
trimmed = merged.drop(columns=['GEOID', 'STATEFP', 'COUNTYFP', '_merge']).reset_index(drop=True)

#Set tract as index
trimmed = trimmed.set_index('Tract')


#%% Map 1: DAC Designations


#Create map to show which tracts are labeled as DAC's
fig1, ax1 = plt.subplots(figsize=(12, 10))
fig1.tight_layout()

trimmed.plot(ax=ax1, color='white', edgecolor='black', linewidth=0.3)
trimmed[trimmed['Is_DAC'] == 1].plot(ax=ax1, color='green', edgecolor='black', linewidth=0.3)

dac_leg = mpatches.Patch(color='green', label='DAC')
ax1.legend(handles=[dac_leg], loc='lower right', frameon=False, fontsize=16)

#Add in text annotation
ax1.text(0.05, 0.80,
         "44% of New York City's census tracts\nare designated as DACs. Most are\nin the Bronx and Brooklyn.",
         transform=ax1.transAxes,
         fontsize=14,
         verticalalignment='top',
         horizontalalignment='left',
         bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

ax1.set_axis_off()
ax1.set_title("Designated Disadvantaged Communities (DAC)", fontsize=20)


#%% Map 2: Cumulative Burden Score Choropleth


#Create map to show gradient of burden and vulnerability compared to DACs, tracts with darkest hue are most vulnerable and most exposed to environmental hazards
fig2, ax2 = plt.subplots(figsize=(12, 10))
fig2.tight_layout()

trimmed.plot(column="Cumulative_Burden_Score", cmap="YlGnBu", linewidth=0.1, edgecolor='gray', legend=True, 
             vmin=trimmed['Cumulative_Burden_Score'].min(), vmax=merged['Cumulative_Burden_Score'].max(), ax=ax2)

#Add in outline for DAC's 
trimmed[trimmed['Is_DAC'] == 1].boundary.plot(ax=ax2, color='black', linewidth=1.0, label='DAC Boundary')

#Add in text annotation
ax2.text(0.05, 0.90,
         "High vulnerability and environmental\nexposure rates are concentrated\nin historically disadvantaged areas\nof New York, including central Bronx\nand south Brooklyn.",
         transform=ax2.transAxes,
         fontsize=14,
         verticalalignment='top',
         horizontalalignment='left',
         bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

ax2.set_axis_off()
ax2.set_title("Vulnerability and Environmental Hazard Exposure", fontsize=20)

#Edit scale bar 
cbar_ax = fig2.axes[-1]
box = cbar_ax.get_position()
cbar_ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])

cbar_ax.tick_params(labelsize=12)


#%% Map 3: Clusters


#Create map to show how clusters created in 'ejanalyze.py' are distributed throughout the city
fig3, ax3 = plt.subplots(figsize=(12,10))
fig3.tight_layout()

#Create a color scheme for the four clusters and the labels they correlate with
cluster_colors = ['skyblue', 'gold', 'lightgreen', 'tomato']
cluster_cmap = mcolors.ListedColormap(cluster_colors)

cluster_labels = ['Cluster 0', 'Cluster 1', 'Cluster 2', 'Cluster 3']

trimmed.plot(column="Cluster", cmap=cluster_cmap, linewidth=0.3, edgecolor='gray', ax=ax3)

#Add in outline for DAC's 
trimmed[trimmed['Is_DAC'] == 1].boundary.plot(ax=ax3, color='black', linewidth=1.0, label='DAC Boundary')

#Add in text annotation
ax3.text(0.05, 0.90,
         "Cluster 0 has the highest rates\nof environmental harms and vulnerability,\nwhile Cluster 1 is the opposite.\nCluster's 2 and 3 are in\nthe middle - 2 has low\npollution with higher metrics\nin vulnerability, while 3 has high\npollution with low vulnerability",
         transform=ax3.transAxes,
         fontsize=14,
         verticalalignment='top',
         horizontalalignment='left',
         bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

ax3.set_axis_off()
ax3.set_title("K-means Cluster Assignments", fontsize=20)

#Add in legend for clusters
patches = [mpatches.Patch(color=col, label=label)
           for col, label in zip(cluster_colors, cluster_labels)]

ax3.legend(handles=patches, title='Cluster', loc='lower right', fontsize=14, title_fontsize=16)


#%% Save Figures as PNGs


#Move to greater project directory
nycenvdir = os.path.abspath(os.path.join(os.getcwd(), ".."))

#Define and check that output figure folder exists/functions
fig_folder = os.path.join(nycenvdir, "output_figures")
os.makedirs(fig_folder, exist_ok=True)

#Define file path and save maps as pngs
fig1.savefig(os.path.join(fig_folder, "dacdesignations.png"))

fig2.savefig(os.path.join(fig_folder, "cumulativeburden.png"))

fig3.savefig(os.path.join(fig_folder, "clusters.png"))

