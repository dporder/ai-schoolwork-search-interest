"""
Regenerate Appendix E (Table tab:robust): the tuned gradient boosting model
under four analytic samples, each re-tuned within its own sample and scored
with 10 repetitions of 5-fold cross-validation.

The four samples correspond to the two treatments of missing outcomes
discussed in Section 3.1, plus two influence checks:

    1. Observed outcomes only (the primary analytic sample, n=198)
    2. Unobserved outcomes coded at zero (n=209)
    3. Smallest 20% of DMAs by population dropped (low-volume Trends check)
    4. Outcome winsorized at its 99th percentile (extreme-value check)

Run from the repo root:
    python3 paper/robustness_appendix.py

Inputs:
    data/processed/merged_dataset.csv

Dependencies: pandas, numpy, scikit-learn.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import (GridSearchCV, KFold, RepeatedKFold,
                                     cross_val_score)

DATA_PATH = "data/processed/merged_dataset.csv"
TARGET = "search_interest"
SUPERVISED = ["median_income", "bach_plus_rate", "population", "pct_hispanic",
              "pct_nh_black", "pct_nh_asian", "score_all_ela"]
PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "learning_rate": [0.01, 0.1, 0.2],
    "max_depth": [3, 5, 7],
    "min_samples_split": [2, 5],
}
SEED = 42
N_REPEATS = 10


def evaluate(frame: pd.DataFrame, zero_code: bool, label: str) -> dict:
    """Re-tune and score the GBM on one analytic sample."""
    y = frame[TARGET].fillna(0).values if zero_code else frame[TARGET].values
    X = frame[SUPERVISED].fillna(frame[SUPERVISED].mean()).values

    grid = GridSearchCV(
        GradientBoostingRegressor(random_state=SEED), PARAM_GRID,
        cv=KFold(n_splits=5, shuffle=True, random_state=SEED),
        scoring="r2", n_jobs=-1,
    ).fit(X, y)

    scores = cross_val_score(
        grid.best_estimator_, X, y,
        cv=RepeatedKFold(n_splits=5, n_repeats=N_REPEATS, random_state=SEED),
        scoring="r2", n_jobs=-1,
    )
    per_repeat = scores.reshape(N_REPEATS, 5).mean(axis=1)
    return {
        "label": label, "n": len(frame),
        "mean": scores.mean(), "sd": scores.std(),
        "lo": per_repeat.min(), "hi": per_repeat.max(),
        "params": grid.best_params_,
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    observed = df[df[TARGET].notna()].copy()

    rows = [
        evaluate(observed, False, "Observed outcomes only (primary)"),
        evaluate(df, True, "Unobserved outcomes coded at zero"),
    ]

    cut = observed["population"].quantile(0.20)
    rows.append(evaluate(observed[observed["population"] > cut], False,
                         "Smallest 20% of DMAs dropped"))

    wins = observed.copy()
    cap = wins[TARGET].quantile(0.99)
    wins[TARGET] = wins[TARGET].clip(upper=cap)
    rows.append(evaluate(wins, False,
                         "Outcome winsorized at 99th percentile"))

    print("\n=== Appendix E (Table tab:robust) ===")
    print(f"{'Analytic sample':40s} {'N':>5s} {'R2 mean (SD)':>16s} {'per-rep range':>16s}")
    for r in rows:
        print(f"{r['label']:40s} {r['n']:5d} "
              f"{r['mean']:8.3f} ({r['sd']:.3f}) {r['lo']:7.3f}--{r['hi']:.3f}")

    print("\nRe-tuned hyperparameters per sample:")
    for r in rows:
        print(f"  {r['label']:40s} {r['params']}")

    print(f"\nWinsorization cap (99th pct of observed outcomes): {cap:.1f}")
    print(f"Population cut for the smallest-20% check: {cut:,.0f}")


if __name__ == "__main__":
    main()
