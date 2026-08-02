"""
Build the LOWESS figure (Figure 1 in the paper).

Resolves Notes 37-38 in the revision pass:
  - Note 37: Y-axis is now "AI-for-schoolwork search interest" instead of the
    raw column name "search_interest".
  - Note 38: Median household income is the first panel (most headline-worthy
    relationship), followed by bachelor-plus rate, graduate/professional rate,
    and Asian share. These are the four strongest-signal predictors mentioned
    in the Results text.

X axes carry human-readable labels with units. Asian share is plotted on a log
scale per the original figure's treatment of heavy right-skew.

Outputs version_2/figures/fig_lowess.pdf.

Run from repo root:
    python3 paper/build_lowess_figure.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.impute import SimpleImputer

DATA_PATH = "data/processed/merged_dataset.csv"
OUT_PATH = "paper/figures/fig_lowess.pdf"

# Order: median income first (most headline-worthy), then bachelor-plus rate,
# then graduate/professional rate. Population was previously included but its
# LOWESS curve was non-monotonic (an inverted-U shape driven by the eleven
# very-low-population zero-imputed DMAs at the left tail), so it was dropped
# from this figure for visual clarity. Population's negative association with
# search interest is reported in the Section 5.1 narrative and surfaced in the
# k-means typology and supervised model.
PANELS = [
    ("median_income", "Median household income (USD)", False),
    ("bach_plus_rate", "Adults with bachelor's degree or higher (%)", False),
    ("grad_prof_rate", "Adults with graduate or professional degree (%)", False),
]


def main():
    df = pd.read_csv(DATA_PATH, index_col=0)
    df = df[df["search_interest"].notna()]  # observed-only primary spec

    # Mean-impute predictors; restrict to observed outcomes (per Section 3 of paper)
    predictors = [p for p, _, _ in PANELS]
    needed = predictors + ["search_interest"]
    imp = SimpleImputer(strategy="mean")
    X = pd.DataFrame(imp.fit_transform(df[predictors]), columns=predictors,
                     index=df.index)
    y = df["search_interest"]
    plot_df = X.copy()
    plot_df["search_interest"] = y

    # 1x3 layout, slightly wider than tall, consistent margins
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))

    for ax, (col, xlabel, log_x) in zip(axes, PANELS):
        x = plot_df[col]
        x_plot = np.log10(x.replace(0, np.nan)) if log_x else x
        sns.regplot(
            x=x_plot,
            y=plot_df["search_interest"],
            ax=ax,
            lowess=True,
            scatter_kws={"alpha": 0.45, "s": 22, "color": "#3a6ea5"},
            line_kws={"color": "#c0392b", "linewidth": 2.2},
        )
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel("")
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(True, alpha=0.25, linestyle="--")
        # Format the income x-axis with thousands separators if not log
        if col == "median_income":
            ax.xaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"${int(v/1000)}k"))

    # Single shared y-label (Note 37 wording)
    axes[0].set_ylabel("AI-for-schoolwork search interest",
                       fontsize=11, fontweight="bold")

    fig.tight_layout()
    fig.savefig(OUT_PATH, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
