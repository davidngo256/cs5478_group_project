"""Grasp wrench space for point contacts with friction (hard or soft finger).

Conventions
- Contacts are given in the object frame as (point, inward unit normal).
- Wrenches are taken about the centre of mass and torques are divided by a
  characteristic length rho so that both halves have force units.
- The hull is built from primitive wrenches that each carry unit normal force,
  so the hull is the set of wrenches reachable with a total normal force of 1.
- Soft-finger contacts add a torsional limit |tau_n| <= gamma * f_n with
  gamma = (2/3) * a * mu for a uniform-pressure disc of radius a.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import ConvexHull, QhullError

M_EDGES_DEFAULT = 8
R_PATCH_DEFAULT = 0.008  # contact patch radius [m]


def tangent_frame(n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Two unit tangents orthogonal to the unit normal n."""
    n = np.asarray(n, float)
    helper = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    t1 = np.cross(n, helper)
    t1 /= np.linalg.norm(t1)
    t2 = np.cross(n, t1)
    return t1, t2


def torsional_coefficient(mu: float, r_patch: float = R_PATCH_DEFAULT, scale: float = 1.0) -> float:
    """gamma [m] for a uniform-pressure circular patch: |tau_n| <= gamma * f_n. `scale` multiplies
    the model (the planner's assumption); the simulator always uses scale 1."""
    return scale * 2.0 / 3.0 * r_patch * mu


def contact_wrenches(p, n, mu: float, com, rho: float, *, soft: bool = True,
                     m_edges: int = M_EDGES_DEFAULT, r_patch: float = R_PATCH_DEFAULT,
                     gamma_scale: float = 1.0) -> np.ndarray:
    """Primitive wrenches of one contact, each with unit normal force. Shape (m_edges[+2], 6)."""
    p = np.asarray(p, float)
    n = np.asarray(n, float)
    n = n / np.linalg.norm(n)
    r = p - np.asarray(com, float)
    t1, t2 = tangent_frame(n)
    rows = []
    for k in range(m_edges):
        th = 2.0 * np.pi * k / m_edges
        f = n + mu * (np.cos(th) * t1 + np.sin(th) * t2)
        rows.append(np.r_[f, np.cross(r, f) / rho])
    if soft:
        gamma = torsional_coefficient(mu, r_patch, gamma_scale)
        for sgn in (1.0, -1.0):
            rows.append(np.r_[n, (np.cross(r, n) + sgn * gamma * n) / rho])
    return np.array(rows)


def grasp_wrenches(contacts, mu: float, com, rho: float, **kw) -> np.ndarray:
    """Stack the primitive wrenches of all contacts. contacts = [(p, n), ...]."""
    return np.vstack([contact_wrenches(p, n, mu, com, rho, **kw) for p, n in contacts])


@dataclass(frozen=True)
class GraspQuality:
    epsilon: float          # radius of largest origin-centred ball in the hull (0 if not force closure)
    nu: float               # hull volume (0 if degenerate)
    force_closure: bool
    _equations: np.ndarray | None = None   # hull facets a.x + b <= 0, kept for min_normal_force

    def min_normal_force(self, wrench: np.ndarray) -> float:
        """Smallest total normal force that resists `wrench` (i.e. applies -wrench).

        Returns inf if the grasp is not force closure or the direction is unreachable.
        """
        if not self.force_closure or self._equations is None:
            return float("inf")
        w = -np.asarray(wrench, float)          # the grasp must apply the opposite wrench
        norm = np.linalg.norm(w)
        if norm < 1e-12:
            return 0.0
        d = w / norm
        a, b = self._equations[:, :-1], self._equations[:, -1]
        ad = a @ d
        ok = ad > 1e-12
        if not np.any(ok):
            return float("inf")
        t_star = np.min(-b[ok] / ad[ok])        # distance to hull boundary along d
        return float(norm / t_star)


def evaluate_hull(W: np.ndarray) -> GraspQuality:
    """Ferrari-Canny epsilon and the hull volume nu from a set of primitive wrenches."""
    if np.linalg.matrix_rank(W - W.mean(axis=0), tol=1e-9) < 6:
        return GraspQuality(0.0, 0.0, False)
    try:
        hull = ConvexHull(W)
    except QhullError:
        try:
            hull = ConvexHull(W, qhull_options="QJ")
        except QhullError:
            return GraspQuality(0.0, 0.0, False)
    offsets = hull.equations[:, -1]           # a.x + b <= 0 inside; origin inside iff all b < 0
    fc = bool(np.all(offsets < -1e-9))
    eps = float(np.min(-offsets)) if fc else 0.0
    return GraspQuality(eps, float(hull.volume), fc, hull.equations if fc else None)


def evaluate_grasp(contacts, mu: float, com, rho: float, **kw) -> GraspQuality:
    return evaluate_hull(grasp_wrenches(contacts, mu, com, rho, **kw))


def nguyen_antipodal(p1, n1, p2, n2, mu: float) -> bool:
    """Planar / two-soft-finger force-closure test: p1p2 strictly inside both cones."""
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    n1, n2 = np.asarray(n1, float), np.asarray(n2, float)
    d = p2 - p1
    d /= np.linalg.norm(d)
    half = np.arctan(mu)
    a1 = np.arccos(np.clip(d @ (n1 / np.linalg.norm(n1)), -1, 1))
    a2 = np.arccos(np.clip(-d @ (n2 / np.linalg.norm(n2)), -1, 1))
    return bool(a1 < half and a2 < half)
