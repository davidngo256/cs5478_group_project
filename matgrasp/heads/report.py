"""Compose results/heads/README.md from the three <head>_summary.json / <head>_ycb.json files."""
from __future__ import annotations

import json
from pathlib import Path

from ..ycb import OBJECTS
from . import common

HEADS = ("dms46", "clip", "mobilenet")


def load(head: str) -> tuple[dict | None, dict | None]:
    s, y = common.RESULTS_DIR / f"{head}_summary.json", common.RESULTS_DIR / f"{head}_ycb.json"
    return (json.loads(s.read_text()) if s.exists() else None, json.loads(y.read_text()) if y.exists() else None)


def fmt(x, nd=3, pct=False):
    if x is None:
        return "n/a"
    return f"{100 * x:.1f}%" if pct else f"{x:.{nd}f}"


def machine_of(summaries: dict[str, dict | None]) -> dict | None:
    """The `machine` record of the first summary that has one (all heads run on the same box)."""
    return next((s["machine"] for s in summaries.values() if s and s.get("machine")), None)


def machine_line(summaries: dict[str, dict | None]) -> str:
    m = machine_of(summaries)
    if not m:
        return "The summaries do not record the machine they were measured on."
    gpu = m["device_name"] if str(m.get("device", "")).startswith("cuda") else "no GPU used"
    return f"All numbers below were measured on this machine ({m['cpu_count']} CPUs, {gpu}, torch {m['torch']})."


def head_table(summaries: dict[str, dict | None]) -> list[str]:
    devs = {str((s.get("latency_ms_per_image") or {}).get("device", "cpu")) for s in summaries.values() if s}
    where = "per head, see notes" if len(devs) != 1 else ("GPU" if next(iter(devs)).startswith("cuda") else "CPU")
    rows = [f"| head | params | latency ms/img (bs=1, {where}; see notes) | YCB image-level top-1 | YCB object-level top-1 | MINC test acc (10 cls) | ECE (MINC test) before -> after T |",
            "|---|---|---|---|---|---|---|"]
    for h in HEADS:
        s = summaries[h]
        if s is None:
            rows.append(f"| {h} | not built | | | | | |")
            continue
        lat = s.get("latency_ms_per_image", {})
        ece = f"{fmt(s['ece_before'])} -> {fmt(s['ece_after'])} (T={s['temperature']:.2f})" if "ece_after" in s else "n/a (no held-out set)"
        rows.append(f"| {h} | {s['params'] / 1e6:.2f}M | {lat.get('mean', float('nan')):.0f} +/- {lat.get('std', float('nan')):.0f} "
                    f"| {fmt(s['ycb']['image_level'], pct=True)} ({s['ycb']['n_images']} imgs) | {fmt(s['ycb']['object_level'], pct=True)} "
                    f"({s['ycb']['n_objects']} obj) | {fmt(s.get('minc_test_accuracy'), pct=True) if s.get('minc_test_accuracy') is not None else 'n/a'} | {ece} |")
    return rows


def per_object_table(summaries: dict[str, dict | None], ycb: dict[str, dict | None]) -> list[str]:
    rows = ["| object | true | " + " | ".join(f"{h}: majority top-1 (views correct) / mean-posterior top-1 (p)" for h in HEADS) + " |",
            "|---|---|" + "---|" * len(HEADS)]
    for oid, o in OBJECTS.items():
        cells = []
        for h in HEADS:
            s, y = summaries[h], ycb[h]
            if not s or not y or oid not in y:
                cells.append("n/a")
                continue
            po = s["ycb"]["per_object"][oid]
            r = y[oid]
            mt = common.top1(r["mean_probs"])
            mark = "ok" if po["pred"] == o.material else "X"
            cells.append(f"**{po['pred']}** {mark} ({po['votes'].get(o.material, 0)}/{po['n_images']}) / {mt} ({r['mean_probs'][mt]:.2f})")
        sources = [ycb[h][oid].get("source", "photo") for h in HEADS if ycb[h] and oid in ycb[h]]
        label = f"{oid} (renders, excluded)" if sources and sources[0] == "render" else oid
        rows.append(f"| {label} | {o.material} | " + " | ".join(cells) + " |")
    return rows


