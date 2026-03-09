import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import pandas as pd

# Sample data points
x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([12, 14, 22, 39, 58, 77])

# Create a CubicSpline object
# 'bc_type' specifies the boundary conditions. 'natural' sets the second derivative to zero at the endpoints.
cs = CubicSpline(x, y, bc_type='natural')

# Evaluate the spline at new points
x_new = np.linspace(0, 5, 100) # Generate 100 points between 0 and 5
y_new = cs(x_new)

# Plotting the results
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'ro', label='Data Points')
plt.plot(x_new, y_new, 'b-', label='Cubic Spline Interpolation')
plt.title('Cubic Spline Interpolation')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.legend()
plt.grid(True)
plt.show()

# cublic spline interpolation in the x-y coordinates
df1 = pd.read_csv("C:/Users/bijan/OneDrive/Desktop/CCVA_ABM/Lesser_yellowlegs_monarch/USFWSLesserYellowlegs_migratory_Johnson_179737.csv")
type(df1)
df1.head(20)
df1.columns
df1.dtypes
df1[['location_long', 'location_lat']]

# inFC1 = "C:/Users/bijan/OneDrive/Desktop/CCVA_ABM/ambR_1/ambR_1.gdb/USFWSLesserYellowlegs_migratory_Johnson_179737"
s_localized = df1['timestamp'].dt.tz_localize('America/Chicago')
s_utc = s_localized.dt.tz_convert('UTC')
s_utc.head()
df5 = df1['timestamp'].timestamp()

df1.describe()
type(df1['timestamp'])
df1['timestamp']=pd.to_datetime(df1['timestamp'])
df1['timestamp']
df1_lon_x = df1['timestamp'].tz_convert('UTC').to_numpy()
# df1_lon_x = df1['location_long'].to_numpy()
df1_lat_y = df1['location_lat'].to_numpy()

cs = CubicSpline(df1_lon_x, df1_lat_y, bc_type='natural')
# showed error: ValueError: `x` must be strictly increasing sequence.

import datetime

# Create a datetime object (e.g., for a specific date and time)
dt_object = datetime.datetime(2025, 8, 25, 10, 30, 0)

# Convert the datetime object to a Unix timestamp
unix_timestamp = dt_object.timestamp()

print(f"Datetime object: {dt_object}")
print(f"Unix timestamp: {unix_timestamp}")

# To get the current Unix timestamp
current_unix_timestamp = datetime.datetime.now().timestamp()
print(f"Current Unix timestamp: {current_unix_timestamp}")

# To get the current UTC Unix timestamp
utc_unix_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
print(f"Current UTC Unix timestamp: {utc_unix_timestamp}")

df1['datetime_col'] = pd.to_datetime(df1['timestamp'])
df1['unix_timestamp'] = df1['datetime_col'].dt.timestamp()
df1.columns
df1.head()

import pandas as pd

# Example DataFrame with a string date column
data = {'date_str': ['2023-01-01 10:30:00', '2023-01-02 11:00:00']}
df = pd.DataFrame(data)

# Convert to datetime objects
df['datetime_col'] = pd.to_datetime(df['date_str'])

df['unix_timestamp'] = df['datetime_col'].dt.timestamp()

print(df)

#---------------------------------------------------------------------------------------------
# 1D interpolation for time-series data
# Create sample time-series data with gaps
data = pd.DataFrame({
    'time': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-04', '2025-01-05']),
    'value': [10, 12, 16, 18]
})

# Create a full time index for interpolation
full_time_index = pd.date_range(start='2025-01-01', end='2025-01-05', freq='D')

# Extract known points
x = data['time'].apply(lambda t: t.toordinal()).values
y = data['value'].values

# Create the cubic spline function
cs = CubicSpline(x, y)

# Interpolate for all dates in the full index
x_new = np.array([t.toordinal() for t in full_time_index])
y_interpolated = cs(x_new)

# Combine and visualize the results
filled_data = pd.DataFrame({'time': full_time_index, 'value': y_interpolated})
print(filled_data)

plt.figure(figsize=(8, 6))
plt.plot(data['time'], data['value'], 'o', label='Original Data')
plt.plot(filled_data['time'], filled_data['value'], '-', label='Cubic Spline Interpolation')
plt.title('1D Cubic Spline for Time-Series Data')
plt.legend()
plt.show()

#------------------------------------------------------------------------------------------------
# Using B-splines or Cubic Splines to interpolate the GPS points:

import numpy as np
from scipy.interpolate import splrep, splev
import matplotlib.pyplot as plt

df1['location_lat'].isna().sum()      # check if there are any null values
df1['location_long'].isna().sum()

# convert the df series to numpy array
latitudes = df1['location_lat'].to_numpy()
longitudes = df1['location_long'].to_numpy()

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

df2.to_csv('C:/Users/bijan/OneDrive/Desktop/CCVA_ABM/Lesser_yellowlegs_monarch/USFWSLesserYellowlegs_Johnson_179737_spline.csv', index=False)

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