"""Trial runner for the material-aware grasping study.

One trial = one object, one settled pose, one true mu*, one candidate set. Every experimental
cell (arm x mode) plans on the same candidates and is executed from the same saved simulator
state, so cells are paired. Executions are cached per (candidate, grip force) because many
cells choose the same grasp.

Cells: name -> (mu used to choose the grasp, mu used to set the grip force), evaluated in both
rank and filter mode.
  baseline   (0.5, 0.5)     the constant-mu assumption
  squeeze    (0.5, mu*)     baseline grasp, oracle force          } 2x2 on
  select     (mu*, 0.5)     oracle grasp, baseline force          } baseline/oracle
  oracle     (mu*, mu*)     ceiling
  table_q    (mu_q, mu_q)   perfect classifier, table lookup, quantile q  (H2 upper bound)
  table_mean (mean, mean)   same with the mean of p(mu)                    (ablation b)
  head:<h>   (mu_q, mu_q)   real classifier posterior for this object, quantile q
  head:<h>:mean             same at the mean of p(mu)
  head:<h>:squeeze (0.5, mu_q)  baseline grasp, force from the head's quantile (what a deployment
                            that only uses the estimate for grip force would do); table_squeeze
                            is the same with the perfect classifier
  sweep:<m>  (m, m)         constant-mu baseline at other values           (ablation d)
"""
from __future__ import annotations

import json
import os
import time
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from .friction import MATERIAL_TABLE, MuDistribution, sample_true_mu
from .planner import EPS_MIN_DEFAULT, FORCE_MIN_DEFAULT, SAFETY_DEFAULT, decide, gravity_wrench, score_candidates
from .sampler import sample_candidates, transform_candidate
from .sim import GraspSim, gripper_urdf, quat_to_mat
from .ycb import OBJECTS, characteristic_radius, ensure_mesh, ensure_vhacd, load_mesh

RESULTS = Path(__file__).resolve().parents[1] / "results"
SWEEP_MUS = (0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.9)


def default_workers() -> int:
    """One simulation process per CPU core: the study is CPU-bound and headless."""
    return os.cpu_count() or 1


@dataclass
class Config:
    n_cands: int = 40
    q: float = 0.1
    quantiles: tuple = (0.05, 0.25)          # extra quantiles for ablation b (table arm only)
    eps_min: float = EPS_MIN_DEFAULT
    safety: float = SAFETY_DEFAULT
    force_min: float = FORCE_MIN_DEFAULT
    cap_min: float = 8.0
    cap_max: float = 40.0
    cap_factor: float = 4.0
    sweep: bool = True
    probe: bool = True
    heads: dict = field(default_factory=dict)   # head name -> {obj_id: {class: prob}}
    widen: float = 1.5                          # spread of the true-mu draw (friction.sample_true_mu)
    min_feasible: int = 8                       # skip the trial if fewer feasible candidates than this
    max_batches: int = 12
    gamma_scale: float = 1.0                    # planner's torsional coefficient x this; the physics is unchanged


def force_cap(obj_id: str, cfg: Config) -> float:
    """Per-object grip-force cap (fragility limit), the same for every arm: cap_factor times the
    ideal per-finger force mg/(2 mu_lo) at the low end of the material's friction range. Off-centre
    grasps need several times the ideal force because of torsion, so the factor leaves room for a
    well-placed grasp but not for a poor one."""
    o = OBJECTS[obj_id]
    lo = MATERIAL_TABLE[o.material].lo
    need = cfg.cap_factor * o.mass * 9.81 / (2 * lo)
    return float(np.clip(need, cfg.cap_min, cfg.cap_max))


def cells_for(mu_star: float, material: str, cfg: Config, heads: dict | None = None) -> list[tuple[str, float, float]]:
    """(cell name, mu_select, mu_force). `heads` maps head name -> class posterior for THIS object."""
    table = MuDistribution.from_class_probs({material: 1.0})
    out = [("baseline", 0.5, 0.5), ("squeeze", 0.5, mu_star), ("select", mu_star, 0.5), ("oracle", mu_star, mu_star)]
    mq = table.quantile(cfg.q)
    out += [("table_q", mq, mq), ("table_mean", table.mean(), table.mean()), ("table_squeeze", 0.5, mq)]
    for q in cfg.quantiles:
        m = table.quantile(q)
        out.append((f"table_q{q}", m, m))
    for name, probs in (heads or {}).items():
        d = MuDistribution.from_class_probs(probs)
        mq, mm = d.quantile(cfg.q), d.mean()
        out += [(f"head:{name}", mq, mq), (f"head:{name}:mean", mm, mm), (f"head:{name}:squeeze", 0.5, mq)]
    if cfg.sweep:
        out += [(f"sweep:{m}", m, m) for m in SWEEP_MUS]
    return out


