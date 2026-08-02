"""
Regenerate Figures 4 (mean cluster interest) and 6 (observed vs predicted)
so that they are consistent with Table 1 and Table 2 in the paper.

Why these figures needed regenerating:

  - Figure 4 (`fig_cluster_interest.pdf`) plots mean interest per cluster
    over the 198 DMAs with observed search interest, matching the primary
    analytic sample defined in Section 3.1. Table 1's N column reports
    cluster membership over all 209 DMAs, because the clustering uses
    predictors only; the caption states this explicitly.

  - Figure 6 (`fig_obs_pred.pdf`) was originally produced from a default
    (untuned) Gradient Boosting fit. This script rebuilds it from the tuned
    headline model on the observed-only sample. It is a single 5-fold pass
    shown as a diagnostic of fit shape, so no R^2 is annotated on it; the
    headline R^2 in Table 2 is a repeated-cross-validation figure.

Run from the repo root:
    python3 paper/build_results_figures.py

Inputs:
    data/processed/merged_dataset.csv

Outputs (each written as a vector PDF for the paper and a PNG for the web):
    paper/figures/fig_cluster_interest.{pdf,png}
    paper/figures/fig_obs_pred.{pdf,png}

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

# Every figure is written twice: a vector PDF for the paper, and a raster PNG
# for the web (GitHub cannot render a PDF inline). The explicit white facecolor
# keeps axis text legible for readers on GitHub's dark theme.
PNG_DPI = 200

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

    Uses the observed-only primary specification so that cluster Ns match
    Table 1.
    """
    rng = np.random.default_rng(42)
    n_boot = 2000

    # Headline outcome: observed values only
    df = df[df[TARGET].notna()]  # observed-only primary spec
    y = df[TARGET].values
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
    fig.savefig("paper/figures/fig_cluster_interest.png", bbox_inches="tight",
                dpi=PNG_DPI, facecolor="white")
    plt.close(fig)
    print("Wrote paper/figures/fig_cluster_interest.{pdf,png}")
    for cid, m, l, h, n in zip(cids, means, lo, hi, ns):
        print(f"  C{cid}: N={n}, mean={m:.2f}, 95% CI [{l:.2f}, {h:.2f}]")


def build_obs_pred(df: pd.DataFrame) -> None:
    """Figure 6: observed vs cross-validated predicted from tuned GBM.

    A single 5-fold pass (random_state=42), shown as a diagnostic of fit shape.
    The headline R^2 is reported in Table 2 under repeated cross-validation and
    is deliberately not annotated on this figure.
    """
    df = df[df[TARGET].notna()]  # observed-only primary spec
    imp = SimpleImputer(strategy="mean")
    X = imp.fit_transform(df[SUPERVISED])
    y = df[TARGET].values

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
    _ = (r2_mean, r2_sd)  # reported in Table 2, not annotated here
    ax.set_title("Gradient Boost: observed vs. cross-validated prediction",
                 fontsize=12)
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig("paper/figures/fig_obs_pred.pdf", bbox_inches="tight")
    fig.savefig("paper/figures/fig_obs_pred.png", bbox_inches="tight",
                dpi=PNG_DPI, facecolor="white")
    plt.close(fig)
    print("Wrote paper/figures/fig_obs_pred.{pdf,png}")


def main() -> None:
    df = pd.read_csv(DATA_PATH, index_col=0)
    print(f"Loaded {len(df)} DMAs from {DATA_PATH}\n")
    print("=== Figure 4 (cluster interest, N matches Table 1) ===")
    build_cluster_interest(df)
    print("\n=== Figure 6 (observed vs predicted, diagnostic, single 5-fold pass) ===")
    build_obs_pred(df)


if __name__ == "__main__":
    main()
