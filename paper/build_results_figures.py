"""
Regenerate Figures 4 (mean cluster interest) and 6 (observed vs predicted)
so that they are consistent with Table 1 and Table 2 in the paper.

Why these figures needed regenerating:

  - Figure 4 (`fig_cluster_interest.pdf`) was originally produced from the
    198 DMAs with observed search interest only, while Table 1 reports
    cluster sizes (N=102, 20, 56, 2, 29) over all 209 DMAs. This script
    rebuilds the figure with the headline convention from Section 3.1: the
    11 below-threshold DMAs are imputed at zero, so cluster Ns and means
    in Figure 4 now match Table 1 exactly.

  - Figure 6 (`fig_obs_pred.pdf`) was originally produced from a default
    (untuned) Gradient Boosting fit (R^2 ~ 0.398), while Table 2 in the
    paper reports the tuned headline model (R^2 ~ 0.417). This script
    rebuilds the figure from the tuned model so the in-figure R^2 matches
    Table 2.

Run from the repo root:
    python3 paper/build_results_figures.py

Inputs:
    data/processed/merged_dataset.csv

Outputs:
    paper/figures/fig_cluster_interest.pdf
    paper/figures/fig_obs_pred.pdf

Dependencies: pandas, numpy, scikit-learn, matplotlib.
"""
from __future__ import annotations

import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV, KFold, cross_val_predict, cross_val_score

warnings.filterwarnings("ignore")

DATA_PATH = "data/processed/merged_dataset.csv"

SUPERVISED = [
    "median_income", "bach_plus_rate", "population", "pct_hispanic",
    "pct_nh_black", "pct_nh_asian", "score_all_ela",
]
TARGET = "search_interest"

# Color and label conventions kept consistent with the cluster map
CLUSTER_COLORS = {
    0: "#9b59b6",   # purple
    1: "#27ae60",   # green
    2: "#f1c40f",   # yellow
    3: "#e74c3c",   # red
    4: "#3498db",   # blue
}
CLUSTER_LABELS = {
    0: "C0: rural &\nsmall-metro\n(N=102)",
    1: "C1: Hispanic\nSW metros\n(N=20)",
    2: "C2: large\nnational metros\n(N=56)",
    3: "C3: SF +\nHonolulu\n(N=2)",
    4: "C4: rural\nSouthern\n(N=29)",
}


def build_cluster_interest(df: pd.DataFrame) -> None:
    """Figure 4: mean cluster search interest with bootstrap 95% CIs.

    Uses the headline zero-imputation convention so that cluster Ns match
    Table 1.
    """
    rng = np.random.default_rng(42)
    n_boot = 2000

    # Headline outcome with zero-imputed NaNs
    y = df[TARGET].fillna(0).values
    cluster = df["cluster_id"].astype(int).values

    means, lo, hi, ns = [], [], [], []
    for cid in sorted(np.unique(cluster)):
        sub = y[cluster == cid]
        ns.append(len(sub))
        means.append(sub.mean())
        if len(sub) >= 2:
            boot = rng.choice(sub, size=(n_boot, len(sub)), replace=True).mean(axis=1)
            lo.append(np.percentile(boot, 2.5))
            hi.append(np.percentile(boot, 97.5))
        else:
            # Cluster 3 has only 2 DMAs; show a degenerate single-value range.
            lo.append(sub.min())
            hi.append(sub.max())

    fig, ax = plt.subplots(figsize=(10, 5))
    cids = sorted(CLUSTER_COLORS.keys())
    bar_pos = np.arange(len(cids))
    colors = [CLUSTER_COLORS[c] for c in cids]
    yerr = np.array([[m - l for m, l in zip(means, lo)],
                     [h - m for m, h in zip(means, hi)]])

    bars = ax.bar(bar_pos, means, color=colors, edgecolor="black",
                  linewidth=0.6, alpha=0.85)
    ax.errorbar(bar_pos, means, yerr=yerr, fmt="none",
                ecolor="black", capsize=4, linewidth=1.0)

    ax.set_xticks(bar_pos)
    ax.set_xticklabels([CLUSTER_LABELS[c] for c in cids], fontsize=9)
    ax.set_ylabel("Mean AI-for-schoolwork search interest (2023--2025)",
                  fontsize=10)
    ax.set_ylim(0, max(hi) * 1.15)
    ax.grid(True, axis="y", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig("paper/figures/fig_cluster_interest.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Wrote paper/figures/fig_cluster_interest.pdf")
    for cid, m, l, h, n in zip(cids, means, lo, hi, ns):
        print(f"  C{cid}: N={n}, mean={m:.2f}, 95% CI [{l:.2f}, {h:.2f}]")


def build_obs_pred(df: pd.DataFrame) -> None:
    """Figure 6: observed vs cross-validated predicted from tuned GBM.

    Uses the same outer 5-fold CV protocol as Table 2 so the in-figure R^2
    matches Table 2's headline value.
    """
    imp = SimpleImputer(strategy="mean")
    X = imp.fit_transform(df[SUPERVISED])
    y = df[TARGET].fillna(0).values

    param_grid = {
        "n_estimators": [100, 200, 300],
        "learning_rate": [0.01, 0.1, 0.2],
        "max_depth": [3, 5, 7],
        "min_samples_split": [2, 5],
    }
    inner = KFold(n_splits=5, shuffle=True, random_state=42)
    outer = KFold(n_splits=5, shuffle=True, random_state=42)

    grid = GridSearchCV(GradientBoostingRegressor(random_state=42),
                        param_grid, cv=inner, scoring="r2", n_jobs=-1)
    grid.fit(X, y)
    best = grid.best_estimator_
    print(f"Best params: {grid.best_params_}")

    r2_scores = cross_val_score(best, X, y, cv=outer, scoring="r2", n_jobs=-1)
    r2_mean, r2_sd = r2_scores.mean(), r2_scores.std()
    y_pred = cross_val_predict(best, X, y, cv=outer, n_jobs=-1)
    print(f"R^2 = {r2_mean:.3f} +/- {r2_sd:.3f}")

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.scatter(y, y_pred, alpha=0.55, s=22, color="#3a6ea5",
               edgecolor="white", linewidth=0.4)
    lims = [min(y.min(), y_pred.min()) - 5, max(y.max(), y_pred.max()) + 5]
    ax.plot(lims, lims, "k--", linewidth=1.0)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Observed search interest", fontsize=11)
    ax.set_ylabel("Predicted search interest (5-fold CV)", fontsize=11)
    ax.set_title(rf"Gradient Boost: CV $R^2 = {r2_mean:.3f} \pm {r2_sd:.3f}$",
                 fontsize=12)
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig("paper/figures/fig_obs_pred.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Wrote paper/figures/fig_obs_pred.pdf")


def main() -> None:
    df = pd.read_csv(DATA_PATH, index_col=0)
    print(f"Loaded {len(df)} DMAs from {DATA_PATH}\n")
    print("=== Figure 4 (cluster interest, N matches Table 1) ===")
    build_cluster_interest(df)
    print("\n=== Figure 6 (observed vs predicted, R^2 matches Table 2) ===")
    build_obs_pred(df)


if __name__ == "__main__":
    main()
