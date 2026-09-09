import gzip
import shutil
import urllib.request
from pathlib import Path

TILE_FILE = Path("data/raw/srtm_tiles.txt")
OUTPUT_DIR = Path("data/raw/dem_tiles")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tiles = [
    line.strip()
    for line in TILE_FILE.read_text().splitlines()
    if line.strip()
]

print(f"Tiles to download: {len(tiles)}")

for i, tile in enumerate(tiles, start=1):

    latitude_folder = tile[:3]

    url = (
        f"https://elevation-tiles-prod.s3.amazonaws.com/"
        f"skadi/{latitude_folder}/{tile}.hgt.gz"
    )

    compressed_file = OUTPUT_DIR / f"{tile}.hgt.gz"
    hgt_file = OUTPUT_DIR / f"{tile}.hgt"

    if hgt_file.exists() and hgt_file.stat().st_size > 0:
        print(f"[{i}/{len(tiles)}] Already exists: {tile}")
        continue

    print(f"[{i}/{len(tiles)}] Downloading {tile}...")

    try:
        urllib.request.urlretrieve(url, compressed_file)

        if compressed_file.stat().st_size == 0:
            raise RuntimeError("Downloaded file is empty")

        with gzip.open(compressed_file, "rb") as source:
            with open(hgt_file, "wb") as destination:
                shutil.copyfileobj(source, destination)

        compressed_file.unlink()

        print(f"    OK: {hgt_file}")

    except Exception as e:
        print(f"    FAILED: {tile}")
        print(f"    {e}")

print("\nDownload process finished.")