# Generate cubic spline of the central track out of 20 tracks from two abmR simulations
# Alaska to Central America flight tracks 2018–2021 LULC raster
# Alaska to Central America flight tracks using 2050 LULC raster

import numpy as np
from scipy.interpolate import splrep, splev
import matplotlib.pyplot as plt
import pandas as pd

# df = pd.read_csv("D:/CCVA_ABM/Lesser_yellowlegs_monarch/Lesser_yellowlegs_alaska_to_CentralAmer_lulc_reclass_20trks.csv")
df = pd.read_csv("D:/CCVA_ABM/Lesser_yellowlegs_monarch/Lesser_yellowlegs_alaska_to_CentralAmer_lulc_2050_20trks.csv")
df.head()

df['lat'].isna().sum()      # check if there are any null values
df['lon'].isna().sum()

df1 = df.loc[df['id'] == 121]     # Use 139 for first raster, and 121 for 2050 modeled raster
df1.head()
len(df1)

# convert the df series to numpy array
latitudes = df1['lat'].to_numpy()
longitudes = df1['lon'].to_numpy()

# Create a parameter 't' for interpolation (e.g., cumulative distance or time)
t = np.arange(len(latitudes))

# Fit B-splines to latitude and longitude separately
tck_lat = splrep(t, latitudes, s=0)  # s=0 for interpolation, adjust for smoothing
tck_lon = splrep(t, longitudes, s=0)

# Generate a new, more dense set of 't' values for the smoothed curve
t_new = np.linspace(t.min(), t.max(), 500)

# Evaluate the splines at the new 't' values
lat_smooth = splev(t_new, tck_lat)
lon_smooth = splev(t_new, tck_lon)

# Plotting the original and smoothed track
plt.figure(figsize=(8, 6))
plt.plot(longitudes, latitudes, 'o', label='Original GPS Points')
plt.plot(lon_smooth, lat_smooth, '-', label='Smoothed Curve')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('GPS Track Smoothing with Splines')
plt.legend()
plt.grid(True)
plt.show()

# display the spline points on the map
import geopandas
from shapely.geometry import Point

# generate a dataframe
df2 = pd.DataFrame({"lat": lat_smooth, "long": lon_smooth})

# df2.to_csv('D:/CCVA_ABM/Lesser_yellowlegs_monarch/Lesser_yellowlegs_alaska_to_CentralAmer_lulc_reclass_20trks_central139_spline.csv', index=False)
df2.to_csv('D:/CCVA_ABM/Lesser_yellowlegs_monarch/Lesser_yellowlegs_alaska_to_CentralAmer_lulc_2050_20trks_central121_spline.csv', index=False)

# geodataframe
geometry = [Point(xy) for xy in zip(df2['long'], df2['lat'])]
gdf = geopandas.GeoDataFrame(df2, geometry=geometry, crs="EPSG:4326")

# load a basemap
import geodatasets
world = geopandas.read_file(geodatasets.data.naturalearth.land['url']) # show the world map as base map

# display north and south america as the base map
# world = geopandas.read_file('C:/Users/bijan/OneDrive/Desktop/CCVA_ABM/North_south_america/World_continents_americas.shp')

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 6))
world.plot(ax=ax, color='lightgray', edgecolor='black')
gdf.plot(ax=ax, marker='o', color='red', markersize=5)
plt.title("Lesser yellowlegs tag 179737")
plt.show()