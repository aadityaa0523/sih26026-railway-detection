"""
2-DOF narcotics-sensing "sniffer" arm for the quadruped -- CHASSIS V3 resize (2026-09-12).

CHASSIS V3 change: the arm's mount moved from the old underside-facing bottom-deck
sensing-bay pattern to a boom cantilevered forward off the bottom deck's front edge, ending
at a pivot INSIDE the V3 SPEC's own NOSE_BOX (params.SNIFFER_MOUNT_X=130mm, well inside its
110-170mm X-range, margin from both edges). Reason: NOSE_BOX's Z range (-88 to +92mm around
the hip axis) is far more generous than BODY_BOX's (-35 to +60mm), and mounting the pivot
there lets a purely VERTICAL dip sweep -- straight UP for STOWED, straight DOWN for DEPLOYED
-- satisfy both required poses without ever crossing the BODY_BOX/NOSE_BOX boundary (X, Y
stay ~constant at the pivot's own values throughout the sweep, only Z changes), which a
sweep starting from inside BODY_BOX could not do without also drifting into NOSE_BOX's X
range partway through -- avoided here by mounting the pivot there from the start.

Two static poses (same "NOT a fully kinematic mechanism" honest simplification as
build_camera_pan_tilt.py -- simplified servo-pocket reference volumes, no simulated
continuous motion):
  - STOWED (dip=0, swing=0): arm points straight UP from the pivot. Required by the V3 SPEC
    task brief: entirely inside BODY_BOX/NOSE_BOX, nothing below the body's own underside
    (Z>=0) -- true by construction here since the whole moving stack sits at Z>=pivot_Z=10mm.
  - DEPLOYED (dip=180, swing=SNIFFER_SWING_RANGE_DEG): arm points straight DOWN, reaching
    >=100mm below the hip axis within NOSE_BOX -- params.SNIFFER_LINK_LENGTH is sized so this
    is true by construction (see params.py's own note); check_chassis.py confirms both
    poses' actual solids, not just this comment's arithmetic.

Structure (boom -> dip pivot -> arm -> swing mount -> sensing-head interface):
  - Boom: bolts to the bottom deck (4 corner holes, mount_post_hole_xy(), shared with
    build_bottom_deck.py) and cantilevers forward to the pivot -- FIXED, part of both poses.
    Carries a small reference box for the DIP servo (mass/realism only, not recessed --
    the boom's own thickness at this small scale makes a true recessed pocket impractical,
    an honest simplification, same convention as elsewhere in this project).
  - Arm: a post rising SNIFFER_LINK_LENGTH from the pivot (reference/dip=0 direction: +Z).
  - Swing mount: an SG90-recessed block (geometry_helpers.build_sg90_mount_block, SAME
    vertical-shaft convention it was built for -- swing rotates about the arm's own long
    axis, which is vertical at both STOWED and DEPLOYED) at the arm's far end.
  - Sensing-head interface: the SAME 90x60mm/4-hole placeholder pattern the old design used
    -- still a documented assumption pending the real fan+3xMQ+BME688 enclosure's own CAD.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import build_sg90_mount_block

out_dir = params.CAD_DIR

PX, PY, PZ = params.SNIFFER_MOUNT_X, params.SNIFFER_MOUNT_Y, params.SNIFFER_MOUNT_Z
BASE_L, BASE_W, BASE_T = params.SENSING_BAY_L, params.SENSING_BAY_W, params.SNIFFER_BASE_T
SHAFT_HOLE_DIA = 6.0   # mm, design choice, clears an SG90 spline + horn boss

# Boom: bolts to the bottom deck (X<=110, inset within BODY_BOX) and cantilevers out to the
# pivot at PX=130mm (inside NOSE_BOX). Deck-top to a bit above the pivot height.
BOOM_X0 = 100.0   # mm, design choice -- inset within the deck's own 220mm length.
BOOM_W = 24.0     # mm, design choice, comfortably inside NOSE_HALF_W*2=40mm.
BOOM_Z0, BOOM_Z1 = params.BODY_PLATE_THICKNESS, 20.0   # deck top to 20mm, spans PZ=10mm.
_BOLT_INSET_X = (4.0, 8.0)   # mm, design choice -- 2 X positions near the boom's deck-side end.
_BOLT_Y = 8.0                # mm, design choice.


def mount_post_hole_xy():
    """Global (x, y) positions of the boom's 4 deck bolt holes -- shared with
    build_bottom_deck.py so the two files can't drift apart."""
    return [(BOOM_X0 + dx, sy) for dx in _BOLT_INSET_X for sy in (-_BOLT_Y, _BOLT_Y)]


def _boom():
    boom = Part.makeBox(PX - BOOM_X0, BOOM_W, BOOM_Z1 - BOOM_Z0,
                         App.Vector(BOOM_X0, -BOOM_W / 2.0, BOOM_Z0))
    for x, y in mount_post_hole_xy():
        hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, params.BODY_PLATE_THICKNESS,
                                  App.Vector(x, y, 0), App.Vector(0, 0, 1))
        boom = boom.cut(hole)
    # Dip servo reference box (SG90, mass/realism only -- see module docstring).
    sg90 = Part.makeBox(params.SG90_BODY_L, params.SG90_BODY_W, params.SG90_BODY_H,
                         App.Vector(PX - params.SG90_BODY_L / 2.0, -params.SG90_BODY_W / 2.0, BOOM_Z1))
    return boom.fuse(sg90)


