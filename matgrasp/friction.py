"""Material -> friction coefficient. Nominal values are an assumption of the study:
static friction of common object surfaces against a rubber-faced gripper pad.
Ranges are stated as [lo, hi] and treated as uniform within the class.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MU_MIN, MU_MAX = 0.05, 1.2


@dataclass(frozen=True)
class MaterialMu:
    nominal: float
    lo: float
    hi: float


# object material class -> friction range against the pad (assumed, see proposal 3.1)
MATERIAL_TABLE: dict[str, MaterialMu] = {
    "glass":     MaterialMu(0.20, 0.12, 0.30),
    "metal":     MaterialMu(0.30, 0.20, 0.40),
    "ceramic":   MaterialMu(0.30, 0.20, 0.42),
    "plastic":   MaterialMu(0.35, 0.25, 0.48),
    "painted":   MaterialMu(0.40, 0.30, 0.50),
    "wood":      MaterialMu(0.50, 0.40, 0.62),
    "paper":     MaterialMu(0.50, 0.40, 0.62),     # includes cardboard
    "leather":   MaterialMu(0.55, 0.45, 0.65),
    "fabric":    MaterialMu(0.60, 0.50, 0.72),
    "foam":      MaterialMu(0.75, 0.60, 0.90),
    "rubber":    MaterialMu(0.80, 0.65, 0.95),
}

# five friction bins spanning the table; used for per-bin reporting
BIN_EDGES = np.array([0.0, 0.25, 0.33, 0.45, 0.65, 1.3])
BIN_NAMES = ["very low", "low", "mid", "mid-high", "high"]


def friction_bin(mu: float) -> str:
    return BIN_NAMES[int(np.clip(np.searchsorted(BIN_EDGES, mu, side="right") - 1, 0, len(BIN_NAMES) - 1))]


class MuDistribution:
    """Mixture of uniform components over mu, induced by class probabilities."""

    def __init__(self, weights, los, his):
        w = np.asarray(weights, float)
        assert w.size and np.all(w >= 0) and w.sum() > 0
        self.w = w / w.sum()
        self.lo = np.asarray(los, float)
        self.hi = np.asarray(his, float)
        assert np.all(self.hi > self.lo)

    @classmethod
    def from_class_probs(cls, probs: dict[str, float], table: dict[str, MaterialMu] = MATERIAL_TABLE):
        items = [(p, table[c]) for c, p in probs.items() if p > 0 and c in table]
        if not items:
            raise ValueError("no material class with positive probability found in table")
        return cls([p for p, _ in items], [m.lo for _, m in items], [m.hi for _, m in items])

    @classmethod
    def point(cls, mu: float, width: float = 1e-4):
        return cls([1.0], [mu - width], [mu + width])

    def cdf(self, mu):
        mu = np.asarray(mu, float)[..., None]
        return np.sum(self.w * np.clip((mu - self.lo) / (self.hi - self.lo), 0.0, 1.0), axis=-1)

    def mean(self) -> float:
        return float(np.sum(self.w * 0.5 * (self.lo + self.hi)))

    def quantile(self, q: float) -> float:
        """q-th quantile by bisection on the piecewise-linear CDF."""
        assert 0.0 <= q <= 1.0
        a, b = float(self.lo.min()), float(self.hi.max())
        if q <= 0.0:
            return a
        if q >= 1.0:
            return b
        for _ in range(60):
            m = 0.5 * (a + b)
            if self.cdf(m) < q:
                a = m
            else:
                b = m
        return 0.5 * (a + b)


def sample_true_mu(material: str, rng: np.random.Generator, widen: float = 1.5,
                   table: dict[str, MaterialMu] = MATERIAL_TABLE) -> float:
    """Ground-truth mu for one trial: normal around the nominal value, with a standard
    deviation `widen` times the table's half-range, so the truth is not a copy of the table."""
    m = table[material]
    sd = widen * 0.5 * (m.hi - m.lo)
    return float(np.clip(rng.normal(m.nominal, sd), MU_MIN, MU_MAX))


# --- mapping other vocabularies onto the material table -----------------------------------

# MINC-2500 classes kept for the object head, and the table class they map to
MINC_TO_TABLE = {
    "ceramic": "ceramic", "fabric": "fabric", "glass": "glass", "leather": "leather",
    "metal": "metal", "paper": "paper", "plastic": "plastic", "polishedstone": "ceramic",
    "wood": "wood", "painted": "painted",
}

# Apple DMS46 names (see taxonomy.json) -> table class; classes not listed are ignored
DMS46_TO_TABLE = {
    "Glass": "glass", "Mirror": "glass", "Metal": "metal", "Ceramic": "ceramic",
    "Stone, polished": "ceramic", "Engineered stone": "ceramic", "Gemstone/quartz": "glass",
    "Plastic, clear": "plastic", "Plastic, non-clear": "plastic", "Paint/plaster/enamel": "painted",
    "Wood": "wood", "Cardboard": "paper", "Paper": "paper", "Photograph/painting": "paper",
    "Leather": "leather", "Fabric/cloth": "fabric", "Carpet/rug": "fabric", "Wicker": "wood",
    "Rubber/latex": "rubber", "Wax": "plastic", "Cork/corkboard": "foam",
}

# prompts for the zero-shot CLIP head, one per table class
CLIP_PROMPTS = {
    "glass": "a photo of an object made of glass",
    "metal": "a photo of an object made of bare metal",
    "ceramic": "a photo of an object made of ceramic",
    "plastic": "a photo of an object made of plastic",
    "painted": "a photo of a painted object",
    "wood": "a photo of an object made of wood",
    "paper": "a photo of an object made of cardboard or paper",
    "leather": "a photo of an object made of leather",
    "fabric": "a photo of an object made of fabric",
    "foam": "a photo of an object made of foam",
    "rubber": "a photo of an object made of rubber",
}


def remap_probs(probs: dict[str, float], mapping: dict[str, str]) -> dict[str, float]:
    """Collapse a model's class posterior onto table classes and renormalise."""
    out: dict[str, float] = {}
    for cls, p in probs.items():
        if cls in mapping:
            out[mapping[cls]] = out.get(mapping[cls], 0.0) + float(p)
    tot = sum(out.values())
    if tot <= 0:
        raise ValueError("no probability mass on mapped classes")
    return {k: v / tot for k, v in out.items()}
