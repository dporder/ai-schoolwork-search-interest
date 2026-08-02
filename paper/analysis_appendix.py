"""
Reproduces the appendix-table numbers in the paper:

  - Appendix B (Table tab:clusterverify): state distributions, Southern share,
    and racial-share means per cluster.
  - Appendix C (Table tab:vif): variance inflation factors for the seven
    supervised features.
  - Section 5.3 cluster characterization: population statistics per cluster
    and the share of cluster-member DMAs below conventional metro-size
    thresholds (used to support the Cluster 0 'rural and small-metropolitan'
    label).

Run from the repo root:
    python3 paper/analysis_appendix.py

Inputs:  merged_dataset.csv
Outputs: prints the numbers; no files written.
Dependencies: pandas, numpy, statsmodels.
"""
import warnings

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")

DATA_PATH = "data/processed/merged_dataset.csv"

SUPERVISED = [
    "median_income", "bach_plus_rate", "population", "pct_hispanic",
    "pct_nh_black", "pct_nh_asian", "score_all_ela",
]
RACE_COLS = ["pct_hispanic", "pct_nh_white", "pct_nh_black", "pct_nh_asian"]
SOUTH = {"AL", "AR", "FL", "GA", "KY", "LA", "MS", "NC",
         "SC", "TN", "VA", "WV", "TX", "OK"}


def get_state(name):
    parts = str(name).strip().split()
    return parts[-1] if parts and len(parts[-1]) == 2 and parts[-1].isupper() else ""


def main():
    df = pd.read_csv(DATA_PATH, index_col=0)
    print(f"Loaded {len(df)} DMAs from {DATA_PATH}")

    # Cluster geography
    df["state"] = df["dma_name"].apply(get_state)
    print("\n=== Cluster geography (Appendix B, Table tab:clusterverify) ===")
    for cid in sorted(df["cluster_id"].dropna().unique()):
        sub = df[df["cluster_id"] == cid]
        states = sub["state"].value_counts()
        south_share = sub["state"].isin(SOUTH).mean()
        print(f"\nCluster {int(cid)} (n={len(sub)}):")
        print(f"  Top states: {dict(states.head(7))}")
        print(f"  Southern share: {south_share:.0%}")
        print("  Racial means: " + ", ".join(
            f"{c}={sub[c].mean():.1f}" for c in RACE_COLS))

    # Cluster population + sub-metro thresholds (Section 5.3 narrative)
    print("\n=== Cluster population + sub-metro thresholds ===")
    print(f"National DMA medians: median pop = {df['population'].median():,.0f}, "
          f"mean pop = {df['population'].mean():,.0f}")
    for cid in sorted(df["cluster_id"].dropna().unique()):
        sub = df[df["cluster_id"] == cid]
        print(f"\nCluster {int(cid)} (n={len(sub)}):")
        print(f"  median pop = {sub['population'].median():,.0f}")
        print(f"  mean pop   = {sub['population'].mean():,.0f}")
        for thresh, label in [(500_000, "<500K"),
                              (1_000_000, "<1M"),
                              (2_500_000, "<2.5M")]:
            share = (sub["population"] < thresh).mean()
            print(f"  {label}: {share:.0%}")

    # VIF (Appendix C)
    print("\n=== VIF (Appendix C, Table tab:vif) ===")
    # Computed on the primary analytic sample (observed outcomes only, n=198),
    # matching the supervised model in Section 5.4.
    X = df[df["search_interest"].notna()][SUPERVISED].copy()
    X = X.fillna(X.mean())
    Xz = (X - X.mean()) / X.std()
    vifs = pd.DataFrame({
        "feature": SUPERVISED,
        "VIF": [variance_inflation_factor(Xz.values, i)
                for i in range(len(SUPERVISED))],
    }).sort_values("VIF", ascending=False)
    print(vifs.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
