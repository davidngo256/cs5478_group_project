"""Fast tests for matgrasp.heads: no model weights, no network, no photos needed."""
import json

import numpy as np
import pytest

from matgrasp.friction import CLIP_PROMPTS, DMS46_TO_TABLE, MATERIAL_TABLE, MINC_TO_TABLE, remap_probs
from matgrasp.heads import common, minc, ycb_photos
from matgrasp.heads.clip_head import build_prompts
from matgrasp.heads.dms46 import DMS46_INDICES


# --- calibration ----------------------------------------------------------------------------

def test_ece_perfect_and_worst_cases():
    p = np.array([[0.9, 0.1], [0.8, 0.2], [0.7, 0.3], [0.6, 0.4]])
    # top-1 always correct with confidences .9,.8,.7,.6 -> each bin gap = 1 - conf
    assert common.ece_score(p, np.zeros(4, int), n_bins=15) == pytest.approx(np.mean([0.1, 0.2, 0.3, 0.4]))
    # always wrong -> gap = conf
    assert common.ece_score(p, np.ones(4, int), n_bins=15) == pytest.approx(np.mean([0.9, 0.8, 0.7, 0.6]))


def test_ece_calibrated_synthetic_is_small():
    rng = np.random.default_rng(0)
    n, c = 20000, 5
    logits = rng.normal(size=(n, c)) * 2.0
    probs = common.softmax(logits)
    # sample labels from the model's own posterior -> calibrated by construction
    labels = np.array([rng.choice(c, p=pr) for pr in probs])
    assert common.ece_score(probs, labels, 15) < 0.02
    # sharpening the same posterior makes it over-confident
    assert common.ece_score(common.softmax(logits, T=0.4), labels, 15) > 0.08


def test_temperature_scaling_recovers_known_temperature():
    rng = np.random.default_rng(1)
    n, c, t_true = 6000, 6, 2.5
    logits = rng.normal(size=(n, c)) * 3.0
    calibrated = common.softmax(logits, T=t_true)
    labels = np.array([rng.choice(c, p=pr) for pr in calibrated])
    t_hat = common.fit_temperature(logits, labels)
    assert abs(t_hat - t_true) / t_true < 0.10
    assert common.ece_score(common.softmax(logits, t_hat), labels) < common.ece_score(common.softmax(logits), labels)


def test_softmax_rows_sum_to_one():
    p = common.softmax(np.array([[1000.0, 0.0, -5.0], [0.0, 0.0, 0.0]]))
    assert np.allclose(p.sum(1), 1.0) and p[0, 0] == pytest.approx(1.0) and p[1].tolist() == pytest.approx([1 / 3] * 3)


def test_confusion_matrix_counts():
    cm = common.confusion_matrix(["a", "a", "b"], ["a", "b", "b"], ["a", "b"])
    assert cm == {"a": {"a": 1, "b": 1}, "b": {"a": 0, "b": 1}}


# --- mask averaging / crops ----------------------------------------------------------------

def test_mask_average_uses_only_mask_pixels():
    post = np.zeros((3, 4, 4))
    post[0] = 1.0                      # background says class 0 everywhere
    mask = np.zeros((4, 4), bool)
    mask[1:3, 1:3] = True
    post[:, mask] = np.array([[0.1, 0.6, 0.3]]).T   # object pixels say class 1
    avg = common.mask_average(post, mask)
    assert avg.tolist() == pytest.approx([0.1, 0.6, 0.3])
    assert avg.sum() == pytest.approx(1.0)
    # empty mask falls back to whole frame
    assert common.mask_average(post, np.zeros((4, 4), bool))[0] == pytest.approx((12 * 1.0 + 4 * 0.1) / 16)


def test_resize_mask_nearest_keeps_boolean():
    m = np.zeros((10, 20), bool)
    m[2:8, 5:15] = True
    r = common.resize_mask(m, 5, 10)
    assert r.shape == (5, 10) and r.dtype == bool and r.any() and not r.all()


