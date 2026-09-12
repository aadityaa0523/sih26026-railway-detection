"""
Parametric top deck for the quadruped's two-deck sandwich chassis, built in FreeCAD's
Python API. Sits above build_bottom_deck.py on 4 real M3 hex standoffs
(params.STANDOFF_HEIGHT=50mm tall, params.STANDOFF_HEX_ACROSS_FLATS=5.5mm, item 6,
modeled as solids in assemble_robot.py -- this script only cuts the matching bolt holes).

Convention: +X is front (matches build_bottom_deck.py). Same 500x290mm footprint as
the bottom deck -- kept identical rather than trimmed since there's no structural or
packaging reason to shrink it yet.

---- CHASSIS V2 (item 4): laser-cut sheet, not a printed/cast plate --------------------
Same material/thickness change as build_bottom_deck.py: THICKNESS is now
params.BODY_PLATE_THICKNESS=3mm (was 4mm, then 6mm originally), through-features only.
The earlier ribbed-plate design (improvement 6, SUPERSEDED) is removed -- stiffness now
comes from the box-section body walls (build_body_walls.py, item 5) instead. Outer
corners are rounded (DECK_CORNER_FILLET_R) and the hip-clearance pockets' inner corners
are rounded (HIP_NOTCH_FILLET_R) via geometry_helpers.fillet_vertical_edges, both applied
BEFORE the box/cutter is used in a boolean cut, per this project's fillet-robustness
convention. Two new cable pass-through slots and top-deck-only lightening cut-outs are
also added (item 4) -- the bottom deck stays solid (ground-facing, dust).

Things on this deck:
  1. Standoff holes at the same (+-STANDOFF_X, +-STANDOFF_Y) positions as the bottom
     deck, for the 4 real M3 hex standoffs (item 6, modeled in assemble_robot.py).
  2. Raspberry Pi 4 mounting pattern (58x49mm, 2.7mm holes) -- unchanged real spec.
  3. Camera/thermal mast, front edge (+X): a short mounting boss (MAST_HEIGHT, CUT from
     50mm to 8mm for Chassis v2 item 1 -- see params.py's own note for the full LiDAR
     scan-plane-occlusion derivation) topped with a flat mounting plate for the pan-tilt
     head (build_camera_pan_tilt.py, improvement 4).
  4. LiDAR pedestal, rear-center (-X): a riser topped with a plate that now follows the
     RPLIDAR A1's REAL base outline (Chassis v2 item 7, LIDAR_PLATE_LENGTH/WIDTH,
     Slamtec's own cited 96.8x70.3mm spec) instead of the old notched 100mm circular
     disc -- approximated as a LIDAR_PLATE_WIDTH-diameter circle unioned with a rectangle
     extending the long axis out to LIDAR_PLATE_LENGTH, long axis along X. The old
     notches (LIDAR_DISC_HIP_NOTCH_*, params.py, now deleted) are no longer needed: the
     real outline is narrower than the old 100mm disc and the interference check
     (assemble_robot.py) confirms it clears the tilted hind hip brackets without them.
  5. Hip-bracket clearance pockets, one at each of the 4 real CHAMP hip positions, sized
     to the hollow hip housing's own 112x80mm footprint (item 8) plus clearance margins,
     inner corners filleted (HIP_NOTCH_FILLET_R, item 4).
  6. Top-deck "avionics cover" (Chassis v2 item 2): REBUILT from the Raspberry Pi 4B's
     REAL board outline (85x56mm, official mechanical drawing) + clearance, wide enough to
     also cover the PCA9685 servo driver mounted beside it, with a full-height opening on
     BOTH short (connector) edges -- the real Pi4 has connectors on both (USB-C power +
     2x micro-HDMI + audio on one edge, Gigabit Ethernet + 4x USB-A on the other) -- plus
     top vent slots. The OLD lid was sized from only the 58x49mm mounting-hole rectangle +
     a flat 20mm margin (98x89mm), which let the real 85x56mm board overhang it on the
     connector side -- this replaces that geometry entirely.
  7. Box-section body-wall flange bolt holes (item 5) -- shared pattern with
     build_bottom_deck.py via geometry_helpers.wall_flange_hole_xy.
"""
import math

import FreeCAD as App
import Part

import params
from geometry_helpers import fillet_vertical_edges, wall_flange_hole_xy

BASE_X = params.BASE_X_LENGTH
BASE_Y = params.BASE_Y_LENGTH
THICKNESS = params.BODY_PLATE_THICKNESS  # 3mm, Chassis v2 item 4 (was 4mm, then 6mm originally)

doc = App.newDocument("top_deck")

plate = Part.makeBox(BASE_X, BASE_Y, THICKNESS, App.Vector(-BASE_X / 2.0, -BASE_Y / 2.0, 0))
plate = fillet_vertical_edges(plate, params.DECK_CORNER_FILLET_R)

