"""
Top deck of the quadruped's two-deck sandwich chassis -- CHASSIS V3 (SpotMicro-scale
resize, 2026-09-12), built in FreeCAD's Python API. Sits above build_bottom_deck.py on 4
real M3 hex standoffs (params.STANDOFF_HEIGHT=70mm, geometry_helpers.build_hex_standoff).

Same CHASSIS_LENGTH x CHASSIS_WIDTH (220x130mm) footprint as the bottom deck (see that
file's own docstring for the V3 SPEC derivation). CHASSIS V3 simplification vs. Chassis v2:
**no hip-bracket clearance pockets are needed any more** -- the ab/ad servo housings
(build_abad_mount.py) top out at Z=65mm, well clear of this deck's own underside at
Z=BODY_PLATE_THICKNESS+STANDOFF_HEIGHT=73mm (the old design's tall hip bracket had to pass
THROUGH the top deck; the V3 ab/ad servo is chassis-owned and stays entirely below it).
Cable routing uses the open corners outboard of the box walls (build_body_walls.py's own
walls stop at X=+-60mm, well short of the ab/ad housings at |X|>=66.5mm) instead of dedicated
pass-through slots -- a secondary refinement on the old 500x290mm deck, not load-bearing, and
honestly dropped rather than force-fit onto a much smaller deck.

Mass-review fix: the mast and LiDAR pedestal are now SEPARATE Part::Feature objects from the
flat deck plate (not fused into one "TopDeck" solid) -- they're chunky 3D risers/platforms,
not laser-cut sheet, so check_chassis.py's mass breakdown can correctly count them as printed
PETG (45% of solid) instead of accidentally pricing them as 100%-solid acrylic sheet (an
earlier pass's real bug: fusing them into the deck made the whole fused blob read as
"acrylic," overstating chassis mass by several hundred grams). LIDAR_RISER_DIA also slimmed
32mm (was 50mm) -- see params.py's own note.

Things on this deck:
  1. Standoff holes, matching build_bottom_deck.py's positions exactly.
  2. Raspberry Pi 4 mounting pattern (58x49mm, 2.7mm holes) -- unchanged real spec.
  3. Camera/thermal mast, front edge (separate CameraMast object): MAST_HEIGHT short post
     (Chassis v2's own LiDAR occlusion fix, unchanged) topped with a flat mounting plate for
     the pan-tilt head (build_camera_pan_tilt.py, internals UNCHANGED per the V3 SPEC brief).
  4. LiDAR pedestal, rear-center (separate LidarPedestal object): a slimmed riser topped with
     the real A1M8 D-shape outline plate (Chassis v2 item 7, unchanged geometry), raised to
     LIDAR_PEDESTAL_HEIGHT=75mm so its own base clears the Z=HIP_AXIS_Z+LEG_MAX_Z=92mm
     restricted-zone ceiling with margin (see params.py's own note) -- confirmed by
     check_chassis.py's LiDAR scan-band check.
  5. Top-deck "avionics cover" (Chassis v2 item 2 geometry, unchanged): real Pi4 85x56mm
     board outline + PCA9685 clearance, connector-side openings on both ends, top vents.
  6. Box-section body-wall flange bolt holes -- shared pattern with build_bottom_deck.py,
     resized for CHASSIS_WIDTH.
  7. Lightening cut-outs -- TOP DECK ONLY (the bottom deck stays solid, ground-facing/dust),
     placed in the deck's own clear areas, checked against every existing hole/pocket/mount
     the same way build_top_deck.py's Chassis-v2-era version did (geometric overlap test,
     not eyeballed).
"""
import math

import FreeCAD as App
import Part

import params
from geometry_helpers import fillet_vertical_edges, wall_flange_hole_xy

BASE_X = params.CHASSIS_LENGTH  # 220mm, V3 SPEC BODY_BOX X extent
BASE_Y = params.CHASSIS_WIDTH   # 130mm, V3 SPEC BODY_BOX Y extent
THICKNESS = params.BODY_PLATE_THICKNESS  # 3mm

