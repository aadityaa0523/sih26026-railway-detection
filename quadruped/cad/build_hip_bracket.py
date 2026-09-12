"""
Parametric hip bracket for the quadruped, built in FreeCAD's Python API.

Overall envelope (112 x 80 x 130mm) is CHAMP's own stock hip_x/y/z_length from
champ_description/urdf/properties.urdf.xacro (docs/champ-research.md #3.1) -- the
hip link's real bounding volume, reused here as the bracket block's envelope.

Three features (all cut with the helpers already used by build_upper_leg.py /
build_lower_leg.py, see geometry_helpers.py, plus one plain 4-hole pattern):
  - Bottom face (Z=0): a servo body pocket + 2 mounting-tab bolt holes recess the
    hip-axis servo into the bracket from underneath. These tab holes are horizontal
    (bore through Y, standard servo-flange screws) -- separate from the vertical
    plate-mounting bolts below, they are NOT the same bolts.
  - Also on the bottom face: 4 vertical (Z-axis) through-holes at the footprint's
    corners (inset by params.HIP_MOUNT_INSET) -- these are what actually bolts the
    bracket down onto build_body_plate.py's matching hip mounting pattern.
  - Front face (Y=0/Y=80, perpendicular to the bottom): the same standard-servo-horn
    bolt-circle pattern (KNEE_HORN_HOLE_DIA / KNEE_BOLT_CIRCLE_DIA from params.py) used
    at the knee joint, reused here for the hip-axis servo's output horn -- this is
    where build_upper_leg.py's hip end (its own servo-horn pocket) bolts on.

Same box+cut Part-module approach as the leg links.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import cut_bolt_circle, cut_servo_pocket_with_tabs

HIP_X = params.HIP_X_LENGTH   # 112mm
HIP_Y = params.HIP_Y_LENGTH   # 80mm, also used as the bolt-circle/pocket cut depth
HIP_Z = params.HIP_Z_LENGTH   # 130mm

doc = App.newDocument("hip_bracket")

block = Part.makeBox(HIP_X, HIP_Y, HIP_Z)

# Bottom face: hip-axis servo pocket + tab holes, recessed from Z=0 upward -- this
# face mates flat against the body plate (build_body_plate.py's hip mounting points).
block = cut_servo_pocket_with_tabs(
    block, HIP_X, HIP_Y, 0.0,
    params.SERVO_BODY_W, params.SERVO_BODY_H, params.SERVO_TAB_SPACING, params.SERVO_TAB_HOLE_DIA,
)

# Bottom face: 4 corner through-bolts that actually mount this bracket to the plate.
inset = params.HIP_MOUNT_INSET
for x in (inset, HIP_X - inset):
    for y in (inset, HIP_Y - inset):
        hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, HIP_Z,
                                  App.Vector(x, y, 0), App.Vector(0, 0, 1))
        block = block.cut(hole)

# Front face (perpendicular to the bottom): the hip servo's output-horn bolt circle,
# positioned well clear of the bottom pocket (0-38mm) and its tab holes.
cx = HIP_X / 2.0
horn_z = HIP_Z - 30.0
block = cut_bolt_circle(block, cx, horn_z, HIP_X, HIP_Y,
                         params.KNEE_HORN_HOLE_DIA, params.KNEE_BOLT_CIRCLE_DIA)

part = doc.addObject("Part::Feature", "HipBracket")
part.Shape = block
doc.recompute()

bbox = block.BoundBox
print(f"HipBracket built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {block.Volume:.0f} mm^3   Solid valid: {block.isValid()}")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/hip_bracket.FCStd")
Part.export([part], f"{out_dir}/hip_bracket.step")
Part.export([part], f"{out_dir}/hip_bracket.stl")
print("Saved: hip_bracket.FCStd, hip_bracket.step, hip_bracket.stl")