def _swing_mount(cut_corner_bolts):
    return build_sg90_mount_block(BASE_L, BASE_W, BASE_T, params.SG90_BODY_L, params.SG90_BODY_W,
                                   params.SG90_TAB_SPACING, params.SG90_TAB_HOLE_DIA,
                                   SHAFT_HOLE_DIA, params.SENSING_BAY_HOLE_INSET,
                                   params.SENSING_BAY_HOLE_DIA, cut_corner_bolts)


def _sensing_head_interface():
    """Placeholder 4-corner-hole mounting plate for the (still uncad'd) fan+3xMQ+BME688
    sensing head -- unchanged pattern, just relocated to this arm's end. Flat, centered."""
    plate = Part.makeBox(BASE_L, BASE_W, BASE_T, App.Vector(-BASE_L / 2.0, -BASE_W / 2.0, 0))
    sl = params.SENSING_BAY_L / 2.0 - params.SENSING_BAY_HOLE_INSET
    sw = params.SENSING_BAY_W / 2.0 - params.SENSING_BAY_HOLE_INSET
    for dx in (-sl, sl):
        for dy in (-sw, sw):
            hole = Part.makeCylinder(params.SENSING_BAY_HOLE_DIA / 2.0, BASE_T,
                                      App.Vector(dx, dy, 0), App.Vector(0, 0, 1))
            plate = plate.cut(hole)
    return plate


def build_pose(dip_deg, swing_deg):
    """Build one static pose of the full sniffer arm (boom + moving stack). Reference
    (dip=0) direction is straight UP from the pivot; dip=180 flips it straight DOWN --
    see module docstring. Returns the fused shape in GLOBAL coordinates."""
    boom = _boom()

    arm = Part.makeBox(15.0, 15.0, params.SNIFFER_LINK_LENGTH,
                        App.Vector(PX - 7.5, PY - 7.5, PZ))

    swing_mount = _swing_mount(cut_corner_bolts=False)
    swing_mount.translate(App.Vector(PX, PY, PZ + params.SNIFFER_LINK_LENGTH))

    head = _sensing_head_interface()
    head_z = PZ + params.SNIFFER_LINK_LENGTH + BASE_T + 5.0   # 5mm standoff above the swing mount
    head.translate(App.Vector(PX, PY, head_z))

    # Swing: rotate the head about the swing servo's own axis (local Z, vertical at both
    # poses) through the swing mount's own center, BEFORE composing the dip rotation.
    swing_pivot = App.Vector(PX, PY, PZ + params.SNIFFER_LINK_LENGTH + BASE_T / 2.0)
    head.rotate(swing_pivot, App.Vector(0, 0, 1), swing_deg)

    moving = arm.fuse(swing_mount).fuse(head)
    # Dip: rotate the whole moving stack about the pivot's own X-axis. dip=0 leaves it
    # pointing straight up (as built); dip=180 flips it straight down.
    moving.rotate(App.Vector(PX, PY, PZ), App.Vector(1, 0, 0), dip_deg)

    return boom.fuse(moving)


def _build_and_export(dip_deg, swing_deg, name, doc_name, label):
    doc = App.newDocument(doc_name)
    shape = build_pose(dip_deg, swing_deg)
    part = doc.addObject("Part::Feature", "SnifferArm")
    part.Shape = shape
    doc.recompute()

    bbox = shape.BoundBox
    print(f"{label} (dip={dip_deg:.0f}deg, swing={swing_deg:.0f}deg) built OK. "
          f"Bounding box (mm): X=[{bbox.XMin:.1f},{bbox.XMax:.1f}] Y=[{bbox.YMin:.1f},{bbox.YMax:.1f}] "
          f"Z=[{bbox.ZMin:.1f},{bbox.ZMax:.1f}]")
    print(f"Volume: {shape.Volume:.0f} mm^3   Solid valid: {shape.isValid()}")

    doc.saveAs(f"{out_dir}/{name}.FCStd")
    Part.export([part], f"{out_dir}/{name}.step")
    Part.export([part], f"{out_dir}/{name}.stl")
    print(f"Saved: {name}.FCStd, {name}.step, {name}.stl")
    return shape


# freecadcmd sets __name__ to the script's own module name, not "__main__" -- no guard,
# same convention as every other script in this directory.
print("2-DOF narcotics-sniffer arm (CHASSIS V3, nose-mounted boom) -- 2x SG90, NOT a fully "
      "kinematic mechanism, see module docstring. Building STOWED and DEPLOYED poses.\n")
stowed_shape = _build_and_export(params.SNIFFER_STOWED_DIP_DEG, 0.0,
                                  "sniffer_arm", "sniffer_arm", "STOWED pose")
print()
deployed_shape = _build_and_export(params.SNIFFER_DEPLOYED_DIP_DEG, params.SNIFFER_SWING_RANGE_DEG,
                                    "sniffer_arm_extended", "sniffer_arm_extended", "DEPLOYED pose")

stowed_bottom = stowed_shape.BoundBox.ZMin
deployed_bottom = deployed_shape.BoundBox.ZMin
below_hip = params.HIP_AXIS_Z - deployed_bottom
print(f"\nSTOWED lowest point: Z={stowed_bottom:.1f}mm (>=0 required): "
      f"{'OK' if stowed_bottom >= 0.0 else 'FAIL'}")
print(f"DEPLOYED lowest point: Z={deployed_bottom:.1f}mm = {below_hip:.1f}mm below the hip "
      f"axis (>=100mm required): {'OK' if below_hip >= 100.0 else 'FAIL'}")
assert stowed_bottom >= 0.0, "STOWED pose dips below the body's own underside (Z<0)"
assert below_hip >= 100.0, "DEPLOYED pose does not reach 100mm below the hip axis"
