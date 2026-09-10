import pandas as pd
import numpy as np
import rasterio
from sklearn.neighbors import NearestNeighbors


# -----------------------------------------
# File paths
# -----------------------------------------

background_file = "data/processed/background_samples.csv"

rainfall_file = "data/processed/landslide_features_rainfall.csv"

output_file = "data/processed/background_features.csv"

dem_file = "data/raw/dem.tif"

slope_file = "data/processed/slope_degrees.tif"


# -----------------------------------------
# Load background points
# -----------------------------------------

df = pd.read_csv(background_file)

print("Background records:", len(df))


# -----------------------------------------
# Load existing NASA rainfall data
# -----------------------------------------

rainfall_df = pd.read_csv(rainfall_file)

rainfall_df["lat_grid"] = rainfall_df["Latitude"].round(1)
rainfall_df["lon_grid"] = rainfall_df["Longitude"].round(1)

rainfall_lookup = (
    rainfall_df[
        ["lat_grid", "lon_grid", "Rainfall_2023"]
    ]
    .drop_duplicates(
        ["lat_grid", "lon_grid"]
    )
)

print(
    "Known rainfall grid points:",
    len(rainfall_lookup)
)


# -----------------------------------------
# Find nearest rainfall grid point
# -----------------------------------------

known_coordinates = rainfall_lookup[
    ["lat_grid", "lon_grid"]
].values

background_coordinates = df[
    ["Latitude", "Longitude"]
].values


model = NearestNeighbors(
    n_neighbors=1
)

model.fit(known_coordinates)


distances, indices = model.kneighbors(
    background_coordinates
)


# Assign nearest rainfall value

df["Rainfall_2023"] = (
    rainfall_lookup
    .iloc[indices.flatten()]
    ["Rainfall_2023"]
    .values
)


print("Rainfall assigned successfully.")


# -----------------------------------------
# Extract DEM elevation
# -----------------------------------------

coordinates = list(
    zip(
        df["Longitude"],
        df["Latitude"]
    )
)


with rasterio.open(dem_file) as dem:

    elevation_values = []

    for value in dem.sample(coordinates):

        elevation_values.append(
            float(value[0])
        )


df["Elevation"] = elevation_values


# -----------------------------------------
# Extract slope
# -----------------------------------------

with rasterio.open(slope_file) as slope:

    slope_values = []

    for value in slope.sample(coordinates):

        slope_values.append(
            float(value[0])
        )


df["Slope"] = slope_values


# -----------------------------------------
# Remove invalid raster values
# -----------------------------------------

df = df[
    (df["Elevation"] != -9999) &
    (df["Slope"] != -9999)
]


# -----------------------------------------
# Save final background features
# -----------------------------------------

df.to_csv(
    output_file,
    index=False
)


# -----------------------------------------
# Results
# -----------------------------------------

print("\nBackground feature extraction complete!")

print("Valid records:", len(df))

print(
    "Missing rainfall:",
    df["Rainfall_2023"].isna().sum()
)

print("\nSample:")

print(
    df[
        [
            "Latitude",
            "Longitude",
            "Elevation",
            "Slope",
            "Rainfall_2023",
            "Label"
        ]
    ].head()
)

print("\nSaved to:")

print(output_file)