"""
Generate the ICWSM two-column submission source from the journal source.

paper/icwsm/main.tex is DERIVED, not hand-maintained. Regenerate it after any
edit to paper/main.tex so the two versions never drift:

    python3 paper/icwsm/build_icwsm_source.py

What this does, and does not, change:

  CHANGES (required by the venue)
    - swaps the article preamble for the AAAI two-column preamble
    - anonymizes the title block (ICWSM is double-anonymous)
    - anonymizes the code-and-data-availability statement, because the live
      GitHub URL identifies the author
    - switches the bibliography style to aaai25

  DOES NOT CHANGE
    - any section of the body text, any table, any figure, any number

Float placement is NOT adjusted here. ICWSM's 11-page limit counts references
but exempts appendices, so if the compiled paper overruns, move figures into
the appendix rather than cutting prose. See README.md in this directory.
"""

import pathlib
import re

HERE = pathlib.Path(__file__).parent
SRC = HERE.parent / "main.tex"
DST = HERE / "main.tex"

AAAI_PREAMBLE = r"""% ============================================================
% GENERATED FILE -- DO NOT EDIT BY HAND.
% Produced by paper/icwsm/build_icwsm_source.py from paper/main.tex.
% Re-run that script after editing the journal source.
% ============================================================
\documentclass[letterpaper]{article}

% AAAI Author Kit 25. aaai25.sty and aaai25.bst are distributed by AAAI and are
% kept out of version control (see .gitignore). Download the kit from
% https://aaai.org/authorkit25/ and place them in this directory. See README.md.
%
% The kit specifically FORBIDS several packages the journal build uses, notably
% float, hyperref, geometry, authblk and setspace. None are needed here: the
% body uses only [!htbp] float placement, and the one \href lived in the
% code-availability section, which is replaced during anonymization.
\usepackage[submission]{aaai25}  % 'submission' suppresses the copyright block
\usepackage{times}
\usepackage{helvet}
\usepackage{courier}
\usepackage[hyphens]{url}
\usepackage{graphicx}
\usepackage{natbib}   % no options permitted
\usepackage{caption}  % no options permitted
\usepackage{booktabs}
\usepackage{amsmath, amssymb}
\usepackage{placeins} % for \FloatBarrier, used in the body
\urlstyle{rm}
\def\UrlFont{\rm}
\frenchspacing
\setlength{\pdfpagewidth}{8.5in}
\setlength{\pdfpageheight}{11in}

\pdfinfo{
/TemplateVersion (2025.1)
}

\title{Who Turns to AI for Schoolwork? \\
Socioeconomic and Educational Predictors of Student Interest in the ChatGPT Era}

% ICWSM 2027 uses double-anonymous review. Per the AAAI Author Kit: "Anonymous
% submissions must not include the author names and affiliations. Write
% 'Anonymous Submission' as the 'sole author' and leave the affiliations empty."
\author{Anonymous Submission}
\affiliations{}

\begin{document}
\maketitle
"""

ANON_AVAILABILITY = r"""\section*{Code and data availability}
Code, the processed dataset, and a reproducible analysis notebook are archived
in a public repository with a permanent DOI. The repository URL and DOI are
withheld here to preserve anonymity during review, and will be given in the
camera-ready version. Raw Google Trends responses are provided as CSVs; Trends
queries are not guaranteed to replicate exactly over time because the
underlying API is non-deterministic.
"""


def main() -> None:
    src = SRC.read_text()

    # 1. everything up to and including \maketitle -> AAAI preamble
    marker = r"\maketitle"
    idx = src.index(marker) + len(marker)
    body = src[idx:]
    out = AAAI_PREAMBLE + body

    # 2. anonymize the code-and-data-availability section
    # lambda repl so backslashes in the replacement are taken literally
    out, n_anon = re.subn(
        r"\\section\*\{Code and data availability\}.*?(?=\n%|\n\\bibliographystyle)",
        lambda _m: ANON_AVAILABILITY,
        out,
        flags=re.DOTALL,
    )
    if n_anon != 1:
        raise SystemExit(
            f"expected exactly one availability section to anonymize, replaced {n_anon}"
        )

    # 3. drop the explicit \bibliographystyle. aaai25.sty issues
    #    \bibliographystyle{aaai25} itself, and a second one makes bibtex fail
    #    with "Illegal, another \bibstyle command".
    out = out.replace("\\bibliographystyle{plainnat}\n", "")

    # 4. bibliography lives one level up
    out = out.replace(r"\bibliography{refs}", r"\bibliography{../refs}")

    # 5. figures live one level up
    out = out.replace("{figures/", "{../figures/")

    DST.write_text(out)

    # report anything that still looks identifying
    leaks = []
    for pattern, why in [
        (r"Porder", "author name"),
        (r"danporder@", "contact email"),
        (r"github\.com/", "repository URL"),
        (r"zenodo\.\d+", "Zenodo DOI"),
        (r"University of London", "affiliation"),
    ]:
        for m in re.finditer(pattern, out):
            line = out[:m.start()].count("\n") + 1
            leaks.append(f"    line {line}: {why} ({m.group(0)!r})")

    print(f"wrote {DST.relative_to(HERE.parent.parent)} ({out.count(chr(10)) + 1} lines)")
    if leaks:
        print("\n  ANONYMITY CHECK FAILED -- identifying strings remain:")
        print("\n".join(leaks))
    else:
        print("  anonymity check: no identifying strings found")


if __name__ == "__main__":
    main()
