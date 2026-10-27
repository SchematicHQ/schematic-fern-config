#!/usr/bin/env python3
"""Type-check the TypeScript samples on the components docs pages.

Every ``ts``, ``tsx`` and ``typescript`` fence under
``fern/docs/pages/components/`` becomes one file in ``scripts/samples/.build/``
and ``tsc`` checks them all against the published packages pinned in
``scripts/samples/package.json``. Each diagnostic is reported against the
page and line it came from, as ``fern/docs/pages/....mdx:<line>:<col>``.

How a fence is wrapped, decided in this order:

1. signature: every top-level statement is a bodiless ``function``
   signature, a ``type`` alias or an ``interface`` (imports allowed). Each
   function gets a ``declare`` prefix.
2. module: the fence contains an ``import`` or ``export``. Checked verbatim.
3. JSX fragment: the first token is ``<``. Wrapped in
   ``export const Sample = () => (<>...</>)``.
4. statement: anything else, wrapped in ``export async function sample() {}``.

Before wrapping, every identifier the fence uses that a package exports, and
the fence does not declare itself, gets an import. A fence then reads the way
it would in an app that imports what it uses, and an invented name fails with
TS2304. A name one of the page's own fences imports comes from that package;
any other is searched for in this order:
``@schematichq/schematic-components/elements``, ``@schematichq/schematic-react``,
``@schematichq/schematic-components``, ``@schematichq/schematic-js``, then
``react`` for its hooks. The export lists come from the published ``.d.ts``
rollups in ``scripts/samples/node_modules``.

Host-owned placeholders (the reader's ``company``, ``router``,
``fetchAccessToken``, ...) are declared once in ``scripts/samples/host.d.ts``.
Read its header before adding one.

Skipping a fence: add the meta token ``nocheck`` to the fence line
(```` ```tsx nocheck ````) or put ``{/* samples: nocheck <reason> */}`` on the
line above it. The skipped count is printed with the summary.

Known blind spots: the elements' ``strings`` prop is
``Record<string, string | undefined>`` in components 2.36.0, so a misspelt
string key passes; and ``strict`` is off, so an untyped parameter is ``any``
and whatever a fence reads off it goes unchecked.

Needs ``npm ci --prefix scripts/samples`` first. Python 3.9, stdlib only.
Usage: ``check_samples.py [-v] [--pages DIR] [PAGE.mdx ...]``.
Exit status 1 on any diagnostic, 2 when the scratch package is not installed.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "fern" / "docs" / "pages" / "components"
SAMPLES = ROOT / "scripts" / "samples"
BUILD = SAMPLES / ".build"
SENTINEL = BUILD / "__sentinel.tsx"
NODE_MODULES = SAMPLES / "node_modules"

LANGUAGES = {"ts", "tsx", "typescript"}
FENCE_OPEN = re.compile(r"^\s*```([A-Za-z0-9_+.-]*)(.*)$")
FENCE_CLOSE = re.compile(r"^\s*```\s*$")
NOCHECK_COMMENT = re.compile(r"^\s*\{/\*\s*samples:\s*nocheck\b.*\*/\}\s*$")

# Module specifier, package directory, `exports` subpath. Precedence order.
PACKAGES = [
    ("@schematichq/schematic-components/elements", "@schematichq/schematic-components", "./elements"),
    ("@schematichq/schematic-react", "@schematichq/schematic-react", "."),
    ("@schematichq/schematic-components", "@schematichq/schematic-components", "."),
    ("@schematichq/schematic-js", "@schematichq/schematic-js", "."),
]
REACT_TYPES = NODE_MODULES / "@types" / "react" / "index.d.ts"
HOST_TYPES = SAMPLES / "host.d.ts"

KEYWORDS = set(
    """abstract any as async await bigint boolean break case catch class const constructor
    continue debugger declare default delete do else enum export extends false finally for from
    function get global if implements import in infer instanceof interface is keyof let module
    namespace never new null number object of override package private protected public readonly
    require return satisfies set static string super switch symbol this throw true try type typeof
    undefined unique unknown var void while with yield""".split()
)

EXPORT_DECL = re.compile(
    r"^export\s+(?:declare\s+)?(?:abstract\s+)?(?:async\s+)?"
    r"(?:function\*?|const|let|var|class|interface|type|enum|namespace)\s+([A-Za-z_$][\w$]*)",
    re.M,
)
EXPORT_LIST = re.compile(r"^export\s*\{([^}]*)\}", re.M)
REACT_HOOK = re.compile(r"^\s*function (use[A-Z]\w*)", re.M)
HOST_GLOBAL = re.compile(r"^\s*(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", re.M)

IDENT = re.compile(r"(?<![\w$.])[A-Za-z_$][\w$]*")
DECL_NAME = re.compile(r"\b(?:function\*?|class|interface|type|enum|namespace)\s+([A-Za-z_$][\w$]*)")
VAR_DECL = re.compile(r"\b(?:const|let|var)\s+")
IMPORT_CLAUSE = re.compile(r"\bimport\s+(?:type\s+)?([^;]*?)\s+from\s+", re.S)
NAMED_IMPORT = re.compile(r"\bimport\s+(?:type\s+)?\{([^}]*)\}\s*from\s*[\"']([^\"']+)[\"']")
FUNCTION_PARAMS = re.compile(r"\bfunction\*?\s*(?:[A-Za-z_$][\w$]*\s*)?(?:<[^()]*>\s*)?\(")
MODULE_STATEMENT = re.compile(r"^\s*(?:import|export)\b", re.M)
STATEMENT_START = re.compile(
    r"(?:function|type|interface|declare|export|import|const|let|var|class|enum|abstract"
    r"|async|namespace|return|if|for|while|switch|throw|try)\b"
)
SIGNATURE_STATEMENT = re.compile(r"(?:export\s+)?(?:declare\s+)?(function\*?|type|interface|import)\b")
DIAGNOSTIC = re.compile(
    r"^(?P<file>.+?)\((?P<line>\d+),(?P<col>\d+)\): (?:error|warning) (?P<code>TS\d+): (?P<msg>.*)$"
)


class Block:
    def __init__(self, page, fence_line, lang, meta, lines):
        self.page = page
        self.fence_line = fence_line  # 1-based line of the opening fence
        self.lang = lang
        self.meta = meta
        self.lines = lines
        self.kind = None
        self.out = None  # generated file path
        self.prefix_lines = 0


# --- fences -----------------------------------------------------------------


def fences(page):
    """Yield (block, skipped) for every TS-family fence on the page."""
    lines = page.read_text().split("\n")
    i = 0
    while i < len(lines):
        m = FENCE_OPEN.match(lines[i])
        if not m:
            i += 1
            continue
        lang, meta = m.group(1), m.group(2)
        start = i
        j = i + 1
        while j < len(lines) and not FENCE_CLOSE.match(lines[j]):
            j += 1
        if lang in LANGUAGES:
            k = start - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            skipped = "nocheck" in meta.split() or (k >= 0 and bool(NOCHECK_COMMENT.match(lines[k])))
            yield Block(page, start + 1, lang, meta, lines[start + 1:j]), skipped
        i = j + 1


# --- exports ----------------------------------------------------------------


def rollup_path(pkg_dir, subpath):
    meta = json.loads((NODE_MODULES / pkg_dir / "package.json").read_text())
    entry = (meta.get("exports") or {}).get(subpath)
    types = entry.get("types") if isinstance(entry, dict) else None
    if types is None and subpath == ".":
        types = meta.get("types") or meta.get("typings")
    if types is None:
        sys.exit(f"check_samples: no types entry for {pkg_dir} {subpath}")
    return NODE_MODULES / pkg_dir / types


def exports_of(path):
    text = path.read_text()
    names = set(EXPORT_DECL.findall(text))
    for group in EXPORT_LIST.findall(text):
        for item in group.split(","):
            item = item.strip()
            if item.startswith("type "):
                item = item[5:].strip()
            if " as " in item:
                item = item.split(" as ")[-1].strip()
            if item and item != "default":
                names.add(item)
    return names


def export_index():
    index = [(spec, exports_of(rollup_path(pkg, sub))) for spec, pkg, sub in PACKAGES]
    index.append(("react", set(REACT_HOOK.findall(REACT_TYPES.read_text()))))
    return index


# --- lexing -----------------------------------------------------------------


def blank_noise(code):
    """Replace comments and string contents with spaces, keeping every offset.

    Template literals keep their ``${...}`` expressions, so identifiers inside
    them are still seen.
    """
    out = list(code)
    n = len(code)

    def blank(a, b):
        for k in range(a, min(b, n)):
            if out[k] != "\n":
                out[k] = " "

    i = 0
    while i < n:
        c = code[i]
        pair = code[i:i + 2]
        if pair == "//":
            j = code.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif pair == "/*":
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(i, j)
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and code[j] not in (c, "\n"):
                j += 2 if code[j] == "\\" else 1
            blank(i + 1, j)
            i = j + 1
        elif c == "`":
            j = i + 1
            while j < n and code[j] != "`":
                if code[j] == "\\":
                    blank(j, j + 2)
                    j += 2
                elif code[j:j + 2] == "${":
                    depth, k = 1, j + 2
                    while k < n and depth:
                        depth += {"{": 1, "}": -1}.get(code[k], 0)
                        k += 1
                    j = k
                else:
                    if code[j] != "\n":
                        out[j] = " "
                    j += 1
            i = j + 1
        else:
            i += 1
    return "".join(out)


def split_top(text, sep):
    """Split on `sep` at bracket depth 0."""
    parts, depth, start = [], 0, 0
    for i, c in enumerate(text):
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == sep and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return parts


def binding_names(pattern):
    """The names a binding pattern (or parameter list) introduces."""
    names = set()
    for seg in split_top(pattern, ","):
        seg = split_top(seg, ":")[0]
        seg = split_top(seg, "=")[0].strip().lstrip(".").rstrip("?").strip()
        if not seg:
            continue
        if seg[0] in "{[":
            close = seg.rfind("}" if seg[0] == "{" else "]")
            inner = seg[1:close] if close > 0 else seg[1:]
            for sub in split_top(inner, ","):
                if seg[0] == "{":
                    parts = split_top(sub, ":")
                    sub = parts[1] if len(parts) > 1 else parts[0]
                names |= binding_names(sub)
        else:
            m = IDENT.match(seg)
            if m:
                names.add(m.group(0))
    return names


def balanced(text, start, open_ch, close_ch):
    """Index just past the bracket matching text[start]."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def declared_names(code):
    """Every name the block declares, at any depth."""
    names = set(DECL_NAME.findall(code))
    for m in VAR_DECL.finditer(code):
        i = m.end()
        if i < len(code) and code[i] in "{[":
            end = balanced(code, i, code[i], "}" if code[i] == "{" else "]")
            names |= binding_names(code[i:end])
        else:
            ident = IDENT.match(code, i)
            if ident:
                names.add(ident.group(0))
    for m in IMPORT_CLAUSE.finditer(code):
        clause = m.group(1)
        brace = clause.find("{")
        if brace >= 0:
            inner = clause[brace + 1:clause.rfind("}")]
            for item in inner.split(","):
                item = item.strip()
                if item.startswith("type "):
                    item = item[5:].strip()
                if " as " in item:
                    item = item.split(" as ")[-1].strip()
                if item:
                    names.add(item)
            clause = clause[:brace]
        for item in clause.split(","):
            item = item.strip()
            if item.startswith("* as "):
                item = item[5:].strip()
            if item:
                names.add(item)
    for m in FUNCTION_PARAMS.finditer(code):
        end = balanced(code, m.end() - 1, "(", ")")
        names |= binding_names(code[m.end():end - 1])
    for m in re.finditer(r"=>", code):
        j = m.start() - 1
        while j >= 0 and code[j].isspace():
            j -= 1
        if j < 0:
            continue
        if code[j] == ")":
            depth, k = 0, j
            while k >= 0:
                depth += {")": 1, "(": -1}.get(code[k], 0)
                if depth == 0:
                    break
                k -= 1
            names |= binding_names(code[k + 1:j])
        elif re.match(r"[\w$]", code[j]):
            k = j
            while k >= 0 and re.match(r"[\w$]", code[k]):
                k -= 1
            names.add(code[k + 1:j + 1])
    return names


