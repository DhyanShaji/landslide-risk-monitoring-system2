import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point


# -----------------------------------------
# File paths
# -----------------------------------------

landslide_file = "data/processed/landslide_features_rainfall.csv"
boundary_file = "data/raw/ner_boundary.geojson"

output_file = "data/processed/background_samples.csv"


# -----------------------------------------
# Load data
# -----------------------------------------

landslides = pd.read_csv(landslide_file)

boundary = gpd.read_file(boundary_file)


print("Landslide records:", len(landslides))


# -----------------------------------------
# Convert landslides to GeoDataFrame
# -----------------------------------------

landslide_points = gpd.GeoDataFrame(
    landslides,
    geometry=[
        Point(lon, lat)
        for lon, lat in zip(
            landslides["Longitude"],
            landslides["Latitude"]
        )
    ],
    crs="EPSG:4326"
)


# -----------------------------------------
# Create a buffer around landslides
# -----------------------------------------
# We use a projected CRS so distance is in metres.

landslide_projected = landslide_points.to_crs(
    "EPSG:32646"
)

landslide_buffer = (
    landslide_projected
    .geometry
    .buffer(1000)
)

buffer_union = landslide_buffer.union_all()


# -----------------------------------------
# Project NER boundary
# -----------------------------------------

boundary_projected = boundary.to_crs(
    "EPSG:32646"
)

boundary_polygon = boundary_projected.geometry.union_all()


# -----------------------------------------
# Generate random background points
# -----------------------------------------

np.random.seed(42)

background_points = []

target = len(landslides)

min_x, min_y, max_x, max_y = boundary_polygon.bounds


print("\nGenerating background points...")

while len(background_points) < target:

    x = np.random.uniform(min_x, max_x)
    y = np.random.uniform(min_y, max_y)

    point = Point(x, y)

    # Point must be inside NER
    if not boundary_polygon.contains(point):
        continue

    # Point should not be close to known landslides
    if buffer_union.contains(point):
        continue

    background_points.append(point)

    if len(background_points) % 500 == 0:
        print(
            f"Generated {len(background_points)}/{target}"
        )


# -----------------------------------------
# Convert back to latitude/longitude
# -----------------------------------------

background_gdf = gpd.GeoDataFrame(
    geometry=background_points,
    crs="EPSG:32646"
)

background_gdf = background_gdf.to_crs(
    "EPSG:4326"
)


# -----------------------------------------
# Create dataframe
# -----------------------------------------

background_df = pd.DataFrame({
    "Latitude": background_gdf.geometry.y,
    "Longitude": background_gdf.geometry.x,
    "Label": 0
})


# -----------------------------------------
# Save
# -----------------------------------------

background_df.to_csv(
    output_file,
    index=False
)


print("\nBackground sampling completed!")

print(
    "Background records:",
    len(background_df)
)

print("\nSample:")

print(background_df.head())

print("\nSaved to:")
print(output_file)