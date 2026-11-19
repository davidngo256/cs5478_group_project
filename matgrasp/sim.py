"""PyBullet grasp evaluation with a floating parallel-jaw gripper.

The gripper is a palm with two prismatic fingers whose position motors are force-limited, so
the commanded grip force is the motor force limit. The palm is held by a fixed constraint to
the world whose target is moved to lift. Motion planning is not modelled: the gripper is
placed at the grasp pose directly and a candidate whose open gripper intersects the object
or the table is reported infeasible (identically for every experimental arm).

Gripper frame: origin at the palm centre, +z = approach (fingers extend along +z),
y = closing axis. Finger pads are 16 mm wide, 8 mm thick, and the contact patch sits
`Z_TIP` from the palm along z.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data

from .sampler import GraspCandidate
from .wrench import torsional_coefficient
from .ycb import DATA_DIR, OBJECTS, characteristic_radius, ensure_vhacd, load_mesh, mesh_dir

DT = 1.0 / 240.0
PALM_HALF = 0.01
FINGER_LEN = 0.05
FINGER_THICK = 0.008
PAD_WIDTH = 0.016
PAD_LEN = 0.02                              # only the tip pad touches the object; the stem is recessed
Z_TIP = PALM_HALF + FINGER_LEN - PAD_LEN / 2   # pad contact centre along the approach axis
OPEN_MAX = 0.045                            # inner face at |y| = OPEN_MAX - q - FINGER_THICK/2
CLEARANCE = 0.01
# probe directions in the gripper frame (x = pad width, y = closing axis, z = approach).
# Friction-mediated: tangential pushes along x and z, torsion about the closing axis y.
# The rest are limited by finger compliance (F +-y) or by rocking on the finite pad (T +-x, T +-z)
# and are recorded but excluded from the friction wrench-at-slip.
PROBE_DIRS = [np.array(v, float) for v in ([1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1])]
FRICTION_DIRS = {"F+x", "F-x", "F+z", "F-z", "T+y", "T-y"}


def gripper_urdf() -> Path:
    path = DATA_DIR / "gripper.urdf"
    if path.exists():
        return path

    def box(sx, sy, sz):
        return f'<geometry><box size="{sx} {sy} {sz}"/></geometry>'

    def inertial(m, sx, sy, sz):
        ixx = m / 12 * (sy**2 + sz**2)
        iyy = m / 12 * (sx**2 + sz**2)
        izz = m / 12 * (sx**2 + sy**2)
        return f'<inertial><mass value="{m}"/><inertia ixx="{ixx}" ixy="0" ixz="0" iyy="{iyy}" iyz="0" izz="{izz}"/></inertial>'

    def finger(name, sign):
        y0 = sign * OPEN_MAX
        stem_len = FINGER_LEN - PAD_LEN
        # stem is thinner and recessed 1.5 mm from the pad's inner face so only the pad makes contact
        stem_y = -sign * 0.0015
        return f'''
  <link name="{name}">
    {inertial(0.02, PAD_WIDTH, FINGER_THICK, FINGER_LEN)}
    <visual><origin xyz="0 0 {PALM_HALF + stem_len / 2}"/>{box(PAD_WIDTH * 0.75, FINGER_THICK - 0.003, stem_len)}</visual>
    <collision><origin xyz="0 {stem_y} {PALM_HALF + stem_len / 2}"/>{box(PAD_WIDTH * 0.75, FINGER_THICK - 0.003, stem_len)}</collision>
    <visual><origin xyz="0 0 {PALM_HALF + FINGER_LEN - PAD_LEN / 2}"/>{box(PAD_WIDTH, FINGER_THICK, PAD_LEN)}</visual>
    <collision><origin xyz="0 0 {PALM_HALF + FINGER_LEN - PAD_LEN / 2}"/>{box(PAD_WIDTH, FINGER_THICK, PAD_LEN)}</collision>
  </link>
  <joint name="{name}_joint" type="prismatic">
    <parent link="palm"/><child link="{name}"/>
    <origin xyz="0 {y0} 0"/><axis xyz="0 {-sign} 0"/>
    <limit lower="0" upper="{OPEN_MAX}" effort="200" velocity="0.2"/>
  </joint>'''

    urdf = f'''<?xml version="1.0"?>
<robot name="floating_gripper">
  <link name="palm">
    {inertial(0.3, PAD_WIDTH, 2 * OPEN_MAX + FINGER_THICK, 2 * PALM_HALF)}
    <visual>{box(PAD_WIDTH, 2 * OPEN_MAX + FINGER_THICK, 2 * PALM_HALF)}</visual>
    <collision>{box(PAD_WIDTH, 2 * OPEN_MAX + FINGER_THICK, 2 * PALM_HALF)}</collision>
  </link>{finger("finger_l", -1)}{finger("finger_r", 1)}
</robot>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(urdf)
    return path


def quat_to_mat(q):
    return np.array(p.getMatrixFromQuaternion(q)).reshape(3, 3)


def mat_to_quat(R):
    from scipy.spatial.transform import Rotation
    return Rotation.from_matrix(R).as_quat()


APPROACH_ANGLES_DEG = [0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150]


def grasp_pose(c: GraspCandidate, angle_deg: float = 0.0):
    """Gripper base (position, quaternion, R) that puts the pads on the candidate's contacts.
    angle_deg = 0 approaches from as close to straight above as the closing axis allows;
    other angles rotate the approach about the closing axis."""
    y = c.axis / np.linalg.norm(c.axis)
    down = np.array([0.0, 0.0, -1.0])
    a0 = down - (down @ y) * y
    if np.linalg.norm(a0) < 0.3:                      # closing axis nearly vertical: start horizontal
        a0 = np.array([1.0, 0.0, 0.0]) - y[0] * y
    a0 /= np.linalg.norm(a0)
    b = np.cross(y, a0)
    th = np.deg2rad(angle_deg)
    a = np.cos(th) * a0 + np.sin(th) * b
    x = np.cross(y, a)
    R = np.column_stack([x, y, a])
    pos = c.centre - a * Z_TIP
    return pos, mat_to_quat(R), R


@dataclass
class ExecResult:
    feasible: bool
    both_contacts: bool = False
    lifted: bool = False
    held: bool = False               # still in the gripper after the hold
    slip_mm: float = 0.0             # relative translation during lift+hold
    pivot_deg: float = 0.0           # relative rotation during lift+hold
    grip_force: float = 0.0
    wrench_at_slip: dict = field(default_factory=dict)   # gripper-frame direction label -> magnitude [N]
    min_wrench: float = float("nan")                      # min over friction-mediated directions
    min_wrench_all: float = float("nan")                  # min over all 12 directions
    approach_deg: float = float("nan")
    note: str = ""

    @property
    def success(self) -> bool:
        return self.feasible and self.lifted and self.held and self.pivot_deg < 15.0


class GraspSim:
    def __init__(self, obj_id: str | None = None, *, box_extents=None, mass: float | None = None,
                 gui: bool = False, r_patch: float = 0.008, visual: bool = False):
        """visual=True gives the object its textured scan as a visual shape (the collision hull is drawn
        otherwise) and colours the gripper, for recorded clips; it changes nothing in the dynamics."""
        self.cid = p.connect(p.GUI if gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.cid)
        p.setGravity(0, 0, -9.81, physicsClientId=self.cid)
        p.setTimeStep(DT, physicsClientId=self.cid)
        p.setPhysicsEngineParameter(numSolverIterations=150, enableConeFriction=1, physicsClientId=self.cid)
        self.plane = p.loadURDF("plane.urdf", physicsClientId=self.cid)
        p.changeDynamics(self.plane, -1, lateralFriction=0.6, physicsClientId=self.cid)
        self.r_patch = r_patch
        vis = -1
        if obj_id is not None:
            spec = OBJECTS[obj_id]
            mesh = load_mesh(obj_id)
            self.rho = characteristic_radius(mesh)
            self.mass = spec.mass if mass is None else mass
            self.height = float(mesh.extents.max())
            col = p.createCollisionShape(p.GEOM_MESH, fileName=str(ensure_vhacd(obj_id, verbose=False)), physicsClientId=self.cid)
            if visual:   # the scan's textured.obj sits in the scan frame; the hull is CoM-centred (ycb.load_mesh)
                vis = p.createVisualShape(p.GEOM_MESH, fileName=str(mesh_dir(obj_id) / "textured.obj"),
                                          visualFramePosition=(-mesh.metadata["centre_offset"]).tolist(),
                                          physicsClientId=self.cid)
        else:
            ext = np.asarray(box_extents, float)
            self.rho = float(0.5 * ext.max())
            self.mass = 0.5 if mass is None else mass
            self.height = float(ext.max())
            col = p.createCollisionShape(p.GEOM_BOX, halfExtents=ext / 2, physicsClientId=self.cid)
        self.obj = p.createMultiBody(self.mass, col, baseVisualShapeIndex=vis, basePosition=[0, 0, self.height],
                                     physicsClientId=self.cid)
        self.gripper = p.loadURDF(str(gripper_urdf()), [0, 0, 1.0], useFixedBase=False, physicsClientId=self.cid)
        if visual:
            for link in (-1, 0, 1):
                p.changeVisualShape(self.gripper, link, rgbaColor=[0.055, 0.106, 0.165, 1.0], physicsClientId=self.cid)
        self.fingers = [0, 1]
        # Bullet combines torsional friction as spin0*mu1 + spin1*mu0, so the pads carry lateral
        # friction 1.0 and NO spinning friction; the object's spinningFriction = gamma(mu) is then
        # the only torsional term and the combined lateral coefficient equals the object's mu.
        for link in (-1, 0, 1):
            p.changeDynamics(self.gripper, link, lateralFriction=1.0, spinningFriction=0.0, rollingFriction=0.0,
                             restitution=0.0, physicsClientId=self.cid)
        self.constraint = p.createConstraint(self.gripper, -1, -1, -1, p.JOINT_FIXED, [0, 0, 0], [0, 0, 0],
                                             [0, 0, 1.0], physicsClientId=self.cid)
        p.changeConstraint(self.constraint, maxForce=2000, physicsClientId=self.cid)
        self.set_friction(0.5)
        self._pristine = p.saveState(physicsClientId=self.cid)

    # ---- setup -----------------------------------------------------------------------
    def close(self):
        p.disconnect(physicsClientId=self.cid)

    def reset(self):
        """Restore the state saved at construction. Bullet's solver warm-start and contact caches
        otherwise carry over from whatever ran before in this client, so a trial's settled pose
        would depend on the trials that preceded it in the same worker."""
        p.restoreState(self._pristine, physicsClientId=self.cid)

    def set_friction(self, mu: float):
        self.mu = mu
        p.changeDynamics(self.obj, -1, lateralFriction=mu, spinningFriction=torsional_coefficient(mu, self.r_patch),
                         rollingFriction=0.0, restitution=0.0, linearDamping=0.02, angularDamping=0.02,
                         physicsClientId=self.cid)

    def _step(self, n: int):
        for _ in range(n):
            p.stepSimulation(physicsClientId=self.cid)

    def park_gripper(self):
        self._move_gripper([0, 0, 1.0], [0, 0, 0, 1])
        for j in self.fingers:
            p.resetJointState(self.gripper, j, 0.0, physicsClientId=self.cid)

    def _move_gripper(self, pos, quat):
        p.resetBasePositionAndOrientation(self.gripper, pos, quat, physicsClientId=self.cid)
        p.resetBaseVelocity(self.gripper, [0, 0, 0], [0, 0, 0], physicsClientId=self.cid)
        p.changeConstraint(self.constraint, jointChildPivot=pos, jointChildFrameOrientation=quat,
                           maxForce=2000, physicsClientId=self.cid)

    def settle_object(self, rng: np.random.Generator, orientation=None):
        """Drop the object from a random orientation and let it come to rest. Returns (pos, quat)."""
        self.park_gripper()
        if orientation is None:
            from scipy.spatial.transform import Rotation
            orientation = Rotation.random(random_state=int(rng.integers(2**31))).as_quat()
        p.resetBasePositionAndOrientation(self.obj, [0, 0, self.height * 0.6 + 0.02], orientation, physicsClientId=self.cid)
        p.resetBaseVelocity(self.obj, [0, 0, 0], [0, 0, 0], physicsClientId=self.cid)
        for _ in range(12):
            self._step(60)
            v, w = p.getBaseVelocity(self.obj, physicsClientId=self.cid)
            if np.linalg.norm(v) < 1e-3 and np.linalg.norm(w) < 1e-2:
                break
        pos, quat = p.getBasePositionAndOrientation(self.obj, physicsClientId=self.cid)
        return np.array(pos), np.array(quat)

    def object_pose(self):
        pos, quat = p.getBasePositionAndOrientation(self.obj, physicsClientId=self.cid)
        return np.array(pos), quat_to_mat(quat)

    def down_in_object_frame(self) -> np.ndarray:
        _, R = self.object_pose()
        return R.T @ np.array([0.0, 0.0, -1.0])

    def _rel_pose(self):
        gp, gq = p.getBasePositionAndOrientation(self.gripper, physicsClientId=self.cid)
        op, oq = p.getBasePositionAndOrientation(self.obj, physicsClientId=self.cid)
        Rg, Ro = quat_to_mat(gq), quat_to_mat(oq)
        return Rg.T @ (np.array(op) - np.array(gp)), Rg.T @ Ro

    @staticmethod
    def _pose_delta(a, b):
        t = np.linalg.norm(b[0] - a[0])
        cos = np.clip((np.trace(a[1].T @ b[1]) - 1) / 2, -1, 1)
        return t, np.degrees(np.arccos(cos))

    def _contacts(self, link):
        return p.getContactPoints(self.gripper, self.obj, linkIndexA=link, physicsClientId=self.cid)

    def find_approach(self, cand_world: GraspCandidate, q_open: float):
        """First collision-free approach angle (open gripper vs object and table), or None."""
        for angle in APPROACH_ANGLES_DEG:
            pos, quat, _ = grasp_pose(cand_world, angle)
            self._move_gripper(pos, quat)
            for j in self.fingers:
                p.resetJointState(self.gripper, j, q_open, physicsClientId=self.cid)
                p.setJointMotorControl2(self.gripper, j, p.POSITION_CONTROL, targetPosition=q_open, force=200, physicsClientId=self.cid)
            p.performCollisionDetection(physicsClientId=self.cid)
            if not p.getContactPoints(self.gripper, self.obj, physicsClientId=self.cid) and \
               not p.getContactPoints(self.gripper, self.plane, physicsClientId=self.cid):
                return pos, quat, angle
        return None

    # ---- execution -------------------------------------------------------------------
    def execute(self, cand_world: GraspCandidate, grip_force: float, *, lift: float = 0.2,
                hold_s: float = 2.0, probe: bool = True, force_rate: float = 20.0,
                max_force: float = 40.0, state_id: int | None = None) -> ExecResult:
        """Execute one grasp on the currently settled object. `cand_world` is in world frame.
        Restores `state_id` first if given (the settled state), so trials are paired."""
        if state_id is not None:
            p.restoreState(state_id, physicsClientId=self.cid)
        res = ExecResult(feasible=False, grip_force=grip_force)
        q_open = max(0.0, OPEN_MAX - (cand_world.width / 2 + FINGER_THICK / 2 + CLEARANCE))
        pose = self.find_approach(cand_world, q_open)
        if pose is None:
            res.note = "open gripper collides at every approach angle"
            return res
        pos, quat, angle = pose
        res.approach_deg = angle
        res.feasible = True
        # close with force-limited motors
        for j in self.fingers:
            p.setJointMotorControl2(self.gripper, j, p.POSITION_CONTROL, targetPosition=OPEN_MAX,
                                    force=grip_force, maxVelocity=0.1, physicsClientId=self.cid)
        self._step(int(0.6 / DT))
        res.both_contacts = bool(self._contacts(0)) and bool(self._contacts(1))
        if not res.both_contacts:
            res.note = "fingers missed"
            return res
        rel0 = self._rel_pose()
        z0 = self.object_pose()[0][2]
        # lift over 1 s, then hold
        n_lift = int(1.0 / DT)
        for k in range(1, n_lift + 1):
            p.changeConstraint(self.constraint, jointChildPivot=pos + np.array([0, 0, lift * k / n_lift]),
                               jointChildFrameOrientation=quat, maxForce=2000, physicsClientId=self.cid)
            self._step(1)
        self._step(int(hold_s / DT))
        rel1 = self._rel_pose()
        res.slip_mm, res.pivot_deg = (lambda t, r: (1000 * t, r))(*self._pose_delta(rel0, rel1))
        z1 = self.object_pose()[0][2]
        res.lifted = (z1 - z0) > 0.7 * lift
        res.held = res.lifted and bool(self._contacts(0)) and bool(self._contacts(1)) and res.slip_mm < 20
        if not res.held:
            res.note = "dropped or slipped during lift"
            return res
        if probe:
            res.wrench_at_slip = self._probe(force_rate, max_force)
            res.min_wrench = min(v for k, v in res.wrench_at_slip.items() if k in FRICTION_DIRS)
            res.min_wrench_all = min(res.wrench_at_slip.values())
        return res

    def _probe(self, force_rate: float, max_force: float) -> dict:
        """Ramp an external force (N) or torque (N m, reported divided by rho) about the object
        CoM along each of 12 directions until the object moves in the gripper."""
        sid = p.saveState(physicsClientId=self.cid)
        _, gq = p.getBasePositionAndOrientation(self.gripper, physicsClientId=self.cid)
        Rg = quat_to_mat(gq)
        out = {}
        for kind in ("F", "T"):
            for d in PROBE_DIRS:
                p.restoreState(sid, physicsClientId=self.cid)
                ref = self._rel_pose()
                label = f"{kind}{'+' if d.sum() > 0 else '-'}{'xyz'[int(np.argmax(np.abs(d)))]}"
                d_world = Rg @ d
                mag = 0.0
                n_max = int(max_force / force_rate / DT)
                for k in range(1, n_max + 1):
                    mag = force_rate * k * DT
                    pos = self.object_pose()[0]
                    if kind == "F":
                        p.applyExternalForce(self.obj, -1, mag * d_world, pos, p.WORLD_FRAME, physicsClientId=self.cid)
                    else:
                        p.applyExternalTorque(self.obj, -1, mag * self.rho * d_world, p.WORLD_FRAME, physicsClientId=self.cid)
                    self._step(1)
                    t, r = self._pose_delta(ref, self._rel_pose())
                    if t > 0.01 or r > 10.0:
                        break
                out[label] = float(mag)
        p.restoreState(sid, physicsClientId=self.cid)
        p.removeState(sid, physicsClientId=self.cid)
        return out
