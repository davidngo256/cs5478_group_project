# Collision hulls

The convex decompositions of the ten study objects, one OBJ file per object, as the simulation loads them.

- Source: the `nontextured.stl` scans of the YCB Object and Model Set (Calli et al.), centred on the centre of
  mass and decomposed with V-HACD through PyBullet (`matgrasp.ycb.ensure_vhacd` holds the parameters).
- Licence: the YCB set is released under Creative Commons Attribution 4.0 International (CC BY 4.0); these
  files are derived from it.
- They are inputs of the study. V-HACD returns slightly different hulls on another machine, and a different
  hull moves individual trials, so the files the tracked results ran on are kept here.
