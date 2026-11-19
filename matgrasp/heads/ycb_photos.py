"""Real YCB photographs for the material heads: streamed download of a small subset of
views (plus object masks where the archive has them), mask loading and object crops.

Berkeley RGB-D archives: <obj>/NP<cam>_<angle>.jpg with masks <obj>/masks/NP<cam>_<angle>_mask.pbm
(025_mug's "rgbd" archive instead holds N<cam>_<angle>.jpg + masks/N<cam>_<angle>_mask.pbm).
028_skillet_lid has no RGB-D archive; its high-res RGB archive (N<cam>_<angle>.jpg) has
no masks, so a mask is derived from the image (see `derive_mask`).
"""
from __future__ import annotations

import re
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

from ..ycb import DATA_DIR, YCB_BASE

PHOTO_DIR = DATA_DIR / "ycb_photos"
CAMERAS = (1, 2, 3)
ANGLES = tuple(range(0, 360, 45))          # 8 angles x 3 cameras = 24 views per object
HIGHRES_ONLY = {"028_skillet_lid"}          # objects without an RGB-D archive
VIEW_RE = re.compile(r"^(NP?|R)(\d)_(\d+)$")   # NP1_45 (rgbd), N1_45 (highres), R1_45 (render fallback)


def is_render(name: str) -> bool:
    """True for a render-fallback view file name (R<cam>_<angle>...)."""
    return Path(name).name.startswith("R") and VIEW_RE.match(Path(name).name.split(".", 1)[0].removesuffix("_mask")) is not None


def archive_url(obj_id: str) -> str:
    if obj_id in HIGHRES_ONLY:
        return f"{YCB_BASE}/berkeley/{obj_id}/{obj_id}_berkeley_rgb_highres.tgz"
    return f"{YCB_BASE}/berkeley/{obj_id}/{obj_id}_berkeley_rgbd.tgz"


def view_stems(obj_id: str, cameras=CAMERAS, angles=ANGLES) -> list[str]:
    """Wanted view stems. RGB-D archives use NP<cam>_<angle>; high-res archives (and some
    'rgbd' archives, e.g. 025_mug, which actually hold high-res N<cam>_<angle>.jpg files with
    masks) use N<cam>_<angle>, so both prefixes are requested for RGB-D objects."""
    prefixes = ("N",) if obj_id in HIGHRES_ONLY else ("NP", "N")
    return [f"{p}{c}_{a}" for p in prefixes for c in cameras for a in angles]


def wanted_member(name: str, stems: set[str]) -> bool:
    """True for the jpg of a wanted view or its mask (any extension/suffix `_mask`)."""
    base = Path(name).name
    stem = base.split(".", 1)[0]
    if stem.endswith("_mask"):
        stem = stem[: -len("_mask")]
    if stem not in stems:
        return False
    return base.lower().endswith((".jpg", ".jpeg", ".png", ".pbm", ".pgm"))


def photo_dir(obj_id: str) -> Path:
    return PHOTO_DIR / obj_id


def fetch_ycb_photos(obj_id: str, retries: int = 3, verbose: bool = True) -> Path:
    """Stream the archive and keep only the wanted views (never stores the tgz on disk).
    Writes `_listing.txt` (all member names, for inspection) and `_done` when complete."""
    out = photo_dir(obj_id)
    if (out / "_done").exists():
        return out
    out.mkdir(parents=True, exist_ok=True)
    stems = set(view_stems(obj_id))
    url = archive_url(obj_id)
    for attempt in range(1, retries + 1):
        t0 = time.time()
        names: list[str] = []
        kept = 0
        try:
            if verbose:
                print(f"[{obj_id}] streaming {url} (attempt {attempt})", flush=True)
            with urllib.request.urlopen(url, timeout=120) as resp:
                with tarfile.open(fileobj=resp, mode="r|gz") as tf:
                    for m in tf:
                        names.append(m.name)
                        if m.isfile() and wanted_member(m.name, stems):
                            f = tf.extractfile(m)
                            assert f is not None
                            (out / Path(m.name).name).write_bytes(f.read())
                            kept += 1
            (out / "_listing.txt").write_text("\n".join(names) + "\n")
            (out / "_done").write_text(f"{url}\nkept={kept}\nmembers={len(names)}\n")
            if verbose:
                print(f"[{obj_id}] kept {kept} files of {len(names)} members in {time.time() - t0:.0f}s", flush=True)
            return out
        except Exception as e:  # network hiccup: restart the stream
            print(f"[{obj_id}] attempt {attempt} failed after {time.time() - t0:.0f}s: {e!r}", flush=True)
            missing = isinstance(e, urllib.error.HTTPError) and e.code == 404   # no such archive: do not retry
            if attempt == retries or missing:
                raise
            time.sleep(10)
    return out


