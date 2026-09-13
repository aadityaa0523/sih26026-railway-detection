"""
LF leg module (3-DOF: ab/ad, hip-pitch, knee) for the SpotMicro-scale quadruped -- V3 SPEC.

Built in the LF HIP FRAME: origin = centre of the ab/ad servo's horn face = CHAMP's
<leg>_hip_joint origin (params.py V3 SPEC). Body axes: +X front, +Y left/outboard, +Z up.
Exported at CHAMP's ZERO POSE (all 3 joints at 0 deg, leg straight down) --
docs/champ-research.md #4: "All joints at zero position will result[] the robot's legs to
be fully stretched towards the ground."

---- Why this design replaces the v2 leg (README "Mechanics check") ----
The old leg had 4/12 working joints, no ab/ad joint, no knee actuator, a coplanar
thigh/shin butt joint, and link lengths copied from CHAMP's VISUAL box sizes instead of
its real kinematic joint-to-joint distances. This module fixes all four:
  1. Ab/ad: the servo itself is a CHASSIS part (sits at hip-frame X<=0, shaft along +X,
     horn face at X=0) -- out of this script's lane. This module's SHOULDER bolts to that
     horn at the origin. No far-side idler bearing: one would need material at hip-frame
     X<0 (chassis' own envelope, forbidden by the V3 contract) -- so ab/ad is carried by
     the servo's own output bearing only (documented single-sided support, see report).
  2. Hip pitch: a real DS3225 servo lives INSIDE the shoulder (shaft axis Y, per
     docs/champ-research.md #3.1's "Upper Leg joints rotate in the Y axis"), its horn
     bolts through to the THIGH via a 25T-horn-style bolt circle, with a 625ZZ idler
     bearing on the thigh's opposite face -- supported on both sides.
  3. Knee: direct drive (SpotMicro-style, preferred per the brief) -- a second DS3225
     lives in the THIGH's lower end, horn bolts to the SHIN, 625ZZ idler bearing opposite.
  4. Thigh and shin are NEVER coplanar: each occupies its own, disjoint band along Y (the
     shared rotation-axis direction for both hip-pitch and knee). Since a rotation about a
     Y-parallel axis preserves every point's Y-coordinate, and ab/ad (the one X-axis joint,
     the root of this chain) rotates shoulder+thigh+shin RIGIDLY together (it cannot change
     their Y-bands relative to each other), these bands stay disjoint FOR EVERY POSE in the
     swept ranges -- self-collision between shoulder/thigh/shin is avoided BY CONSTRUCTION,
     not just checked after the fact. The sweep below confirms this numerically anyway.
  Joint-to-joint distances (hip-pitch axis, knee axis, foot) are all held at the SAME
  local Y = L0 (see below) -- exactly the classic SpotMicro/CHAMP planar-leg convention
  (a single lateral "hip offset" carries the whole HIP_TO_FOOT_Y, thigh+shin are a purely
  planar 2-link chain from there) -- so THIGH_LENGTH/SHIN_LENGTH/HIP_TO_FOOT_Y hit their
  targets exactly, independent of how wide the PHYSICAL link bodies are (which is a
  separate, purely mechanical band-offset chosen for print/assembly clearance).

---- Sourcing / honesty convention (every number is cited, a design choice, or flagged) ----
  - DS3225 servo: 40x20x40.5mm case, cited via web search (wiki.52pi.com "D-0001" product
    page: 67g, 21kgf-cm@5V/25kgf-cm@6.8V, "Size: 40x20x40.5mm" -- matches params.py's
    SERVO_BODY_L/W/H exactly, no discrepancy found; params.py's own SERVO_TAB_SPACING(49.5)/
    SERVO_SHAFT_OFFSET(10)/SERVO_TAB_HEIGHT(27.7) are flagged there as "drawing read --
    verify" and no numeric datasheet page contradicting them was found in this pass, so
    they are used as-is (no local override).
  - 25T aluminium round servo horn: Pololu product 3433 (Power HD SR8 25T horn) -- "two
    general-purpose mounting holes are threaded for M3 screws" "located 15.0mm and 19.0mm
    from the axis of rotation", weight 1.8g. This module reuses this project's EXISTING
    KNEE_HORN_HOLE_DIA(6mm)/KNEE_BOLT_CIRCLE_DIA(30mm, i.e. 15mm radius) convention for
    every horn interface (ab/ad, hip-pitch, knee) -- matching the Pololu horn's own
    15mm-radius hole ring -- https://www.pololu.com/product/3433
  - 625ZZ / F625ZZ idler bearing: bore 5mm, OD 16mm, width 5mm -- cited (BC Robotics
    product page; Misumi/NTN/EZO catalog listings agree). The bearing's own stationary
    pin/shoulder-bolt (threading into the parent body, carrying the inner race across the
    joint gap) is NOT separately modeled as its own solid -- ASSUMPTION, same convention
    this project already uses for small fasteners (tab screws, etc.) -- represented only
    by the bearing envelope + its mounting bore.
  - Foot cap: a bought rubber/TPU cap over a rounded (domed) boss tip -- NOT modeled,
    same documented-assumption level as build_lower_leg.py's (removed) foot cap.
  - HIP_TO_FOOT_Y_TARGET (55mm) is used AS the "L0" hip-offset with zero further lateral
    drift -- hits the 55mm target exactly (0mm off center of the +-10mm band).
  - Everything else (WIDE_T, GAP, bar cross-section, bearing-pocket depth, cable channel)
    is a plain DESIGN CHOICE, called out inline where it's set.

Run: "C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_leg_module.py
"""
import json
import math

