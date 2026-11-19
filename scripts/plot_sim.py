"""Figures for the report and the decks from results/sim/<run>/rows.jsonl.
Usage: python scripts/plot_sim.py core [heads]
  core:  the per-object 2x2 bars, the constant-mu sweep, epsilon vs wrench and the paired 2x2 gains
  heads: the paired gains of the head arms (fig_heads.png)
  The torsion runs (results/sim/torsion_k*.json, when present) add fig_torsion.png: the 2x2 gains at each
  planner torsional scale on the first 40 trials per object.

Every figure is drawn twice, each time at the size it is placed, so its type is never scaled under the floor
of the design language (section 6: 9 pt in a document, 20 px = 10 pt on the 1920 px slide canvas):
  results/figures/          the report set, sized for the NeurIPS 5.5 in line (report/report.tex)
  results/figures/slides/   the deck set, sized for the slide boxes of scripts/deck_style.py (1 px = 1/144 in)
The deck set also holds the talk charts of the final presentation (TARGETS["slides"]["talk"]), drawn at 24 px
type for a room: fig_oracle_objects.png (baseline against oracle per object, one mode), fig_2x2_gain.png
(fig_2x2_bars at the larger type; fig_2x2_bars.png stays as the milestone slides placed it),
fig_eps_vs_wrench.png and fig_heads_force.png (force only against grasp and force per head, pooled).
Presentation follows design_language/ (tokens.json, sections 5, 6 and 10): IBM Plex Sans for legends, IBM
Plex Mono for ticks, axis labels and direct labels, text in ink or muted only, the fixed data slots in COLOUR,
a hairline grid, no fill or frame of its own (the report and the decks add the hairline outline and the mono
caption line). The PNGs are deterministic.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matgrasp.analysis import load_rows, paired_diff, table_by_trial
from matgrasp.experiment import RESULTS
from matgrasp.friction import MATERIAL_TABLE
from matgrasp.ycb import OBJECTS

# Tokens (design_language/tokens.json, light mode).
INK, INK2, MUTED, SURFACE, SURFACE2 = "#0E1B2A", "#4A5563", "#626C78", "#FFFFFF", "#EFEDE8"
HAIRLINE, GRID = (14 / 255, 27 / 255, 42 / 255, 0.14), (14 / 255, 27 / 255, 42 / 255, 0.08)
PHOTON, PHOTON_SOFT = "#E07B1F", "#FBEFE4"          # the soft wash is photon at 12 % over white
SLOTS = ["#2A64AE", "#E07B1F", "#12A08E", "#CFA000", "#C9528E", "#3E8E2E", "#6B5BD2", "#D2473F"]
SEQUENTIAL = ["#93B0D8", "#7399CB", "#5581BB", "#3F6AA4", "#2E5690", "#214479", "#163360"]
SANS, MONO = "IBM Plex Sans", "IBM Plex Mono"
DPI = 200

# The two renders. Sizes are (width, height) in inches at the point of use: the report places a figure at a
# fraction of the 5.5 in line (the fractions in report.tex match these widths); a slide box of w px is
# w / 144 in. FS is the base type size in points, the floor of each medium.
TARGETS = {
    "report": dict(sub="", fs=9.0, compact=True, sweep_modes=("rank",), heads_panels=("low",),
                   success=(5.5, 2.05), bars=(3.2, 2.4), sweep=(5.5, 1.75), eps=(2.5, 2.35), heads=(2.85, 2.35),
                   torsion=(3.2, 2.4), torsion_panels=("all",), demo=(5.5, 1.25), talk=None),
    "slides": dict(sub="slides", fs=10.0, compact=False, sweep_modes=("rank", "filter"), heads_panels=("all", "low"),
                   success=(12.0, 3.6), bars=(6.93, 3.5), sweep=(6.93, 4.2), eps=None, heads=(12.0, 3.2),
                   torsion=(6.93, 3.5), torsion_panels=("all", "low"), demo=None,
                   talk=dict(fs=12.0, objects=(12.0, 3.4), gain=(6.93, 3.5), eps=(6.93, 3.9), heads=(6.93, 3.5))),
}
FS = 9.0          # set per target by set_type()
COMPACT = True    # the report set: short labels, rotated category labels, long names in the caption instead
SHORT = {"skillet_lid": "skillet lid", "padlock": "padlock", "potted_meat_can": "meat can", "plate": "plate",
         "mustard_bottle": "mustard", "bleach_cleanser": "bleach", "cracker_box": "cracker box",
         "sugar_box": "sugar box", "foam_brick": "foam brick", "racquetball": "racquetball"}

# One series-to-colour mapping for every figure, by what the arm does:
#   baseline (constant mu = 0.5 for grasp and force)               slot 1  silicon blue
#   oracle (true mu for grasp and force)                            slot 2  photon amber
#   force only: baseline grasp, force from the estimate             slot 3  oxide teal
#   selection only: grasp from the estimate, baseline force         slot 4  film gold
#   grasp and force at the pessimistic quantile of p(mu)            slot 5  film magenta
#   grasp and force at the posterior mean                           slot 6  green
HEADS = ("dms46", "clip", "mobilenet")
COLOUR = {"baseline": SLOTS[0],
          "oracle": SLOTS[1],
          "squeeze": SLOTS[2], "table_squeeze": SLOTS[2], **{f"head:{h}:squeeze": SLOTS[2] for h in HEADS},
          "select": SLOTS[3],
          "table_q": SLOTS[4], **{f"head:{h}": SLOTS[4] for h in HEADS},
          "table_mean": SLOTS[5], **{f"head:{h}:mean": SLOTS[5] for h in HEADS}}
LOW = {o for o, s in OBJECTS.items() if MATERIAL_TABLE[s.material].nominal <= 0.35}
HIGH = {o for o, s in OBJECTS.items() if MATERIAL_TABLE[s.material].nominal >= 0.5}


def colour(cell):
    """The slot of a cell; head cells not listed in COLOUR (another head name) go by their suffix."""
    if cell in COLOUR:
        return COLOUR[cell]
    if cell.startswith("head:"):
        return SLOTS[2] if cell.endswith(":squeeze") else SLOTS[5] if cell.endswith(":mean") else SLOTS[4]
    raise KeyError(cell)


FONT_DIR = Path(__file__).resolve().parents[1] / "fonts"   # the three IBM Plex faces the figures use (SIL OFL 1.1)


def register_fonts():
    """Register the IBM Plex faces in fonts/ and drop any copy installed on the machine, so the figures need no
    font installed and do not change with the release of Plex a machine happens to have. Then set the
    defaults: mono for everything on the axes (Plex Mono has no Greek, so mu, epsilon and Delta fall back
    glyph by glyph to Plex Sans), ink and muted text, white surfaces, dpi 200."""
    manager = font_manager.fontManager
    manager.ttflist = [f for f in manager.ttflist if f.name not in (SANS, MONO)]
    for path in sorted(FONT_DIR.glob("IBMPlex*.ttf")):
        manager.addfont(str(path))
    plt.rcParams.update({
        "font.family": [MONO, SANS], "font.weight": 400,
        "text.color": INK, "axes.labelcolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": HAIRLINE, "axes.linewidth": 0.8,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "savefig.dpi": DPI,
        "legend.frameon": False,
        "mathtext.fontset": "custom", "mathtext.rm": MONO, "mathtext.it": f"{MONO}:italic", "mathtext.bf": f"{MONO}:bold",
    })


def set_type(fs, compact):
    """Every piece of type on a chart at the floor of its medium: ticks, axis labels, legend, panel labels."""
    global FS, COMPACT
    FS, COMPACT = fs, compact
    plt.rcParams.update({"font.size": fs, "axes.labelsize": fs, "xtick.labelsize": fs, "ytick.labelsize": fs,
                         "legend.fontsize": fs})


register_fonts()


def lab(long, short):
    """An axis or panel label: the long form where there is room, the short one in the report set."""
    return short if COMPACT else long


def legend_kw():
    return dict(prop={"family": SANS, "size": FS}, labelcolor=INK, handlelength=1.0, handleheight=1.0,
                handletextpad=0.5, borderaxespad=0.4)


def style(ax, grid="y"):
    """Design-language axes: no top, right or left spine, a hairline bottom spine, no tick marks, hairline grid."""
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="both", length=0)
    ax.grid(False)
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def headroom(ax, frac):
    """Extend the y range above the data for the panel label, and drop the ticks that would sit in that band.
    Call it after everything is plotted (it fixes the limits, also on axes sharing the y axis)."""
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + frac * (hi - lo))
    ax.set_yticks([t for t in ax.get_yticks() if lo <= t <= hi])


def panel_label(ax, text):
    """Mono uppercase label above the panel's top-left corner, at the floor size, clear of the data."""
    ax.text(0, 1.04, text, transform=ax.transAxes, ha="left", va="bottom", fontsize=FS, color=MUTED)


