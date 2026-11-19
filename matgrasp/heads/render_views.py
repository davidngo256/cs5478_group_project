"""Fallback for objects with no photographs on the YCB server (028_skillet_lid: the S3 bucket
holds no `berkeley/` archive for it at all, only the Google scans). Renders the Google 16k
textured scan from 24 viewpoints (3 elevations x 8 azimuths, mirroring the NP1-3 x 45-degree
photo subset) with PyBullet's software renderer on a plain light background, and writes
R<cam>_<angle>.jpg + R<cam>_<angle>_mask.pbm (mask from the segmentation buffer) into the
object's photo directory. These are renders, not photographs, and the evaluation code keeps
them out of the photo accuracy numbers (see common.ycb_accuracy).

Note for the skillet lid specifically: the scanner did not capture the glass disc, only the
metal rim and handle (see texture_map.png), so the renders show a metal ring - a very weak
stand-in for "glass".
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image

from ..ycb import ensure_mesh
from . import ycb_photos

ELEVATIONS_DEG = (20.0, 40.0, 60.0)   # R1, R2, R3
AZIMUTHS_DEG = tuple(range(0, 360, 45))


def render_object(obj_id: str, width: int = 640, height: int = 512, fov: float = 35.0,
                  verbose: bool = True) -> Path:
    import pybullet as p
    import trimesh

    d = ensure_mesh(obj_id, verbose=verbose)
    out = ycb_photos.photo_dir(obj_id)
    out.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load(d / "textured.obj", force="mesh")
    lo, hi = mesh.bounds
    centre = 0.5 * (lo + hi)
    radius = 0.5 * float(np.linalg.norm(hi - lo))
    dist = radius / math.tan(math.radians(fov) / 2) * 1.15

    cid = p.connect(p.DIRECT)
    try:
        vs = p.createVisualShape(p.GEOM_MESH, fileName=str(d / "textured.obj"), physicsClientId=cid)
        p.createMultiBody(baseMass=0, baseVisualShapeIndex=vs, basePosition=[0, 0, 0], physicsClientId=cid)
        proj = p.computeProjectionMatrixFOV(fov=fov, aspect=width / height, nearVal=0.01, farVal=dist * 4)
        n = 0
        for cam, el in enumerate(ELEVATIONS_DEG, start=1):
            for az in AZIMUTHS_DEG:
                a, e = math.radians(az), math.radians(el)
                eye = centre + dist * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
                view = p.computeViewMatrix(eye.tolist(), centre.tolist(), [0, 0, 1])
                w, h, rgba, _, seg = p.getCameraImage(width, height, view, proj, renderer=p.ER_TINY_RENDERER,
                                                      lightDirection=[0.5, -0.8, 1.5], shadow=0, physicsClientId=cid)
                rgb = np.asarray(rgba, np.uint8).reshape(h, w, 4)[..., :3]
                mask = np.asarray(seg).reshape(h, w) >= 0
                stem = f"R{cam}_{az}"
                Image.fromarray(rgb).save(out / f"{stem}.jpg", quality=92)
                # same convention as the YCB masks: object black on white
                Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).convert("1").save(out / f"{stem}_mask.pbm")
                n += 1
    finally:
        p.disconnect(cid)
    (out / "_rendered").write_text(f"{n} views rendered from {d / 'textured.obj'}\n")
    if verbose:
        print(f"[{obj_id}] rendered {n} views into {out}", flush=True)
    return out


if __name__ == "__main__":
    import sys

    for oid in sys.argv[1:] or ["028_skillet_lid"]:
        render_object(oid)