import FreeCAD as App
import Part

import params
from geometry_helpers import chassis_envelope

CAD_DIR = params.CAD_DIR

# ================================ leg-local constants ======================================
# (leg-specific -- per the task's own boundary rules, params.py/geometry_helpers.py are not
# touched; anything needed only by this leg lives here.)
L0 = params.HIP_TO_FOOT_Y_TARGET     # 55.0mm -- ab/ad axis -> hip-pitch axis -> knee axis ->
                                       # foot, ALL held at this one local Y (see docstring).
GAP = 3.0                             # mm, air gap between adjacent moving bodies -- real
                                       # assembly clearance + FreeCAD boolean touching-face
                                       # safety margin (design choice).
WALL = params.WALL                    # 4.0mm, reused

SBW, SBH, SBL = params.SERVO_BODY_W, params.SERVO_BODY_H, params.SERVO_BODY_L  # 20/40.5/40mm
# Standard hobby-servo case: shaft emerges through the SBH ("base to top of case") face, so
# for a Y-axis shaft (hip-pitch, knee -- docs/champ-research.md #3.1) the servo sits with its
# SBH dimension along Y (shaft depth), SBL(40mm, "length", contains the shaft-offset-10mm
# axis) along Z, SBW(20mm) along X. Tab screws are NOT modeled (design choice -- the horn
# bolt circle is the real structural interface; a friction-fit + optional 2x self-tapping
# screw into the case sides is the honest real-world retention, not worth a full internal
# hollow-housing rebuild here) -- flagged, see report.

HORN_HOLE_DIA = params.KNEE_HORN_HOLE_DIA   # 6.0mm, 25T spline clearance (existing convention)
HORN_BC_DIA = params.KNEE_BOLT_CIRCLE_DIA   # 30.0mm (15mm radius, matches the Pololu 25T horn)
HORN_DISC_DIA = 36.0                         # mm, design choice, horn envelope outer dia
                                               # (Pololu/thinkrobotics 25T horns run ~35mm long)
HORN_THICKNESS = GAP                         # mm -- the horn disc exactly fills the joint gap

BEARING_OD, BEARING_BORE, BEARING_W = 16.0, 5.0, 5.0   # 625ZZ, cited (see docstring)
BEARING_POCKET_DEPTH = 3.0   # mm, design choice -- shallow recess, bearing sits mostly proud

# Bar cross-section (X-width), reused for shoulder + thigh + shin so every horn interface is
# the SAME hardware everywhere (existing project convention). Must clear the wider of: the
# servo body + walls (20+2*4=28mm), or the 30mm horn bolt circle + walls (30+2*4=38mm).
BAR_X = 40.0
# Shoulder's own Z half-height: must clear the servo pocket half-length (SBL/2=20mm) + wall.
BAR_Z_HALF = 24.0

MASS_DS3225_G = 67.0   # g, cited -- wiki.52pi.com "D-0001" DS3225 product page.

FOOT_BOSS_DIA = 22.0        # mm, reused from the (removed) v2 foot-boss convention
FOOT_BOSS_HEIGHT = 16.0     # mm
FOOT_CAP_BORE_DIA = 12.0    # mm, blind bore for the bought rubber/TPU foot cap's own spigot
FOOT_CAP_BORE_DEPTH = 8.0   # mm

