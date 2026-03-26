# ==========================================
# STEP 1: ENVIRONMENT SETUP & DOWNLOAD
# ==========================================
import rasterio
import numpy as np
import plotly.graph_objects as go

# ==========================================
# STEP 2: LOAD AND DOWNSAMPLE DATA
# ==========================================
print("Loading and downsampling the NASA elevation data...")

with rasterio.open('moon_dem.tif') as dataset:
    downsample_factor = 100
    
    # FIX 1: Convert the raw 16-bit integer data to floats immediately to prevent the overflow
    elevation_data = dataset.read(1)[::downsample_factor, ::downsample_factor].astype(np.float32)

# FIX 2: Handle "NoData" pixels (USGS often uses -32768 for missing data)
# The moon's actual elevation is roughly between -9000m and +10700m. 
# We will set anything crazy to "NaN" so it doesn't ruin our math.
elevation_data[elevation_data < -20000] = np.nan 

# Safely calculate the min and max, ignoring those NaNs
valid_min = np.nanmin(elevation_data)
valid_max = np.nanmax(elevation_data)

# Normalize the elevation data between 0 and 1 for rendering
elevation_scaled = (elevation_data - valid_min) / (valid_max - valid_min)

# Fill any NaN gaps with a neutral middle gray (0.5) so Plotly doesn't crash
elevation_scaled = np.nan_to_num(elevation_scaled, nan=0.5)

# ==========================================
# STEP 3: SPHERICAL PROJECTION MATH
# ==========================================
print("Calculating 3D spherical coordinates...")

rows, cols = elevation_scaled.shape

# Global maps typically range from 90 to -90 Latitude, and -180 to 180 Longitude
lat = np.linspace(np.pi/2, -np.pi/2, rows)
lon = np.linspace(-np.pi, np.pi, cols)
lon_grid, lat_grid = np.meshgrid(lon, lat)

base_radius = 1.0
exaggeration = 0.05 # Adjust this to make mountains/craters taller or flatter

# Calculate final radius
R = base_radius + (elevation_scaled * exaggeration)

# Convert to Cartesian (X, Y, Z) coordinates
X = R * np.cos(lat_grid) * np.cos(lon_grid)
Y = R * np.cos(lat_grid) * np.sin(lon_grid)
Z = R * np.sin(lat_grid)

# ==========================================
# STEP 4: RENDER THE 3D GLOBE
# ==========================================
print("Rendering the interactive 3D map...")

moon_surface = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=elevation_scaled, 
    colorscale='gray',
    showscale=False,
    cmin=0, cmax=1
)

layout = go.Layout(
    title='Interactive 3D Moon Globe (USGS LOLA Data)',
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    width=800,
    height=800,
    scene=dict(
        xaxis=dict(visible=False), 
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data' 
    )
)

fig = go.Figure(data=[moon_surface], layout=layout)
fig.show()
