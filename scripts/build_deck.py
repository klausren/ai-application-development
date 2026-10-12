"""Deck builder for the AI Application Development course.

Renders a 16:9 (33.867 x 19.05 cm) lecture deck from a language-neutral slide
spec.  Every visual is a native PowerPoint shape, table or chart — no raster or
SVG assets are embedded, so PowerPoint never shows "picture can't be displayed".

Usage:
    python scripts/build_deck.py week-03
"""

import re
import sys
from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

# ---------------------------------------------------------------- palette ----
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BG         = RGBColor(0xFF, 0xFF, 0xFF)
TEXT       = RGBColor(0x1F, 0x29, 0x37)
MUTED      = RGBColor(0x6B, 0x72, 0x80)
BORDER     = RGBColor(0xE5, 0xE7, 0xEB)
CARD       = RGBColor(0xF0, 0xF5, 0xFC)
ACCENT     = RGBColor(0x1E, 0x4F, 0xA8)
ACCENT_BR  = RGBColor(0x3D, 0x7B, 0xD9)
DEEP       = RGBColor(0x0E, 0x3F, 0x8C)
GREEN      = RGBColor(0x05, 0x96, 0x69)
GREEN_BG   = RGBColor(0xEC, 0xFD, 0xF5)
ORANGE     = RGBColor(0xD9, 0x77, 0x06)
ORANGE_BG  = RGBColor(0xFF, 0xFB, 0xEB)
RED        = RGBColor(0xB9, 0x1C, 0x1C)
RED_BG     = RGBColor(0xFE, 0xF2, 0xF2)
CODE_BG    = RGBColor(0x0F, 0x17, 0x2A)
CODE_TEXT  = RGBColor(0xE2, 0xE8, 0xF0)
GHOST      = RGBColor(0xF5, 0xF7, 0xFA)

FONT = "Source Han Sans SC"
CODE_FONT = "Menlo"

SW, SH = 33.867, 19.05
M = 2.22                      # outer margin
CW = SW - 2 * M               # content width
HEADER_H = 2.12
BODY_TOP = 2.90
FOOTER_Y = 18.04


# -------------------------------------------------- bilingual (bi) support ----
# "bi" mode renders one deck carrying both languages: English stays at its
# original size, Chinese follows on the next line at 0.78x in muted grey.
# L() returns a Bi (a str that also carries its translation) so every existing
# call site becomes bilingual for free; text() emits the second line.
BI = False                    # set by build(); read by the few special-cased renderers
SEC_RATIO = 0.78              # secondary-language size, relative to the primary
SEC_MIN = 8.0                 # never render the secondary smaller than this
SEC_COLOR = MUTED
SEC_SEP = " ｜ "              # joins the two languages when they share a line


class Bi(str):
    """A str that remembers its translation in ``.sec``.

    Concatenation is preserved in both directions so idioms such as
    ``"• " + L(x, lang)`` keep working: ``"• " + Bi("a", "甲")`` gives
    ``Bi("• a", "• 甲")``.
    """

    sec = ""

    def __new__(cls, primary, sec=""):
        o = super().__new__(cls, primary)
        o.sec = sec or ""
        return o

    def __add__(self, other):
        tail = other.sec if isinstance(other, Bi) else (other if isinstance(other, str) else "")
        return Bi(str.__add__(self, other), str.__add__(self.sec, tail))

    def __radd__(self, other):
        other = other if isinstance(other, str) else str(other)
        return Bi(str.__add__(other, str(self)), str.__add__(other, self.sec))


def sec_size(primary_pt):
    return max(SEC_MIN, round(primary_pt * SEC_RATIO, 1))


# A rough line-break model.  It only ever decides *where the next block starts*,
# so it must err generous: an under-estimate is exactly what drops a follow-on
# block onto the Chinese line.  CJK glyphs are full-width, Latin ones a bit over
# half, measured against what LibreOffice actually did.
PT_CM = 28.3465
CJK_CHAR = re.compile(r"[\u2e80-\u9fff\uff00-\uffef\u3000-\u303f]")
LATIN_W = 0.55                 # average Latin glyph advance, in em (measured)
CJK_W = 1.00                   # CJK glyphs are exactly one em
LEAD = 1.20                    # line pitch = spacing x LEAD em, measured
SEC_LEAD = 1.5                 # pt of space_before on a secondary paragraph
SEC_PITCH = 1.25               # secondary paragraphs resolve ~1.5 em, not 1.26
SEC_COLOR_LIGHT = RGBColor(0xCF, 0xDD, 0xF2)   # secondary type on a dark fill


def wrap_lines(parts, width_cm):
    """Line count when ``[(text, size_pt), ...]`` wraps into ``width_cm``."""
    if not any(str(t) for t, _ in parts):
        return 0
    limit = width_cm * PT_CM
    lines, used = 1, 0.0
    for text, size in parts:
        for ch in str(text):
            if ch == "\n":
                lines, used = lines + 1, 0.0
                continue
            w = size * (CJK_W if CJK_CHAR.match(ch) else LATIN_W)
            if used + w > limit and used > 0:
                lines, used = lines + 1, 0.0
            used += w
    return lines


def est_lines(s, size_pt, width_cm):
    return wrap_lines([(s, size_pt)], width_cm)


def est_block_h(s, size_pt, width_cm, spacing=1.14):
    """Height in cm that ``s`` will occupy, wrapping included.

    The leading factor is measured, not assumed: LibreOffice lays out a
    ``nspPr`` line-spacing multiple against a 1.20 em natural line, so reading
    ``spacing`` as em under-reports every block by a fifth.
    """
    return est_lines(s, size_pt, width_cm) * size_pt * spacing * LEAD / PT_CM


def para_h(v, size_pt, width_cm, spacing=1.25, sec_inline=False):
    """Height of the paragraph(s) ``text()`` will emit for a single value.

    Mirrors :func:`text` exactly — including the extra ``space_before`` that
    keeps the two languages' descenders apart — because anything less lands the
    next block on top of the Chinese line.

    The secondary line carries its own pitch: LibreOffice does not resolve
    ``<a:lnSpc>`` the same way for a *second* paragraph as for a first one.  A
    Chinese block measured at 8.58 pt / 105 % renders on a 1.5 em pitch, not the
    1.26 em a naive reading gives, so the model uses :data:`SEC_PITCH`.
    """
    prim, sec = str(v), getattr(v, "sec", "")
    if sec_inline and sec:
        parts = [(prim, size_pt),
                 (SEC_SEP, sec_size(size_pt)),
                 (sec, sec_size(size_pt))]
        return wrap_lines(parts, width_cm) * size_pt * spacing * LEAD / PT_CM
    h = est_block_h(prim, size_pt, width_cm, spacing)
    if sec:
        h += SEC_LEAD / PT_CM + est_block_h(sec, sec_size(size_pt), width_cm,
                                            SEC_PITCH)
    return h


def text_h(runs, size_pt, width_cm, spacing=1.25, space_after=0,
           sec_inline=False):
    """Height of the whole text box :func:`text` will emit for ``runs``."""
    raw = [runs] if isinstance(runs, (str, Bi)) else list(runs)
    total = 0.0
    for item in raw:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], dict):
            v, opts = item
        elif isinstance(item, (list, tuple)):
            v, opts = "".join(str(x[0] if isinstance(x, tuple) else x)
                              for x in item), {}
        else:
            v, opts = item, {}
        total += para_h(v, opts.get("size", size_pt), width_cm, spacing,
                        sec_inline)
        total += space_after / PT_CM
    return total


def flow(v, sep=" "):
    """Join a hard-wrapped spec string into one flowing paragraph.

    A literal LF inside a run is collapsed to a space by LibreOffice, and the
    breaks a spec author put in for the *mono* 12.5 pt column land nowhere near
    where the bilingual column breaks.  Re-joining makes the estimated line
    count match what is actually drawn, instead of over-counting every segment.
    Use ``sep=" · "`` for lists whose items must stay distinguishable.
    """
    if isinstance(v, Bi):
        return Bi(sep.join(str(v).split("\n")),
                  sep.join(v.sec.split("\n")) if v.sec else "")
    return sep.join(str(v).split("\n"))


def fit_size(measure, sizes):
    """First (largest) size in ``sizes`` for which ``measure(size)`` fits.

    ``measure`` must return the height the block needs; the caller compares it
    with the space available.  Returns the last size when nothing fits, so the
    caller can still report a deficit rather than raise.
    """
    for s in sizes:
        if measure(s):
            return s
    return sizes[-1]


