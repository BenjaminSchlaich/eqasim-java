"""
Plot the average absolute slope (relative to 4-neighbour cells) for the canton of Zürich.

Reuses the height sampling utilities from plot_height_map.py to stay consistent
with tile loading and masking.
"""

import matplotlib.pyplot as plt
import numpy as np

from plot_height_map import (
    MERCATOR,
    load_zurich_boundary,
    make_grid,
    sample_heights,
)


def compute_neighbor_slope(heights: np.ndarray) -> np.ndarray:
    """
    Average absolute elevation difference to the four direct neighbours.
    Edges are set to NaN.
    """
    # Differences to neighbours (wraps are masked out later)
    diff_up = np.abs(heights - np.roll(heights, 1, axis=0))
    diff_down = np.abs(heights - np.roll(heights, -1, axis=0))
    diff_left = np.abs(heights - np.roll(heights, 1, axis=1))
    diff_right = np.abs(heights - np.roll(heights, -1, axis=1))

    stacked = np.stack([diff_up, diff_down, diff_left, diff_right], axis=0)
    slope = np.nanmean(stacked, axis=0)

    # Remove wrapped edges: no valid neighbour outside the grid
    slope[[0, -1], :] = np.nan
    slope[:, [0, -1]] = np.nan
    return slope


def plot_zurich_slope_map(n_cols: int = 500):
    """Create and show the Zürich slope map."""
    boundary = load_zurich_boundary()
    lon_grid, lat_grid, mask = make_grid(boundary, n_cols=n_cols, pad_ratio=0.10)

    heights = sample_heights(lon_grid, lat_grid)
    heights[~mask] = np.nan

    slope = compute_neighbor_slope(heights)
    slope[~mask] = np.nan

    mx, my = MERCATOR.transform(lon_grid, lat_grid)
    boundary_merc = boundary.to_crs("EPSG:3857")

    fig, ax = plt.subplots(figsize=(10, 9))
    pcm = ax.pcolormesh(mx, my, slope, cmap="viridis", shading="auto")
    boundary_merc.boundary.plot(ax=ax, color="black", linewidth=0.8, alpha=0.7)
    ax.set_facecolor("white")

    ax.set_title("Average absolute slope – Canton of Zürich")
    ax.set_xlabel("Web Mercator X")
    ax.set_ylabel("Web Mercator Y")
    fig.colorbar(pcm, ax=ax, label="Mean |Δz| to 4-neighbour cells (m)")
    fig.tight_layout()
    return fig, ax


if __name__ == "__main__":
    plot_zurich_slope_map()
    plt.show()
