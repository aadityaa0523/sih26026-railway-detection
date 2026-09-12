"""
Parametric bottom deck for the quadruped's two-deck sandwich chassis, built in
FreeCAD's Python API.

Formerly `build_body_plate.py` -- renamed because the single flat body plate has been
split into a bottom deck (this file) + a top deck (build_top_deck.py) on standoffs, the
standard SpotMicroAI/Mini Pupper approach for fitting a battery + sensor payload that a
single flat plate has no room for. See build_top_deck.py's docstring for the standoff
side of this split.

*** DRAFT -- overall footprint is a STARTING point, not final ***. The 500x290mm
footprint is still CHAMP's own stock base_x_length/base_y_length (docs/champ-research.md
#3.1), reused only as a plausible starting envelope -- it has NOT been physically
test-fit. Unlike the leg/hip parts (fixed by servo geometry + CHAMP's own hip offsets,
no review needed), review and approve final body sizing before treating this as final.

Convention: +X is the robot's front (same axis the hip legs are offset along via
BASE_TO_HIP_X), +Y is left.

---- CHASSIS V2 (item 4): laser-cut sheet, not a printed/cast plate --------------------
500x290mm cannot be 3D-printed on a common bed, and the earlier ribbed-plate design
(improvement 6, SUPERSEDED, see params.py) cannot be laser-cut either -- so this deck is
now a plain THROUGH-FEATURES-ONLY 3mm sheet (5052 aluminium as production intent, or 3mm
acrylic for the prototype -- identical geometry, params.BODY_PLATE_THICKNESS, design
choice). No ribs, no blind pockets: the battery bay's old 2mm locating pocket is REMOVED
(kept only the 2 through strap slots); the earlier stiffening role of the ribs is now
carried by the box-section body walls instead (build_body_walls.py, item 5). Outer
corners are rounded (DECK_CORNER_FILLET_R, design choice) via geometry_helpers.
fillet_vertical_edges, applied to the plain box BEFORE any hole is cut, per this
project's fillet-robustness convention.

Six things on this deck, all cut into the same 500x290x3mm sheet:
  1. Hip mounting patterns (UNCHANGED): 4 corners at CHAMP's real base_to_hip_x/y offsets
     (175/105mm), each a 4-hole rectangle matching build_hip_bracket.py's own footprint.
  2. Standoff holes: 4 vertical through-holes at (+-STANDOFF_X, +-STANDOFF_Y) for the
     real M3 hex standoffs (build_hex_standoff, item 6) that carry the top deck.
  3. Battery bay, centered at the plate origin for a low/central center of gravity: 2
     full-thickness strap slots (one past each end) for a hook-and-loop/zip-tie strap
     looping under the deck and over the battery -- no locating pocket any more, see above.
  4. Narcotics-sensing-bay mount, front edge (+X), underside-facing: a 90x60mm 4-corner
     screw-hole pattern only -- the fan+3xMQ+BME688 assembly's own CAD doesn't exist yet,
     so this is a documented placeholder, sized generously, not a real footprint.
  5. Box-section body-wall flange bolt holes (item 5): 8 holes (2 side walls + front/rear
     bulkheads x 2 each) matching build_body_walls.py's own flange pattern exactly (shared
     positions via geometry_helpers.wall_flange_hole_xy so the two files can't drift apart).
  6. Outer-corner fillets (see above).

The Raspberry Pi 4 mounting pattern that the old body plate carried lives on the top deck
(build_top_deck.py) -- it does not belong here.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import fillet_vertical_edges, wall_flange_hole_xy

BASE_X = params.BASE_X_LENGTH   # 500mm, DRAFT starting size -- see module docstring
BASE_Y = params.BASE_Y_LENGTH   # 290mm, DRAFT starting size -- see module docstring
THICKNESS = params.BODY_PLATE_THICKNESS  # 3mm, Chassis v2 item 4 (was 4mm, then 6mm originally)

doc = App.newDocument("bottom_deck")

# Plate centered at the XY origin (matches CHAMP's own base_to_hip_x/y convention,
# which is measured from the body's center). Outer corners filleted BEFORE any hole is cut.
plate = Part.makeBox(BASE_X, BASE_Y, THICKNESS, App.Vector(-BASE_X / 2.0, -BASE_Y / 2.0, 0))
plate = fillet_vertical_edges(plate, params.DECK_CORNER_FILLET_R)

# 1. Hip-bracket mounting patterns -- unchanged from the old body plate.
inset = params.HIP_MOUNT_INSET
hx = params.HIP_X_LENGTH / 2.0 - inset
hy = params.HIP_Y_LENGTH / 2.0 - inset
hip_hole_dia = params.SERVO_TAB_HOLE_DIA
for hip_x in (-params.BASE_TO_HIP_X, params.BASE_TO_HIP_X):
    for hip_y in (-params.BASE_TO_HIP_Y, params.BASE_TO_HIP_Y):
        for dx in (-hx, hx):
            for dy in (-hy, hy):
                hole = Part.makeCylinder(hip_hole_dia / 2.0, THICKNESS,
                                          App.Vector(hip_x + dx, hip_y + dy, 0), App.Vector(0, 0, 1))
                plate = plate.cut(hole)

# 2. Standoff holes -- same 4 XY positions build_top_deck.py cuts, for the real M3 hex
# standoffs (params.STANDOFF_HEIGHT tall, item 6) that bolt the two decks together.
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(sx, sy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 3. Battery bay, centered at plate origin -- low/central CG. CHASSIS V2: the old 2mm
# locating pocket is REMOVED (a laser-cut sheet has no blind features) -- only the 2
# through strap slots straddling the battery's long (X) axis remain.
strap_x = params.BATTERY_L / 2.0 + 8.0  # mm, design choice: slot sits 8mm clear of the battery footprint
for sx in (-strap_x, strap_x):
    slot = Part.makeBox(params.BATTERY_STRAP_SLOT_W, params.BATTERY_STRAP_SLOT_L, THICKNESS,
                         App.Vector(sx - params.BATTERY_STRAP_SLOT_W / 2.0,
                                    -params.BATTERY_STRAP_SLOT_L / 2.0, 0))
    plate = plate.cut(slot)

# 4. Narcotics-sensing-bay mount, front edge (+X), underside-facing -- placeholder 4-hole
# pattern only, see module docstring. Inset 50mm from the front edge (design choice).
sensing_cx = BASE_X / 2.0 - 50.0
sl = params.SENSING_BAY_L / 2.0 - params.SENSING_BAY_HOLE_INSET
sw = params.SENSING_BAY_W / 2.0 - params.SENSING_BAY_HOLE_INSET
for dx in (-sl, sl):
    for dy in (-sw, sw):
        hole = Part.makeCylinder(params.SENSING_BAY_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(sensing_cx + dx, dy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 5. Box-section body-wall flange bolt holes (item 5) -- shared pattern, see
# geometry_helpers.wall_flange_hole_xy's own docstring.
wall_holes = wall_flange_hole_xy(params.WALL_SIDE_LENGTH, params.BULKHEAD_LENGTH,
                                  params.BULKHEAD_X, BASE_Y, params.WALL_HOLE_INSET,
                                  params.WALL_THICKNESS, params.WALL_FLANGE)
for x, y in wall_holes:
    hole = Part.makeCylinder(params.WALL_BOLT_DIA / 2.0, THICKNESS, App.Vector(x, y, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)

# 6. MPU6050/GY-521 IMU mounting hole (Chassis v2 item 9) -- 1 hole (many real GY-521 boards
# ship with a single mounting hole, not a 4-corner pattern), within 60mm of the body's XY
# center per the item 9 placement rule, clear of the battery bay/straps.
imu_hole = Part.makeCylinder(params.MPU6050_HOLE_DIA / 2.0, THICKNESS,
                              App.Vector(params.IMU_MOUNT_X, params.IMU_MOUNT_Y, 0), App.Vector(0, 0, 1))
plate = plate.cut(imu_hole)

part = doc.addObject("Part::Feature", "BottomDeck")
part.Shape = plate
doc.recompute()

bbox = plate.BoundBox
print(f"BottomDeck built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print(f"CHASSIS V2: {THICKNESS:.0f}mm laser-cut sheet (5052 aluminium / acrylic, design "
      f"choice), through-features only -- no ribs, no blind pockets. "
      f"{len(wall_holes)} body-wall flange holes cut.")
print("*** DRAFT SIZE -- 500x290mm footprint NOT yet confirmed final; no physical test-fit done. ***")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/bottom_deck.FCStd")
Part.export([part], f"{out_dir}/bottom_deck.step")
Part.export([part], f"{out_dir}/bottom_deck.stl")
print("Saved: bottom_deck.FCStd, bottom_deck.step, bottom_deck.stl")