def test_mask_bbox_expands_and_clips():
    m = np.zeros((100, 200), bool)
    m[40:60, 50:150] = True             # h=20, w=100
    assert ycb_photos.mask_bbox(m, 0.10) == (40, 38, 160, 62)
    m[:, :] = True
    assert ycb_photos.mask_bbox(m, 0.10) == (0, 0, 200, 100)
    assert ycb_photos.mask_bbox(np.zeros((5, 7), bool)) == (0, 0, 7, 5)


def test_object_crop_leaves_background_pixels():
    img = np.full((50, 50, 3), 7, np.uint8)
    img[20:30, 20:30] = 200
    mask = np.zeros((50, 50), bool)
    mask[20:30, 20:30] = True
    crop, cm = ycb_photos.object_crop(img, mask, 0.10)
    assert crop.shape == (12, 12, 3) and cm.shape == (12, 12)
    assert crop[0, 0].tolist() == [7, 7, 7] and crop[1, 1].tolist() == [200, 200, 200]


def test_derive_mask_finds_blob_on_flat_background():
    img = np.full((120, 160, 3), 240, np.uint8)
    img[30:90, 50:110] = (30, 60, 90)
    m = ycb_photos.derive_mask(img, border=10)
    assert m[60, 80] and not m[5, 5]
    assert 0.8 < m.sum() / (60 * 60) < 1.2


# --- YCB view parsing -----------------------------------------------------------------------

def test_view_stems_and_wanted_members():
    stems = ycb_photos.view_stems("003_cracker_box")
    assert len(stems) == 48 and stems[0] == "NP1_0" and "NP3_315" in stems and "N3_315" in stems
    assert ycb_photos.view_stems("028_skillet_lid") == [f"N{c}_{a}" for c in (1, 2, 3) for a in range(0, 360, 45)]
    s = set(stems)
    assert ycb_photos.wanted_member("003_cracker_box/NP1_45.jpg", s)
    assert ycb_photos.wanted_member("003_cracker_box/masks/NP1_45_mask.pbm", s)
    assert not ycb_photos.wanted_member("003_cracker_box/NP1_45.h5", s)
    assert not ycb_photos.wanted_member("003_cracker_box/NP1_48.jpg", s)
    assert not ycb_photos.wanted_member("003_cracker_box/NP4_45.jpg", s)


def test_parse_view_files_groups_masks_with_images():
    names = ["NP1_0.jpg", "NP1_0_mask.pbm", "NP2_45.jpg", "N1_90.jpg", "N1_90_mask.pbm",
             "_listing.txt", "_done", "calibration.h5", "NP2_45.h5"]
    v = ycb_photos.parse_view_files(names)
    assert v == {"NP1_0": {"image": "NP1_0.jpg", "mask": "NP1_0_mask.pbm"},
                 "NP2_45": {"image": "NP2_45.jpg"},
                 "N1_90": {"image": "N1_90.jpg", "mask": "N1_90_mask.pbm"}}
    assert sorted(v, key=ycb_photos.sort_key) == ["NP1_0", "N1_90", "NP2_45"]


def test_list_views_on_tmp_dir(tmp_path, monkeypatch):
    d = tmp_path / "obj"
    d.mkdir()
    for n in ["NP1_0.jpg", "NP1_0_mask.pbm", "NP1_45.jpg", "_listing.txt"]:
        (d / n).write_bytes(b"")
    monkeypatch.setattr(ycb_photos, "PHOTO_DIR", tmp_path)
    assert ycb_photos.list_views("obj") == []          # no completion marker: download in progress
    (d / "_done").write_bytes(b"")
    views = ycb_photos.list_views("obj")
    assert [(a.name, b.name if b else None) for a, b in views] == [("NP1_0.jpg", "NP1_0_mask.pbm"), ("NP1_45.jpg", None)]
    assert ycb_photos.list_views("missing") == []