# 1. Standoff holes -- must match build_bottom_deck.py's positions exactly.
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

# 3. Camera/thermal mast, front edge -- short mounting boss (MAST_HEIGHT now only 8mm, see
# module docstring and params.py) + flat mounting plate for the pan-tilt head.
FRONT_X = BASE_X / 2.0 - 30.0  # mm, design choice: 30mm inset from the front edge for margin

post = Part.makeBox(params.MAST_POST_D, params.MAST_POST_W, params.MAST_HEIGHT,
                     App.Vector(FRONT_X - params.MAST_POST_D / 2.0, -params.MAST_POST_W / 2.0, THICKNESS))

mount_plate = Part.makeBox(params.PANTILT_BASE_W, params.PANTILT_BASE_D, params.MAST_FACE_THICKNESS,
                            App.Vector(FRONT_X - params.PANTILT_BASE_W / 2.0, -params.PANTILT_BASE_D / 2.0,
                                       THICKNESS + params.MAST_HEIGHT))
mount_inset = 6.0   # mm, design choice, matches the general corner-bolt-inset convention
for dx in (-(params.PANTILT_BASE_W / 2.0 - mount_inset), params.PANTILT_BASE_W / 2.0 - mount_inset):
    for dy in (-(params.PANTILT_BASE_D / 2.0 - mount_inset), params.PANTILT_BASE_D / 2.0 - mount_inset):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, params.MAST_FACE_THICKNESS,
                                  App.Vector(FRONT_X + dx, dy, THICKNESS + params.MAST_HEIGHT),
                                  App.Vector(0, 0, 1))
        mount_plate = mount_plate.cut(hole)

mast = post.fuse(mount_plate)
plate = plate.fuse(mast)

# 4. LiDAR pedestal, rear-center -- riser + a plate now following the RPLIDAR A1's REAL
# base outline (Chassis v2 item 7, see module docstring). Inset from the rear edge widened
# from the old disc's 55mm to 65mm: the real D-shape's own "tail" (rect_len, above) reaches
# circle_r+rect_len=61.65mm from REAR_X, more than the old 100mm disc's 50mm radius, so it
# needs a bigger inset to stay inside the deck's own rear edge (confirmed by the deck's own
# bounding-box check below, not assumed).
REAR_X = -(BASE_X / 2.0 - 65.0)

riser_h = params.LIDAR_PEDESTAL_HEIGHT - params.LIDAR_TOP_DISC_THICKNESS
riser = Part.makeCylinder(params.LIDAR_RISER_DIA / 2.0, riser_h,
                           App.Vector(REAR_X, 0, THICKNESS), App.Vector(0, 0, 1))

plate_z = THICKNESS + riser_h
circle_r = params.LIDAR_PLATE_WIDTH / 2.0
circle = Part.makeCylinder(circle_r, params.LIDAR_TOP_DISC_THICKNESS,
                            App.Vector(REAR_X, 0, plate_z), App.Vector(0, 0, 1))
# "D-shape" approximation: the rectangle spans from REAR_X (the circle's own CENTER, so it
# genuinely overlaps roughly half the circle's own volume -- a rect that only touched the
# circle at its tangent edge produced 2 disconnected solids that share no face, confirmed
# by a real len(Solids) check, not assumed) out to the full LIDAR_PLATE_LENGTH, extending
# further toward the rear (-X, away from the hind hips).
rect_len = params.LIDAR_PLATE_LENGTH - circle_r   # = L - r, guarantees >= r of real overlap
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

pedestal = riser.fuse(lidar_plate)

# 5. Hip-bracket clearance pockets -- straight through-cut at each real hip position, sized
# to the hollow hip housing's 112x80mm footprint (item 8) plus a fit margin so the bracket's
# CHAMP-sourced 130mm-tall body can pass through this deck. Inner corners filleted
# (HIP_NOTCH_FILLET_R, item 4) -- fillet the cutter box BEFORE cutting, per this project's
# fillet-robustness convention.
pocket_x = params.HIP_X_LENGTH + 2 * params.HIP_CLEARANCE_MARGIN + 2 * params.HIP_ABDUCTION_CLEARANCE_EXTRA
pocket_y = params.HIP_Y_LENGTH + 2 * params.HIP_CLEARANCE_MARGIN + 2 * params.HIP_ABDUCTION_CLEARANCE_EXTRA
# The pocket's outer X edge (175+71=246mm) stops 4mm short of the deck's 250mm end, which left
# a 4mm x 95mm sliver of 3mm sheet hanging off each corner -- too flimsy to laser-cut/handle.
# So the cutter runs from the pocket's inner edge straight out past the deck end (open notch).
# Its Y extent already runs past the deck's side edge, so each corner is now fully open.
pocket_inner_x = params.BASE_TO_HIP_X - pocket_x / 2.0
notch_len_x = BASE_X / 2.0 + 10.0 - pocket_inner_x
for hip_x in (-params.BASE_TO_HIP_X, params.BASE_TO_HIP_X):
    for hip_y in (-params.BASE_TO_HIP_Y, params.BASE_TO_HIP_Y):
        x0 = pocket_inner_x if hip_x > 0 else -pocket_inner_x - notch_len_x
        cutter = Part.makeBox(notch_len_x, pocket_y, THICKNESS,
                               App.Vector(x0, hip_y - pocket_y / 2.0, 0))
        cutter = fillet_vertical_edges(cutter, params.HIP_NOTCH_FILLET_R)
        plate = plate.cut(cutter)

