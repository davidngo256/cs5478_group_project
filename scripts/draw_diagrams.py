"""The two drawn diagrams of the report and the decks, cones.png and pipeline.png, in the design language
(design_language/, sections 6 and 11): ink line work, Surface 2 for the off-the-shelf blocks, mono labels, one
Photon element per image. Like plot_sim.py, each is drawn twice at the size it is placed (results/figures/
for the report, results/figures/slides/ for the decks) so the type stays at or above the floor of its medium
(9 pt in a document, 20 px = 10 pt on a slide). Tokens and font registration come from plot_sim.py. The PNGs
are deterministic. Usage: python scripts/draw_diagrams.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_sim import DPI, HAIRLINE, INK, INK2, MONO, MUTED, PHOTON, PHOTON_SOFT, RESULTS, SANS, SURFACE, SURFACE2

OUT = RESULTS / "figures"
MONO_FB = [MONO, SANS]        # Plex Mono has no Greek: mu and epsilon fall back glyph by glyph to Plex Sans
# width in inches at the point of use and the type size (see plot_sim.TARGETS): the floor of the medium in the
# report; on the slides both diagrams fill the 12-column width of a slide of the final presentation and their
# type is sized for a room (14 pt = 28 px on the 1920 px canvas), with the line work scaled to match
TARGETS = {"report": dict(sub="", fs=9.0, cones=3.3, pipeline=5.5, long=False, tight=True),
           "slides": dict(sub="slides", fs=14.0, cones=12.0, pipeline=12.0, long=True, tight=False)}


# ---- cones.png: the same antipodal grasp at mu = 0.5 and mu = 0.2 -------------------------------------------
W, H, L = 3.6, 2.1, 1.65      # object width and height, cone length along the normal (drawing units)
TILT = 14.9                   # angle between the segment p1p2 and the inward normals, degrees


def cone(ax, apex, direction, half_angle, length, k=1.0):
    """Friction cone as an isosceles triangle, apex at the contact, opening inward along `direction`."""
    x, y = apex
    h = length * np.tan(np.radians(half_angle))
    bx = x + direction * length
    ax.add_patch(Polygon([(x, y), (bx, y + h), (bx, y - h)], closed=True, facecolor=SURFACE, edgecolor=INK,
                         linewidth=1.2 * k, joinstyle="miter", zorder=3))


def cones_panel(ax, mu, title, verdict, fs):
    k = fs / 9.0 if fs > 10 else 1.0          # line work grows with the type of the large slide drawing
    half = np.degrees(np.arctan(mu))
    dy = W * np.tan(np.radians(TILT))
    p1, p2 = (0.0, H / 2 + dy / 2), (W, H / 2 - dy / 2)
    ax.add_patch(Rectangle((0, 0), W, H, facecolor=SURFACE2, edgecolor=HAIRLINE, linewidth=0.8, zorder=1))
    cone(ax, p1, +1, half, L, k)
    cone(ax, p2, -1, half, L, k)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=PHOTON, lw=1.5 * k, solid_capstyle="round", zorder=4)   # the one Photon element
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "o", color=INK, ms=4.5 * k, zorder=5)
    ax.text(p1[0] - 0.14, p1[1], "p₁", ha="right", va="center", fontsize=fs + 1, color=INK, family=MONO_FB)
    ax.text(p2[0] + 0.14, p2[1], "p₂", ha="left", va="center", fontsize=fs + 1, color=INK, family=MONO_FB)
    # a mono label above (under 40 characters) and the verdict as a mixed-case sans line in Ink 2 below
    ax.text(W / 2, H + 0.58, title, ha="center", va="center", fontsize=fs, color=MUTED, family=MONO_FB)
    ax.text(W / 2, -0.55, verdict, ha="center", va="center", fontsize=fs, color=INK2, family=SANS)
    ax.set_xlim(-0.75, W + 0.75); ax.set_ylim(-0.8, H + 0.8)
    ax.set_aspect("equal"); ax.axis("off")


def draw_cones(out, width, fs, long):
    fig, axes = plt.subplots(1, 2, figsize=(width, width / 3.0), dpi=DPI)
    if long:
        titles = ("μ = 0.5 · HALF-ANGLE 26.6°", "μ = 0.2 · HALF-ANGLE 11.3°")
        verdicts = ("Force closure (14.9° ≤ 26.6°)", "Not force closure (14.9° > 11.3°)")
    else:
        titles = ("μ = 0.5 · α = 26.6°", "μ = 0.2 · α = 11.3°")
        verdicts = ("force closure", "not force closure")
    cones_panel(axes[0], 0.5, titles[0], verdicts[0], fs)
    cones_panel(axes[1], 0.2, titles[1], verdicts[1], fs)
    fig.tight_layout(pad=0.4); fig.savefig(out); plt.close(fig)


# ---- pipeline.png: the block diagram -------------------------------------------------------------------------
KIND = {"new": dict(facecolor=PHOTON_SOFT, edgecolor=PHOTON),          # the one Photon element: the wash
        "fixed": dict(facecolor=SURFACE2, edgecolor=HAIRLINE),
        "io": dict(facecolor=SURFACE, edgecolor=HAIRLINE)}
# (key, kind, title, subtitle lines); a subtitle line is a string or a list of (text, subscript) pieces
TOP = [("rgb", "io", "RGB image", ["one view"]),
       ("seg", "fixed", "Segmentation", ["SAM, fixed"]),
       ("head", "new", "Material head", ["MobileNetV3"]),
       ("mu", "new", "μ lookup", ["class → p(μ)"])]
BOTTOM = [("depth", "io", "Depth", ["point cloud"]),
          ("cand", "fixed", "Candidates", ["generator"])]
SCORER = ("scorer", "new", "Material-conditioned scorer",
          [[("friction cones at μ", False), ("q", True)],
           "rank by ε or filter by FC",
           [("grip force from μ", False), ("q", True)]])
OUTPUT = ("out", "io", "Grasp pose", ["+ force"])


def arrow(ax, p, q, fs, color=INK, lw=1.0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.22", color=color,
                                                     lw=lw, mutation_scale=fs * 1.1, shrinkA=0, shrinkB=0))


class Measure:
    """Text widths in inches at the figure's dpi, so blocks can be sized from their content."""

    def __init__(self, fig, ax):
        self.fig, self.ax = fig, ax
        self.renderer = fig.canvas.get_renderer()

    def width(self, s, size, family=MONO_FB, weight=400):
        t = self.ax.text(0, 0, s, fontsize=size, family=family, weight=weight)
        w = t.get_window_extent(self.renderer).width / DPI
        t.remove()
        return w

    def line(self, line, size):
        if isinstance(line, str):
            return self.width(line, size)
        return sum(self.width(s, size * (0.78 if sub else 1)) for s, sub in line)