def reference(ax, y, label="ORACLE", below=False, right=False):
    """A target line: 2 px photon amber with a mono uppercase label at its left end (never in the legend), or at
    its right end when the series crosses the left one. The label goes under the line when the caller says so
    or when the line sits in the top fifth of the axes."""
    lo, hi = ax.get_ylim()
    below = below or (y - lo) / (hi - lo) > 0.8
    ax.axhline(y, color=PHOTON, lw=1.5, zorder=2.5)
    ax.annotate(label, (1 if right else 0, y), xycoords=("axes fraction", "data"),
                xytext=(-4 if right else 4, -2.5 if below else 2.5), textcoords="offset points",
                ha="right" if right else "left", va="top" if below else "bottom", fontsize=FS, color=INK)


def top_legend(fig, axes, handles, labels, ncol, top=0.9):
    """Legend as a row above the panels, left-aligned with the first panel (the design language's chart
    layout), so it never covers data. Lays the figure out first; the caller does not call tight_layout."""
    fig.tight_layout(rect=(0, 0, 1, top))
    x0 = 0.01 if COMPACT and fig.get_figwidth() < 4 else axes[0].get_position().x0   # a narrow figure: from its edge
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(x0, top + 0.005), ncol=ncol,
               columnspacing=1.0 if COMPACT else 1.5, **{**legend_kw(), "borderaxespad": 0})