def test_clean_mask_drops_stray_blobs_but_keeps_bridged_parts():
    m = np.zeros((100, 100), bool)
    m[40:60, 40:60] = True            # body (400 px)
    m[30:38, 45:55] = True            # "shackle" separated by a 2 px gap -> stays
    m[5:12, 5:12] = True              # stray blob far away -> dropped
    c = ycb_photos.clean_mask(m, gap=5)
    assert c[50, 50] and c[34, 50] and not c[8, 8]
    assert c.sum() == 400 + 80 and not (c & ~m).any()   # subset of the input, no fattening
    assert ycb_photos.clean_mask(np.zeros((5, 5), bool)).sum() == 0
    assert ycb_photos.mask_bbox(c, 0.0) == (40, 30, 60, 60)


def test_load_mask_polarity(tmp_path):
    from PIL import Image
    # YCB style: object black (0) on white (1)
    arr = np.ones((20, 30), np.uint8) * 255
    arr[5:10, 5:10] = 0
    p = tmp_path / "m.pbm"
    Image.fromarray(arr).convert("1").save(p)
    m = ycb_photos.load_mask(p)
    assert m.shape == (20, 30) and m[7, 7] and not m[0, 0] and m.sum() == 25


# --- vocabulary plumbing ----------------------------------------------------------------------

def test_build_prompts_table_order_and_missing():
    classes, prompts = build_prompts()
    assert classes == list(MATERIAL_TABLE) and len(prompts) == 11
    assert prompts[classes.index("paper")] == CLIP_PROMPTS["paper"]
    with pytest.raises(KeyError):
        build_prompts({"glass": "x"}, ["glass", "metal"])


def test_full_table_probs_fills_and_normalises():
    p = common.full_table_probs({"plastic": 2.0, "glass": 2.0})
    assert list(p) == list(MATERIAL_TABLE) and p["plastic"] == 0.5 and p["foam"] == 0.0
    assert sum(p.values()) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        common.full_table_probs({"unobtainium": 1.0})


def test_dms46_indices_cover_mapping():
    names = ["No label", "Animal skin", "Bone/teeth/horn", "Brickwork", "Cardboard", "Carpet/rug", "Ceiling tile",
             "Ceramic", "Chalkboard/blackboard", "Clutter", "Concrete", "Cork/corkboard", "Engineered stone",
             "Fabric/cloth", "Fiberglass wool", "Fire", "Foliage", "Food", "Fur", "Gemstone/quartz", "Glass", "Hair",
             "I cannot tell", "Ice", "Leather", "Liquid, non-water", "Metal", "Mirror", "Not on list",
             "Paint/plaster/enamel", "Paper", "Pearl", "Photograph/painting", "Plastic, clear", "Plastic, non-clear",
             "Rubber/latex", "Sand", "Skin/lips", "Sky", "Snow", "Soap", "Soil/mud", "Sponge", "Stone, natural",
             "Stone, polished", "Styrofoam", "Tile", "Wallpaper", "Water", "Wax", "Whiteboard", "Wicker", "Wood",
             "Wood, tree", "Bad polygon", "Multiple materials", "Asphalt"]
    assert len(DMS46_INDICES) == 46 and len(set(DMS46_INDICES)) == 46
    trained = {names[i] for i in DMS46_INDICES}
    assert set(DMS46_TO_TABLE) <= trained
    # a 46-way posterior remaps onto table classes and stays normalised
    post = {names[i]: 1.0 / 46 for i in DMS46_INDICES}
    out = common.full_table_probs(remap_probs(post, DMS46_TO_TABLE))
    assert sum(out.values()) == pytest.approx(1.0) and out["plastic"] > out["rubber"]


def test_minc_row_selection_helpers():
    labels = [0, 0, 0, 1, 1, 2, 2, 2, 2]
    assert minc.choose_rows(labels, {0, 2}, 2) == [0, 1, 5, 6]
    assert minc.choose_rows(labels, {2}, None) == [5, 6, 7, 8]
    assert minc.row_groups_for([0, 1, 5], [3, 3, 3]) == [(0, 0, 3), (1, 3, 6)]
    assert minc.MINC_CLASSES == sorted(MINC_TO_TABLE)
    ents = [{"file": f"{c}/{i}.jpg", "label": c} for c in ("a", "b") for i in range(5)]
    sub = minc.subsample(ents, 3, seed=0)
    assert len(sub) == 6 and {e["label"] for e in sub} == {"a", "b"}


