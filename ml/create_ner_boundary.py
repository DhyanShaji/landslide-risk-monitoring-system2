import geopandas as gpd
import pandas as pd
from pathlib import Path

# Folder containing the 8 NER state files
raw = Path("data/raw")

states = [
    "arunachal-pradesh.geojson",
    "assam.geojson",
    "manipur.geojson",
    "meghalaya.geojson",
    "mizoram.geojson",
    "nagaland.geojson",
    "sikkim.geojson",
    "tripura.geojson"
]

gdfs = []

for state in states:
    file_path = raw / state

    print(f"Reading {state}...")

    gdf = gpd.read_file(file_path)

    # Keep track of the state
    gdf["state"] = state.replace(".geojson", "")

    gdfs.append(gdf)

# Combine all 8 states
ner = gpd.GeoDataFrame(
    pd.concat(gdfs, ignore_index=True),
    crs=gdfs[0].crs
)

# Fix invalid geometries if necessary
ner["geometry"] = ner.geometry.make_valid()

# Save the combined boundary
output = raw / "ner_boundary.geojson"

ner.to_file(output, driver="GeoJSON")

print("\nSUCCESS!")
print(f"Saved: {output}")
print("\nStates included:")

for state in states:
    print(" -", state.replace(".geojson", ""))

print(f"\nTotal features: {len(ner)}")