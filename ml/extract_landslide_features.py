import geopandas as gpd
import rasterio
import pandas as pd


# --------------------------------------------------
# 1. Load landslide data
# --------------------------------------------------

landslides = gpd.read_file(
    "data/raw/landslides_ner_2023.geojson"
)

print("Landslides loaded:", len(landslides))


# --------------------------------------------------
# 2. Open DEM and slope files
# --------------------------------------------------

dem_path = "data/raw/dem.tif"
slope_path = "data/processed/slope_degrees.tif"

dem = rasterio.open(dem_path)
slope = rasterio.open(slope_path)


# --------------------------------------------------
# 3. Create coordinates
# --------------------------------------------------

coordinates = list(
    zip(
        landslides["Longitude"],
        landslides["Latitude"]
    )
)


# --------------------------------------------------
# 4. Extract elevation
# --------------------------------------------------

elevation_values = []

for value in dem.sample(coordinates):
    elevation_values.append(float(value[0]))


# --------------------------------------------------
# 5. Extract slope
# --------------------------------------------------

slope_values = []

for value in slope.sample(coordinates):
    slope_values.append(float(value[0]))


# --------------------------------------------------
# 6. Add values to landslide data
# --------------------------------------------------

landslides["Elevation"] = elevation_values
landslides["Slope"] = slope_values


# --------------------------------------------------
# 7. Remove invalid values
# --------------------------------------------------

landslides = landslides[
    (landslides["Elevation"] != -9999) &
    (landslides["Slope"] != -9999)
]


# --------------------------------------------------
# 8. Save feature dataset
# --------------------------------------------------

output = "data/processed/landslide_features.csv"

landslides.drop(
    columns="geometry"
).to_csv(
    output,
    index=False
)


# --------------------------------------------------
# 9. Display results
# --------------------------------------------------

print("\nFeature extraction complete!")

print("Remaining records:", len(landslides))

print("\nSample data:")

print(
    landslides[
        [
            "State",
            "District",
            "Latitude",
            "Longitude",
            "Elevation",
            "Slope"
        ]
    ].head()
)

print("\nSaved to:")
print(output)