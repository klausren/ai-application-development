"""Layout QA for a .pptx deck: find text that collides or runs off the slide.

Why this exists
---------------
A deck is a 33.867 x 19.05 cm canvas with fixed text-box positions.  Adding a
second language to every box pushes text past the box it was sized for, and
PowerPoint never clips — it just overlaps the next thing.  Counting characters
by hand does not scale to 116 slides, and eyeballing 116 renders is worse.

So: render the deck with LibreOffice, read the *actual* laid-out line boxes out
of the PDF, and report geometry.  This catches what a reader only notices on the
slide that got mangled.

Usage
-----
    python scripts/qa_deck_layout.py lectures/week-05/lecture-bi.pptx [...]

Reports, per page: lines that overflow the footer, lines that collide with
another line, and lines that straddle a named horizontal rule.
"""

import os
import shutil
import subprocess
import sys
import tempfile

import pymupdf
from pptx import Presentation

CM = 72.0 / 2.54                  # points per centimetre
SW, SH = 33.867, 19.05            # slide size, cm
M = 2.22
FOOTER_Y = 18.04
SAFE_BOTTOM = SH - 0.45           # nothing should print below this
MIN_OVERLAP = 0.30                # cm^2 before a collision is worth reporting

SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


def to_pdf(pptx):
    """Convert with LibreOffice, caching on (path, mtime, size) so that re-runs
    during a layout-fix loop cost nothing."""
    src = os.path.abspath(pptx)
    stamp = f"{os.path.getmtime(src):.0f}-{os.path.getsize(src)}"
    cache = os.path.join(tempfile.gettempdir(), "deckqa-cache")
    os.makedirs(cache, exist_ok=True)
    key = os.path.join(cache, os.path.basename(src).rsplit(".", 1)[0] + ".pdf")
    loc = key + ".stamp"
    if os.path.exists(loc) and open(loc).read() == stamp:
        return key, cache
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf",
                    "--outdir", cache, src],
                   check=True, capture_output=True, timeout=300)
    if not os.path.exists(key):
        raise RuntimeError(f"LibreOffice produced no PDF for {pptx}")
    open(loc, "w").write(stamp)
    return key, cache


def header_rules(pptx):
    """Per-page y of the header separator, read off the deck itself.

    The band is not a constant: in the bilingual decks it grows to hold both
    languages plus the protocol chip, so a hard-coded rule y would report
    straddles that are not there (and miss the ones that are).
    """
    out = []
    for slide in Presentation(pptx).slides:
        rule = None
        for sp in slide.shapes:
            try:
                h = sp.height / 360000.0              # EMU -> cm
                y = sp.top / 360000.0
                w = sp.width / 360000.0
            except (TypeError, ValueError):
                continue
            if h <= 0.08 and w >= SW - 0.5 and 1.9 <= y <= 3.2:
                rule = y
        out.append(rule)
    return out


def card_boxes(pptx):
    """Per page, the card-like filled rectangles a line can spill out of.

    Collision detection is blind to a line that overruns the bottom border of
    its own card but hits nothing else — which is exactly what happens when a
    box is sized for one language and then has to hold two.  Only real cards
    count: full-bleed bands, hairlines and small badges are excluded so that a
    note deliberately placed *under* a table is not reported as sticking out.
    """
    out = []
    for slide in Presentation(pptx).slides:
        page_boxes = []
        for sp in slide.shapes:
            try:
                x = sp.left / 360000.0
                y = sp.top / 360000.0
                w = sp.width / 360000.0
                h = sp.height / 360000.0
            except (TypeError, ValueError):
                continue
            if not sp.shape_type or "AUTO_SHAPE" not in str(sp.shape_type):
                continue
            if w < 2.5 or h < 0.7 or w > SW - 0.5:
                continue
            try:
                if sp.fill.type is None or sp.fill.type == 5:    # 5 = background
                    continue
            except (AttributeError, ValueError):
                pass
            page_boxes.append((x, y, w, h))
        out.append(page_boxes)
    return out


def spills(ls, boxes):
    """Lines that start inside a card but end below its bottom edge."""
    bad = []
    for l in ls:
        xc = (l["x0"] + l["x1"]) / 2
        best = None
        for (x, y, w, h) in boxes:
            if not (x <= xc <= x + w):
                continue
            if l["y0"] < y - 0.05 or l["y0"] > y + h:
                continue                       # does not begin inside this card
            if best is None or y > best[1]:
                best = (x, y, w, h)
        if best and l["y1"] > best[1] + best[3] + 0.10:
            bad.append(f"SPILLS card bottom {best[1] + best[3]:.2f} "
                       f"(line ends {l['y1']:.2f}) : {l['txt'][:56]}")
    return bad