plate = plate.fuse(pedestal)

# 6. Cable pass-through slots (item 4) -- 2 rounded slots between the decks near the
# avionics area, so wiring can cross from the bottom deck (battery) to the top deck
# (Pi4/PCA9685) without routing around the box-section walls.
for sy in (-40.0, 40.0):   # mm, design choice, straddling the Pi4 mount's own Y-extent
    slot = Part.makeCylinder(params.CABLE_PASSTHRU_W / 2.0, THICKNESS,
                              App.Vector(0, sy, 0), App.Vector(0, 0, 1))
    # stadium-shape slot: a cylinder-capped rectangle -- simplest 2D rounded-slot approximation.
    rect = Part.makeBox(params.CABLE_PASSTHRU_L, params.CABLE_PASSTHRU_W, THICKNESS,
                         App.Vector(-params.CABLE_PASSTHRU_L / 2.0, sy - params.CABLE_PASSTHRU_W / 2.0, 0))
    slot_shape = slot.fuse(rect)
    plate = plate.cut(slot_shape)

# 7. Lightening cut-outs -- TOP DECK ONLY (the bottom deck stays solid, ground-facing/dust,
# see item 4), placed in the deck's own clear areas: the mid-body band between the hip
# pockets and outboard of the standoffs, checked to clear every existing feature the same
# way every other placement in this project is checked.
lightening_centers = [(-40.0, 100.0), (-40.0, -100.0), (40.0, 100.0), (40.0, -100.0)]
r = params.LIGHTENING_HOLE_DIA / 2.0
keepout_boxes = [
    (0.0, 0.0, 60.0, 40.0),                                            # Pi4 + avionics cover area
    (FRONT_X, 0.0, params.PANTILT_BASE_W / 2.0 + 10.0, params.PANTILT_BASE_D / 2.0 + 10.0),
    (REAR_X, 0.0, params.LIDAR_PLATE_LENGTH / 2.0 + 10.0, params.LIDAR_PLATE_WIDTH / 2.0 + 10.0),
]
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy2 in (-params.STANDOFF_Y, params.STANDOFF_Y):
        keepout_boxes.append((sx, sy2, 12.0, 12.0))
for hip_x in (-params.BASE_TO_HIP_X, params.BASE_TO_HIP_X):
    for hip_y in (-params.BASE_TO_HIP_Y, params.BASE_TO_HIP_Y):
        keepout_boxes.append((hip_x, hip_y, pocket_x / 2.0, pocket_y / 2.0))

