# MOON_Surface
Using NASA LRO dataset and python generating a 3D map of moon.

# 🌕 Interactive 3D Moon Globe

An interactive 3D map of the Moon's surface built from NASA's LRO LOLA elevation dataset, rendered as a rotatable globe with hover tooltips, POI markers, and switchable colour modes.

**Vibe-coded with Claude from idea to working visualisation in one session.**

![Moon Globe]
<img width="1233" height="689" alt="image" src="https://github.com/user-attachments/assets/54c0db0d-229e-49b8-9733-1dac215c9a9a" />

<img width="698" height="660" alt="image" src="https://github.com/user-attachments/assets/7fdafdac-a26e-412b-a4f2-788e9bc0aa10" />


## What it does

- Loads the [NASA LRO LOLA Global DEM (118m resolution)](https://planetarymaps.usgs.gov/mosaic/) — a real 6.5 GB elevation dataset
- Downsamples, cleans outliers, and projects the elevation data onto a 3D sphere
- Renders an interactive Plotly globe you can rotate, zoom, and hover over to read lat/lon/elevation
- Plots labelled POI markers for Apollo, Chandrayaan, Chang'e, and Luna landing sites
- Toggle between **Realistic Grayscale** and **Elevation Contour (Turbo)** colour modes

## Why it exists

I was working on a Lunar ISRU habitat design project and wanted to visually explore candidate polar drilling sites. Instead of using an existing tool, I vibe-coded this in an afternoon it turned out to be a good exercise in the full pipeline: raw satellite data → processing → interactive product. Same workflow I'd apply to SAR or EO data.

## Stack

- Python (NumPy, Rasterio, Plotly) runs in Jupyter / Google Colab
- Single script, no backend required
- Dataset auto-downloads on first run (~300 MB after downsampling)

## Run it
```bash
pip install rasterio plotly
jupyter notebook moon.py
```

Or open directly in [Google Colab](https://colab.research.google.com/) — the `!wget` and `!pip` lines handle setup automatically.

## Output

The globe renders inline in Jupyter or as a standalone HTML file (`fig.write_html("Interactive_Moon_Map.html")`).
