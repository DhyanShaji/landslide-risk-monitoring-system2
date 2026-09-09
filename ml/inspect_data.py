"""
Inspect datasets placed in data/raw/.

This script only reads files. It does not create, download, or change
any data. Column names and types come from each file itself.

Usage (from the project root):
    python ml/inspect_data.py
"""

from pathlib import Path

import pandas as pd

# GeoPandas is used only for geospatial files (shapefiles, GeoJSON, etc.).
try:
    import geopandas as gpd
except ImportError:
    gpd = None


# Folder that holds the raw datasets (next to this file: ../data/raw).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# File types we try to open as tables.
PANDAS_SUFFIXES = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".parquet", ".json"}
GEOPANDAS_SUFFIXES = {".shp", ".geojson", ".gpkg", ".gpkg.zip", ".gpx", ".kml", ".gml"}

# Extra shapefile sidecar files. We inspect the .shp once, not these.
SHAPEFILE_SIDECARS = {".shx", ".dbf", ".prj", ".cpg", ".sbn", ".sbx", ".shp.xml"}

# Names we never treat as datasets.
SKIP_NAMES = {"readme.md", "readme.txt", ".gitkeep"}


def is_data_file(path: Path) -> bool:
    """Return True if this path looks like a dataset file we can inspect."""
    if not path.is_file():
        return False
    if path.name.lower() in SKIP_NAMES:
        return False
    if path.name.startswith("."):
        return False

    suffix = path.suffix.lower()
    # Shapefile sidecars are not inspected on their own.
    if suffix in SHAPEFILE_SIDECARS or path.name.lower().endswith(".shp.xml"):
        return False

    return suffix in PANDAS_SUFFIXES or suffix in GEOPANDAS_SUFFIXES


def load_table(path: Path):
    """
    Load one file into a DataFrame or GeoDataFrame.

    - Geospatial formats -> GeoPandas (if installed)
    - Spreadsheet / CSV / Parquet / JSON -> Pandas
    """
    suffix = path.suffix.lower()

    if suffix in GEOPANDAS_SUFFIXES:
        if gpd is None:
            raise ImportError(
                "geopandas is required to read geospatial files. "
                "Install it, then run this script again."
            )
        return gpd.read_file(path)

    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t")
    if suffix == ".txt":
        # Try comma first, then tab. We do not guess extra column names.
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.read_csv(path, sep="\t")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".json":
        # JSON might be a table or GeoJSON. Try GeoPandas first when available.
        if gpd is not None:
            try:
                geo_table = gpd.read_file(path)
                if "geometry" in geo_table.columns:
                    return geo_table
            except Exception:
                pass
        return pd.read_json(path)

    raise ValueError(f"Unsupported file type: {path.suffix}")


def print_section(title: str) -> None:
    """Print a simple heading so each report is easy to scan."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def inspect_dataframe(name: str, table: pd.DataFrame) -> None:
    """Print the requested summary for one loaded table."""
    print_section(f"File: {name}")

    n_rows, n_cols = table.shape
    print(f"Number of rows: {n_rows}")
    print(f"Number of columns: {n_cols}")

    print("\nColumn names:")
    if n_cols == 0:
        print("  (no columns in this file)")
    else:
        for col in table.columns:
            print(f"  - {col}")

    print("\nData types:")
    print(table.dtypes.to_string())

    print("\nMissing values (count per column):")
    missing = table.isna().sum()
    print(missing.to_string())
    print(f"Total missing cells: {int(missing.sum())}")

    print("\nDuplicate rows:")
    try:
        n_duplicates = int(table.duplicated().sum())
        print(f"  {n_duplicates}")
    except TypeError:
        # Some geometry columns cannot be hashed for duplicate checks.
        print("  Could not count duplicates for this file (unsupported column types).")

    print("\nFirst 5 rows:")
    if n_rows == 0:
        print("  (file has no rows)")
    else:
        # to_string keeps the layout readable in the terminal.
        print(table.head(5).to_string())


def main() -> None:
    print_section("Raw data folder")
    print(f"Looking in: {RAW_DATA_DIR}")

    if not RAW_DATA_DIR.exists():
        print("The folder data/raw/ does not exist. No files were changed.")
        return

    # Collect files under data/raw/, including nested folders.
    all_files = sorted(p for p in RAW_DATA_DIR.rglob("*") if is_data_file(p))

    if not all_files:
        print("No dataset files were found in data/raw/.")
        print("Place CSV, Excel, Parquet, JSON, GeoJSON, GPKG, or shapefile data there.")
        print("This script does not download or generate sample data.")
        return

    print(f"Found {len(all_files)} dataset file(s):")
    for path in all_files:
        relative = path.relative_to(RAW_DATA_DIR)
        print(f"  - {relative}")

    for path in all_files:
        relative = path.relative_to(RAW_DATA_DIR)
        try:
            table = load_table(path)
        except Exception as error:
            print_section(f"File: {relative}")
            print(f"Could not read this file: {error}")
            continue

        inspect_dataframe(str(relative), table)

    print()
    print("Inspection finished. No files in data/raw/ were modified.")


if __name__ == "__main__":
    main()
