"""Vector figures for the AI Application Development decks.

Why vector
----------
Everything here is drawn from the same primitives the rest of the deck uses:
connectors for straight runs, freeform polygons for curves and shaded areas,
plain rectangles for cells.  No picture part is ever added, so

  * `validate_deck.py`'s "0 media files" rule still holds — nothing can ever
    show PowerPoint's "the picture can't be displayed" placeholder,
  * the figures stay sharp at any projector resolution and cost a few kB,
  * every label is ordinary slide text, so the figures are bilingual for free
    and the numbers inside them can be asserted at build time.

The last point matters most: the convolution, pooling and confusion-matrix
figures **compute their own result** from the numbers in the spec and assert it,
so a figure cannot silently drift away from the arithmetic it teaches.

Wiring
------
This module never imports `build_deck`.  It is handed the builder instead::

    deck_figures.register(sys.modules[__name__])      # end of build_deck.py

Importing it back would re-execute the builder under a second module name and
split the global ``BI`` flag in two — half the deck would render monolingual.

Spec shape
----------
    {"type": "figure", "kind": "conv",
     "title": {...}, "subtitle": {...}, "right": MOD, "note": {...},
     ...kind-specific fields...}

Each kind is ``_fig_<kind>(bd, slide, sp, lang, x, y, w, h)``.
"""

import math

from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1F, 0x29, 0x37)


# ------------------------------------------------------------- primitives ---
def line(bd, slide, x1, y1, x2, y2, color=None, w=1.25, dash=False):
    """One straight stroke (a connector, so it can be dashed and rotated)."""
    cn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                    Cm(x1), Cm(y1), Cm(x2), Cm(y2))
    cn.shadow.inherit = False
    cn.line.color.rgb = bd.BORDER if color is None else color
    cn.line.width = Pt(w)
    if dash:
        cn.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return cn


def poly(bd, slide, pts, color=None, w=1.75, dash=False, close=False, fill=None):
    """One freeform through ``pts`` (cm).  ``fill`` closes and shades it."""
    if len(pts) < 2:
        return None
    pts = [(float(a), float(b)) for a, b in pts]
    out = [pts[0]]
    for p in pts[1:]:                      # drop repeats: zero-length segments
        if abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if len(out) < 2:
        return None
    fb = slide.shapes.build_freeform(Cm(out[0][0]), Cm(out[0][1]), scale=1.0)
    fb.add_line_segments([(Cm(a), Cm(b)) for a, b in out[1:]],
                         close=bool(close or fill is not None))
    sp = fb.convert_to_shape()
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if color is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = color
        sp.line.width = Pt(w)
        if dash:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return sp


def dot(bd, slide, x, y, d=0.36, fill=None, line=None, line_w=1.0):
    return bd.rect(slide, x - d / 2, y - d / 2, d, d,
                   fill=bd.ACCENT if fill is None else fill, line=line,
                   line_w=line_w, shape=MSO_SHAPE.OVAL)


def ring(bd, slide, x, y, d, color, w=1.75):
    return bd.rect(slide, x - d / 2, y - d / 2, d, d, fill=None,
                   line=color, line_w=w, shape=MSO_SHAPE.OVAL)


