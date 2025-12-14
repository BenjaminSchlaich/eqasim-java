"""
Create elevation maps for the canton of Zürich and (stub) for the Netherlands.

Zürich uses the Swissalti3D tiles already present under data/heights. The tiles
are addressed via the helper utilities in add_heights_big to stay consistent
with the altitude lookup logic used for microcensus processing.
"""

import os
import pathlib
import re
from typing import Dict, List, Tuple

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import Point
from shapely.prepared import prep

import add_heights_big

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
BOUNDARY_PATH = DATA_DIR / "Boundary" / "Zurich.shp"

MERCATOR = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
WGS_TO_LV95 = Transformer.from_crs("EPSG:4326", "EPSG:2056", always_xy=True)
HEIGHTS_DIR = add_heights_big.HEIGHTS_DIR

SUBSAMPLE = 5  # keep every 10th point (10 m -> 100 m) to speed up interpolation and reduce memory


def load_zurich_boundary() -> gpd.GeoDataFrame:
    """Boundary of the canton in WGS84."""
    boundary = gpd.read_file(BOUNDARY_PATH)
    return boundary.to_crs("EPSG:4326")


def _mask_polygon(lon_grid: np.ndarray, lat_grid: np.ndarray, polygon) -> np.ndarray:
    """Boolean mask keeping only cells within the given polygon."""
    prepared = prep(polygon)
    flat_lon = lon_grid.ravel()
    flat_lat = lat_grid.ravel()
    mask_flat = np.fromiter(
        (prepared.contains(Point(x, y)) for x, y in zip(flat_lon, flat_lat)),
        dtype=bool,
        count=len(flat_lon),
    )
    return mask_flat.reshape(lon_grid.shape)


