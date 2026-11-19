import numpy as np
import pytest

from matgrasp.wrench import (contact_wrenches, evaluate_grasp, grasp_wrenches,
                             nguyen_antipodal, torsional_coefficient)

RHO = 0.05
COM = np.zeros(3)


def box_grasp(offset=0.0, half_width=0.04):
    """Two contacts on opposite faces of a box, closing axis x, contacts offset along z."""
    p1 = np.array([-half_width, 0.0, 0.0])
    p2 = np.array([half_width, 0.0, offset])
    return [(p1, np.array([1.0, 0, 0])), (p2, np.array([-1.0, 0, 0]))]


def test_hard_finger_two_contacts_is_rank_deficient():
    W = grasp_wrenches(box_grasp(), 0.5, COM, RHO, soft=False)
    assert np.linalg.matrix_rank(W, tol=1e-9) == 5
    q = evaluate_grasp(box_grasp(), 0.5, COM, RHO, soft=False)
    assert q.epsilon == 0.0 and not q.force_closure


def test_soft_finger_two_contacts_is_force_closure():
    q = evaluate_grasp(box_grasp(), 0.5, COM, RHO)
    assert q.force_closure and q.epsilon > 0 and q.nu > 0


def test_epsilon_and_nu_increase_with_mu():
    eps = [evaluate_grasp(box_grasp(), mu, COM, RHO).epsilon for mu in (0.2, 0.4, 0.6, 0.8)]
    nus = [evaluate_grasp(box_grasp(), mu, COM, RHO).nu for mu in (0.2, 0.4, 0.6, 0.8)]
    assert all(a < b for a, b in zip(eps, eps[1:]))
    assert all(a < b for a, b in zip(nus, nus[1:]))


def test_offset_grasp_loses_closure_at_low_mu():
    # contacts offset so the segment makes ~14.9 deg with the normals (Figure 1 of the proposal)
    offset = 2 * 0.04 * np.tan(np.deg2rad(14.9))
    g = box_grasp(offset=offset)
    assert nguyen_antipodal(*g[0], *g[1], mu=0.5)
    assert not nguyen_antipodal(*g[0], *g[1], mu=0.2)
    assert evaluate_grasp(g, 0.5, COM, RHO).force_closure
    assert not evaluate_grasp(g, 0.2, COM, RHO).force_closure


def test_hull_matches_nguyen_on_aligned_and_misaligned_grasps():
    rng = np.random.default_rng(0)
    agree = 0
    n = 60
    for _ in range(n):
        offset = rng.uniform(0, 0.05)
        mu = rng.uniform(0.15, 0.9)
        g = box_grasp(offset=offset)
        agree += nguyen_antipodal(*g[0], *g[1], mu) == evaluate_grasp(g, mu, COM, RHO).force_closure
    assert agree >= n - 2   # linearisation can disagree right at the cone boundary


def test_primitive_forces_lie_on_cone_and_torsion_uses_gamma():
    W = contact_wrenches([0, 0, 0], [0, 0, 1], 0.4, COM, RHO, m_edges=8)
    forces = W[:8, :3]
    assert np.allclose(forces[:, 2], 1.0)
    assert np.allclose(np.linalg.norm(forces[:, :2], axis=1), 0.4)
    tors = W[8:, 3:] * RHO
    assert np.allclose(np.abs(tors[:, 2]), torsional_coefficient(0.4))


def test_min_normal_force_scales_with_wrench_and_inverse_mu():
    g = box_grasp()
    gravity = np.array([0, 0, -1.0, 0, 0, 0])          # 1 N downward, tangential to both pads
    f_lo = evaluate_grasp(g, 0.25, COM, RHO).min_normal_force(gravity)
    f_hi = evaluate_grasp(g, 0.5, COM, RHO).min_normal_force(gravity)
    assert f_hi < f_lo
    assert f_lo == pytest.approx(2 * f_hi, rel=0.15)     # tangential capacity ~ mu * F_n
    assert evaluate_grasp(g, 0.5, COM, RHO).min_normal_force(2 * gravity) == pytest.approx(2 * f_hi)


def test_min_normal_force_sanity_value():
    # two pads, mu=0.5, 1 N tangential load: total normal force needed ~ 1/mu = 2 N (before linearisation loss)
    g = box_grasp()
    f = evaluate_grasp(g, 0.5, COM, RHO).min_normal_force(np.array([0, 0, -1.0, 0, 0, 0]))
    assert 1.8 < f < 2.6


def test_gamma_scale_scales_only_the_torsional_rows():
    from matgrasp.wrench import contact_wrenches

    p, n, com, rho = np.array([0.03, 0.0, 0.0]), np.array([-1.0, 0.0, 0.0]), np.zeros(3), 0.05
    w1 = contact_wrenches(p, n, 0.4, com, rho, m_edges=8)
    w2 = contact_wrenches(p, n, 0.4, com, rho, m_edges=8, gamma_scale=2.0)
    assert np.allclose(w1[:8], w2[:8])                                  # cone edges unchanged
    tors1 = w1[8:, 3:] @ n; tors2 = w2[8:, 3:] @ n                       # torque component along the normal
    assert np.allclose(tors2, 2.0 * tors1) and not np.allclose(tors1, 0)
