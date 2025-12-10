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
import read_mz.utils as util

import add_heights
import add_heights_big


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
BOUNDARY_PATH = DATA_DIR / "Boundary" / "Zurich.shp"
ETAPPEN_PATH = DATA_DIR / "microcensus" / "etappen.csv"
ETAPPEN_OUT = DATA_DIR / "microcensus" / "etappen_zurich.csv"
WEGE_PATH = DATA_DIR / "microcensus" / "wege.csv"
WEGE_OUT = DATA_DIR / "microcensus" / "wege_zurich.csv"
MZ_PATH = DATA_DIR
ENCODING = "latin1"

# should the trips be filtered using load_filtered_zurich() again or just reloaded from the stored .csv?
RECOMPUTE_FILTER = True

boundary = gpd.read_file(BOUNDARY_PATH).to_crs("EPSG:4326").geometry
canton_geom = boundary.union_all()  # merge into a single polygon for spatial tests

# filter out for only trips that start&end within zürich
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

# Plot the age demographic of the data frame nicely
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

# Plot trips with height data on a map
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

# Returns the filtered trips inside Zürich joined with persons. Filtered by demographics, location and sanity checks.
def load_filtered_zurich():

    if(RECOMPUTE_FILTER):
        print("refiltering the microzensus wege...")

        pop = mz.main(MZ_PATH)                              # load the population

        print(f"filtering age")
        pop = pop[pop["age"] >= 6]                          # filter out individuals younger than 6

        wege, filterout_ids = tr.get_trips(MZ_PATH)         # load the wege

        print(f"filtering location (only zürich)")
        wege = filter_location(wege)                        # filter for only wege with start&end inside zürich

        print(f"filtering milos' stuff")
        pop = pop[~pop["person_id"].isin(filterout_ids)]    # filter out individuals with stupid trip stats according to Milos

        wege = pd.merge(wege, pop, on="person_id")          # keep only wege of filtered population

        print(f"The remaining number of wege is {wege}")

        print(f"saving filtered wege to csv")
        output_path = MZ_PATH / "microcensus" / "filtered_zurich.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wege.to_csv(output_path, index=False, encoding=ENCODING)
        
    else:
        print("loading filtered microzensus wege")
        wege = pd.read_csv(MZ_PATH / "microcensus" / "filtered_zurich.csv", encoding=ENCODING)

    return wege

# Returns the dataframe from filtered_zurich() with added z-coordinates
def with_height_zurich():

    if(add_heights.RECOMPUTE_ALTITUDE):
        df = load_filtered_zurich()

        print("adding height data to wege...")
        df = add_heights.process_df(df)

        print("saving wege with altitude to csv")
        output_path = MZ_PATH / "microcensus" / "heights_zurich.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding=ENCODING)
        
    else:
        df = pd.read_csv(MZ_PATH / "microcensus" / "heights_zurich.csv", encoding=ENCODING)

    return df

# Computes the weighted median...
def weighted_median(values, weights):
    sorter = np.argsort(values)
    v_sorted = np.array(values)[sorter]
    w_sorted = np.array(weights)[sorter]
    cum_weights = np.cumsum(w_sorted)
    cutoff = 0.5 * w_sorted.sum()
    return v_sorted[np.searchsorted(cum_weights, cutoff)]

