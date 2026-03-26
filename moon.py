# ==========================================
# STEP 1: ENVIRONMENT SETUP & DOWNLOAD
# ==========================================
!pip install -q rasterio plotly

!wget -nc "https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif" -O moon_dem.tif

import rasterio
import numpy as np
import plotly.graph_objects as go

# ==========================================
# STEP 2: LOAD & CLEAN DATA
# ==========================================
print("Loading data...")
with rasterio.open('moon_dem.tif') as dataset:
    downsample_factor = 100
    elevation_data = dataset.read(1)[::downsample_factor, ::downsample_factor].astype(np.float32)

# Fix outliers and missing data
elevation_data[elevation_data < -20000] = np.nan 

# Clamp the elevation range so colors pop
valid_min = -9500.0  
valid_max = 11000.0  
elevation_data = np.clip(elevation_data, valid_min, valid_max)

elevation_scaled = (elevation_data - valid_min) / (valid_max - valid_min)
elevation_scaled = np.nan_to_num(elevation_scaled, nan=0.5)

# ==========================================
# STEP 3: SPHERICAL PROJECTION
# ==========================================
print("Calculating coordinates...")
rows, cols = elevation_scaled.shape

lat = np.linspace(np.pi/2, -np.pi/2, rows)
lon = np.linspace(-np.pi, np.pi, cols)
lon_grid, lat_grid = np.meshgrid(lon, lat)

base_radius = 1.0
exaggeration = 0.05 
R = base_radius + (elevation_scaled * exaggeration)

X = R * np.cos(lat_grid) * np.cos(lon_grid)
Y = R * np.cos(lat_grid) * np.sin(lon_grid)
Z = R * np.sin(lat_grid)

lat_deg = np.degrees(lat_grid)
lon_deg = np.degrees(lon_grid)

# Clean the raw elevation data before passing it to the hover tool
elevation_hover = np.nan_to_num(elevation_data, nan=0.0)
custom_hover_data = np.stack((lat_deg, lon_deg, elevation_hover), axis=-1)

# ==========================================
# STEP 4: LAYERS, MARKERS, AND BOUNDARY
# ==========================================
print("Building map layers...")
tick_vals = [0.0, 0.25, 0.5, 0.75, 1.0]
tick_text = [f"{int(valid_min + v*(valid_max - valid_min)):,} m" for v in tick_vals]

# Layer 1: The Moon Surface
moon_surface = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=elevation_scaled, 
    colorscale='Greys', 
    showscale=False, 
    cmin=0, cmax=1,
    colorbar=dict(title="Elevation", x=0.9, tickvals=tick_vals, ticktext=tick_text),
    customdata=custom_hover_data,
    hovertemplate="<b>Lat:</b> %{customdata[0]:.2f}°<br><b>Lon:</b> %{customdata[1]:.2f}°<br><b>Elevation:</b> %{customdata[2]:.0f} m<extra></extra>"
)

map_layers = [moon_surface] 

# Layer 2: Space Agency POIs
lunar_features = {
    "NASA": {"Apollo 11 Base": (0.674, 23.472), "Apollo 15 (Hadley Rille)": (26.13, 3.63)},
    "ISRO": {"Chandrayaan-3 (Shiv Shakti)": (-69.37, 32.32), "Chandrayaan-1 (Impact Probe)": (-89.76, -39.40)},
    "CNSA": {"Chang'e 4 (Far Side)": (-45.44, 177.60), "Chang'e 5 (Sample Return)": (43.1, -51.8)},
    "USSR": {"Luna 9 (First Soft Landing)": (7.08, -64.37), "Lunokhod 1 (First Rover)": (38.3, -35.0)},
    "Natural Features": {"Tycho Crater": (-43.3, -11.2), "Copernicus Crater": (9.62, -20.08)}
}
agency_colors = {"NASA": "blue", "ISRO": "orange", "CNSA": "red", "USSR": "yellow", "Natural Features": "white"}