def gain(rows, mode, metric, cell, subset=None):
    """(mean paired delta of `cell` vs baseline, (lo, hi) 95% bootstrap CI, n trials), optionally over
    the trials of the objects in `subset`."""
    t = table_by_trial(rows, mode, metric)
    base = t["baseline"] if subset is None else {k: v for k, v in t["baseline"].items() if k[0] in subset}
    return paired_diff(t[cell], base)


def errbar(ax, x, d, lo, hi):
    ax.errorbar(x, d, yerr=[[d - lo], [hi - d]], color=INK, capsize=2, lw=1, capthick=1, ls="none", zorder=4)


def bar(ax, x, y, w, **kw):
    """A bar with the design language's white gap to its neighbour."""
    return ax.bar(x, y, w, edgecolor=SURFACE, linewidth=1, **kw)


def per_object_means(rows, mode, metric, cell):
    t = table_by_trial(rows, mode, metric)[cell]
    return {o: np.mean([v for (oo, _), v in t.items() if oo == o]) for o in OBJECTS if any(oo == o for oo, _ in t)}


def fig_2x2(rows, metric, label, out, size):
    """Lift success (or wrench) per object and cell, rank and filter mode. The legend names the cells; the
    caption of the report or the deck spells out what each cell plans with."""
    objs = sorted(OBJECTS, key=lambda o: MATERIAL_TABLE[OBJECTS[o].material].nominal)
    cells = [("baseline", "baseline"), ("squeeze", "squeeze only"), ("select", "selection only"), ("oracle", "oracle")]
    fig, axes = plt.subplots(1, 2, figsize=size, sharey=True)
    w = 0.2
    for ax, mode in zip(axes, ("rank", "filter")):
        for k, (cell, _) in enumerate(cells):
            m = per_object_means(rows, mode, metric, cell)
            bar(ax, np.arange(len(objs)) + (k - 1.5) * w, [m.get(o, 0) for o in objs], w, color=COLOUR[cell])
        ax.set_xticks(range(len(objs)))
        if COMPACT:      # one line per object, in the order of the caption (nominal mu); Table 1 has the rest
            names = [SHORT[o[4:]] for o in objs]
        else:
            names = [f"{o[4:].replace('_', ' ')}\n{OBJECTS[o].material} {MATERIAL_TABLE[OBJECTS[o].material].nominal:.2f}"
                     for o in objs]
        ax.set_xticklabels(names, rotation=60, ha="right", rotation_mode="anchor")
        style(ax)
        panel_label(ax, f"{mode.upper()} MODE")
    headroom(axes[0], 0.04)
    if COMPACT:      # three ticks: at 9 pt the six default ones run into each other on a panel this low
        lo, hi = axes[0].get_ylim()
        ticks = [0.0, 0.5, 1.0] if metric == "success" else MaxNLocator(nbins=3, steps=[1, 2, 5, 10]).tick_values(lo, hi)
        axes[0].set_yticks([t for t in ticks if lo <= t <= hi])
    axes[0].set_ylabel(lab(label, label.split(" [")[0].split(" under")[0] + (" [N]" if "[N]" in label else "")))
    top_legend(fig, axes, [Patch(facecolor=COLOUR[c]) for c, _ in cells], [name for _, name in cells], ncol=4)
    fig.savefig(out); plt.close(fig)


