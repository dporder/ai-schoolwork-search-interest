# Who Turns to AI for Schoolwork?

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20185969.svg)](https://doi.org/10.5281/zenodo.20185969)
[![Release](https://img.shields.io/github/v/release/dporder/ai-schoolwork-search-interest)](https://github.com/dporder/ai-schoolwork-search-interest/releases/latest)

Code, data, and paper for **"Who Turns to AI for Schoolwork? Socioeconomic and Educational Predictors of Student Interest in the ChatGPT Era"** by Dan Porder.

This research links 2019 pre-ChatGPT regional conditions (American Community Survey, Stanford Education Data Archive) to 2023-2025 student-intent AI search interest at the U.S. Designated Market Area (DMA) level. Counterintuitively, the results show that smaller, less affluent DMAs with lower degree attainment had the highest interest in AI for schoolwork following ChatGPT's release, an inversion of the regional pattern documented for general-purpose AI chatbot search interest. Regionally, the highest-interest cluster is a non-metropolitan Southern group with markedly elevated Black population shares.

[![Student AI-for-schoolwork search interest plotted against median household income, bachelor's-or-higher attainment, and graduate-or-professional attainment. All three LOWESS curves slope downward, so interest is highest in the lowest-income, lowest-attainment DMAs.](paper/figures/fig_lowess.png)](paper/figures/fig_lowess.pdf)

*Figure 1 — AI-for-schoolwork search interest declines as regional income and degree attainment rise. Click through for the vector PDF.*

[![Map of the continental U.S. shaded by DMA socioeconomic cluster, showing five clusters: rural and small-metro predominantly white, Hispanic-majority Southwestern metros, large national metros, San Francisco plus Honolulu, and a contiguous rural Southern block with elevated Black population share.](paper/figures/fig_cluster_map.png)](paper/figures/fig_cluster_map.pdf)

*Figure 2 — The five DMA socioeconomic clusters. Cluster 4 (blue), the rural Southern group, shows the highest mean search interest.*

A gradient boosting model on seven 2019 features explains about 39% of the cross-region variance in 2023-2025 student AI-for-schoolwork search interest under repeated cross-validation, estimated on the 198 DMAs with observed search interest.

---

## How to cite

If you use the dataset or code, please cite both the paper and the software release:

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
  version   = {1.1.0},
  doi       = {10.5281/zenodo.20185969},
  url       = {https://github.com/dporder/ai-schoolwork-search-interest}
}
```

GitHub auto-renders `CITATION.cff` as a "Cite this repository" button in the right sidebar, and clicking it copies a ready-to-paste citation.

---

## How to reproduce

There are two reproduction paths:
1. **Cached-data** path *(recommended)*: Use this path to verify the paper's exact numbers.
2. **Fresh-pull** path: Use this path to regenerate the pipeline from upstream sources (with the caveat that Google Trends is non-deterministic; see [Reproducibility notes](#reproducibility-notes)).

### Cached-data path (recommended, ~30 seconds)

This regenerates every figure and table in the paper from the shipped `data/processed/merged_dataset.csv`.

```bash
git clone https://github.com/dporder/ai-schoolwork-search-interest.git
cd ai-schoolwork-search-interest
python3 -m pip install -r requirements.txt

# Reproduce the paper's headline numbers
jupyter notebook notebooks/02_reproduce_paper_numbers.ipynb

# Or run the standalone scripts:
python3 paper/build_lowess_figure.py     # Figure 1 (LOWESS panels)
python3 paper/build_results_figures.py   # Figures 4 and 6 (cluster means, observed vs. predicted)
python3 paper/build_cluster_map.py       # Figure 2 (DMA cluster map; needs geopandas)
python3 paper/analysis_appendix.py       # Appendix B and C numbers
python3 paper/robustness_appendix.py     # Appendix E (missing-outcome + influence checks)
```

Each figure script writes two files: a vector PDF that `paper/main.tex` embeds, and a 200-DPI PNG of the same figure for display on the web (GitHub cannot render a PDF inline, which is why the figures above are PNGs).

### Fresh-pull path (full pipeline, requires API credentials)

```bash
cp .env.example .env
# Edit .env with CENSUS_API_KEY, KAGGLE_USERNAME, KAGGLE_KEY

jupyter notebook notebooks/01_full_pipeline.ipynb
```

The full pipeline takes about 30-45 minutes depending on Google Trends rate limiting.

### Compile the paper

```bash
make paper      # requires pdflatex and bibtex on PATH
```

---

## Repository structure

```
.
├── README.md                          # this file
├── LICENSE                            # MIT license for code
├── LICENSE-DATA                       # CC BY 4.0 for derived dataset
├── CITATION.cff                       # citation metadata
├── .zenodo.json                       # metadata Zenodo reads at release
├── CHANGELOG.md                       # version history
├── requirements.txt                   # pinned Python dependencies
├── pyproject.toml                     # ruff/pytest config
├── Makefile                           # common entry points
├── .env.example                       # credential template (no real keys)
├── .gitignore
├── scripts/
│   └── release.sh                     # stamp + tag a release (make release)
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
│   ├── figures/                       # all paper figures (PDF for LaTeX,
│   │                                  #   PNG for the web)
│   ├── build_lowess_figure.py         # Figure 1 (LOWESS panels)
│   ├── build_results_figures.py       # Figures 4 + 6 (cluster means, obs vs. predicted)
│   ├── build_cluster_map.py           # Figure 2 (DMA cluster map; needs geopandas)
│   ├── analysis_appendix.py           # Appendix B + C reproducer
│   └── robustness_appendix.py         # Appendix E reproducer
├── tests/
│   └── test_smoke.py                  # runs in CI
└── .github/
    └── workflows/
        └── ci.yml                     # GitHub Actions
```

---

## Reproducibility notes

This repository is designed around two related but distinct goals:

1. **Bit-for-bit reproducibility of the paper's numbers** from the shipped `data/processed/merged_dataset.csv`. For this, utilize `notebooks/02_reproduce_paper_numbers.ipynb`.

2. **Reproducibility of the data acquisition pipeline** from upstream sources. For this, utilize `notebooks/01_full_pipeline.ipynb`.

*IMPORTANT NOTE*: The second is harder because Google Trends is non-deterministic ([Hölzl, Keusch, & Sajons, 2025](https://doi.org/10.1016/j.ssresearch.2024.103099)), and, as such, the same DMA-level query at two different times can return materially different normalized values. The canonical pull date used for the paper is 2025-08-19, recorded in `data/README.md`. If your fresh pull produces a different `merged_dataset.csv`, the qualitative claims in the paper (smaller, less affluent, lower-attainment regions show higher AI-for-schoolwork search interest) should still hold, however the exact R-squared and cluster means may shift.

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

Full per-dataset provenance, including pull dates and exact API tables, is documented in [`data/README.md`](data/README.md).

---

## Versioning

Every tagged release is archived on Zenodo, which issues two kinds of DOI. Which one to cite depends on what you are citing. The **concept DOI** (the badge at the top of this file) always resolves to the most recent release; cite it when you mean the project. Each release additionally gets its own **version DOI**, which permanently resolves to that one frozen snapshot; cite it when you need the exact code and data behind a specific set of numbers. The published version of the paper pins a version DOI in its data-availability statement for that reason.

Numbers reported in the paper change between releases. [`CHANGELOG.md`](CHANGELOG.md) records what differs and why, so if you are reproducing a published figure, use the version DOI cited in that paper rather than the latest release.

Releases are cut with `make release VERSION=x.y.z`, which stamps the version into `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`, and this file's BibTeX entry before tagging, so the metadata Zenodo archives always matches the tag.

---

## License

- Code: [MIT](LICENSE)
- Derived dataset: [CC BY 4.0](LICENSE-DATA)
- Upstream data sources retain their own licenses; see [`data/README.md`](data/README.md).