def make_grid(boundary: gpd.GeoDataFrame, n_cols: int = 500, pad_ratio: float = 0.10) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a lon/lat grid covering the canton and mask it to the polygon.

    Grid resolution is driven by n_cols; the number of rows is scaled to the
    aspect ratio of the canton bounding box.
    """
    canton = boundary.unary_union
    minx, miny, maxx, maxy = canton.bounds

    # Expand the bounding box to leave a margin around the canton outline
    width = maxx - minx
    height = maxy - miny
    pad_x = width * pad_ratio * 0.5
    pad_y = height * pad_ratio * 0.5
    minx -= pad_x
    maxx += pad_x
    miny -= pad_y
    maxy += pad_y

    width = maxx - minx
    height = maxy - miny
    n_rows = max(50, int(n_cols * height / width))

    lon = np.linspace(minx, maxx, n_cols)
    lat = np.linspace(miny, maxy, n_rows)
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    mask = _mask_polygon(lon_grid, lat_grid, canton)
    return lon_grid, lat_grid, mask


def _load_location_files_lv95() -> List[Tuple[float, float, str]]:
    """
    Return list of (east_min, north_min, filename) from tile names in LV95.

    Supports both zipped swissalti files and extracted .xyz tiles.
    """
    entries: List[Tuple[float, float, str]] = []
    # Expect either swissaltiregio_2465-1104_...xyz.zip or extracted 2465000_1104000.xyz
    pattern_zip = re.compile(r"swissaltiregio_(\d+)-(\d+)_.*\.xyz\.zip$")
    pattern_xyz = re.compile(r"(\d+)_(\d+)\.xyz$")

    for fname in os.listdir(HEIGHTS_DIR):
        m_zip = pattern_zip.match(fname)
        m_xyz = pattern_xyz.match(fname)
        if m_zip:
            east = int(m_zip.group(1)) * 1000
            north = int(m_zip.group(2)) * 1000
        elif m_xyz:
            east = int(m_xyz.group(1))
            north = int(m_xyz.group(2))
        else:
            continue
        entries.append((east, north, fname))
    if not entries:
        raise FileNotFoundError(f"No altitude tiles found in {HEIGHTS_DIR}")
    return entries


def _location_files_to_grid_lv95(
    locations: List[Tuple[float, float, str]]
) -> Tuple[List[float], List[List[Tuple[float, str]]]]:
    """Build LV95-based grid for tile lookup."""
    buckets: Dict[float, List[Tuple[float, str]]] = {}
    for east, north, fname in locations:
        buckets.setdefault(east, []).append((north, fname))

    xs = sorted(buckets.keys())
    grid: List[List[Tuple[float, str]]] = []
    for x in xs:
        ys = sorted(buckets[x], key=lambda item: item[0])
        grid.append(ys)
    return xs, grid


LOCATION_FILES_LV95 = _load_location_files_lv95()
FILE_GRID_LV95 = _location_files_to_grid_lv95(LOCATION_FILES_LV95)


def sample_heights(lon_grid: np.ndarray, lat_grid: np.ndarray) -> np.ndarray:
    """
    Query altitudes for every grid point using tile-local KD-Trees.

    Grid points are bucketed by their containing tile; for each tile we build a
    KDTree using that tile plus its 8 neighbors (same logic as add_heights_big)
    and assign heights to the bucketed grid cells. This avoids a global
    interpolation solve while still keeping nearest-neighbour behavior.
    """
    east_grid, north_grid = WGS_TO_LV95.transform(lon_grid, lat_grid)
    coords = np.column_stack([east_grid.ravel(), north_grid.ravel()])

    buckets: Dict[Tuple[int, int], List[int]] = {}
    for idx, (east, north) in enumerate(coords):
        if not np.isfinite(east) or not np.isfinite(north):
            continue
        tile_idx = _coordinate_to_grid_lv95(east, north, FILE_GRID_LV95)
        if tile_idx is None:
            continue
        buckets.setdefault(tile_idx, []).append(idx)

    heights = np.full(len(coords), np.nan)
    total_buckets = len(buckets)
    if total_buckets == 0:
        raise RuntimeError("No grid cells fell into any altitude tile.")

    print(f"Found {total_buckets} tile buckets for Zürich grid.")

    for b_idx, (tile_idx, indices) in enumerate(buckets.items(), start=1):
        x_idx, y_idx = tile_idx
        neighbor_idxs = _neighbor_tiles_lv95(x_idx, y_idx, FILE_GRID_LV95)

        pts_list = []
        zs_list = []
        for xi, yi in neighbor_idxs:
            fname = FILE_GRID_LV95[1][xi][yi][1]
            pts_lv95, zs = _load_tile_lv95(fname)
            pts_list.append(pts_lv95[::SUBSAMPLE])
            zs_list.append(zs[::SUBSAMPLE])

        pts_all = np.vstack(pts_list)
        zs_all = np.concatenate(zs_list)

        tree = cKDTree(pts_all)
        _, nearest = tree.query(coords[indices])
        heights[indices] = zs_all[nearest]

        if b_idx == 1 or b_idx == total_buckets or b_idx % max(1, total_buckets // 10) == 0:
            print(f"  Processed tile bucket {b_idx}/{total_buckets}")

        del tree, pts_all, zs_all  # free memory early

    return heights.reshape(lon_grid.shape)


def _coordinate_to_grid_lv95(
    east: float,
    north: float,
    grid: Tuple[List[float], List[List[Tuple[float, str]]]] = FILE_GRID_LV95,
):
    """Locate LV95 tile index for a coordinate using east/north minima."""
    xs, columns = grid
    if not xs or not columns:
        return None

    import bisect

    x_idx = bisect.bisect_right(xs, east) - 1
    x_idx = min(max(x_idx, 0), len(xs) - 1)

    y_mins = [y for y, _ in columns[x_idx]]
    y_idx = bisect.bisect_right(y_mins, north) - 1
    y_idx = min(max(y_idx, 0), len(columns[x_idx]) - 1)
    return x_idx, y_idx


def _neighbor_tiles_lv95(x_idx: int, y_idx: int, grid) -> List[Tuple[int, int]]:
    """Return indices for the 3x3 neighborhood around (x_idx, y_idx) in LV95 grid."""
    xs, columns = grid
    coords = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            xi = x_idx + dx
            yi = y_idx + dy
            if 0 <= xi < len(xs) and 0 <= yi < len(columns[xi]):
                coords.append((xi, yi))
    return coords


def _load_tile_lv95(zip_name: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load raw LV95 coordinates and elevations from a tile (zipped or extracted).
    """
    inner_name = add_heights_big._tile_inner_filename(zip_name) if zip_name.endswith(".zip") else zip_name
    extracted_path = os.path.join(HEIGHTS_DIR, inner_name)

    if os.path.exists(extracted_path):
        df = add_heights_big.pd.read_csv(
            extracted_path,
            sep=r"\s+",
            header=0,
            names=["x", "y", "z"],
            dtype=float,
            comment="#",
        )
    else:
        zip_path = os.path.join(HEIGHTS_DIR, zip_name)
        with add_heights_big.zipfile.ZipFile(zip_path) as zf, zf.open(inner_name) as fh:
            df = add_heights_big.pd.read_csv(
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
    pts_lv95 = np.column_stack((xs, ys))
    return pts_lv95, zs


def plot_zurich_height_map(n_cols: int = 500):
    """Create and show the Zürich elevation map."""
    boundary = load_zurich_boundary()
    print("Building grid over canton extent…")
    lon_grid, lat_grid, mask = make_grid(boundary, n_cols=n_cols, pad_ratio=0.10)

    print("Sampling altitude grid for Zürich…")
    heights = sample_heights(lon_grid, lat_grid)
    heights[~mask] = np.nan

    mx, my = MERCATOR.transform(lon_grid, lat_grid)
    boundary_merc = boundary.to_crs("EPSG:3857")

    fig, ax = plt.subplots(figsize=(10, 9))
    pcm = ax.pcolormesh(mx, my, heights, cmap="terrain", shading="auto")
    boundary_merc.boundary.plot(ax=ax, color="black", linewidth=0.8, alpha=0.7)
    ax.set_facecolor("white")

    ax.set_title("Elevation map – Canton of Zürich")
    ax.set_xlabel("Web Mercator X")
    ax.set_ylabel("Web Mercator Y")
    fig.colorbar(pcm, ax=ax, label="Elevation (m a.s.l.)")
    fig.tight_layout()
    return fig, ax


def plot_netherlands_height_map(*, dem_path: pathlib.Path):
    """
    Placeholder for Netherlands elevation map.

    Provide a raster DEM for the Netherlands (e.g. AHN GeoTIFF) and feed its
    path here to draw a second map. This keeps the entry point ready while the
    required data source is decided.
    """
    raise NotImplementedError(
        f"No Netherlands DEM configured. Supply a GeoTIFF path via dem_path ({dem_path}) once the data is available."
    )


if __name__ == "__main__":
    plot_zurich_height_map()
    plt.show()
