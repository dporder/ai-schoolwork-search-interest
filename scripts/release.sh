#!/usr/bin/env bash
#
# release.sh — stamp version metadata, commit, and tag a release.
#
# Usage:
#   make release VERSION=1.1.0
#   make release VERSION=1.1.0 DRY_RUN=1     # show changes, touch nothing
#
# Stamps VERSION into CITATION.cff, .zenodo.json, CHANGELOG.md, and the
# README's @software BibTeX entry, commits the result, and creates an
# annotated v<VERSION> tag.
#
# It deliberately does NOT push. Zenodo archives the tarball and mints a DOI
# the moment the GitHub Release is published, and Zenodo DOIs cannot be
# withdrawn once minted. The metadata therefore has to be correct *before* the
# release exists, and the push is left as a separate, deliberate step. The
# script prints the exact commands to run next.

set -euo pipefail

VERSION="${VERSION:-}"
DRY_RUN="${DRY_RUN:-}"

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

[ -n "$VERSION" ] || die "VERSION is not set. Usage: make release VERSION=1.1.0"

# Reject a leading "v" rather than silently producing tag "vv1.1.0".
case "$VERSION" in
    v*) die "VERSION must not start with 'v' (got '$VERSION'); the tag is derived from it" ;;
esac

printf '%s' "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' \
    || die "VERSION must be semver MAJOR.MINOR.PATCH (got '$VERSION')"

# Always operate on the repo root, wherever make was invoked from.
cd "$(dirname "$0")/.."
[ -f CITATION.cff ] || die "CITATION.cff not found; are you in the repo root?"

TAG="v$VERSION"
DATE="$(date -u +%Y-%m-%d)"

# --- Preflight -------------------------------------------------------------

git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ "$BRANCH" = "main" ] || die "on branch '$BRANCH'; releases are cut from main"

git rev-parse -q --verify "refs/tags/$TAG" >/dev/null \
    && die "tag $TAG already exists; bump VERSION or delete the tag first"

if [ -z "$DRY_RUN" ] && [ -n "$(git status --porcelain)" ]; then
    die "working tree is dirty; commit or stash first (or pass DRY_RUN=1)"
fi

# A release with no changelog entry is a release nobody can interpret later.
grep -Eq "^## \[$VERSION\]" CHANGELOG.md \
    || die "CHANGELOG.md has no '## [$VERSION]' section; write one first"

# --- Stamp -----------------------------------------------------------------

python3 - "$VERSION" "$DATE" "${DRY_RUN:-}" <<'PY'
import json
import pathlib
import re
import sys

version, date, dry_run = sys.argv[1], sys.argv[2], bool(sys.argv[3])
changed = []


def write(path: pathlib.Path, old: str, new: str) -> None:
    if old == new:
        print(f"  {path}: already current")
        return
    changed.append(str(path))
    if dry_run:
        print(f"  {path}: would update")
    else:
        path.write_text(new, encoding="utf-8")
        print(f"  {path}: updated")


# CITATION.cff — line-targeted so comments and block scalars survive.
cff_path = pathlib.Path("CITATION.cff")
cff = cff_path.read_text(encoding="utf-8")
if not re.search(r"(?m)^version:", cff) or not re.search(r"(?m)^date-released:", cff):
    sys.exit("error: CITATION.cff is missing a version or date-released key")
new_cff = re.sub(r'(?m)^version:.*$', f'version: "{version}"', cff, count=1)
new_cff = re.sub(r'(?m)^date-released:.*$', f"date-released: {date}", new_cff, count=1)
write(cff_path, cff, new_cff)

# .zenodo.json — this is what Zenodo reads at ingest, in preference to
# CITATION.cff, so its version must match the tag being archived.
zen_path = pathlib.Path(".zenodo.json")
zen = zen_path.read_text(encoding="utf-8")
data = json.loads(zen)
data["version"] = version
write(zen_path, zen, json.dumps(data, indent=2, ensure_ascii=False) + "\n")

# CHANGELOG.md — flip "unreleased" to the release date.
log_path = pathlib.Path("CHANGELOG.md")
log = log_path.read_text(encoding="utf-8")
# [ \t]* rather than \s*: \s matches newlines, which would swallow the blank
# line separating the heading from the section body.
pattern = re.compile(
    rf"(?mi)^(## \[{re.escape(version)}\][ \t]*[—-][ \t]*)unreleased[ \t]*$"
)
new_log = pattern.sub(rf"\g<1>{date}", log, count=1)
if new_log == log and re.search(
    rf"(?mi)^## \[{re.escape(version)}\][ \t]*[—-][ \t]*unreleased", log
):
    sys.exit("error: failed to stamp the CHANGELOG heading")
write(log_path, log, new_log)

# README.md — the @software BibTeX entry names a version. It is the only
# version string left in the README; everything else there resolves through
# the concept DOI and the release badge, which track latest on their own.
readme_path = pathlib.Path("README.md")
readme = readme_path.read_text(encoding="utf-8")
new_readme, n = re.subn(
    r"(?m)^(\s*version\s*=\s*\{)[^}]*(\})", rf"\g<1>{version}\g<2>", readme, count=1
)
if n == 0:
    sys.exit("error: no 'version = {...}' field found in the README BibTeX block")
write(readme_path, readme, new_readme)

if not changed:
    print("nothing to stamp; metadata already matches this version")
PY

if [ -n "$DRY_RUN" ]; then
    printf '\nDRY_RUN set — no files written, nothing committed or tagged.\n'
    exit 0
fi

# --- Commit and tag --------------------------------------------------------

if [ -n "$(git status --porcelain CITATION.cff .zenodo.json CHANGELOG.md README.md)" ]; then
    git add CITATION.cff .zenodo.json CHANGELOG.md README.md
    git commit -m "Release $TAG"
else
    echo "metadata already current; tagging existing commit"
fi

git tag -a "$TAG" -m "Release $TAG"

cat <<EOF

Tagged $TAG locally. Nothing has been pushed.

Before pushing, confirm the Zenodo GitHub toggle is ON for this repo —
Zenodo only archives releases published while it is enabled, and it will
not pick this one up retroactively:

  open 'https://zenodo.org/account/settings/github/'

Then publish. Zenodo archives on release publication, so this is the step
that mints the DOI:

  git push origin main && git push origin $TAG
  gh release create $TAG --title "$TAG" --notes-from-tag

EOF
