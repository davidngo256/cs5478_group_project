## Data and protocol

- Photos:
  - For each object the Berkeley `*_berkeley_rgbd.tgz` archive was streamed (never stored).
  - Only cameras NP1-3 at angles 0, 45, ..., 315 were kept (24 views + their `masks/*_mask.pbm`), then
    discarded.
  - Masks are the archive's own object masks (object = black in the PBM, inverted on load).
  - Checked visually against the images for the cracker box, padlock, plate, mug and the lid renders: they
    align.
  - The background-subtraction fallback in `ycb_photos.derive_mask` was implemented but never needed: every
    used view had an archive mask.
- Object set:
  - `matgrasp.ycb.OBJECTS` changed while this was running (007_tuna_fish_can -> 038_padlock, 025_mug ->
    029_plate, both because the originals were ungraspable in simulation).
  - The padlock and plate were fetched and evaluated with the same procedure (RGB-D archives, 24 views,
    archive masks).
  - The only results ever computed for the tuna can and the mug came from an earlier pass (CLIP only, before
    the mask cleaning below was added). They were discarded rather than mixed in. --> The final files contain
    exactly the current ten objects.
  - Their photos are still under `data/ycb_photos/`. `common.run_head` keeps entries for objects that leave
    `OBJECTS` flagged `"retired": true`, excluded from the accuracies, should the set change again.
  - For the record: the mug's "rgbd" archive actually holds high-resolution `N<cam>_<angle>.jpg` images plus
    masks. The physical mug is red speckled enamelware, i.e. coated metal rather than ceramic.
- 028_skillet_lid has NO photographs on the YCB server at all.
  - Both `028_skillet_lid_berkeley_rgbd.tgz` and `028_skillet_lid_berkeley_rgb_highres.tgz` return HTTP 404.
    An S3 listing of the bucket with prefix `data/berkeley/028` is empty (only
    `data/google/028_skillet_lid_google_{16k,64k,512k}.tgz` exist).
  - Stand-in: `matgrasp/heads/render_views.py` renders the Google 16k textured scan from 24 viewpoints with
    PyBullet's software renderer (files `R<cam>_<angle>.jpg`, masks from the segmentation buffer).
  - These renders are evaluated and reported per object but excluded from ALL photo accuracy numbers
    (`excluded_render_objects` in the summaries).
  - They are a poor stand-in for two reasons. They are renders. The scan itself contains only the metal rim
    and handle (the scanner did not capture the transparent glass disc) --> the "glass" object looks like a
    metal ring.
- Mask cleaning (`ycb_photos.clean_mask`):
  - Only the largest connected component is kept (components bridged by gaps of up to ~10px count as
    connected).
  - This matters for 038_padlock: its archive masks contain stray blobs from turntable reflections far from
    the object (8.6% of mask pixels on average; without cleaning the crop box was 16x larger than the object).
  - For the other photographed objects it removes 0-0.6% of mask pixels. Render masks are not cleaned (they
    are exact).
- 038_padlock is small in the frame (0.3-0.4% of the pixels, crops of roughly 75 x 100px).
  - --> Every head sees a heavily upsampled patch (DMS46 works at 512px on the long side, the classifiers at
    224).
  - Its archive masks also cover only the laminated body with its blue bumper. The thin chrome shackle is
    absent from the YCB masks themselves (checked: it is not a separate component that cleaning removed). -->
    The heads mostly judge the body.
- Object crops: bounding box of the mask grown by 10% per side, background pixels left untouched.
  - The DMS46 head averages its per-pixel 46-way softmax over mask pixels only (mask resized to the network's
    working resolution).
  - The two classifier heads see the crop as-is.
