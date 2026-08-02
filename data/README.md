# Data provenance

This directory contains the analytic dataset used in
"Who Turns to AI for Schoolwork?" plus pointers and license notes for
upstream sources. The headline numbers in the paper are reproduced from
`processed/merged_dataset.csv`.

## Directory layout

```
data/
├── processed/
│   └── merged_dataset.csv   # 209 DMAs, ACS+SEDA+Trends merged, cluster IDs
└── raw/                     # cached upstream pulls (excluded from git release;
                             #   regenerate with notebooks/01_full_pipeline.ipynb)
```

## processed/merged_dataset.csv

- **Rows:** 209 (one per U.S. Designated Market Area covered by the analysis)
- **Columns:** 33 (DMA name, 9 ACS demographic/economic covariates, 4
  racial-composition shares, search-interest outcome, 14 SEDA achievement
  scores, plus engineered rates and the k-means cluster assignment)
- **Target column:** `search_interest` — anchor-normalized mean across 73
  student-intent Google Trends keywords, 2023-01-01 through 2025-07-31, with
  11 low-population DMAs carrying `NaN` and treated as effectively zero in
  the headline supervised model (see paper §3.1).
- **Cluster column:** `cluster_id` — k-means assignment to one of five
  clusters using the seven clustering features defined in paper §4.2.
- **License:** CC BY 4.0 (see `LICENSE-DATA` at the repo root).
- **Citation:** Porder, D. (2026). Who Turns to AI for Schoolwork? Derived
  dataset. https://github.com/dporder/ai-schoolwork-search-interest

## Upstream sources

### 1. Google Trends — student-intent search interest

- **Source:** Google Trends API via the `pytrends` package (v4.9.2).
- **Pull date:** 2025-08-19.
- **Time window:** 2023-01-01 through 2025-07-31.
- **Geography:** Designated Market Area (DMA).
- **Query design:** 73 student-intent keywords distributed across 19
  five-keyword batches, each batch including the high-volume term
  "homework" as a shared anchor for cross-batch normalization. The full
  batch list is reproduced verbatim in Appendix A of the paper.
- **License / TOS:** Subject to Google Trends Terms of Service. We cache
  derived normalized values; we do not claim a redistribution license over
  raw query archives.
- **Reproducibility caveat:** Google Trends is non-deterministic; the same
  query at a later time can return materially different values
  ([Hölzl, Keusch, & Sajons, 2025](https://doi.org/10.1016/j.ssresearch.2024.103099)).
  The values shipped in `processed/merged_dataset.csv` are the canonical
  values used in the paper. To refresh from the live API, see
  `notebooks/01_full_pipeline.ipynb` and expect the numbers to change.

### 2. American Community Survey 5-year estimates (2015-2019)

- **Source:** U.S. Census Bureau API.
- **Pull date:** 2025-08-19.
- **Tables used:**
    - `B01003` (total population)
    - `B03002` (Hispanic-origin x race composition)
    - `B15003` (educational attainment)
    - `B17001` (poverty status)
    - `B19013` (median household income)
- **Geography:** county.
- **License:** Public domain (U.S. government work).
- **Note:** the ACS 5-year product pools data collected from 2015 through
  2019 into a single estimate published in 2020. It is not an average of
  five separate annual datasets but a single 2015-2019 estimate centered
  on conditions immediately before the COVID and ChatGPT shocks. See paper
  §3.2.

### 3. Stanford Education Data Archive (SEDA)

- **Source:** Reardon et al., Stanford Education Data Archive (Version SEDA
  2024). https://purl.stanford.edu/pt329xg7054
- **Pull date:** 2025-08-19.
- **Subset used:** 2018-2019 school year, county level, overall and
  grade-level mean ELA and math scores.
- **License:** Per the Reardon et al. authors' terms at the SEDA distribution
  page above.
- **Note:** the choice of 2019 is *not* because SEDA was discontinued
  (newer SEDA releases exist). It is because 2018-2019 is the last fully
  pre-COVID, pre-ChatGPT school year, and therefore the cleanest baseline
  for measuring structural educational conditions before the disruptions
  and intervention this study analyzes. See paper §3.3 and the Limitations
  section.

### 4. DMA / FIPS county crosswalk

- **Source:** Kapastor, "Google Trends County-DMA-FIPS mapping" on Kaggle.
  https://www.kaggle.com/datasets/kapastor/google-trends-countydma-mapping
- **Pull date:** 2025-08-19.
- **License:** Per the Kaggle dataset's posted terms.
- **Use:** maps each U.S. county FIPS code to its containing Nielsen DMA,
  enabling county-level ACS and SEDA covariates to be aggregated to the
  DMA level for merge with the Google Trends outcome. See paper §3.4.

### 5. Nielsen DMA GeoJSON

- **Source:** simzou/nielsen-dma on GitHub.
  https://github.com/simzou/nielsen-dma
- **Pull date:** 2025-08-19 (fetched at notebook runtime; not cached locally).
- **License:** MIT, per the upstream repository.
- **Use:** geographic plotting of cluster assignments (paper Figure 2).

## Refreshing the raw data

The `raw/` directory is intentionally empty in this release. The data
pipeline in `notebooks/01_full_pipeline.ipynb` will regenerate every
intermediate artifact when run with the appropriate API credentials (see
`.env.example`).

Expected raw artifacts after a fresh run:

| Filename                        | Source         | Approx. size |
|---------------------------------|----------------|--------------|
| `search_interest_data.csv`      | Google Trends  |  ~700 KB     |
| `census_data.csv`               | ACS API        |  ~250 KB     |
| `seda_county_2019.csv`          | SEDA           |  ~1 MB       |
| `dma_fips_crosswalk.csv`        | Kaggle dataset |  ~150 KB     |

If you re-fetch and find that your `merged_dataset.csv` differs from the
shipped version on the search-interest column, that is expected
(non-deterministic Trends API). The qualitative paper claims should still
hold; the exact $R^2$ and cluster means may shift.
