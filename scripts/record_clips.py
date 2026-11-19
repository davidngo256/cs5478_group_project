"""Record the four 2x2 cells of one trial of the core run as looping GIF clips for the final deck.
Usage: python scripts/record_clips.py [--obj 038_padlock --trial 118 --run core120 --mode rank]
  -> results/clips/<obj>_t<trial>_<cell>.gif for baseline, squeeze, select and oracle, each the close,
     the 20cm lift and the 2s hold at 20 fps with the cell's grasp and force burned in at the top and the
     outcome (held or dropped) on a final 1.5s frame; and, with --sheet DIR, a contact sheet to look at.
The trial is replayed exactly as scripts/run_study.py ran it (Runner.prepare, then planner.decide per cell),
and the script stops if a cell's chosen candidate, force or outcome differs from results/sim/<run>/rows.jsonl,
so the clips show the trial the tables count. The object carries its textured scan (GraspSim(visual=True),
which changes nothing in the dynamics) and the gripper is drawn in ink. Animated GIFs because PowerPoint and
LibreOffice both play them in a slideshow without codecs, timing nodes or clicks; the PDF shows the first frame.
Needs the YCB data under data/ (see README.md), so it is not part of build_reports.sh."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import math
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pybullet as p
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from matgrasp.experiment import RESULTS, Config, Runner, cells_for   # noqa: E402
from matgrasp.planner import decide, gravity_wrench                   # noqa: E402
from matgrasp.sim import DT, GraspSim                                 # noqa: E402

FPS = 20
WIDTH, HEIGHT = 800, 450
HOLD_MS = 1500                                     # the last frame, with the outcome, before the loop restarts
FOV, DIST, ELEVATION = 40.0, 0.32, 24.0            # camera: vertical field of view [deg], distance [m], above horizontal
LABEL_PX, OUTCOME_PX = 34, 44                      # 20 px and 26 px once the 800 px frame sits 487 px wide on the slide
INK = (14, 27, 42)
FONTS = ROOT / "fonts"                               # the IBM Plex faces shipped with the repo
CELLS = {"baseline": "grasp μ = 0.5 · force μ = 0.5", "squeeze": "grasp μ = 0.5 · force μ*",
         "select": "grasp μ* · force μ = 0.5", "oracle": "grasp μ* · force μ*"}
_GREEK = re.compile(r"[Ͱ-Ͽ]+")


class RecordingSim(GraspSim):
    """GraspSim that grabs a frame every 1/FPS of simulated time while `recording` is set. The camera rides
    with the gripper (the object is 6 to 20cm, the lift 20cm: a fixed frame that holds both makes the object a
    speck), so a held object stays put in the frame and a dropped one falls out of it."""

    def __init__(self, obj_id: str):
        super().__init__(obj_id, visual=True)
        self.recording = False
        self.frames: list[np.ndarray] = []
        self._n = 0
        self._every = round(1.0 / (FPS * DT))
        self.azimuth = 0.0
        self.proj = p.computeProjectionMatrixFOV(fov=FOV, aspect=WIDTH / HEIGHT, nearVal=0.05, farVal=30.0)
        tex = Path(tempfile.gettempdir()) / "matgrasp_table.png"
        Image.new("RGB", (4, 4), (235, 233, 228)).save(tex)       # a plain table instead of the checker
        p.changeVisualShape(self.plane, -1, textureUniqueId=p.loadTexture(str(tex), physicsClientId=self.cid),
                            rgbaColor=[1, 1, 1, 1], physicsClientId=self.cid)

    def frame(self) -> np.ndarray:
        gp = np.array(p.getBasePositionAndOrientation(self.gripper, physicsClientId=self.cid)[0])
        target = gp + np.array([0.0, 0.0, -0.05])
        a, e = math.radians(self.azimuth), math.radians(ELEVATION)
        eye = target + DIST * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        view = p.computeViewMatrix(eye.tolist(), target.tolist(), [0, 0, 1])
        _, _, rgba, _, _ = p.getCameraImage(WIDTH, HEIGHT, view, self.proj, renderer=p.ER_TINY_RENDERER,
                                            lightDirection=[0.4, -0.6, 1.5], shadow=1, physicsClientId=self.cid)
        return np.asarray(rgba, np.uint8).reshape(HEIGHT, WIDTH, 4)[..., :3].copy()

    def _step(self, n: int):
        for _ in range(n):
            p.stepSimulation(physicsClientId=self.cid)
            if self.recording:
                self._n += 1
                if self._n % self._every == 0:
                    self.frames.append(self.frame())

    def start(self):
        self.frames, self._n, self.recording = [], 0, True

    def stop(self) -> list[np.ndarray]:
        self.recording = False
        return self.frames


def draw_label(dr: ImageDraw.ImageDraw, xy, s: str, mono: ImageFont.FreeTypeFont, sans: ImageFont.FreeTypeFont):
    """An uppercase mono label; Greek letters in Plex Sans, since Plex Mono has none (deck_style.mono_runs)."""
    x, y = xy
    pos = 0
    pieces = []
    for m in _GREEK.finditer(s):
        if m.start() > pos:
            pieces.append((s[pos:m.start()].upper(), mono))
        pieces.append((m.group(), sans))
        pos = m.end()
    if pos < len(s):
        pieces.append((s[pos:].upper(), mono))
    for seg, font in pieces:
        dr.text((x, y), seg, font=font, fill=INK)
        x += dr.textlength(seg, font=font)


def write_gif(frames: list[np.ndarray], path: Path, cell_label: str, outcome: str):
    """Frames to a looping GIF on one shared palette (no flicker between frames), the cell label on every
    frame and the outcome word on a last, longer frame."""
    mono = ImageFont.truetype(str(FONTS / "IBMPlexMono-Regular.ttf"), LABEL_PX)
    sans = ImageFont.truetype(str(FONTS / "IBMPlexSans-Regular.ttf"), LABEL_PX)
    semi = ImageFont.truetype(str(FONTS / "IBMPlexSans-SemiBold.ttf"), OUTCOME_PX)
    rgb = [Image.fromarray(f) for f in frames]
    rgb.append(rgb[-1].copy())
    for k, im in enumerate(rgb):
        dr = ImageDraw.Draw(im)
        draw_label(dr, (28, HEIGHT - 28 - LABEL_PX), cell_label, mono, sans)
        if k == len(rgb) - 1:
            dr.text((WIDTH - 28, HEIGHT - 28 - OUTCOME_PX), outcome, font=semi, fill=INK, anchor="ra")
    pick = [rgb[0], rgb[len(rgb) // 3], rgb[2 * len(rgb) // 3], rgb[-1]]
    sheet = Image.new("RGB", (WIDTH, HEIGHT * len(pick)))
    for k, im in enumerate(pick):
        sheet.paste(im, (0, k * HEIGHT))
    palette = sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    imgs = [im.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for im in rgb]
    durations = [1000 // FPS] * len(imgs)
    durations[-1] = HOLD_MS
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durations, loop=0, optimize=False)
    return rgb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--obj", default="038_padlock")
    ap.add_argument("--trial", type=int, default=118)
    ap.add_argument("--run", default="core120")
    ap.add_argument("--mode", default="rank", choices=["rank", "filter"])
    ap.add_argument("--out", default=str(RESULTS / "clips"))
    ap.add_argument("--sheet", default=None, help="directory for a contact sheet of each clip (first, middle, last frames)")
    a = ap.parse_args()
    run_dir = RESULTS / "sim" / a.run
    raw = json.loads((run_dir / "config.json").read_text())
    cfg = Config(**{k: v for k, v in raw.items() if k in Config.__dataclass_fields__})
    rows = {}
    for line in (run_dir / "rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r.get("obj") == a.obj and r.get("trial") == a.trial and r.get("mode") == a.mode and r.get("cell") in CELLS:
            rows[r["cell"]] = r
    assert set(rows) == set(CELLS), f"rows.jsonl has {sorted(rows)} for {a.obj} trial {a.trial}"

    sim = RecordingSim(a.obj)
    runner = Runner(a.obj, cfg, sim=sim)
    pr = runner.prepare(a.trial)
    assert pr.state is not None, "the trial was skipped"
    assert abs(pr.mu_star - rows["baseline"]["mu_star"]) < 1e-9, (pr.mu_star, rows["baseline"]["mu_star"])
    w_g = gravity_wrench(runner.spec.mass, pr.R.T @ np.array([0.0, 0.0, -1.0]))
    cells = {n: (ms, mf) for n, ms, mf in cells_for(pr.mu_star, runner.spec.material, cfg)}
    plan = {}
    for name in CELLS:
        mu_sel, mu_f = cells[name]
        d = decide(pr.cands, np.zeros(3), runner.rho, mu_sel, mu_f, a.mode, w_g, runner.cap, cfg.eps_min, cfg.safety,
                   cfg.force_min, gamma_scale=cfg.gamma_scale)
        f = round(d.force.per_finger, 2)
        row = rows[name]
        assert d.index == row["chosen"] and abs(f - row["force"]) < 1e-6, (name, d.index, f, row["chosen"], row["force"])
        plan[name] = (d.index, f)
    # one camera for the four clips: a view across the baseline grasp's closing axis, so both fingers show
    axis = pr.world[plan["baseline"][0]].axis
    sim.azimuth = math.degrees(math.atan2(axis[1], axis[0])) + 90.0

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f"{a.obj} trial {a.trial} ({a.mode}): mu* = {pr.mu_star:.3f}, cap {runner.cap:.1f}N, {len(pr.cands)} candidates")
    for name, (idx, f) in plan.items():
        sim.start()
        res = sim.execute(pr.world[idx], f, probe=False, state_id=pr.state)
        frames = sim.stop()
        row = rows[name]
        assert (res.success, res.lifted, res.held) == (row["success"], row["lifted"], row["held"]), \
            (name, res.success, res.lifted, res.held, row["success"], row["lifted"], row["held"])
        outcome = "Held" if res.success else "Dropped"
        path = out / f"{a.obj}_t{a.trial}_{name}.gif"
        rgb = write_gif(frames, path, CELLS[name], outcome)
        print(f"  {name:9s} candidate {idx:2d}  {f:5.2f}N per finger  {outcome:7s} slip {res.slip_mm:6.1f}mm "
              f"(run: {row['slip_mm']:6.1f}mm)  {len(frames)} frames  {path.stat().st_size / 1e6:.1f} MB  -> {path.name}")
        if a.sheet:
            pick = [rgb[0], rgb[len(rgb) // 3], rgb[2 * len(rgb) // 3], rgb[-1]]
            sheet = Image.new("RGB", (WIDTH * len(pick), HEIGHT))
            for k, im in enumerate(pick):
                sheet.paste(im, (k * WIDTH, 0))
            sheet.save(Path(a.sheet) / f"{name}.png")
    p.removeState(pr.state, physicsClientId=sim.cid)
    sim.close()


if __name__ == "__main__":
    main()
