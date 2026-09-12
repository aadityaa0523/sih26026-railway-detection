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
BASE_TO_HIP_X), +Y is left. Plate thickness (BODY_PLATE_THICKNESS = 6mm) is NOT a CHAMP
number, see build_body_plate.py's old header / README for that reasoning -- unchanged
here.

Four things on this deck, all cut into the same 500x290x6mm plate:
  1. Hip mounting patterns (UNCHANGED from the old body plate): 4 corners at CHAMP's real
     base_to_hip_x/y offsets (175/105mm), each a 4-hole rectangle matching
     build_hip_bracket.py's own footprint.
  2. Standoff holes: 4 vertical through-holes at (+-STANDOFF_X, +-STANDOFF_Y) -- see
     params.py for the "near each hip corner, inset" placement reasoning -- where
     threaded standoffs (STANDOFF_HEIGHT=50mm, a design choice) will carry the top deck.
  3. Battery bay, centered at the plate origin for a low/central center of gravity: a
     shallow 2mm locating pocket sized to the Zeee 3S 2200mAh pack's 75x34mm footprint,
     plus 2 full-thickness strap slots (one past each end) for a hook-and-loop/zip-tie
     strap looping under the deck and over the battery.
  4. Narcotics-sensing-bay mount, front edge (+X), underside-facing: a 90x60mm 4-corner
     screw-hole pattern only -- the fan+3xMQ+BME688 assembly's own CAD doesn't exist yet,
     so this is a documented placeholder, sized generously, not a real footprint.

The Raspberry Pi 4 mounting pattern that the old body plate carried has MOVED to the top
deck (build_top_deck.py) -- it no longer belongs here.
"""
import FreeCAD as App
import Part

import params

BASE_X = params.BASE_X_LENGTH   # 500mm, DRAFT starting size -- see module docstring
BASE_Y = params.BASE_Y_LENGTH   # 290mm, DRAFT starting size -- see module docstring
THICKNESS = params.BODY_PLATE_THICKNESS  # 6mm

doc = App.newDocument("bottom_deck")

# Plate centered at the XY origin (matches CHAMP's own base_to_hip_x/y convention,
# which is measured from the body's center).
plate = Part.makeBox(BASE_X, BASE_Y, THICKNESS, App.Vector(-BASE_X / 2.0, -BASE_Y / 2.0, 0))

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

# 2. Standoff holes -- same 4 XY positions build_top_deck.py cuts, so threaded standoffs
# (STANDOFF_HEIGHT tall) bolt the two decks together.
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(sx, sy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 3. Battery bay, centered at plate origin -- low/central CG. Shallow locating pocket cut
# into the top face (does not go through, so the deck stays solid underneath) plus 2
# through strap slots straddling the battery's long (X) axis.
pocket = Part.makeBox(params.BATTERY_L, params.BATTERY_W, params.BATTERY_BAY_POCKET_DEPTH,
                       App.Vector(-params.BATTERY_L / 2.0, -params.BATTERY_W / 2.0,
                                  THICKNESS - params.BATTERY_BAY_POCKET_DEPTH))
plate = plate.cut(pocket)
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

part = doc.addObject("Part::Feature", "BottomDeck")
part.Shape = plate
doc.recompute()

bbox = plate.BoundBox
print(f"BottomDeck built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print("*** DRAFT SIZE -- 500x290mm footprint NOT yet confirmed final; no physical test-fit done. ***")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/bottom_deck.FCStd")
Part.export([part], f"{out_dir}/bottom_deck.step")
Part.export([part], f"{out_dir}/bottom_deck.stl")
print("Saved: bottom_deck.FCStd, bottom_deck.step, bottom_deck.stl")
