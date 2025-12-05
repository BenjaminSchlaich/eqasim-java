
# extend the mikrozensus files wege.csv and etappen.csv with altitude data

import pandas as pd
import numpy as np
import glob
from scipy.spatial import cKDTree
from pyproj import Transformer

# ---------------------------
# 1. Load and convert altitude grid (LV95 → WGS84)
# ---------------------------

def load_altitude_points(path="data/heights/*.xyz"):
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

    pts = np.vstack(points_lv95)
    zs = np.hstack(alts)

    return pts, zs


transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)

def lv95_to_wgs84(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat


print("Loading altitude data…")
pts_lv95, alts = load_altitude_points()

print("Converting altitude grid coordinates to WGS84…")
pts_wgs = np.column_stack(lv95_to_wgs84(pts_lv95[:,0], pts_lv95[:,1]))

print("Building KDTree…")
tree = cKDTree(pts_wgs)


# ---------------------------
# 2. Altitude lookup function
# ---------------------------

def lookup_altitude(lon, lat):
    dist, idx = tree.query([lon, lat])
    return alts[idx]


# ---------------------------
# 3. Process a microcensus CSV (wege or etappen)
# ---------------------------

def process_file(path):
    print(f"\nProcessing {path} …")
    # Microcensus CSV uses Latin-1 (contains umlauts); specify encoding to avoid decode errors
    df = pd.read_csv(path, encoding="latin1")

    # Prepare S_Z and Z_Z columns
    df["S_Z"] = df.apply(lambda r: lookup_altitude(r["S_X"], r["S_Y"]) 
                         if np.isfinite(r["S_X"]) and np.isfinite(r["S_Y"]) else np.nan, axis=1)

    df["Z_Z"] = df.apply(lambda r: lookup_altitude(r["Z_X"], r["Z_Y"]) 
                         if np.isfinite(r["Z_X"]) and np.isfinite(r["Z_Y"]) else np.nan, axis=1)

    out = path.replace(".csv", "_alt.csv")
    df.to_csv(out, index=False)
    print(f"Saved → {out}")


# ---------------------------
# 4. Run for both datasets
# ---------------------------

process_file("data/microcensus/wege_zurich.csv")
process_file("data/microcensus/etappen_zurich.csv")

print("\nDone.")