doc = App.newDocument("top_deck")

plate = Part.makeBox(BASE_X, BASE_Y, THICKNESS, App.Vector(-BASE_X / 2.0, -BASE_Y / 2.0, 0))
plate = fillet_vertical_edges(plate, params.DECK_CORNER_FILLET_R)

# 1. Standoff holes.
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(sx, sy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 2. Raspberry Pi 4 mount, centered -- real official spec, unchanged.
for dx in (-params.PI4_MOUNT_X / 2.0, params.PI4_MOUNT_X / 2.0):
    for dy in (-params.PI4_MOUNT_Y / 2.0, params.PI4_MOUNT_Y / 2.0):
        hole = Part.makeCylinder(params.PI4_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(dx, dy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 3. Camera/thermal mast, front edge -- CHASSIS V3: inset from the new, much shorter front
# edge (was 30mm inset off a 500mm-long deck; now 20mm off a 220mm-long one).
FRONT_X = BASE_X / 2.0 - 20.0   # mm, design choice.

post = Part.makeBox(params.MAST_POST_D, params.MAST_POST_W, params.MAST_HEIGHT,
                     App.Vector(FRONT_X - params.MAST_POST_D / 2.0, -params.MAST_POST_W / 2.0, THICKNESS))

mount_plate = Part.makeBox(params.PANTILT_BASE_W, params.PANTILT_BASE_D, params.MAST_FACE_THICKNESS,
                            App.Vector(FRONT_X - params.PANTILT_BASE_W / 2.0, -params.PANTILT_BASE_D / 2.0,
                                       THICKNESS + params.MAST_HEIGHT))
mount_inset = 6.0
for dx in (-(params.PANTILT_BASE_W / 2.0 - mount_inset), params.PANTILT_BASE_W / 2.0 - mount_inset):
    for dy in (-(params.PANTILT_BASE_D / 2.0 - mount_inset), params.PANTILT_BASE_D / 2.0 - mount_inset):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, params.MAST_FACE_THICKNESS,
                                  App.Vector(FRONT_X + dx, dy, THICKNESS + params.MAST_HEIGHT),
                                  App.Vector(0, 0, 1))
        mount_plate = mount_plate.cut(hole)

mast = post.fuse(mount_plate)   # kept SEPARATE from `plate` -- see module docstring (mass review).

# 4. LiDAR pedestal, rear-center -- CHASSIS V3: REAR_X inset so the riser (radius
# LIDAR_RISER_DIA/2=25mm) stays inside BODY_BOX's own X range while below the Z=92mm
# restricted-zone ceiling (the wide D-shape top plate rises above that ceiling anyway, see
# module docstring, so it needs no X/Y containment once it clears Z=92).
REAR_X = -(BASE_X / 2.0 - 30.0)   # mm, design choice -- -80mm, riser spans X[-105,-55].

riser_h = params.LIDAR_PEDESTAL_HEIGHT - params.LIDAR_TOP_DISC_THICKNESS
riser = Part.makeCylinder(params.LIDAR_RISER_DIA / 2.0, riser_h,
                           App.Vector(REAR_X, 0, THICKNESS), App.Vector(0, 0, 1))

plate_z = THICKNESS + riser_h
circle_r = params.LIDAR_PLATE_WIDTH / 2.0
circle = Part.makeCylinder(circle_r, params.LIDAR_TOP_DISC_THICKNESS,
                            App.Vector(REAR_X, 0, plate_z), App.Vector(0, 0, 1))
rect_len = params.LIDAR_PLATE_LENGTH - circle_r
rect = Part.makeBox(rect_len, params.LIDAR_PLATE_WIDTH, params.LIDAR_TOP_DISC_THICKNESS,
                     App.Vector(REAR_X - rect_len, -circle_r, plate_z))
lidar_plate = circle.fuse(rect)

n_holes = 4
for i in range(n_holes):
    angle = math.radians(i * 360.0 / n_holes)
    hx = REAR_X + (params.LIDAR_BOLT_CIRCLE_DIA / 2.0) * math.cos(angle)
    hy = (params.LIDAR_BOLT_CIRCLE_DIA / 2.0) * math.sin(angle)
    hole = Part.makeCylinder(params.LIDAR_BOLT_HOLE_DIA / 2.0, params.LIDAR_TOP_DISC_THICKNESS,
                              App.Vector(hx, hy, plate_z), App.Vector(0, 0, 1))
    lidar_plate = lidar_plate.cut(hole)

pedestal = riser.fuse(lidar_plate)   # kept SEPARATE from `plate` -- see module docstring.

# 5. Box-section body-wall flange bolt holes -- shared pattern with build_bottom_deck.py.
wall_holes = wall_flange_hole_xy(params.WALL_SIDE_LENGTH, params.BULKHEAD_LENGTH,
                                  params.BULKHEAD_X, BASE_Y, params.WALL_HOLE_INSET,
                                  params.WALL_THICKNESS, params.WALL_FLANGE)
for x, y in wall_holes:
    hole = Part.makeCylinder(params.WALL_BOLT_DIA / 2.0, THICKNESS, App.Vector(x, y, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)

# 6. Top-deck "avionics cover" (Chassis v2 item 2 geometry, unchanged) -- real Pi4 85x56mm
# board outline + clearance, wide enough to also cover the PCA9685 beside it, connector-side
# openings on both ends + top vents. Kept as a SEPARATE, removable solid.
lid_l = params.PI4_BOARD_L + 2 * params.PI4_LID_CLEARANCE
lid_y_min = -params.PI4_BOARD_W / 2.0 - params.PI4_LID_CLEARANCE
lid_y_max = (params.PI4_BOARD_W / 2.0 + params.PI4_LID_BOARD_GAP + params.PCA9685_W
             + params.PI4_LID_CLEARANCE)
lid_w = lid_y_max - lid_y_min
lid_h = params.PI4_STANDOFF_HEIGHT + params.PI4_CONNECTOR_HEIGHT + 5.0
lw = params.TOPDECK_LID_WALL
lid_outer = Part.makeBox(lid_l, lid_w, lid_h, App.Vector(-lid_l / 2.0, lid_y_min, THICKNESS))
lid_inner = Part.makeBox(lid_l - 2 * lw, lid_w - 2 * lw, lid_h - lw,
                          App.Vector(-lid_l / 2.0 + lw, lid_y_min + lw, THICKNESS))
lid = lid_outer.cut(lid_inner)

pi4_y0 = -params.PI4_BOARD_W / 2.0
conn_slot_w = params.PI4_BOARD_W
for xside in (-lid_l / 2.0, lid_l / 2.0 - lw):
    slot = Part.makeBox(lw, conn_slot_w, lid_h, App.Vector(xside, pi4_y0, THICKNESS))
    lid = lid.cut(slot)

n_vents = 5
vent_y0 = lid_y_min + 15.0
for i in range(n_vents):
    vy = vent_y0 + i * params.VENT_SLOT_PITCH
    if vy + params.VENT_SLOT_W / 2.0 > lid_y_max - 15.0:
        break
    vent = Part.makeBox(params.VENT_SLOT_L, params.VENT_SLOT_W, lw,
                         App.Vector(-params.VENT_SLOT_L / 2.0, vy - params.VENT_SLOT_W / 2.0, THICKNESS + lid_h - lw))
    lid = lid.cut(vent)

# 7. Lightening cut-outs -- TOP DECK ONLY (mass-review addition; the bottom deck stays solid,
# ground-facing/dust). Candidate centers in the deck's own clear mid-body band, each checked
# against every real keepout on this deck (geometric overlap test, not eyeballed).
lightening_r = params.LIGHTENING_HOLE_DIA / 2.0
lightening_centers = [(-30.0, 45.0), (-30.0, -45.0), (30.0, 45.0), (30.0, -45.0),
                       (70.0, 45.0), (70.0, -45.0), (-95.0, 45.0), (-95.0, -45.0)]
keepout_boxes = [
    (0.0, (lid_y_min + lid_y_max) / 2.0, lid_l / 2.0, (lid_y_max - lid_y_min) / 2.0),  # avionics cover
    (FRONT_X, 0.0, params.MAST_POST_D, params.PANTILT_BASE_D / 2.0 + 5.0),
    (REAR_X, 0.0, params.LIDAR_RISER_DIA / 2.0 + 5.0, params.LIDAR_RISER_DIA / 2.0 + 5.0),
]
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy2 in (-params.STANDOFF_Y, params.STANDOFF_Y):
        keepout_boxes.append((sx, sy2, 10.0, 10.0))
n_lighten, n_skip = 0, 0
for cx, cy in lightening_centers:
    if abs(cx) + lightening_r > BASE_X / 2.0 - params.DECK_CORNER_FILLET_R or \
       abs(cy) + lightening_r > BASE_Y / 2.0 - 5.0:
        n_skip += 1
        continue
    clash = any(abs(cx - kx) < (lightening_r + hw) and abs(cy - ky) < (lightening_r + hh)
                for kx, ky, hw, hh in keepout_boxes)
    if clash:
        n_skip += 1
        print(f"  SKIPPED lightening hole at ({cx:.0f},{cy:.0f}) -- overlaps a keepout.")
        continue
    hole = Part.makeCylinder(lightening_r, THICKNESS, App.Vector(cx, cy, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)
    n_lighten += 1
print(f"Lightening cut-outs (top deck only, mass review): {n_lighten} cut, {n_skip} skipped.")

part = doc.addObject("Part::Feature", "TopDeckPlate")
part.Shape = plate
doc.recompute()

mast_obj = doc.addObject("Part::Feature", "CameraMast")
mast_obj.Shape = mast
doc.recompute()

pedestal_obj = doc.addObject("Part::Feature", "LidarPedestal")
pedestal_obj.Shape = pedestal
doc.recompute()

lid_obj = doc.addObject("Part::Feature", "TopDeckLid")
lid_obj.Shape = lid
doc.recompute()

bbox = plate.BoundBox
print(f"TopDeckPlate (CHASSIS V3) built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print(f"CameraMast: Volume={mast.Volume:.0f}mm^3  Solid valid: {mast.isValid()}")
print(f"LidarPedestal: Volume={pedestal.Volume:.0f}mm^3  Solid valid: {pedestal.isValid()}")
print(f"TopDeckLid (avionics cover) solid valid: {lid.isValid()} -- {lid_l:.0f}x{lid_w:.0f}x{lid_h:.0f}mm.")
print(f"Camera/thermal mast top: {THICKNESS + params.MAST_HEIGHT:.1f}mm above deck. "
      f"LiDAR pedestal top (own base): {THICKNESS + params.LIDAR_PEDESTAL_HEIGHT:.1f}mm above deck "
      f"= {params.STANDOFF_HEIGHT + THICKNESS + params.LIDAR_PEDESTAL_HEIGHT:.1f}mm above Z=0, "
      f"{params.STANDOFF_HEIGHT + THICKNESS + params.LIDAR_PEDESTAL_HEIGHT - (params.HIP_AXIS_Z + params.LEG_MAX_Z):.1f}mm "
      f"clear of the Z={params.HIP_AXIS_Z + params.LEG_MAX_Z:.0f}mm restricted-zone ceiling.")

out_dir = params.CAD_DIR
doc.saveAs(f"{out_dir}/top_deck.FCStd")
all_objs = [part, mast_obj, pedestal_obj, lid_obj]
Part.export(all_objs, f"{out_dir}/top_deck.step")
Part.export(all_objs, f"{out_dir}/top_deck.stl")
print("Saved: top_deck.FCStd, top_deck.step, top_deck.stl (plate + mast + LiDAR pedestal + avionics cover)")