# ---- key joint/body coordinates (hip frame, all exact per the V3 contract) ----
ABAD_ORIGIN = App.Vector(0, 0, 0)
ABAD_AXIS = App.Vector(1, 0, 0)
HIP_PITCH_ORIGIN = App.Vector(0, L0, 0)
HIP_PITCH_AXIS = App.Vector(0, 1, 0)
KNEE_Z = -params.THIGH_LENGTH
KNEE_ORIGIN = App.Vector(0, L0, KNEE_Z)
KNEE_AXIS = App.Vector(0, 1, 0)
FOOT_Z = KNEE_Z - params.SHIN_LENGTH
FOOT_POINT = App.Vector(0, L0, FOOT_Z)

# ---- physical Y-bands (disjoint by construction -- see docstring) ----
SHOULDER_Y0, SHOULDER_Y1 = -20.0, L0                 # [-20, 55]
THIGH_Y_IN = L0 + GAP                                # 58, inboard (horn) face, both segments
THIGH_Y_TOP_OUT = THIGH_Y_IN + 14.0                  # 72, narrow top segment's outboard face
WIDE_T = SBH + 3.5                                   # 44.0mm, knee-servo segment width
THIGH_Y_BOT_OUT = THIGH_Y_IN + WIDE_T                # 102, wide bottom segment's outboard face
SHIN_Y_IN = THIGH_Y_BOT_OUT + GAP                    # 105
SHIN_T = 12.0
SHIN_Y_OUT = SHIN_Y_IN + SHIN_T                       # 117


def cut_bolt_circle_3d(shape, center, axis, thickness, hole_dia, bc_dia, n=4):
    """Cut a center clearance hole + an n-hole M3-clearance (1.6mm) bolt circle, at an
    ARBITRARY 3D center point and bore axis, `thickness` mm long CENTERED on `center` along
    `axis`. geometry_helpers.cut_bolt_circle hardcodes "holes in local XZ, bored through +Y
    starting at y=0" (a good fit for a part whose relevant face sits at its own local Y=0,
    like the old flat leg bars) -- this module's ab/ad interface (bored through X) and its
    hip-pitch/knee interfaces (sitting mid-part, not at a Y=0 face) don't fit that hardcoded
    convention, so this is a small, deliberately-generalized sibling, same 4-hole/M3 idiom.
    """
    axis = App.Vector(axis)
    axis.normalize()
    ref = App.Vector(0, 0, 1) if abs(axis.z) < 0.9 else App.Vector(1, 0, 0)
    u = axis.cross(ref)
    u.normalize()
    v = axis.cross(u)
    v.normalize()
    start = center - axis * (thickness / 2.0)
    shape = shape.cut(Part.makeCylinder(hole_dia / 2.0, thickness, start, axis))
    for i in range(n):
        ang = math.radians(i * 360.0 / n)
        pt = center + u * (bc_dia / 2.0 * math.cos(ang)) + v * (bc_dia / 2.0 * math.sin(ang))
        shape = shape.cut(Part.makeCylinder(1.6, thickness, pt - axis * (thickness / 2.0), axis))
    return shape


def cut_bearing_pocket(shape, center, axis):
    """Shallow BEARING_OD recess + a BEARING_BORE through-hole for the (unmodeled, see
    docstring) stationary idler pin -- at an arbitrary 3D center/axis, same reasoning as
    cut_bolt_circle_3d above."""
    axis = App.Vector(axis)
    axis.normalize()
    shape = shape.cut(Part.makeCylinder(BEARING_OD / 2.0, BEARING_POCKET_DEPTH, center, axis))
    pin_start = center - axis * 2.0
    return shape.cut(Part.makeCylinder(BEARING_BORE / 2.0, BEARING_POCKET_DEPTH + 4.0, pin_start, axis))


