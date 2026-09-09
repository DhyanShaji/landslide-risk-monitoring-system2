import glob
from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask


# --------------------------------------------------
# Paths
# --------------------------------------------------

TILE_DIR = Path("data/raw/dem_tiles")
BOUNDARY_FILE = Path("data/raw/ner_boundary.geojson")
TEMP_MOSAIC = Path("data/raw/temp_mosaic.tif")
OUTPUT_DEM = Path("data/raw/dem.tif")


# --------------------------------------------------
# Find SRTM tiles
# --------------------------------------------------

tile_files = sorted(TILE_DIR.glob("*.hgt"))

print(f"SRTM tiles found: {len(tile_files)}")

if len(tile_files) != 45:
    raise RuntimeError(
        f"Expected 45 SRTM tiles, but found {len(tile_files)}."
    )


# --------------------------------------------------
# Open all tiles
# --------------------------------------------------

src_files = []

try:
    for tile in tile_files:
        src = rasterio.open(tile)
        src_files.append(src)

    print("All SRTM tiles opened successfully.")

    # --------------------------------------------------
    # Create mosaic
    # --------------------------------------------------

    print("Creating DEM mosaic...")

    mosaic, transform = merge(src_files)

    print("Mosaic created.")
    print(f"Mosaic dimensions: {mosaic.shape}")

    # Use metadata from first tile
    meta = src_files[0].meta.copy()

    meta.update(
        {
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": transform,
            "compress": "deflate",
            "tiled": True,
        }
    )

    # --------------------------------------------------
    # Save temporary mosaic
    # --------------------------------------------------

    print("Saving temporary mosaic...")

    with rasterio.open(TEMP_MOSAIC, "w", **meta) as dest:
        dest.write(mosaic)

    print(f"Temporary mosaic saved: {TEMP_MOSAIC}")

finally:
    for src in src_files:
        src.close()


# --------------------------------------------------
# Load NER boundary
# --------------------------------------------------

print("Loading NER boundary...")

boundary = gpd.read_file(BOUNDARY_FILE)

print(f"Boundary CRS: {boundary.crs}")


# --------------------------------------------------
# Clip mosaic to NER boundary
# --------------------------------------------------

print("Clipping DEM to NER boundary...")

with rasterio.open(TEMP_MOSAIC) as src:

    # Make sure boundary uses same CRS
    boundary = boundary.to_crs(src.crs)

    geometries = boundary.geometry.values

    clipped, clipped_transform = mask(
        src,
        geometries,
        crop=True,
        nodata=-9999,
    )

    clipped_meta = src.meta.copy()

    clipped_meta.update(
        {
            "driver": "GTiff",
            "height": clipped.shape[1],
            "width": clipped.shape[2],
            "transform": clipped_transform,
            "nodata": -9999,
            "compress": "deflate",
            "tiled": True,
        }
    )


# --------------------------------------------------
# Save final DEM
# --------------------------------------------------

print("Saving final DEM...")

with rasterio.open(OUTPUT_DEM, "w", **clipped_meta) as dest:
    dest.write(clipped)


print()
print("======================================")
print("DEM BUILD COMPLETE")
print("======================================")
print(f"Output: {OUTPUT_DEM}")
print(f"Size: {OUTPUT_DEM.stat().st_size:,} bytes")