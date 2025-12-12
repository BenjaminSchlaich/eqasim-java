
import os
import zipfile
import bisect
from typing import Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

import matplotlib.pyplot as plt
import contextily as ctx
from pyproj import Transformer

transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
HEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "heights")

RECOMPUTE_ALTITUDE = False

# convert from swiss to global coordinates
def lv95_to_wgs84(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat

# Returns a ditionary mapping from (east, north) coordinate tuples to the corresponding .zip filename
def load_location_files():
    # Get all of the filenames from the .zip files in data/heights 
    # an example filename would be "data/heights/swissaltiregio_2465-1104_2056_5728.xyz.zip"
    # where the name can be broken down into:
    # swissaltiregio_<PREFIX_EAST>-<PREFIX_NORTH>_<...>_<...>.xyz.zip
    data_dir = 'data/heights'
    zip_filenames = [f for f in os.listdir(data_dir) if f.endswith('.zip')]
    
    # For each filename, PREFIX_EAST*1000 is the lowest east coordinate within that file
    # and PREFIX_NORTH*1000 is the lowest north coordinate within that file
    # We will store these in a list of tuples for easy access later
    location_files = []
    for zip_filename in zip_filenames:
        parts = zip_filename.split('_')
        if len(parts) < 2:
            continue
        prefix_part = parts[1]
        prefix_east_str, prefix_north_str = prefix_part.split('-')
        prefix_east = int(prefix_east_str) * 1000
        prefix_north = int(prefix_north_str) * 1000

        # convert to WGS84
        lon, lat = lv95_to_wgs84(prefix_east, prefix_north)

        location_files.append((lon, lat, zip_filename))
    
    # draw the map of switzerland with these locations using contextily for visualization
    # lons = [loc[0] for loc in location_files]
    # lats = [loc[1] for loc in location_files]
    # plt.figure(figsize=(10, 10))
    # plt.scatter(lons, lats, c='red', marker='o')
    # plt.title('Altitude Tile Locations in Switzerland')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # ctx.add_basemap(plt.gca(), crs='EPSG:4326')
    # plt.show()

    # map the (prefix_east, prefix_north) to the corresponding zip filename
    return location_files


def loctaion_files_to_grid(
    locations: Iterable[Tuple[float, float, str]]
) -> Tuple[List[float], List[List[Tuple[float, str]]]]:
    """
    Build a 2D grid for fast tile lookup via binary search.

    Returns a tuple (xs, grid) where:
      - xs is a sorted list of unique x minima.
      - grid[i] is a list of (y_min, filename) for that x, sorted by y_min.

    Given a coordinate (x, y), find i = bisect_right(xs, x) - 1,
    then j = bisect_right([y for y, _ in grid[i]], y) - 1 to locate the tile.
    """
    buckets = {}
    for lon, lat, filename in locations:
        buckets.setdefault(lon, []).append((lat, filename))

    xs = sorted(buckets.keys())
    grid = []
    for x in xs:
        ys = sorted(buckets[x], key=lambda item: item[0])
        grid.append(ys)

    return xs, grid

# This is used to lookup which files must be loaded
location_files = load_location_files()
file_grid = loctaion_files_to_grid(location_files)


def coordinate_to_grid(
    lon: float,
    lat: float,
    grid: Tuple[List[float], List[List[Tuple[float, str]]]] = file_grid,
) -> Optional[Tuple[int, int]]:
    """
    Locate the tile indices (x_idx, y_idx) for the given coordinate.

    Each tile entry stores the smallest x/y of that tile, so we use
    bisect_right to find the last tile whose min coordinate is <= the query.
    When the coordinate lies outside the known range, return the nearest tile.
    """
    xs, columns = grid
    if not xs or not columns:
        return None

    x_idx = bisect.bisect_right(xs, lon) - 1
    if x_idx < 0:
        x_idx = 0
    elif x_idx >= len(xs):
        x_idx = len(xs) - 1

    y_mins = [y for y, _ in columns[x_idx]]
    y_idx = bisect.bisect_right(y_mins, lat) - 1
    if y_idx < 0:
        y_idx = 0
    elif y_idx >= len(columns[x_idx]):
        y_idx = len(columns[x_idx]) - 1

    return x_idx, y_idx


def coordinates_to_grid(
    coords: Iterable[Tuple[float, float]],
    file_grid: Tuple[List[float], List[List[Tuple[float, str]]]] = file_grid,
) -> List[List[List[Tuple[float, float]]]]:
    """
    Bucket coordinates by their containing tile.

    Returns a 2D list mirroring the shape of `file_grid[1]`, where each
    bucket holds the coordinates that fall into that tile.
    """
    _, columns = file_grid
    buckets: List[List[List[Tuple[float, float]]]] = [
        [[] for _ in col] for col in columns
    ]

    for lon, lat in coords:
        if not np.isfinite(lon) or not np.isfinite(lat):
            continue
        idx = coordinate_to_grid(lon, lat, file_grid)
        if idx is None:
            continue
        x_idx, y_idx = idx
        buckets[x_idx][y_idx].append((lon, lat))

    return buckets


def _tile_inner_filename(zip_name: str) -> str:
    """Derive inner xyz filename from zip filename."""
    parts = zip_name.split("_")
    if len(parts) < 2:
        raise ValueError(f"Unexpected tile name {zip_name}")
    prefix_part = parts[1]
    return prefix_part.replace("-", "_") + ".xyz"


def _load_tile(zip_name: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load a tile's xyz data, returning (pts_wgs, zs).

    Tries to reuse an extracted .xyz file if present; otherwise reads from zip.
    """
    inner_name = _tile_inner_filename(zip_name)
    extracted_path = os.path.join(HEIGHTS_DIR, inner_name)
    if os.path.exists(extracted_path):
        df = pd.read_csv(
            extracted_path,
            sep=r"\s+",
            header=0,
            names=["x", "y", "z"],
            dtype=float,
            comment="#",
        )
    else:
        zip_path = os.path.join(HEIGHTS_DIR, zip_name)
        with zipfile.ZipFile(zip_path) as zf, zf.open(inner_name) as fh:
            df = pd.read_csv(
                fh,
                sep=r"\s+",
                header=0,
                names=["x", "y", "z"],
                dtype=float,
                comment="#",
            )

    xs = df["x"].to_numpy()
    ys = df["y"].to_numpy()
    zs = df["z"].to_numpy()
    lon, lat = lv95_to_wgs84(xs, ys)
    pts_wgs = np.column_stack((lon, lat))
    return pts_wgs, zs


def _neighbor_tiles(x_idx: int, y_idx: int) -> List[Tuple[int, int]]:
    """Return indices for the 3x3 neighborhood around (x_idx, y_idx)."""
    xs, columns = file_grid
    coords = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            xi = x_idx + dx
            yi = y_idx + dy
            if 0 <= xi < len(xs) and 0 <= yi < len(columns[xi]):
                coords.append((xi, yi))
    return coords


def process_df(df):
    """
    Add altitude columns (S_Z, Z_Z) by loading only needed tiles on demand.

    Coordinates are bucketed into the file grid, then for each bucket a KDTree
    is built from the tile plus its 8 neighbors to resolve nearest heights.
    """
    xs, columns = file_grid

    start_coords = df[["S_X", "S_Y"]].to_numpy()
    end_coords = df[["Z_X", "Z_Y"]].to_numpy()

    # Bucket coordinates using the prepared grid
    start_buckets = coordinates_to_grid(start_coords, file_grid)
    end_buckets = coordinates_to_grid(end_coords, file_grid)

    # Mirror grids but store dataframe row indices
    start_indices: List[List[List[int]]] = [[[] for _ in col] for col in columns]
    end_indices: List[List[List[int]]] = [[[] for _ in col] for col in columns]

    for pos, (lon, lat) in enumerate(start_coords):
        if not np.isfinite(lon) or not np.isfinite(lat):
            continue
        idx = coordinate_to_grid(lon, lat, file_grid)
        if idx is None:
            continue
        xi, yi = idx
        start_indices[xi][yi].append(pos)

    for pos, (lon, lat) in enumerate(end_coords):
        if not np.isfinite(lon) or not np.isfinite(lat):
            continue
        idx = coordinate_to_grid(lon, lat, file_grid)
        if idx is None:
            continue
        xi, yi = idx
        end_indices[xi][yi].append(pos)

    s_z = np.full(len(df), np.nan)
    z_z = np.full(len(df), np.nan)

    total_queries = sum(
        len(bucket) for column in start_buckets for bucket in column
    ) + sum(len(bucket) for column in end_buckets for bucket in column)
    processed = 0

    for x_idx in range(len(xs)):
        for y_idx in range(len(columns[x_idx])):
            bucket_points = start_buckets[x_idx][y_idx] + end_buckets[x_idx][y_idx]
            if not bucket_points:
                continue

            neighbor_coords = _neighbor_tiles(x_idx, y_idx)
            filenames = []
            for xi, yi in neighbor_coords:
                filenames.append(columns[xi][yi][1])
            filenames = list(dict.fromkeys(filenames))  # preserve order, remove dupes

            pts_list = []
            zs_list = []
            for fname in filenames:
                pts, zs_tile = _load_tile(fname)
                pts_list.append(pts)
                zs_list.append(zs_tile)

            pts_all = np.vstack(pts_list)
            zs_all = np.concatenate(zs_list)
            tree = cKDTree(pts_all)

            # Assign start points
            for pos, (lon, lat) in zip(start_indices[x_idx][y_idx], start_buckets[x_idx][y_idx]):
                _, idx = tree.query([lon, lat])
                s_z[pos] = zs_all[idx]

            # Assign end points
            for pos, (lon, lat) in zip(end_indices[x_idx][y_idx], end_buckets[x_idx][y_idx]):
                _, idx = tree.query([lon, lat])
                z_z[pos] = zs_all[idx]

            processed += len(bucket_points)
            if total_queries:
                progress = processed / total_queries * 100
                print(f"Processing altitude lookup… {progress:5.1f}% ({processed}/{total_queries})", end="\r", flush=True)

            # Explicitly drop large intermediates to ease memory pressure
            del tree, pts_all, zs_all

    df = df.copy()
    df["S_Z"] = pd.Series(s_z, index=df.index)
    df["Z_Z"] = pd.Series(z_z, index=df.index)
    if total_queries:
        print(f"Processing altitude lookup… 100.0% ({total_queries}/{total_queries})")
    return df
