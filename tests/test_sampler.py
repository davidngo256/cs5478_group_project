import numpy as np
import pytest
import trimesh

from matgrasp.sampler import PANDA_MAX_WIDTH, sample_candidates, transform_candidate
from matgrasp.wrench import evaluate_grasp


@pytest.fixture(scope="module")
def box():
    return trimesh.creation.box(extents=[0.06, 0.10, 0.15])


def test_candidates_lie_on_surface_and_fit_gripper(box):
    rng = np.random.default_rng(0)
    cands = sample_candidates(box, 50, rng)
    assert len(cands) == 50
    closest, dist, _ = trimesh.proximity.closest_point(box, np.array([c.p1 for c in cands]))
    assert np.all(dist < 1e-3)
    closest, dist, _ = trimesh.proximity.closest_point(box, np.array([c.p2 for c in cands]))
    assert np.all(dist < 1e-3)
    for c in cands:
        assert 0.004 <= c.width <= PANDA_MAX_WIDTH
        assert np.isclose(np.linalg.norm(c.axis), 1.0)
        assert np.isclose(c.width, np.linalg.norm(c.p2 - c.p1), atol=1e-6)
        # normals are inward: pointing from the contact towards the interior (towards the other contact)
        assert c.n1 @ c.axis > 0 and c.n2 @ c.axis < 0
        assert c.misalignment_deg() <= 25.0 + 1e-6


def test_box_grasps_only_across_thin_dimensions(box):
    # the 15 cm dimension exceeds the gripper, so no candidate closes along z
    rng = np.random.default_rng(1)
    cands = sample_candidates(box, 80, rng)
    assert all(abs(c.axis[2]) < 0.6 for c in cands)


def test_mix_of_good_and_bad_grasps(box):
    rng = np.random.default_rng(2)
    cands = sample_candidates(box, 100, rng)
    eps = np.array([evaluate_grasp(c.contacts, 0.3, np.zeros(3), 0.075).epsilon for c in cands])
    assert 0.1 < np.mean(eps > 0) < 0.95      # neither all force-closure nor none


def test_seed_reproducible(box):
    a = sample_candidates(box, 10, np.random.default_rng(7))
    b = sample_candidates(box, 10, np.random.default_rng(7))
    assert all(np.allclose(x.p1, y.p1) and np.allclose(x.p2, y.p2) for x, y in zip(a, b))


def test_transform_preserves_geometry(box):
    c = sample_candidates(box, 1, np.random.default_rng(3))[0]
    R = trimesh.transformations.rotation_matrix(0.7, [0.3, 0.5, 0.8])[:3, :3]
    t = np.array([0.1, -0.2, 0.3])
    d = transform_candidate(c, R, t)
    assert np.isclose(d.width, c.width)
    assert np.isclose(np.linalg.norm(d.p2 - d.p1), c.width)
    assert np.isclose(d.n1 @ d.axis, c.n1 @ c.axis)
