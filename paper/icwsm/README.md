# ICWSM variant — separate build

This directory holds the **ICWSM submission variant** of the paper. It is
deliberately separate from `paper/main.tex`, which stays in the standard
single-column article format used for journal submissions.

Both variants share `../refs.bib` and `../figures/`, so bibliography fixes and
regenerated figures propagate to both automatically. Nothing here overwrites the
journal build.

## Build

```bash
make icwsm       # from the repo root
```

## Prerequisite: the AAAI Author Kit (not vendored here)

ICWSM 2027 requires AAAI two-column format via **AAAI Author Kit version 25**.
Those style files are distributed by AAAI and are not redistributable, so they
are not committed to this repo. Before the first build, download the kit and
place `aaai25.sty` (and its companion files) in this directory:

- Author Kit: <https://aaai.org/authorkit25/>
- Or use the Overleaf template `aaai-authorkit25-anonymoussubmission`

Until then, `make icwsm` will fail with a missing-style-file error. That is
expected.

## The constraint that shapes everything

| | |
|---|---|
| Page limit | **11 pages** (8 recommended), 12 on revise-and-resubmit |
| References | **count toward the limit** (unusual — journals exclude them) |
| Appendices | **do not** count, but "excessively long appendices may result in rejection" |
| Format | two-column, US Letter, AAAI Author Kit 25 |
| Review | double-anonymous — strip name, affiliation, email, and acknowledgements |
| Deadline | **15 September 2026, 23:59 AoE** (Round 2) |

The journal version is ~5,650 words of body text with 6 figures and 5 tables,
compiling to 22 pages single-column. In AAAI two-column that is roughly 10–10.5
pages including references, which fits 11 but leaves almost no slack.

## Compression plan

The body text does **not** need cutting. The page budget is consumed by floats
and references, so that is where to work.

**Move to the appendix (free — appendices are exempt):**
- Appendix E robustness table (already appendix-resident)
- Figure 6 (observed vs. predicted) — a diagnostic, the first thing to move
- Figure 3 / Figure 5 if the budget is still tight

**Keep in the body (these carry the argument):**
- Figure 1 (LOWESS panels) — the univariate gradients
- Figure 2 (DMA cluster map) — the geography, this is the paper's signature image
- Table 1 (cluster typology) — the headline result
- Table 2 (model comparison)

**Tighten, do not cut:**
- Related Work compresses well; ICWSM reviewers know Daepp & Counts and the
  digital-divide literature, so the background can be assumed more heavily than
  for an education-journal audience.
- The three-interpretations discussion is the paper's best defensive asset and
  should survive close to intact.

**Reframe for the venue:**
- Lead harder on the inversion of Daepp & Counts (ICWSM 2025). That contrast is
  the reason this paper belongs at this venue, and it should appear in the
  abstract's first two sentences.
- Foreground the released 209-DMA dataset and the anchor-normalized 73-keyword
  method as reusable contributions. Computational-social-science venues weight
  method and data contributions heavily.

## Anonymization checklist

- [ ] Remove `\author`, `\affil`, and the contact email from the title block
- [ ] Remove the ORCID line
- [ ] Replace the Code-and-data-availability URL with an anonymized note
      ("code and data will be released on acceptance"), or use an anonymous
      mirror — the live GitHub URL identifies the author
- [ ] Check `refs.bib` for self-citations that would need third-person phrasing
- [ ] Remove acknowledgements

Note: ICWSM permits public preprints during review. Its anonymity clause states
that "the anonymity requirement does not extend outside the review process
(e.g., you can distribute your papers on the Web)". So a SocArXiv or arXiv
posting does not conflict with the double-anonymous submission.
