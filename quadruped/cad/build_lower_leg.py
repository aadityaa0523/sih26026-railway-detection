"""
Parametric lower-leg link ("tibia") for the quadruped, built in FreeCAD's Python API.

Length (156mm) is CHAMP's own stock lower_leg_z_length from
champ_description/urdf/properties.urdf.xacro (docs/champ-research.md #3.1).

Top end mates with build_upper_leg.py's knee-end bolt circle: same
KNEE_HORN_HOLE_DIA center hole + same KNEE_BOLT_CIRCLE_DIA 4-hole pattern (both
from params.py, cut via the shared geometry_helpers.cut_bolt_circle), so the two
links bolt directly together at the knee servo horn.

Bottom end is now a COMPLIANT foot interface (improvement 3, shock absorption --
real deployed quadrupeds use compliant/sprung feet, not rigid ones): the same rigid
mounting boss as before, PLUS a generic small bought compression spring seated in a
blind bore in the boss (no precise spec invented -- "generic small compression
spring, ~10mm dia range, exact spec TBD at purchase", same documented-assumption
level as the rubber foot cap), PLUS the same bought rubber foot cap on top of the
spring (still not modeled -- no rubber-foot-cap CAD exists anywhere in this repo).
The boss itself was widened/deepened vs. the original rigid-only version so the
recess can actually accept this spring+cap stack.

Also carries a cable routing channel (improvement 7) along the link's front face --
a shallow groove sized for a 3-4 servo signal wire bundle, kept clear of both end
features (knee bolt circle, foot boss).

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

# Foot-tip boss: sized to hold the spring+rubber-cap compliant stack (improvement 3).
# Widened/deepened vs. the original rigid-only boss (18mm dia x 10mm) so it can actually
# recess params.SPRING_BORE_DIA/DEPTH's blind bore for the bought compression spring
# underneath the still-bought, still-unmodeled rubber foot cap -- a design choice.
FOOT_BOSS_DIA = 22.0     # mm, was 18.0
FOOT_BOSS_HEIGHT = 16.0  # mm, was 10.0

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
# compliant foot stack a round post to grip.
cy = BRACKET_THICKNESS / 2.0
foot_boss = Part.makeCylinder(FOOT_BOSS_DIA / 2.0, FOOT_BOSS_HEIGHT,
                               App.Vector(cx, cy, -FOOT_BOSS_HEIGHT), App.Vector(0, 0, 1))
bar = bar.fuse(foot_boss)

# Compliant foot (improvement 3): a blind bore up into the boss from its bottom face seats
# the bought compression spring; the bought rubber foot cap then sits on top of the spring,
# still not modeled here, same as before. Bore depth is comfortably less than
# FOOT_BOSS_HEIGHT so the boss keeps a solid floor above the knee-facing side.
spring_bore = Part.makeCylinder(params.SPRING_BORE_DIA / 2.0, params.SPRING_BORE_DEPTH,
                                 App.Vector(cx, cy, -FOOT_BOSS_HEIGHT), App.Vector(0, 0, 1))
bar = bar.cut(spring_bore)

# Cable routing channel (improvement 7): a shallow groove along the link's front face
# (Y=0), sized for a 3-4 servo signal wire bundle. Bottom end kept clear of the foot boss
# via CABLE_CHANNEL_END_MARGIN; top end kept clear of the knee bolt-circle cluster itself
# (center hole + 2 surviving bolt holes span roughly knee_z +- (bolt-circle radius + bolt
# hole radius), computed here rather than reusing the same flat margin on both ends).
channel_z0 = params.CABLE_CHANNEL_END_MARGIN
channel_z1 = knee_z - KNEE_BOLT_CIRCLE_DIA / 2.0 - 5.0  # mm, 5mm buffer past the bolt holes
channel = Part.makeBox(params.CABLE_CHANNEL_WIDTH, params.CABLE_CHANNEL_DEPTH, channel_z1 - channel_z0,
                        App.Vector(cx - params.CABLE_CHANNEL_WIDTH / 2.0, 0, channel_z0))
bar = bar.cut(channel)

part = doc.addObject("Part::Feature", "LowerLegLink")
part.Shape = bar
doc.recompute()

bbox = bar.BoundBox
print(f"LowerLegLink built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {bar.Volume:.0f} mm^3   Solid valid: {bar.isValid()}")

out_dir = params.CAD_DIR
doc.saveAs(f"{out_dir}/lower_leg.FCStd")
Part.export([part], f"{out_dir}/lower_leg.step")
Part.export([part], f"{out_dir}/lower_leg.stl")
print("Saved: lower_leg.FCStd, lower_leg.step, lower_leg.stl")