# --- classification ---------------------------------------------------------


def top_level_statements(text):
    """(start, end) spans of the top-level statements of blanked code."""
    spans, i, n = [], 0, len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        start, depth, end = i, 0, None
        while i < n and end is None:
            c = text[i]
            if c in "({[":
                depth += 1
            elif c in ")}]":
                depth -= 1
                if depth == 0 and c == "}":
                    j = i + 1
                    while j < n and text[j].isspace():
                        j += 1
                    if j < n and text[j] == ";":
                        end = j + 1
                    elif j < n and text[j] in "|&":
                        i = j
                    else:
                        end = i + 1
            elif depth == 0 and c == ";":
                end = i + 1
            elif depth == 0 and c == "\n":
                j = i + 1
                while j < n and text[j].isspace():
                    j += 1
                if j < n and (text[j] == "<" or STATEMENT_START.match(text, j)):
                    end = i
            i += 1
        spans.append((start, n if end is None else end))
        i = max(i, spans[-1][1])
    return spans


def bodiless(stmt):
    """A function signature without an implementation."""
    if not stmt.rstrip().endswith(";"):
        return False
    depth = 0
    for i, c in enumerate(stmt):
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "{" and depth == 0:
            before = stmt[:i].rstrip()
            return before.endswith(("=>", ":", "|", "&", ",", "=", "<", "("))
    return True


