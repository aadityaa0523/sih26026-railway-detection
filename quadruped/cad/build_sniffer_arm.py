"""
Parametric 2-DOF narcotics-sensing "sniffer" arm for the quadruped (improvement 4), built
in FreeCAD's Python API. Bolts to build_bottom_deck.py's EXISTING sensing-bay hole pattern
(SENSING_BAY_L/W, 90x60mm, 4 corner holes) -- reused directly as this arm's base footprint
so it lines up with holes the deck already cuts, rather than a new mismatched pattern.

This is the project's key differentiator (see README): the original static
underside-facing sensing-bay mount only let the robot sample air wherever its BODY happened
to be positioned ("static sensing"). A real fan+3xMQ+BME688 head still has no CAD of its own
(unchanged placeholder, see build_bottom_deck.py), but it can now be carried on a 2-DOF
DIP + SWING arm (2x SG90, real/ubiquitous spec, params.py) that lowers/aims the head toward
a target instead of relying purely on body position -- "active sensing".

NOT a fully kinematic mechanism -- same honest simplification as build_camera_pan_tilt.py:
simplified servo-pocket recesses, two static poses instead of simulated motion --
NEUTRAL (dip=0, swing=0, arm tucked straight down close to the body) and EXTENDED
(dip=SNIFFER_DIP_RANGE_DEG, swing=SNIFFER_SWING_RANGE_DEG, arm lowered/swung toward a
target). assemble_robot.py uses the NEUTRAL pose (sniffer_arm.step); the EXTENDED pose
(sniffer_arm_extended.step) is a standalone demonstration only.

Structure (base -> dip arm -> swing mount -> sensing-head interface), all hanging DOWN
(-Z) from the bottom deck's underside, matching the sensing bay's own underside-facing intent:
  - Base: bolts to the deck's sensing-bay pattern, DIP servo recessed in its bottom face --
    this is the "shoulder" that lowers the whole arm toward a target.
  - Dip arm: a post hanging SNIFFER_LINK_LENGTH down from the base.
  - Swing mount: an identical recessed block at the bottom of the dip arm, SWING servo
    recessed in ITS bottom face -- this is the "wrist" that aims the head side to side.
  - Sensing-head interface: the SAME 90x60mm/4-hole placeholder pattern the bottom deck
    used to carry directly, now at the end of the arm instead -- still a documented
    assumption pending the real sensing-head enclosure's own CAD.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import build_sg90_mount_block

out_dir = params.CAD_DIR

BASE_L, BASE_W, BASE_T = params.SENSING_BAY_L, params.SENSING_BAY_W, params.SNIFFER_BASE_T
MOUNT_INSET = params.SENSING_BAY_HOLE_INSET   # matches the deck's own sensing-bay hole inset
SHAFT_HOLE_DIA = 6.0   # mm, design choice, clears an SG90 spline + horn boss


def _servo_mount_block(cut_corner_bolts):
    return build_sg90_mount_block(BASE_L, BASE_W, BASE_T, params.SG90_BODY_L, params.SG90_BODY_W,
                                   params.SG90_TAB_SPACING, params.SG90_TAB_HOLE_DIA,
                                   SHAFT_HOLE_DIA, MOUNT_INSET, params.SENSING_BAY_HOLE_DIA,
                                   cut_corner_bolts)


def _sensing_head_interface():
    """Placeholder 4-corner-hole mounting plate for the (still uncad'd) fan+3xMQ+BME688
    sensing head -- identical pattern to what build_bottom_deck.py cuts directly into the
    deck today, just relocated to the end of this arm. Built flat, centered at the origin.
    """
    plate = Part.makeBox(BASE_L, BASE_W, BASE_T, App.Vector(-BASE_L / 2.0, -BASE_W / 2.0, -BASE_T))
    sl = params.SENSING_BAY_L / 2.0 - params.SENSING_BAY_HOLE_INSET
    sw = params.SENSING_BAY_W / 2.0 - params.SENSING_BAY_HOLE_INSET
    for dx in (-sl, sl):
        for dy in (-sw, sw):
            hole = Part.makeCylinder(params.SENSING_BAY_HOLE_DIA / 2.0, BASE_T,
                                      App.Vector(dx, dy, -BASE_T), App.Vector(0, 0, 1))
            plate = plate.cut(hole)
    return plate


def build_pose(dip_deg, swing_deg):
    """Build one static pose of the full sniffer arm. Returns the fused shape, with the
    base's TOP face at local Z=0 (bolts flush to the bottom deck's underside)."""
    base = _servo_mount_block(cut_corner_bolts=True)
    base.translate(App.Vector(0, 0, -BASE_T))   # base hangs BELOW Z=0, not above

    arm = Part.makeBox(15.0, 15.0, params.SNIFFER_LINK_LENGTH,
                        App.Vector(-7.5, -7.5, -BASE_T - params.SNIFFER_LINK_LENGTH))

    swing_mount = _servo_mount_block(cut_corner_bolts=False)
    swing_mount.translate(App.Vector(0, 0, -BASE_T - params.SNIFFER_LINK_LENGTH - BASE_T))

    head = _sensing_head_interface()
    head_z = -BASE_T - params.SNIFFER_LINK_LENGTH - BASE_T - 5.0   # 5mm standoff below the swing mount
    head.translate(App.Vector(0, 0, head_z))

    # Swing: rotate the head about the swing servo's axis (local Z, through the swing
    # mount's own center) BEFORE composing with the dip rotation below.
    swing_pivot = App.Vector(0, 0, -BASE_T - params.SNIFFER_LINK_LENGTH - BASE_T / 2.0)
    head.rotate(swing_pivot, App.Vector(0, 0, 1), swing_deg)

    moving = arm.fuse(swing_mount).fuse(head)
    # Dip: rotate everything below the base about the dip servo's axis (local X, through
    # the base's own bottom-center).
    moving.rotate(App.Vector(0, 0, -BASE_T), App.Vector(1, 0, 0), dip_deg)

    return base.fuse(moving)


def _build_and_export(dip_deg, swing_deg, name, doc_name, label):
    doc = App.newDocument(doc_name)
    shape = build_pose(dip_deg, swing_deg)
    part = doc.addObject("Part::Feature", "SnifferArm")
    part.Shape = shape
    doc.recompute()

    bbox = shape.BoundBox
    print(f"{label} (dip={dip_deg:.0f}deg, swing={swing_deg:.0f}deg) built OK. "
          f"Bounding box (mm): X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
    print(f"Volume: {shape.Volume:.0f} mm^3   Solid valid: {shape.isValid()}")

    doc.saveAs(f"{out_dir}/{name}.FCStd")
    Part.export([part], f"{out_dir}/{name}.step")
    Part.export([part], f"{out_dir}/{name}.stl")
    print(f"Saved: {name}.FCStd, {name}.step, {name}.stl")


# freecadcmd sets __name__ to the script's own module name, not "__main__" -- no guard,
# same convention as every other script in this directory.
print("2-DOF narcotics-sniffer arm -- 2x SG90 (params.py), NOT a fully kinematic mechanism, "
      "see module docstring. Building NEUTRAL and EXTENDED demonstration poses.\n")
_build_and_export(0.0, 0.0, "sniffer_arm", "sniffer_arm", "NEUTRAL pose")
print()
_build_and_export(params.SNIFFER_DIP_RANGE_DEG, params.SNIFFER_SWING_RANGE_DEG,
                   "sniffer_arm_extended", "sniffer_arm_extended", "EXTENDED pose (demo only)")