def build_shoulder():
    """Ab/ad horn interface (Y~0) -> hip-pitch servo pocket -> hip-pitch horn interface
    (Y=L0). Band: Y in [-20, 55]."""
    box = Part.makeBox(BAR_X, SHOULDER_Y1 - SHOULDER_Y0, 2 * BAR_Z_HALF,
                        App.Vector(0, SHOULDER_Y0, -BAR_Z_HALF))
    # Ab/ad horn interface: through-bolted (a real M3x40 screw is unusual but simplest to
    # model; design choice), centered exactly on the ab/ad axis (world origin).
    box = cut_bolt_circle_3d(box, App.Vector(BAR_X / 2.0, 0, 0), ABAD_AXIS, BAR_X,
                              HORN_HOLE_DIA, HORN_BC_DIA)
    # Hip-pitch servo pocket: blind, recessed from the Y=L0 face inward by the servo's own
    # base-to-horn depth (SBH) -- shaft points +Y, toward the thigh.
    pocket = Part.makeBox(SBW, SBH, SBL, App.Vector((BAR_X - SBW) / 2.0, L0 - SBH, -SBL / 2.0))
    box = box.cut(pocket)
    # Hip-pitch horn bolt circle, cut into the pocket's open (outboard) face.
    box = cut_bolt_circle_3d(box, HIP_PITCH_ORIGIN, HIP_PITCH_AXIS, 6.0, HORN_HOLE_DIA, HORN_BC_DIA)
    # Cable routing channel (item 7): one shallow groove along the front (X=0) face, from
    # just past the ab/ad interface to just short of the servo pocket.
    ch_z0, ch_z1 = -BAR_Z_HALF + 10.0, BAR_Z_HALF - 10.0
    channel = Part.makeBox(params.CABLE_CHANNEL_WIDTH, params.CABLE_CHANNEL_DEPTH, ch_z1 - ch_z0,
                            App.Vector(BAR_X / 2.0 - params.CABLE_CHANNEL_WIDTH / 2.0, SHOULDER_Y0, ch_z0))
    box = box.cut(channel)
    return box


def build_thigh():
    """Hip-pitch horn interface (Y=THIGH_Y_IN, narrow band) -> idler bearing opposite ->
    knee servo pocket (wide band) -> knee horn interface (Y=THIGH_Y_BOT_OUT)."""
    z_top, z_mid = 19.0, -70.0
    z_bot = KNEE_Z - SBL / 2.0 - WALL   # -131.5, clears the knee pocket's own Z-extent
    top_seg = Part.makeBox(BAR_X, THIGH_Y_TOP_OUT - THIGH_Y_IN, z_top - z_mid,
                            App.Vector(0, THIGH_Y_IN, z_mid))
    bot_seg = Part.makeBox(BAR_X, THIGH_Y_BOT_OUT - THIGH_Y_IN, z_mid - z_bot,
                            App.Vector(0, THIGH_Y_IN, z_bot))
    shape = top_seg.fuse(bot_seg)

    shape = cut_bolt_circle_3d(shape, HIP_PITCH_ORIGIN, HIP_PITCH_AXIS, 6.0, HORN_HOLE_DIA, HORN_BC_DIA)
    shape = cut_bearing_pocket(shape, App.Vector(BAR_X / 2.0, THIGH_Y_TOP_OUT, 0), HIP_PITCH_AXIS)

    pocket = Part.makeBox(SBW, SBH, SBL,
                           App.Vector((BAR_X - SBW) / 2.0, THIGH_Y_BOT_OUT - SBH, KNEE_Z - SBL / 2.0))
    shape = shape.cut(pocket)
    knee_horn_origin = App.Vector(BAR_X / 2.0, THIGH_Y_BOT_OUT, KNEE_Z)
    shape = cut_bolt_circle_3d(shape, knee_horn_origin, KNEE_AXIS, 6.0, HORN_HOLE_DIA, HORN_BC_DIA)

    # Cable routing channel (item 7): front (X=0) face, between the bearing boss and the
    # knee pocket.
    ch_z0, ch_z1 = z_bot + SBL + 10.0, -10.0
    channel = Part.makeBox(params.CABLE_CHANNEL_WIDTH, params.CABLE_CHANNEL_DEPTH, ch_z1 - ch_z0,
                            App.Vector(BAR_X / 2.0 - params.CABLE_CHANNEL_WIDTH / 2.0, THIGH_Y_IN, ch_z0))
    shape = shape.cut(channel)
    return shape


