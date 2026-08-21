#!/usr/bin/env python3
"""Sync the server SDK docs pages from the READMEs in their SDK repos.

Each page under fern/docs/pages/developer_resources/sdks/ is the repo's README
verbatim, with four deviations:

  1. The leading H1 is dropped; the page title comes from the frontmatter.
  2. Repo-only sections (Contributing, Reference) are dropped.
  3. Repo-relative links are rewritten to absolute GitHub URLs.
  4. Absolute docs.schematichq.com links are rewritten to root-relative.

Deviations 3 and 4 are the same rule seen from both ends: a link has to be
absolute wherever it is not already on that site. A README renders on GitHub
and npm, so its docs links must be absolute and its repo links may be
relative; on the docs site it is the other way round. Root-relative docs links
also survive the next IA move, which absolute ones do not (see #399).

Usage:
    scripts/sync_sdk_readmes.py            # rewrite the pages in place
    scripts/sync_sdk_readmes.py --check    # exit 1 if any page is out of date

PHP is deliberately absent: schematic-php's README is OpenAPI generator output
(endpoint tables and a model index linking to files inside the repo), not a
hand-written guide, so its page is maintained by hand.
"""

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "fern/docs/pages/developer_resources/sdks"
GENERATORS = REPO_ROOT / "fern/generators.yml"

# SDK repo -> docs page. Explicit because the mapping is arbitrary
# (schematic-node -> nodejs.mdx). Checked against generators.yml below.
SDKS = {
    "schematic-go": "go.mdx",
    "schematic-java": "java.mdx",
    "schematic-node": "nodejs.mdx",
    "schematic-python": "python.mdx",
    "schematic-ruby": "ruby.mdx",
    "schematic-csharp": "csharp.mdx",
}

# Sections that exist to serve contributors of the SDK repo, not readers of the
# docs site. Dropped along with everything up to the next H2.
DROP_SECTIONS = ("Contributing", "Reference")

BRANCHES = ("main", "master")

DOCS_SITE = "https://docs.schematichq.com"


def fetch_readme(repo):
    """Return the README of SchematicHQ/<repo> from its default branch."""
    errors = []
    for branch in BRANCHES:
        url = f"https://raw.githubusercontent.com/SchematicHQ/{repo}/{branch}/README.md"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            errors.append(f"{branch}: HTTP {err.code}")
        except urllib.error.URLError as err:
            errors.append(f"{branch}: {err.reason}")
    raise SystemExit(f"could not fetch README for {repo} ({'; '.join(errors)})")


def drop_section(body, title):
    """Drop a '## title' section and its content, up to the next H2."""
    out, skipping = [], False
    for line in body.split("\n"):
        if re.match(rf"^## +{re.escape(title)}\s*$", line):
            skipping = True
            continue
        if skipping:
            if re.match(r"^## +", line):
                skipping = False
            else:
                continue
        out.append(line)
    return "\n".join(out)


def to_page_body(readme, repo):
    body = re.sub(r"\A#\s+[^\n]*\n+", "", readme)
    for section in DROP_SECTIONS:
        body = drop_section(body, section)
    body = re.sub(
        r"\]\(\./", f"](https://github.com/SchematicHQ/{repo}/blob/main/", body
    )
    # Only link targets, never bare URLs in prose: a bare URL is something the
    # reader may copy elsewhere, where a root-relative path means nothing.
    body = re.sub(rf"\]\({re.escape(DOCS_SITE)}(/|(?=\)))", "](/", body)
    return body.rstrip("\n") + "\n"


def frontmatter(path):
    match = re.match(r"\A---\n.*?\n---\n", path.read_text(), re.S)
    if not match:
        raise SystemExit(f"{path.name} has no frontmatter; refusing to overwrite it")
    return match.group(0)


def check_coverage():
    """Fail if generators.yml has an SDK repo this script doesn't know about."""
    configured = set(re.findall(r"repository:\s*\S+/(\S+)", GENERATORS.read_text()))
    unknown = configured - set(SDKS)
    if unknown:
        raise SystemExit(
            f"generators.yml configures {', '.join(sorted(unknown))}, which "
            f"{__file__} has no docs page mapping for. Add it to SDKS (or note "
            f"why it is excluded) and rerun."
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report out-of-date pages and exit 1 without writing",
    )
    args = parser.parse_args()

    check_coverage()

    stale = []
    for repo, page in sorted(SDKS.items()):
        path = DOCS_DIR / page
        if not path.exists():
            raise SystemExit(f"{path} does not exist")

        wanted = frontmatter(path) + "\n" + to_page_body(fetch_readme(repo), repo)
        if path.read_text() == wanted:
            print(f"  ok       {page}")
            continue

        stale.append(page)
        if args.check:
            print(f"  STALE    {page} (behind {repo})")
        else:
            path.write_text(wanted)
            print(f"  updated  {page} (from {repo})")

    if args.check and stale:
        print(
            f"\n{len(stale)} page(s) out of date with their READMEs. "
            f"Run scripts/sync_sdk_readmes.py to update them.",
            file=sys.stderr,
        )
        return 1
    if not stale:
        print("\nAll SDK pages match their READMEs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