n_cut, n_skip = 0, 0
for cx, cy in lightening_centers:
    clash = any(abs(cx - kx) < (r + hw) and abs(cy - ky) < (r + hh) for kx, ky, hw, hh in keepout_boxes)
    if clash:
        n_skip += 1
        print(f"  SKIPPED lightening hole at ({cx:.0f},{cy:.0f}) -- overlaps a keepout.")
        continue
    hole = Part.makeCylinder(r, THICKNESS, App.Vector(cx, cy, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)
    n_cut += 1
print(f"Lightening cut-outs (top deck only): {n_cut} cut, {n_skip} skipped for keepout overlap.")

# 8. Box-section body-wall flange bolt holes (item 5) -- shared pattern with build_bottom_deck.py.
wall_holes = wall_flange_hole_xy(params.WALL_SIDE_LENGTH, params.BULKHEAD_LENGTH,
                                  params.BULKHEAD_X, BASE_Y, params.WALL_HOLE_INSET,
                                  params.WALL_THICKNESS, params.WALL_FLANGE)
for x, y in wall_holes:
    hole = Part.makeCylinder(params.WALL_BOLT_DIA / 2.0, THICKNESS, App.Vector(x, y, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)

# 9. Top-deck "avionics cover" (Chassis v2 item 2) -- rebuilt from the Pi4's real 85x56mm
# board outline + clearance, wide enough to also cover the PCA9685 mounted beside it, with a
# full-height opening on both short (connector) edges + top vent slots. Kept as a SEPARATE
# solid (not fused to the deck plate), removable, same as the old lid.
#
# The Pi4's own mounting-hole pattern (PI4_MOUNT_X/Y, cut in step 2 above) is UNCHANGED and
# stays centered at the deck's own origin (hard constraint: keep every existing mount
# pattern) -- so the cover is NOT symmetric about Y=0: it extends -Y just enough for the
# Pi4 board, and +Y further to also cover the PCA9685 beside it (build_payload.py's Pi4/
# PCA9685 envelopes use these exact same Y bounds).
lid_l = params.PI4_BOARD_L + 2 * params.PI4_LID_CLEARANCE
lid_y_min = -params.PI4_BOARD_W / 2.0 - params.PI4_LID_CLEARANCE
lid_y_max = (params.PI4_BOARD_W / 2.0 + params.PI4_LID_BOARD_GAP + params.PCA9685_W
             + params.PI4_LID_CLEARANCE)
lid_w = lid_y_max - lid_y_min
lid_h = params.PI4_STANDOFF_HEIGHT + params.PI4_CONNECTOR_HEIGHT + 5.0   # mm, +5mm fit margin
lw = params.TOPDECK_LID_WALL
lid_outer = Part.makeBox(lid_l, lid_w, lid_h, App.Vector(-lid_l / 2.0, lid_y_min, THICKNESS))
lid_inner = Part.makeBox(lid_l - 2 * lw, lid_w - 2 * lw, lid_h - lw,
                          App.Vector(-lid_l / 2.0 + lw, lid_y_min + lw, THICKNESS))
lid = lid_outer.cut(lid_inner)

# Connector-side openings: full-height slots on BOTH short (X) ends, spanning the Pi4
# board's own Y-band (centered at Y=0, matching the mount pattern) -- the real Pi4 has
# connectors on both short edges (USB-C power + 2x micro-HDMI + audio on one, Gigabit
# Ethernet + 2x USB2 + 2x USB3 on the other).
pi4_y0 = -params.PI4_BOARD_W / 2.0
conn_slot_w = params.PI4_BOARD_W
for xside in (-lid_l / 2.0, lid_l / 2.0 - lw):
    slot = Part.makeBox(lw, conn_slot_w, lid_h, App.Vector(xside, pi4_y0, THICKNESS))
    lid = lid.cut(slot)

# Top vent slots -- generic array, design choice.
n_vents = 5
vent_y0 = lid_y_min + 15.0
for i in range(n_vents):
    vy = vent_y0 + i * params.VENT_SLOT_PITCH
    if vy + params.VENT_SLOT_W / 2.0 > lid_y_max - 15.0:
        break
    vent = Part.makeBox(params.VENT_SLOT_L, params.VENT_SLOT_W, lw,
                         App.Vector(-params.VENT_SLOT_L / 2.0, vy - params.VENT_SLOT_W / 2.0, THICKNESS + lid_h - lw))
    lid = lid.cut(vent)

# 10. Stiffening ribs -- SUPERSEDED, see params.py's own "6. Ribbed decks" note and module
# docstring: a laser-cut sheet can't carry printed ribs; the box-section walls (item 5) now
# carry that load instead. No ribs are built here any more.

part = doc.addObject("Part::Feature", "TopDeck")
part.Shape = plate
doc.recompute()

lid_obj = doc.addObject("Part::Feature", "TopDeckLid")
lid_obj.Shape = lid
doc.recompute()

bbox = plate.BoundBox
print(f"TopDeck built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print(f"TopDeckLid (avionics cover, item 2) solid valid: {lid.isValid()} -- built from the "
      f"real Pi4 85x56mm board outline + {params.PI4_LID_CLEARANCE:.0f}mm clearance, "
      f"{lid_l:.0f}x{lid_w:.0f}x{lid_h:.0f}mm overall, connector-side openings on both ends, "
      f"also covers the PCA9685 alongside. GEOMETRIC ENCLOSURE ONLY -- real IP-rating "
      f"depends on gaskets/seals not modelable here, stated honestly.")
print(f"Camera/thermal mast top: {THICKNESS + params.MAST_HEIGHT:.1f}mm above deck (CUT from "
      f"50mm to {params.MAST_HEIGHT:.0f}mm for Chassis v2 item 1, LiDAR scan-plane occlusion "
      f"fix -- see params.py). LiDAR pedestal top: {THICKNESS + params.LIDAR_PEDESTAL_HEIGHT:.1f}mm "
      f"above deck (real-outline plate, item 7).")

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"
doc.saveAs(f"{out_dir}/top_deck.FCStd")
Part.export([part, lid_obj], f"{out_dir}/top_deck.step")
Part.export([part, lid_obj], f"{out_dir}/top_deck.stl")
print("Saved: top_deck.FCStd, top_deck.step, top_deck.stl (deck + avionics cover)")
