"""
Parametric upper-leg link ("femur") for the quadruped, built in FreeCAD's Python API.

Dimensions are NOT invented: the leg length (190.5mm) is CHAMP's own stock
upper_leg_z_length from champ_description/urdf/properties.urdf.xacro (see
docs/champ-research.md #3.1) -- a real, community-validated hobby-servo scale, not
an arbitrary pick. Servo footprint is the standard-size analog/digital servo
envelope shared by both the MG996R and DS3218 (both are drop-in "standard size"
servos on the same JR/Futaba-style mounting-tab spacing). All shared numbers live
in params.py; the pocket/bolt-circle cutting logic lives in geometry_helpers.py
(reused by build_lower_leg.py and build_hip_bracket.py).

This is the FIRST slice of the physical model: one link, checked for valid geometry,
before mirroring to a full leg (+lower leg, +foot) and then all four legs + body.
Open the exported .FCStd in FreeCAD to actually look at it -- this script only proves
the geometry is buildable and reports its bounding box; it cannot render a screenshot
headlessly.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import cut_bolt_circle, cut_servo_pocket_with_tabs

UPPER_LEG_LENGTH = params.UPPER_LEG_LENGTH
SERVO_BODY_W = params.SERVO_BODY_W
SERVO_BODY_H = params.SERVO_BODY_H
SERVO_TAB_SPACING = params.SERVO_TAB_SPACING
SERVO_TAB_HOLE_DIA = params.SERVO_TAB_HOLE_DIA
WALL = params.WALL
BRACKET_WIDTH = SERVO_BODY_W + 2 * WALL   # 28.2mm
BRACKET_THICKNESS = 8.0                    # mm, the flat bracket's own material thickness
KNEE_HORN_HOLE_DIA = params.KNEE_HORN_HOLE_DIA
KNEE_BOLT_CIRCLE_DIA = params.KNEE_BOLT_CIRCLE_DIA

doc = App.newDocument("upper_leg")

# Main link body: a flat bar the full leg length, wide/thick enough to carry the hip
# servo pocket at the top without flexing under a 12-servo quadruped's own weight.
bar = Part.makeBox(BRACKET_WIDTH, BRACKET_THICKNESS, UPPER_LEG_LENGTH)

# Hip-end servo pocket: recesses the hip servo's body INTO the top of the bracket so the
# servo horn sits flush against the link (standard SpotMicro-style mounting).
bar = cut_servo_pocket_with_tabs(
    bar, BRACKET_WIDTH, BRACKET_THICKNESS, UPPER_LEG_LENGTH - SERVO_BODY_H,
    SERVO_BODY_W, SERVO_BODY_H, SERVO_TAB_SPACING, SERVO_TAB_HOLE_DIA,
)

# Knee end: a boss clearance hole (for the knee servo's spline/horn to pass through) plus
# a 4-bolt circle to bolt the link directly onto the knee servo horn.
cx = BRACKET_WIDTH / 2.0
bar = cut_bolt_circle(bar, cx, 20.0, BRACKET_WIDTH, BRACKET_THICKNESS,
                       KNEE_HORN_HOLE_DIA, KNEE_BOLT_CIRCLE_DIA)

part = doc.addObject("Part::Feature", "UpperLegLink")
part.Shape = bar
doc.recompute()

bbox = bar.BoundBox
print(f"UpperLegLink built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {bar.Volume:.0f} mm^3   Solid valid: {bar.isValid()}")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/upper_leg.FCStd")
Part.export([part], f"{out_dir}/upper_leg.step")
Part.export([part], f"{out_dir}/upper_leg.stl")
print("Saved: upper_leg.FCStd, upper_leg.step, upper_leg.stl")
