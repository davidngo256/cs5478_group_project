import numpy as np

from matgrasp.analysis import paired_diff
from matgrasp.experiment import Config, cells_for, force_cap
from matgrasp.friction import MATERIAL_TABLE
from matgrasp.ycb import OBJECTS


def test_force_cap_is_within_bounds_and_scales_with_mass():
    cfg = Config()
    caps = {o: force_cap(o, cfg) for o in OBJECTS}
    assert all(cfg.cap_min <= c <= cfg.cap_max for c in caps.values())
    assert caps["021_bleach_cleanser"] >= caps["006_mustard_bottle"] > caps["003_cracker_box"] > caps["061_foam_brick"]


def test_cells_cover_2x2_and_use_true_mu():
    cfg = Config(sweep=False)
    cells = dict((n, (a, b)) for n, a, b in cells_for(0.27, "plastic", cfg, heads={"h": {"glass": 0.6, "plastic": 0.4}}))
    assert cells["baseline"] == (0.5, 0.5)
    assert cells["squeeze"] == (0.5, 0.27) and cells["select"] == (0.27, 0.5) and cells["oracle"] == (0.27, 0.27)
    lo, hi = MATERIAL_TABLE["plastic"].lo, MATERIAL_TABLE["plastic"].hi
    assert lo <= cells["table_q"][0] < cells["table_mean"][0] <= hi
    assert cells["head:h"][0] < cells["head:h:mean"][0]
    assert cells["table_squeeze"] == (0.5, cells["table_q"][1])          # baseline grasp, table-quantile force
    assert cells["head:h:squeeze"] == (0.5, cells["head:h"][1])          # baseline grasp, head-quantile force
    assert cells["head:h"][0] < MATERIAL_TABLE["glass"].hi        # pessimistic quantile lands in the glass range
    assert not any(n.startswith("sweep") for n in cells)
    assert any(n.startswith("sweep") for n, _, _ in cells_for(0.3, "plastic", Config()))


def test_paired_diff_recovers_shift():
    rng = np.random.default_rng(0)
    a = {k: float(v) for k, v in enumerate(rng.normal(1.0, 1.0, 400))}
    b = {k: a[k] - 0.3 + rng.normal(0, 0.05) for k in a}
    d, (lo, hi), n = paired_diff(a, b)
    assert n == 400 and abs(d - 0.3) < 0.02 and lo < 0.3 < hi