def classify(blanked):
    spans = top_level_statements(blanked)
    kinds = []
    for start, end in spans:
        m = SIGNATURE_STATEMENT.match(blanked, start)
        if not m or (m.group(1).startswith("function") and not bodiless(blanked[start:end])):
            kinds = None
            break
        kinds.append(m.group(1))
    if kinds and any(k != "import" for k in kinds):
        return "signature", spans
    if MODULE_STATEMENT.search(blanked):
        return "module", spans
    if blanked.lstrip().startswith("<"):
        return "fragment", spans
    return "statement", spans


# --- building ---------------------------------------------------------------


def page_imports(blocks):
    """Where the page's own fences import each name from, first import wins.

    A fragment on a page follows the page's imports, so `<PricingTable />` on a
    page whose module blocks import `PricingTable` from the root package is
    checked against that package rather than the elements entry point.
    """
    preferred = {}
    for block in blocks:
        for m in NAMED_IMPORT.finditer("\n".join(block.lines)):
            names, spec = m.group(1), m.group(2)
            if spec.startswith("."):
                continue
            for item in names.split(","):
                item = item.strip()
                if item.startswith("type "):
                    item = item[5:].strip()
                if " as " in item:
                    item = item.split(" as ")[-1].strip()
                if item:
                    preferred.setdefault(item, spec)
    return preferred