# --- listing views on disk --------------------------------------------------------------

def parse_view_files(names: list[str]) -> dict[str, dict[str, str]]:
    """Group file names into views: {"NP1_0": {"image": "NP1_0.jpg", "mask": "NP1_0_mask.pbm"}}.
    Pure function so it can be unit-tested without data."""
    views: dict[str, dict[str, str]] = {}
    for n in sorted(names):
        stem, dot, ext = n.partition(".")
        if not dot:
            continue
        is_mask = stem.endswith("_mask")
        key = stem[: -len("_mask")] if is_mask else stem
        if not VIEW_RE.match(key):
            continue
        if is_mask:
            views.setdefault(key, {})["mask"] = n
        elif ext.lower() in ("jpg", "jpeg", "png"):
            views.setdefault(key, {})["image"] = n
    return {k: v for k, v in views.items() if "image" in v}


def sort_key(stem: str):
    m = VIEW_RE.match(stem)
    return (int(m.group(2)), int(m.group(3))) if m else (99, 0)


def list_views(obj_id: str) -> list[tuple[Path, Path | None]]:
    """[(image_path, mask_path_or_None)] for the views on disk, camera-major order. Empty
    unless the directory is complete (`_done` from the fetch or `_rendered` from the renderer),
    so a download in progress is never evaluated."""
    d = photo_dir(obj_id)
    if not d.exists() or not ((d / "_done").exists() or (d / "_rendered").exists()):
        return []
    views = parse_view_files([p.name for p in d.iterdir() if p.is_file()])
    # if an archive had both NP<cam>_<angle> and N<cam>_<angle> for a view, keep the RGB-D one
    views = {k: v for k, v in views.items() if not (k.startswith("N") and not k.startswith("NP") and ("NP" + k[1:]) in views)}
    out = []
    for k in sorted(views, key=sort_key):
        v = views[k]
        out.append((d / v["image"], d / v["mask"] if "mask" in v else None))
    return out


# --- masks and crops --------------------------------------------------------------------

def load_mask(path: Path, clean: bool = True) -> np.ndarray:
    """Boolean object mask (True = object). YCB .pbm masks store the object as black (0)
    on a white background, which PIL reads as False/True, so we invert; if the polarity
    looks wrong (object covering more than half the frame) we flip so the minority is the
    object. With `clean`, stray blobs are removed (see `clean_mask`)."""
    m = np.asarray(Image.open(path).convert("1"))
    obj = ~m
    if obj.mean() > 0.5:
        obj = ~obj
    return clean_mask(obj) if clean else obj


def clean_mask(mask: np.ndarray, gap: int = 5) -> np.ndarray:
    """Keep the connected component of the mask with the largest area, where components
    separated by gaps of up to about 2*gap pixels count as connected (so a handle or shackle
    stays with its body). The YCB archive masks of small objects (e.g. 038_padlock) contain
    stray blobs from turntable reflections far from the object; without this the mask
    bounding box and the mask average both include them. The returned mask is a subset of
    the input (the closing is only used to decide connectivity)."""
    from scipy import ndimage

    mask = np.asarray(mask, bool)
    if not mask.any():
        return mask
    joined = ndimage.binary_closing(mask, iterations=gap) | mask
    lab, n = ndimage.label(joined)
    if n <= 1:
        return mask
    areas = ndimage.sum(mask, lab, index=np.arange(1, n + 1))   # area of the *original* mask per component
    return mask & (lab == int(np.argmax(areas)) + 1)


