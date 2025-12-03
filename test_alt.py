import sys

import pandas as pd


def main():
    # Load both datasets (wege not used further, but opened as requested)
    wege = pd.read_csv("data/microcensus/wege_alt.csv", encoding="latin1")
    etappen = pd.read_csv("data/microcensus/etappen_alt.csv", encoding="latin1")

    idx = 100
    if idx >= len(etappen):
        print(f"Index {idx} out of range for etappen_alt.csv (len={len(etappen)})")
        sys.exit(1)

    row = etappen.iloc[idx]

    start = (float(row["S_X"]), float(row["S_Y"]), float(row.get("S_Z", float("nan"))))
    end = (float(row["Z_X"]), float(row["Z_Y"]), float(row.get("Z_Z", float("nan"))))

    print(f"Etappe #{idx}")
    print(f"  Start (x, y, z): {start[0]} {start[1]} {start[2]}")
    print(f"  End   (x, y, z): {end[0]} {end[1]} {end[2]}")


if __name__ == "__main__":
    main()