def fig_oracle_objects(rows, out, size):
    """Lift success per object for the baseline and the oracle, rank mode: the first result of the talk. Two of
    the four cells of fig_2x2 and one mode, so it reads in one look. Objects in order of nominal mu with their
    material under them (one label per run of objects of a material), a hairline between the low-mu and the
    high-mu group, and the values on the two metal objects, where the gain is."""
    objs = sorted(OBJECTS, key=lambda o: MATERIAL_TABLE[OBJECTS[o].material].nominal)
    cells = [("baseline", "baseline, μ = 0.5"), ("oracle", "oracle, true μ*")]
    means = {cell: per_object_means(rows, "rank", "success", cell) for cell, _ in cells}
    fig, ax = plt.subplots(figsize=size)
    w = 0.36
    for i, o in enumerate(objs):
        for k, (cell, _) in enumerate(cells):
            x, y = i + (k - 0.5) * w, means[cell].get(o, 0)
            bar(ax, x, y, w, color=COLOUR[cell])
            if OBJECTS[o].material == "metal":
                ax.annotate(f"{y:.2f}", (x, y), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                            fontsize=FS, color=INK)
        if max(means[cell].get(o, 0) for cell, _ in cells) == 0:      # no bar to see: say so
            ax.annotate("0.00", (i, 0), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                        fontsize=FS, color=INK)
    ax.set_xticks(range(len(objs)))
    # names in Plex Sans (eleven mono characters are wider than a slot); the second line is the material row
    ax.set_xticklabels([SHORT[o[4:]] + "\n" for o in objs], family=SANS, color=INK2)
    mats = [OBJECTS[o].material for o in objs]
    for m in dict.fromkeys(mats):
        idx = [i for i, mm in enumerate(mats) if mm == m]
        ax.annotate(f"{m} {MATERIAL_TABLE[m].nominal:.2f}", (np.mean(idx), 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -(3.5 + 1.3 * FS)), textcoords="offset points", ha="center", va="top", fontsize=FS,
                    color=MUTED)
    ax.set_xlim(-0.6, len(objs) - 0.4)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("lift success")
    style(ax)
    headroom(ax, 0.2)
    n_low = sum(o in LOW for o in objs)
    ax.axvline(n_low - 0.5, color=HAIRLINE, lw=0.8, zorder=1)
    for x0, name, subset in ((-0.5, "LOW-μ OBJECTS", LOW), (n_low - 0.5, "HIGH-μ OBJECTS", HIGH)):
        n = gain(rows, "rank", "success", "oracle", subset)[2]
        ax.text(x0 + 0.08, 1.19, f"{name} · N = {n}", ha="left", va="top", fontsize=FS, color=MUTED)
    top_legend(fig, [ax], [Patch(facecolor=COLOUR[c]) for c, _ in cells], [name for _, name in cells], ncol=2)
    fig.savefig(out); plt.close(fig)


def fig_heads_force(rows, out, size):
    """Paired gain in lift success over the baseline (rank mode, all objects) for the perfect classifier and the
    three real heads at quantile 0.1 of p(mu): force only (the baseline's grasp) beside grasp and force. The
    oracle's gain is the reference line. The talk's version of fig_heads: one panel, two arms per head."""
    groups = [("perfect\nclassifier", "table_squeeze", "table_q")]
    groups += [(name, f"head:{h}:squeeze", f"head:{h}") for h, name in (("dms46", "DMS46"), ("clip", "CLIP"),
                                                                       ("mobilenet", "MobileNet"))]
    fig, ax = plt.subplots(figsize=size)
    w = 0.36
    for g, (_, force, full) in enumerate(groups):
        for k, cell in enumerate((force, full)):
            d, (lo, hi), _ = gain(rows, "rank", "success", cell)
            bar(ax, g + (k - 0.5) * w, d, w, color=colour(cell))
            errbar(ax, g + (k - 0.5) * w, d, lo, hi)
    ax.axhline(0, color=INK, lw=0.6, zorder=1)
    ax.set_xticks(range(len(groups))); ax.set_xticklabels([name for name, _, _ in groups])
    ax.set_xlim(-1.25, len(groups) - 0.5)      # room for the ORACLE label left of the first bar
    ax.set_ylabel("Δ lift success vs baseline")
    style(ax)
    headroom(ax, 0.1)
    reference(ax, gain(rows, "rank", "success", "oracle")[0])
    top_legend(fig, [ax], [Patch(facecolor=SLOTS[2]), Patch(facecolor=SLOTS[4])],
               ["force only", "grasp + force"], ncol=2, top=0.92)
    fig.savefig(out); plt.close(fig)


