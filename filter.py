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


BOUNDARY_PATH = "data/Boundary/Zurich.shp"
ETAPPEN_PATH = "data/microcensus/etappen.csv"
ETAPPEN_OUT = "data/microcensus/etappen_zurich.csv"
WEGE_PATH = "data/microcensus/wege.csv"
WEGE_OUT = "data/microcensus/wege_zurich.csv"
ENCODING = "latin1"


def load_canton_geometry():
    boundary = gpd.read_file(BOUNDARY_PATH).to_crs("EPSG:4326")
    return boundary.geometry.unary_union


def filter_dataframe(df, canton_geom):
    """Return rows where start/end points fall within the canton."""
    start = gpd.GeoSeries(
        [Point(xy) for xy in zip(df["S_X"], df["S_Y"])], crs="EPSG:4326"
    )
    end = gpd.GeoSeries(
        [Point(xy) for xy in zip(df["Z_X"], df["Z_Y"])], crs="EPSG:4326"
    )
    mask = start.within(canton_geom) & end.within(canton_geom)
    return df[mask].copy()


def filter_etappen(canton_geom):
    etappen = pd.read_csv(ETAPPEN_PATH, encoding=ENCODING)
    filtered = filter_dataframe(etappen, canton_geom)
    output = pathlib.Path(ETAPPEN_OUT)
    output.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output, index=False, encoding=ENCODING)
    print(f"Etappen: kept {len(filtered)}/{len(etappen)} rows → {output}")


def filter_wege(canton_geom):
    wege = pd.read_csv(WEGE_PATH, encoding=ENCODING)
    filtered = filter_dataframe(wege, canton_geom)
    output = pathlib.Path(WEGE_OUT)
    output.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output, index=False, encoding=ENCODING)
    print(f"Wege: kept {len(filtered)}/{len(wege)} rows → {output}")


def main():
    canton_geom = load_canton_geometry()

    filter_wege(canton_geom)
    filter_etappen(canton_geom)


if __name__ == "__main__":
    main()
