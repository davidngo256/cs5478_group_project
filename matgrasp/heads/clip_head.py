"""CLIP head: open_clip ViT-B-32 zero-shot over the table classes with CLIP_PROMPTS.
The image is the object crop (mask bbox +10%, background left as-is) passed through the
model's own preprocessing (resize 224 + centre crop); logits = logit_scale * cos(image,
text), softmax over the eleven table-class prompts.
"""
from __future__ import annotations

import json

import numpy as np
from PIL import Image

from ..friction import CLIP_PROMPTS
from . import common, ycb_photos

MODEL_NAME = "ViT-B-32"
PRETRAINED_TAGS = ("laion2b_s34b_b79k", "openai")
CACHE_DIR = common.MODELS_DIR / "open_clip"


def build_prompts(prompts: dict[str, str] = CLIP_PROMPTS, classes: list[str] = common.TABLE_CLASSES):
    """(classes, prompt texts) in table order; every table class must have a prompt."""
    missing = [c for c in classes if c not in prompts]
    if missing:
        raise KeyError(f"no CLIP prompt for {missing}")
    return list(classes), [prompts[c] for c in classes]


class ClipHead:
    name = "clip"

    def __init__(self, model_name: str = MODEL_NAME, pretrained=PRETRAINED_TAGS, threads: int | None = None,
                 expand: float = 0.10):
        # threads: torch's default (the physical core count) unless overridden; see MobileNetHead
        import open_clip
        import torch

        if threads:
            torch.set_num_threads(threads)
        self.device = common.device()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        err = None
        for tag in ([pretrained] if isinstance(pretrained, str) else pretrained):
            try:
                self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                    model_name, pretrained=tag, cache_dir=str(CACHE_DIR))
                self.pretrained = tag
                break
            except Exception as e:  # download failure -> next tag
                err = e
                print(f"[clip] pretrained={tag} failed: {e!r}", flush=True)
        else:
            raise RuntimeError(f"could not load any CLIP weights: {err!r}")
        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.classes, self.prompts = build_prompts()
        with torch.no_grad():
            t = self.model.encode_text(self.tokenizer(self.prompts).to(self.device))
            self.text = t / t.norm(dim=-1, keepdim=True)
            self.scale = float(self.model.logit_scale.exp().item())
        self.expand = expand

    def logits(self, pil: Image.Image) -> np.ndarray:
        import torch

        with torch.no_grad():
            x = self.preprocess(pil).unsqueeze(0).to(self.device)
            f = self.model.encode_image(x)
            f = f / f.norm(dim=-1, keepdim=True)
            return (self.scale * f @ self.text.T)[0].cpu().numpy()

    def predict(self, img: np.ndarray, mask: np.ndarray) -> dict[str, float]:
        crop, _ = ycb_photos.object_crop(img, mask, self.expand)
        p = common.softmax(self.logits(Image.fromarray(crop))[None])[0]
        return common.full_table_probs(dict(zip(self.classes, p.tolist())))

    def forward_one(self, pair):
        img, mask = pair
        return self.predict(img, mask)


def main():
    import sys

    head = ClipHead()
    if sys.argv[1:] == ["latency"]:
        print(json.dumps(common.remeasure_latency(head)))
        return
    lat = common.first_views(20)
    summary = common.run_head(head, latency_inputs=lat,
                              extra_summary={"model": MODEL_NAME, "pretrained": head.pretrained,
                                             "logit_scale": head.scale, "prompts": dict(zip(head.classes, head.prompts)),
                                             "input": "object crop (mask bbox +10%), CLIP preprocess 224"})
    print(json.dumps({k: v for k, v in summary.items() if k != "ycb"}, indent=1))
    print(json.dumps(summary["ycb"], indent=1))


if __name__ == "__main__":
    main()