def auto_imports(used, index, preferred):
    by_spec = {}
    for name in sorted(used):
        if name in preferred:
            by_spec.setdefault(preferred[name], []).append(name)
            continue
        for spec, names in index:
            if name in names and (spec != "react" or name.startswith("use")):
                by_spec.setdefault(spec, []).append(name)
                break
    return [f'import {{ {", ".join(names)} }} from "{spec}";' for spec, names in by_spec.items()]


def build(block, index, host_names, preferred):
    code = "\n".join(block.lines)
    blanked = blank_noise(code)
    kind, spans = classify(blanked)
    declared = declared_names(blanked)
    used = set(IDENT.findall(blanked.replace("...", "   "))) - KEYWORDS - declared - host_names
    header = "".join(line + "\n" for line in auto_imports(used, index, preferred))

    if kind == "signature":
        body = code
        for start, _ in reversed(spans):
            if re.match(r"function\b", blanked[start:]):
                body = body[:start] + "declare " + body[start:]
        prefix, suffix = header, "\nexport {};\n"
    elif kind == "module":
        body, prefix, suffix = code, header, "\n"
    elif kind == "fragment":
        body, prefix, suffix = code, header + "export const Sample = () => (<>\n", "\n</>);\n"
    else:
        body, prefix, suffix = code, header + "export async function sample() {\n", "\n}\n"

    rel = block.page.relative_to(block.pages_root).with_suffix("")
    block.out = BUILD / (str(rel).replace("/", "__") + f"__L{block.fence_line}.tsx")
    block.kind = kind
    block.prefix_lines = prefix.count("\n")
    block.out.write_text(prefix + body + suffix)