def rich_line(m, ax, cx, y, pieces, size, color):
    """A centred mono line composed of pieces, each (text, subscript); subscripts are smaller and lowered."""
    widths = [m.width(s, size * (0.78 if sub else 1)) for s, sub in pieces]
    x = cx - sum(widths) / 2
    for (s, sub), w in zip(pieces, widths):
        ax.text(x, y - (0.03 if sub else 0), s, fontsize=size * (0.78 if sub else 1), color=color, family=MONO_FB,
                ha="left", va="baseline")
        x += w


def block(m, ax, x0, x1, y0, y1, kind, title, subs, ts, fs, pad):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.015",
                                linewidth=0.8, zorder=2, **KIND[kind]))
    cx = (x0 + x1) / 2
    lh_t, lh_s = ts * 1.3 / 72, fs * 1.3 / 72          # line pitches in inches
    y = y1 - pad - lh_t * 0.75
    ax.text(cx, y, title, ha="center", va="baseline", fontsize=ts, color=INK, family=SANS, weight=600, zorder=3)
    for sub in subs:
        y -= lh_s
        if isinstance(sub, str):
            ax.text(cx, y, sub, ha="center", va="baseline", fontsize=fs, color=MUTED, family=MONO_FB, zorder=3)
        else:
            rich_line(m, ax, cx, y, sub, fs, MUTED)


