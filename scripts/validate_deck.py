"""Deck validator for the AI Application Development course.

Usage:
    python scripts/validate_deck.py lectures/week-01/lecture-en.pptx [more.pptx ...]

Per deck it prints the slide count and a language verdict chosen by the file
suffix — the same suffix the builder uses for the output language:

  -en.pptx   no CJK anywhere; Chinese on a slide means a zh/en field got swapped
  -zh.pptx   every slide carries Chinese
  -bi.pptx   every slide carries *both* scripts (the whole point of the deck:
             one page must serve the international students and the swap-in
             reading for everyone else, without a second file)

Any deck that embeds media also fails.  Every slide in this course is drawn from
native shapes and charts — there is not a single picture in the package — so a
`ppt/media/` part means something was pasted in by hand and will not survive the
next rebuild from the spec.
"""

import re
import sys
import zipfile

from pptx import Presentation

CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]{2,}")


def slide_text(slide):
    parts = []
    for sh in slide.shapes:
        if sh.has_text_frame:
            parts.append(sh.text_frame.text)
        if sh.has_table:
            for row in sh.table.rows:
                for cell in row.cells:
                    parts.append(cell.text)
    return "\n".join(parts)


def check(path):
    prs = Presentation(path)
    n = len(prs.slides)
    pages = [slide_text(s) for s in prs.slides]

    if path.endswith("-en.pptx"):
        bad, what = [i for i, t in enumerate(pages, 1) if CJK.search(t)], "cjk_leak"
    elif path.endswith("-zh.pptx"):
        bad, what = [i for i, t in enumerate(pages, 1) if not CJK.search(t)], "no_cjk"
    elif path.endswith("-bi.pptx"):
        bad = [i for i, t in enumerate(pages, 1)
               if not (CJK.search(t) and LATIN.search(t))]
        what = "monolingual"
    else:
        bad, what = [], "cjk_leak"

    media = [p for p in zipfile.ZipFile(path).namelist()
             if p.startswith("ppt/media/")]

    ok = not bad and not media
    print(f"{'OK' if ok else 'FAIL':4}  {path}  slides={n}  "
          f"{what}={bad if bad else 'none'}  media={len(media)}")
    return ok


if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        sys.exit(1)
    good = all(check(f) for f in files)
    sys.exit(0 if good else 2)