@dataclass
class Prepared:
    """The part of a trial every cell shares: the true mu, the settled pose, the candidate set in the object
    frame and in the world frame, and the saved simulator state to execute from (None when the trial is
    skipped for too few feasible candidates). The caller removes `state`."""
    mu_star: float
    pos: np.ndarray
    R: np.ndarray
    cands: list
    world: list
    state: int | None


class Runner:
    """Holds one simulator per process; call run_trial repeatedly. `sim` lets a recording pass in a
    subclass of GraspSim (scripts/record_clips.py)."""

    def __init__(self, obj_id: str, cfg: Config, sim: GraspSim | None = None):
        self.obj_id = obj_id
        self.cfg = cfg
        self.spec = OBJECTS[obj_id]
        self.mesh = load_mesh(obj_id)
        self.rho = characteristic_radius(self.mesh)
        self.sim = sim or GraspSim(obj_id)
        self.cap = force_cap(obj_id, cfg)

    def close(self):
        self.sim.close()

    def prepare(self, trial: int) -> Prepared:
        """Draw the trial's true mu, settle the object and sample its feasible candidates (seeded by object
        and trial index, so the same in every run), then save the state the cells execute from."""
        import pybullet as p
        cfg, sim = self.cfg, self.sim
        sim.reset()
        # crc32, not hash(): str hashes are salted per interpreter, which made every run draw different trials
        rng = np.random.default_rng([zlib.crc32(self.obj_id.encode()), trial])
        mu_star = sample_true_mu(self.spec.material, rng, widen=cfg.widen)
        sim.set_friction(mu_star)
        # even trials: the scanned (upright) pose with a random yaw; odd trials: random drop
        if trial % 2 == 0:
            from scipy.spatial.transform import Rotation
            orn = Rotation.from_euler("z", rng.uniform(0, 2 * np.pi)).as_quat()
            pos, quat = sim.settle_object(rng, orientation=orn)
        else:
            pos, quat = sim.settle_object(rng)
        R = quat_to_mat(quat)
        up_obj = R.T @ np.array([0.0, 0.0, 1.0])
        # candidates in the object frame, feasibility-filtered in the world frame (mu-independent)
        cands, world = [], []
        for _ in range(cfg.max_batches):
            batch = sample_candidates(self.mesh, cfg.n_cands, rng, table_up=up_obj)
            for c in batch:
                cw = transform_candidate(c, R, pos)
                q_open = max(0.0, 0.045 - (c.width / 2 + 0.004 + 0.01))
                if sim.find_approach(cw, q_open) is not None:
                    cands.append(c); world.append(cw)
            if len(cands) >= cfg.n_cands:
                break
        cands, world = cands[:cfg.n_cands], world[:cfg.n_cands]
        sim.park_gripper()
        if len(cands) < cfg.min_feasible:
            return Prepared(mu_star, pos, R, cands, world, None)
        return Prepared(mu_star, pos, R, cands, world, p.saveState(physicsClientId=sim.cid))

    def run_trial(self, trial: int) -> list[dict]:
        import pybullet as p
        cfg, sim = self.cfg, self.sim
        pr = self.prepare(trial)
        mu_star, pos, R, cands, world, state = pr.mu_star, pr.pos, pr.R, pr.cands, pr.world, pr.state
        if state is None:
            return [dict(obj=self.obj_id, material=self.spec.material, trial=trial, mu_star=mu_star, upright=trial % 2 == 0,
                         n_cands=len(cands), skipped=True, note=f"only {len(cands)} feasible candidates")]
        w_g = gravity_wrench(self.spec.mass, R.T @ np.array([0.0, 0.0, -1.0]))
        q_true = score_candidates(cands, mu_star, np.zeros(3), self.rho, gamma_scale=cfg.gamma_scale)
        base = dict(obj=self.obj_id, material=self.spec.material, trial=trial, mu_star=mu_star, upright=trial % 2 == 0,
                    n_cands=len(cands), n_fc_true=int(sum(q.force_closure for q in q_true)), cap=self.cap)
        rows, cache = [], {}
        t0 = time.time()
        obj_heads = {n: p[self.obj_id] for n, p in cfg.heads.items() if self.obj_id in p}
        for mode in ("rank", "filter"):
            for name, mu_sel, mu_f in cells_for(mu_star, self.spec.material, cfg, obj_heads):
                if not cands:
                    rows.append(dict(base, cell=name, mode=mode, mu_select=mu_sel, mu_force=mu_f, chosen=None, executed=False))
                    continue
                d = decide(cands, np.zeros(3), self.rho, mu_sel, mu_f, mode, w_g, self.cap, cfg.eps_min, cfg.safety,
                           cfg.force_min, gamma_scale=cfg.gamma_scale)
                row = dict(base, cell=name, mode=mode, mu_select=mu_sel, mu_force=mu_f, chosen=d.index, fallback=d.fallback)
                if d.index is None:
                    row.update(executed=False, note="no acceptable candidate")
                    rows.append(row)
                    continue
                f = round(d.force.per_finger, 2)
                key = (d.index, f)
                if key not in cache:
                    cache[key] = sim.execute(world[d.index], f, probe=cfg.probe, state_id=state)
                r = cache[key]
                qt = q_true[d.index]
                row.update(executed=True, force=f, force_required=d.force.required, capped=d.force.capped,
                           eps_true=qt.epsilon, fc_true=qt.force_closure, eps_plan=None,
                           feasible=r.feasible, both_contacts=r.both_contacts, lifted=bool(r.lifted), held=bool(r.held),
                           success=bool(r.success), slip_mm=float(r.slip_mm), pivot_deg=float(r.pivot_deg),
                           min_wrench=float(r.min_wrench), min_wrench_all=float(r.min_wrench_all),
                           wrench=r.wrench_at_slip, approach_deg=float(r.approach_deg), note=r.note,
                           misalign_deg=cands[d.index].misalignment_deg(), width=cands[d.index].width)
                rows.append(row)
        p.removeState(state, physicsClientId=sim.cid)
        for r in rows:
            r["n_exec"] = len(cache)
            r["wall_s"] = round(time.time() - t0, 1)
        return rows


