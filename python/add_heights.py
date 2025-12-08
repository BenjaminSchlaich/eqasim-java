
# extend the mikrozensus files wege.csv and etappen.csv with altitude data

import pandas as pd
import numpy as np
import glob
from scipy.spatial import cKDTree
from pyproj import Transformer
import pathlib

RECOMPUTE_ALTITUDE = False

# ---------------------------
# 1. Load and convert altitude grid (LV95 → WGS84)
# ---------------------------

transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
HEIGHTS_DIR = (pathlib.Path(__file__).resolve().parents[1] / "data" / "heights").as_posix()


def lv95_to_wgs84(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat


def load_altitude_points(path=None):

    print("Loading altitude data…")

    if path is None:
        path = f"{HEIGHTS_DIR}/*.xyz"

    files = glob.glob(path)
    points_lv95 = []
    alts = []

    for f in files:
        # Files have a single header row ("x y z"); skip it and read numeric data only
        df = pd.read_csv(
            f,
            sep=r"\s+",
            header=0,
            names=["x", "y", "z"],
            dtype=float,
            comment="#",
        )
        points_lv95.append(df[["x", "y"]].values)
        alts.append(df["z"].values)

    if not points_lv95:
        raise FileNotFoundError(f"No altitude tiles found under {path}")

    pts = np.vstack(points_lv95)
    zs = np.hstack(alts)

    print("Converting altitude grid coordinates to WGS84…")
    pts_wgs = np.column_stack(lv95_to_wgs84(pts[:,0], pts[:,1]))

    print("Building KDTree…")
    tree = cKDTree(pts_wgs)

    return tree, zs

if RECOMPUTE_ALTITUDE:
    tree, zs = load_altitude_points()

# ---------------------------
# 2. Altitude lookup function
# ---------------------------

def lookup_altitude(lon, lat):
    dist, idx = tree.query([lon, lat])
    return zs[idx]

# Process a dataframe
def process_df(df):
    # Prepare S_Z and Z_Z columns
    df["S_Z"] = df.apply(lambda r: lookup_altitude(r["S_X"], r["S_Y"]) 
                         if np.isfinite(r["S_X"]) and np.isfinite(r["S_Y"]) else np.nan, axis=1)

    df["Z_Z"] = df.apply(lambda r: lookup_altitude(r["Z_X"], r["Z_Y"]) 
                         if np.isfinite(r["Z_X"]) and np.isfinite(r["Z_Y"]) else np.nan, axis=1)
    return df
