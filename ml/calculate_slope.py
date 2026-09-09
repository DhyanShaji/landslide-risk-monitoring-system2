import math
from pathlib import Path

import numpy as np
import rasterio


INPUT_DEM = Path("data/raw/dem.tif")
OUTPUT_SLOPE = Path("data/processed/slope_degrees.tif")

OUTPUT_SLOPE.parent.mkdir(parents=True, exist_ok=True)


# Earth radius in metres
EARTH_RADIUS = 6_371_000.0


def meters_per_degree_lat(lat):
    """Approximate metres per degree of latitude."""
    lat_rad = np.radians(lat)

    return (
        111132.92
        - 559.82 * np.cos(2 * lat_rad)
        + 1.175 * np.cos(4 * lat_rad)
        - 0.0023 * np.cos(6 * lat_rad)
    )


def meters_per_degree_lon(lat):
    """Approximate metres per degree of longitude."""
    lat_rad = np.radians(lat)

    return (
        111412.84 * np.cos(lat_rad)
        - 93.5 * np.cos(3 * lat_rad)
        + 0.118 * np.cos(5 * lat_rad)
    )


with rasterio.open(INPUT_DEM) as src:

    if src.crs.to_epsg() != 4326:
        raise RuntimeError(
            f"Expected EPSG:4326 DEM, found {src.crs}"
        )

    print("Input DEM:", INPUT_DEM)
    print("Size:", src.width, "x", src.height)
    print("Resolution:", src.res)
    print("CRS:", src.crs)

    profile = src.profile.copy()

    profile.update(
        {
            "driver": "GTiff",
            "dtype": "float32",
            "count": 1,
            "nodata": -9999.0,
            "compress": "deflate",
            "tiled": True,
        }
    )

    with rasterio.open(OUTPUT_SLOPE, "w", **profile) as dst:

        # Process the DEM in blocks to avoid loading
        # the entire 300+ MB raster into RAM.
        for block_index, (_, window) in enumerate(
    src.block_windows(1), start=1
        ):


            # Add a 1-pixel border for gradient calculation
            row_start = max(0, window.row_off - 1)
            col_start = max(0, window.col_off - 1)

            row_end = min(
                src.height,
                window.row_off + window.height + 1,
            )

            col_end = min(
                src.width,
                window.col_off + window.width + 1,
            )

            read_window = rasterio.windows.Window(
                col_start,
                row_start,
                col_end - col_start,
                row_end - row_start,
            )

            dem = src.read(
                1,
                window=read_window,
                masked=True,
            )

            elevation = dem.astype(np.float64).filled(np.nan)

            # Latitude of each raster row
            rows = np.arange(
                row_start,
                row_end,
                dtype=np.float64,
            )

            latitudes = (
                src.transform.f
                + (rows + 0.5) * src.transform.e
            )

            # Metres represented by one degree
            # at each latitude
            dy_per_degree = meters_per_degree_lat(latitudes)
            dx_per_degree = meters_per_degree_lon(latitudes)

            # DEM coordinate resolution in degrees
            dx_deg = abs(src.transform.a)
            dy_deg = abs(src.transform.e)

            # Calculate elevation gradients
            dz_drow, dz_dcol = np.gradient(
                elevation
            )

            # Convert from elevation-per-degree
            # to elevation-per-metre
            dz_dx = (
                dz_dcol
                / (dx_deg * dx_per_degree[:, None])
            )

            dz_dy = (
                dz_drow
                / (dy_deg * dy_per_degree[:, None])
            )

            # Slope angle in radians
            slope_radians = np.arctan(
                np.sqrt(
                    dz_dx ** 2
                    + dz_dy ** 2
                )
            )

            # Convert radians to degrees
            slope_degrees = np.degrees(
                slope_radians
            )

            # Extract original block from
            # the halo-expanded calculation
            row_offset = window.row_off - row_start
            col_offset = window.col_off - col_start

            slope_block = slope_degrees[
                row_offset:
                row_offset + window.height,
                col_offset:
                col_offset + window.width,
            ]

            # Invalid DEM pixels remain invalid
            slope_block = np.where(
                np.isfinite(slope_block),
                slope_block,
                -9999.0,
            ).astype(np.float32)

            dst.write(
                slope_block,
                1,
                window=window,
            )

            if block_index % 100 == 0:
                print(
                    f"Processed {block_index} raster blocks..."
                )


print()
print("======================================")
print("SLOPE CALCULATION COMPLETE")
print("======================================")
print("Output:", OUTPUT_SLOPE)
print("Format: GeoTIFF")
print("Units: degrees")