def draw_pipeline(out, width, fs, tight=False):
    """tight: the report's 5.5 in line leaves the blocks little slack, so a column is as wide as the wider of its
    two blocks and the mask label stands left of its connector, clear of the scorer block."""
    ts = fs + 0.5                      # block titles, Plex Sans 600
    pad = 0.5 * fs / 72                # inner padding of a block, inches
    gap = (0.03 if tight else 0.035) * width      # the arrows between blocks
    margin = 0.03
    fig = plt.figure(figsize=(width, 1.0), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    m = Measure(fig, ax)

    def natural(spec):
        _, _, title, subs = spec
        return max([m.width(title, ts, SANS, 600)] + [m.line(s, fs) for s in subs]) + 2 * pad

    widths = {s[0]: natural(s) for s in TOP + BOTTOM + [SCORER, OUTPUT]}
    if tight:
        widths["rgb"] = max(widths["rgb"], widths["depth"]); widths["seg"] = max(widths["seg"], widths["cand"])
    short = widths["scorer"] - (widths["head"] + widths["mu"] + gap)   # the scorer spans its two parents
    if short > 0:
        widths["head"] += short / 2; widths["mu"] += short / 2
    row = sum(widths[s[0]] for s in TOP) + 3 * gap
    need = 2 * margin + row + gap + widths["out"]
    assert need <= width, f"pipeline text needs {need:.2f} in, figure is {width:.2f} in: shorten a label"
    extra = (width - need) / 5                                   # the slack widens the five blocks of the row
    xs, x = {}, margin
    for key, _, _, _ in TOP:
        xs[key] = (x, x + widths[key] + extra); x = xs[key][1] + gap
    xs["out"] = (x, x + widths["out"] + extra)
    xs["depth"], xs["cand"] = xs["rgb"], xs["seg"]
    xs["scorer"] = (xs["head"][0], xs["mu"][1])
    assert xs["scorer"][1] - xs["scorer"][0] >= widths["scorer"], "the scorer block is wider than its two parents"

    hb = (ts + fs) * 1.3 / 72 + 2 * pad                          # a block with one subtitle line
    hs = (ts + 3 * fs) * 1.3 / 72 + 2 * pad                      # the scorer, three lines
    y_leg, y_bot = 0.1, 0.42
    y_top = y_bot + hs + 0.38                                    # room for the mask label and the mu arrow
    height = y_top + hb + 0.08
    fig.set_size_inches(width, height)
    ax.set_xlim(0, width); ax.set_ylim(0, height)
    ys = {k: (y_top, y_top + hb) for k, _, _, _ in TOP}
    ys.update({k: (y_bot, y_bot + hb) for k, _, _, _ in BOTTOM})
    ys["scorer"] = (y_bot, y_bot + hs)
    oc = (y_bot + hs) / 2 + y_bot / 2                            # output block centred on the scorer
    ys["out"] = (oc - hb / 2, oc + hb / 2)
    for key, kind, title, subs in TOP + BOTTOM + [SCORER, OUTPUT]:
        block(m, ax, *xs[key], *ys[key], kind, title, subs, ts, fs, pad)

    yt = (ys["rgb"][0] + ys["rgb"][1]) / 2
    yb = (ys["depth"][0] + ys["depth"][1]) / 2
    for a, b in (("rgb", "seg"), ("seg", "head"), ("head", "mu")):
        arrow(ax, (xs[a][1], yt), (xs[b][0], yt), fs)
    for a, b in (("depth", "cand"), ("cand", "scorer")):
        arrow(ax, (xs[a][1], yb), (xs[b][0], yb), fs)
    xm = (xs["mu"][0] + xs["mu"][1]) / 2
    arrow(ax, (xm, ys["mu"][0]), (xm, ys["scorer"][1]), fs)
    arrow(ax, (xs["scorer"][1], oc), (xs["out"][0], oc), fs)
    # the object mask: a thin connector from the segmentation down to the candidate generator
    xc = (xs["seg"][0] + xs["seg"][1]) / 2
    arrow(ax, (xc, ys["seg"][0]), (xc, ys["cand"][1]), fs, color=MUTED, lw=0.7)
    ax.text(xc - 0.06 if tight else xc + 0.06, (ys["seg"][0] + ys["cand"][1]) / 2, "object mask",
            ha="right" if tight else "left", va="center", fontsize=fs, color=MUTED, family=MONO_FB)
    # legend, bottom left
    x = margin
    sw = 0.14
    for kind, label in (("new", "NEW IN THIS PROJECT"), ("fixed", "OFF THE SHELF, HELD FIXED ACROSS ALL ARMS")):
        ax.add_patch(FancyBboxPatch((x, y_leg), sw, sw, boxstyle="round,pad=0,rounding_size=0.015", linewidth=0.8,
                                    **KIND[kind]))
        ax.text(x + sw + 0.08, y_leg + sw / 2, label, ha="left", va="center", fontsize=fs, color=MUTED, family=MONO_FB)
        x += sw + 0.08 + m.width(label, fs) + 0.3
    fig.savefig(out); plt.close(fig)
    return height


def main():
    for name, t in TARGETS.items():
        out = OUT / t["sub"]
        out.mkdir(parents=True, exist_ok=True)
        draw_cones(out / "cones.png", t["cones"], t["fs"], t["long"])
        h = draw_pipeline(out / "pipeline.png", t["pipeline"], t["fs"], t["tight"])
        print(f"{name} diagrams written to {out} (pipeline {t['pipeline']:.2f} x {h:.2f} in)")


if __name__ == "__main__":
    main()