def build_shin():
    """Knee horn interface (Y=SHIN_Y_IN) -> idler bearing opposite -> rounded foot tip."""
    z_top = KNEE_Z + 19.0
    z_bar_bot = FOOT_Z + FOOT_BOSS_HEIGHT
    bar = Part.makeBox(BAR_X, SHIN_Y_OUT - SHIN_Y_IN, z_top - z_bar_bot,
                        App.Vector(0, SHIN_Y_IN, z_bar_bot))

    knee_horn_origin = App.Vector(BAR_X / 2.0, SHIN_Y_IN, KNEE_Z)
    bar = cut_bolt_circle_3d(bar, knee_horn_origin, KNEE_AXIS, 6.0, HORN_HOLE_DIA, HORN_BC_DIA)
    bar = cut_bearing_pocket(bar, App.Vector(BAR_X / 2.0, SHIN_Y_OUT, KNEE_Z), KNEE_AXIS)

    fx, fy = BAR_X / 2.0, (SHIN_Y_IN + SHIN_Y_OUT) / 2.0
    sphere_z = FOOT_Z + FOOT_BOSS_DIA / 2.0
    boss_cyl = Part.makeCylinder(FOOT_BOSS_DIA / 2.0, z_bar_bot - sphere_z,
                                  App.Vector(fx, fy, sphere_z), App.Vector(0, 0, 1))
    boss_sphere = Part.makeSphere(FOOT_BOSS_DIA / 2.0, App.Vector(fx, fy, sphere_z))
    bar = bar.fuse(boss_cyl).fuse(boss_sphere)
    # Blind bore for the bought rubber/TPU foot cap's own spigot -- cap itself NOT modeled
    # (ASSUMPTION, same level as the removed v2 foot cap).
    cap_bore = Part.makeCylinder(FOOT_CAP_BORE_DIA / 2.0, FOOT_CAP_BORE_DEPTH,
                                  App.Vector(fx, fy, FOOT_Z), App.Vector(0, 0, 1))
    bar = bar.cut(cap_bore)

    ch_z0, ch_z1 = z_bar_bot + FOOT_BOSS_HEIGHT + 5.0, KNEE_Z - 10.0
    channel = Part.makeBox(params.CABLE_CHANNEL_WIDTH, params.CABLE_CHANNEL_DEPTH, ch_z1 - ch_z0,
                            App.Vector(BAR_X / 2.0 - params.CABLE_CHANNEL_WIDTH / 2.0, SHIN_Y_IN, ch_z0))
    bar = bar.cut(channel)
    return bar


def build_bought_parts():
    """Hip-pitch + knee horns (25T-style discs) and idler bearings (625ZZ), as separate
    solids -- see docstring for citations. Each sized/placed to exactly fill its joint gap."""
    def horn(origin):
        h = Part.makeCylinder(HORN_DISC_DIA / 2.0, HORN_THICKNESS, origin, App.Vector(0, 1, 0))
        return cut_bolt_circle_3d(h, origin + App.Vector(0, HORN_THICKNESS / 2.0, 0),
                                   App.Vector(0, 1, 0), HORN_THICKNESS + 0.2, HORN_HOLE_DIA, HORN_BC_DIA)

    def bearing(face_center, axis):
        axis = App.Vector(axis)
        axis.normalize()
        base = face_center - axis * BEARING_POCKET_DEPTH
        ring = Part.makeCylinder(BEARING_OD / 2.0, BEARING_W, base, axis)
        bore = Part.makeCylinder(BEARING_BORE / 2.0, BEARING_W + 0.2, base - axis * 0.1, axis)
        return ring.cut(bore)

    hip_pitch_horn = horn(App.Vector(BAR_X / 2.0, L0, 0))
    knee_horn = horn(App.Vector(BAR_X / 2.0, THIGH_Y_BOT_OUT, KNEE_Z))
    hip_pitch_bearing = bearing(App.Vector(BAR_X / 2.0, THIGH_Y_TOP_OUT, 0), HIP_PITCH_AXIS)
    knee_bearing = bearing(App.Vector(BAR_X / 2.0, SHIN_Y_OUT, KNEE_Z), KNEE_AXIS)
    return {"hip_pitch_horn": hip_pitch_horn, "knee_horn": knee_horn,
            "hip_pitch_bearing": hip_pitch_bearing, "knee_bearing": knee_bearing}


# ================================ build + export ============================================
# .cut()/.fuse() chains can hand back a Part.Compound wrapping the one real solid instead of
# a bare Solid (Part.Compound has no .CenterOfMass) -- normalize to the real solid right away,
# same "never trust the raw Compound" convention as geometry_helpers.load_step_solids.
def _solid(shape):
    return shape.Solids[0] if shape.Solids else shape


