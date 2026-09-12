"""
Parametric top deck for the quadruped's two-deck sandwich chassis, built in FreeCAD's
Python API. Sits above build_bottom_deck.py on 4 standoffs (STANDOFF_HEIGHT=50mm, a
design choice -- clears the 26.5mm battery on the bottom deck plus wiring slack).

Convention: +X is front (matches build_bottom_deck.py). Same 500x290x6mm footprint as
the bottom deck -- kept identical rather than trimmed since there's no structural or
packaging reason to shrink it yet (ample room for the Pi4 + mast + pedestal below, and
matching footprints keep the standoff/hip-corner geometry simple); trim it later if a
real weight/cost reason shows up.

Four things on this deck:
  1. Standoff holes at the same (+-STANDOFF_X, +-STANDOFF_Y) positions as the bottom
     deck, so the two decks bolt together through the same 4 standoffs.
  2. Raspberry Pi 4 mounting pattern (58x49mm, 2.7mm holes) -- UNCHANGED real spec,
     moved here from the old body plate, centered at the deck origin.
  3. Camera/thermal mast, front edge (+X): a short vertical post (MAST_HEIGHT=50mm,
     design choice, inside the requested 40-60mm range) carrying a mounting face tilted
     MAST_TILT_DEG=12 degrees forward-and-down, with 2 mounting holes each for the Pi
     Camera (25x24mm PCB) and the AMG8833 thermal breakout (25.6x25.3mm), side by side.
     Forward+down angling puts both sensors at "approach height" for facial recognition
     and gives the thermal camera a clear forward view -- not straight up at the sky.
  4. LiDAR pedestal, rear-center (-X): a riser + top mounting disc raised
     LIDAR_PEDESTAL_HEIGHT=70mm above the deck -- deliberately taller than the 50mm
     camera mast so the RPLIDAR A1's 360-degree scan plane clears every other part of the
     robot (mast included) and also functions as the platform's main obstacle-avoidance
     sensor (see docs/champ-research.md and README for the ultrasonic-to-LiDAR swap
     rationale). Top disc carries a 4-hole bolt pattern -- see params.py for the
     "sized to fit within the ~97mm base, exact spacing unconfirmed" assumption note.
  5. Hip-bracket clearance pockets, one at each of the 4 real CHAMP hip positions
     (+-BASE_TO_HIP_X, +-BASE_TO_HIP_Y): a straight rectangular through-cut sized to the
     hip bracket's own 112x80mm footprint plus HIP_CLEARANCE_MARGIN on each side. The hip
     bracket's CHAMP-sourced 130mm height is taller than the 56mm gap to this deck, so it
     passes THROUGH here rather than stopping below it -- see README "Hip/deck interference
     fix" for why this fix (not a taller standoff or a shorter bracket) was chosen.
"""
import math

import FreeCAD as App
import Part

import params

BASE_X = params.BASE_X_LENGTH
BASE_Y = params.BASE_Y_LENGTH
THICKNESS = params.BODY_PLATE_THICKNESS  # 6mm, same draft plate thickness as the bottom deck

doc = App.newDocument("top_deck")

plate = Part.makeBox(BASE_X, BASE_Y, THICKNESS, App.Vector(-BASE_X / 2.0, -BASE_Y / 2.0, 0))

