import numpy as np
import pytest
import trimesh

from matgrasp.planner import choose, decide, gravity_wrench, grip_force, score_candidates
from matgrasp.sampler import sample_candidates
from matgrasp.wrench import evaluate_grasp

COM = np.zeros(3)


@pytest.fixture(scope="module")
def setup():
    mesh = trimesh.creation.box(extents=[0.06, 0.10, 0.15])
    cands = sample_candidates(mesh, 60, np.random.default_rng(0))
    return mesh, cands, 0.075


def test_rank_picks_max_epsilon(setup):
    _, cands, rho = setup
    quals = score_candidates(cands, 0.5, COM, rho)
    i = choose(cands, quals, "rank")
    assert quals[i].epsilon == max(q.epsilon for q in quals)


def test_filter_respects_generator_order(setup):
    _, cands, rho = setup
    quals = score_candidates(cands, 0.5, COM, rho)
    i = choose(cands, quals, "filter")
    # nothing with a higher gen_score is acceptable
    for k, c in enumerate(cands):
        if c.gen_score > cands[i].gen_score:
            assert not (quals[k].force_closure and quals[k].epsilon >= 1e-3)


def test_filter_and_rank_both_pick_force_closure(setup):
    _, cands, rho = setup
    quals = score_candidates(cands, 0.3, COM, rho)
    for mode in ("rank", "filter"):
        i = choose(cands, quals, mode)
        assert i is not None and quals[i].force_closure


def test_low_mu_rejects_more_candidates(setup):
    _, cands, rho = setup
    n_fc = [sum(q.force_closure for q in score_candidates(cands, mu, COM, rho)) for mu in (0.15, 0.3, 0.6)]
    assert n_fc[0] < n_fc[1] < n_fc[2]


def test_grip_force_scales_with_inverse_mu_and_caps():
    g = [(np.array([-0.04, 0, 0]), np.array([1.0, 0, 0])), (np.array([0.04, 0, 0]), np.array([-1.0, 0, 0]))]
    w = gravity_wrench(0.6, [0, 0, -1])                     # 0.6 kg, closing axis horizontal
    f3 = grip_force(evaluate_grasp(g, 0.3, COM, 0.05), w, cap=100.0)
    f6 = grip_force(evaluate_grasp(g, 0.6, COM, 0.05), w, cap=100.0)
    assert f3.per_finger == pytest.approx(2 * f6.per_finger, rel=0.15)
    # 0.6 kg at mu=0.3 with 1.5 safety: total ~ 1.5 * 5.9 / 0.3 ~ 29 N, ~15 N per finger
    assert 10 < f3.per_finger < 22 and not f3.capped
    assert grip_force(evaluate_grasp(g, 0.3, COM, 0.05), w, cap=8.0).per_finger == 8.0
    # a light object still gets the actuator floor
    light = grip_force(evaluate_grasp(g, 0.8, COM, 0.05), gravity_wrench(0.04, [0, 0, -1]), cap=40.0)
    assert light.per_finger == 3.0 and not light.capped


def test_cap_aware_selection_prefers_holdable_grasps(setup):
    _, cands, rho = setup
    w = gravity_wrench(0.5, [0, 0, -1])
    tight = decide(cands, COM, rho, 0.3, 0.3, "rank", w, cap=6.0)
    loose = decide(cands, COM, rho, 0.3, 0.3, "rank", w, cap=200.0)
    assert not loose.fallback and not loose.force.capped
    # under a tight cap the planner either finds a holdable grasp (not capped) or falls back at the cap
    assert tight.fallback == tight.force.capped


def test_decide_cells_share_grasp_when_only_force_mu_differs(setup):
    _, cands, rho = setup
    w = gravity_wrench(0.5, [0, 0, -1])
    a = decide(cands, COM, rho, mu_select=0.5, mu_force=0.5, mode="rank", w_gravity=w, cap=40.0)
    b = decide(cands, COM, rho, mu_select=0.5, mu_force=0.2, mode="rank", w_gravity=w, cap=40.0)
    assert a.index == b.index
    assert b.force.per_finger > a.force.per_finger