- Ground truth: `matgrasp.ycb.OBJECTS`.
- Latency protocol:
  - Batch size 1, `torch.no_grad`, 5 warm-up calls then 20 timed calls on YCB views (round-robin over
    objects).
  - The time includes cropping and preprocessing on the CPU, the host-device copies and the forward pass on
    the GPU (`torch.cuda.synchronize()` brackets every call, so queued kernels are counted, not just their
    launch).
  - Machine: an NVIDIA GB10 (unified memory) next to 20 aarch64 cores (10 Cortex-X925 + 10 Cortex-A725).
  - Date: 15-Oct-2026, nothing else running on the box (1-minute load 0.4-1.1 at the start of each timing,
    which is the head's own model load; `loadavg_1min_at_start` in each summary).
  - Each head was timed three times in a row with `python -m matgrasp.heads.<head> latency`; the summary
    keeps the last pass.
  - The three passes read 21.2 / 21.2 / 21.2ms for DMS46, 11.4 / 10.9 / 11.0ms for CLIP and 8.2 / 8.8 / 8.4ms
    for MobileNet (`results/timing_idle/latency_*.out`).
- Latency history:
  - 1-Oct-2026, previous machine (an NVIDIA L4 next to 4 vCPUs, two physical cores of a 2.2GHz Xeon, idle;
    `results/timing_idle_l4/`): 74 +/- 25 / 13 +/- 1 / 13 +/- 2ms.
  - 23-Sep on the same box: 75 / 14 / 13ms. A pass that shared the CPU and GPU with another job had read
    90 / 18 / 26ms with two to three times the jitter.
- Where the time goes:
  - The GPU forward itself is 3.8ms for CLIP and 1.2ms for MobileNet here (5-6ms on the L4). The rest is
    Python, cropping, PIL resizing and the copies. --> The 1.5M-parameter MobileNet (8 +/- 1ms) is not much
    faster than CLIP (11 +/- 1ms) at batch size 1.
  - DMS46's spread (21 +/- 6ms, min 10) follows the crop size: it works at 512px on the long side, and its
    forward takes 7-25ms.
  - Its per-pixel posterior is averaged over the mask on the device and only the 46 class means are
    copied back.
  - The original code copied the 46 x H x W posterior (11-44MB) to the host first. This unified-memory GPU
    did that in anywhere from 0.2 to 380ms per image (mean 96ms, s.d. 108ms; the L4 took a few ms). --> A
    first pass on this machine had read 120-150 +/- 100ms for DMS46.
  - The device-side average gives identical posteriors (maximum difference 1e-16).
- Torch threads:
  - Torch's CPU thread pool is left at its default (the physical core count, 20 here). For DMS46 on this box
    20, 10, 4 and 1 threads gave the same latency.
  - On the 2-core L4 VM forcing 4 threads had tripled the MobileNet and CLIP latencies and made them jittery,
    the same oversubscription seen on an earlier 8-vCPU machine at 8 threads.
- CPU-only reference: the same code on that machine's CPU (no GPU, shared with a 7-worker simulation study,
  4 threads) measured DMS46 2.3s, CLIP 143ms and MobileNet 12ms per image. `MATGRASP_DEVICE=cpu` reproduces a
  CPU-only run.
- To re-time on an idle box: `python -m matgrasp.heads.<dms46|clip_head|mobilenet> latency` rewrites only the
  latency field of that head's summary; then `python -m matgrasp.heads.report`.

## Head-specific caveats

- DMS46:
  - The TorchScript `forward()` only returns the per-pixel argmax. The 46-way logits are obtained by calling
    `model.encoder` / `model.decoder` directly (verified to reproduce the official argmax).
  - Only the 21 DMS classes listed in `DMS46_TO_TABLE` carry mass onto the table. Mass on other DMS classes
    (Food, Clutter, ...) is dropped by `remap_probs`.
  - DMS46 was trained for scene parsing on Open Images and has never seen turntable product shots. It is used
    as-is, without calibration (no labelled held-out set in the table vocabulary) --> no ECE is reported for
    it.
