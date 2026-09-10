import requests
import pandas as pd
import time


# -----------------------------------------
# File paths
# -----------------------------------------

input_file = "data/processed/landslide_features.csv"
output_file = "data/processed/landslide_features_rainfall.csv"


# -----------------------------------------
# Load landslide data
# -----------------------------------------

df = pd.read_csv(input_file)

print("Landslide records:", len(df))


# -----------------------------------------
# Round coordinates
# -----------------------------------------
# This groups nearby locations together.
# We use 1 decimal degree for the prototype.

df["lat_grid"] = df["Latitude"].round(1)
df["lon_grid"] = df["Longitude"].round(1)

grid_points = df[
    ["lat_grid", "lon_grid"]
].drop_duplicates()

print("Unique rainfall grid points:", len(grid_points))


# -----------------------------------------
# NASA POWER API
# -----------------------------------------

url = "https://power.larc.nasa.gov/api/temporal/daily/point"


# -----------------------------------------
# Function to get rainfall
# -----------------------------------------

def get_rainfall(latitude, longitude):

    params = {
        "parameters": "PRECTOTCORR",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": "20230101",
        "end": "20231231",
        "format": "JSON"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            print(
                "API error:",
                response.status_code,
                latitude,
                longitude
            )
            return None

        data = response.json()

        rainfall = data[
            "properties"
        ][
            "parameter"
        ][
            "PRECTOTCORR"
        ]

        return sum(rainfall.values())

    except Exception as e:

        print("Error:", e)

        return None


# -----------------------------------------
# Download rainfall for each grid point
# -----------------------------------------

rainfall_data = []

total = len(grid_points)

for index, row in grid_points.iterrows():

    latitude = row["lat_grid"]
    longitude = row["lon_grid"]

    print(
        f"{len(rainfall_data) + 1}/{total} "
        f"| Lat: {latitude} "
        f"| Lon: {longitude}"
    )

    rainfall = get_rainfall(
        latitude,
        longitude
    )

    rainfall_data.append(
        {
            "lat_grid": latitude,
            "lon_grid": longitude,
            "Rainfall_2023": rainfall
        }
    )

    time.sleep(0.2)


# -----------------------------------------
# Create rainfall dataframe
# -----------------------------------------

rainfall_df = pd.DataFrame(
    rainfall_data
)


# -----------------------------------------
# Merge rainfall with landslide data
# -----------------------------------------

df = df.merge(
    rainfall_df,
    on=["lat_grid", "lon_grid"],
    how="left"
)


# -----------------------------------------
# Remove temporary grid columns
# -----------------------------------------

df = df.drop(
    columns=["lat_grid", "lon_grid"]
)


# -----------------------------------------
# Save final dataset
# -----------------------------------------

df.to_csv(
    output_file,
    index=False
)


# -----------------------------------------
# Display results
# -----------------------------------------

print("\nRainfall processing completed!")

print(
    "Records:",
    len(df)
)

print(
    "Missing rainfall values:",
    df["Rainfall_2023"].isna().sum()
)

print("\nSample data:")

print(
    df[
        [
            "State",
            "Latitude",
            "Longitude",
            "Elevation",
            "Slope",
            "Rainfall_2023"
        ]
    ].head()
)

print("\nSaved to:")
print(output_file)