# --- reporting --------------------------------------------------------------


def page_label(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def tsc_once(blocks):
    """Run tsc over .build and map each diagnostic back to its page.

    Returns (diagnostics, whether the type checker ran, blocks with a diagnostic).
    """
    proc = subprocess.run(
        [str(NODE_MODULES / ".bin" / "tsc"), "-p", "tsconfig.json", "--noEmit", "--pretty", "false"],
        cwd=str(SAMPLES), capture_output=True, text=True,
    )
    by_file = {str(b.out.relative_to(SAMPLES)): b for b in blocks}
    diagnostics, with_errors, checked = [], [], False
    for line in (proc.stdout + proc.stderr).splitlines():
        m = DIAGNOSTIC.match(line)
        if not m:
            if line.startswith(" ") and diagnostics:
                diagnostics[-1] += "\n" + line
            elif line.strip():
                diagnostics.append(line)
            continue
        if m.group("file") == str(SENTINEL.relative_to(SAMPLES)):
            checked = True
            continue
        block = by_file.get(m.group("file"))
        if block is None:
            where = f"{page_label(SAMPLES / m.group('file'))}:{m.group('line')}:{m.group('col')}"
        else:
            line_no = block.fence_line + max(int(m.group("line")) - block.prefix_lines, 0)
            where = f"{page_label(block.page)}:{line_no}:{m.group('col')}"
            if block not in with_errors:
                with_errors.append(block)
        diagnostics.append(f"{where}: {m.group('code')} {m.group('msg')}")
    return diagnostics, checked, with_errors


def run_tsc(blocks):
    """Collect every diagnostic, re-running without the fences that fail to parse.

    tsc reports only syntax errors while any file has one. The sentinel file
    carries a type error, so its absence from the output says the type checker
    did not run; the fences with errors are then dropped and tsc runs again.
    """
    SENTINEL.write_text('export const sentinel: number = "the type checker ran";\n')
    diagnostics, remaining = [], list(blocks)
    for _ in range(8):
        found, checked, with_errors = tsc_once(remaining)
        diagnostics += found
        if checked or not with_errors:
            break
        for block in with_errors:
            block.out.unlink()
        remaining = [b for b in remaining if b not in with_errors]
    return diagnostics


def main(argv):
    verbose = "-v" in argv
    argv = [a for a in argv if a != "-v"]
    pages_root = PAGES
    if "--pages" in argv:
        i = argv.index("--pages")
        pages_root = pathlib.Path(argv[i + 1]).resolve()
        del argv[i:i + 2]
    pages = [pathlib.Path(a).resolve() for a in argv] or sorted(pages_root.rglob("*.mdx"))

    if not (NODE_MODULES / ".bin" / "tsc").exists():
        print("check_samples: scripts/samples/node_modules is missing; run: npm ci --prefix scripts/samples")
        return 2
    index = export_index()
    host_names = set(HOST_GLOBAL.findall(HOST_TYPES.read_text()))

    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir()
    blocks, skipped = [], 0
    for page in pages:
        found = list(fences(page))
        preferred = page_imports([block for block, _ in found])
        for block, skip in found:
            if skip:
                skipped += 1
                continue
            block.pages_root = pages_root
            build(block, index, host_names, preferred)
            blocks.append(block)
            if verbose:
                print(f"{page_label(page)}:{block.fence_line}: {block.kind} -> {block.out.name}")

    diagnostics = run_tsc(blocks) if blocks else []
    if diagnostics is None:
        return 2
    for d in diagnostics:
        print(d)
    print(f"check_samples: {len(blocks)} fence(s) checked, {skipped} skipped, {len(diagnostics)} diagnostic(s)")
    return 1 if diagnostics else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
