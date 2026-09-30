"""
MuJoCo walking simulation of the RAIL-N.E.D. quadruped built from the EXACT exported CAD.

Everything geometric comes from quadruped/cad/:
  - chassis STLs (bottom_deck, top_deck, body_walls, abad_mount, skid_plate, payload,
    pan_tilt_head, sniffer_arm) are loaded as-is, body frame, mm -> m;
  - leg STLs (leg_shoulder / leg_thigh / leg_shin) are in the LF hip frame; the other three
    legs are mirrored copies exactly as assemble_robot.py places them (RF: mirror Y,
    LH: mirror X, RH: both);
  - joint origins/axes and per-link masses come from leg_kinematics.json; hip point is
    (+-BASE_TO_HIP_X, +-BASE_TO_HIP_Y, HIP_AXIS_Z) from params.py; whole-robot mass is
    MASS_TARGET_KG.
The gait is a plain open-loop trot driven through numerical IK. Servos are modelled as
position actuators torque-limited to the DS3225 stall torque, so if the design cannot
carry itself the video shows it.

Run:  MUJOCO_GL=glfw xvfb-run -a python3 mujoco_walk.py   (writes out/quadruped_walk.mp4)
"""
import json
import os
import re

import imageio.v2 as imageio
import mujoco
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, "..", "cad")
OUT = os.path.join(HERE, "out")
MESH_DIR = os.path.join(OUT, "_meshes")
os.makedirs(MESH_DIR, exist_ok=True)


def read_params():
    src = open(os.path.join(CAD, "params.py")).read()
    def g(name):
        return float(re.search(rf"^{name}\s*=\s*([-\d.]+)", src, re.M).group(1))
    return dict(hx=g("BASE_TO_HIP_X"), hy=g("BASE_TO_HIP_Y"), hz=g("HIP_AXIS_Z"),
                mass=g("MASS_TARGET_KG"), nominal_h=190.0)


P = read_params()
KIN = json.load(open(os.path.join(CAD, "leg_kinematics.json")))
J = KIN["joints"]
LEG_MASS = {k: v["mass_g"] / 1000.0 for k, v in KIN["bodies"].items()}
SERVO_STALL_NM = 25.0 * 0.0980665  # DS3225 25 kgf.cm


def mirrored(name, sx, sy):
    """Write (and return the path of) a copy of <name>.stl mirrored per leg."""
    dst = os.path.join(MESH_DIR, f"{name}_{'m' if sx < 0 else 'p'}{'m' if sy < 0 else 'p'}.stl")
    m = trimesh.load(os.path.join(CAD, f"{name}.stl"))
    if sx < 0 or sy < 0:
        T = np.diag([sx, sy, 1.0, 1.0])
        m.apply_transform(T)
        if sx * sy < 0:
            m.invert()          # single mirror flips winding
    m.export(dst)
    return dst, m


def chassis(name):
    """FreeCAD writes ASCII STL, which MuJoCo can't decode -- re-export as binary, geometry untouched."""
    dst = os.path.join(MESH_DIR, f"{name}.stl")
    trimesh.load(os.path.join(CAD, f"{name}.stl")).export(dst)
    return dst


LEGS = {"LF": (1, 1), "RF": (1, -1), "LH": (-1, 1), "RH": (-1, -1)}   # name -> (sx, sy)

# chassis part -> (rgba, share of body mass). Shares only distribute the mass left after the legs.
CHASSIS = {
    "bottom_deck":   ((0.20, 0.22, 0.26, 1), 0.10),
    "top_deck":      ((0.22, 0.30, 0.42, 1), 0.10),
    "body_walls":    ((0.30, 0.34, 0.40, 1), 0.07),
    "abad_mount":    ((0.85, 0.45, 0.12, 1), 0.12),
    "skid_plate":    ((0.15, 0.15, 0.15, 1), 0.03),
    "payload":       ((0.35, 0.60, 0.85, 0.55), 0.50),
    "pan_tilt_head": ((0.10, 0.60, 0.55, 1), 0.04),
    "sniffer_arm":   ((0.10, 0.60, 0.55, 1), 0.04),
}
LEG_COLORS = {"shoulder": (0.85, 0.45, 0.12, 1), "thigh": (0.90, 0.70, 0.15, 1), "shin": (0.30, 0.65, 0.35, 1)}
LEG_FILES = {"shoulder": "leg_shoulder", "thigh": "leg_thigh", "shin": "leg_shin"}