def fig_sweep(rows, out, size, modes):
    """Mean outcome of a planner that assumes one constant mu for every object, against the oracle. One
    row per mode: lift success on the left, wrench at slip on the right."""
    sweep = sorted({r["cell"] for r in rows if r["cell"].startswith("sweep:")}, key=lambda c: float(c.split(":")[1]))
    if not sweep:
        return
    metrics = (("success", "lift success", "LIFT SUCCESS"), ("wrench", lab("wrench at slip [N]", "slip wrench [N]"), "WRENCH AT SLIP"))
    fig, axes = plt.subplots(len(modes), 2, figsize=size, sharex=True, sharey="col", squeeze=False)
    panels = []
    for i, mode in enumerate(modes):          # plot every panel first: the columns share their y range
        for j, (metric, label, short) in enumerate(metrics):
            ax = axes[i, j]
            xs, ys = [], []
            for c in sweep + ["baseline"]:
                t = table_by_trial(rows, mode, metric)[c]
                xs.append(0.5 if c == "baseline" else float(c.split(":")[1])); ys.append(np.mean(list(t.values())))
            o = np.argsort(xs)
            xs, ys = np.array(xs)[o], np.array(ys)[o]
            ax.plot(xs, ys, "-o", color=COLOUR["baseline"], lw=1.3, ms=3.2, zorder=3)
            oracle = np.mean(list(table_by_trial(rows, mode, metric)["oracle"].values()))
            name = short if len(modes) == 1 else f"{mode.upper()} · {short}"
            panels.append((ax, xs, ys, oracle, name, label, i == len(modes) - 1))
    for ax, xs, ys, oracle, name, label, bottom in panels:
        style(ax)
        headroom(ax, 0.14)
        if COMPACT:      # the report's one row: the oracle line clear of the panel's top edge, and its label at
            lo, hi = ax.get_ylim()      # the right end, where the series has fallen away from it
            if oracle > hi - 0.1 * (hi - lo):
                ax.set_ylim(lo, oracle + 0.1 * (hi - lo))
        reference(ax, oracle, below=ys[0] > oracle, right=COMPACT)
        # the one series, labelled once beside its first point, on the side away from the line
        rising = ys[1] > ys[0]
        ax.annotate("CONSTANT μ", (xs[0], ys[0]), xytext=(5, -4 if rising else 4), textcoords="offset points",
                    ha="left", va="top" if rising else "bottom", fontsize=FS, color=INK)
        panel_label(ax, name)
        ax.set_ylabel(label)
        ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
        if bottom:
            ax.set_xlabel("assumed μ, all objects")
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def fig_eps_vs_wrench(rows, out, size):
    seen, pts = set(), []
    for r in rows:
        if r.get("executed") and r.get("success") and np.isfinite(r.get("min_wrench", np.nan)):
            key = (r["obj"], r["trial"], r["chosen"], r["force"])
            if key not in seen:
                seen.add(key); pts.append((r["eps_true"] * 2 * r["force"], r["min_wrench"], r["material"]))
    if not pts:
        return
    if COMPACT:
        fig, ax = pair_axes(size, left=0.5)
    else:
        fig, ax = plt.subplots(figsize=size)
    mats = sorted({p[2] for p in pts}, key=lambda m: MATERIAL_TABLE[m].nominal)
    # the sequential ramp, lightest for the lowest nominal mu; steps dropped evenly when fewer materials are present
    steps = np.round(np.linspace(0, len(SEQUENTIAL) - 1, min(len(mats), len(SEQUENTIAL)))).astype(int)
    handles = []
    ms = 8 if size[0] > 4 else 5
    for m, k in zip(mats, steps):
        xs = [p[0] for p in pts if p[2] == m]; ys = [p[1] for p in pts if p[2] == m]
        ax.scatter(xs, ys, s=ms, alpha=0.7, color=SEQUENTIAL[k], linewidths=0)
        handles.append(Line2D([], [], ls="none", marker="o", ms=4.5, color=SEQUENTIAL[k],
                              label=f"{m} ({MATERIAL_TABLE[m].nominal:.2f})"))
    ax.set_xlabel(lab("ε(μ*) × 2F, analytical worst-case capacity [N]", "ε(μ*) × 2F [N]"))
    ax.set_ylabel(lab("measured wrench at slip [N]", "wrench at slip [N]"))
    style(ax, grid="both")
    if COMPACT:      # no empty corner at this size, and a legend beside the axes leaves them a strip: the
        # materials stand above the plot in two rows, read across in order of nominal mu (the caption says
        # that the darker point is the higher mu), and the axes keep the width of the figure
        ax.set_ylim(bottom=0)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4, steps=[1, 2, 5, 10]))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=3, steps=[1, 2, 5, 10]))
        cols = 3
        rows_n = -(-len(handles) // cols)
        order = [r + c * rows_n for r in range(rows_n) for c in range(cols) if r + c * rows_n < len(handles)]
        across = sorted(range(len(handles)), key=lambda i: order[i])        # matplotlib fills a legend by column
        fig.legend([handles[i] for i in across], [mats[i] for i in across], loc="upper left",
                   bbox_to_anchor=(0.01, 1 - 0.04 / size[1]), ncol=cols, labelspacing=0.3, columnspacing=1.0,
                   **{**legend_kw(), "borderaxespad": 0})
        fig.savefig(out); plt.close(fig)
        return
    ax.legend(handles=handles, loc="upper left", labelspacing=0.3, **legend_kw())
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def fig_2x2_bars(rows, out, size):
    """Paired gain in lift success over the baseline for the three other 2x2 cells (rank mode), pooled
    and by friction group, with 95% bootstrap CIs."""
    groups = [("all", None), ("low-μ", LOW), ("high-μ", HIGH)]
    cells = [("squeeze", "squeeze only"), ("select", "selection only"), ("oracle", "oracle")]
    fig, ax = plt.subplots(figsize=size)
    w, labels = 0.26, []
    for g, (name, subset) in enumerate(groups):
        n = 0
        for k, (cell, label) in enumerate(cells):
            d, (lo, hi), n = gain(rows, "rank", "success", cell, subset)
            bar(ax, g + (k - 1) * w, d, w, color=COLOUR[cell], label=label if g == 0 else None)
            errbar(ax, g + (k - 1) * w, d, lo, hi)
        labels.append(f"{name}\nn = {n}")
    ax.axhline(0, color=INK, lw=0.6, zorder=1)
    ax.set_xticks(range(len(groups))); ax.set_xticklabels(labels)
    ax.set_ylabel(lab("Δ lift success vs baseline", "Δ lift success"))
    style(ax)
    top_legend(fig, [ax], [Patch(facecolor=COLOUR[c]) for c, _ in cells], [name for _, name in cells],
               ncol=2 if COMPACT else 3, top=0.82 if COMPACT else 0.92)
    fig.savefig(out); plt.close(fig)


# The report sets two charts side by side as one figure (report.tex: fig_heads at 0.518 of the line, the scatter
# at 0.455). Both keep the same bands above and below the plot area, in inches, so the two plot areas share a
# top and a baseline on the page: the band above holds the legend (and a panel label), the one below the ticks
# and the axis label.
PAIR_TOP, PAIR_BOTTOM = 0.45, 0.47


def pair_axes(size, left, right=0.1):
    """A figure of `size` inches with one axes placed by hand: `left` inches for the y labels."""
    w, h = size
    fig = plt.figure(figsize=size)
    return fig, fig.add_axes((left / w, PAIR_BOTTOM / h, (w - left - right) / w, (h - PAIR_TOP - PAIR_BOTTOM) / h))


def head_groups(rows):
    """(source name, its cells present in the run): the oracle, the perfect classifier, the three heads; in a
    group the arm at the mean of p(mu), at quantile q, and force only."""
    present = {r["cell"] for r in rows}
    groups = [("oracle", ["oracle"]), ("perfect\nclassifier", ["table_mean", "table_q", "table_squeeze"])]
    for h, name in (("dms46", "DMS46"), ("clip", "CLIP"), ("mobilenet", "MobileNet")):
        groups.append((name, [f"head:{h}:mean", f"head:{h}", f"head:{h}:squeeze"]))
    groups = [(name, [c for c in cells if c in present]) for name, cells in groups]
    return [g for g in groups if g[1]]


HEAD_SUBSETS = {"all": ("ALL", None), "low": ("LOW-μ", LOW)}


def fig_heads_rows(rows, out, size, panel):
    """The report's fig_heads: one panel, the arms as horizontal bars. Five source names do not fit under
    grouped bars at 9 pt on half a line (set slanted they took more room than the bars), so they stand level at
    the left of their rows. Rows from the top: the oracle, the perfect classifier, the three heads; in a row the
    arm at the mean, at quantile q, and force only, in the order of the legend. The oracle's gain is its own
    amber bar and the line through the other rows (the caption says so)."""
    groups = head_groups(rows)
    if not groups:
        return
    title, subset = HEAD_SUBSETS[panel]
    fig, ax = pair_axes(size, left=0.86)
    y, ticks, n_or, d_or, x_lo, x_hi = 0.0, [], 0, None, 0.0, 0.0
    for name, cells in groups:
        ys = [y - k for k in range(len(cells))]
        for cell, yi in zip(cells, ys):
            d, (lo, hi), n = gain(rows, "rank", "success", cell, subset)
            ax.barh(yi, d, 0.78, color=colour(cell), edgecolor=SURFACE, linewidth=1)
            ax.errorbar(d, yi, xerr=[[d - lo], [hi - d]], color=INK, capsize=2, lw=1, capthick=1, ls="none", zorder=4)
            x_lo, x_hi = min(x_lo, lo), max(x_hi, hi)
            if cell == "oracle":
                n_or, d_or = n, d
        ticks.append((np.mean(ys), name))
        last = ys[-1]
        # rows 1 apart, groups 0.7 further apart; 1.5 under a one-row group, whose label would otherwise run
        # into the two-line label of the group below it
        y = last - (2.5 if len(cells) == 1 else 1.7)
    ax.axvline(0, color=INK, lw=0.6, zorder=1)
    if d_or is not None:
        ax.axvline(d_or, color=PHOTON, lw=1.5, zorder=2.5)
    ax.set_yticks([t for t, _ in ticks]); ax.set_yticklabels([name for _, name in ticks])
    ax.set_ylim(last - 0.65, 0.65)
    pad = 0.04 * (x_hi - x_lo)
    ax.set_xlim(x_lo - (pad if x_lo < 0 else 0), x_hi + pad)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=3, steps=[1, 2, 5, 10]))
    ax.set_xlabel("Δ lift success")
    style(ax, grid="x")
    panel_label(ax, f"{title} · N = {n_or}")
    fig.legend([Patch(facecolor=SLOTS[5]), Patch(facecolor=SLOTS[4]), Patch(facecolor=SLOTS[2])],
               ["mean", "q = 0.1", "force only"], loc="upper left", bbox_to_anchor=(0.01, 1 - 0.04 / size[1]),
               ncol=3, columnspacing=1.0, **{**legend_kw(), "borderaxespad": 0})
    fig.savefig(out); plt.close(fig)


