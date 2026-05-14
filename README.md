# Who Turns to AI for Schoolwork?

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/PENDING.svg)](https://doi.org/PENDING)

Code, data, and paper for **"Who Turns to AI for Schoolwork? Socioeconomic
and Educational Predictors of Student Interest in the ChatGPT Era"** by
Dan Porder.

We link 2019 pre-ChatGPT regional conditions (American Community Survey,
Stanford Education Data Archive) to 2023-2025 student-intent AI search
interest at the U.S. Designated Market Area (DMA) level. The headline
finding: smaller, less affluent DMAs with lower degree attainment and
higher Black or Hispanic population shares show the highest subsequent
interest in AI for schoolwork — an inversion of the regional pattern
documented for general-purpose ChatGPT search interest.

A gradient boosting model on seven 2019 features explains about 42% of
the cross-region variance in 2023-2025 student AI-for-schoolwork search
interest under 5-fold cross-validation.

---

## How to cite

If you use the dataset or code, please cite both the paper and the
software release:

```bibtex
@article{porder2026schoolworkai,
  title  = {Who Turns to {AI} for Schoolwork? {S}ocioeconomic and
            Educational Predictors of Student Interest in the {ChatGPT} Era},
  author = {Porder, Dan},
  year   = {2026},
  note   = {arXiv: PENDING}
}

@software{porder2026schoolworkai_code,
  author    = {Porder, Dan},
  title     = {Who Turns to {AI} for Schoolwork? Code and data},
  year      = {2026},
  version   = {1.0.0},
  doi       = {PENDING},
  url       = {https://github.com/danporder/ai-schoolwork-search-interest}
}
```

GitHub auto-renders `CITATION.cff` as a "Cite this repository" button in
the right sidebar; clicking it copies a ready-to-paste citation.

---

## How to reproduce

There are two reproduction paths. Use the **cached-data** path to verify
the paper's exact numbers; use the **fresh-pull** path to regenerate the
pipeline from upstream sources (with the caveat that Google Trends is
non-deterministic — see [Reproducibility notes](#reproducibility-notes)).

### Cached-data path (recommended; ~30 seconds)

This regenerates every figure and table in the paper from the shipped
`data/processed/merged_dataset.csv`.

```bash
git clone https://github.com/danporder/ai-schoolwork-search-interest.git
cd ai-schoolwork-search-interest
python3 -m pip install -r requirements.txt

# Reproduce the paper's headline numbers
jupyter notebook notebooks/02_reproduce_paper_numbers.ipynb

# Or run the standalone scripts:
python3 paper/build_lowess_figure.py     # Figure 1 (LOWESS panels)
python3 paper/build_results_figures.py   # Figures 4 + 6 (cluster means, obs vs. predicted)
python3 paper/build_cluster_map.py       # Figure 2 (DMA cluster map; needs geopandas)
python3 paper/analysis_appendix.py       # Appendix B + C numbers
```

### Fresh-pull path (full pipeline; requires API credentials)

```bash
cp .env.example .env
# Edit .env with CENSUS_API_KEY, KAGGLE_USERNAME, KAGGLE_KEY

jupyter notebook notebooks/01_full_pipeline.ipynb
```

The full pipeline takes about 30-45 minutes depending on Google Trends
rate limiting.

### Compile the paper

```bash
make paper      # requires pdflatex + bibtex on PATH
```

---

## Repository structure

```
.
├── README.md                          # this file
├── LICENSE                            # MIT license for code
├── LICENSE-DATA                       # CC BY 4.0 for derived dataset
├── CITATION.cff                       # citation metadata
├── CHANGELOG.md                       # version history
├── requirements.txt                   # pinned Python dependencies
├── pyproject.toml                     # ruff/pytest config
├── Makefile                           # common entry points
├── .env.example                       # credential template (no real keys)
├── .gitignore
├── data/
│   ├── README.md                      # per-dataset provenance log
│   ├── processed/
│   │   └── merged_dataset.csv         # 209-DMA analytic dataset
│   └── raw/                           # cached upstream pulls (regenerated
│                                      #   by the full-pipeline notebook)
├── notebooks/
│   ├── 01_full_pipeline.ipynb         # end-to-end pull + analysis
│   └── 02_reproduce_paper_numbers.ipynb
├── paper/
│   ├── main.tex                       # paper source
│   ├── refs.bib
│   ├── figures/                       # all paper figures (PDF)
│   ├── build_lowess_figure.py         # Figure 1 (LOWESS panels)
│   ├── build_results_figures.py       # Figures 4 + 6 (cluster means, obs vs. predicted)
│   ├── build_cluster_map.py           # Figure 2 (DMA cluster map; needs geopandas)
│   └── analysis_appendix.py           # Appendix B + C reproducer
├── tests/
│   └── test_smoke.py                  # runs in CI
└── .github/
    └── workflows/
        └── ci.yml                     # GitHub Actions
```

---

## Reproducibility notes

This repository is designed around two related but distinct goals:

1. **Bit-for-bit reproducibility of the paper's numbers** from the shipped
   `data/processed/merged_dataset.csv`. Use
   `notebooks/02_reproduce_paper_numbers.ipynb`.

2. **Reproducibility of the data acquisition pipeline** from upstream
   sources. Use `notebooks/01_full_pipeline.ipynb`.

The second is harder because Google Trends is non-deterministic
([Hölzl, Keusch, & Sajons, 2025](https://doi.org/10.1016/j.ssresearch.2024.103099)):
the same DMA-level query at two different times can return materially
different normalized values. We follow the anchor-bank principle of
[West (2020)](https://doi.org/10.1145/3340531.3412075) — every keyword
batch shares the high-volume term "homework" as a calibration anchor — but
this only stabilizes *within-pull* comparisons, not *across-pull*. The
canonical pull date used for the paper is **2025-08-19**, recorded in
`data/README.md`.

If your fresh pull produces a different `merged_dataset.csv`, the
qualitative claims in the paper (smaller, less affluent, higher
Black-or-Hispanic-share regions show higher AI-for-schoolwork search
interest) should still hold; the exact $R^2$ and cluster means may shift.

---

## Data sources and licenses

| Source                                  | License                          | See                       |
|-----------------------------------------|----------------------------------|---------------------------|
| Derived `merged_dataset.csv`            | CC BY 4.0                        | `LICENSE-DATA`            |
| ACS 5-year estimates 2015-2019          | Public domain (U.S. gov.)        | `data/README.md`          |
| Stanford Education Data Archive 2024    | Per Reardon et al. terms         | `data/README.md`          |
| Google Trends search-interest values    | Google Trends ToS (cached only)  | `data/README.md`          |
| Kaggle DMA-FIPS crosswalk               | Per Kaggle dataset terms         | `data/README.md`          |
| Nielsen DMA GeoJSON                     | MIT                              | `data/README.md`          |

Full per-dataset provenance, including pull dates and exact API tables,
is documented in [`data/README.md`](data/README.md).

---

## Versioning

Releases are tagged on GitHub and snapshotted on Zenodo for permanent
DOI citation. The paper-of-record is the v1.0.0 release. See
[`CHANGELOG.md`](CHANGELOG.md) for the full version history.

---

## Acknowledgments

This work was originally produced as a coursework project; the open-source
release was prepared for arXiv submission and reviewer scrutiny.

---

## License

- Code: [MIT](LICENSE)
- Derived dataset: [CC BY 4.0](LICENSE-DATA)
- Upstream data sources retain their own licenses; see
  [`data/README.md`](data/README.md).