def est_table_h(cols, rows, widths, body_pt, head_pt, pad=0.20):
    """Height a PowerPoint table will actually take once its cells wrap.

    Table rows are a *minimum* height — PowerPoint grows them to fit, which is
    why a bilingual table runs past the ``note`` parked under its nominal box.
    """
    def cell(v, wcm, pt):
        return para_h(v, pt, max(1.0, wcm - 0.40)) + pad

    total = max(cell(c, widths[j], head_pt) for j, c in enumerate(cols))
    for row in rows:
        total += max(cell(v, widths[j], body_pt) for j, v in enumerate(row))
    return total


# ---------------------------------------------------------------- helpers ----
def L(item, lang):
    """Pick a language from a {'zh': .., 'en': ..} value, or return plain text.

    In ``bi`` mode the result is a :class:`Bi` carrying the *other* language in
    ``.sec`` (English primary, Chinese secondary).  Identical translations
    collapse — the Chinese line is suppressed when it would just repeat the
    English one.
    """
    if isinstance(item, dict):
        if lang == "bi":
            en = item.get("en") or item.get("zh") or ""
            zh = item.get("zh") or ""
            return Bi(en, zh if zh and zh != en else "")
        return item.get(lang) or item.get("en") or item.get("zh") or ""
    return item


def S(item, lang):
    """Always single-language — for meta labels (page numbers, chips, footers).

    These sit in boxes too short to stack a second line, and they carry no
    teaching content, so they stay in the deck's primary language (English).
    """
    if isinstance(item, dict):
        return item.get("en") or item.get("zh") or "" if lang == "bi" \
            else item.get(lang) or item.get("en") or item.get("zh") or ""
    return item


def _txbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    tb = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tb, tf


def _sec_opts(opts, default_size, sec_color=None):
    """Font options for the secondary-language line: smaller, grey, never bold.

    On a dark chip the grey would vanish, so callers that fill with DEEP/ACCENT
    pass a light :data:`SEC_COLOR_LIGHT` instead.
    """
    o = dict(opts)
    o["size"] = sec_size(o.get("size", default_size))
    o["color"] = sec_color or SEC_COLOR
    o["bold"] = False
    o.pop("italic", None)
    return o


def text(slide, x, y, w, h, runs, size=13, bold=False, color=TEXT,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.25,
         font=FONT, space_after=0, sec_inline=False, sec_color=None):
    """runs: str  ->  single paragraph;  list[str] -> one paragraph per item.

    In ``bi`` mode any run carrying a translation (a :class:`Bi`) is followed by
    that translation — on a new line by default, or on the same line when
    ``sec_inline=True`` (used where a second line would not fit).
    """
    tb, tf = _txbox(slide, x, y, w, h, anchor)

    # -- normalise into [ [(text, opts), ...], ... ], one list per paragraph --
    raw = [runs] if isinstance(runs, str) else list(runs)
    paras = []
    for item in raw:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], dict):
            paras.append([item])                    # (text, opts) -> one run
        elif isinstance(item, (list, tuple)):
            paras.append(list(item))
        else:
            paras.append([item])

    # -- expand each paragraph's translations into extra blocks --
    blocks = []                                     # (runs, is_secondary, after)
    for runs_ in paras:
        prim, sec = [], []
        hard = False
        for r in runs_:
            txt, opts = (r if isinstance(r, tuple) else (r, {}))
            prim.append((str(txt), opts))
            if isinstance(txt, Bi) and txt.sec:
                sec.append((txt.sec, opts))
            if isinstance(txt, Bi) and "\n" in str(txt) and len(runs_) == 1:
                hard = True
        if hard and not sec_inline:
            # A literal LF inside a run does not pick up <a:lnSpc>, so embedded
            # breaks render tighter than wrapped ones.  Emitting one paragraph
            # per line restores a single, predictable pitch — and the height
            # model can then be trusted.  (Bi only: the mono path is frozen.)
            o = prim[0][1]
            for ln in str(prim[0][0]).split("\n"):
                blocks.append(([(ln, o)], False, 0))
            if sec:
                so = _sec_opts(sec[0][1], size, sec_color)
                for ln in sec[0][0].split("\n"):
                    blocks.append(([(ln, so)], True, 0))
            continue
        if sec_inline:
            if sec:
                prim = prim + [(SEC_SEP, _sec_opts({}, size, sec_color))] + \
                       [(t, _sec_opts(o, size, sec_color)) for t, o in sec]
            blocks.append((prim, False, space_after))
            continue
        blocks.append((prim, False, 0 if sec else space_after))
        if sec:
            blocks.append(([(t, _sec_opts(o, size, sec_color)) for t, o in sec],
                           True, space_after))

    for i, (runs_, is_sec, after) in enumerate(blocks):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.05 if is_sec else spacing
        if is_sec:
            p.space_before = Pt(1.5)      # keep the two languages' descenders apart
        if after:
            p.space_after = Pt(after)
        for txt, opts in runs_:
            run = p.add_run()
            run.text = txt
            f = run.font
            f.name = opts.get("font", font)
            f.size = Pt(opts.get("size", size))
            f.bold = opts.get("bold", bold)
            f.italic = opts.get("italic", False)
            f.color.rgb = opts.get("color", color)
        if tf.word_wrap is None:
            tf.word_wrap = True
    return tb


def style_cell(cell, item, lang, size, bold, color, ratio=0.85, sec_color=SEC_COLOR):
    """Write one bilingual table cell: English first, Chinese on the line below.

    Tables are the one place where a second *paragraph* beats a second *run*:
    PowerPoint grows the row to fit, so nothing is ever clipped.  Dark header
    cells need their own lighter secondary colour to stay legible.
    """
    value = L(item, lang)
    sec = getattr(value, "sec", "")
    cell.text = str(value)
    p = cell.text_frame.paragraphs[0]
    p.runs[0].font.size = Pt(size)
    p.runs[0].font.bold = bold
    p.runs[0].font.name = FONT
    p.runs[0].font.color.rgb = color
    if sec:
        p2 = cell.text_frame.add_paragraph()
        p2.line_spacing = 1.0
        r2 = p2.add_run()
        r2.text = sec
        r2.font.size = Pt(max(SEC_MIN, round(size * ratio, 1)))
        r2.font.bold = False
        r2.font.name = FONT
        r2.font.color.rgb = sec_color


def rect(slide, x, y, w, h, fill=WHITE, line=None, line_w=0.75,
         shape=MSO_SHAPE.RECTANGLE, adj=None):
    sp = slide.shapes.add_shape(shape, Cm(x), Cm(y), Cm(w), Cm(h))
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(line_w)
    sp.text_frame.word_wrap = True
    if adj is not None:
        try:
            sp.adjustments[0] = adj
        except Exception:
            pass
    return sp


def arrow(slide, x, y, w, h, color=ACCENT_BR, shape=MSO_SHAPE.RIGHT_ARROW):
    sp = rect(slide, x, y, w, h, fill=color, shape=shape)
    return sp


def hexc(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def col(v, default=TEXT):
    if v is None:
        return default
    if isinstance(v, RGBColor):
        return v
    return hexc(v)


# ------------------------------------------------------------ slide frame ----
def new_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, SW, SH, fill=BG)
    return s


HEAD_BOX = CW - 8.0            # title column, leaving room for the right meta
HEAD_RIGHT_W = 7.6
BAND_MAX = 3.00                # the rule may not move down into the body


