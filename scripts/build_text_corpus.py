"""Build the Week-8 text-classification corpus from this repository's own text.

Why our own text instead of a public corpus:
  * it is ours, so there is no licence question about redistributing it
  * it needs no download, so the lab works offline and the numbers are stable
  * it comes from the same materials the students are reading, so the task is
    the retrieval prerequisite behind the capstone's course-assistant track:
    before an assistant can answer from the materials it has to find the right
    material.

Task: given one English passage, decide which week of the course it came from.

Sources per week (Week 1-6):
    lesson-plans/week-XX/lecture-en.html
    lesson-plans/week-XX/lab-en.html
    textbook/chapter-XX/en.html
    labs/week-XX/lab-handout.md

Anti-leakage scrub — reads the label straight out of the text. Every passage is
stripped of the literal week / lab / CU identifiers, because "Week 3" in the
text makes the task trivially solvable and the accuracy meaningless. The number
of replacements is reported in outputs/w8_corpus_facts.json so the scrub can be
audited rather than trusted.

Writes:
    data/raw/course-text-corpus.jsonl      (committed; our own text, CC BY-NC-SA)
    outputs/w8_corpus_facts.json           (counts, vocab, length distribution, sha256)
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEKS = range(1, 7)
MIN_TOKENS = 20
MAX_TOKENS = 400
SEED = 42

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
CJK = re.compile(r"[\u4e00-\u9fff]")

# --------------------------------------------------------- leak scrubbers ---
# "Week 3", "Week 03", "week-3", "W3", "Week Three" -> generic token
SCRUB = [
    (re.compile(r"\bWeeks?\s*[-–]?\s*0?([0-9]{1,2})\b", re.I), "<WEEK>"),
    (re.compile(r"\bW\s*0?([0-9]{1,2})\b(?=[^0-9]|$)"), "<WEEK>"),
    (re.compile(r"\bCU\s*[\(\[]?\s*0?([0-9]{1,2})\s*[\)\]]?", re.I), "<UNIT>"),
    (re.compile(r"\bLabs?\s*0?([0-9]{1,2})\b", re.I), "<LAB>"),
    (re.compile(r"实验\s*[0-9]{1,2}"), "<LAB>"),
    (re.compile(r"第\s*[0-9]{1,2}\s*周"), "<WEEK>"),
    (re.compile(r"第\s*[0-9]{1,2}\s*次课"), "<UNIT>"),
]
# month / date stamps from the lesson-plan footers
SCRUB += [(re.compile(r"\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b"), "<DATE>")]


class _Text(HTMLParser):
    """Collect visible text; drop script/style; break blocks into paragraphs."""

    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "br", "td", "th",
             "section", "article", "tr", "ul", "ol", "table", "pre"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_paragraphs(path: Path) -> list[str]:
    p = _Text()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    text = "".join(p.out)
    return [seg.strip() for seg in text.split("\n")]


def markdown_paragraphs(path: Path) -> list[str]:
    """Markdown blocks, minus fenced code and table rows (code is a giveaway:
    the same library imports appear in every week)."""
    out, in_fence = [], False
    buf = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            if buf:
                out.append(" ".join(buf)); buf = []
            continue
        if in_fence:
            continue
        s = line.strip()
        if not s:
            if buf:
                out.append(" ".join(buf)); buf = []
            continue
        if s.startswith("|") or set(s) <= set("-|: "):
            continue                       # table row or table rule
        buf.append(s.lstrip("#>*-+ ").strip())
    if buf:
        out.append(" ".join(buf))
    return out


def clean_paragraph(seg: str, counters: dict) -> str | None:
    seg = re.sub(r"\s+", " ", seg).strip()
    seg = re.sub(r"^[\-\u2022\u00b7\d\.\)\s]+", "", seg)      # leading bullets
    for rx, rep in SCRUB:
        seg, n = rx.subn(rep, seg)
        counters["scrubbed"] += n
    if CJK.search(seg):
        counters["dropped_cjk"] += 1
        return None
    letters = sum(ch.isalpha() for ch in seg)
    if letters / max(len(seg), 1) < 0.45:
        counters["dropped_symbolic"] += 1
        return None
    n_tok = len(WORD.findall(seg))
    if n_tok < MIN_TOKENS:
        counters["dropped_short"] += 1
        return None
    if n_tok > MAX_TOKENS:
        # keep the head — truncation is deterministic and documented
        words = seg.split()
        seg = " ".join(words[:MAX_TOKENS])
        counters["truncated"] += 1
    return seg


def main() -> None:
    counters = {"scrubbed": 0, "dropped_cjk": 0, "dropped_symbolic": 0,
                "dropped_short": 0, "truncated": 0, "dropped_dupe": 0}
    rows, seen = [], set()
    per_week = {}
    for w in WEEKS:
        wd = f"{w:02d}"
        sources = ([("lecture", ROOT / f"lesson-plans/week-{wd}/lecture-en.html"),
                    ("lab-plan", ROOT / f"lesson-plans/week-{wd}/lab-en.html"),
                    ("textbook", ROOT / f"textbook/chapter-{wd}/en.html"),
                    ("lab", ROOT / f"labs/week-{wd}/lab-handout.md")])
        n = 0
        for kind, path in sources:
            if not path.exists():
                print(f"  !! missing {path.relative_to(ROOT)}")
                continue
            raw = (html_paragraphs(path) if path.suffix == ".html"
                   else markdown_paragraphs(path))
            for seg in raw:
                text = clean_paragraph(seg, counters)
                if text is None:
                    continue
                key = text.lower()
                if key in seen:
                    counters["dropped_dupe"] += 1
                    continue
                seen.add(key)
                rows.append({"week": w, "source": kind, "text": text})
                n += 1
        per_week[w] = n

    random.Random(SEED).shuffle(rows)                 # deterministic order
    out_path = ROOT / "data/raw/course-text-corpus.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({"id": i, **r}, ensure_ascii=False) + "\n")

    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    lens = sorted(len(WORD.findall(r["text"])) for r in rows)
    vocab_all = set()
    for r in rows:
        vocab_all.update(t.lower() for t in WORD.findall(r["text"]))

    facts = {
        "task": "given one English passage, name the course week it came from",
        "classes": [f"week-{w:02d}" for w in WEEKS],
        "n_passages": len(rows),
        "per_class": {f"week-{w:02d}": per_week[w] for w in WEEKS},
        "passages_by_source": {k: sum(1 for r in rows if r["source"] == k)
                               for k in ("lecture", "lab-plan", "textbook", "lab")},
        "min_word_tokens": MIN_TOKENS,
        "max_word_tokens": MAX_TOKENS,
        "token_length": {
            "min": lens[0], "p25": lens[len(lens) // 4],
            "median": lens[len(lens) // 2], "p75": lens[3 * len(lens) // 4],
            "p95": lens[int(len(lens) * 0.95)], "max": lens[-1],
            "mean": round(sum(lens) / len(lens), 1),
        },
        "vocab_full": len(vocab_all),
        "scrub_counters": counters,
        "note_on_scrub": ("week / lab / CU identifiers are replaced with <WEEK>, "
                          "<LAB>, <UNIT> before the corpus is written; without this "
                          "the label is literally in the text and accuracy is "
                          "meaningless. Counted above so the scrub is auditable."),
        "sha256": digest,
        "source_note": ("built from this repository's own Week 1-6 materials "
                        "(CC BY-NC-SA 4.0); regenerate with "
                        "python scripts/build_text_corpus.py"),
    }
    facts_path = ROOT / "outputs/w8_corpus_facts.json"
    facts_path.parent.mkdir(parents=True, exist_ok=True)
    facts_path.write_text(json.dumps(facts, indent=1, ensure_ascii=False))

    print(f"passages : {len(rows)}")
    print("per week :", per_week)
    print("by source:", facts["passages_by_source"])
    print("tokens   :", facts["token_length"])
    print("vocab    :", len(vocab_all))
    print("scrubbed identifiers:", counters["scrubbed"])
    print("dropped  :", {k: v for k, v in counters.items() if k.startswith("dropped")})
    print("sha256   :", digest[:16], "...")
    print("wrote", out_path.relative_to(ROOT), "and", facts_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
