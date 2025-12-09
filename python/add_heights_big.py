
import os
import zipfile
import bisect
from typing import Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import contextily as ctx
from pyproj import Transformer

transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)

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
        idx = coordinate_to_grid(lon, lat, file_grid)
        if idx is None:
            continue
        x_idx, y_idx = idx
        buckets[x_idx][y_idx].append((lon, lat))

    return buckets