# ---- multiprocessing driver ----------------------------------------------------------------
_runner: Runner | None = None


def _work(args):
    global _runner
    obj_id, trials, cfg_dict = args
    cfg = Config(**cfg_dict)
    if _runner is None or _runner.obj_id != obj_id:
        if _runner is not None:
            _runner.close()
        _runner = Runner(obj_id, cfg)
    out = []
    for t in trials:
        try:
            out.extend(_runner.run_trial(t))
        except Exception as e:  # keep the sweep going; record the failure
            out.append(dict(obj=obj_id, trial=t, error=repr(e)))
    return out


def _prepare(obj_id: str) -> str:
    """Fetch one object's mesh into data/ and make sure its convex hulls exist."""
    try:
        ensure_mesh(obj_id, verbose=False)
        ensure_vhacd(obj_id, verbose=False)
    except Exception as e:   # a download error cannot be pickled back to the parent: send its text instead
        raise RuntimeError(f"could not prepare {obj_id}: {e!r}") from None
    return obj_id


def run_study(run_name: str, objects: list[str], n_trials: int, cfg: Config, workers: int | None = None,
              chunk: int = 5) -> Path:
    from multiprocessing import Pool
    workers = workers or default_workers()
    out_dir = RESULTS / "sim" / run_name
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(o, list(range(s, min(s + chunk, n_trials))), asdict(cfg)) for o in objects for s in range(0, n_trials, chunk)]
    path = out_dir / "rows.jsonl"
    part = out_dir / "rows.jsonl.part"   # the rows collect here and replace rows.jsonl once the run is complete,
    n = 0                                # so a run that fails or is interrupted keeps the previous rows
    with Pool(workers) as pool, open(part, "w") as f:
        # Several workers get trials of the same object. On a fresh data/ they would all download its mesh at
        # once (and decompose it, for an object without a shipped hull file), and one would load a file another
        # is still writing. Prepare each object once, one process per object, before the trials start.
        gripper_urdf()
        pool.map(_prepare, objects, chunksize=1)
        for rows in pool.imap_unordered(_work, jobs):
            for r in rows:
                f.write(json.dumps(r, default=float) + "\n")
            n += len(rows)
            f.flush()
    os.replace(part, path)
    (out_dir / "config.json").write_text(json.dumps(dict(asdict(cfg), objects=objects, n_trials=n_trials), indent=1, default=str))
    print(f"wrote {n} rows to {path}")
    return path