def hspills(ls, boxes):
    """Lines that *begin* inside a card but run out past its side edge.

    The vertical rule above is blind to the mirror case: a text box whose left
    edge is tucked inside a filled shape (a fold cell, a band) while its right
    edge sails on past it, printing the line straight over the shape's label.
    Collision detection misses it too — the shape's own label is often narrower
    than the 1 cm the collision gate needs — so the case needs its own rule.
    """
    bad = []
    for l in ls:
        yc = (l["y0"] + l["y1"]) / 2
        best = None
        for (x, y, w, h) in boxes:
            if not (y - 0.05 <= yc <= y + h):
                continue
            if not (x - 0.05 <= l["x0"] <= x + w):
                continue                      # does not begin inside this card
            if best is None or (w + h) < (best[2] + best[3]):
                best = (x, y, w, h)
        if not best:
            continue
        x, y, w, h = best
        right, left = l["x1"] - (x + w), x - l["x0"]
        over = max(right, left)
        if over > 0.12:
            edge = x + w if right > left else x
            bad.append(f"HSPILLS past card {'right' if right > left else 'left'} "
                       f"edge {edge:.2f} (+{over:.2f}cm) : {l['txt'][:52]}")
    return bad


def lines_of(page, rules=()):
    """All visible text lines on a page, in cm, plus any rule they straddle."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk["lines"]:
            txt = "".join(s["text"] for s in ln["spans"]).strip()
            if not txt:
                continue
            size = max(s["size"] for s in ln["spans"]) / CM
            x0, y0, x1, y1 = (v / CM for v in ln["bbox"])
            straddles = [r for r in rules if y0 < r - 0.06 and y1 > r + 0.06]
            out.append({"txt": txt, "size": size,
                        "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                        "straddles": straddles})
    return out


def collides(a, b):
    """Area of a genuine glyph collision, else 0.

    Line boxes on tight leading always overlap by a few points of font padding —
    that is not a collision.  A real one is a large *fraction of the line height*
    landing on another line, so depth ratio is the discriminator, not area.
    """
    w = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    if w <= 1.0:                       # needs real horizontal extent too
        return 0.0
    h = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
    if h <= 0:
        return 0.0
    shortest = min(a["y1"] - a["y0"], b["y1"] - b["y0"])
    return w * h if h / shortest >= 0.35 else 0.0


def dump(path, pages):
    """Print every line box on the given pages, in reading order — for the
    eyeball half of the loop, next to the render."""
    pdf, _ = to_pdf(path)
    doc = pymupdf.open(pdf)
    for pno in pages:
        if pno < 1 or pno > doc.page_count:
            continue
        print(f"\n=== {os.path.basename(path)} page {pno} ===")
        for l in sorted(lines_of(doc[pno - 1]), key=lambda l: (round(l["y0"], 1), l["x0"])):
            print(f"  y {l['y0']:6.2f}-{l['y1']:6.2f}  x {l['x0']:6.2f}-{l['x1']:6.2f}  "
                  f"{l['size'] * CM:5.1f}pt  {l['txt'][:70]}")
    doc.close()


def check(path, head_rule=None):
    pdf, tmp = to_pdf(path)
    doc = pymupdf.open(pdf)
    deck_rules = header_rules(path)
    deck_cards = card_boxes(path)
    problems = 0

    for pno, page in enumerate(doc, 1):
        rule = head_rule
        if rule is None and pno <= len(deck_rules):
            rule = deck_rules[pno - 1]
        ls = lines_of(page, [rule] if rule else [])
        issues = []

        for l in ls:
            if l["y1"] > SAFE_BOTTOM:
                issues.append(f"OFF-PAGE bottom {l['y1']:.2f}cm : {l['txt'][:64]}")
            if l["y0"] < 0.10 or l["x1"] > SW - 0.10 or l["x0"] < -0.10:
                issues.append(f"OFF-CANVAS ({l['x0']:.2f},{l['y0']:.2f})-"
                              f"({l['x1']:.2f},{l['y1']:.2f}) : {l['txt'][:48]}")

        if pno <= len(deck_cards):
            issues.extend(spills(ls, deck_cards[pno - 1]))
            issues.extend(hspills(ls, deck_cards[pno - 1]))

        for i, a in enumerate(ls):
            for b in ls[i + 1:]:
                if max(a["size"], b["size"]) >= 1.4:     # >= 40 pt: the watermark digit
                    continue
                area = collides(a, b)
                if area:
                    issues.append(f"COLLIDE {area:.2f}cm2 "
                                  f"[{a['txt'][:34]}] x [{b['txt'][:34]}]")

        for l in ls:
            for r in l["straddles"]:
                issues.append(f"STRADDLES rule y={r:.2f} : {l['txt'][:60]}")

        if issues:
            problems += len(issues)
            print(f"\n--- page {pno} ({len(issues)}) ---")
            for s in issues[:8]:
                print("   ", s)
            if len(issues) > 8:
                print(f"    ... +{len(issues) - 8} more")

    doc.close()
    print(f"\n{os.path.basename(path)}: {problems} layout issue(s)")
    return problems


if __name__ == "__main__":
    args = sys.argv[1:]
    rule, pages = None, []
    for a in list(args):
        if a.startswith("--rule="):
            rule = float(a.split("=", 1)[1])
            args.remove(a)
        elif a.startswith("--dump="):
            pages = [int(v) for v in a.split("=", 1)[1].split(",")]
            args.remove(a)
    if not args:
        sys.exit("usage: qa_deck_layout.py [--rule=2.95] [--dump=3,7] deck.pptx [...]")
    if pages:
        for p in args:
            dump(p, pages)
        sys.exit(0)
    total = sum(check(p, rule) for p in args)
    sys.exit(1 if total else 0)
