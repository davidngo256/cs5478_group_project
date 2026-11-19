"""Material heads: per-object class posteriors over the friction.py table classes.

Three heads share one interface (see `common.MaterialHead`):
  - dms46:      Apple DMS46 dense material segmenter (TorchScript), per-pixel posterior
                averaged over the object mask, remapped with DMS46_TO_TABLE.
  - clip_head:  open_clip ViT-B-32 zero-shot with CLIP_PROMPTS.
  - mobilenet:  torchvision MobileNetV3-Small fine-tuned on 10 MINC-2500 classes,
                temperature-scaled, remapped with MINC_TO_TABLE.
"""
