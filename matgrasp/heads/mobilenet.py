"""MobileNetV3-Small head: torchvision ImageNet weights fine-tuned on the ten MINC-2500
classes in friction.MINC_TO_TABLE, temperature-scaled on the MINC validation split.
Inference: object crop (mask bbox +10%) -> resize 256 / centre crop 224 -> logits / T ->
softmax over the 10 MINC classes -> remap_probs(MINC_TO_TABLE) (foam/rubber get 0).

`python -m matgrasp.heads.mobilenet train` fine-tunes and calibrates (39 s on an NVIDIA GB10, 2.3 min on an L4);
`python -m matgrasp.heads.mobilenet` evaluates the saved weights on the YCB photos.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

from ..friction import MINC_TO_TABLE, remap_probs
from . import common, minc, ycb_photos

WEIGHTS_PATH = common.MODELS_DIR / "mobilenet_minc.pt"
TRAIN_LOG = common.RESULTS_DIR / "mobilenet_train.log"
MINC_METRICS = common.RESULTS_DIR / "mobilenet_minc.json"
CLASSES = minc.MINC_CLASSES  # 10 MINC class names, sorted; training label = index


def build_model(n_classes: int = len(CLASSES), pretrained: bool = True):
    import torch
    import torchvision

    w = torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1 if pretrained else None
    m = torchvision.models.mobilenet_v3_small(weights=w)
    m.classifier[3] = torch.nn.Linear(m.classifier[3].in_features, n_classes)
    return m


def transforms(train: bool):
    import torchvision.transforms as T

    norm = T.Normalize(common.IMAGENET_MEAN.tolist(), common.IMAGENET_STD.tolist())
    if train:
        return T.Compose([T.RandomResizedCrop(224, scale=(0.35, 1.0)), T.RandomHorizontalFlip(),
                          T.ColorJitter(0.2, 0.2, 0.2), T.ToTensor(), norm])
    return T.Compose([T.Resize(256), T.CenterCrop(224), T.ToTensor(), norm])


class MincDataset:
    def __init__(self, entries: list[dict], train: bool):
        self.entries = entries
        self.tf = transforms(train)

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, i):
        e = self.entries[i]
        img = Image.open(minc.MINC_DIR / e["file"]).convert("RGB")
        return self.tf(img), CLASSES.index(e["label"])


def split_logits(model, entries: list[dict], batch: int = 128, workers: int = 2, device: str = "cpu"):
    """(logits [N,10], labels [N]) of a split under the eval transform."""
    import torch

    dl = torch.utils.data.DataLoader(MincDataset(entries, False), batch_size=batch, num_workers=workers)
    zs, ys = [], []
    model.eval()
    with torch.no_grad():
        for x, y in dl:
            zs.append(model(x.to(device)).cpu().numpy())
            ys.append(y.numpy())
    return np.concatenate(zs), np.concatenate(ys)


def calibration_report(logits: np.ndarray, labels: np.ndarray, T: float, n_bins: int = 15) -> dict:
    p0, p1 = common.softmax(logits), common.softmax(logits, T)
    nll = lambda p: float(-np.log(np.clip(p[np.arange(len(labels)), labels], 1e-12, 1)).mean())
    return {"accuracy": float((logits.argmax(1) == labels).mean()),
            "ece_before": common.ece_score(p0, labels, n_bins), "ece_after": common.ece_score(p1, labels, n_bins),
            "nll_before": nll(p0), "nll_after": nll(p1), "n": int(len(labels))}


def train(per_class: int = 600, epochs: int = 8, batch: int = 64, lr: float = 6e-4, wd: float = 0.01,
          seed: int = 0, threads: int | None = None, workers: int = 4) -> dict:
    """Fine-tune on common.device() (CUDA when available, else CPU). `threads` overrides torch's
    CPU thread pool; its default (the physical core count) is the right one, oversubscribing the
    cores slows the CPU-side work several-fold. `workers` are the DataLoader processes, the
    bottleneck once the forward runs on a GPU."""
    import torch

    dev = common.device()
    torch.manual_seed(seed)
    if threads:
        torch.set_num_threads(threads)
    common.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log = open(TRAIN_LOG, "w")

    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    tr_all, va, te = minc.load_index("train"), minc.load_index("validation"), minc.load_index("test")
    tr = minc.subsample(tr_all, per_class, seed)
    say(f"MINC-2500 split 1, classes={CLASSES}")
    say(f"train {len(tr)} (subsampled {per_class}/class from {len(tr_all)}), val {len(va)}, test {len(te)}")
    say(f"epochs={epochs} batch={batch} lr={lr} wd={wd} seed={seed} threads={torch.get_num_threads()} workers={workers} "
        f"device={dev} ({common.device_name(dev)})")

    model = build_model().to(dev)
    say(f"params={common.count_params(model)}")
    dl = torch.utils.data.DataLoader(MincDataset(tr, True), batch_size=batch, shuffle=True,
                                     num_workers=workers, drop_last=True, persistent_workers=workers > 0,
                                     pin_memory=dev.startswith("cuda"))
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    total = epochs * len(dl)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=total, pct_start=0.15)
    t_start = time.time()
    for ep in range(epochs):
        model.train()
        t0, n, loss_sum, ok = time.time(), 0, 0.0, 0
        for i, (x, y) in enumerate(dl):
            x, y = x.to(dev, non_blocking=True), y.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            z = model(x)
            loss = torch.nn.functional.cross_entropy(z, y)
            loss.backward()
            opt.step()
            sched.step()
            n += len(y)
            loss_sum += float(loss) * len(y)
            ok += int((z.argmax(1) == y).sum())
            if (i + 1) % 20 == 0:
                say(f"  ep {ep + 1} step {i + 1}/{len(dl)} loss {loss_sum / n:.3f} acc {ok / n:.3f} "
                    f"lr {sched.get_last_lr()[0]:.2e} {time.time() - t0:.0f}s")
        zv, yv = split_logits(model, va, workers=workers, device=dev)
        va_acc = float((zv.argmax(1) == yv).mean())
        say(f"epoch {ep + 1}/{epochs}: train loss {loss_sum / n:.3f} acc {ok / n:.3f} | val acc {va_acc:.3f} "
            f"| {time.time() - t0:.0f}s (total {time.time() - t_start:.0f}s)")

    # temperature scaling on validation, evaluation on the full test split
    zv, yv = split_logits(model, va, workers=workers, device=dev)
    T = common.fit_temperature(zv, yv)
    zt, yt = split_logits(model, te, workers=workers, device=dev)
    val_rep, test_rep = calibration_report(zv, yv, T), calibration_report(zt, yt, T)
    pt = common.softmax(zt, T)
    table_true = [MINC_TO_TABLE[CLASSES[i]] for i in yt]
    table_pred = [common.top1(remap_probs(dict(zip(CLASSES, p)), MINC_TO_TABLE)) for p in pt]
    table_classes = sorted(set(MINC_TO_TABLE.values()), key=common.TABLE_CLASSES.index)
    cm = common.confusion_matrix(table_true, table_pred, table_classes)
    cm_minc = common.confusion_matrix([CLASSES[i] for i in yt], [CLASSES[i] for i in zt.argmax(1)], CLASSES)
    per_class_acc = {c: float((zt.argmax(1)[yt == i] == i).mean()) for i, c in enumerate(CLASSES)}
    metrics = {"temperature": T, "validation": val_rep, "test": test_rep,
               "test_accuracy_table_classes": float(np.mean([a == b for a, b in zip(table_true, table_pred)])),
               "test_per_class_accuracy": per_class_acc,
               "confusion_matrix_table": cm, "confusion_matrix_minc": cm_minc,
               "train_images": len(tr), "epochs": epochs, "batch": batch, "lr": lr,
               "train_time_s": time.time() - t_start, "classes": CLASSES,
               "device": dev, "device_name": common.device_name(dev)}
    say(f"temperature T={T:.3f}")
    say(f"validation: {json.dumps(val_rep)}")
    say(f"test: {json.dumps(test_rep)}")
    say(f"test per-class acc: {json.dumps(per_class_acc)}")
    say(f"total time {time.time() - t_start:.0f}s")
    log.close()
    WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": {k: v.cpu() for k, v in model.state_dict().items()}, "classes": CLASSES,
                "temperature": T}, WEIGHTS_PATH)
    common.write_json(MINC_METRICS, metrics)
    return metrics


class MobileNetHead:
    name = "mobilenet"

    def __init__(self, weights: Path = WEIGHTS_PATH, threads: int | None = None, expand: float = 0.10):
        # threads: torch's default (the physical core count) unless overridden. Oversubscribing the
        # cores (4 threads on a 2-core box, 8 on a shared 8-vCPU box) made batch-1 inference several
        # times slower and much noisier, on the GPU too, since cropping and resizing stay on the CPU.
        import torch

        if threads:
            torch.set_num_threads(threads)
        self.device = common.device()
        ck = torch.load(weights, map_location="cpu")
        self.classes = list(ck["classes"])
        self.model = build_model(len(self.classes), pretrained=False)
        self.model.load_state_dict(ck["state_dict"])
        self.model = self.model.to(self.device).eval()
        self.T = float(ck["temperature"])
        self.tf = transforms(False)
        self.expand = expand

    def logits(self, pil: Image.Image) -> np.ndarray:
        import torch

        with torch.no_grad():
            return self.model(self.tf(pil).unsqueeze(0).to(self.device))[0].cpu().numpy()

    def predict_raw(self, img: np.ndarray, mask: np.ndarray) -> dict[str, float]:
        crop, _ = ycb_photos.object_crop(img, mask, self.expand)
        p = common.softmax(self.logits(Image.fromarray(crop))[None], self.T)[0]
        return dict(zip(self.classes, p.tolist()))

    def predict(self, img: np.ndarray, mask: np.ndarray) -> dict[str, float]:
        return common.full_table_probs(remap_probs(self.predict_raw(img, mask), MINC_TO_TABLE))

    def forward_one(self, pair):
        img, mask = pair
        return self.predict(img, mask)


def main(argv):
    if argv[:1] == ["train"]:
        train()
        return
    head = MobileNetHead()
    if argv[:1] == ["latency"]:
        print(json.dumps(common.remeasure_latency(head)))
        return
    metrics = json.loads(MINC_METRICS.read_text()) if MINC_METRICS.exists() else {}
    extra = {"input": "object crop (mask bbox +10%), resize 256 / centre crop 224",
             "temperature": head.T, "minc_classes": head.classes,
             "minc_test_accuracy": metrics.get("test", {}).get("accuracy"),
             "minc_test_accuracy_table_classes": metrics.get("test_accuracy_table_classes"),
             "ece_before": metrics.get("test", {}).get("ece_before"),
             "ece_after": metrics.get("test", {}).get("ece_after"),
             "ece_validation_before": metrics.get("validation", {}).get("ece_before"),
             "ece_validation_after": metrics.get("validation", {}).get("ece_after"),
             "confusion_matrix_table": metrics.get("confusion_matrix_table"),
             "minc_training": {k: metrics.get(k) for k in ("train_images", "epochs", "batch", "lr", "train_time_s",
                                                          "device", "device_name")},
             "minc_test_per_class_accuracy": metrics.get("test_per_class_accuracy")}
    summary = common.run_head(head, latency_inputs=common.first_views(20), extra_summary=extra)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("ycb", "confusion_matrix_table")}, indent=1))
    print(json.dumps(summary["ycb"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
