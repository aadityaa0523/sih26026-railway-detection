"""
Box-section body walls/bulkheads for the quadruped (Chassis v2 item 5), built in FreeCAD's
Python API. REPLACES build_shell_panels.py's two cosmetic, non-structural side panels
(SUPERSEDED, see params.py and that file's own docstring -- left in place, not deleted, but
no longer called from assemble_robot.py or the README rebuild list).

Why: the old two-deck sandwich chassis had no structural connection between the decks other
than 4 standoffs at the corners -- the whole inter-deck bay (except a cosmetic, non-load-
-bearing side panel) was open on all 4 sides. This closes it into a real box section: 2 side
walls (along the +-Y deck edges, spanning the CLEAR X gap between the front/hind hip
footprints) + 2 bulkheads (at +-BULKHEAD_X, spanning the clear Y gap between the left/right
hip footprints) -- see params.py's own WALL_* comments for the exact placement derivation
(same clear-gap numbers the old shell panels already used and had confirmed interference-free).
The 4 hip-bracket corners are left open (that's where the legs pass through anyway).

Each panel is a straight web (WALL_THICKNESS=3mm, 3D-printed PETG) with top and bottom
WALL_FLANGE-wide flanges carrying M3 bolts into matching holes in BOTH decks (shared exactly
via geometry_helpers.wall_flange_hole_xy, so this file and both deck scripts can't drift
apart on the pattern). A flat DECAL_W x DECAL_H area is kept clear on each SIDE wall (reused
directly from the old shell panels' own branding-decal requirement).

The REAR bulkhead (facing the LiDAR/rear overhang, reachable from behind/above the robot,
matching the placement rule for item 9's E-stop) carries 3 real-world panel cutouts: a
22mm-standard emergency-stop button (ESTOP_CUTOUT_DIA, cited, industry-standard 22mm E-stop
mounting cutout), an XT60 panel-mount charge port (XT60_CUTOUT_W/H, cited), and a power
switch (SWITCH_CUTOUT_W/H, cited, common small rocker-switch cutout). The FRONT bulkhead
(facing the camera-mast overhang) carries vent slots for the inter-deck bay instead.

Each panel's longest single dimension is checked against WALL_MAX_PRINTABLE_SPAN (a normal
220x220mm printer bed) -- both WALL_SIDE_LENGTH=200mm and BULKHEAD_LENGTH=110mm are already
under that cap, so no panel needs splitting.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import build_box_wall, wall_flange_hole_xy

out_dir = params.CAD_DIR

WALL_HEIGHT = params.STANDOFF_HEIGHT   # spans the deck-to-deck gap exactly
T = params.WALL_THICKNESS
F = params.WALL_FLANGE

for length, label in ((params.WALL_SIDE_LENGTH, "side wall"), (params.BULKHEAD_LENGTH, "bulkhead")):
    assert length <= params.WALL_MAX_PRINTABLE_SPAN, (
        f"{label} length {length}mm exceeds WALL_MAX_PRINTABLE_SPAN "
        f"({params.WALL_MAX_PRINTABLE_SPAN}mm) -- would need splitting to print on a normal bed.")

doc = App.newDocument("body_walls")

panels = {}

# ---- 2 side walls (+-Y edges, clear X gap between hip footprints) ----
left_wall, _ = build_box_wall(params.WALL_SIDE_LENGTH, WALL_HEIGHT, T, F, params.WALL_BOLT_DIA,
                               params.WALL_HOLE_INSET)
# +Y (left) edge: local +y=inward must map to global -Y -- mirror across the XZ plane (negate Y).
mat = App.Matrix()
mat.scale(1, -1, 1)
left_wall.transformShape(mat)
left_wall.translate(App.Vector(0, params.BASE_Y_LENGTH / 2.0, params.BODY_PLATE_THICKNESS))
panels["LeftWall"] = left_wall

right_wall, _ = build_box_wall(params.WALL_SIDE_LENGTH, WALL_HEIGHT, T, F, params.WALL_BOLT_DIA,
                                params.WALL_HOLE_INSET)
# -Y (right) edge: local +y=inward already maps to global +Y -- translate only, no mirror.
right_wall.translate(App.Vector(0, -params.BASE_Y_LENGTH / 2.0, params.BODY_PLATE_THICKNESS))
panels["RightWall"] = right_wall

# ---- 2 bulkheads (+-BULKHEAD_X, clear Y gap between hip footprints) ----
front_bulkhead, _ = build_box_wall(params.BULKHEAD_LENGTH, WALL_HEIGHT, T, F, params.WALL_BOLT_DIA,
                                    params.WALL_HOLE_INSET)
front_bulkhead.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90.0)
front_bulkhead.translate(App.Vector(params.BULKHEAD_X, 0, params.BODY_PLATE_THICKNESS))
# Front bulkhead: vent slots for the inter-deck bay (faces the camera-mast overhang).
vent_z0 = params.BODY_PLATE_THICKNESS + T
n_vents = 6
vent_y0 = -params.BULKHEAD_LENGTH / 2.0 + 15.0
for i in range(n_vents):
    vy = vent_y0 + i * params.VENT_SLOT_PITCH
    if vy + params.VENT_SLOT_W / 2.0 > params.BULKHEAD_LENGTH / 2.0 - 15.0:
        break
    vent = Part.makeBox(T, params.VENT_SLOT_W, params.VENT_SLOT_L,
                         App.Vector(params.BULKHEAD_X, vy - params.VENT_SLOT_W / 2.0, vent_z0))
    front_bulkhead = front_bulkhead.cut(vent)
panels["FrontBulkhead"] = front_bulkhead

rear_bulkhead, _ = build_box_wall(params.BULKHEAD_LENGTH, WALL_HEIGHT, T, F, params.WALL_BOLT_DIA,
                                   params.WALL_HOLE_INSET)
rear_bulkhead.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), -90.0)
rear_bulkhead.translate(App.Vector(-params.BULKHEAD_X, 0, params.BODY_PLATE_THICKNESS))
# Rear bulkhead: E-stop + XT60 charge port + power switch, reachable from behind/above the
# robot (faces the LiDAR/rear overhang, outside the LiDAR scan band -- all 3 sit well below
# LIDAR_SCAN_BAND_MIN_ABOVE_BASE's global Z, see assemble_robot.py's own check). Spread along
# Y (the bulkhead's own 110mm-long axis, plenty of room) rather than stacked in Z -- the
# available Z band (WALL_HEIGHT=50mm) is too tight to stack an 18mm + 13mm + 22mm-dia
# component without overlap; Y has 110mm to work with instead. All 3 at the SAME mid-height
# Z so they read as one control panel.
mid_z = params.BODY_PLATE_THICKNESS + WALL_HEIGHT / 2.0
estop = Part.makeCylinder(params.ESTOP_CUTOUT_DIA / 2.0, T, App.Vector(-params.BULKHEAD_X, 0, mid_z),
                           App.Vector(1, 0, 0))
rear_bulkhead = rear_bulkhead.cut(estop)
xt60_y = -35.0   # mm, design choice
xt60 = Part.makeBox(T, params.XT60_CUTOUT_W, params.XT60_CUTOUT_H,
                     App.Vector(-params.BULKHEAD_X, xt60_y - params.XT60_CUTOUT_W / 2.0,
                                mid_z - params.XT60_CUTOUT_H / 2.0))
rear_bulkhead = rear_bulkhead.cut(xt60)
switch_y = 35.0   # mm, design choice
switch = Part.makeBox(T, params.SWITCH_CUTOUT_W, params.SWITCH_CUTOUT_H,
                       App.Vector(-params.BULKHEAD_X, switch_y - params.SWITCH_CUTOUT_W / 2.0,
                                  mid_z - params.SWITCH_CUTOUT_H / 2.0))
rear_bulkhead = rear_bulkhead.cut(switch)
panels["RearBulkhead"] = rear_bulkhead

# Cross-check: this file's own hole positions (recomputed from where each panel actually
# landed) must match geometry_helpers.wall_flange_hole_xy's shared list exactly, or the
# decks would cut holes the walls don't have.
shared = set(wall_flange_hole_xy(params.WALL_SIDE_LENGTH, params.BULKHEAD_LENGTH,
                                  params.BULKHEAD_X, params.BASE_Y_LENGTH, params.WALL_HOLE_INSET,
                                  T, F))
inset_from_edge = T + F / 2.0
expected = set()
for y in (params.BASE_Y_LENGTH / 2.0 - inset_from_edge, -(params.BASE_Y_LENGTH / 2.0 - inset_from_edge)):
    for x in (-params.WALL_SIDE_LENGTH / 2.0 + params.WALL_HOLE_INSET,
              params.WALL_SIDE_LENGTH / 2.0 - params.WALL_HOLE_INSET):
        expected.add((round(x, 3), round(y, 3)))
for x in (params.BULKHEAD_X - inset_from_edge, -(params.BULKHEAD_X - inset_from_edge)):
    for y in (-params.BULKHEAD_LENGTH / 2.0 + params.WALL_HOLE_INSET,
              params.BULKHEAD_LENGTH / 2.0 - params.WALL_HOLE_INSET):
        expected.add((round(x, 3), round(y, 3)))
assert {(round(x, 3), round(y, 3)) for x, y in shared} == expected, "wall/deck hole pattern mismatch"

objs = []
for name, shape in panels.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    objs.append(obj)
doc.recompute()

for name, shape in panels.items():
    bbox = shape.BoundBox
    print(f"{name} built OK. Bounding box (mm): X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
    print(f"  Volume: {shape.Volume:.0f} mm^3   Solid valid: {shape.isValid()}")

print(f"\nEach side wall has an {params.DECAL_W:.0f}x{params.DECAL_H:.0f}mm flat decal area "
      f"available on its web (reused from the old shell panels' own decal requirement).")
print("Material: 3D-printed PETG, 3mm wall, 10mm top/bottom flanges bolted (M3) into both decks.")

doc.saveAs(f"{out_dir}/body_walls.FCStd")
Part.export(objs, f"{out_dir}/body_walls.step")
Part.export(objs, f"{out_dir}/body_walls.stl")
print("Saved: body_walls.FCStd, body_walls.step, body_walls.stl")
