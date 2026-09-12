"""
Parametric hip bracket ("housing") for the quadruped, built in FreeCAD's Python API.

Overall envelope (112 x 80 x 130mm) is CHAMP's own stock hip_x/y/z_length from
champ_description/urdf/properties.urdf.xacro (docs/champ-research.md #3.1) -- the
hip link's real bounding volume, reused here as the housing's own outer envelope.
UNCHANGED by Chassis v2 (hard constraint: outer envelope + horn-face bolt-circle
position stay exactly where they were).

---- CHASSIS V2 item 8: hollowed housing + separate cap + real internal servo mount -----
The v1 bracket was a SOLID printed block -- unrealistic (heavy, wasteful, and the servo
was never actually seated on anything, just implied by a pocket at the wrong height, see
below). Now a real housing:
  - 4mm floor (HIP_HOUSING_FLOOR_T) + 4mm walls (HIP_HOUSING_WALL_T), open top, outer
    vertical edges filleted R6 (HIP_HOUSING_FILLET_R) -- fillet the plain outer box BEFORE
    any other feature is cut, per this project's fillet-robustness convention
    (geometry_helpers.fillet_vertical_edges).
  - The open top is closed by a SEPARATE 3mm cap (HIP_CAP_THICKNESS,
    build_hip_bracket_cap.step) screwed onto 4 corner bosses -- printed and installed
    separately so the internal servo web (below) is reachable during assembly.
  - Internal servo web (NEW): the v1 design's bottom-face pocket (Z=0..38, "servo enters
    from underneath") never actually lined up with the SAME servo's own output horn on the
    front face (Z~100) -- an honest but unrealistic simplification (see the old docstring
    below, kept in git history). REPLACED here with a horizontal internal shelf at the
    SAME height as the horn-face bolt circle (its own coaxial requirement) carrying a
    SERVO_BODY_L x SERVO_BODY_W clearance cutout + 2 SERVO_TAB_HOLE_DIA tab holes at
    SERVO_TAB_SPACING -- the servo now actually sits with its output shaft pointing OUT
    through the outboard wall's own horn bolt circle, coaxial by construction (not implied).
    Shelf top sits SERVO_HORN_FLANGE_HEIGHT (ASSUMPTION, params.py -- no manufacturer
    drawing found for this MG996R dimension) below the horn bolt-circle's own Z, so the
    servo's spline boss reaches the horn height from its mounting flange.
  - Cable exit slot (NEW): a HIP_CABLE_SLOT_W x HIP_CABLE_SLOT_H rectangular cut through the
    INBOARD wall (Y=0, facing the body/deck side) for the servo signal + power leads.
  - The 4 corner floor bolts that mount this housing down onto the deck are now cut through
    the FLOOR ONLY (HIP_HOUSING_FLOOR_T), not the full 130mm height (there is no longer
    "full height" solid material to bore through).

Both this housing and its cap are picked up by assemble_full_leg.py's build_full_leg() and
carried through the same abduction-tilt + mirror + translate transform every other leg part
gets (see assemble_robot.py).
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import cut_bolt_circle, fillet_vertical_edges

HIP_X = params.HIP_X_LENGTH   # 112mm, UNCHANGED (hard constraint)
HIP_Y = params.HIP_Y_LENGTH   # 80mm, UNCHANGED
HIP_Z = params.HIP_Z_LENGTH   # 130mm, UNCHANGED

FLOOR_T = params.HIP_HOUSING_FLOOR_T
WALL_T = params.HIP_HOUSING_WALL_T

doc = App.newDocument("hip_bracket")

# ---- Outer shell: fillet the plain box FIRST, then hollow it out. ----
outer = Part.makeBox(HIP_X, HIP_Y, HIP_Z)
outer = fillet_vertical_edges(outer, params.HIP_HOUSING_FILLET_R)

cavity = Part.makeBox(HIP_X - 2 * WALL_T, HIP_Y - 2 * WALL_T, HIP_Z - FLOOR_T + 1.0,
                       App.Vector(WALL_T, WALL_T, FLOOR_T))
block = outer.cut(cavity)   # floor + 4 walls, open top

# Bottom face (Z=0): 4 corner through-bolts that mount this housing to the deck -- FLOOR
# ONLY now (there is no full-height solid to bore through any more).
inset = params.HIP_MOUNT_INSET
for x in (inset, HIP_X - inset):
    for y in (inset, HIP_Y - inset):
        hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, FLOOR_T,
                                  App.Vector(x, y, 0), App.Vector(0, 0, 1))
        block = block.cut(hole)

# Front face (Y=HIP_Y, perpendicular to the bottom): the hip servo's output-horn bolt
# circle -- UNCHANGED position (hard constraint): same cx/horn_z as v1.
cx = HIP_X / 2.0
horn_z = HIP_Z - 30.0
block = cut_bolt_circle(block, cx, horn_z, HIP_X, HIP_Y,
                         params.KNEE_HORN_HOLE_DIA, params.KNEE_BOLT_CIRCLE_DIA)

# Internal servo web (NEW, item 8): a horizontal shelf carrying the ACTUAL hip servo, its
# output shaft coaxial with the horn bolt circle above (by construction, not implied).
shelf_top_z = horn_z - params.SERVO_HORN_FLANGE_HEIGHT
shelf_t = WALL_T
shelf = Part.makeBox(HIP_X - 2 * WALL_T, HIP_Y - 2 * WALL_T, shelf_t,
                      App.Vector(WALL_T, WALL_T, shelf_top_z - shelf_t))
# Clearance cutout for the servo body -- L (along Y, the shaft axis, servo body runs up to
# the outboard wall where its horn passes through) x W (along X) -- passes fully through
# the shelf's own thickness.
cut_l, cut_w = params.SERVO_BODY_L, params.SERVO_BODY_W
servo_cut = Part.makeBox(cut_w, cut_l, shelf_t,
                          App.Vector(cx - cut_w / 2.0, HIP_Y - cut_l, shelf_top_z - shelf_t))
shelf = shelf.cut(servo_cut)
for dx in (-params.SERVO_TAB_SPACING / 2.0, params.SERVO_TAB_SPACING / 2.0):
    x = cx + dx
    if WALL_T < x < HIP_X - WALL_T:
        tab_hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, shelf_t,
                                      App.Vector(x, HIP_Y - cut_l / 2.0, shelf_top_z - shelf_t),
                                      App.Vector(0, 0, 1))
        shelf = shelf.cut(tab_hole)
block = block.fuse(shelf)

# Cable exit slot (NEW): inboard face (Y=0, body/deck side), a rectangular cut through the wall.
slot_cz = shelf_top_z - params.HIP_CABLE_SLOT_H - 10.0   # mm, design choice, below the shelf
cable_slot = Part.makeBox(params.HIP_CABLE_SLOT_W, WALL_T + 2.0, params.HIP_CABLE_SLOT_H,
                           App.Vector(cx - params.HIP_CABLE_SLOT_W / 2.0, -1.0, slot_cz))
block = block.cut(cable_slot)

# Corner boss posts (NEW) -- 4 small posts standing proud of the open top rim, for the
# separate cap (below) to screw into.
boss_inset = 8.0   # mm, design choice -- clears both the R6 corner fillet and the 4mm wall.
boss_h = 2.0       # mm, design choice -- kept SHORT deliberately: closing an open top with a
                    # cap unavoidably adds some height above the 112x80x130 envelope (the cap
                    # has to sit somewhere), so this stays as small as still gives the cap
                    # screw somewhere to bite (2mm boss + 3mm cap = 5mm added, see README).
boss_positions = [(boss_inset, boss_inset), (HIP_X - boss_inset, boss_inset),
                  (boss_inset, HIP_Y - boss_inset), (HIP_X - boss_inset, HIP_Y - boss_inset)]
for x, y in boss_positions:
    boss = Part.makeCylinder(params.HIP_CAP_BOSS_DIA / 2.0, boss_h, App.Vector(x, y, HIP_Z), App.Vector(0, 0, 1))
    block = block.fuse(boss)
    pilot = Part.makeCylinder(params.HIP_CAP_SCREW_DIA / 2.0, boss_h + 2.0, App.Vector(x, y, HIP_Z - 2.0),
                               App.Vector(0, 0, 1))
    block = block.cut(pilot)

# ---- Separate cap (NEW): closes the open top, screwed onto the 4 boss posts above. ----
cap = Part.makeBox(HIP_X, HIP_Y, params.HIP_CAP_THICKNESS)
cap = fillet_vertical_edges(cap, params.HIP_HOUSING_FILLET_R)
for x, y in boss_positions:
    hole = Part.makeCylinder(params.HIP_CAP_SCREW_DIA / 2.0, params.HIP_CAP_THICKNESS,
                              App.Vector(x, y, 0), App.Vector(0, 0, 1))
    cap = cap.cut(hole)
# Cap sits at global Z = HIP_Z + boss_h in the housing's own native frame (on top of the bosses).
cap.translate(App.Vector(0, 0, HIP_Z + boss_h))

part = doc.addObject("Part::Feature", "HipBracket")
part.Shape = block
cap_obj = doc.addObject("Part::Feature", "HipBracketCap")
cap_obj.Shape = cap
doc.recompute()

bbox = block.BoundBox
print(f"HipBracket (housing) built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {block.Volume:.0f} mm^3   Solid valid: {block.isValid()}")
cap_bbox = cap.BoundBox
print(f"HipBracketCap built OK. Bounding box (mm): "
      f"X={cap_bbox.XLength:.1f} Y={cap_bbox.YLength:.1f} Z={cap_bbox.ZLength:.1f}")
print(f"Volume: {cap.Volume:.0f} mm^3   Solid valid: {cap.isValid()}")
print("Outer envelope + horn-face bolt-circle position UNCHANGED from v1 (hard constraint) -- "
      "only hollowed out + given a real internal servo mount + separate cap (item 8).")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/hip_bracket.FCStd")
Part.export([part], f"{out_dir}/hip_bracket.step")
Part.export([part], f"{out_dir}/hip_bracket.stl")
Part.export([cap_obj], f"{out_dir}/hip_bracket_cap.step")
Part.export([cap_obj], f"{out_dir}/hip_bracket_cap.stl")
print("Saved: hip_bracket.FCStd, hip_bracket.step, hip_bracket.stl, "
      "hip_bracket_cap.step, hip_bracket_cap.stl")