def build_xml():
    body_mass = P["mass"] - 4 * sum(LEG_MASS.values())
    share_sum = sum(s for _, s in CHASSIS.values())
    assets, base_geoms, legs_xml, acts = [], [], [], []
    foot_local = {}
    for n, (rgba, share) in CHASSIS.items():
        assets.append(f'<mesh name="{n}" file="{chassis(n)}" scale="0.001 0.001 0.001"/>')
        col = "1" if n == "skid_plate" else "0"
        base_geoms.append(
            f'<geom type="mesh" mesh="{n}" rgba="{" ".join(map(str, rgba))}" mass="{body_mass * share / share_sum:.4f}" '
            f'contype="{col}" conaffinity="{col}"/>')

    for leg, (sx, sy) in LEGS.items():
        hip = (sx * P["hx"] / 1000, sy * P["hy"] / 1000, P["hz"] / 1000)
        bodies = {}
        for part, f in LEG_FILES.items():
            path, m = mirrored(f, sx, sy)
            assets.append(f'<mesh name="{leg}_{part}" file="{path}" scale="0.001 0.001 0.001"/>')
            bodies[part] = path
            if part == "shin":
                v = m.vertices
                low = v[v[:, 2] < v[:, 2].min() + 2.0]
                foot_local[leg] = low.mean(axis=0) / 1000.0      # physical foot tip, hip frame, m

        def geom(part):
            return (f'<geom type="mesh" mesh="{leg}_{part}" rgba="{" ".join(map(str, LEG_COLORS[part]))}" '
                    f'mass="{LEG_MASS[part]:.4f}" contype="0" conaffinity="0"/>')

        ab = np.array(J["abad"]["origin"]) / 1000
        hp = np.array(J["hip_pitch"]["origin"]) / 1000 * np.array([sx, sy, 1])
        kn = np.array(J["knee"]["origin"]) / 1000 * np.array([sx, sy, 1])
        ax_ab = np.array(J["abad"]["axis"])
        ax_p = np.array(J["hip_pitch"]["axis"])
        ax_k = np.array(J["knee"]["axis"])
        fx, fy, fz = foot_local[leg]
        fmt = lambda a: " ".join(f"{x:.6f}" for x in a)
        legs_xml.append(f'''
    <body name="{leg}_abad" pos="{fmt(hip)}">
      <joint name="{leg}_abad" type="hinge" axis="{fmt(ax_ab)}" pos="{fmt(ab)}" range="-25 25" damping="0.05" armature="0.004"/>
      {geom("shoulder")}
      <body name="{leg}_thigh">
        <joint name="{leg}_hip" type="hinge" axis="{fmt(ax_p)}" pos="{fmt(hp)}" range="-90 90" damping="0.05" armature="0.004"/>
        {geom("thigh")}
        <body name="{leg}_shin">
          <joint name="{leg}_knee" type="hinge" axis="{fmt(ax_k)}" pos="{fmt(kn)}" range="-150 150" damping="0.05" armature="0.004"/>
          {geom("shin")}
          <geom type="sphere" size="0.007" pos="{fx:.6f} {fy:.6f} {fz + 0.007:.6f}" rgba="0.1 0.1 0.1 1"
                friction="1.2 0.01 0.001" contype="1" conaffinity="1" mass="0.001"/>
          <site name="{leg}_foot" pos="{fx:.6f} {fy:.6f} {fz:.6f}" size="0.004" rgba="1 0 0 1"/>
        </body>
      </body>
    </body>''')
        for j in ("abad", "hip", "knee"):
            acts.append(f'<position name="{leg}_{j}" joint="{leg}_{j}" kp="30" kv="0.8" '
                        f'forcerange="-{SERVO_STALL_NM:.3f} {SERVO_STALL_NM:.3f}"/>')

    return f'''<mujoco model="rail_ned_quadruped">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.001" integrator="implicitfast" gravity="0 0 -9.81"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <quality shadowsize="4096"/>
    <headlight ambient="0.45 0.45 0.45" diffuse="0.6 0.6 0.6"/>
  </visual>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.75 0.85 0.95" rgb2="0.95 0.95 0.97" width="512" height="512"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.36 0.41 0.49" rgb2="0.27 0.31 0.39" width="512" height="512"/>
    <material name="grid" texture="grid" texrepeat="12 12" texuniform="true" reflectance="0.03"/>
    {chr(10).join("    " + a for a in assets)}
  </asset>
  <worldbody>
    <light pos="0.5 -0.5 2.0" dir="-0.2 0.2 -1" directional="true" diffuse="0.8 0.8 0.8" castshadow="true"/>
    <geom name="floor" type="plane" size="20 20 0.1" material="grid" friction="1.0 0.01 0.001"/>
    <body name="base" pos="0 0 0.4">
      <freejoint name="root"/>
      {chr(10).join("      " + g for g in base_geoms)}
      {"".join(legs_xml)}
    </body>
  </worldbody>
  <actuator>
    {chr(10).join("    " + a for a in acts)}
  </actuator>
</mujoco>''', foot_local