def fig_heads(rows, out, size, panels=("all", "low")):
    """Paired gain in lift success over the baseline (rank mode) for the oracle, the perfect-classifier
    table arms and each real head at the mean of its p(mu), at quantile q, and force-only (baseline grasp,
    force from the quantile), pooled and on low-mu objects. Bars are grouped by source and coloured by what
    the arm does (the legend); the oracle's gain is the reference line. The decks' version; the report set
    draws one panel as rows (fig_heads_rows)."""
    if COMPACT:
        return fig_heads_rows(rows, out, size, panels[0])
    groups = head_groups(rows)
    if not groups:
        return
    xs, ticks, x = [], [], 0.0            # bars 1 apart, groups 0.7 further apart
    for name, cells in groups:
        xs.append([x + k for k in range(len(cells))]); ticks.append(x + (len(cells) - 1) / 2)
        x += len(cells) + 0.7
    fig, axes = plt.subplots(1, len(panels), figsize=size, squeeze=False)
    axes = axes[0]
    subsets = {"all": ("ALL OBJECTS", None), "low": ("LOW-μ OBJECTS", LOW)}
    for ax, (title, subset) in zip(axes, (subsets[p] for p in panels)):
        n_or, d_or = 0, None
        for (name, cells), gx in zip(groups, xs):
            for cell, xi in zip(cells, gx):
                d, (lo, hi), n = gain(rows, "rank", "success", cell, subset)
                bar(ax, xi, d, 0.78, color=colour(cell))
                errbar(ax, xi, d, lo, hi)
                if cell == "oracle":
                    n_or, d_or = n, d
        ax.axhline(0, color=INK, lw=0.6, zorder=1)
        ax.set_xticks(ticks)
        ax.set_xticklabels([name for name, _ in groups])
        ax.set_xlim(-2.4, x - 0.7 - 0.5 + 0.4)   # room for the ORACLE label left of its bar
        style(ax)
        headroom(ax, 0.1)
        if d_or is not None:
            reference(ax, d_or)
        panel_label(ax, f"{title} · N = {n_or} PAIRED TRIALS")
    axes[0].set_ylabel("Δ lift success vs constant μ = 0.5")
    top_legend(fig, axes, [Patch(facecolor=SLOTS[2]), Patch(facecolor=SLOTS[4]), Patch(facecolor=SLOTS[5])],
               ["force only", "grasp + force at q = 0.1", "grasp + force at the mean"], ncol=3, top=0.9)
    fig.savefig(out); plt.close(fig)


