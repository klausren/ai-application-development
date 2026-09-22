#!/usr/bin/env python
"""Assert that every assessment-weight statement in the repo is self-consistent.

The course has one authority for assessment weights: the official course standard
《课程标准》§7, plus the instructor's decision that the capstone is an **individual**
project. That resolves to:

    course grade 100
      = formative 50   (attendance 10 + labs 15 + milestone review 15 + AI log 10)
      + summative 50   (a 100-point scale: individual performance 90 + bonus 10)

    individual performance 90
      = project rubric (out of 100) × 0.70 → 63
      + defence rubric (out of 100) × 0.30 → 27

The old team-era figures (capstone = 35% of the grade; rubrics "折算 70%/30%") are
wrong twice over: they contradict the official 50% summative, and they contradict this
repo's own syllabus. This script fails the build if any of them creeps back.

Run:  <managed python> scripts/verify_assessment_weights.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORMATIVE, SUMMATIVE = 50, 50
PERFORMANCE, BONUS = 90, 10
PROJECT_SHARE, DEFENCE_SHARE = 0.70, 0.30
PROJECT_PTS, DEFENCE_PTS = 63, 27

# strings that must NOT appear anywhere (the team-era / 35% scheme)
FORBIDDEN = [
    "35% of the final grade",
    "占期末总评 35%",
    "35 分怎么算",
    "How the 35% is calculated",
    "35 分怎么构成",
    "How the 35% splits",
    "折算 70%）",
    "折算 30%）",
    "Capstone Project (35%)",
]

results: list[tuple[str, object, object]] = []


def check(name: str, got, want) -> None:
    results.append((name, got, want))


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"missing file: {rel}")
    return p.read_text(encoding="utf-8")


def table_rows_after(text: str, heading: str) -> list[str]:
    """Return the FIRST contiguous markdown table under `heading`.

    Only the first block is taken on purpose: sections can contain a second,
    illustrative table (e.g. the 70/30 breakdown in the syllabus) whose numbers must
    not be folded into the item-sum checks.
    """
    tail = text[text.index(heading):]
    rows: list[str] = []
    for ln in tail.splitlines():
        if ln.strip().startswith("|"):
            rows.append(ln)
        elif rows:
            break
    return rows


def nums(rows: list[str], first_col: str) -> list[int]:
    """Pull the points cell (column 3) out of each row whose first cell matches."""
    out = []
    for ln in rows:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(first_col, cells[0]):
            out.append(int(cells[2]))
    return out


def main() -> None:
    syl = read("syllabus.md")

    # ---- syllabus.md: the two top-level halves -----------------------------
    f_rows = table_rows_after(syl, "### 形成性考核")
    f_items = [int(c.strip()) for ln in f_rows
               if re.fullmatch(r"\d+", c := ln.strip().strip("|").split("|")[-1].strip())]
    check("syllabus: formative items sum", sum(f_items), FORMATIVE)

    s_rows = table_rows_after(syl, "### 终结性考核")
    s_items = [int(c.strip()) for ln in s_rows
               if re.fullmatch(r"\d+", c := ln.strip().strip("|").split("|")[-1].strip())]
    check("syllabus: summative items sum (performance + bonus)", sum(s_items), PERFORMANCE + BONUS)
    check("syllabus: individual performance", s_items[0] if s_items else None, PERFORMANCE)
    check("syllabus: bonus", s_items[1] if len(s_items) > 1 else None, BONUS)

    check("course grade halves add up", FORMATIVE + SUMMATIVE, 100)

    # ---- the 70/30 split of individual performance --------------------------
    check("70% of 90 -> project points", round(PERFORMANCE * PROJECT_SHARE), PROJECT_PTS)
    check("30% of 90 -> defence points", round(PERFORMANCE * DEFENCE_SHARE), DEFENCE_PTS)
    check("project + defence points = performance", PROJECT_PTS + DEFENCE_PTS, PERFORMANCE)
    for rel in ("projects/README.md", "projects/capstone/README.md"):
        t = read(rel)
        check(f"{rel}: states 63", "63" in t, True)
        check(f"{rel}: states 27", "27" in t, True)
        check(f"{rel}: states 50%", "50%" in t, True)

    # ---- the two rubrics must each total 100 -------------------------------
    rp = read("projects/capstone/rubric-project.md")
    rp_rows = table_rows_after(rp, "## Overview")
    rp_pts = nums(rp_rows, r"[A-G]")
    check("rubric-project: dimension count", len(rp_pts), 7)
    check("rubric-project: dimensions sum", sum(rp_pts), 100)

    rd = read("projects/capstone/rubric-defence.md")
    rd_rows = table_rows_after(rd, "## Overview")
    rd_pts = nums(rd_rows, r"[1-4]")
    check("rubric-defence: dimension count", len(rd_pts), 4)
    check("rubric-defence: dimensions sum", sum(rd_pts), 100)

    # ---- the old scheme must be gone ---------------------------------------
    scanned = 0
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir() or ".git" in p.parts or p.suffix not in (".md", ".html"):
            continue
        scanned += 1
        t = p.read_text(encoding="utf-8", errors="replace")
        for bad in FORBIDDEN:
            if bad in t:
                check(f"{p.relative_to(ROOT)}: no '{bad}'", "FOUND", "absent")
    print(f"scanned {scanned} markdown/html files for retired wording")

    # ---- report -------------------------------------------------------------
    width = max(len(n) for n, _, _ in results)
    failed = 0
    for name, got, want in results:
        ok = got == want
        failed += not ok
        print(f"{'OK ' if ok else 'FAIL'}  {name:<{width}}  got={got!r:<22} want={want!r}")
    print(f"\n{len(results) - failed} checks passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