- CLIP:
  - `ViT-B-32` with the `laion2b_s34b_b79k` weights (first tag that downloaded), zero-shot with the prompts
    in `friction.CLIP_PROMPTS`, softmax over the eleven table classes with the model's logit scale (100).
  - Not calibrated either: there is no labelled calibration set, and the posterior is dominated by the prompt
    wording ("painted object" attracts every printed can and box). Numbers are reported as they are.
- MobileNetV3-Small:
  - Fine-tuned on the ten MINC-2500 classes in `MINC_TO_TABLE` only --> foam and rubber receive exactly ZERO
    probability from this head by construction; 061_foam_brick and 057_racquetball can never be predicted
    correctly by it.
  - `polishedstone` is merged into `ceramic` by `remap_probs`.
  - The MINC-2500 subset was read from the Hugging Face mirror by fetching only the parquet row groups holding
    those classes. Train: first 700 images per class, of which 600/class were used. Validation and test:
    complete, 125 and 250 per class.
  - Temperature was fitted on the validation split. ECE is reported on both validation and the full 10-class
    test split.
  - Training ran on the NVIDIA GB10 (seed 0, 4 DataLoader workers, torch's default 20 CPU threads): 5s per
    epoch, 39s in total on the idle machine (41s for the stage including start-up), still bounded by JPEG
    decoding and augmentation in the four loader processes.
  - On the previous machine (NVIDIA L4, 4 vCPUs) the same fine-tune took 2.3min (16-18s per epoch) idle on
    1-Oct-2026 and 3.8min (26-31s per epoch) on 23-Sep while another job shared the CPUs.
- MobileNet checkpoints (GPU training is not bit-reproducible; the checkpoint was retrained on 15-Oct-2026):
  - 1-Oct checkpoint: 71.2% MINC test accuracy, ECE 0.079 -> 0.027 at T = 1.39. It predicted ceramic for the
    plate where this one predicts plastic (so the object-level top-1 is 2/9 here, 3/9 on 1-Oct).
  - 23-Sep checkpoint: 70.3%, ECE 0.082 -> 0.021 at T = 1.39. It voted metal for the skillet-lid renders where
    this one votes glass.
  - Earlier CPU-trained checkpoint (47min on a shared 8-vCPU box): 70.1%, ECE 0.080 -> 0.029 at T = 1.44. It
    predicted plastic for the plate and the racquetball.
  - Validation accuracy was still rising slowly at epoch 8 (0.687 -> 0.694 over the last three epochs). A
    longer budget would help a little, but the fine-tune is mainly limited by the 600 images/class.

## Files

- `<head>_ycb.json`: per-object, per-view posteriors over the table classes (sum to 1), mean posterior, true
  material, per-view top-1 rate; `source` = photo or render.
- `<head>_summary.json`: params, latency, YCB accuracies (image- and object-level, per-object votes), and for
  MobileNet the MINC test accuracy, ECE before/after, fitted temperature and confusion matrix.
- `mobilenet_train.log`: training log (git-ignored).
  - Tracked copy of the 15-Oct run: `results/timing_idle/mobilenet_train.out`; of the 1-Oct L4 run:
    `results/timing_idle_l4/mobilenet_train.out`.
- `mobilenet_minc.json`: full MINC metrics incl. 10-class confusion matrix.
- Code: `matgrasp/heads/{common,ycb_photos,minc,render_views,dms46,clip_head,mobilenet,report}.py`; tests in
  `tests/test_heads.py`.
- Reproduce: `python -m matgrasp.heads.ycb_photos`, `python -m matgrasp.heads.render_views`,
  `python -m matgrasp.heads.minc`, `python -m matgrasp.heads.mobilenet train`, then
  `python -m matgrasp.heads.{dms46,clip_head,mobilenet}` and `python -m matgrasp.heads.report` (caveat text
  from `results/heads/notes.md`).
- Device: the heads run on CUDA when available and on the CPU otherwise; `MATGRASP_DEVICE=cpu` forces the CPU.