class Walker:
    def __init__(self):
        xml, _ = build_xml()
        open(os.path.join(OUT, "rail_ned_quadruped.xml"), "w").write(xml)
        self.m = mujoco.MjModel.from_xml_string(xml)
        self.d = mujoco.MjData(self.m)
        self.dk = mujoco.MjData(self.m)      # kinematics-only copy, base at identity
        self.leg_j = {l: [self.m.joint(f"{l}_{j}").qposadr[0] for j in ("abad", "hip", "knee")] for l in LEGS}
        self.leg_dof = {l: [self.m.joint(f"{l}_{j}").dofadr[0] for j in ("abad", "hip", "knee")] for l in LEGS}
        self.site = {l: self.m.site(f"{l}_foot").id for l in LEGS}
        self.act = {l: [self.m.actuator(f"{l}_{j}").id for j in ("abad", "hip", "knee")] for l in LEGS}
        self.q = {l: np.zeros(3) for l in LEGS}
        self.dk.qpos[:7] = [0, 0, 0, 1, 0, 0, 0]
        mujoco.mj_forward(self.m, self.dk)
        self.foot0 = {l: self.dk.site_xpos[self.site[l]].copy() for l in LEGS}   # zero pose, body frame
        # nominal stance: same lateral/fore-aft placement as the zero pose, foot HIP_AXIS_Z-190mm
        self.stance = {l: np.array([self.foot0[l][0], self.foot0[l][1], (P["hz"] - P["nominal_h"]) / 1000])
                       for l in LEGS}

    def ik(self, leg, target, q0):
        q = q0.copy()
        for _ in range(60):
            for a, adr in zip(q, self.leg_j[leg]):
                pass
            self.dk.qpos[self.leg_j[leg]] = q
            mujoco.mj_kinematics(self.m, self.dk)
            mujoco.mj_comPos(self.m, self.dk)
            err = target - self.dk.site_xpos[self.site[leg]]
            if np.linalg.norm(err) < 1e-5:
                break
            jac = np.zeros((3, self.m.nv))
            mujoco.mj_jacSite(self.m, self.dk, jac, None, self.site[leg])
            Jl = jac[:, self.leg_dof[leg]]
            dq = Jl.T @ np.linalg.solve(Jl @ Jl.T + 1e-6 * np.eye(3), err)
            q = np.clip(q + dq, np.radians([-25, -90, -150]), np.radians([25, 90, 150]))
        return q

    def foot_target(self, leg, t, v, period=0.8, duty=0.6, swing_h=0.035):
        phase_off = {"LF": 0.0, "RH": 0.0, "RF": 0.5, "LH": 0.5}[leg]
        ph = ((t / period) + phase_off) % 1.0
        stride = v * period * duty
        p = self.stance[leg].copy()
        if ph < duty:                                   # stance: foot moves backward relative to body
            u = ph / duty
            p[0] += stride * (0.5 - u)
        else:                                           # swing: forward arc
            u = (ph - duty) / (1 - duty)
            s = 0.5 - 0.5 * np.cos(np.pi * u)
            p[0] += stride * (-0.5 + s)
            p[2] += swing_h * np.sin(np.pi * u)
        return p

    def init_pose(self):
        for l in LEGS:
            self.q[l] = self.ik(l, self.stance[l], np.radians([0, 20, -40]))
            self.d.qpos[self.leg_j[l]] = self.q[l]
            self.d.ctrl[self.act[l]] = self.q[l]
        self.d.qpos[:7] = [0, 0, 0.4, 1, 0, 0, 0]
        mujoco.mj_forward(self.m, self.d)
        lowest = min(self.d.site_xpos[self.site[l]][2] for l in LEGS)
        self.d.qpos[2] = 0.4 - lowest + 0.004
        mujoco.mj_forward(self.m, self.d)

    def step(self, t, v):
        for l in LEGS:
            self.q[l] = self.ik(l, self.foot_target(l, t, v), self.q[l])
            self.d.ctrl[self.act[l]] = self.q[l]
        mujoco.mj_step(self.m, self.d)


