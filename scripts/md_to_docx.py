#!/usr/bin/env python3
"""Generic Markdown -> DOCX for student-facing handouts.

Why this exists
---------------
`build_topic_handout.py` proved the pipeline (Markdown -> styled HTML -> the
tencent-docx bundled engine -> .docx) but it is welded to the topic catalogue:
its title block, column-width profiles and verification are all catalogue-shaped.
Any *other* handout copy-pasted from it would drift the moment the catalogue
changed.

This script is the reusable half.  It takes any Markdown file and produces a
.docx with the same look, plus a verification pass that is generic:

  * every heading in the source appears in the output
  * the table count survives
  * no Markdown syntax leaked through as literal text (``**``, backticks, ``|---``)
  * emoji with no text-presentation glyph are substituted (💻 / 🖥)

Usage, from the repo root:

    <managed python> scripts/md_to_docx.py projects/capstone/START-HERE-W6.md
    <managed python> scripts/md_to_docx.py <input.md> <output.docx> --footer "..."

Exit code 0 = built and verified; 1 = verification failed (the .docx is left on
disk for inspection).

Environment traps this script already accounts for
--------------------------------------------------
* The tencent-docx plugin's own venv is x86_64 and cannot run on this arm64
  machine (no Rosetta).  So the engine is invoked with *this* interpreter, which
  must be the managed arm64 one -- see ``sys.executable`` in ``run_engine``.
* The engine's ``apply_font_family`` writes the FIRST font of a CSS list to
  ``w:ascii``, ``w:hAnsi`` AND ``w:eastAsia``.  Every family used below is a
  single dual-coverage face on purpose; do not turn one into a list.
* Word's built-in Heading styles leak their own definitions through (measured:
  Heading 4 renders blue italic underlined).  ``normalize_headings`` rewrites
  the heading runs explicitly, including ``italic=False`` / ``underline=False``.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# Reuse the audited pieces rather than re-deriving them.
from build_topic_handout import (  # noqa: E402
    HEADING_FONT,
    HEADING_SPEC,
    PRINT_SUBSTITUTIONS,
    engine_dir,
    normalize_headings,
    preprocess_md,
)

REPO_URL = "https://github.com/klausren/ai-application-development"
BRANCH = "main"

BLOCK_CONTAINERS = {"body", "div", "blockquote", "section", "ul", "ol", "table",
                    "tr", "thead", "tbody"}
TEXT_BLOCK_TAGS = ("p", "li", "td", "th", "h1", "h2", "h3", "h4")
INLINE_TAGS = ("em", "strong", "code", "a", "span", "sub", "sup")
LATIN = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


def css(footer_left: str) -> str:
    """Stylesheet -- only properties the engine actually maps."""
    base = f"""
    @page {{
        @bottom-left  {{ content: "{footer_left}"; }}
        @bottom-right {{ content: counter(page) " / " counter(pages); }}
    }}
    body {{ font-family: "宋体"; font-size: 10.5pt; color: #1a1a1a; line-height: 1.45; }}

    p  {{ margin-top: 3pt; margin-bottom: 3pt; }}

    ul, ol {{ margin-top: 3pt; margin-bottom: 3pt; }}
    li {{ margin-bottom: 2pt; }}

    blockquote {{ font-size: 9.5pt; color: #444444; background-color: #F4F6F8;
                 border-left: 2.5pt solid #9DB8D2; margin-top: 6pt; margin-bottom: 6pt; }}

    table {{ width: 100%; font-size: 8.5pt; }}
    th {{ background-color: #1F4E79; color: #FFFFFF; font-size: 8.5pt;
         padding: 3pt; border: 0.5pt solid #A9B7C6; }}
    td {{ font-size: 8.5pt; padding: 3pt; border: 0.5pt solid #C6CDD5; }}

    code {{ font-family: "Consolas"; font-size: 8.5pt; color: #A33A1E; }}
    hr {{ border-bottom: 0.75pt solid #D0D5DA; }}

    .subtitle {{ font-family: "微软雅黑"; font-size: 10.5pt; color: #44546A;
                text-align: center; margin-top: 2pt; margin-bottom: 0; }}
    .subtitle2 {{ font-size: 9pt; color: #7A7A7A;
                 text-align: center; margin-top: 0; margin-bottom: 10pt; }}
    """
    spacing = {
        1: "margin-bottom: 2pt;",
        2: "border-bottom: 1.5pt solid #1F4E79; margin-top: 16pt; margin-bottom: 6pt;",
        3: "margin-top: 13pt; margin-bottom: 4pt;",
        4: "background-color: #E8F0F8; margin-top: 11pt; margin-bottom: 3pt;",
    }
    rules = [
        f'h{level} {{ font-family: "{HEADING_FONT}"; font-size: {size}pt;'
        f' color: #{colour}; font-weight: {"bold" if bold else "normal"};'
        f' text-align: {align}; {spacing[level]} }}'
        for level, (size, bold, colour, align) in HEADING_SPEC.items()
    ]
    return base + "\n    " + "\n    ".join(rules) + "\n    "


def md_to_html(md_text: str, md_path: Path, footer_left: str,
               title_html: str = "") -> tuple[str, dict]:
    import markdown
    from bs4 import BeautifulSoup

    body_md = preprocess_md(md_text)
    raw = markdown.markdown(body_md, extensions=["tables", "sane_lists", "fenced_code"])
    soup = BeautifulSoup(raw, "lxml")

    stats = {"tables": 0, "empty_headers_dropped": 0, "links_rewritten": 0,
             "blockquotes_inlined": 0, "soft_breaks_joined": 0, "glue_risks": []}

    # 0. The engine drops a text node's leading whitespace when that node begins
    #    with a newline, which glues "…menu.\n21 seeds" into "menu.21 seeds".
    #    HTML says a newline in text is only a space, so normalise it here.
    for node in soup.find_all(string=True):
        raw_text = str(node)
        if "\n" not in raw_text:
            continue
        if not raw_text.strip() and node.parent.name in BLOCK_CONTAINERS:
            continue
        normalised = re.sub(r"[ \t]*\n[ \t]*", " ", raw_text)
        if normalised != raw_text:
            node.replace_with(normalised)
            stats["soft_breaks_joined"] += 1

    # 0a. Regression guard for exactly that bug.
    for block in soup.find_all(TEXT_BLOCK_TAGS):
        for child in block.children:
            if getattr(child, "name", None) not in INLINE_TAGS:
                continue
            nxt = child.next_sibling
            if nxt is None or getattr(nxt, "name", None):
                continue
            tail = str(nxt)
            head = child.get_text().rstrip()
            if not tail or not head or tail[0].isspace():
                continue
            last, first = head[-1], tail[0]
            if (last in LATIN and first in LATIN) or (last == "." and first in LATIN):
                stats["glue_risks"].append(f"{head[-24:]!r} would fuse with {tail[:24]!r}")

    # 0b. Markdown wraps block quotes as <blockquote><p>…</p></blockquote>, but the
    #     engine's blockquote handler only reads a direct text child, so the tint
    #     and left rule are lost.  Inline the style onto the paragraph instead.
    for bq in soup.find_all("blockquote"):
        ps = bq.find_all("p")
        if ps:
            for p in ps:
                p["style"] = (p.get("style", "") + "background-color: #F4F6F8;"
                              " border-left: 2.5pt solid #9DB8D2;"
                              " margin-top: 6pt; margin-bottom: 6pt;")
            bq.unwrap()
            stats["blockquotes_inlined"] += 1

    # 1. `| | |` label/value grids have an empty header row; left alone it ships blank.
    for thead in soup.find_all("thead"):
        if not thead.get_text(strip=True):
            thead.decompose()
            stats["empty_headers_dropped"] += 1

    # 2. Relative links are useless on a printout -- point them at the published file.
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path, _, anchor = href.partition("#")
        try:
            rel = (md_path.parent / path).resolve().relative_to(ROOT).as_posix()
        except ValueError:
            continue
        a["href"] = f"{REPO_URL}/blob/{BRANCH}/{rel}" + (f"#{anchor}" if anchor else "")
        stats["links_rewritten"] += 1

    # 3. Column widths must be inline on the first row; CSS in <style> never reaches
    #    the engine.  Keep the table's own header proportions.
    for table in soup.find_all("table"):
        stats["tables"] += 1

    # 3a. The engine auto-converts "Chinese label + colon + run of _ ＿ — -" into a
    #     Word form field (html_to_docx/bookmarks.py:_append_automatic_fields).  Two
    #     things go wrong: the visible blank line is *deleted* rather than left to
    #     write on, and if the surrounding text node holds anything else, that text
    #     is dropped silently (the node is rebuilt from the prefix only).  A printed
    #     form with a missing line and arbitrary missing words is worthless, so
    #     reproduce the engine's own regex here and fail loudly.  Separate the label
    #     from the blank with a full-width space (U+3000) to stay clear of it.
    stats["field_text_loss"] = []
    field_re = re.compile(
        r"(?P<label>[\u4e00-\u9fff]{2,12})[：:](?P<line>[_＿—-]{3,})"
        r"|(?P<label2>[\u4e00-\u9fff]{2,12})(?P<line2>[_＿—-]{3,})")
    for node in soup.find_all(string=True):
        parent = node.parent
        if parent is None or parent.name in {"style", "script"}:
            continue
        if parent.find_parent(["td", "th"]) is not None:
            continue
        if parent.find(attrs={"data-docx-field": True}):
            continue
        text = str(node)
        for mt in field_re.finditer(text):
            label = mt.group("label") or mt.group("label2")
            blank = mt.group("line") or mt.group("line2")
            lost = []
            if text[:mt.start()].strip():
                lost.append(f"preceding {text[:mt.start()]!r}")
            if text[mt.end():].strip():
                lost.append(f"following {text[mt.end():]!r}")
            if lost:
                stats["field_text_loss"].append(
                    f"{label!r}+{len(blank)}x{blank[0]!r} would swallow "
                    + " and ".join(lost))

    content = str(soup)
    if title_html:
        content = re.sub(r"<h1>.*?</h1>", "", content, count=1, flags=re.S)

    doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
           f"<style>{css(footer_left)}</style></head><body>{title_html}{content}</body></html>")
    return doc, stats


def run_engine(html_path: Path, out_path: Path) -> None:
    scripts = engine_dir()
    cmd = [
        sys.executable, "-m", "html_to_docx", "convert", str(html_path),
        "-o", str(out_path),
        "--page-size", "A4", "--orientation", "portrait",
        "--margin-top", "1.9", "--margin-bottom", "1.8",
        "--margin-left", "1.6", "--margin-right", "1.6",
    ]
    proc = subprocess.run(cmd, cwd=str(scripts), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"engine failed (exit {proc.returncode}):\n{proc.stderr[-2000:]}")
    tail = proc.stdout.strip().splitlines()
    print(f"  engine: {tail[-1] if tail else 'ok'}")


def docx_blob(path: Path) -> tuple[str, list[str], int]:
    from docx import Document

    doc = Document(str(path))
    chunks: list[str] = []
    heads: list[str] = []
    for p in doc.paragraphs:
        chunks.append(p.text)
        if p.style.name.startswith("Heading") and p.text.strip():
            heads.append(p.text.strip())
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                chunks.append(c.text)
    return "\n".join(chunks), heads, len(doc.tables)


# A heading is "covered" if this much of it survives.  The engine sometimes
# normalises punctuation inside a heading, so compare on a squashed prefix.
def _squash(s: str) -> str:
    return re.sub(r"[\s·:：\-—–/|]+", "", s).lower()


def verify(md_text: str, docx_path: Path, stats: dict) -> list[str]:
    problems: list[str] = []
    blob, heads, n_tables = docx_blob(docx_path)
    squashed_blob = _squash(blob)

    md_heads = [h.strip() for h in re.findall(r"^#{1,4}\s+(.+)$", md_text, flags=re.M)]
    for h in md_heads:
        if _squash(h)[:40] not in squashed_blob:
            problems.append(f"heading missing from the .docx: {h[:60]!r}")

    if n_tables != stats["tables"]:
        problems.append(f"handout has {n_tables} tables, HTML had {stats['tables']}")

    for token, label in (("**", "bold markers"), ("`", "backticks"), ("|---", "table rules")):
        if token in blob:
            problems.append(f"literal {label} ({token!r}) survived into the .docx")

    for bad, label in (("\U0001f4bb", "💻"), ("\U0001f5a5", "🖥")):
        if bad in blob:
            problems.append(f"unrenderable {label} survived into the .docx")

    for risk in stats["glue_risks"]:
        problems.append(f"would glue in the handout: {risk}")

    for loss in stats.get("field_text_loss", ()):
        problems.append(f"invisible form-field would drop text: {loss}")

    # Fill-in blanks.  A run of three or more "_" is never legitimate markdown
    # (emphasis needs exactly two), but CommonMark happily eats it as nested
    # emphasis: "__________" renders as 4 underscores and "____年__月__日"
    # loses characters outright.  A printable form with shredded blanks is
    # worthless, so require runs of 3+ to survive byte-for-byte.  Use full-width
    # "＿" (U+FF3F) for blanks -- markdown never touches it.
    src_runs = sorted(re.findall(r"_{3,}", md_text), key=len)
    dst_runs = sorted(re.findall(r"_{3,}", blob), key=len)
    if src_runs != dst_runs:
        problems.append(
            "underscore blanks were eaten by markdown emphasis: "
            f"source {[len(r) for r in src_runs]} vs docx {[len(r) for r in dst_runs]} "
            "(use full-width ＿ for fill-in blanks)")

    from docx import Document

    doc = Document(str(docx_path))
    for para in doc.paragraphs:
        if not para.style.name.startswith("Heading"):
            continue
        for run in para.runs:
            if run.font.italic or (run.font.underline is not None and run.font.underline):
                problems.append(f"heading has stray italic/underline: {para.text[:40]!r}")
                break

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="source Markdown file")
    ap.add_argument("output", nargs="?", help="target .docx (default: beside the source)")
    ap.add_argument("--footer", default="", help="left footer text (default: derived)")
    ap.add_argument("--title-html", default="",
                    help="HTML block replacing the source's own H1 (optional)")
    ap.add_argument("--course", default="52015CC3BV · AI Application Development",
                    help="used in the default footer")
    args = ap.parse_args()

    md_path = Path(args.input).resolve()
    if not md_path.exists():
        raise SystemExit(f"source not found: {md_path}")
    out_path = Path(args.output).resolve() if args.output else md_path.with_suffix(".docx")

    footer = args.footer or f"{args.course} · {md_path.stem}"
    md_text = md_path.read_text(encoding="utf-8")
    out_html, stats = md_to_html(md_text, md_path, footer, args.title_html)

    rel_in = md_path.relative_to(ROOT) if md_path.is_relative_to(ROOT) else md_path
    print(f"source : {rel_in}  ({len(md_text.splitlines())} lines)")
    print(f"  tables kept          : {stats['tables']}")
    print(f"  empty headers dropped: {stats['empty_headers_dropped']}")
    print(f"  links made absolute  : {stats['links_rewritten']}")
    print(f"  soft breaks joined   : {stats['soft_breaks_joined']}")
    print(f"  blockquotes inlined  : {stats['blockquotes_inlined']}")

    if stats["glue_risks"]:
        print(f"  GLUE RISKS           : {len(stats['glue_risks'])}")

    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / (md_path.stem + ".html")
        html_path.write_text(out_html, encoding="utf-8")
        print(f"target : {out_path}")
        run_engine(html_path, out_path)

    print(f"  headings normalised  : {normalize_headings(out_path)}")

    problems = verify(md_text, out_path, stats)
    size_kb = out_path.stat().st_size / 1024
    if problems:
        print(f"\nFAILED verification ({len(problems)} problem(s)):")
        for p in problems:
            print(f"  - {p}")
        return 1

    _, heads, n_tables = docx_blob(out_path)
    print(f"\nOK  {out_path.name}  {size_kb:.0f} KB")
    print(f"    {len(heads)} headings · {n_tables} tables · all source headings present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