shoulder = _solid(build_shoulder())
thigh = _solid(build_thigh())
shin = _solid(build_shin())
bought = {k: _solid(v) for k, v in build_bought_parts().items()}

print("=== Solid validity ===")
for name, shp in [("shoulder", shoulder), ("thigh", thigh), ("shin", shin)] + list(bought.items()):
    print(f"  {name}: isValid={shp.isValid()} volume={shp.Volume:.0f}mm^3")

doc = App.newDocument("leg_module")
objs = {}
for name, shp in [("leg_shoulder", shoulder), ("leg_thigh", thigh), ("leg_shin", shin)]:
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shp
    objs[name] = obj
    doc.recompute()
    Part.export([obj], f"{CAD_DIR}/{name}.step")
    Part.export([obj], f"{CAD_DIR}/{name}.stl")
    sub_doc = App.newDocument(name)
    sub_obj = sub_doc.addObject("Part::Feature", name)
    sub_obj.Shape = shp
    sub_doc.recompute()
    sub_doc.saveAs(f"{CAD_DIR}/{name}.FCStd")
    App.closeDocument(sub_doc.Name)
print("Saved: leg_shoulder.*, leg_thigh.*, leg_shin.* (.FCStd/.step/.stl)")

bought_objs = []
for name, shp in bought.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shp
    bought_objs.append(obj)
doc.recompute()
Part.export(bought_objs, f"{CAD_DIR}/leg_bought.step")
print("Saved: leg_bought.step (hip-pitch horn+bearing, knee horn+bearing)")

doc.saveAs(f"{CAD_DIR}/leg_module_zero.FCStd")
print("Saved: leg_module_zero.FCStd (all bodies at zero pose)")

# ================================ leg_kinematics.json =======================================
def body_mass_com(shape, servo_com=None):
    mass_printed = shape.Volume * 0.45 * params.DENSITY_PETG   # 45% infill PETG, ASSUMPTION
    com_printed = shape.CenterOfMass
    if servo_com is None:
        return mass_printed, (com_printed.x, com_printed.y, com_printed.z)
    total = mass_printed + MASS_DS3225_G
    com = (com_printed * mass_printed + servo_com * MASS_DS3225_G) / total
    return total, (com.x, com.y, com.z)


shoulder_servo_com = App.Vector(BAR_X / 2.0, L0 - SBH / 2.0, 0)
thigh_servo_com = App.Vector(BAR_X / 2.0, THIGH_Y_BOT_OUT - SBH / 2.0, KNEE_Z)

shoulder_mass, shoulder_com = body_mass_com(shoulder, shoulder_servo_com)
thigh_mass, thigh_com = body_mass_com(thigh, thigh_servo_com)
shin_mass, shin_com = body_mass_com(shin, None)

kinematics = {
    "frame": "LF hip frame, mm, zero pose (all joints 0, leg straight down)",
    "joints": {
        "abad": {"origin": [ABAD_ORIGIN.x, ABAD_ORIGIN.y, ABAD_ORIGIN.z], "axis": [1, 0, 0]},
        "hip_pitch": {"origin": [HIP_PITCH_ORIGIN.x, HIP_PITCH_ORIGIN.y, HIP_PITCH_ORIGIN.z], "axis": [0, 1, 0]},
        "knee": {"origin": [KNEE_ORIGIN.x, KNEE_ORIGIN.y, KNEE_ORIGIN.z], "axis": [0, 1, 0]},
    },
    "foot": [FOOT_POINT.x, FOOT_POINT.y, FOOT_POINT.z],
    "hip_to_foot_y_achieved_mm": L0,
    "bodies": {
        "shoulder": {"step_files": ["leg_shoulder.step"], "carries_servo": "hip_pitch (DS3225)",
                     "mass_g": round(shoulder_mass, 1), "com_mm": [round(c, 2) for c in shoulder_com]},
        "thigh": {"step_files": ["leg_thigh.step"], "carries_servo": "knee (DS3225)",
                  "mass_g": round(thigh_mass, 1), "com_mm": [round(c, 2) for c in thigh_com]},
        "shin": {"step_files": ["leg_shin.step"], "carries_servo": None,
                 "mass_g": round(shin_mass, 1), "com_mm": [round(c, 2) for c in shin_com]},
    },
    "bought_parts_step_file": "leg_bought.step",
}
with open(f"{CAD_DIR}/leg_kinematics.json", "w") as f:
    json.dump(kinematics, f, indent=2)
