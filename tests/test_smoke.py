"""
Smoke tests for the analytic dataset and headline numbers.

These exist primarily to (1) catch regressions if `data/processed/merged_dataset.csv`
is accidentally modified, and (2) give CI something concrete to verify on push.
They are deliberately narrow: they confirm shape, the qualitative cluster
ordering, and a couple of pre-computed numbers.

Run with:
    python3 -m pytest tests/ -v
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "merged_dataset.csv"


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    assert DATA_PATH.exists(), f"Missing data file: {DATA_PATH}"
    return pd.read_csv(DATA_PATH, index_col=0)


def test_shape(df):
    assert len(df) == 209, "Expected 209 DMAs in the analytic dataset"


def test_required_columns_present(df):
    required = {
        "dma_name",
        "median_income",
        "bach_plus_rate",
        "population",
        "pct_hispanic",
        "pct_nh_black",
        "pct_nh_asian",
        "score_all_ela",
        "search_interest",
        "cluster_id",
    }
    missing = required - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def test_search_interest_missingness(df):
    """11 low-population DMAs are zero-imputed; the rest have observed values."""
    n_nan = df["search_interest"].isna().sum()
    assert n_nan == 11, f"Expected 11 NaN search_interest values, got {n_nan}"


def test_five_clusters(df):
    cluster_counts = df["cluster_id"].value_counts().sort_index().to_dict()
    assert cluster_counts == {0: 102, 1: 20, 2: 56, 3: 2, 4: 29}, (
        f"Cluster sizes do not match paper Section 5.3: {cluster_counts}"
    )


def test_cluster_interest_ordering(df):
    """Lower-income / lower-attainment clusters should have higher mean interest.

    The paper's headline claim is that Cluster 4 > Cluster 0 > Cluster 1
    > Cluster 2 > Cluster 3 by mean search_interest.
    """
    means = df.groupby("cluster_id")["search_interest"].mean()
    assert means[4] > means[0] > means[1] > means[2] > means[3], (
        f"Cluster mean ordering violates paper claim: {means.to_dict()}"
    )


def test_cluster_4_southern_concentration(df):
    """Paper Section 5.3 / Appendix B: Cluster 4 is 97% Southern-state."""
    south = {"AL", "AR", "FL", "GA", "KY", "LA", "MS", "NC",
             "SC", "TN", "VA", "WV", "TX", "OK"}

    def state_of(name):
        parts = str(name).strip().split()
        return parts[-1] if parts and len(parts[-1]) == 2 and parts[-1].isupper() else ""

    sub = df[df["cluster_id"] == 4].copy()
    sub["state"] = sub["dma_name"].apply(state_of)
    south_share = sub["state"].isin(south).mean()
    assert south_share >= 0.95, (
        f"Cluster 4 Southern share dropped below 95%: {south_share:.0%}"
    )


def test_cluster_0_rurality(df):
    """Cluster 0 should have ~74% of DMAs below 1M population (paper Section 5.3)."""
    sub = df[df["cluster_id"] == 0]
    share_under_1m = (sub["population"] < 1_000_000).mean()
    assert 0.70 <= share_under_1m <= 0.78, (
        f"Cluster 0 sub-1M share outside expected range: {share_under_1m:.0%}"
    )