def tip(bd, slide, x, y, direction="right", size=0.44, color=None):
    """A small solid triangle, used as an arrow head."""
    sp = bd.rect(slide, x - size / 2, y - size / 2, size, size,
                 fill=bd.BORDER if color is None else color,
                 shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    sp.rotation = {"up": 0, "right": 90, "down": 180, "left": 270}[direction]
    return sp


def arrow_r(bd, slide, x1, x2, y, color=None, w=1.75):
    """Horizontal arrow from x1 to x2 at height y."""
    c = bd.ACCENT_BR if color is None else color
    line(bd, slide, x1, y, x2 - 0.20, y, color=c, w=w)
    tip(bd, slide, x2 - 0.10, y, "right", 0.42, c)


def dash_rect(bd, slide, x, y, w, h, color, wpt=1.5):
    """Outlined rectangle whose sides are dashed — the sliding-window ghost."""
    for x1, y1, x2, y2 in ((x, y, x + w, y), (x + w, y, x + w, y + h),
                           (x + w, y + h, x, y + h), (x, y + h, x, y)):
        line(bd, slide, x1, y1, x2, y2, color=color, w=wpt, dash=True)


def cell(bd, slide, x, y, w, h, fill, text_v=None, color=None, size=10.0,
         bold=False, outline=None, lw=0.75):
    bd.rect(slide, x, y, w, h, fill=fill,
            line=bd.BORDER if outline is None else outline, line_w=lw)
    if text_v is not None and str(text_v) != "":
        bd.text(slide, x, y, w, h, str(text_v), size=size, bold=bold,
                color=bd.TEXT if color is None else color,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def lerp(c1, c2, t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return RGBColor(*[int(round(a + (b - a) * t))
                      for a, b in zip(tuple(c1), tuple(c2))])


def grey(v, lo=0.0, hi=1.0):
    """0 -> white, 1 -> the body ink: a greyscale image in one call."""
    return lerp(WHITE, INK, (v - lo) / (hi - lo) if hi > lo else 0.0)


def label(bd, slide, lang, item, x, y, w, h, size=12, bold=False, color=None,
          align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.25, inline=False):
    """A bilingual caption.  Numbers and ticks should be passed as plain str."""
    v = bd.L(item, lang) if isinstance(item, dict) else item
    bd.text(slide, x, y, w, h, v, size=size, bold=bold,
            color=bd.TEXT if color is None else color, align=align,
            anchor=anchor, spacing=spacing, sec_inline=inline)


def panel(bd, slide, x, y, w, h, fill=None):
    """The card a figure panel sits on."""
    bd.rect(slide, x, y, w, h, fill=bd.GHOST if fill is None else fill,
            line=bd.BORDER, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.035)


def measure(bd, item, lang, size, w, inline=False, spacing=1.25):
    v = bd.L(item, lang) if isinstance(item, dict) else item
    return bd.para_h(v, size, w, spacing, inline)


def axes(bd, slide, x, y, w, h, color=None):
    """L-shaped axes with arrow heads."""
    c = bd.BORDER if color is None else color
    line(bd, slide, x, y + h, x + w - 0.18, y + h, color=c, w=1.4)
    line(bd, slide, x, y + h, x, y + 0.20, color=c, w=1.4)
    tip(bd, slide, x + w - 0.09, y + h, "right", 0.40, c)
    tip(bd, slide, x, y + 0.09, "up", 0.40, c)


def plot(bd, slide, x, y, w, h, xs, ys, xr, yr, color=None, width=2.4,
         dash=False):
    """Map (xs, ys) into the axes box and stroke them; stops at the first
    point that leaves the box, which is how a diverging run reads as
    'off the chart' rather than a line to nowhere."""
    x0, x1 = xr
    y0, y1 = yr
    pts = []
    for vx, vy in zip(xs, ys):
        px = x + (vx - x0) / (x1 - x0) * w
        py = y + h - (vy - y0) / (y1 - y0) * h
        if not (x - 1e-9 <= px <= x + w + 1e-9 and y - 1e-9 <= py <= y + h + 1e-9):
            break
        pts.append((px, py))
    poly(bd, slide, pts, color=color or bd.ACCENT, w=width, dash=dash)
    return pts


# ================================================================ 1-D bowl ==
def loss_bowl(w):
    """L(w) = (w - 3)^2 — a quadratic with its minimum at w* = 3."""
    return (w - 3.0) ** 2


def descent_trace(w0, lr, n):
    """Plain gradient descent:  w <- w - lr * 2(w - 3)."""
    ws = [float(w0)]
    for _ in range(n):
        ws.append(ws[-1] - lr * 2 * (ws[-1] - 3.0))
    return ws


def _fig_descent1d(bd, slide, sp, lang, x, y, w, h):
    panels = sp["panels"]
    n = len(panels)
    gap = 0.85
    pw = (w - gap * (n - 1)) / n
    w_lo, w_hi = sp.get("w_range", (0.0, 6.0))
    l_hi = sp.get("loss_max", 9.0)

    for i, p in enumerate(panels):
        px = x + i * (pw + gap)
        panel(bd, slide, px, y, pw, h)
        bx = px + 0.75
        bw = pw - 1.5

        tsz = 15.0 if not bd.BI else 13.0
        th = measure(bd, p["title"], lang, tsz, bw, inline=bd.BI)
        label(bd, slide, lang, p["title"], bx, y + 0.56, bw, th + 0.3,
              size=tsz, bold=True, color=bd.DEEP, inline=bd.BI)
        sy = y + 0.56 + th + (0.22 if bd.BI else 0.12)
        sh = measure(bd, p["sub"], lang, 11.5, bw, inline=bd.BI)
        label(bd, slide, lang, p["sub"], bx, sy, bw, sh + 0.3, size=11.5,
              color=bd.MUTED, inline=bd.BI)

        ay = sy + sh + 0.95
        ah = y + h - 2.35 - ay
        ax = bx + 0.32
        aw = bw - 0.60

        axes(bd, slide, ax, ay, aw, ah)
        xs = [w_lo + (w_hi - w_lo) * k / 120.0 for k in range(121)]
        plot(bd, slide, ax, ay, aw, ah, xs, [loss_bowl(v) for v in xs],
             (w_lo, w_hi), (0.0, l_hi), color=bd.BORDER, width=2.2)

        mx = ax + (3.0 - w_lo) / (w_hi - w_lo) * aw
        line(bd, slide, mx, ay + ah, mx, ay + 0.22, color=bd.BORDER, w=1.1,
             dash=True)

        col = bd.col(p.get("color"), bd.ACCENT)
        ws = descent_trace(p["w0"], p["lr"], p["steps"])[: p.get("n_plot", 99)]
        prev = None
        for wv in ws:
            lv = loss_bowl(wv)
            if not (w_lo <= wv <= w_hi and 0.0 <= lv <= l_hi):
                break
            cx = ax + (wv - w_lo) / (w_hi - w_lo) * aw
            cy = ay + ah - lv / l_hi * ah
            if prev is not None:
                # the staircase: step across at the old height, then drop
                line(bd, slide, prev[0], prev[1], cx, prev[1], color=col, w=1.5)
                line(bd, slide, cx, prev[1], cx, cy, color=col, w=1.5)
            dot(bd, slide, cx, cy, 0.34, fill=col)
            prev = (cx, cy)
        if ws and w_lo <= ws[0] <= w_hi and 0.0 <= loss_bowl(ws[0]) <= l_hi:
            sx = ax + (ws[0] - w_lo) / (w_hi - w_lo) * aw
            sy2 = ay + ah - loss_bowl(ws[0]) / l_hi * ah
            ring(bd, slide, sx, sy2, 0.52, bd.DEEP, 1.6)
            dot(bd, slide, sx, sy2, 0.36, fill=bd.DEEP)

        label(bd, slide, lang, sp["y_axis"], ax - 0.14, ay - 0.46, 4.2, 0.5,
              size=10.5, color=bd.MUTED)
        label(bd, slide, lang, sp["x_axis"], ax - 0.14, ay + ah + 0.16, 3.0,
              0.5, size=10.5, color=bd.MUTED)
        label(bd, slide, lang, sp["wstar"], mx - 2.2, ay + ah + 0.16, 2.1,
              0.5, size=10.5, color=bd.MUTED, align=PP_ALIGN.RIGHT)

        vz = measure(bd, p["verdict"], lang, 11.5, bw, inline=bd.BI)
        label(bd, slide, lang, p["verdict"], bx, y + h - 1.20, bw, vz + 0.3,
              size=11.5, color=col, bold=True, align=PP_ALIGN.CENTER,
              inline=bd.BI)


# ============================================================== 2-D ravine ==
def ravine(mode, lr, n, x0, y0, aniso=9.0, beta=0.9):
    """f(x, y) = x^2 + aniso*y^2, so grad = (2x, 2*aniso*y).  'sgd' or 'adam'.

    ``aniso`` is the ratio of curvatures: 9 makes a 1:3 ellipse, 36 a 1:6 one.
    A steeper ravine is the honest way to show what an adaptive step buys — on a
    near-isotropic quadratic plain gradient descent with a well-chosen rate is
    hard to beat, which is not the story the deck is telling.
    """
    x, y = float(x0), float(y0)
    mx = my = v2x = v2y = 0.0
    t = 0
    pts = [(x, y)]
    for _ in range(n):
        gx, gy = 2 * x, 2 * aniso * y
        if mode == "sgd":
            x -= lr * gx
            y -= lr * gy
        else:
            t += 1
            b1, b2, eps = 0.9, 0.999, 1e-8
            mx = b1 * mx + (1 - b1) * gx
            my = b1 * my + (1 - b1) * gy
            v2x = b2 * v2x + (1 - b2) * gx * gx
            v2y = b2 * v2y + (1 - b2) * gy * gy
            x -= lr * (mx / (1 - b1 ** t)) / (math.sqrt(v2x / (1 - b2 ** t)) + eps)
            y -= lr * (my / (1 - b1 ** t)) / (math.sqrt(v2y / (1 - b2 ** t)) + eps)
        pts.append((x, y))
    return pts


def _fig_contour(bd, slide, sp, lang, x, y, w, h):
    lw = sp.get("plot_w", w * 0.70)
    px, py = x, y + 0.90
    ph = h - 2.70
    panel(bd, slide, px, py, lw, ph, fill=WHITE)

    xr = sp.get("x_range", (-2.3, 2.3))
    yr = sp.get("y_range", (-0.60, 0.60))
    A = sp.get("aniso", 9.0)          # f = x^2 + A y^2, so level c is 1:sqrt(A)
    ix, iy = px + 1.05, py + 0.62
    iw, ih = lw - 1.85, ph - 1.55

    def mx(v):
        return ix + (v - xr[0]) / (xr[1] - xr[0]) * iw

    def my(v):
        return iy + ih - (v - yr[0]) / (yr[1] - yr[0]) * ih

    for c in sp.get("levels", (0.25, 1.0, 2.25)):
        rx, ry = math.sqrt(c), math.sqrt(c / A)
        bd.rect(slide, mx(-rx), my(ry), mx(rx) - mx(-rx), my(-ry) - my(ry),
                fill=None, line=bd.BORDER, line_w=1.1, shape=MSO_SHAPE.OVAL)
    line(bd, slide, mx(xr[0]), my(0), mx(xr[1]), my(0), color=bd.BORDER, w=0.9)
    line(bd, slide, mx(0), my(yr[0]), mx(0), my(yr[1]), color=bd.BORDER, w=0.9)
    dot(bd, slide, mx(0), my(0), 0.30, fill=bd.DEEP)

    label(bd, slide, lang, sp["y_axis"], ix - 1.42, my(0) - 0.28, 1.35, 0.55,
          size=11, color=bd.MUTED, align=PP_ALIGN.RIGHT)
    label(bd, slide, lang, sp["x_axis"], mx(xr[1]) - 2.0, my(yr[0]) + 0.14,
          2.1, 0.5, size=11, color=bd.MUTED, align=PP_ALIGN.RIGHT)

    for path in reversed(sp["paths"]):
        c = bd.col(path.get("color"), bd.ACCENT)
        raw = ravine(path["mode"], path["lr"], path["steps"],
                     sp["start"][0], sp["start"][1], A)
        # Stop the polyline at the first point outside the frame: an envelope of
        # zeros is how a diverging run should read, not a line to nowhere.
        inside = [(a, b) for a, b in raw
                  if xr[0] <= a <= xr[1] and yr[0] <= b <= yr[1]]
        if len(inside) < len(raw) and len(inside) >= 2:
            inside = raw[:len(inside) + 1]
            inside = [p for p in inside
                      if xr[0] <= p[0] <= xr[1] and yr[0] <= p[1] <= yr[1]]
        cm_pts = [(mx(a), my(b)) for a, b in inside]
        if len(cm_pts) < 2:
            continue
        # A white underlay: the two walks share the right-hand third of the frame
        # and cross each other, and without a halo they read as one scribble.
        poly(bd, slide, cm_pts, color=WHITE, w=path.get("width", 2.2) + 1.8)
        poly(bd, slide, cm_pts, color=c, w=path.get("width", 2.2),
             dash=path.get("dash", False))
        for k, (cxx, cyy) in enumerate(cm_pts):
            if 0 < k < len(cm_pts) - 1:
                dot(bd, slide, cxx, cyy, 0.20, fill=c)
        ex, ey = cm_pts[-1]
        ax_, ay_ = cm_pts[-2]
        if abs(ex - ax_) >= abs(ey - ay_):
            tip(bd, slide, ex, ey, "right" if ex > ax_ else "left", 0.40, c)
        else:
            tip(bd, slide, ex, ey, "down" if ey > ay_ else "up", 0.40, c)

    sx, sy = mx(sp["start"][0]), my(sp["start"][1])
    ring(bd, slide, sx, sy, 0.50, bd.DEEP, 1.75)
    dot(bd, slide, sx, sy, 0.30, fill=bd.DEEP)
    label(bd, slide, lang, sp["start_label"], sx - 1.4, sy - 0.92, 2.8, 0.5,
          size=10.5, color=bd.DEEP)

    lx = px + lw + 0.80
    ly = py
    lwc = x + w - lx
    for path in sp["paths"]:
        c = bd.col(path.get("color"), bd.ACCENT)
        th = measure(bd, path["name"], lang, 13.5, lwc - 0.9, inline=bd.BI)
        dh = measure(bd, path["fact"], lang, 11.0, lwc - 0.9, inline=bd.BI)
        ch = 0.36 + th + 0.16 + dh + 0.36
        panel(bd, slide, lx, ly, lwc, ch)
        bd.rect(slide, lx, ly, 0.14, ch, fill=c)
        label(bd, slide, lang, path["name"], lx + 0.48, ly + 0.32, lwc - 0.95,
              th + 0.3, size=13.5, bold=True, color=bd.DEEP, inline=bd.BI)
        label(bd, slide, lang, path["fact"], lx + 0.48, ly + 0.32 + th + 0.14,
              lwc - 0.95, dh + 0.6, size=11.0, color=bd.MUTED, inline=bd.BI)
        ly += ch + 0.34

    # the page-level note is emitted by r_figure, not here — drawing it in both
    # places is how it ended up printed twice.


# ================================================================== conv ====
def _fig_conv(bd, slide, sp, lang, x, y, w, h):
    src, ker = sp["input"], sp["kernel"]
    kr, kc = len(ker), len(ker[0])
    nr, nc = len(src), len(src[0])
    r0, c0 = sp.get("window", (0, 0))
    orows, ocols = nr - kr + 1, nc - kc + 1
    kmax = max(abs(z) for row in ker for z in row) or 1

    out = [[sum(ker[i][j] * src[a + i][b + j]
                for i in range(kr) for j in range(kc))
            for b in range(ocols)] for a in range(orows)]
    if sp.get("assert_out") is not None:
        assert out == sp["assert_out"], f"conv output drifted: {out}"

    cw = sp.get("cell", 1.18)
    cap_w = max(nc * cw, 9.8)
    cap_h = max(measure(bd, sp[k], lang, 12, cap_w, inline=bd.BI)
                for k in ("in_cap", "k_cap", "out_cap"))
    top = y + 0.55 + cap_h + 0.30
    ix = x
    kx = x + nc * cw + 2.15
    ox = x + nc * cw + kr * cw + 4.25

    label(bd, slide, lang, sp["in_cap"], ix, y + 0.55, cap_w, cap_h + 0.3,
          size=12, bold=True, color=bd.DEEP, inline=bd.BI)
    label(bd, slide, lang, sp["k_cap"], kx, y + 0.55 + (nr - kr) * cw / 2,
          cap_w, cap_h + 0.3, size=12, bold=True, color=bd.DEEP, inline=bd.BI)
    label(bd, slide, lang, sp["out_cap"], ox, y + 0.55, cap_w, cap_h + 0.3,
          size=12, bold=True, color=bd.DEEP, inline=bd.BI)

    for a in range(nr):
        for b in range(nc):
            v = src[a][b]
            cell(bd, slide, ix + b * cw, top + a * cw, cw, cw, grey(v, 0, 9),
                 text_v=v, color=WHITE if v >= 5 else bd.TEXT, size=9.5)

    wy, wx = top + r0 * cw, ix + c0 * cw
    bd.rect(slide, wx, wy, kc * cw, kr * cw, fill=None, line=bd.ACCENT,
            line_w=2.75)
    g = sp.get("ghost")
    if g:
        dash_rect(bd, slide, ix + g[1] * cw, top + g[0] * cw, kc * cw,
                  kr * cw, bd.ACCENT_BR, 1.75)

    ky = top + (nr - kr) * cw / 2
    arrow_r(bd, slide, ix + nc * cw + 0.20, kx - 0.15, wy + kr * cw / 2,
            color=bd.ACCENT_BR, w=1.5)
    for a in range(kr):
        for b in range(kc):
            v = ker[a][b]
            cell(bd, slide, kx + b * cw, ky + a * cw, cw, cw,
                 lerp(WHITE, bd.ORANGE, abs(v) / kmax),
                 text_v="%+d" % v if v else "0",
                 color=WHITE if abs(v) > kmax / 2 else bd.TEXT, size=9.5)
    label(bd, slide, lang, sp.get("kernel_note", ""), kx, ky + kr * cw + 0.30,
          kr * cw + 3.2, 0.7, size=10.5, color=bd.MUTED, inline=bd.BI)

    arrow_r(bd, slide, kx + kr * cw + 0.20, ox - 0.25, ky + kr * cw / 2,
            color=bd.ACCENT_BR, w=1.5)
    hi = tuple(sp.get("highlight", (0, 0)))
    for a in range(orows):
        for b in range(ocols):
            v = out[a][b]
            on = (a, b) == hi
            fill = bd.DEEP if on else lerp(WHITE, bd.ORANGE, min(1.0, abs(v) / 32.0))
            cell(bd, slide, ox + b * cw, top + a * cw, cw, cw, fill,
                 text_v="%+d" % v if v else "0",
                 color=WHITE if on or abs(v) >= 18 else bd.TEXT, size=9.5)
    bd.rect(slide, ox + hi[1] * cw, top + hi[0] * cw, cw, cw, fill=None,
            line=bd.DEEP, line_w=2.75)

    terms = ["%+dx%d" % (ker[i][j], src[r0 + i][c0 + j])
             for i in range(kr) for j in range(kc)]
    eq = "\n".join(" ".join(terms[q:q + kc]) for q in range(0, len(terms), kc))
    ay = y + h - 2.90
    bd.rect(slide, x, ay, w, 2.55, fill=bd.CODE_BG)
    bd.text(slide, x + 0.60, ay + 0.38, 11.0, 1.9,
            [(eq, {"font": bd.CODE_FONT, "size": 12.5})],
            size=12.5, color=bd.CODE_TEXT, spacing=1.24)
    bd.text(slide, x + 8.4, ay + 0.38, 5.0, 1.9,
            [("= %d" % out[hi[0]][hi[1]],
              {"font": bd.CODE_FONT, "size": 14, "bold": True})],
            size=14, color=RGBColor(0x93, 0xC5, 0xFD))
    label(bd, slide, lang, sp.get("arith_note"), x + 13.9, ay + 0.42,
          w - 14.5, 2.0, size=11.5, color=bd.CODE_TEXT, spacing=1.3,
          inline=bd.BI)


# ================================================================== pool ====
def _fig_pool(bd, slide, sp, lang, x, y, w, h):
    src = sp["input"]
    nr, nc = len(src), len(src[0])
    kh, kw = sp.get("k", (2, 2))
    orows, ocols = nr // kh, nc // kw
    cw = sp.get("cell", 1.58)
    panels = sp["panels"]
    lo, hi = min(min(r) for r in src), max(max(r) for r in src)

    max_out = [[max(src[a * kh + i][b * kw + j] for i in range(kh)
                    for j in range(kw)) for b in range(ocols)]
               for a in range(orows)]
    avg_out = [[sum(src[a * kh + i][b * kw + j] for i in range(kh)
                    for j in range(kw)) / (kh * kw) for b in range(ocols)]
               for a in range(orows)]
    if sp.get("assert_max") is not None:
        assert max_out == sp["assert_max"], f"max-pool drifted: {max_out}"

    gapx = 2.95
    blk = nc * cw + gapx + ocols * cw
    total = len(panels) * blk + (len(panels) - 1) * 2.1
    x0 = x + max(0.0, (w - total) / 2)

    for pi, p in enumerate(panels):
        px = x0 + pi * (blk + 2.1)
        th = measure(bd, p["title"], lang, 14, blk, inline=bd.BI)
        label(bd, slide, lang, p["title"], px, y + 0.58, blk, th + 0.3,
              size=14, bold=True, color=bd.DEEP, inline=bd.BI)
        sy = y + 0.58 + th + 0.16
        sh = measure(bd, p["sub"], lang, 11, blk, inline=bd.BI)
        label(bd, slide, lang, p["sub"], px, sy, blk, sh + 0.3, size=11,
              color=bd.MUTED, inline=bd.BI)
        top = sy + sh + 0.78

        for a in range(nr):
            for b in range(nc):
                v = src[a][b]
                cell(bd, slide, px + b * cw, top + a * cw, cw, cw,
                     grey(v, lo, hi), text_v=v,
                     color=WHITE if v >= 6 else bd.TEXT, size=11)
        if pi == 0:
            bd.rect(slide, px, top, kw * cw, kh * cw, fill=None,
                    line=bd.ACCENT, line_w=2.75)
            bd.rect(slide, px + kw * cw, top + kh * cw, kw * cw, kh * cw,
                    fill=None, line=bd.ACCENT_BR, line_w=1.0)

        arrow_r(bd, slide, px + nc * cw + 0.25, px + nc * cw + gapx - 0.30,
                top + nr * cw / 2, color=bd.ACCENT_BR, w=2.0)

        ox = px + nc * cw + gapx
        oy = top + (nr - orows) * cw / 2
        for a in range(orows):
            for b in range(ocols):
                if pi == 0:
                    fill = bd.DEEP if (a, b) == (0, 0) else bd.GREEN_BG
                    fg = WHITE if (a, b) == (0, 0) else bd.GREEN
                    txt = str(max_out[a][b])
                else:
                    fill = bd.DEEP if (a, b) == (0, 0) else bd.ORANGE_BG
                    fg = WHITE if (a, b) == (0, 0) else bd.ORANGE
                    txt = ("%.1f" % avg_out[a][b]).rstrip("0").rstrip(".")
                cell(bd, slide, ox + b * cw, oy + a * cw, cw, cw, fill,
                     text_v=txt, color=fg, size=12, bold=True)
        bd.rect(slide, ox, oy, cw, cw, fill=None, line=bd.DEEP, line_w=2.75)

        label(bd, slide, lang, p["note"], px, top + nr * cw + 0.45, blk, 1.3,
              size=11, color=bd.MUTED, spacing=1.3, inline=bd.BI)


# ====================================================== confusion matrix ====
def _fig_cm(bd, slide, sp, lang, x, y, w, h):
    tp, fn, fp, tn = sp["tp"], sp["fn"], sp["fp"], sp["tn"]
    n = tp + fn + fp + tn
    acc = (tp + tn) / n
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)
    base = max(tp + fn, tn + fp) / n          # what "always guess majority" gets

    cw, ch = sp.get("cell", 7.40), sp.get("ch", 3.85)
    gx, gy = 0.55, 0.55
    lab_w = 3.30
    mx0 = x + lab_w
    my0 = y + 1.78

    label(bd, slide, lang, sp["col_cap"], mx0, y + 0.56, 2 * cw + gx, 0.55,
          size=12, bold=True, color=bd.MUTED, align=PP_ALIGN.CENTER,
          inline=bd.BI)
    for b, lab in enumerate(sp["col_labels"]):
        label(bd, slide, lang, lab, mx0 + b * (cw + gx), y + 1.12, cw, 0.5,
              size=12.5, color=bd.TEXT, align=PP_ALIGN.CENTER)
    for a, lab in enumerate(sp["row_labels"]):
        label(bd, slide, lang, lab, x, my0 + a * (ch + gy), lab_w - 0.25, ch,
              size=12.5, color=bd.TEXT, anchor=MSO_ANCHOR.MIDDLE,
              align=PP_ALIGN.RIGHT, spacing=1.2)
    label(bd, slide, lang, sp["row_cap"], x - 0.05, my0 + ch + gy / 2, lab_w,
          0.5, size=12, bold=True, color=bd.MUTED, align=PP_ALIGN.RIGHT,
          inline=bd.BI)

    for a, b, v, tag, bg, fg in ((0, 0, tp, "TP", bd.GREEN_BG, bd.GREEN),
                                 (0, 1, fp, "FP", bd.RED_BG, bd.RED),
                                 (1, 0, fn, "FN", bd.RED_BG, bd.RED),
                                 (1, 1, tn, "TN", bd.GREEN_BG, bd.GREEN)):
        cx = mx0 + b * (cw + gx)
        cy = my0 + a * (ch + gy)
        bd.rect(slide, cx, cy, cw, ch, fill=bg, line=fg, line_w=1.4)
        bd.text(slide, cx + 0.35, cy + 0.42, cw - 0.7, 1.05, str(v), size=30,
                bold=True, color=fg, align=PP_ALIGN.CENTER)
        bd.text(slide, cx + 0.35, cy + 1.78, cw - 0.7, 1.1,
                bd.L(sp["tags"][tag], lang), size=12, color=fg,
                align=PP_ALIGN.CENTER, spacing=1.2, sec_inline=bd.BI)

    rx = mx0 + 2 * cw + gx + 0.95
    rw = x + w - rx
    label(bd, slide, lang, sp["metrics_cap"], rx, y + 0.56, rw, 0.6, size=13,
          bold=True, color=bd.DEEP, inline=bd.BI)
    yy = y + 1.45
    # the description under each metric is bilingual here, so the row has to be
    # as tall as the *taller* language pays for — a fixed height lets the second
    # language print straight over the row below
    dh = max(measure(bd, d, lang, 10.5, rw - 0.84, inline=bd.BI)
             for d in (sp["m_acc"], sp["m_prec"], sp["m_rec"], sp["m_f1"]))
    rh = 0.90 + dh + 0.29
    for name, val, desc in (("Accuracy", "%.3f" % acc, sp["m_acc"]),
                            ("Precision", "%.3f" % prec, sp["m_prec"]),
                            ("Recall", "%.3f" % rec, sp["m_rec"]),
                            ("F1", "%.3f" % f1, sp["m_f1"])):
        bd.rect(slide, rx, yy, rw, rh, fill=bd.GHOST, line=bd.BORDER)
        bd.text(slide, rx + 0.42, yy + 0.22, 4.2, 0.6, name, size=13,
                bold=True, color=bd.DEEP)
        bd.text(slide, rx + rw - 3.4, yy + 0.14, 3.0, 0.7, val, size=19,
                bold=True, color=bd.ACCENT, align=PP_ALIGN.RIGHT)
        label(bd, slide, lang, desc, rx + 0.42, yy + 0.92, rw - 0.84, dh + 0.3,
              size=10.5, color=bd.MUTED, spacing=1.2, inline=bd.BI)
        yy += rh + 0.20

    bh = bd.para_h(bd.L(sp["baseline"], lang), 11.5, rw - 0.84, 1.25, bd.BI)
    bd.rect(slide, rx, yy + 0.10, rw, bh + 0.62, fill=bd.RED_BG, line=bd.RED)
    bd.text(slide, rx + 0.42, yy + 0.38, rw - 0.84, bh + 0.3,
            bd.L(sp["baseline"], lang).replace("{base}", "%.3f" % base),
            size=11.5, color=bd.RED, spacing=1.25, sec_inline=bd.BI)


# ============================================== three bias/variance shapes ===
def curve_pair(kind):
    """Schematic train/validation loss against fraction-of-training.

    No numbers are claimed: these are shape sketches for reading a curve, which
    is exactly what the Week 6 slide asks students to do.  The measured curves
    live on the two chart pages either side of it.
    """
    t = [k / 60.0 for k in range(61)]
    if kind == "underfit":
        return ([0.84 - 0.17 * v for v in t], [0.88 - 0.16 * v for v in t])
    if kind == "good":
        return ([0.92 * math.exp(-3.6 * v) + 0.05 for v in t],
                [0.88 * math.exp(-3.2 * v) + 0.10 for v in t])
    if kind == "overfit":
        return ([0.96 * math.exp(-4.4 * v) + 0.015 for v in t],
                [0.88 * math.exp(-3.8 * v) + 0.085 + 0.44 * v ** 2.7 for v in t])
    raise ValueError(kind)


def _fig_curves(bd, slide, sp, lang, x, y, w, h):
    panels = sp["panels"]
    n = len(panels)
    gap = 0.95
    pw = (w - gap * (n - 1)) / n
    for i, p in enumerate(panels):
        px = x + i * (pw + gap)
        panel(bd, slide, px, y, pw, h)
        bx = px + 0.82
        bw = pw - 1.64
        th = measure(bd, p["title"], lang, 14.5, bw, inline=bd.BI)
        label(bd, slide, lang, p["title"], bx, y + 0.54, bw, th + 0.3,
              size=14.5, bold=True, color=bd.DEEP, inline=bd.BI)
        sh = measure(bd, p["sub"], lang, 11, bw, inline=bd.BI)
        label(bd, slide, lang, p["sub"], bx, y + 0.54 + th + 0.14, bw, sh + 0.3,
              size=11, color=bd.MUTED, inline=bd.BI)

        ay = y + 0.54 + th + sh + 1.05
        vy = measure(bd, p["verdict"], lang, 11.5, bw, inline=bd.BI)
        # stack the panel from the bottom up: the verdict is the one block that
        # grows with the second language, so it decides where the axes stop
        vy_y = y + h - 0.38 - vy
        ly = vy_y - 0.62
        ah = ly - 0.78 - ay
        aw = bw - 0.30
        axes(bd, slide, bx, ay, aw, ah)
        tr, va = curve_pair(p["shape"])
        ep = [k / 60.0 for k in range(61)]
        plot(bd, slide, bx, ay, aw, ah, ep, tr, (0.0, 1.0), (0.0, 1.0),
             color=bd.ACCENT, width=2.4)
        plot(bd, slide, bx, ay, aw, ah, ep, va, (0.0, 1.0), (0.0, 1.0),
             color=bd.ORANGE, width=2.4, dash=True)
        label(bd, slide, lang, sp["x_axis"], bx, ay + ah + 0.16, aw, 0.45,
              size=10.5, color=bd.MUTED, align=PP_ALIGN.CENTER)

        for k, key in enumerate(("train", "val")):
            cc = bd.ACCENT if key == "train" else bd.ORANGE
            line(bd, slide, bx + k * bw / 2, ly + 0.20,
                 bx + k * bw / 2 + 0.55, ly + 0.20, color=cc, w=2.6,
                 dash=(key == "val"))
            bd.text(slide, bx + k * bw / 2 + 0.70, ly, bw / 2 - 0.95, 0.5,
                    bd.L(sp["labels"][key], lang), size=11, color=bd.MUTED)
        label(bd, slide, lang, p["verdict"], bx, vy_y, bw, vy + 0.3,
              size=11.5, bold=True, color=bd.col(p["accent"], bd.DEEP),
              align=PP_ALIGN.CENTER, inline=bd.BI)


# ============================================================ shape chain ===
def _fig_shapes(bd, slide, sp, lang, x, y, w, h):
    """A left-to-right tensor pipeline: box, arrow, and the shape under it."""
    steps = sp["steps"]
    n = len(steps)
    gap = 0.60
    bw = (w - gap * (n - 1)) / n
    bh = sp.get("box_h", 3.00)
    by = y + 1.35
    for i, s in enumerate(steps):
        bx = x + i * (bw + gap)
        c = bd.col(s.get("color"), bd.ACCENT)
        bd.rect(slide, bx, by, bw, bh, fill=bd.GHOST, line=c, line_w=1.4,
                shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.10)
        bd.text(slide, bx + 0.24, by + 0.20, bw - 0.48, bh - 0.4,
                bd.L(s["title"], lang), size=12.5, bold=True, color=c,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2,
                sec_inline=bd.BI)
        if s.get("shape"):
            label(bd, slide, lang, s["shape"], bx, by + bh + 0.26, bw, 0.55,
                  size=12, align=PP_ALIGN.CENTER)
        if i < n - 1:
            arrow_r(bd, slide, bx + bw + 0.05, bx + bw + gap - 0.05,
                    by + bh / 2, color=bd.MUTED, w=1.5)

    ny = by + bh + 1.05
    if sp.get("note_under"):
        nh = measure(bd, sp["note_under"], lang, 11.5, w, inline=bd.BI)
        label(bd, slide, lang, sp["note_under"], x, ny, w, nh + 0.5,
              size=11.5, color=bd.MUTED, spacing=1.3, inline=bd.BI)
        ny += nh + 0.70

    lo = sp.get("lower")
    if lo:
        lh = lo.get("box_h", 2.50)
        label(bd, slide, lang, lo["cap"], x, ny, w, 0.55, size=12.5, bold=True,
              color=bd.DEEP)
        ly = ny + 0.62
        m = len(lo["steps"])
        lgap = 0.60
        lbw = (w - lgap * (m - 1)) / m
        for i, s in enumerate(lo["steps"]):
            bx = x + i * (lbw + lgap)
            c = bd.col(s.get("color"), bd.ACCENT_BR)
            bd.rect(slide, bx, ly, lbw, lh, fill=bd.CARD, line=c, line_w=1.2,
                    shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.10)
            bd.text(slide, bx + 0.20, ly + 0.18, lbw - 0.4, lh - 0.36,
                    bd.L(s["title"], lang), size=11.5, bold=True, color=c,
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                    spacing=1.2, sec_inline=bd.BI)
            if i < m - 1:
                arrow_r(bd, slide, bx + lbw + 0.05, bx + lbw + lgap - 0.05,
                        ly + lh / 2, color=bd.MUTED, w=1.4)


# ============================================================== masking =====
def _fig_mask(bd, slide, sp, lang, x, y, w, h):
    """Two rows over the same slots: the token ids, then the mask they produce.

    Row 1 is the document — real tokens shaded, padding blank.  Row 2 is the
    mask the model should be multiplying by: 1 on a real token, 0 on padding.
    The red rule marks where padding starts, which is where every un-masked
    mean over the time axis silently loses its denominator.
    """
    nt = sp.get("real", 9)
    total = sp.get("width", 24)
    cw = min((w - 4.6) / total, 1.02)
    gx = x + 0.1
    ch = cw
    cap_h = measure(bd, sp["cap_len"], lang, 12.5, 11.6, inline=bd.BI)
    ty = y + 0.44 + cap_h + 0.72

    label(bd, slide, lang, sp["cap_len"], gx - 0.15, y + 0.44, 11.6, cap_h + 0.3,
          size=12.5, bold=True, color=bd.DEEP, inline=bd.BI)

    for r, lab in enumerate((sp["row_real"], sp["row_pad"])):
        ry = ty + r * (ch + 0.32)
        for i in range(total):
            if r == 0:                                  # the document itself
                if i < nt:
                    fill = lerp(WHITE, bd.ACCENT,
                                0.25 + 0.55 * (i / max(1, nt - 1)))
                    text_v, fg = (str(i + 1) if cw >= 0.82 else None), WHITE
                else:
                    fill, text_v, fg = bd.GHOST, None, bd.MUTED
            else:                                        # the mask
                if i < nt:
                    fill, text_v, fg = bd.GREEN_BG, "1", bd.GREEN
                else:
                    fill, text_v, fg = bd.RED_BG, "0", bd.RED
            cell(bd, slide, gx + i * cw, ry, cw, ch, fill, text_v=text_v,
                 color=fg, size=9.5 if r else 9)
        label(bd, slide, lang, lab, gx + total * cw + 0.35, ry, 3.8, ch,
              size=11.5, color=bd.TEXT if r == 0 else bd.MUTED,
              anchor=MSO_ANCHOR.MIDDLE, inline=bd.BI)

    # The tick reads "slot 1 ..." — i.e. the numbering starts at the first drawn
    # cell and runs on to the right.  It used to be placed off the *right* end of
    # the grid, which said the opposite.
    label(bd, slide, lang, sp["tick"], gx + 0.02,
          ty + 2 * ch + 1.05, 4.2, 0.55, size=10.5, color=bd.MUTED,
          inline=bd.BI)

    # the marker goes *below* the grid: above it, a long bilingual caption in the
    # same band had nowhere to go
    px = gx + nt * cw
    line(bd, slide, px, ty - 0.45, px, ty + 2 * ch + 0.55, color=bd.RED, w=1.5,
         dash=True)
    label(bd, slide, lang, sp["pad_mark"], px + 0.18, ty + 2 * ch + 0.42,
          8.5, 0.55, size=11, color=bd.RED, inline=bd.BI)

    my = ty + 2 * ch + 2.30
    mh = min(2.30, max(1.60, y + h - my))
    bd.rect(slide, x, my, w, mh, fill=bd.CODE_BG)
    # The two listings are written as {"en": .., "zh": ..} and picked the way the
    # `code` renderer picks them — a bilingual deck reads the English listing, not
    # both.  Printing bd.L() here would stack a second line and run it out of the
    # band; leaving the source as a bare string printed the *Chinese* comments in
    # the English deck, which validate_deck.py flags as a CJK leak.
    for key, col, dx in (("code_wrong", RGBColor(0xF8, 0xB4, 0xB4), 0.60),
                         ("code_right", RGBColor(0x86, 0xEF, 0xAC), w / 2 + 0.30)):
        src = sp[key]
        if isinstance(src, dict):
            src = src.get(lang) or src.get("en")
        bd.text(slide, x + dx, my + 0.32, w / 2 - 1.4, mh - 0.64,
                [(ln, {"font": bd.CODE_FONT, "size": 12.5})
                 for ln in src.split("\n")],
                size=12.5, color=col, spacing=1.28)


# ====================================================== receptive field =====
def _fig_rf(bd, slide, sp, lang, x, y, w, h):
    """How much of the input one output cell can see, layer by layer.

    Three identical grids stand for the input and the two feature maps after it.
    The shaded square is the set of cells that feed one cell of the *next*
    stage — the point being that it grows by (k - 1) per layer, so the receptive
    field of a deep stack is much larger than the kernel suggests.
    """
    n = sp.get("grid", 9)
    layers = sp["layers"]
    cw = sp.get("cell", 1.02)
    gap = 2.30
    gw = n * cw
    total = len(layers) * gw + (len(layers) - 1) * gap
    x0 = x + max(0.0, (w - total) / 2)

    th = max(measure(bd, p["title"], lang, 13.5, gw + 1.2, inline=bd.BI)
             for p in layers)
    sh = max(measure(bd, p["sub"], lang, 11, gw + 1.2, inline=bd.BI)
             for p in layers)
    top = y + 0.60 + th + sh + 0.85

    for i, p in enumerate(layers):
        px = x0 + i * (gw + gap)
        label(bd, slide, lang, p["title"], px - 0.6, y + 0.60, gw + 1.2,
              th + 0.3, size=13.5, bold=True, color=bd.DEEP,
              align=PP_ALIGN.CENTER, inline=bd.BI)
        label(bd, slide, lang, p["sub"], px - 0.6, y + 0.60 + th + 0.16,
              gw + 1.2, sh + 0.3, size=11, color=bd.MUTED,
              align=PP_ALIGN.CENTER, inline=bd.BI)

        for a in range(n):
            for b in range(n):
                cell(bd, slide, px + b * cw, top + a * cw, cw, cw, WHITE,
                     outline=bd.BORDER, lw=0.6)

        c = n // 2
        reach = min(int(p["reach"]), n)    # a window cannot outgrow the grid
        # Centred on the output cell, then pulled back inside the grid: on the
        # last stage reach == n, where "centred" would start at column 1 and hang
        # one cell off the right edge.
        lo = max(0, min(n - reach, c - (reach - 1) // 2))
        bd.rect(slide, px + lo * cw, top + lo * cw, reach * cw, reach * cw,
                fill=lerp(WHITE, bd.ACCENT, 0.13), line=bd.ACCENT, line_w=1.4)
        bd.rect(slide, px + c * cw, top + c * cw, cw, cw, fill=bd.DEEP,
                line=bd.DEEP, line_w=1.0)

        if i < len(layers) - 1:
            arrow_r(bd, slide, px + gw + 0.16, px + gw + gap - 0.20,
                    top + gw / 2, color=bd.MUTED, w=1.6)

    note_y = top + gw + (0.95 if sp.get("scale") else 0.62)
    for i, p in enumerate(layers):
        px = x0 + i * (gw + gap)
        label(bd, slide, lang, p["note"], px - 0.6, note_y, gw + 1.2, 1.2,
              size=11, color=bd.col(p.get("color"), bd.MUTED),
              align=PP_ALIGN.CENTER, spacing=1.3, inline=bd.BI)

    if sp.get("scale"):
        label(bd, slide, lang, sp["scale"], x, note_y + 1.35, w, 0.8, size=11.5,
              color=bd.TEXT, align=PP_ALIGN.CENTER, inline=bd.BI)


# ------------------------------------------------------------------ driver --
KINDS = {
    "descent1d": _fig_descent1d,
    "contour": _fig_contour,
    "conv": _fig_conv,
    "pool": _fig_pool,
    "rf": _fig_rf,
    "cm": _fig_cm,
    "curves": _fig_curves,
    "shapes": _fig_shapes,
    "mask": _fig_mask,
}


def register(bd):
    """Hand the builder a ``figure`` renderer.  Called at the end of
    build_deck.py, which keeps this module from importing it back."""

    def r_figure(slide, sp, ctx):
        lang = ctx["lang"]
        bd.header(slide, sp["title"], sp.get("right"), lang, sp.get("subtitle"))
        bd.footer(slide, ctx["week"], sp["page"], ctx["total"])
        top = sp.get("top", bd.BODY_TOP + 0.35)
        note = sp.get("note")
        nh = 0.0
        if note:
            nh = bd.para_h(bd.L(note, lang), 12, bd.CW, 1.35) + 0.62
        avail = bd.FOOTER_Y - 0.34 - nh - top
        h = min(sp.get("h", avail), avail)
        KINDS[sp["kind"]](bd, slide, sp, lang, bd.M, top, bd.CW, h)
        if note:
            nv = bd.L(note, lang)
            ny = min(top + h + 0.52,
                     bd.FOOTER_Y - 0.34 - bd.para_h(nv, 12, bd.CW, 1.35))
            bd.text(slide, bd.M, ny, bd.CW, 1.8, nv, size=12, color=bd.MUTED,
                    spacing=1.35)

    bd.RENDERERS["figure"] = r_figure
