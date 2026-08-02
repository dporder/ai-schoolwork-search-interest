# Makefile for ai-schoolwork-search-interest
#
# Common entry points:
#   make install    - install Python dependencies
#   make figures    - regenerate Figure 1 (LOWESS) and Figures 4+6
#                     (cluster means, obs vs. predicted)
#   make map        - regenerate Figure 2 (DMA cluster map; requires
#                     geopandas / cartopy)
#
#   Both figure targets write each figure twice: a vector PDF for
#   paper/main.tex and a 200-DPI PNG for README.md and the web.
#   make appendix   - regenerate Appendix B and C numbers (cluster
#                     geography + VIF)
#   make robustness - regenerate Appendix E (missing-outcome + influence checks)
#   make verify     - run the smoke test suite
#   make paper      - compile paper/main.tex to paper/main.pdf (requires
#                     pdflatex + bibtex on PATH)
#   make icwsm      - compile the ICWSM two-column variant (requires the
#                     AAAI Author Kit; see paper/icwsm/README.md)
#   make release    - stamp VERSION into CITATION.cff, .zenodo.json, and
#                     CHANGELOG.md, then commit and tag. Does not push.
#                     Usage: make release VERSION=1.1.0
#                            make release VERSION=1.1.0 DRY_RUN=1
#   make clean      - remove LaTeX build artifacts

.PHONY: install figures map appendix robustness verify paper icwsm release clean help

help:
	@echo "Available targets: install figures map appendix robustness verify paper icwsm release clean"

install:
	python3 -m pip install -r requirements.txt

figures:
	python3 paper/build_lowess_figure.py
	python3 paper/build_results_figures.py

map:
	python3 paper/build_cluster_map.py

appendix:
	python3 paper/analysis_appendix.py

robustness:
	python3 paper/robustness_appendix.py

verify:
	python3 -m pytest tests/ -v

paper:
	cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

icwsm:
	cd paper/icwsm && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

release:
	@VERSION="$(VERSION)" DRY_RUN="$(DRY_RUN)" bash scripts/release.sh

clean:
	cd paper && rm -f main.aux main.bbl main.blg main.log main.out main.synctex.gz main.fdb_latexmk main.fls missfont.log *.tmp