def test_ycb_accuracy_majority_vote():
    def probs(c):
        p = {k: 0.0 for k in MATERIAL_TABLE}
        p[c] = 1.0
        return p
    x, y, z = "010_potted_meat_can", "003_cracker_box", "028_skillet_lid"   # real ids: metal, paper, glass
    res = {x: {"images": [{"probs": probs("metal")}, {"probs": probs("metal")}, {"probs": probs("glass")}],
               "mean_probs": probs("metal"), "true_material": "metal", "top1_correct_rate": 2 / 3},
           y: {"images": [{"probs": probs("wood")}], "mean_probs": probs("wood"), "true_material": "paper",
               "top1_correct_rate": 0.0}}
    acc = common.ycb_accuracy(res)
    assert acc["image_level"] == pytest.approx(0.5) and acc["object_level"] == pytest.approx(0.5)
    assert acc["per_object"][x]["pred"] == "metal" and acc["per_object"][y]["pred"] == "wood"
    assert acc["n_objects"] == 2 and acc["excluded"] == {}
    json.dumps(acc)  # serialisable
    # render-fallback objects are reported but kept out of the photo accuracy
    res[z] = {"images": [{"probs": probs("glass")}], "mean_probs": probs("glass"), "true_material": "glass",
              "top1_correct_rate": 1.0, "source": "render"}
    # objects no longer in OBJECTS (retired) are kept in the file but excluded too
    res["025_mug"] = {"images": [{"probs": probs("ceramic")}], "mean_probs": probs("ceramic"),
                      "true_material": "ceramic", "top1_correct_rate": 1.0, "retired": True}
    acc = common.ycb_accuracy(res)
    assert acc["object_level"] == pytest.approx(0.5) and acc["n_images"] == 4 and acc["n_objects"] == 2
    assert acc["excluded_render_objects"] == [z] and acc["per_object"][z]["pred"] == "glass"
    assert set(acc["excluded"]) == {z, "025_mug"} and acc["per_object"]["025_mug"]["source"] == "retired"


def test_evaluate_ycb_reuses_previous_entries(tmp_path, monkeypatch):
    from PIL import Image
    d = tmp_path / "003_cracker_box"
    d.mkdir()
    Image.fromarray(np.full((8, 8, 3), 100, np.uint8)).save(d / "NP1_0.jpg")
    (d / "_done").write_bytes(b"")
    monkeypatch.setattr(ycb_photos, "PHOTO_DIR", tmp_path)
    monkeypatch.setattr(common, "DATA_DIR", tmp_path.parent)
    calls = []

    class Head:
        name = "fake"

        def predict(self, img, mask):
            calls.append(1)
            return {"paper": 1.0}

    first = common.evaluate_ycb(Head(), ["003_cracker_box"], verbose=False)
    assert len(calls) == 1 and first["003_cracker_box"]["images"][0]["probs"]["paper"] == 1.0
    again = common.evaluate_ycb(Head(), ["003_cracker_box"], verbose=False, previous=first)
    assert len(calls) == 1 and again == first          # reused, no new predict() call
    stale = {"003_cracker_box": {**first["003_cracker_box"], "true_material": "metal"}}
    common.evaluate_ycb(Head(), ["003_cracker_box"], verbose=False, previous=stale)
    assert len(calls) == 2                              # truth changed -> recomputed


def test_render_view_names_are_recognised():
    assert ycb_photos.is_render("R1_45.jpg") and ycb_photos.is_render("R2_0_mask.pbm")
    assert not ycb_photos.is_render("NP1_45.jpg") and not ycb_photos.is_render("README.md")
    v = ycb_photos.parse_view_files(["R1_0.jpg", "R1_0_mask.pbm", "_rendered"])
    assert v == {"R1_0": {"image": "R1_0.jpg", "mask": "R1_0_mask.pbm"}}
