"""DMS46 head: Apple's dense material segmenter (Upchurch & Niu, ECCV 2022), TorchScript
`DMS46_v1.pt`. The scripted forward() returns only the per-pixel argmax, so we call the
encoder/decoder submodules to get the 46-way logits (verified: their argmax equals the
official output). Preprocessing follows the official inference.py: scale so the longer
side is 512 (LANCZOS), ImageNet mean/std on the 0-255 range. Per pixel softmax over the
46 logits, averaged over the object-mask pixels, then remapped with DMS46_TO_TABLE.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from ..friction import DMS46_TO_TABLE, remap_probs
from . import common, ycb_photos

# indices into taxonomy.json "names" of the 46 trained classes (from the official inference.py)
DMS46_INDICES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 23,
                 24, 26, 27, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 41, 43, 44, 46, 47, 48, 49,
                 50, 51, 52, 53, 56]
MODEL_PATH = common.MODELS_DIR / "DMS46_v1.pt"
TAXONOMY_PATH = common.MODELS_DIR / "dms_taxonomy.json"


def class_names(taxonomy_path: Path = TAXONOMY_PATH) -> list[str]:
    names = json.loads(Path(taxonomy_path).read_text())["names"]
    return [names[i] for i in DMS46_INDICES]


def preprocess(img: np.ndarray, new_dim: int = 512):
    """Official resize (longer side -> new_dim, ceil) and normalisation; returns [1,3,H,W]."""
    import torch

    h, w = img.shape[:2]
    scale = min(new_dim / h, new_dim / w)
    new_h, new_w = math.ceil(scale * h), math.ceil(scale * w)
    x = np.asarray(Image.fromarray(img).resize((new_w, new_h), Image.LANCZOS), np.float32)
    x = (x - common.IMAGENET_MEAN * 255.0) / (common.IMAGENET_STD * 255.0)
    return torch.from_numpy(x.transpose(2, 0, 1)).unsqueeze(0)


class DMS46Head:
    name = "dms46"

    def __init__(self, model_path: Path = MODEL_PATH, crop: bool = True, expand: float = 0.10,
                 threads: int | None = None):
        # threads: torch's default (the physical core count) unless overridden; see MobileNetHead
        import torch

        if threads:
            torch.set_num_threads(threads)
        self.device = common.device()
        self.model = torch.jit.load(str(model_path), map_location=self.device).eval()
        self.classes = class_names()
        assert len(self.classes) == 46
        missing = [c for c in DMS46_TO_TABLE if c not in self.classes]
        assert not missing, f"DMS46_TO_TABLE names not in taxonomy: {missing}"
        self.crop = crop
        self.expand = expand

    def logits(self, x):
        """[46, H, W] logits for a preprocessed [1,3,H,W] tensor."""
        feats = self.model.encoder(x)
        return self.model.decoder(feats, int(x.shape[2]), int(x.shape[3]))[0]

    def posterior(self, img: np.ndarray) -> np.ndarray:
        """Per-pixel softmax posterior [46, H', W'] at the network's working resolution."""
        import torch

        with torch.no_grad():
            z = self.logits(preprocess(img).to(self.device))
            return torch.softmax(z, dim=0).cpu().numpy()

    def predict_raw(self, img: np.ndarray, mask: np.ndarray) -> dict[str, float]:
        """46-class posterior averaged over the (resized) object mask. The average is taken on the
        device and only the 46 class means are copied back: copying the 11-44 MB per-pixel posterior
        to the host (what `posterior()` does) cost 0.2-380 ms per image on a unified-memory GB10,
        more than the forward pass and wildly variable, where the L4 did it in a few ms."""
        import torch

        if self.crop:
            img, mask = ycb_photos.object_crop(img, mask, self.expand)
        with torch.no_grad():
            z = self.logits(preprocess(img).to(self.device))
            post = torch.softmax(z, dim=0)
            m = common.resize_mask(mask, int(post.shape[1]), int(post.shape[2]))
            if not m.any():                       # same fallback as common.mask_average
                m = np.ones_like(m)
            sel = torch.from_numpy(m).to(post.device)
            avg = post[:, sel].double().mean(dim=1).cpu().numpy()
        return dict(zip(self.classes, avg.tolist()))

    def predict(self, img: np.ndarray, mask: np.ndarray) -> dict[str, float]:
        return common.full_table_probs(remap_probs(self.predict_raw(img, mask), DMS46_TO_TABLE))

    def forward_one(self, pair):
        img, mask = pair
        return self.predict(img, mask)


def main():
    import sys

    head = DMS46Head()
    if sys.argv[1:] == ["latency"]:
        print(json.dumps(common.remeasure_latency(head)))
        return
    lat = common.first_views(20)
    summary = common.run_head(head, latency_inputs=lat,
                              extra_summary={"input": "object crop (mask bbox +10%), longer side 512",
                                             "mapping": "DMS46_TO_TABLE, unmapped DMS classes dropped"})
    print(json.dumps({k: v for k, v in summary.items() if k != "ycb"}, indent=1))
    print(json.dumps(summary["ycb"], indent=1))


if __name__ == "__main__":
    main()