def caption(img, lines):
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im, "RGBA")
    try:
        f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        f2 = ImageFont.truetype("DejaVuSans.ttf", 17)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    dr.rectangle([0, 0, im.width, 78], fill=(11, 42, 91, 225))
    dr.text((18, 10), lines[0], font=f1, fill=(255, 255, 255, 255))
    dr.text((18, 46), lines[1], font=f2, fill=(205, 218, 240, 255))
    dr.rectangle([0, im.height - 34, im.width, im.height], fill=(11, 42, 91, 225))
    dr.text((18, im.height - 27), lines[2], font=f2, fill=(255, 255, 255, 255))
    return np.array(im)


def main(seconds=14.0, fps=30, v_cmd=0.10):
    w = Walker()
    w.init_pose()
    m, d = w.m, w.d
    rend = mujoco.Renderer(m, 720, 1280)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    frames, log = [], []
    stand_t = 2.0
    steps_per_frame = int(round(1.0 / (fps * m.opt.timestep)))
    n_frames = int(seconds * fps)
    for i in range(n_frames):
        for _ in range(steps_per_frame):
            t = d.time
            if t < stand_t:
                v = 0.0
            else:
                v = v_cmd * min(1.0, (t - stand_t) / 1.6)
            w.step(max(t - stand_t, 0.0) if t >= stand_t else 0.0, v)
        base = d.qpos[:3].copy()
        cam.lookat[:] = [base[0], base[1], 0.10]
        cam.distance = 0.95
        cam.elevation = -18
        cam.azimuth = 35 + 40 * np.sin(i / n_frames * np.pi)      # gentle sweep
        rend.update_scene(d, camera=cam)
        img = rend.render()
        frames.append(caption(img, [
            "RAIL-N.E.D. quadruped  |  MuJoCo simulation of the exported CAD",
            f"trot gait, cmd {v_cmd*100:.0f} cm/s  |  12 x DS3225 servos, torque-limited to {SERVO_STALL_NM:.2f} N.m  |  mass {P['mass']:.1f} kg",
            f"t = {d.time:5.1f} s    forward = {base[0]*100:5.1f} cm    body height = {base[2]*1000:4.0f} mm     (physics sim, not the physical robot)"]))
        log.append((d.time, *base, *d.qpos[3:7]))
    path = os.path.join(OUT, "quadruped_walk.mp4")
    imageio.mimsave(path, frames, fps=fps, codec="libx264", quality=8, macro_block_size=1)
    np.save(os.path.join(OUT, "trajectory.npy"), np.array(log))
    print("saved", path, "final base pos", np.round(d.qpos[:3], 3), "quat", np.round(d.qpos[3:7], 3))


if __name__ == "__main__":
    main()
