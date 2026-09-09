#!/usr/bin/env python3
"""Check MDX body prose against the writing rules in CLAUDE.md.

Covers only the mechanical rules. "Person in the subject slot" and "every setup
paragraph needs a consequence" need a reader.
"""
import re
import sys
import pathlib

RULES = [
    ("frame-not-point", r"\b(The problem this solves|What this does is|The key here is"
                        r"|The idea here is|It'?s worth noting|matters more than it (looks|sounds))\b"),
    ("em-dash", r"—"),
    ("heavy-tense", r"\b(ha[sd]|have) been \w+ing\b"),
    # "Give the reader verbs, not a pile of nouns" is deliberately not checked here.
    # A gerund subject is often the clearest option ("Selling AI means protecting two
    # things"), so it needs a reader rather than a pattern.
    # Roadmap talk: would be deleted the day the feature ships.
    ("documents-a-gap", r"(?i)(does not yet|do not yet|not currently supported"
                        r"|does not currently support|Schematic does not support"
                        r"|does not ship|unshipped)"),
]

GENERATED = {"go.mdx", "java.mdx", "nodejs.mdx", "python.mdx", "ruby.mdx", "csharp.mdx"}

LIST_ITEM = re.compile(r"\s*([-*]\s|\d+\.\s)")
TABLE_ROW = re.compile(r"\s*\|")

# The sanctioned hub-entry format: a link, then a spaced em dash, then the outcome.
HUB_ENTRY = re.compile(r"^\s*([-*]|\d+\.)\s+\**\[[^\]]+\]\([^)]+\)\**[^—]{0,40}—")

# A bolded term followed by a spaced dash, standing in for a sentence. Matches the
# em dash, the double hyphen, and the single hyphen, because all three have turned
# up in the docs doing the same job.
BULLET_TERM_DASH = re.compile(r"^\s*([-*]|\d+\.)\s+\**\*\*[^*]+\*\*[^\n]{0,30}?\s(—|--|-)\s")


def body_prose(text):
    """Strip what the em-dash and phrase rules do not govern.

    Code fences and table rows are not prose. List items are checked, except for
    the hub-entry format, whose em dash is a convention rather than a mistake.
    Blanking every list item is what let the `**Term** — description` pattern
    accumulate 35 instances while the em-dash rule was nominally in force.
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return "\n".join(
        "" if TABLE_ROW.match(line) or HUB_ENTRY.match(line) else line
        for line in text.split("\n")
    )


def bullet_term_dash(text):
    """Find list items where a bolded term and a dash replace a sentence."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        if HUB_ENTRY.match(line) or not LIST_ITEM.match(line):
            continue
        m = BULLET_TERM_DASH.search(line)
        if m:
            out.append((i, m.group(0).strip()))
    return out


def main():
    root = pathlib.Path(__file__).resolve().parent.parent / "fern/docs/pages"
    findings = []
    for path in sorted(root.rglob("*.mdx")):
        if "api_documentation" in str(path) or path.name in GENERATED:
            continue
        text = path.read_text()
        prose = body_prose(text)
        for name, pattern in RULES:
            for match in re.finditer(pattern, prose):
                line = prose[:match.start()].count("\n") + 1
                findings.append((path, line, name, match.group(0)))
        for line, snippet in bullet_term_dash(text):
            findings.append((path, line, "bullet-term-dash", snippet))

    for path, line, name, text in findings:
        rel = path.relative_to(root.parent.parent.parent)
        print(f"{rel}:{line}: [{name}] {text.strip()[:60]}")

    if findings:
        print(f"\n{len(findings)} finding(s). See the writing rules in CLAUDE.md.")
        return 1
    print("prose lint: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