# 1. Standoff holes -- must match build_bottom_deck.py's positions exactly.
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(sx, sy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 2. Raspberry Pi 4 mount, centered -- real official spec, unchanged from the old body plate.
for dx in (-params.PI4_MOUNT_X / 2.0, params.PI4_MOUNT_X / 2.0):
    for dy in (-params.PI4_MOUNT_Y / 2.0, params.PI4_MOUNT_Y / 2.0):
        hole = Part.makeCylinder(params.PI4_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(dx, dy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 3. Camera/thermal mast, front edge -- post + tilted mounting face.
FRONT_X = BASE_X / 2.0 - 30.0  # mm, design choice: 30mm inset from the front edge for margin

post = Part.makeBox(params.MAST_POST_D, params.MAST_POST_W, params.MAST_HEIGHT,
                     App.Vector(FRONT_X - params.MAST_POST_D / 2.0, -params.MAST_POST_W / 2.0, THICKNESS))

# Mounting face: built flat and centered on the origin first (so its own holes are trivial
# to place), then rotated MAST_TILT_DEG about Y (tilts its +X-facing normal forward-and-down)
# and translated to the post's front face, overlapping it by half the face's own thickness
# so the two solids fuse cleanly.
plate_w = params.PICAM_PCB_L + params.AMG8833_L + 6.0   # mm, 6mm gap between the two devices
plate_h = max(params.PICAM_PCB_W, params.AMG8833_W) + 6.0  # mm, 6mm edge margin
face = Part.makeBox(params.MAST_FACE_THICKNESS, plate_w, plate_h,
                     App.Vector(-params.MAST_FACE_THICKNESS / 2.0, -plate_w / 2.0, -plate_h / 2.0))

y_cam = -plate_w / 2.0 + params.PICAM_PCB_L / 2.0 + 3.0
y_amg = plate_w / 2.0 - params.AMG8833_L / 2.0 - 3.0
cam_spacing = params.PICAM_PCB_L - 6.0
amg_spacing = params.AMG8833_L - 6.0
for y in (y_cam - cam_spacing / 2.0, y_cam + cam_spacing / 2.0):
    hole = Part.makeCylinder(params.PICAM_HOLE_DIA / 2.0, params.MAST_FACE_THICKNESS,
                              App.Vector(-params.MAST_FACE_THICKNESS / 2.0, y, 0), App.Vector(1, 0, 0))
    face = face.cut(hole)
for y in (y_amg - amg_spacing / 2.0, y_amg + amg_spacing / 2.0):
    hole = Part.makeCylinder(params.AMG8833_HOLE_DIA / 2.0, params.MAST_FACE_THICKNESS,
                              App.Vector(-params.MAST_FACE_THICKNESS / 2.0, y, 0), App.Vector(1, 0, 0))
    face = face.cut(hole)

face.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), params.MAST_TILT_DEG)
face_x = FRONT_X + params.MAST_POST_D / 2.0
face_z = THICKNESS + params.MAST_HEIGHT - plate_h / 2.0 - 5.0  # mm, 5mm reveal below the post top
face.translate(App.Vector(face_x, 0, face_z))

mast = post.fuse(face)
plate = plate.fuse(mast)

# 4. LiDAR pedestal, rear-center -- riser + top mounting disc with a 4-hole bolt pattern.
# Inset 55mm (not the mast's 30mm) -- the top disc's 100mm diameter (50mm radius) would
# overhang the rear edge at a 30mm inset; 55mm keeps the whole disc within the footprint.
REAR_X = -(BASE_X / 2.0 - 55.0)

riser_h = params.LIDAR_PEDESTAL_HEIGHT - params.LIDAR_TOP_DISC_THICKNESS
riser = Part.makeCylinder(params.LIDAR_RISER_DIA / 2.0, riser_h,
                           App.Vector(REAR_X, 0, THICKNESS), App.Vector(0, 0, 1))
top_disc = Part.makeCylinder(params.LIDAR_TOP_DISC_DIA / 2.0, params.LIDAR_TOP_DISC_THICKNESS,
                              App.Vector(REAR_X, 0, THICKNESS + riser_h), App.Vector(0, 0, 1))
pedestal = riser.fuse(top_disc)

n_holes = 4
for i in range(n_holes):
    angle = math.radians(i * 360.0 / n_holes)
    hx = REAR_X + (params.LIDAR_BOLT_CIRCLE_DIA / 2.0) * math.cos(angle)
    hy = (params.LIDAR_BOLT_CIRCLE_DIA / 2.0) * math.sin(angle)
    hole = Part.makeCylinder(params.LIDAR_BOLT_HOLE_DIA / 2.0, params.LIDAR_TOP_DISC_THICKNESS,
                              App.Vector(hx, hy, THICKNESS + riser_h), App.Vector(0, 0, 1))
    pedestal = pedestal.cut(hole)

# 5. Hip-bracket clearance pockets -- straight through-cut at each real hip position, sized
# to the hip bracket's 112x80mm footprint (params.HIP_X_LENGTH x params.HIP_Y_LENGTH) plus
# a fit margin on each side, so the bracket's CHAMP-sourced 130mm-tall body can pass through
# this deck rather than colliding with it.
pocket_x = params.HIP_X_LENGTH + 2 * params.HIP_CLEARANCE_MARGIN
pocket_y = params.HIP_Y_LENGTH + 2 * params.HIP_CLEARANCE_MARGIN
for hip_x in (-params.BASE_TO_HIP_X, params.BASE_TO_HIP_X):
    for hip_y in (-params.BASE_TO_HIP_Y, params.BASE_TO_HIP_Y):
        pocket = Part.makeBox(pocket_x, pocket_y, THICKNESS,
                               App.Vector(hip_x - pocket_x / 2.0, hip_y - pocket_y / 2.0, 0))
        plate = plate.cut(pocket)

plate = plate.fuse(pedestal)

part = doc.addObject("Part::Feature", "TopDeck")
part.Shape = plate
doc.recompute()

bbox = plate.BoundBox
print(f"TopDeck built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print(f"Camera/thermal mast top: {THICKNESS + params.MAST_HEIGHT:.1f}mm above deck. "
      f"LiDAR pedestal top: {THICKNESS + params.LIDAR_PEDESTAL_HEIGHT:.1f}mm above deck "
      f"(clears the mast by {params.LIDAR_PEDESTAL_HEIGHT - params.MAST_HEIGHT:.1f}mm).")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/top_deck.FCStd")
Part.export([part], f"{out_dir}/top_deck.step")
Part.export([part], f"{out_dir}/top_deck.stl")
print("Saved: top_deck.FCStd, top_deck.step, top_deck.stl")
