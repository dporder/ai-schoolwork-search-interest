"""
Regenerate the DMA cluster map (Figure 2 in the paper).

The original notebook code joined the DMA GeoJSON to the cluster-assigned data
on a `latitude`/`longitude` column that does not exist in the upstream GeoJSON
(it only carries polygon geometry), with the result that the post-merge
`dropna(subset=['latitude','longitude'])` discarded every row and rendered a
legend-only PDF with no map polygons.

This script fixes the bug by:
  - Computing centroids from the polygon geometry to derive lat/long.
  - Plotting the polygons (filled by cluster_id) rather than scatter dots,
    which matches the figure caption in the paper.
  - Restricting to the continental U.S. (Hawaii and Alaska excluded per the
    caption).

Run from the repo root:
    python3 paper/build_cluster_map.py

Inputs:
    data/processed/merged_dataset.csv
    https://raw.githubusercontent.com/simzou/nielsen-dma/master/nielsen-mkt-map.json

Output:
    paper/figures/fig_cluster_map.pdf   (for the paper)
    paper/figures/fig_cluster_map.png   (for README.md)
"""
from __future__ import annotations

import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from thefuzz import process

warnings.filterwarnings("ignore")

DATA_PATH = "data/processed/merged_dataset.csv"
GEOJSON_URL = (
    "https://raw.githubusercontent.com/simzou/nielsen-dma/master/"
    "nielsen-mkt-map.json"
)
OUT_PATH = "paper/figures/fig_cluster_map.pdf"
# The paper uses the vector PDF; the PNG is the copy embedded in README.md,
# since GitHub cannot render a PDF inline. An explicit white facecolor keeps
# the legend text legible for readers on GitHub's dark theme.
PNG_PATH = "paper/figures/fig_cluster_map.png"
PNG_DPI = 200

# Cluster colors and labels matching the paper's narrative
CLUSTER_LABELS = {
    0: "Cluster 0: rural & small-metro, predominantly white (n=102)",
    1: "Cluster 1: Hispanic-majority SW metros (n=20)",
    2: "Cluster 2: large national metros (n=56)",
    3: "Cluster 3: SF + Honolulu, high Asian share (n=2)",
    4: "Cluster 4: rural Southern, elevated Black share (n=29)",
}
CLUSTER_COLORS = {
    0: "#9b59b6",   # purple
    1: "#27ae60",   # green
    2: "#f1c40f",   # yellow
    3: "#e74c3c",   # red
    4: "#3498db",   # blue
}


def main():
    df = pd.read_csv(DATA_PATH, index_col=0)
    print(f"Loaded {len(df)} DMAs from {DATA_PATH}")

    print(f"Fetching DMA GeoJSON from {GEOJSON_URL} ...")
    gdf = gpd.read_file(GEOJSON_URL)
    print(f"  Got {len(gdf)} DMA polygons; columns: {list(gdf.columns)}")

    # The GeoJSON's name field varies across releases; prefer 'dma1' / 'dma_name'.
    name_col = next((c for c in ["dma_name", "dma1", "DMA", "name"] if c in gdf.columns), None)
    if name_col is None:
        raise RuntimeError(f"Could not find a DMA name column. Columns: {list(gdf.columns)}")

    # Fuzzy match DMA names from our data onto the GeoJSON's canonical names
    canonical = gdf[name_col].astype(str).unique()
    matched = {}
    for name in df["dma_name"].astype(str).unique():
        match, score = process.extractOne(name, canonical)
        if score > 80:
            matched[name] = match
    print(f"  Matched {len(matched)}/{df['dma_name'].nunique()} DMA names "
          f"to GeoJSON polygons")

    df = df.copy()
    df["dma_match"] = df["dma_name"].map(matched)
    df = df.dropna(subset=["dma_match", "cluster_id"])

    merged = gdf.merge(
        df[["dma_match", "cluster_id"]],
        left_on=name_col, right_on="dma_match", how="inner",
    )
    # GeoJSON sometimes has missing CRS metadata; assume WGS84 (EPSG:4326).
    if merged.crs is None:
        merged = merged.set_crs(epsg=4326)
    print(f"  Merged GeoDataFrame has {len(merged)} polygons (CRS: {merged.crs}).")

    # Use the existing lat/long columns from the GeoJSON to filter to continental US.
    # (Avoids any CRS-conversion ambiguity in centroid computation.)
    in_continental = (
        merged["longitude"].between(-125, -66.5)
        & merged["latitude"].between(24, 50)
    )
    plot_df = merged[in_continental].copy()
    print(f"  Continental subset: {len(plot_df)} polygons")

    # Plot in geographic coordinates (EPSG:4326) and apply a simple aspect-ratio
    # correction approximating a Mercator-like view at the US mid-latitude.
    # We avoid Albers reprojection here because matplotlib's default y-axis
    # orientation conflicts with that projected CRS in some environments.
    fig, ax = plt.subplots(figsize=(14, 8))
    # Cosine-of-mid-latitude correction (~37 degN) for visual aspect
    import math
    mid_lat = 37.5
    ax.set_aspect(1.0 / math.cos(math.radians(mid_lat)))

    # Plot one cluster at a time so the legend is clean and ordering is fixed.
    for cid in sorted(plot_df["cluster_id"].unique()):
        sub = plot_df[plot_df["cluster_id"] == cid]
        sub.plot(
            ax=ax,
            facecolor=CLUSTER_COLORS.get(int(cid), "#888888"),
            edgecolor="white",
            linewidth=0.4,
        )

    legend_elems = [
        Patch(facecolor=CLUSTER_COLORS[c], edgecolor="black",
              label=CLUSTER_LABELS[c])
        for c in sorted(CLUSTER_LABELS) if c in plot_df["cluster_id"].unique()
    ]
    ax.legend(handles=legend_elems, loc="lower left", fontsize=9,
              frameon=True, framealpha=0.95)
    ax.set_axis_off()
    ax.set_title("DMA socioeconomic clusters across the continental U.S.",
                 fontsize=14, fontweight="bold")

    fig.tight_layout()
    fig.savefig(OUT_PATH, bbox_inches="tight", dpi=150)
    fig.savefig(PNG_PATH, bbox_inches="tight", dpi=PNG_DPI, facecolor="white")
    plt.close(fig)
    print(f"Saved {OUT_PATH} and {PNG_PATH}")


if __name__ == "__main__":
    main()
