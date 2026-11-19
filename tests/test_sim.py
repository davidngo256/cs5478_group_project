"""Physics harness sanity tests on a synthetic box (no YCB download needed)."""
import numpy as np
import pytest
import trimesh

from matgrasp.sampler import GraspCandidate, sample_candidates, transform_candidate
from matgrasp.sim import GraspSim, grasp_pose

EXT = [0.06, 0.05, 0.10]     # x, y, z


@pytest.fixture(scope="module")
def sim():
    s = GraspSim(box_extents=EXT, mass=0.4)
    yield s
    s.close()


def centred_grasp(sim, offset_x=0.0):
    """Grasp across the 5 cm (y) dimension at the current object pose; offset_x moves the
    contacts along x so gravity loads torsion about the closing axis."""
    pos, R = sim.object_pose()
    p1 = np.array([offset_x, -EXT[1] / 2, 0.0])
    p2 = np.array([offset_x, EXT[1] / 2, 0.0])
    c = GraspCandidate(p1, np.array([0, 1.0, 0]), p2, np.array([0, -1.0, 0]), np.array([0, 1.0, 0]), EXT[1], 1.0)
    return transform_candidate(c, R, pos)


def test_settle_puts_box_on_table(sim):
    rng = np.random.default_rng(0)
    pos, quat = sim.settle_object(rng, orientation=[0, 0, 0, 1])
    assert abs(pos[2] - EXT[2] / 2) < 0.005


def test_grasp_pose_places_pads_on_contacts(sim):
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    c = centred_grasp(sim)
    pos, quat, R = grasp_pose(c)
    assert np.allclose(R[:, 1], c.axis)                 # y = closing axis
    assert R[:, 2] @ np.array([0, 0, -1]) > 0.99        # angle 0 = from above
    pos90, _, R90 = grasp_pose(c, 90)
    assert abs(R90[:, 2] @ np.array([0, 0, -1])) < 1e-6 # 90 deg = horizontal approach
    assert np.allclose(R90[:, 1], c.axis)


def test_adequate_force_lifts_and_holds(sim):
    sim.set_friction(0.5)
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    r = sim.execute(centred_grasp(sim), grip_force=20.0, probe=True)
    assert r.feasible and r.both_contacts and r.lifted and r.held, r
    assert r.pivot_deg < 5 and r.slip_mm < 8
    assert len(r.wrench_at_slip) == 12 and r.min_wrench > 0


def test_tiny_force_drops_the_object(sim):
    sim.set_friction(0.5)
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    # 0.4 kg needs ~ 3.9/(2*0.5) ~ 4 N per finger; 1 N cannot hold it
    r = sim.execute(centred_grasp(sim), grip_force=1.0, probe=False)
    assert r.feasible and not r.success


def test_wrench_at_slip_grows_with_friction_and_force(sim):
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    sid_vals = {}
    for mu, f in ((0.2, 20.0), (0.6, 20.0), (0.6, 40.0)):
        sim.set_friction(mu)
        sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
        r = sim.execute(centred_grasp(sim), grip_force=f)
        assert r.held, (mu, f, r)
        sid_vals[(mu, f)] = r.min_wrench
    assert sid_vals[(0.2, 20.0)] < sid_vals[(0.6, 20.0)] <= sid_vals[(0.6, 40.0)] + 1e-9


def test_offset_grasp_pivots_more_than_centred(sim):
    sim.set_friction(0.3)
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    centred = sim.execute(centred_grasp(sim, 0.0), grip_force=8.0, probe=False)
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    offset = sim.execute(centred_grasp(sim, 0.025), grip_force=8.0, probe=False)
    assert centred.feasible and offset.feasible
    assert offset.pivot_deg > centred.pivot_deg + 2.0, (centred.pivot_deg, offset.pivot_deg)


def test_infeasible_when_gripper_hits_table(sim):
    sim.settle_object(np.random.default_rng(0), orientation=[0, 0, 0, 1])
    pos, R = sim.object_pose()
    # closing axis vertical: approach must be horizontal, palm ends up 4 cm below the table top... make it collide
    p1 = np.array([0.0, 0.0, -EXT[2] / 2]); p2 = np.array([0.0, 0.0, EXT[2] / 2])
    c = GraspCandidate(p1, np.array([0, 0, 1.0]), p2, np.array([0, 0, -1.0]), np.array([0, 0, 1.0]), EXT[2], 1.0)
    r = sim.execute(transform_candidate(c, R, pos), grip_force=10.0, probe=False)
    assert not r.feasible


def test_sampled_mesh_candidates_run_end_to_end(sim):
    mesh = trimesh.creation.box(extents=EXT)
    sim.set_friction(0.5)
    sim.settle_object(np.random.default_rng(1), orientation=[0, 0, 0, 1])
    pos, R = sim.object_pose()
    cands = sample_candidates(mesh, 10, np.random.default_rng(1))
    outcomes = [sim.execute(transform_candidate(c, R, pos), grip_force=15.0, probe=False) for c in cands]
    assert any(o.feasible for o in outcomes)


def test_reset_makes_settling_independent_of_history():
    sim = GraspSim(box_extents=[0.06, 0.04, 0.10], mass=0.3)
    try:
        sim.reset()
        pose_a = sim.settle_object(np.random.default_rng(7))
        sim.settle_object(np.random.default_rng(11))                     # something else happens in between
        sim.reset()
        pose_b = sim.settle_object(np.random.default_rng(7))
        assert np.allclose(pose_a[0], pose_b[0], atol=1e-9) and np.allclose(pose_a[1], pose_b[1], atol=1e-9)
    finally:
        sim.close()