def confusion_table(cm: dict[str, dict[str, int]]) -> list[str]:
    classes = list(cm)
    rows = ["| true \\ pred | " + " | ".join(classes) + " |", "|---|" + "---|" * len(classes)]
    for t in classes:
        rows.append(f"| {t} | " + " | ".join(str(cm[t][p]) for p in classes) + " |")
    return rows


def build(notes: str = "") -> str:
    summaries = {h: load(h)[0] for h in HEADS}
    ycb = {h: load(h)[1] for h in HEADS}
    L = ["# Material heads on real YCB photographs", "",
         "Three material classifiers producing a posterior over the `friction.MATERIAL_TABLE` classes "
         "(glass, metal, ceramic, plastic, painted, wood, paper, leather, fabric, foam, rubber) for the ten "
         "YCB objects in `matgrasp.ycb.OBJECTS`, evaluated on 24 real views per object "
         "(cameras NP1-3, turntable angles 0..315 step 45) from the YCB Berkeley RGB-D archives. "
         "028_skillet_lid has no photographs on the YCB server; it is evaluated on 24 renders of its "
         "textured scan and excluded from the accuracy numbers (see caveats). " + machine_line(summaries), "",
         "## Summary", ""] + head_table(summaries) + ["",
         "Latency = wall-clock per image, batch size 1, `torch.no_grad`, after 5 warm-up calls, mean +/- std over "
         "20 YCB views; it includes cropping, resizing/normalisation and the network forward.", "",
         "## Per-object top-1 predictions", "",
         "Majority vote of the per-view top-1 over the 24 views (ties broken by the mean posterior); in "
         "brackets the number of views whose top-1 is the true class. Second entry: top-1 of the mean posterior "
         "over views with its probability.", ""] + per_object_table(summaries, ycb)
    m = summaries.get("mobilenet")
    if m and m.get("confusion_matrix_table"):
        L += ["", "## MobileNetV3-Small on MINC-2500 (test split, table-class vocabulary, after temperature scaling)", ""]
        L += confusion_table(m["confusion_matrix_table"])
        tr = m.get("minc_training") or {}
        L += ["", f"Test accuracy over the 10 MINC classes: {fmt(m.get('minc_test_accuracy'), pct=True)} "
              f"({fmt(m.get('minc_test_accuracy_table_classes'), pct=True)} after collapsing polishedstone -> ceramic). "
              f"ECE (15 bins) on the test split {fmt(m.get('ece_before'))} -> {fmt(m.get('ece_after'))} with T = {m.get('temperature', float('nan')):.3f} "
              f"fitted on the validation split (validation ECE {fmt(m.get('ece_validation_before'))} -> {fmt(m.get('ece_validation_after'))}). "
              f"Training: {tr.get('train_images')} images ({tr.get('epochs')} epochs, batch {tr.get('batch')}, AdamW lr {tr.get('lr')}), "
              f"{(tr.get('train_time_s') or 0) / 60:.0f} min on {tr.get('device_name') or 'CPU'}; log in `mobilenet_train.log`."]
        pc = m.get("minc_test_per_class_accuracy") or {}
        if pc:
            L += ["", "Per-class MINC test accuracy: " + ", ".join(f"{k} {fmt(v, pct=True)}" for k, v in pc.items()) + "."]
    if notes:
        L += ["", notes]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    import sys

    notes_path = Path(sys.argv[1]) if len(sys.argv) > 1 else common.RESULTS_DIR / "notes.md"
    notes = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
    out = common.RESULTS_DIR / "README.md"
    out.write_text(build(notes), encoding="utf-8")
    print(f"wrote {out}")