def derive_mask(img: np.ndarray, border: int = 40, thresh: float = 45.0, work_side: int = 1024) -> np.ndarray:
    """Mask for archives without one: pixels whose colour differs from the median border
    colour by more than `thresh` (L2 in RGB) are object. Small components are removed by
    keeping only the largest connected blob after a light morphological cleanup. Computed
    on a copy downscaled to `work_side` on the long side, then upsampled (nearest)."""
    from scipy import ndimage

    h, w = img.shape[:2]
    s = max(h, w) / work_side
    if s > 1.0:
        small = np.asarray(Image.fromarray(img).resize((int(round(w / s)), int(round(h / s))), Image.BILINEAR))
        m = derive_mask(small, max(2, int(border / s)), thresh, work_side)
        return np.asarray(Image.fromarray(m.astype(np.uint8) * 255).resize((w, h), Image.NEAREST)) > 127
    x = img.astype(np.float32)
    ring = np.concatenate([x[:border].reshape(-1, 3), x[-border:].reshape(-1, 3),
                           x[:, :border].reshape(-1, 3), x[:, -border:].reshape(-1, 3)])
    bg = np.median(ring, axis=0)
    diff = np.linalg.norm(x - bg, axis=-1)
    m = diff > thresh
    m = ndimage.binary_opening(m, iterations=2)
    m = ndimage.binary_closing(m, iterations=4)
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n == 0:
        return centre_mask(img.shape[0], img.shape[1])
    sizes = ndimage.sum(m, lab, index=np.arange(1, n + 1))
    return lab == (int(np.argmax(sizes)) + 1)


def centre_mask(h: int, w: int, frac: float = 0.5) -> np.ndarray:
    m = np.zeros((h, w), bool)
    y0, y1 = int(h * (1 - frac) / 2), int(h * (1 + frac) / 2)
    x0, x1 = int(w * (1 - frac) / 2), int(w * (1 + frac) / 2)
    m[y0:y1, x0:x1] = True
    return m


def mask_bbox(mask: np.ndarray, expand: float = 0.10) -> tuple[int, int, int, int]:
    """(x0, y0, x1, y1) of the mask, each side grown by `expand` of the box size, clipped."""
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return 0, 0, mask.shape[1], mask.shape[0]
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    dh, dw = int(round((y1 - y0) * expand)), int(round((x1 - x0) * expand))
    return (max(0, x0 - dw), max(0, y0 - dh), min(mask.shape[1], x1 + dw), min(mask.shape[0], y1 + dh))


def load_view(image_path: Path, mask_path: Path | None) -> tuple[np.ndarray, np.ndarray, str]:
    """RGB uint8 image, boolean object mask, and a string saying where the mask came from."""
    img = np.asarray(Image.open(image_path).convert("RGB"))
    if mask_path is not None and mask_path.exists():
        render = is_render(image_path.name)
        # archive masks get the stray-blob cleanup; render masks come from the segmentation
        # buffer and are exact (cleaning would drop e.g. the lid handle in some views)
        mask = load_mask(mask_path, clean=not render)
        if mask.shape != img.shape[:2]:
            mask = np.asarray(Image.fromarray(mask).resize((img.shape[1], img.shape[0]), Image.NEAREST))
        return img, mask, ("render" if render else "archive")
    return img, derive_mask(img), "derived"


def object_crop(img: np.ndarray, mask: np.ndarray, expand: float = 0.10) -> tuple[np.ndarray, np.ndarray]:
    """Crop image and mask to the expanded mask bounding box; background pixels untouched."""
    x0, y0, x1, y1 = mask_bbox(mask, expand)
    return img[y0:y1, x0:x1], mask[y0:y1, x0:x1]


if __name__ == "__main__":
    import sys

    from ..ycb import OBJECTS

    ids = sys.argv[1:] or list(OBJECTS)
    for oid in ids:
        try:
            fetch_ycb_photos(oid)
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            # 028_skillet_lid: the server holds no photographs of it, and its views are rendered instead
            print(f"[{oid}] no photographs on the YCB server; render its views with "
                  f"`python -m matgrasp.heads.render_views {oid}`", flush=True)
