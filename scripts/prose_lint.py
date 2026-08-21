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


def body_prose(text):
    """Strip what the rules do not govern: code fences, list items, table rows.

    Ordered and unordered list items both carry the sanctioned hub-entry format,
    `[Link](/slug) — lowercase outcome`, so neither is checked for em dashes.
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return "\n".join(
        "" if re.match(r"\s*([-*]\s|\d+\.\s|\|)", line) else line
        for line in text.split("\n")
    )


def main():
    root = pathlib.Path(__file__).resolve().parent.parent / "fern/docs/pages"
    findings = []
    for path in sorted(root.rglob("*.mdx")):
        if "api_documentation" in str(path) or path.name in GENERATED:
            continue
        prose = body_prose(path.read_text())
        for name, pattern in RULES:
            for match in re.finditer(pattern, prose):
                line = prose[:match.start()].count("\n") + 1
                findings.append((path, line, name, match.group(0)))

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
