"""YCB object registry, mesh download/cache, and convex decomposition for PyBullet."""
from __future__ import annotations

import io
import os
import shutil
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

YCB_BASE = "http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/data"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
HULL_DIR = Path(__file__).resolve().parent / "hulls"   # the convex decompositions the study ran on


@dataclass(frozen=True)
class YcbObject:
    id: str
    material: str       # class in friction.MATERIAL_TABLE
    mass: float         # kg, from the YCB object list
    note: str = ""


# ten objects across the friction bins; masses from the YCB object set listing
OBJECTS: dict[str, YcbObject] = {o.id: o for o in [
    YcbObject("028_skillet_lid",    "glass",   0.652, "tempered glass lid with metal rim; only glass item in YCB"),
    YcbObject("038_padlock",        "metal",   0.304, "steel/brass padlock; replaces 007_tuna_fish_can (8.6 cm disc: wider than the gripper, only a top-bottom pinch, infeasible on a table)"),
    YcbObject("010_potted_meat_can", "metal",  0.370, "printed metal can"),
    YcbObject("029_plate",          "ceramic", 0.279, "glazed ceramic plate, rim grasps; replaces 025_mug (body at the gripper limit, <2% of sampled grasps feasible)"),
    YcbObject("006_mustard_bottle", "plastic", 0.603, "HDPE bottle"),
    YcbObject("021_bleach_cleanser", "plastic", 1.131, "HDPE bottle, heaviest object"),
    YcbObject("003_cracker_box",    "paper",   0.411, "cardboard box"),
    YcbObject("004_sugar_box",      "paper",   0.514, "cardboard box, tall; 036_wood_block was dropped: all its dimensions exceed the Panda opening"),
    YcbObject("061_foam_brick",     "foam",    0.028, "foam brick"),
    YcbObject("057_racquetball",    "rubber",  0.041, "rubber ball"),
]}


def mesh_dir(obj_id: str) -> Path:
    return DATA_DIR / "ycb" / obj_id / "google_16k"


def ensure_mesh(obj_id: str, verbose: bool = True) -> Path:
    """Download and extract the google_16k mesh archive if not cached. Returns the mesh dir."""
    d = mesh_dir(obj_id)
    stl = d / "nontextured.stl"
    if stl.exists():
        return d
    url = f"{YCB_BASE}/google/{obj_id}_google_16k.tgz"
    if verbose:
        print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as r:
        buf = io.BytesIO(r.read())
    # Extract beside the target and move the files into place, the stl last: it marks the mesh as present, so
    # an interrupted download or a second process never meets a half-written mesh that looks complete.
    part = DATA_DIR / "ycb" / f".{obj_id}.{os.getpid()}.part"
    with tarfile.open(fileobj=buf, mode="r:gz") as tf:
        members = [m for m in tf.getmembers() if m.name.endswith(("nontextured.stl", "textured.obj", "textured.mtl", "texture_map.png"))]
        tf.extractall(part, members=members, filter="data")
    files = sorted((f for f in part.rglob("*") if f.is_file()), key=lambda f: f.name == stl.name)
    for f in files:
        dest = DATA_DIR / "ycb" / f.relative_to(part)
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(f, dest)
    shutil.rmtree(part, ignore_errors=True)
    assert stl.exists(), f"extraction failed for {obj_id}"
    return d


def load_mesh(obj_id: str) -> trimesh.Trimesh:
    """Watertight-ish mesh in metres, translated so the volume centroid is at the origin."""
    d = ensure_mesh(obj_id, verbose=False)
    m = trimesh.load(d / "nontextured.stl", force="mesh")
    if not m.is_watertight:
        trimesh.repair.fill_holes(m)
    com = m.center_mass if m.is_volume else m.centroid
    m.apply_translation(-com)
    m.metadata["obj_id"] = obj_id
    m.metadata["centre_offset"] = np.asarray(com, float)   # the scan frame's origin, in this mesh's frame: -offset
    return m


def characteristic_radius(mesh: trimesh.Trimesh) -> float:
    """rho for torque scaling: half the largest extent of the object."""
    return float(0.5 * np.max(mesh.extents))


def ensure_vhacd(obj_id: str, verbose: bool = True) -> Path:
    """Convex decomposition for dynamic concave bodies in PyBullet. The study objects use the hull files in
    matgrasp/hulls: V-HACD returns slightly different hulls on another machine, and that moves individual
    trials, so the hulls the study ran on ship with the code. Any other object is decomposed here and cached."""
    shipped = HULL_DIR / f"{obj_id}.obj"
    if shipped.exists():
        return shipped
    d = ensure_mesh(obj_id, verbose=verbose)
    out = d / "vhacd.obj"
    if out.exists():
        return out
    import pybullet as p
    # export the CoM-centred mesh (same frame as load_mesh) so collision and candidates agree
    src = d / "centred.obj"
    load_mesh(obj_id).export(src)
    log = d / "vhacd.log"
    # The decomposition takes seconds and writes as it goes: write under another name and rename, so that
    # vhacd.obj exists only once it is complete (an interrupted run leaves nothing that looks cached).
    part = d / f"vhacd.{os.getpid()}.part.obj"
    p.vhacd(str(src), str(part), str(log), resolution=1_000_000, maxNumVerticesPerCH=128, concavity=0.0002, minVolumePerCH=0.00001)
    assert part.exists(), f"vhacd failed for {obj_id}"
    os.replace(part, out)
    return out
