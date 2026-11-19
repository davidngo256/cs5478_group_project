import numpy as np
import pytest

from matgrasp.friction import (BIN_NAMES, DMS46_TO_TABLE, MATERIAL_TABLE, MINC_TO_TABLE,
                               MuDistribution, friction_bin, remap_probs, sample_true_mu)


def test_table_is_ordered_and_ranges_contain_nominal():
    for name, m in MATERIAL_TABLE.items():
        assert m.lo < m.nominal < m.hi, name


def test_point_distribution_quantiles():
    d = MuDistribution.point(0.4)
    assert d.quantile(0.1) == pytest.approx(0.4, abs=1e-3)
    assert d.mean() == pytest.approx(0.4, abs=1e-3)


def test_single_class_uniform_quantile():
    d = MuDistribution.from_class_probs({"glass": 1.0})
    g = MATERIAL_TABLE["glass"]
    assert d.quantile(0.0) == pytest.approx(g.lo)
    assert d.quantile(0.5) == pytest.approx(0.5 * (g.lo + g.hi), abs=1e-6)
    assert d.quantile(1.0) == pytest.approx(g.hi)


def test_mixture_quantile_is_pessimistic_under_ambiguity():
    # 55% glass / 45% plastic: low quantile sits in the glass range, mean sits between
    d = MuDistribution.from_class_probs({"glass": 0.55, "plastic": 0.45})
    q10 = d.quantile(0.10)
    assert MATERIAL_TABLE["glass"].lo <= q10 <= MATERIAL_TABLE["glass"].hi
    assert d.mean() > q10
    # cdf is monotone and reaches 1
    grid = np.linspace(0.0, 1.2, 200)
    c = d.cdf(grid)
    assert np.all(np.diff(c) >= -1e-12) and c[-1] == pytest.approx(1.0)


def test_true_mu_is_wider_than_table_but_centred():
    rng = np.random.default_rng(1)
    draws = np.array([sample_true_mu("plastic", rng) for _ in range(4000)])
    m = MATERIAL_TABLE["plastic"]
    assert abs(draws.mean() - m.nominal) < 0.01
    assert draws.min() < m.lo and draws.max() > m.hi      # deliberately outside the table range
    assert np.mean((draws >= m.lo) & (draws <= m.hi)) > 0.4


def test_friction_bins_cover_table():
    assert friction_bin(0.2) == "very low" and friction_bin(0.8) == "high"
    assert {friction_bin(m.nominal) for m in MATERIAL_TABLE.values()} == set(BIN_NAMES)


def test_remap_collapses_and_renormalises():
    p = remap_probs({"Plastic, clear": 0.3, "Plastic, non-clear": 0.2, "Glass": 0.4, "Sky": 0.1}, DMS46_TO_TABLE)
    assert p["plastic"] == pytest.approx(0.5 / 0.9)
    assert p["glass"] == pytest.approx(0.4 / 0.9)
    assert set(MINC_TO_TABLE.values()) <= set(MATERIAL_TABLE)
    assert set(DMS46_TO_TABLE.values()) <= set(MATERIAL_TABLE)
