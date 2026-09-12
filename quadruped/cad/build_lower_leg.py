"""
Parametric lower-leg link ("tibia") for the quadruped, built in FreeCAD's Python API.

Length (156mm) is CHAMP's own stock lower_leg_z_length from
champ_description/urdf/properties.urdf.xacro (docs/champ-research.md #3.1).

Top end mates with build_upper_leg.py's knee-end bolt circle: same
KNEE_HORN_HOLE_DIA center hole + same KNEE_BOLT_CIRCLE_DIA 4-hole pattern (both
from params.py, cut via the shared geometry_helpers.cut_bolt_circle), so the two
links bolt directly together at the knee servo horn.

Bottom end is a foot-tip mount: a cylindrical boss sized to hold a rubber foot cap
(a bought part -- not modeled here, no rubber-foot-cap CAD exists anywhere in this repo).

Same box+cut Part-module approach as build_upper_leg.py.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import cut_bolt_circle

LOWER_LEG_LENGTH = params.LOWER_LEG_LENGTH
KNEE_HORN_HOLE_DIA = params.KNEE_HORN_HOLE_DIA
KNEE_BOLT_CIRCLE_DIA = params.KNEE_BOLT_CIRCLE_DIA
WALL = params.WALL

# Link cross-section: reuse the same bracket width/thickness convention as the upper
# leg so the two links look and mount consistently (narrower than the upper leg is
# fine structurally -- the tibia carries less bending load than the femur).
BRACKET_WIDTH = params.SERVO_BODY_W + 2 * WALL   # 28.2mm, same as upper leg
BRACKET_THICKNESS = 8.0                           # mm

# Foot-tip boss: sized to hold a bought rubber foot cap (not modeled).
FOOT_BOSS_DIA = 18.0    # mm
FOOT_BOSS_HEIGHT = 10.0  # mm

doc = App.newDocument("lower_leg")

# Main link body: flat bar the full tibia length.
bar = Part.makeBox(BRACKET_WIDTH, BRACKET_THICKNESS, LOWER_LEG_LENGTH)

# Top end: knee bolt-circle interface -- mirrors build_upper_leg.py's knee end exactly
# so the two links bolt together at the same 4-hole pattern around a shared center hole.
cx = BRACKET_WIDTH / 2.0
knee_z = LOWER_LEG_LENGTH - 20.0  # same 20mm inset from the link end as the upper leg's knee end
bar = cut_bolt_circle(bar, cx, knee_z, BRACKET_WIDTH, BRACKET_THICKNESS,
                       KNEE_HORN_HOLE_DIA, KNEE_BOLT_CIRCLE_DIA)

# Bottom end: foot-tip mount -- a cylindrical boss centered on the link's bottom face,
# protruding beyond the bar's own footprint (foot boss dia > bracket width) to give the
# rubber foot cap a round post to grip.
cy = BRACKET_THICKNESS / 2.0
foot_boss = Part.makeCylinder(FOOT_BOSS_DIA / 2.0, FOOT_BOSS_HEIGHT,
                               App.Vector(cx, cy, -FOOT_BOSS_HEIGHT), App.Vector(0, 0, 1))
bar = bar.fuse(foot_boss)

part = doc.addObject("Part::Feature", "LowerLegLink")
part.Shape = bar
doc.recompute()

bbox = bar.BoundBox
print(f"LowerLegLink built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {bar.Volume:.0f} mm^3   Solid valid: {bar.isValid()}")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/lower_leg.FCStd")
Part.export([part], f"{out_dir}/lower_leg.step")
Part.export([part], f"{out_dir}/lower_leg.stl")
print("Saved: lower_leg.FCStd, lower_leg.step, lower_leg.stl")
