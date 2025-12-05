import matplotlib.pyplot as plt
import pandas as pd
import contextily as ctx
from pyproj import Transformer


def main():
    path = "data/microcensus/etappen_zurich_alt.csv"
    etappen = pd.read_csv(path, encoding="latin1")

    required_cols = {"S_X", "S_Y", "Z_X", "Z_Y", "S_Z", "Z_Z"}
    missing = required_cols.difference(etappen.columns)
    if missing:
        raise ValueError(f"{path} missing required columns: {sorted(missing)}")

    sample_size = min(1000, len(etappen))
    sampled = etappen #etappen.sample(n=sample_size, random_state=42)

    lon = pd.concat([sampled["S_X"], sampled["Z_X"]], ignore_index=True)
    lat = pd.concat([sampled["S_Y"], sampled["Z_Y"]], ignore_index=True)
    z = pd.concat(
        [pd.Series(sampled["S_Z"], name="z"), pd.Series(sampled["Z_Z"], name="z")],
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
    ax.set_title(f"Heights for {sample_size} Random Etappen (start & end points)")
    ax.set_xlabel("Web Mercator X")
    ax.set_ylabel("Web Mercator Y")
    ax.set_aspect("equal")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