for agency, locations in lunar_features.items():
    feat_x, feat_y, feat_z, feat_names = [], [], [], []
    for name, (f_lat, f_lon) in locations.items():
        f_lat_rad, f_lon_rad = np.radians(f_lat), np.radians(f_lon)
        r_feat = base_radius + 0.08 
        feat_x.append(r_feat * np.cos(f_lat_rad) * np.cos(f_lon_rad))
        feat_y.append(r_feat * np.cos(f_lat_rad) * np.sin(f_lon_rad))
        feat_z.append(r_feat * np.sin(f_lat_rad))
        feat_names.append(name)
        
    agency_layer = go.Scatter3d(
        x=feat_x, y=feat_y, z=feat_z, mode='markers+text',
        marker=dict(size=6, color=agency_colors[agency]),
        text=feat_names, textposition='top center', textfont=dict(color=agency_colors[agency], size=11),
        hovertemplate="<b>%{text}</b><br>Agency: " + agency + "<extra></extra>",
        name=agency 
    )
    map_layers.append(agency_layer)

# Layer 3: Boundary Line
bound_lat = np.linspace(-np.pi/2, np.pi/2, 100)
bound_lon_E = np.full_like(bound_lat, np.pi/2)  
bound_lon_W = np.full_like(bound_lat, -np.pi/2) 

X_E, Y_E, Z_E = (base_radius + 0.06) * np.cos(bound_lat) * np.cos(bound_lon_E), (base_radius + 0.06) * np.cos(bound_lat) * np.sin(bound_lon_E), (base_radius + 0.06) * np.sin(bound_lat)
X_W, Y_W, Z_W = (base_radius + 0.06) * np.cos(bound_lat) * np.cos(bound_lon_W), (base_radius + 0.06) * np.cos(bound_lat) * np.sin(bound_lon_W), (base_radius + 0.06) * np.sin(bound_lat)

map_layers.append(go.Scatter3d(
    x=np.concatenate([X_E, X_W[::-1], [X_E[0]]]), y=np.concatenate([Y_E, Y_W[::-1], [Y_E[0]]]), z=np.concatenate([Z_E, Z_W[::-1], [Z_E[0]]]),
    mode='lines', line=dict(color='yellow', width=4, dash='dot'), hoverinfo='skip', showlegend=False 
))

# Layer 4: Hemisphere Labels
label_radius = base_radius + 0.15
map_layers.append(go.Scatter3d(
    x=[label_radius, -label_radius], y=[0, 0], z=[0, 0], 
    mode='text', text=['<b>NEAR SIDE</b>', '<b>FAR SIDE</b>'],
    textposition='middle center', textfont=dict(color='lightgreen', size=18), hoverinfo='skip', showlegend=False
))

# ==========================================
# STEP 5: RENDER WITH UI FIXES
# ==========================================
print("Rendering the map...")

layout = go.Layout(
    title='Interactive 3D Moon Globe',
    plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'),
    width=1000, height=800,
    margin=dict(l=0, r=0, b=0, t=50), 
    scene=dict(
        xaxis=dict(visible=False, showspikes=False), 
        yaxis=dict(visible=False, showspikes=False), 
        zaxis=dict(visible=False, showspikes=False),
        aspectmode='data' 
    ),
    showlegend=True,
    legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.05, bgcolor="rgba(0,0,0,0.5)"),
    
    # --- THE JAVASCRIPT FIX ---
    # Values are now wrapped in lists [] and use strict Plotly.js naming ("Greys")
    updatemenus=[
        dict(
            type="buttons", direction="right", x=0.1, y=1.05, showactive=True,
            buttons=[
                dict(label="🌑 Realistic (Grayscale)", method="restyle", args=[{"colorscale": ["Greys"], "showscale": [False]}, [0]]),
                dict(label="🌈 Elevation Contour", method="restyle", args=[{"colorscale": ["Turbo"], "showscale": [True]}, [0]])
            ]
        )
    ]
)

fig = go.Figure(data=map_layers, layout=layout)
fig.show()

# fig.write_html("Interactive_Moon_Map.html")
# print("Map saved as Interactive_Moon_Map.html!")