# The demo trial: scripts/record_clips.py replays one trial of the core run as four looping clips, one per
# 2x2 cell, into results/clips (the demo slide of the final deck plays them). The report gets one still per
# cell, taken at the same moment of the lift, with the cell's force and outcome read from rows.jsonl.
CLIPS = RESULTS / "clips"
DEMO_OBJ, DEMO_TRIAL, DEMO_MODE = "038_padlock", 118, "rank"
DEMO_T_MS = 900                                # 0.3 s into the lift: a dropped object has left the fingers
DEMO_CROP = (156, 55, 644, 380)                # the gripper's part of the 800 x 450 frame, 3:2, above the label band
DEMO_CELLS = [("baseline", "BASELINE"), ("squeeze", "SQUEEZE ONLY"), ("select", "SELECTION ONLY"), ("oracle", "ORACLE")]


def gif_frame(path, t_ms):
    """The frame of an animated GIF showing at t_ms (frames carry their own durations)."""
    im = Image.open(path)
    acc = 0
    for k in range(im.n_frames):
        im.seek(k)
        d = im.info.get("duration", 50)
        if acc + d > t_ms:
            return im.convert("RGB")
        acc += d
    return im.convert("RGB")


def fig_demo(rows, out, size):
    """One still per 2x2 cell of the demo trial, cropped to the gripper, with a mono label under each: the cell,
    then its per-finger force and outcome from rows.jsonl. Skipped when the clips are not there."""
    paths = {cell: CLIPS / f"{DEMO_OBJ}_t{DEMO_TRIAL}_{cell}.gif" for cell, _ in DEMO_CELLS}
    if not all(p.exists() for p in paths.values()):
        print("no demo clips in", CLIPS, "- fig_demo skipped")
        return
    row = {r["cell"]: r for r in rows if r["obj"] == DEMO_OBJ and r["trial"] == DEMO_TRIAL and r["mode"] == DEMO_MODE}
    w_in, h_in = size
    gap = 0.06                                  # inches between panels; two lines of type go under each
    pw = (w_in - gap * (len(DEMO_CELLS) - 1)) / len(DEMO_CELLS)
    ph = pw * (DEMO_CROP[3] - DEMO_CROP[1]) / (DEMO_CROP[2] - DEMO_CROP[0])
    fig = plt.figure(figsize=size)
    for k, (cell, name) in enumerate(DEMO_CELLS):
        x0 = k * (pw + gap) / w_in
        ax = fig.add_axes((x0, 1 - ph / h_in, pw / w_in, ph / h_in))
        ax.imshow(np.asarray(gif_frame(paths[cell], DEMO_T_MS).crop(DEMO_CROP)), interpolation="lanczos")
        ax.axis("off")
        r = row[cell]
        fig.text(x0, 1 - (ph + 0.04) / h_in, name, ha="left", va="top", fontsize=FS, color=MUTED)
        fig.text(x0, 1 - (ph + 0.04 + FS * 1.2 / 72) / h_in, f"{r['force']:.1f}N · {'HELD' if r['success'] else 'DROPPED'}",
                 ha="left", va="top", fontsize=FS, color=INK)
    fig.savefig(out); plt.close(fig)