def header(slide, title, right, lang, subtitle=None):
    """Slide running head.

    In ``bi`` mode the band has to size itself.  Two blocks share it — the
    title/subtitle stack on the left and the protocol chip on the right — and
    whichever is taller decides where the rule goes.  Sizing off the left block
    alone is what let a three-line ``PROTO`` chip hang through the rule.
    """
    band = HEADER_H
    right_v, rs = None, 10.0
    ts, ss, h1, h2, gap, y_sub = 15.5, 10.0, 0.0, 0.0, 0.0, 0.0
    if BI:
        title_v = L(title, lang)
        sub_v = L(subtitle, lang) if subtitle else None
        for ts, ss, gap in ((15.5, 10.0, 0.12), (15.0, 9.8, 0.12),
                            (14.0, 9.4, 0.10), (13.5, 9.0, 0.10),
                            (13.0, 8.8, 0.08), (12.0, 8.4, 0.08),
                            (11.0, 8.0, 0.06)):
            h1 = para_h(title_v, ts, HEAD_BOX, 1.14)
            h2 = para_h(sub_v, ss, HEAD_BOX, 1.14) if sub_v else 0.0
            gap = gap if sub_v else 0.0
            if 0.36 + h1 + gap + h2 <= 2.92:
                break
        y_sub = 0.36 + h1 + gap
        band = max(HEADER_H, 0.36 + h1 + gap + h2 + 0.14)
        if right:
            right_v, rs = L(right, lang), 10.0
            # The protocol chip is the one block that can outgrow the band.  If
            # both languages will not fit above the rule at a readable size, drop
            # to the primary language — it is a spec sheet, not teaching text.
            if 0.86 + para_h(right_v, rs, HEAD_RIGHT_W, 1.16, True) > 2.86:
                right_v = S(right, lang)
            band = max(band, 0.86 + para_h(right_v, rs, HEAD_RIGHT_W, 1.16, True)
                       + 0.14)
        band = min(band, BAND_MAX)
        rect(slide, 0, 0, SW, band, fill=WHITE)
        rect(slide, 0, band, SW, 0.04, fill=BORDER)
        text(slide, M, 0.36, HEAD_BOX, h1 + 0.4, title_v, size=ts, bold=True,
             color=DEEP, spacing=1.14)
        if sub_v:
            text(slide, M, y_sub, HEAD_BOX, h2 + 0.3, sub_v, size=ss,
                 color=MUTED, spacing=1.14)
    else:
        rect(slide, 0, 0, SW, band, fill=WHITE)
        rect(slide, 0, band, SW, 0.04, fill=BORDER)
        if subtitle:
            text(slide, M, 0.62, HEAD_BOX, 0.72, L(title, lang), size=19,
                 bold=True, color=DEEP)
            text(slide, M, 1.38, HEAD_BOX, 0.5, L(subtitle, lang), size=11.5,
                 color=MUTED)
        else:
            text(slide, M, 0.71, HEAD_BOX, 0.72, L(title, lang), size=19,
                 bold=True, color=DEEP)
    if right and not BI:
        text(slide, SW - M - HEAD_RIGHT_W, 0.82, HEAD_RIGHT_W, 0.5,
             L(right, lang), size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    elif right_v is not None:
        text(slide, SW - M - HEAD_RIGHT_W, 0.86, HEAD_RIGHT_W, 2.0, right_v,
             size=rs, color=MUTED, align=PP_ALIGN.RIGHT, spacing=1.16,
             sec_inline=True)


def footer(slide, week, page, total):
    text(slide, M, FOOTER_Y, 12, 0.45,
         f"AI Application Development · Week {week}", size=10, color=MUTED)
    text(slide, SW - M - 3, FOOTER_Y, 3, 0.45, f"{page:02d} / {total}",
         size=10, color=MUTED, align=PP_ALIGN.RIGHT)


# ------------------------------------------------------------- renderers ----
def r_cover(slide, sp, ctx):
    lang, week = ctx["lang"], ctx["week"]
    rect(slide, 0, 0, SW, 0.37, fill=ACCENT)
    rect(slide, 0, 0.37, SW, 0.16, fill=ACCENT_BR)
    text(slide, SW / 2, 2.38, SW / 2 - M, 12.7, f"{week:02d}", size=190,
         bold=True, color=CARD, align=PP_ALIGN.RIGHT)
    text(slide, M, 2.38, 20, 0.6, L(sp["kicker"], lang), size=11.5, bold=True,
         color=ACCENT)
    rect(slide, M, 3.52, 1.69, 0.11, fill=ACCENT)
    if BI:
        # Both titles are on the slide, so an English ``title_sub`` would just
        # repeat the English title — it keeps its own tagline slot instead.
        text(slide, M, 4.05, CW, 1.3, S(sp["title"], lang), size=36, bold=True, color=DEEP)
        zh = sp["title"].get("zh") if isinstance(sp["title"], dict) else ""
        if zh:
            text(slide, M, 5.85, CW, 1.2, zh, size=23, bold=True, color=TEXT)
        if sp.get("title_sub"):
            text(slide, M, 7.55, CW, 0.9, S(sp["title_sub"], lang), size=15, color=MUTED)
        text(slide, M, 9.40, CW, 2.2, L(sp["subtitle"], lang), size=12.5, color=MUTED)
    else:
        text(slide, M, 4.47, CW, 1.5, L(sp["title"], lang), size=40, bold=True, color=DEEP)
        if sp.get("title_sub"):
            text(slide, M, 6.2, CW, 2.7, L(sp["title_sub"], lang), size=25, color=TEXT)
        text(slide, M, 9.29, CW, 0.8, L(sp["subtitle"], lang), size=14, color=MUTED)
    chips = sp["chips"]
    gap = 0.62
    total_w = CW - gap * (len(chips) - 1)
    widths = [total_w * c[1] / sum(c[1] for c in chips) for c in chips]
    x = M
    for (label, _), w in zip(chips, widths):
        rect(slide, x, 14.71, w, 0.9, fill=CARD)
        text(slide, x + 0.48, 14.9, w - 0.96, 0.53, S(label, lang), size=11.5,
             bold=True, color=DEEP)
        x += w + gap
    rect(slide, M, 16.30, 1.16, 1.16, fill=DEEP)
    text(slide, M + 0.16, 16.56, 0.85, 0.64, f"W{week}", size=11, bold=True, color=WHITE)
    text(slide, M + 1.48, 16.62, 16, 0.56, L(sp.get("lecturer",
         "Lecturer: ____________  ·  School of Software Engineering"), lang),
         size=11, color=MUTED)


def r_contents(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, {"zh": "目录", "en": "Contents"}, sp.get("right"), lang)
    footer(slide, week, sp["page"], total)
    rect(slide, M, BODY_TOP, 7.94, 13.76, fill=CARD)
    PW = 6.56                                   # panel content width
    PANEL_BOT = BODY_TOP + 13.76
    # Bilingual: the count, its label, the divider, the tagline and the timing
    # box all stack on *measured* heights.  The mono layout keeps the original
    # hard-coded coordinates (26 pt count, divider at 8.31, timing at 11.69).
    cnt = L(sp["count"], lang)
    cnt_h = para_h(cnt, 26, PW, 1.14) if BI else 1.08
    text(slide, M + 0.69, 6.01, PW, cnt_h + 0.30, cnt, size=26,
         bold=True, color=DEEP)
    cl = L(sp["count_label"], lang)
    if BI:
        cl_y = 6.01 + cnt_h + 0.20
        cl_h = para_h(cl, 11.5, PW, 1.14)
        sep_y = cl_y + cl_h + 0.16
    else:
        cl_y, cl_h, sep_y = 7.30, 0.53, 8.31
    text(slide, M + 0.69, cl_y, PW, cl_h + 0.25, cl, size=11.5, bold=True,
         color=MUTED)
    rect(slide, M + 0.69, sep_y, PW, 0.05, fill=ACCENT_BR)

    tg = L(sp["tagline"], lang)
    tm = L(sp["timing"], lang)
    if BI:
        # The mono column is hand-wrapped for 12.5 pt; two languages in the same
        # 6.56 cm column break elsewhere, so re-flow both blocks and let them
        # wrap naturally.  The timing box is pinned to the panel bottom and the
        # tagline takes whatever is left above it.
        tg, tm = flow(tg), flow(tm, " · ")
        t_avail = PANEL_BOT - 0.28 - 11.69
        tsz = fit_size(lambda s: para_h(tm, s, 5.82, 1.28) + 0.44 <= t_avail,
                       (11, 10.4, 9.8, 9.2, 8.6, 8.0, 7.4))
        tb_h = para_h(tm, tsz, 5.82, 1.28) + 0.44
        tg_y = sep_y + 0.26
        tg_room = max(1.2, PANEL_BOT - 0.28 - tb_h - 0.34 - tg_y)
        tg_size = fit_size(lambda s: para_h(tg, s, PW, 1.30) <= tg_room,
                           (12.5, 11.8, 11.0, 10.2, 9.4, 8.8, 8.2, 7.6, 7.0))
        tg_h = para_h(tg, tg_size, PW, 1.30)
        text(slide, M + 0.69, tg_y, PW, tg_h + 0.40, tg, size=tg_size,
             color=TEXT, spacing=1.30)
        tb_y = PANEL_BOT - 0.28 - tb_h
        rect(slide, M + 0.69, tb_y, PW, tb_h, fill=WHITE, line=BORDER)
        text(slide, M + 1.06, tb_y + 0.22, 5.82, tb_h - 0.44, tm, size=tsz,
             color=MUTED, spacing=1.28)
    else:
        text(slide, M + 0.69, 8.78, PW, 2.49, tg, size=12.5, color=TEXT,
             spacing=1.4)
        rect(slide, M + 0.69, 11.69, PW, 1.91, fill=WHITE, line=BORDER)
        text(slide, M + 1.06, 11.96, 5.82, 1.38, tm, size=11.5,
             color=MUTED, spacing=1.35)

    x0, w = 10.90, 20.74
    # Bilingual part cards share one line per pair: title on line 1, the
    # one-line description on line 2.  Stacking either pair (English above
    # Chinese) needs six rendered lines and overruns the 2.12 cm card, so both
    # use ``sec_inline``.  ``title_en`` — a short alias of the English title
    # ("Loss" for "The Loss: What We Optimise") — is dropped in bi mode: it
    # would be a third line saying what line 1 already says.
    y = 4.58
    tsz = 11.5
    if BI:
        _rows = [(L(p["title"], lang), L(p["desc"], lang)) for p in sp["parts"]]
        tsz = fit_size(
            lambda s: all(0.26 + para_h(t, s, 17.0, 1.2, True)
                          + 0.14 + para_h(d, 9, 17.36, 1.25, True) <= 1.96
                          for t, d in _rows),
            (13.5, 12.6, 11.8, 11.5, 11.0, 10.4, 9.8, 9.2))
    for i, part in enumerate(sp["parts"]):
        rect(slide, x0, y, w, 2.12, fill=WHITE, line=BORDER)
        rect(slide, x0 + 0.21, y + 0.34, 1.38, 1.38, fill=CARD)
        text(slide, x0 + 0.21, y + 0.62, 1.38, 0.64, f"{i + 1:02d}", size=17,
             bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
        if BI:
            tv, dv = L(part["title"], lang), L(part["desc"], lang)
            tv_h = para_h(tv, tsz, 17.0, 1.2, True)
            text(slide, x0 + 2.12, y + 0.26, 17.0, tv_h + 0.30, tv,
                 size=tsz, bold=True, color=DEEP, sec_inline=True)
            text(slide, x0 + 2.12, y + 0.26 + tv_h + 0.14, 17.36, 1.10,
                 dv, size=9, color=MUTED, sec_inline=True)
        else:
            text(slide, x0 + 2.12, y + 0.39, 12, 0.77, L(part["title"], lang), size=16,
                 bold=True, color=DEEP)
            if part.get("title_en"):
                text(slide, x0 + 2.12 + 0, y + 1.19, 12, 0.45,
                     L(part["title_en"], lang), size=11.5, color=ACCENT_BR, bold=True)
            text(slide, x0 + 2.12, y + 1.79 if not part.get("title_en") else y + 1.72,
                 17.36, 0.45, L(part["desc"], lang), size=11.5, color=MUTED)
        # chevron instead of an icon asset
        arrow(slide, x0 + w - 0.95, y + 0.79, 0.5, 0.53, color=ACCENT_BR)
        y += 2.09


def r_section(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    rect(slide, 0, 0, SW, 0.26, fill=ACCENT)
    text(slide, SW - M - 18.5, 1.06, 18.52, 15.69, sp["num"], size=170, bold=True,
         color=CARD, align=PP_ALIGN.RIGHT)
    rect(slide, M + 0.16, 2.91, 3.44, 3.44, fill=DEEP)
    text(slide, M + 1.06, 3.65, 1.67, 1.98, sp["num"], size=32, bold=True,
         color=WHITE, align=PP_ALIGN.CENTER)
    cards = sp.get("pillars", [])
    pillar_top, pillar_h = 13.89, 2.25
    if BI and cards:
        # Pillar captions are two languages each; give them the room the mono
        # deck never needed, still clear of the footer.
        pillar_h = min(17.60 - pillar_top, 2.95)
    TW, t_y = 14.0, 3.07
    tv = L(sp["title"], lang)
    lv = L(sp["lead"], lang) if sp.get("lead") else None
    limit = (pillar_top - 0.25) if cards else 16.2
    tsz = 30
    if BI:
        # The English title wraps to three lines on the long Lab titles and the
        # Chinese title doubles it again, so the lead has to start below the
        # measured stack rather than at a fixed 7.6.
        tsz = fit_size(lambda s: t_y + para_h(tv, s, TW, 1.15) + 0.5
                       + (para_h(lv, 15, 24, 1.5) if lv else 0.0) <= limit,
                       (30, 27, 24, 21.5, 19, 17, 15.5))
    t_h = para_h(tv, tsz, TW, 1.15) if BI else 1.4
    text(slide, M + 4.39, t_y, TW, t_h + 0.3, tv, size=tsz, bold=True, color=DEEP)
    if sp.get("title_en") and not BI:
        text(slide, M + 4.39, 4.63, 14, 0.85, L(sp["title_en"], lang), size=15, color=ACCENT_BR)
    if lv:
        y0 = max(7.6, t_y + t_h + 0.5) if BI else 7.6
        size = 15
        if BI:
            room = limit - y0
            size = fit_size(lambda s: para_h(lv, s, 24, 1.5) <= room,
                            (15, 14, 13, 12, 11.5, 11))
        text(slide, M, y0, 24, para_h(lv, size, 24, 1.5) + 0.4, lv, size=size,
             color=TEXT, spacing=1.5)
    if cards:
        gap = 0.63
        w = (CW - gap * (len(cards) - 1)) / len(cards)
        x = M
        for c in cards:
            rect(slide, x, pillar_top, w, pillar_h, fill=CARD)
            rect(slide, x, pillar_top, w, 0.07, fill=ACCENT_BR)
            if BI:
                cv, sv = L(c["title"], lang), L(c["sub"], lang)
                cw = w - 1.16
                cs = fit_size(
                    lambda s: 0.41 + para_h(cv, s, cw, 1.2, True)
                              + 0.12 + para_h(sv, 9.5, cw, 1.25) <= pillar_h - 0.16,
                    (13, 12.2, 11.4, 10.6, 10.0))
                c_h = para_h(cv, cs, cw, 1.2, True)
                text(slide, x + 0.58, pillar_top + 0.41, cw, c_h + 0.3, cv,
                     size=cs, bold=True, color=DEEP, sec_inline=True)
                text(slide, x + 0.58, pillar_top + 0.41 + c_h + 0.12, cw,
                     pillar_h - 0.53 - c_h, sv, size=9.5, color=MUTED,
                     spacing=1.25)
            else:
                text(slide, x + 0.58, pillar_top + 0.48, w - 1.16, 0.71,
                     L(c["title"], lang), size=15, bold=True, color=DEEP)
                text(slide, x + 0.58, pillar_top + 1.30, w - 1.16, 0.48,
                     L(c["sub"], lang), size=11, color=MUTED)
            x += w + gap
    footer(slide, week, sp["page"], total)


CARD_PAD_TOP = 0.42             # card padding above the title
CARD_PAD_BOT = 0.30
CARD_TITLE_GAP = 0.24
BODY_FLOOR = 9.0                # smallest body type the bilingual grid will use
GRID_BOTTOM = FOOTER_Y - 0.32   # the last row may not print below this


def _card_runs(c, lang, bi):
    """The bullets a card will render, tags folded in as a final line.

    The bottom-right badge is positioned off the card's fixed height, which
    bilingual bullets overrun — so in ``bi`` mode the tag flows in as text.
    """
    body = c.get("body") or []
    if isinstance(body, str):
        body = [body]
    runs = [b if isinstance(b, tuple)
            else ("• " + L(b, lang),
                  {} if bi else {"size": c.get("body_size", 12)})
            for b in body]
    if bi and c.get("tag"):
        runs.append(("→ " + L(c["tag"], lang), {"color": ACCENT_BR}))
    return runs


def _card_grid(cards, lang, bi, w, top, h_spec, gap, cols, bs_spec):
    """Largest body size (and the row height that goes with it) at which every
    card's bilingual content fits the grid.

    Bilingual bullets run roughly twice as tall as the English originals, so a
    spec sized for one language will not hold two.  Shrink the body, then the
    leading, then let the card grow — in that order, because type size is what
    the reader actually pays for.
    """
    bw = w - 1.24
    rows = (len(cards) + cols - 1) // cols
    if not bi:
        return bs_spec, h_spec, 1.4
    titles = [L(c["title"], lang) for c in cards]
    runs = [_card_runs(c, lang, bi) for c in cards]
    sizes = []
    s = bs_spec
    while s >= BODY_FLOOR - 1e-6:
        sizes.append(round(s, 1))
        s -= 0.5
    best = None
    for spacing in (1.40, 1.30, 1.22):
        for bs in sizes:
            need = [CARD_PAD_TOP + para_h(t, 14.5, bw, 1.2) + CARD_TITLE_GAP
                    + text_h(r, bs, bw, spacing, 4, True) + CARD_PAD_BOT
                    for t, r in zip(titles, runs)]
            h = max([h_spec] + need)
            if top + rows * h + (rows - 1) * gap <= GRID_BOTTOM:
                return bs, h, spacing
            best = (bs, h, spacing)
    return best


def r_cards(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    cards = sp["cards"]
    cols = sp.get("cols", 2)
    gap = sp.get("gap", 0.6)
    top = sp.get("top", BODY_TOP + 0.35)
    h = sp.get("h", 4.2)
    w = (CW - gap * (cols - 1)) / cols
    bs_spec = max(c.get("body_size", 12) for c in cards)
    bs, h, spacing = _card_grid(cards, lang, BI, w, top, h, gap, cols, bs_spec)
    for i, c in enumerate(cards):
        r, cidx = divmod(i, cols)
        x = M + cidx * (w + gap)
        y = top + r * (h + gap)
        rect(slide, x, y, w, h, fill=col(c.get("bg"), CARD), line=BORDER)
        rect(slide, x, y, 0.09, h, fill=col(c.get("accent"), ACCENT_BR))
        title_v = L(c["title"], lang)
        text(slide, x + 0.62, y + CARD_PAD_TOP if BI else y + 0.52,
             w - 1.24, 0.62, title_v, size=14.5 if BI else 15.5, bold=True,
             color=col(c.get("title_color"), DEEP))
        if c.get("title_en") and not BI:
            text(slide, x + 0.62, y + 1.16, w - 1.24, 0.42, L(c["title_en"], lang),
                 size=11, color=ACCENT_BR, bold=True)
        if BI:
            body_top = y + CARD_PAD_TOP + para_h(title_v, 14.5, w - 1.24, 1.2) \
                + CARD_TITLE_GAP
        else:
            body_top = y + (1.72 if c.get("title_en") else 1.28)
        text(slide, x + 0.62, body_top, w - 1.24,
             h - (body_top - y) - (0.2 if BI else 0.4),
             _card_runs(c, lang, BI), size=bs if BI else c.get("body_size", 12),
             color=TEXT, spacing=spacing, space_after=4, sec_inline=BI)
        if c.get("tag") and not BI:
            rect(slide, x + w - 3.4, y + h - 1.15, 2.8, 0.62, fill=col(c.get("tag_bg"), DEEP))
            text(slide, x + w - 3.4, y + h - 1.02, 2.8, 0.42, L(c["tag"], lang),
                 size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def r_table(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    cols = sp["cols"]
    rows = sp["rows"]
    top = sp.get("top", BODY_TOP + 0.3)
    w = sp.get("w", CW)
    x = sp.get("x", M)
    h = sp.get("h", min(13.0, 1.15 * (len(rows) + 1)))
    widths = sp.get("widths") or [w / len(cols)] * len(cols)
    hs = round(sp.get("head_size", 12.5) * (0.94 if BI else 1.0), 1)
    bs = round(sp.get("body_size", 11.5) * (0.92 if BI else 1.0), 1)
    if sp.get("note"):
        # Rows are a *minimum* height, so the note has to clear the height the
        # table will really take — not the nominal box the spec asked for.
        room = FOOTER_Y - 0.30 - top - 0.35
        nv = L(sp["note"], lang)
        while BI and bs > 9.0 and est_table_h(cols, rows, widths, bs, hs) \
                + para_h(nv, 11.5, w, 1.35) > room:
            bs, hs = round(bs - 0.4, 1), round(hs - 0.3, 1)
        h = est_table_h(cols, rows, widths, bs, hs) if BI else h
    shape = slide.shapes.add_table(len(rows) + 1, len(cols), Cm(x), Cm(top),
                                   Cm(w), Cm(h))
    tbl = shape.table
    for i, cwv in enumerate(widths):
        tbl.columns[i].width = Cm(cwv)
    for j, c in enumerate(cols):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DEEP
        style_cell(cell, c, lang, hs, True, WHITE,
                   sec_color=RGBColor(0xC3, 0xD4, 0xEF))
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 else CARD
            style_cell(cell, val, lang, bs, bool(j == 0 and sp.get("bold_first")), TEXT)
    if sp.get("note"):
        ny = top + h + 0.4
        if BI:
            ny = min(top + h + 0.35,
                     FOOTER_Y - 0.30 - para_h(nv, 11.5, w, 1.35))
        text(slide, x, ny, w, 1.4, nv, size=11.5, color=MUTED, spacing=1.35)


def r_flow(slide, sp, ctx):
    """Horizontal steps connected by arrows; optional note below."""
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    steps = sp["steps"]
    gap = 0.95
    n = len(steps)
    aw = 0.85                                   # arrow width
    w = (CW - gap * (n - 1) - aw * (n - 1)) / n
    y = sp.get("y", 6.4)
    h = sp.get("h", 4.6)
    x = M
    for i, s in enumerate(steps):
        rect(slide, x, y, w, h, fill=col(s.get("bg"), CARD), line=BORDER)
        rect(slide, x, y, w, 0.1, fill=col(s.get("accent"), ACCENT_BR))
        rect(slide, x + w / 2 - 0.62, y + 0.55, 1.24, 1.24, fill=col(s.get("accent"), ACCENT_BR))
        text(slide, x + w / 2 - 0.62, y + 0.78, 1.24, 0.8, f"{i + 1}", size=18,
             bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tv = L(s["title"], lang)
        t_h = para_h(tv, 11.5, w - 1.1, 1.25, True) if BI else 0.62
        text(slide, x + 0.55, y + 2.05, w - 1.1, t_h + 0.2, tv,
             size=11.5 if BI else 14.5, bold=True, color=DEEP,
             align=PP_ALIGN.CENTER, sec_inline=BI)
        if s.get("title_en") and not BI:
            text(slide, x + 0.55, y + 2.68, w - 1.1, 0.4, L(s["title_en"], lang),
                 size=10.5, color=ACCENT_BR, align=PP_ALIGN.CENTER)
        d_y = y + 2.05 + t_h + 0.16 if BI else y + 3.2
        text(slide, x + 0.55, d_y, w - 1.1, y + h - d_y - (0.1 if BI else 0.2),
             L(s["desc"], lang), size=10 if BI else 11.5, color=MUTED,
             align=PP_ALIGN.CENTER, spacing=1.28 if BI else 1.35)
        x += w
        if i < n - 1:
            arrow(slide, x + (gap - aw) / 2, y + h / 2 - 0.32, aw, 0.64,
                  color=col(s.get("accent"), ACCENT_BR))
            x += gap
    if sp.get("note"):
        text(slide, M, y + h + 0.85, CW, 1.6, L(sp["note"], lang), size=12.5,
             color=TEXT, spacing=1.4)


def r_compare(slide, sp, ctx):
    """Two (or three) columns side by side with bullet lists."""
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    cols = sp["columns"]
    gap = 0.85
    w = (CW - gap * (len(cols) - 1)) / len(cols)
    top = sp.get("top", BODY_TOP + 0.35)
    h = sp.get("h", 11.4)
    def runs_of(c):
        return [("• " + L(i, lang)) for i in c.get("items", [])]

    def need_h(s):
        return max([2.0 + text_h(runs_of(c), s, w - 1.2, 1.4, 8, True) + 0.30
                    for c in cols] or [h])

    isz = 11.5
    if BI:
        nl = para_h(L(sp["note"], lang), 12.5, CW, 1.4) + 0.45 if sp.get("note") else 0.0
        isz = fit_size(
            lambda s: top + max(h, need_h(s)) + nl <= FOOTER_Y - 0.32,
            (11.5, 11.0, 10.4, 9.8, 9.2, 8.8))
        h = max(h, need_h(isz))
    x = M
    for c in cols:
        rect(slide, x, top, w, h, fill=col(c.get("bg"), CARD), line=BORDER)
        rect(slide, x, top, w, 1.5, fill=col(c.get("accent"), DEEP))
        text(slide, x + 0.6, top + 0.42, w - 1.2, 0.7, L(c["title"], lang),
             size=16, bold=True, color=WHITE, sec_color=SEC_COLOR_LIGHT)
        text(slide, x + 0.6, top + 2.0, w - 1.2, h - 2.3, runs_of(c),
             size=isz if BI else 12.5, color=TEXT, spacing=1.4 if BI else 1.5,
             space_after=8, sec_inline=BI)
        x += w + gap
    if sp.get("note"):
        ny = top + h + (0.45 if BI else 0.5)
        if BI:
            ny = min(ny, FOOTER_Y - 0.32
                     - para_h(L(sp["note"], lang), 12.5, CW, 1.4))
        text(slide, M, ny, CW, 1.6, L(sp["note"], lang), size=12.5,
             color=TEXT, spacing=1.4)


def r_splitbar(slide, sp, ctx):
    """Proportional horizontal segments (train / val / test ...)."""
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    segs = sp["segments"]
    total_v = sum(s["value"] for s in segs)
    y, h = sp.get("y", 5.6), sp.get("h", 3.1)
    dsz = 10.5 if BI else 12
    d_y = y + h + 0.55
    x = M
    for s in segs:
        w = CW * s["value"] / total_v
        rect(slide, x, y, w - 0.12, h, fill=col(s.get("color"), ACCENT))
        tv = L(s["title"], lang)
        if BI:
            # Inline "Validation ｜ 验证集" is wider than a 15 % band and runs
            # under the next band; stacked it is only as wide as its longer
            # half.  The pct follows the two-line label down.
            bw = w - 0.34
            lh = para_h(tv, 14, bw, 1.15)
            text(slide, x + 0.11, y + 0.44, bw, lh + 0.20, tv, size=14,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER, spacing=1.15,
                 sec_color=SEC_COLOR_LIGHT)
            text(slide, x, y + 0.44 + lh + 0.14, w - 0.12, 0.6, s.get("pct", ""),
                 size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        else:
            text(slide, x, y + 0.55, w - 0.12, 0.8, tv,
                 size=17, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
            text(slide, x, y + 1.42, w - 0.12, 0.6, s.get("pct", ""), size=13,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        if not BI:
            text(slide, x + 0.5, d_y, w - 1.0, 2.6, L(s["desc"], lang),
                 size=12, color=TEXT, spacing=1.4)
        x += w
    if not BI:
        if sp.get("note"):
            text(slide, M, y + h + 3.5, CW, 2.0, L(sp["note"], lang), size=12.5,
                 color=DEEP, spacing=1.4)
        return
    # The descriptions hang under the bar and their height decides where the
    # note goes — a fixed offset leaves the note sitting on the last line.
    descs = [(CW * s["value"] / total_v - 1.0, L(s["desc"], lang)) for s in segs]
    dz = FOOTER_Y - 0.32
    if sp.get("note"):
        dz -= para_h(L(sp["note"], lang), 12.5, CW, 1.4) + 0.45
    for i, (dw, dv) in enumerate(descs):
        dx = M + sum(CW * s["value"] / total_v for s in segs[:i]) + 0.5
        text(slide, dx, d_y, dw, max(1.2, dz - d_y), dv, size=dsz, color=TEXT,
             spacing=1.35)
    if sp.get("note"):
        text(slide, M, dz, CW, 2.0, L(sp["note"], lang), size=12.5,
             color=DEEP, spacing=1.4)


def r_kfold(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    k = sp.get("k", 5)
    rows = sp.get("rows", k)
    x, y = sp.get("x", M), sp.get("y", 4.4)
    w = sp.get("w", 18.5)
    # The note column is positioned at `x + w + 1.1`, but `w` measures the
    # *cell block* alone — the cells start 3.3 cm in, after the row labels, so
    # they occupy 3.3 + w of horizontal room.  Reading `w` as "everything up to
    # the notes" is what put the notes on top of the last fold's cells.  Leave
    # the note column where the spec puts it and stop the cells short of it.
    nx = x + w + 1.1
    w = min(w, nx - 0.35 - 3.3 - x + 0.14)
    h, gap = 1.32, 0.42
    seg_w = w / k
    for i in range(rows):
        if BI:
            label = Bi(f"Fold {i + 1}", f"第 {i + 1} 折")
        else:
            label = f"Fold {i + 1}" if lang == "en" else f"第 {i + 1} 折"
        text(slide, x, y + i * (h + gap) + 0.28, 3.0, 0.6, label,
             size=11 if BI else 12, bold=True, color=DEEP)
        for j in range(k):
            sx = x + 3.3 + j * seg_w
            is_val = j == i
            rect(slide, sx, y + i * (h + gap), seg_w - 0.14, h,
                 fill=ORANGE if is_val else col(sp.get("train_color"), DEEP))
            if BI:
                txt = Bi("val" if is_val else "train", "验证" if is_val else "训练")
            else:
                txt = ("val" if is_val else "train") if lang == "en" \
                    else ("验证" if is_val else "训练")
            text(slide, sx, y + i * (h + gap) + 0.36, seg_w - 0.14, 0.6, txt,
                 size=10.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 sec_color=SEC_COLOR_LIGHT)
    notes = sp.get("notes", [])
    if notes:
        def _note(n):
            # The bullet belongs to the item, not to each language: giving the
            # Chinese half its own bullet lets the wrapper strand it at the end
            # of the previous line ("... StratifiedKFold. ｜ •").
            if BI:
                return Bi("• " + n["en"], n["zh"])
            return "• " + (n["en"] if lang == "en" else n["zh"])

        text(slide, nx, y + 0.2, SW - M - nx, 9.5,
             [_note(n) for n in notes], size=11.5 if BI else 12.5,
             color=TEXT, spacing=1.5, space_after=9, sec_inline=True)
    if sp.get("note"):
        text(slide, M, y + rows * (h + gap) + 0.7, CW, 1.8, L(sp["note"], lang),
             size=12.5, color=MUTED, spacing=1.4)


def r_chart(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    def both(v):
        """Charts only take plain strings — keep both languages on one line."""
        t = L(v, lang)
        sec = getattr(t, "sec", "")
        return f"{t} / {sec}" if sec else str(t)

    data = CategoryChartData()
    data.categories = sp["categories"]
    for s in sp["series"]:
        data.add_series(both(s["name"]), s["values"])
    x, y = sp.get("x", M), sp.get("y", BODY_TOP + 0.3)
    w, h = sp.get("w", 19.0), sp.get("h", 11.6)
    nv = None
    if BI and sp.get("note"):
        nv = L(sp["note"], lang)
        nh = para_h(nv, 12, CW, 1.35)
        h = max(6.0, min(h, FOOTER_Y - 0.30 - y - 0.45 - nh))
    gf = slide.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS if sp.get("markers", True)
                                else XL_CHART_TYPE.LINE,
                                Cm(x), Cm(y), Cm(w), Cm(h), data)
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.BOTTOM
    ch.legend.include_in_layout = False
    ch.font.size = Pt(11)
    ch.font.name = FONT
    for i, (s, ser) in enumerate(zip(sp["series"], ch.plots[0].series)):
        c = col(s.get("color"), [ACCENT, ORANGE, GREEN, RED][i % 4])
        ser.format.line.color.rgb = c
        ser.format.line.width = Pt(2.5 if s.get("emphasis") else 1.75)
        ser.smooth = s.get("smooth", True)
        if s.get("no_markers"):
            ser.marker.format.fill.background()
    if sp.get("x_label"):
        ch.category_axis.axis_title.text_frame.text = both(sp["x_label"])
        ch.category_axis.has_major_gridlines = False
    if sp.get("y_label"):
        ch.value_axis.axis_title.text_frame.text = both(sp["y_label"])
    if sp.get("y_max") is not None:
        ch.value_axis.maximum_scale = sp["y_max"]
    notes = sp.get("notes", [])
    if notes:
        text(slide, x + w + 0.9, y + 0.3, SW - M - (x + w + 0.9), 9.0,
             [("• " + L(n, lang)) for n in notes], size=11.5 if BI else 12.5,
             color=TEXT, spacing=1.45, space_after=8, sec_inline=True)
    if sp.get("note"):
        ny = y + h + 0.45
        if BI:
            ny = min(ny, FOOTER_Y - 0.30 - para_h(L(sp["note"], lang), 12,
                                                  CW, 1.35))
        text(slide, M, ny, CW, 1.6, L(sp["note"], lang), size=12,
             color=MUTED, spacing=1.35)


def r_code(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    blocks = sp["blocks"]
    gap = 0.62
    n = len(blocks)
    w = (CW - gap * (n - 1)) / n
    top = sp.get("top", BODY_TOP + 0.35)
    h = sp.get("h", 11.3)
    sizes = []
    for b in blocks:
        c = b["code"]
        if isinstance(c, dict):
            c = c.get(lang) or c.get("en")
        sizes.append(len(c.split("\n")) if isinstance(c, str) else len(c))
    if BI:
        # The source listings did not fit their nominal box even in the
        # monolingual decks; with room to spare, let the panel be as tall as
        # the longest listing actually needs.
        nv = L(sp["note"], lang) if sp.get("note") else None
        nh = (para_h(nv, 12, CW, 1.35) + 0.45) if nv else 0.0
        room = FOOTER_Y - 0.30 - top - nh
        for csz in (blocks[0].get("size", 11), 10.5, 10, 9.5, 9, 8.5, 8, 7.5, 7.0):
            # one line of slack: the rendered listing carries a trailing empty
            # paragraph that the naive line count does not include
            need = max(1.15 + (n + 1) * csz * 1.28 * LEAD / PT_CM + 0.4
                       for n in sizes)
            if need <= room:
                break
        h = max(h, min(need, room))
    x = M
    for b, nlines in zip(blocks, sizes):
        rect(slide, x, top, w, h, fill=CODE_BG)
        rect(slide, x, top, w, 0.85, fill=RGBColor(0x1B, 0x26, 0x3D))
        text(slide, x + 0.45, top + 0.24, w - 3, 0.45, L(b["title"], lang),
             size=11.5, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
        code = b["code"]
        if isinstance(code, dict):                 # per-language code block
            code = code.get(lang) or code.get("en")
        lines = code
        if isinstance(lines, str):
            lines = lines.split("\n")
        text(slide, x + 0.55, top + 1.15, w - 1.1, h - 1.35,
             [(ln, {"font": CODE_FONT, "size": csz if BI else b.get("size", 11)})
              for ln in lines],
             size=csz if BI else b.get("size", 11), color=CODE_TEXT,
             spacing=1.28)
        x += w + gap
    if sp.get("note"):
        ny = top + h + 0.5
        if BI:
            ny = min(ny, FOOTER_Y - 0.30 - para_h(L(sp["note"], lang), 12,
                                                  CW, 1.35))
        text(slide, M, ny, CW, 1.7, L(sp["note"], lang), size=12,
             color=TEXT, spacing=1.35)


def r_checklist(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    items = sp["items"]
    top = sp.get("top", BODY_TOP + 0.3)
    h, gap = sp.get("h", 2.05), 0.42
    tw = CW - 4.0
    PAD_T, PAD_M, PAD_B = (0.30, 0.14, 0.26) if BI else (0.34, 0.16, 0.34)
    tsz, dsz = 12.5, 10.5
    BW = 2.5                                   # badge chip width

    def need(it, ts, ds):
        return (PAD_T + para_h(L(it["title"], lang), ts, tw, 1.2, True) + PAD_M
                + para_h(L(it["desc"], lang), ds, tw, 1.3) + PAD_B)

    # The bilingual badge is two paragraphs in a 2.5 cm chip, so the chip has to
    # be sized from its own text — the old fixed 0.9 cm ate the second language.
    badge_need = 0.0
    if BI:
        for it in items:
            if it.get("badge"):
                badge_need = max(badge_need,
                                 para_h(L(it["badge"], lang), 11, BW - 0.16, 1.05)
                                 + 0.44)

    if BI:
        gap = 0.30
        sp_h = sp.get("h", 2.05)
        avail = (FOOTER_Y - 0.32 - top - (len(items) - 1) * gap) / len(items)
        for tsz, dsz in ((12.5, 10.5), (12.0, 10.0), (11.4, 9.6), (10.8, 9.2),
                         (10.2, 8.8), (9.6, 8.4), (9.0, 7.8), (8.4, 7.2),
                         (7.8, 6.8)):
            h = max(max(need(i, tsz, dsz) for i in items), badge_need,
                    sp_h if sp_h <= avail else 0.0)
            if h <= avail:
                break
        h = min(h, max(avail, badge_need))
    for i, it in enumerate(items):
        y = top + i * (h + gap)
        rect(slide, M, y, CW, h, fill=WHITE, line=BORDER)
        rect(slide, M, y, 0.09, h, fill=col(it.get("accent"), ACCENT_BR))
        if it.get("badge"):
            bv = L(it["badge"], lang)
            if BI:
                bh = min(h - 0.20, para_h(bv, 11, BW - 0.16, 1.05) + 0.18)
                by = y + max(0.10, (h - bh) / 2)
                rect(slide, M + 0.5, by, BW, bh, fill=col(it.get("accent"), ACCENT_BR))
                text(slide, M + 0.5, by, BW, bh, bv, size=11, bold=True,
                     color=WHITE, align=PP_ALIGN.CENTER,
                     anchor=MSO_ANCHOR.MIDDLE, spacing=1.05,
                     sec_color=SEC_COLOR_LIGHT)
            else:
                rect(slide, M + 0.5, y + 0.52, BW, 0.9, fill=col(it.get("accent"), ACCENT_BR))
                text(slide, M + 0.5, y + 0.72, BW, 0.5, bv, size=11.5, bold=True,
                     color=WHITE, align=PP_ALIGN.CENTER)
        title_v = L(it["title"], lang)
        if BI:
            t_h = para_h(title_v, tsz, tw, 1.2, True)
            t_y, d_y = y + PAD_T, y + PAD_T + t_h + PAD_M
        else:
            t_y, d_y = y + 0.32, y + 0.95
        text(slide, M + 3.4, t_y, tw, t_h + 0.3 if BI else 0.55, title_v,
             size=tsz if BI else 14, bold=True, color=DEEP, sec_inline=BI)
        text(slide, M + 3.4, d_y, tw, h - (d_y - y) - 0.15, L(it["desc"], lang),
             size=dsz if BI else 11.5, color=MUTED, spacing=1.3)


def r_quiz(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    qs = sp["questions"]
    cols = sp.get("cols", 2)
    gap = 0.55
    w = (CW - gap * (cols - 1)) / cols
    top = sp.get("top", BODY_TOP + 0.25)
    rows = (len(qs) + cols - 1) // cols
    h = sp.get("h", (14.4 - (rows - 1) * gap) / rows)
    q_sz = 12.5
    o_sz = 11.5
    if BI:
        # Option lines are bilingual and run to two lines each; solve the option
        # size and the card height together instead of shrinking into a corner
        # and overflowing when the ladder bottoms out.
        q_sz = 11.5
        avail = (FOOTER_Y - 0.32 - top - (rows - 1) * gap) / rows

        def need_at(os):
            m = 0.0
            for q in qs:
                qh = para_h(L(q["q"], lang), q_sz, w - 3.9, 1.28)
                oy = max(2.15, 0.45 + qh + 0.22)
                oh = text_h([L(o, lang) for o in q.get("options", [])],
                            os, w - 1.1, 1.34, 3, True)
                m = max(m, oy + oh + 0.30)
            return m

        for o_sz in (10.5, 10.0, 9.5, 9.0, 8.5, 8.0, 7.6):
            if need_at(o_sz) <= avail:
                break
        h = max(h, min(need_at(o_sz), avail))
    for i, q in enumerate(qs):
        r, c = divmod(i, cols)
        x = M + c * (w + gap)
        y = top + r * (h + gap)
        rect(slide, x, y, w, h, fill=CARD, line=BORDER)
        tag_v = L(q["tag"], lang)
        if BI:
            # a two-language tag needs a chip sized from its own text
            tch = para_h(tag_v, 10.5, 2.36, 1.1) + 0.16
            rect(slide, x + 0.55, y + 0.45, 2.5, tch, fill=DEEP)
            text(slide, x + 0.55, y + 0.45, 2.5, tch, tag_v, size=10.5,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE, spacing=1.1,
                 sec_color=SEC_COLOR_LIGHT)
        else:
            rect(slide, x + 0.55, y + 0.45, 2.5, 0.62, fill=DEEP)
            text(slide, x + 0.55, y + 0.58, 2.5, 0.42, tag_v, size=10.5,
                 bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        qv = L(q["q"], lang)
        q_h = para_h(qv, q_sz, w - 3.9, 1.28)
        text(slide, x + 3.35, y + 0.45, w - 3.9, q_h + 0.3, qv,
             size=q_sz, bold=True, color=DEEP, spacing=1.28)
        opts = [L(o, lang) for o in q.get("options", [])]
        o_y = max(y + 2.15, y + 0.45 + q_h + 0.22) if BI else y + 2.15
        text(slide, x + 0.55, o_y, w - 1.1, h - (o_y - y) - 0.2, opts,
             size=o_sz, color=TEXT, spacing=1.34, space_after=3, sec_inline=BI)


def r_summary(slide, sp, ctx):
    lang, week, total = ctx["lang"], ctx["week"], ctx["total"]
    header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
    footer(slide, week, sp["page"], total)
    pts = sp["points"]
    w = sp.get("w", 18.6)
    top = sp.get("top", BODY_TOP + 0.3)
    todos = sp.get("todos", [])
    bottom = FOOTER_Y - 0.32
    # Bilingual points run ~40% taller, so the cards grow and the gaps shrink.
    h, gap = (2.62, 0.12) if BI else (1.85, 0.42)
    psz = 12
    if BI and pts:
        gap = 0.10
        for psz in (12, 11.5, 11, 10.5, 10, 9.5, 9):
            h = max(1.85, max(0.34 + para_h(L(p, lang), psz, w - 2.4, 1.3)
                             for p in pts))
            if len(pts) * h + (len(pts) - 1) * gap <= bottom - top:
                break
    for i, p in enumerate(pts):
        y = top + i * (h + gap)
        rect(slide, M, y, w, h, fill=CARD)
        rect(slide, M, y, 1.32, h, fill=DEEP)
        text(slide, M, y + ((h - 0.7) / 2 if BI else 0.55), 1.32, 0.7,
             f"{i + 1}", size=19, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        text(slide, M + 1.75, y + (0.16 if BI else 0.35), w - 2.4,
             h - (0.32 if BI else 0.7), L(p, lang),
             size=psz if BI else 13, color=TEXT, anchor=MSO_ANCHOR.MIDDLE,
             spacing=1.3 if BI else 1.35)
    if todos:
        x = M + w + 0.85
        tw = SW - M - x
        tt = L(sp.get("todo_title", {"zh": "课后待办", "en": "After Class"}), lang)
        # English + Chinese share one line ("After Class ｜ 课后待办"): stacked,
        # the second line would spill out of the 1.35 cm dark bar.
        tbar = max(1.35, 0.30 + para_h(tt, 14, tw - 1.2, 1.25, True) + 0.28) \
            if BI else 1.35
        rect(slide, x, top, tw, tbar, fill=DEEP)
        text(slide, x + 0.6, top + (0.32 if BI else 0.36), tw - 1.2, 0.6,
             tt, size=14, bold=True, color=WHITE, sec_inline=BI,
             sec_color=SEC_COLOR_LIGHT)
        th, step, tk = 2.60, 2.95, 0.42
        tdsz = 10
        t0 = top + 1.85
        if BI:
            step, tk = 0.30, 0.36
            t0 = max(top + 1.85, top + tbar + 0.42)

            def need(t, ts, ds):
                return (tk + para_h(L(t["title"], lang), ts, tw - 1.2, 1.22,
                                    True) + 0.10
                        + para_h(L(t["desc"], lang), ds, tw - 1.2, 1.3) + 0.30)

            room = (bottom - t0 - (len(todos) - 1) * step) / len(todos)
            fit = None
            for d in (10, 9.5, 9, 8.5, 8):
                need_h = max(need(t, 10.5, d) for t in todos)
                if need_h <= room:
                    fit = (need_h, d)
                    break
            th, tdsz = fit if fit else (room, 8)
            th = max(1.8, th)
            step = th + 0.30
        for i, t in enumerate(todos):
            y = t0 + i * step
            rect(slide, x, y, tw, th, fill=WHITE, line=BORDER)
            text(slide, x + 0.6, y + tk, tw - 1.2, 0.6, L(t["title"], lang),
                 size=10.5 if BI else 13.5, bold=True, color=DEEP, sec_inline=BI)
            d_off = (tk + para_h(L(t["title"], lang), 10.5, tw - 1.2, 1.22, True)
                     + 0.10) if BI else 1.12
            text(slide, x + 0.6, y + d_off, tw - 1.2,
                 th - d_off - (0.15 if BI else 0.18),
                 L(t["desc"], lang), size=tdsz if BI else 11.5, color=MUTED,
                 spacing=1.3 if BI else 1.35)


def r_closing(slide, sp, ctx):
    lang, week = ctx["lang"], ctx["week"]
    rect(slide, 0, 0, SW, 0.26, fill=ACCENT)
    text(slide, SW - M - 18.5, 1.06, 18.52, 15.69, f"{week:02d}", size=170,
         bold=True, color=CARD, align=PP_ALIGN.RIGHT)
    rect(slide, M + 0.16, 2.6, 1.16, 1.16, fill=DEEP)
    text(slide, M + 0.32, 2.86, 0.85, 0.64, f"W{week}", size=11, bold=True, color=WHITE)
    rect(slide, M, 4.4, 1.69, 0.11, fill=ACCENT)
    QW = 24.0
    qv = L(sp["quote"], lang)
    thanks_v = L(sp.get("thanks", {"zh": "谢谢大家", "en": "Thank you"}), lang)
    sv = L(sp["quote_sub"], lang) if sp.get("quote_sub") else None
    nl = L(sp.get("next_label", {"zh": "下周预告", "en": "Next week"}), lang)
    if BI:
        # The quote is the tallest run and everything stacks under it, so size
        # the quote against the space actually left by the preview box.  The box
        # itself is measured from the blurb it has to hold — a fixed 2.0 cm box
        # clips the bilingual "next week" paragraph.
        next_v = L(sp["next"], lang)
        nl_h = para_h(nl, 11, CW - 1.4, 1.2, True)

        def _box(nsz):
            return 0.30 + nl_h + 0.14 + para_h(next_v, nsz, CW - 1.4, 1.25) + 0.28

        nsz = fit_size(lambda s: _box(s) <= 2.70,
                       (12.5, 11.8, 11.0, 10.4, 9.8, 9.2, 8.6))
        box_h = _box(nsz)

        def _col(s):
            return (para_h(qv, s, QW, 1.3)
                    + (para_h(sv, 12, QW, 1.3) + 0.35 if sv else 0.0)
                    + para_h(thanks_v, 19, 22, 1.2) + 0.30)

        q_sz = fit_size(lambda s: 5.3 + _col(s) + box_h + 0.30
                        <= FOOTER_Y - 0.35,
                        (23, 21.5, 20, 18.5, 17, 15.5, 14, 12.5, 11))
        q_h = para_h(qv, q_sz, QW, 1.3)
        text(slide, M, 5.3, QW, q_h + 0.4, qv, size=q_sz, bold=True,
             color=DEEP, spacing=1.3)
        y = 5.3 + q_h + 0.30
        if sv:
            text(slide, M, y, QW, 1.2, sv, size=12, color=MUTED)
            y += para_h(sv, 12, QW, 1.3) + 0.35
        text(slide, M, y, 22, 1.0, thanks_v, size=19, bold=True, color=TEXT)
        box_y = max(13.3, y + para_h(thanks_v, 19, 22, 1.2) + 0.30)
        rect(slide, M, box_y, CW, box_h, fill=CARD, line=BORDER)
        text(slide, M + 0.7, box_y + 0.30, CW - 1.4, nl_h + 0.25, nl,
             size=11, bold=True, color=ACCENT, sec_inline=True)
        text(slide, M + 0.7, box_y + 0.30 + nl_h + 0.14, CW - 1.4,
             max(0.6, box_h - 0.44 - nl_h), next_v,
             size=nsz, color=DEEP, spacing=1.25)
        text(slide, M, FOOTER_Y, 20, 0.45, L(sp.get(
            "sign", f"AI Application Development · Week {week} Lecture · "
                    f"{{n}} / {{n}}"), lang).replace("{n}", str(ctx["total"])),
            size=10, color=MUTED)
        return
    text(slide, M, 5.3, 24, 5.5, qv, size=27, bold=True, color=DEEP, spacing=1.3)
    if sp.get("quote_sub"):
        text(slide, M, 9.4, 24, 1.2, sv, size=13.5, color=MUTED)
    text(slide, M, 11.6, 22, 0.9, thanks_v, size=22, bold=True, color=TEXT)
    rect(slide, M, 13.3, CW, 2.0, fill=CARD, line=BORDER)
    text(slide, M + 0.7, 13.62, CW - 1.4, 0.5, nl, size=11, bold=True,
         color=ACCENT)
    text(slide, M + 0.7, 14.15, CW - 1.4, 0.9, L(sp["next"], lang), size=14,
         color=DEEP, spacing=1.25)
    text(slide, M, FOOTER_Y, 20, 0.45, L(sp.get(
        "sign", f"AI Application Development · Week {week} Lecture · {{n}} / {{n}}"), lang)
        .replace("{n}", str(ctx["total"])), size=10, color=MUTED)


RENDERERS = {
    "cover": r_cover, "contents": r_contents, "section": r_section,
    "cards": r_cards, "table": r_table, "flow": r_flow, "compare": r_compare,
    "splitbar": r_splitbar, "kfold": r_kfold, "chart": r_chart, "code": r_code,
    "checklist": r_checklist, "quiz": r_quiz, "summary": r_summary,
    "closing": r_closing,
}


def build(spec, out_path, lang):
    global BI
    BI = (lang == "bi")
    prs = Presentation()
    prs.slide_width = Cm(SW)
    prs.slide_height = Cm(SH)
    slides = spec["slides"]
    ctx = {"lang": lang, "week": spec["week"], "total": len(slides)}
    for i, sp in enumerate(slides, start=1):
        sp = dict(sp)
        sp["page"] = i
        slide = new_slide(prs)
        RENDERERS[sp["type"]](slide, sp, ctx)
    prs.save(out_path)
    return len(slides)


if __name__ == "__main__":
    import importlib
    week = sys.argv[1] if len(sys.argv) > 1 else "week-03"
    mod = importlib.import_module(f"deck_specs.{week.replace('-', '_')}")
    spec = mod.SPEC
    for lang in (sys.argv[2:] or ["en", "zh"]):
        n = build(spec, f"/tmp/{week}-{lang}.pptx", lang)
    print("slides:", n)
