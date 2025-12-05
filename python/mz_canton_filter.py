"""
Filter microcensus Etappen and Wege to those fully inside the canton of Zürich.

Loads the Zürich boundary from data/Boundary/Zurich.shp, assumes coordinates
S_X/S_Y and Z_X/Z_Y are in WGS84 (lon/lat), and keeps rows where both start and
end points fall within the canton. Writes the results to:
- data/microcensus/etappen_zurich.csv
- data/microcensus/wege_zurich.csv
"""

import pathlib

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

import read_mz.mikrozensus as mz
import read_mz.trips as tr


BOUNDARY_PATH = "../data/Boundary/Zurich.shp"
ETAPPEN_PATH = "../data/microcensus/etappen.csv"
ETAPPEN_OUT = "../data/microcensus/etappen_zurich.csv"
WEGE_PATH = "../data/microcensus/wege.csv"
WEGE_OUT = "../data/microcensus/wege_zurich.csv"
MZ_PATH = "../data"
ENCODING = "latin1"

canton_geom = boundary = gpd.read_file(BOUNDARY_PATH).to_crs("EPSG:4326").geometry.union_all

def filter_location(df, canton_geom):
    """Return rows where start/end points fall within the canton."""
    start = gpd.GeoSeries(
        [Point(xy) for xy in zip(df["S_X"], df["S_Y"])], crs="EPSG:4326"
    )
    end = gpd.GeoSeries(
        [Point(xy) for xy in zip(df["Z_X"], df["Z_Y"])], crs="EPSG:4326"
    )
    mask = start.within(canton_geom) & end.within(canton_geom)
    return df[mask].copy()

def plot_age_distribution(df):
    # FILL IN CODE HERE
    return

def plot_map(df):
    required_cols = {"S_X", "S_Y", "Z_X", "Z_Y", "S_Z", "Z_Z"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"dataframe missing required columns: {sorted(missing)}")

    lon = pd.concat([df["S_X"], df["Z_X"]], ignore_index=True)
    lat = pd.concat([df["S_Y"], df["Z_Y"]], ignore_index=True)
    z = pd.concat(
        [pd.Series(df["S_Z"], name="z"), pd.Series(df["Z_Z"], name="z")],
        ignore_index=True,
    )

    points = pd.DataFrame({"x": lon, "y": lat, "z": z}).dropna(subset=["x", "y", "z"])
    if points.empty:
        raise ValueError(f"No complete altitude records found in {path}")

    # Project to Web Mercator for contextily basemap.
    merc_transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    mx, my = merc_transformer.transform(points["x"].values, points["y"].values)

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(
        mx,
        my,
        c=points["z"],
        cmap="coolwarm",
        s=8,
        alpha=0.7,
    )
    ctx.add_basemap(ax, crs="EPSG:3857")
    fig.colorbar(scatter, ax=ax, label="Height (m)")
    ax.set_title(f"Heights for {etappen} Etappen (start & end points)")
    ax.set_xlabel("Web Mercator X")
    ax.set_ylabel("Web Mercator Y")
    ax.set_aspect("equal")
    fig.tight_layout()
    plt.show()
    return

def filtered():
    pop = mz.main(MZ_PATH)                              # load the population

    pop = pop[pop["age"] >= 6]                          # filter out individuals younger than 6

    pop = pop[pop["day"] <= 5]                          # filter out persons which were queried for a weekend day

    wege, filterout_ids = tr.get_trips(MZ_PATH)         # load the wege

    wege = filter_location(wege, canton_geom)           # filter for only wege with start&end inside zürich

    pop = pop[~pop["person_id"].isin(filterout_ids)]    # filter out individuals with stupid trip stats according to Milos

    wege = pd.merge(wege, pop)                          # keep only wege of filtered population

    return wege

def main():


    wege = filtered()

    print(f"The remaining number of wege is {wege}")


if __name__ == "__main__":
    main()