def fig_torsion(scaled, out, size, panels=("all", "low")):
    """Paired gain in lift success over the baseline (rank mode) for squeeze-only, selection-only and the
    oracle at each planner torsional scale, pooled and on low-mu objects, with 95% bootstrap CIs. scaled:
    [(scale, rows), ...] on the same trials in every run (the first 40 per object)."""
    cells = [("squeeze", "squeeze only"), ("select", "selection only"), ("oracle", "oracle")]
    subsets = {"all": (lab("ALL OBJECTS", "ALL"), None), "low": (lab("LOW-μ OBJECTS", "LOW-μ"), LOW)}
    ticks = {1.0: "1.0x\n(the model)", 3.2: "3.2x\n(flat-face fit)"}
    fig, axes = plt.subplots(1, len(panels), figsize=size, squeeze=False)
    axes = axes[0]
    w = 0.26
    for ax, (title, subset) in zip(axes, (subsets[p] for p in panels)):
        n = 0
        for g, (scale, rows) in enumerate(scaled):
            for k, (cell, _) in enumerate(cells):
                d, (lo, hi), n = gain(rows, "rank", "success", cell, subset)
                bar(ax, g + (k - 1) * w, d, w, color=COLOUR[cell])
                errbar(ax, g + (k - 1) * w, d, lo, hi)
        ax.axhline(0, color=INK, lw=0.6, zorder=1)
        ax.set_xticks(range(len(scaled)))
        ax.set_xticklabels([ticks.get(sc, f"{sc:.1f}x") if not COMPACT else f"{sc:.1f}x" for sc, _ in scaled])
        ax.set_xlabel(lab("planner torsional scale", "torsional scale"))
        style(ax)
        headroom(ax, 0.1)
        panel_label(ax, f"{title} · N = {n}")
    axes[0].set_ylabel(lab("Δ lift success vs baseline", "Δ lift success"))
    top_legend(fig, axes, [Patch(facecolor=COLOUR[c]) for c, _ in cells], [name for _, name in cells],
               ncol=2 if COMPACT else 3, top=0.82 if COMPACT else 0.9)
    fig.savefig(out); plt.close(fig)


def torsion_runs(rows):
    """The core run and the torsion runs that exist, each cut to the first 40 trials per object, by scale."""
    scaled = [(1.0, [r for r in rows if r["trial"] < 40])]
    for run in ("torsion_k2.0", "torsion_k3.2"):
        path = RESULTS / "sim" / run / "rows.jsonl"
        if path.exists():
            cfg = json.loads((path.parent / "config.json").read_text())
            scaled.append((float(cfg.get("gamma_scale", 1.0)), [r for r in load_rows(path) if r["trial"] < 40]))
    return scaled


def main(runs):
    rows = load_rows(RESULTS / "sim" / runs[0] / "rows.jsonl")
    heads = load_rows(RESULTS / "sim" / runs[1] / "rows.jsonl") if len(runs) > 1 else None
    torsion = torsion_runs(rows)
    for name, t in TARGETS.items():
        out = RESULTS / "figures" / t["sub"]
        out.mkdir(parents=True, exist_ok=True)
        set_type(t["fs"], t["compact"])
        fig_2x2(rows, "success", "lift success under force cap", out / "fig_2x2_success.png", t["success"])
        fig_2x2(rows, "wrench", "wrench at slip [N] (0 = failed)", out / "fig_2x2_wrench.png", t["success"])
        fig_sweep(rows, out / "fig_sweep.png", t["sweep"], t["sweep_modes"])
        if t["eps"] is not None:
            fig_eps_vs_wrench(rows, out / "fig_eps_vs_wrench.png", t["eps"])
        fig_2x2_bars(rows, out / "fig_2x2_bars.png", t["bars"])
        if heads is not None:
            fig_heads(heads, out / "fig_heads.png", t["heads"], t["heads_panels"])
        if len(torsion) > 1:
            fig_torsion(torsion, out / "fig_torsion.png", t["torsion"], t["torsion_panels"])
        if t["demo"] is not None:
            fig_demo(rows, out / "fig_demo.png", t["demo"])
        talk = t["talk"]
        if talk is not None:          # the final presentation's charts, one per result slide, at a larger type
            set_type(talk["fs"], t["compact"])
            fig_oracle_objects(rows, out / "fig_oracle_objects.png", talk["objects"])
            fig_2x2_bars(rows, out / "fig_2x2_gain.png", talk["gain"])
            fig_eps_vs_wrench(rows, out / "fig_eps_vs_wrench.png", talk["eps"])
            if heads is not None:
                fig_heads_force(heads, out / "fig_heads_force.png", talk["heads"])
        print(f"{name} figures written to", out)


if __name__ == "__main__":
    main(sys.argv[1:] or ["core"])