# Computes the beta for bike utility.
def compute_beta(wege):

    util.require_columns(wege, {"S_Z", "Z_Z", "mode", "person_weight", "crowfly_distance"})

    slope = (wege["Z_Z"] - wege["S_Z"]) / (wege["crowfly_distance"])
    weights = wege["person_weight"]

    # bike trips only filter:
    is_bike = wege["mode"] == "bike"

    # compute the median slope of bike trips: 
    med_slope = weighted_median(slope[is_bike], weights[is_bike])

    # category 1: the indices of trips with less than or equal to bike median slope
    cat_1 = slope <= med_slope
    # total weight of category 1:
    cat_1_w = weights[cat_1].sum()

    # category 2: the indices of trips with more than bike median slope
    cat_2 = slope > med_slope
    # total weight of category 2:
    cat_2_w = weights[cat_2].sum()

    # the weighted sum of bike trips in category 1
    bike_s1 = weights[is_bike & cat_1].sum()
    # the weighted sum of bike trips in category 2
    bike_s2 = weights[is_bike & cat_2].sum()

    # mean slope of trips in category 1
    mean_slope_1 = (slope[cat_1] * weights[cat_1]).sum() / cat_1_w
    # mean slope of trips in category 2
    mean_slope_2 = (slope[cat_2] * weights[cat_2]).sum() / cat_2_w

    # the weighted sum of all trips in category 1
    all_s1 = weights[cat_1].sum()
    # the bike mode share for trips in category 1
    m1 =  bike_s1 / all_s1

    # the weighted sum of all trips in category 2
    all_s2 = weights[cat_2].sum()
    # the bike mode share for trips in category 2
    m2 =  bike_s2 / all_s2

    # the increase/decrease in mode share relative to m1 per slope
    beta = ((m2 - m1) / m1) / (mean_slope_2 - mean_slope_1) # (mean_slope_bike_2 - mean_slope_bike_1)
    
    print(f"Mode share goes from {m1} to {m2} for changing the mean slope from {mean_slope_1} to {mean_slope_2}.")

    return beta

# Plot mode shares per slope bin nicely
def plot_slope_shares(wege):
    """Plot bike mode share for minimum slope thresholds from 0.0 to 0.1."""
    util.require_columns(wege, {"S_Z", "Z_Z", "mode", "person_weight", "crowfly_distance"})

    slope = (wege["Z_Z"] - wege["S_Z"]) / (wege["crowfly_distance"])
    weights = wege["person_weight"]
    is_bike = wege["mode"] == "bike"

    thresholds = np.arange(-0.20, 0.20, 0.02)
    shares = []

    for t in thresholds:
        mask = (slope >= t) & (slope <= t + 0.01)
        total_w = weights[mask].sum()
        bike_w = weights[mask & is_bike].sum()
        share = bike_w / total_w if total_w > 0 else np.nan
        shares.append(share)

    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, shares, marker="o")
    plt.xlabel("Minimum slope")
    plt.ylabel("Bike mode share")
    plt.title("Bike mode share by minimum slope threshold")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

# Returns the filtered trips with joined persons. Filtered by demographics, location and sanity checks.
def load_filtered_switzerland():

    if(RECOMPUTE_FILTER):
        print("refiltering the microzensus wege...")

        pop = mz.main(MZ_PATH)                              # load the population

        print(f"filtering age")
        pop = pop[pop["age"] >= 6]                          # filter out individuals younger than 6

        wege, filterout_ids = tr.get_trips(MZ_PATH)         # load the wege

        print(f"filtering milos' stuff")
        pop = pop[~pop["person_id"].isin(filterout_ids)]    # filter out individuals with stupid trip stats according to Milos

        wege = pd.merge(wege, pop, on="person_id")          # keep only wege of filtered population

        print(f"The remaining number of wege is {wege}")

        print(f"saving filtered wege to csv")
        output_path = MZ_PATH / "microcensus" / "filtered_switzerland.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wege.to_csv(output_path, index=False, encoding=ENCODING)
        
    else:
        print("loading filtered microzensus wege")
        wege = pd.read_csv(MZ_PATH / "microcensus" / "filtered_switzerland.csv", encoding=ENCODING)

    return wege

# Returns the dataframe from filtered_zurich() with added z-coordinates
def with_height_switzerland():

    if(add_heights_big.RECOMPUTE_ALTITUDE):
        df = load_filtered_switzerland()

        print("adding height data to wege...")
        df = add_heights_big.process_df(df)

        print("saving wege with altitude to csv")
        output_path = MZ_PATH / "microcensus" / "heights_switzerland.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding=ENCODING)
        
    else:
        df = pd.read_csv(MZ_PATH / "microcensus" / "heights_switzerland.csv", encoding=ENCODING)

    return df

def main():

    wege = with_height_switzerland()

    # plot_age_distribution(wege)
    plot_map(wege)

    plot_slope_shares(wege)

    beta = compute_beta(wege)
    print(f"The computed beta is {beta}")


if __name__ == "__main__":
    main()
