# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — unreleased

Revisions made while preparing the paper for submission. **Numbers reported in
this release differ from v1.0.0.** Anyone comparing against the v1.0.0 Zenodo
record should read this section first.

### Changed

- **Primary analytic sample is now the 198 DMAs with observed search interest**,
  rather than all 209 with the 11 unobserved outcomes coded at zero. Google
  documents `NaN` as meaning either "unavailable" or "below an unspecified
  reporting threshold" and does not distinguish the two, so neither treatment is
  assumption-free. The paper now reports both throughout (see Section 3.1 and
  Appendix E) and every substantive conclusion is the same under each.
- **Headline model performance is now reported under repeated cross-validation**
  (10 repetitions of 5-fold) rather than a single 5-fold split. The single-split
  figure was unstable at this sample size: per-repetition means range from 0.29
  to 0.47. Headline tuned-GBM R-squared is **0.39 (SD 0.11)**, replacing the
  0.42 reported in v1.0.0.
- Table 1 cluster means now average over observed outcomes only. Cluster 0 reads
  45.2 (was 41.7) and Cluster 2 reads 19.7 (was 18.7). **The cluster ordering is
  unchanged: C4 > C0 > C1 > C2 > C3.**
- Table 2 regenerated on the primary sample under repeated cross-validation.
- Appendix C variance inflation factors recomputed on n=198. All remain below 5.
- Figures 1, 4, and 6 regenerated. Figure 6 no longer annotates an R-squared,
  since it shows a single cross-validation pass as a fit-shape diagnostic while
  the headline is a repeated-CV figure.
- The OLS, Lasso, and bootstrap-Lasso stages previously mean-imputed the
  *outcome* variable as an unintended side effect of imputing predictors and
  outcome in one call. They now use the same observed-only sample as every other
  stage. Coefficient signs, significance, and Lasso selection are unaffected.
- Abstract, introduction, and conclusion reworded so that racial composition is
  described at the level of the regional cluster typology rather than as an
  independent predictor, which is what the data support.
- Corrected the published repository URL throughout (`danporder` to `dporder`).
- **Author name normalised to "Dan Porder" everywhere.** `paper/main.tex`,
  `CITATION.cff`, and the README BibTeX entries variously carried "Daniel
  Clopton Porder"; all now read "Dan Porder", matching `LICENSE`,
  `pyproject.toml`, and the v1.0.0 Zenodo record.
- Figure build scripts now write each figure twice: the vector PDF used by
  `paper/main.tex` and a 200-DPI PNG on a white background for README.md,
  since GitHub cannot render PDFs inline.
- README versioning section no longer names a release. It explains Zenodo's
  concept DOI (always resolves to latest) versus version DOI (a frozen
  snapshot) and which to cite for what. The previous text claimed the
  paper-of-record was v1.0.0, which stopped being true once this release
  changed the reported numbers.
- Bibliography corrections: `daepp2025` now cites the peer-reviewed ICWSM 2025
  version; `darlinghammond2024` now cites the AERA Open article rather than its
  data deposit, with the co-author's name corrected; plus fixes to
  `wimberley2002`, `simzou`, `zhang2025`, and `nielsen2025`.

### Added

- `paper/robustness_appendix.py` and `make robustness`, regenerating Appendix E:
  the tuned model under four analytic samples, each re-tuned within its own
  sample and scored with repeated cross-validation.
- Appendix E to the paper, reporting both missing-outcome treatments plus a
  small-DMA check and a winsorization check.
- `vonhippel2007` to the bibliography, supporting the complete-case rationale.
- `.zenodo.json`, which Zenodo reads in preference to `CITATION.cff` when
  archiving a release, pinning the author name and project metadata on the
  deposited record.
- `scripts/release.sh` and `make release VERSION=x.y.z`, which stamps the
  version into `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`, and the README
  BibTeX entry, then commits and tags. It does not push: Zenodo mints the DOI
  when the GitHub Release is published and DOIs cannot be withdrawn, so
  metadata has to be correct before that point.
- PNG copies of Figures 1, 2, 4, and 6 under `paper/figures/`, for README
  display.

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
    - `paper/build_results_figures.py` — Figures 4 and 6.
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

[1.1.0]: https://github.com/dporder/ai-schoolwork-search-interest/releases/tag/v1.1.0
[1.0.0]: https://github.com/dporder/ai-schoolwork-search-interest/releases/tag/v1.0.0
