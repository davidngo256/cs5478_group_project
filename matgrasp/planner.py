"""Grasp selection and grip force from a friction estimate.

rank mode   : execute the candidate with the largest epsilon(mu), ties broken by nu.
filter mode : keep the generator's own ordering (gen_score) and execute the first candidate
              that is force closure at mu with epsilon >= eps_min.
grip force  : the minimum normal force that resists the gravity wrench at mu, times a safety
              factor, clipped to a cap. Reported per finger (two fingers share the total).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .sampler import GraspCandidate
from .wrench import GraspQuality, evaluate_grasp

EPS_MIN_DEFAULT = 1e-3
SAFETY_DEFAULT = 1.5
FORCE_MIN_DEFAULT = 3.0     # per-finger floor [N]: real grippers cannot command sub-newton grips
G = 9.81


def score_candidates(cands: list[GraspCandidate], mu: float, com, rho: float, **kw) -> list[GraspQuality]:
    return [evaluate_grasp(c.contacts, mu, com, rho, **kw) for c in cands]


def choose(cands: list[GraspCandidate], quals: list[GraspQuality], mode: str,
           eps_min: float = EPS_MIN_DEFAULT, acceptable=None) -> int | None:
    """Index of the chosen candidate, or None if nothing is acceptable.
    `acceptable` is an optional boolean mask (e.g. holdable under the grip-force cap at the
    planning mu); candidates outside it are ignored."""
    ok = [q.force_closure and q.epsilon >= eps_min for q in quals]
    if acceptable is not None:
        ok = [a and b for a, b in zip(ok, acceptable)]
    if mode == "rank":
        idx = [i for i in range(len(quals)) if ok[i]]
        if not idx:
            return None
        return int(max(idx, key=lambda k: (quals[k].epsilon, quals[k].nu)))
    if mode == "filter":
        for i in sorted(range(len(cands)), key=lambda k: -cands[k].gen_score):
            if ok[i]:
                return i
        return None
    raise ValueError(mode)


def gravity_wrench(mass: float, down_obj: np.ndarray) -> np.ndarray:
    """Gravity wrench about the CoM in the object frame; `down_obj` is the world -z axis
    expressed in the object frame."""
    d = np.asarray(down_obj, float)
    return np.r_[mass * G * d / np.linalg.norm(d), 0.0, 0.0, 0.0]


@dataclass(frozen=True)
class GripForce:
    per_finger: float       # commanded force per finger [N]
    required: float         # analytical minimum total normal force before safety/cap [N]
    capped: bool


def grip_force(q: GraspQuality, w_gravity: np.ndarray, cap: float, safety: float = SAFETY_DEFAULT,
               floor: float = FORCE_MIN_DEFAULT) -> GripForce:
    """Per-finger grip force for a two-finger grasp with quality q at the planning mu:
    safety x analytical minimum, no less than `floor`, no more than `cap`."""
    req = q.min_normal_force(w_gravity)
    if not np.isfinite(req):
        return GripForce(cap, float("inf"), True)
    per = max(safety * req / 2.0, floor)
    return GripForce(float(min(per, cap)), float(req), per > cap)


@dataclass(frozen=True)
class Decision:
    index: int | None
    force: GripForce | None
    mu_select: float
    mu_force: float
    mode: str
    fallback: bool = False      # no candidate was holdable under the cap at mu_select; chose by force closure only


def decide(cands, com, rho, mu_select: float, mu_force: float, mode: str, w_gravity, cap: float,
           eps_min: float = EPS_MIN_DEFAULT, safety: float = SAFETY_DEFAULT, floor: float = FORCE_MIN_DEFAULT, **kw) -> Decision:
    """Full decision: pick a grasp with mu_select, set its force with mu_force (the 2x2 cells
    differ only in these two arguments). A candidate is acceptable if, at mu_select, it is force
    closure and the planner believes it can hold the gravity wrench within the grip-force cap;
    if none is, the planner falls back to force closure alone and commands the cap."""
    quals = score_candidates(cands, mu_select, com, rho, **kw)
    holdable = [not grip_force(q, w_gravity, cap, safety, floor).capped for q in quals]
    i = choose(cands, quals, mode, eps_min, acceptable=holdable)
    fallback = False
    if i is None:
        i = choose(cands, quals, mode, eps_min)
        fallback = True
    if i is None:
        return Decision(None, None, mu_select, mu_force, mode, True)
    q_force = quals[i] if mu_force == mu_select else evaluate_grasp(cands[i].contacts, mu_force, com, rho, **kw)
    return Decision(i, grip_force(q_force, w_gravity, cap, safety, floor), mu_select, mu_force, mode, fallback)
