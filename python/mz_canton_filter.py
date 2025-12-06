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
import matplotlib.pyplot as plt
import numpy as np
import contextily as ctx
from shapely.geometry import Point
from pyproj import Transformer

import read_mz.mikrozensus as mz
import read_mz.trips as tr

import add_heights


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
BOUNDARY_PATH = DATA_DIR / "Boundary" / "Zurich.shp"
ETAPPEN_PATH = DATA_DIR / "microcensus" / "etappen.csv"
ETAPPEN_OUT = DATA_DIR / "microcensus" / "etappen_zurich.csv"
WEGE_PATH = DATA_DIR / "microcensus" / "wege.csv"
WEGE_OUT = DATA_DIR / "microcensus" / "wege_zurich.csv"
MZ_PATH = DATA_DIR
ENCODING = "latin1"

RECOMPUTE_FILTER = False

boundary = gpd.read_file(BOUNDARY_PATH).to_crs("EPSG:4326").geometry
canton_geom = boundary.union_all()  # merge into a single polygon for spatial tests

def filter_location(df):
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
    required_cols = {"age", "sex"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"dataframe missing required columns: {sorted(missing)}")

    weight_col = "person_weight" if "person_weight" in df.columns else None
    max_age = int(df["age"].max())
    bin_edges = list(range(0, max_age + 10, 5))
    bin_labels = [f"{start}-{end - 1}" for start, end in zip(bin_edges[:-1], bin_edges[1:])]
    df = df.copy()
    df["age_group"] = pd.cut(
        df["age"], bins=bin_edges, right=False, labels=bin_labels, include_lowest=True
    )

    sex_labels = {0: "Male", 1: "Female"}
    df["sex_label"] = df["sex"].map(sex_labels).fillna("Other")

    if weight_col:
        grouped = df.groupby(["age_group", "sex_label"])[weight_col].sum()
    else:
        grouped = df.groupby(["age_group", "sex_label"]).size()

    pyramid = grouped.unstack(fill_value=0).reindex(bin_labels)
    if pyramid.empty:
        raise ValueError("No data available to plot age distribution.")

    male = -pyramid.get("Male", pd.Series(index=pyramid.index, dtype=float)).values
    female = pyramid.get("Female", pd.Series(index=pyramid.index, dtype=float)).values

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(pyramid.index, male, color="#4C78A8", label="Male", alpha=0.8)
    ax.barh(pyramid.index, female, color="#F58518", label="Female", alpha=0.8)

    max_population = max(np.abs(male).max(), np.abs(female).max())
    ax.set_xlim(-1.1 * max_population, 1.1 * max_population)
    ax.set_xlabel("Population (weighted)" if weight_col else "Population")
    ax.set_ylabel("Age group (years)")
    ax.set_title("Age-sex pyramid for filtered microcensus sample")
    ax.legend(loc="upper right")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_map(etappen):
    required_cols = {"S_X", "S_Y", "Z_X", "Z_Y", "S_Z", "Z_Z"}
    missing = required_cols.difference(etappen.columns)
    if missing:
        raise ValueError(f"etappen missing required columns: {sorted(missing)}")

    lon = pd.concat([etappen["S_X"], etappen["Z_X"]], ignore_index=True)
    lat = pd.concat([etappen["S_Y"], etappen["Z_Y"]], ignore_index=True)
    z = pd.concat(
        [pd.Series(etappen["S_Z"], name="z"), pd.Series(etappen["Z_Z"], name="z")],
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

def filter():

    if(RECOMPUTE_FILTER):
        print("refiltering the microzensus wege...")

        pop = mz.main(MZ_PATH)                              # load the population

        print(f"filtering age")
        pop = pop[pop["age"] >= 6]                          # filter out individuals younger than 6

        wege, filterout_ids = tr.get_trips(MZ_PATH)         # load the wege

        print(f"filtering location")
        wege = filter_location(wege)                        # filter for only wege with start&end inside zürich

        print(f"filtering milos' stuff")
        pop = pop[~pop["person_id"].isin(filterout_ids)]    # filter out individuals with stupid trip stats according to Milos

        wege = pd.merge(wege, pop)                          # keep only wege of filtered population

        print(f"The remaining number of wege is {wege}")

        print(f"saving filtered wege to csv")
        output_path = MZ_PATH / "microcensus" / "filtered.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wege.to_csv(output_path, index=False, encoding=ENCODING)
        
    else:
        print("loading filtered microzensus wege")
        wege = pd.read_csv(MZ_PATH / "microcensus" / "filtered.csv", encoding=ENCODING)

    return wege

def height():

    if(add_heights.RECOMPUTE_ALTITUDE):
        df = filter()

        print("adding height data to wege...")
        df = add_heights.process_df(df)

        print("saving wege with altitude to csv")
        output_path = MZ_PATH / "microcensus" / "heights.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding=ENCODING)
        
    else:
        df = pd.read_csv(MZ_PATH / "microcensus" / "heights.csv", encoding=ENCODING)

    return df


def main():

    wege = height()

    plot_age_distribution(wege)

    plot_map(wege)


if __name__ == "__main__":
    main()