print(f"Saved: leg_kinematics.json")
print(f"Total leg mass (shoulder+thigh+shin, incl. 2x DS3225): "
      f"{shoulder_mass + thigh_mass + shin_mass:.1f}g")

# ================================ verification ===============================================
report_lines = []


def log(s):
    print(s)
    report_lines.append(s)


log("\n=== Verification ===")
log("Mirrors: right legs = mirror in Y, hind legs = mirror in X. This module's own sweep uses "
    "SYMMETRIC +-25/+-90/+-150 ranges, so the identical geometry (mirrored) gives identical "
    "clearance numbers for all 4 legs -- one LF sweep covers all of them.")

ABAD_DEGS = [-25, 0, 25]
HIP_DEGS = [-90, -45, 0, 45, 90]
KNEE_DEGS = [-150, -90, -30, 0, 30, 90, 150]

worst_self_nonadjacent = 0.0   # shoulder vs shin
worst_self_adjacent = 0.0      # shoulder-thigh, thigh-shin
worst_envelope = 0.0
worst_z = shoulder.BoundBox.ZMax
worst_pose_env = None
worst_pose_self = None
worst_pose_z = None

TRANSLATE_TO_BODY = App.Vector(params.BASE_TO_HIP_X, params.BASE_TO_HIP_Y, 0)
envelope = chassis_envelope(0.0)

n_poses = 0
for a in ABAD_DEGS:
    for h in HIP_DEGS:
        for k in KNEE_DEGS:
            n_poses += 1
            s_ = shoulder.copy()
            t_ = thigh.copy()
            sh_ = shin.copy()

            sh_.rotate(KNEE_ORIGIN, KNEE_AXIS, k)
            t_.rotate(HIP_PITCH_ORIGIN, HIP_PITCH_AXIS, h)
            sh_.rotate(HIP_PITCH_ORIGIN, HIP_PITCH_AXIS, h)
            s_.rotate(ABAD_ORIGIN, ABAD_AXIS, a)
            t_.rotate(ABAD_ORIGIN, ABAD_AXIS, a)
            sh_.rotate(ABAD_ORIGIN, ABAD_AXIS, a)

            v_st = s_.common(t_).Volume
            v_tk = t_.common(sh_).Volume
            v_sk = s_.common(sh_).Volume
            if max(v_st, v_tk) > worst_self_adjacent:
                worst_self_adjacent = max(v_st, v_tk)
            if v_sk > worst_self_nonadjacent:
                worst_self_nonadjacent = v_sk
                worst_pose_self = (a, h, k)

            z_max = max(s_.BoundBox.ZMax, t_.BoundBox.ZMax, sh_.BoundBox.ZMax)
            if z_max > worst_z:
                worst_z = z_max
                worst_pose_z = (a, h, k)

            combo = Part.makeCompound([s_, t_, sh_])
            combo.translate(TRANSLATE_TO_BODY)
            v_env = combo.common(envelope).Volume
            if v_env > worst_envelope:
                worst_envelope = v_env
                worst_pose_env = (a, h, k)

log(f"Swept {n_poses} poses (ab/ad x hip_pitch x knee = "
    f"{len(ABAD_DEGS)}x{len(HIP_DEGS)}x{len(KNEE_DEGS)}).")
log(f"Worst self-collision, NON-adjacent (shoulder vs shin, must be ~0): "
    f"{worst_self_nonadjacent:.3f} mm^3 at pose {worst_pose_self}")
log(f"Worst self-collision, ADJACENT (shoulder-thigh / thigh-shin, <=1mm^3 allowed): "
    f"{worst_self_adjacent:.3f} mm^3")
log(f"Worst envelope overlap (leg module vs chassis_envelope, must be <=1mm^3): "
    f"{worst_envelope:.3f} mm^3 at pose {worst_pose_env}")
log(f"Worst Z reached (hip frame, must be <= LEG_MAX_Z={params.LEG_MAX_Z}mm): "
    f"{worst_z:.2f}mm at pose {worst_pose_z}")

ok = worst_self_nonadjacent <= 1.0 and worst_self_adjacent <= 1.0 and worst_envelope <= 1.0 and worst_z <= params.LEG_MAX_Z
log(f"\nRESULT: {'PASS' if ok else 'FAIL'}")

with open(f"{CAD_DIR}/leg_module_report.txt", "w") as f:
    f.write("\n".join(report_lines) + "\n")
