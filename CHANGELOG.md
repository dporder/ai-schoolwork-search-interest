# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-10

Initial public release accompanying the paper "Who Turns to AI for Schoolwork?"

### Included

- Derived DMA-level analytic dataset (`data/processed/merged_dataset.csv`,
  209 DMAs with linked 2019 ACS, 2018-2019 SEDA, and 2023-2025 Google Trends
  search-interest values).
- Full pipeline notebook (`notebooks/01_full_pipeline.ipynb`) reproducing the
  data acquisition, feature selection, k-means typology, and supervised
  prediction stages of the paper.
- Reproduce-paper-numbers notebook (`notebooks/02_reproduce_paper_numbers.ipynb`)
  that loads `merged_dataset.csv` and regenerates Tables 1, 2, 3, and 4 plus
  Figures 1 through 6.
- Paper source (`paper/main.tex`, `paper/refs.bib`) and figures.
- Reproducible standalone scripts:
    - `paper/build_lowess_figure.py` — Figure 1 (LOWESS panels).
    - `paper/analysis_appendix.py` — Appendix B and C numbers (cluster
      geography, VIF).
- Per-dataset provenance log (`data/README.md`).
- Pinned Python dependencies (`requirements.txt`).
- MIT license for code; CC BY 4.0 for the derived dataset.

### Notes on reproducibility

- Google Trends search interest values are non-deterministic across re-pulls.
  The `data/processed/merged_dataset.csv` shipped with this release captures
  the values used for every number reported in the paper.
- Census API and Kaggle credentials are not included. Refresh-from-source
  workflows in `notebooks/01_full_pipeline.ipynb` require the user to set
  `CENSUS_API_KEY`, `KAGGLE_USERNAME`, and `KAGGLE_KEY` environment variables;
  see `.env.example`.

[1.0.0]: https://github.com/danporder/ai-schoolwork-search-interest/releases/tag/v1.0.0
