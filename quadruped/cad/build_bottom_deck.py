"""
Bottom deck of the quadruped's two-deck sandwich chassis -- CHASSIS V3 (SpotMicro-scale
resize, 2026-09-12), built in FreeCAD's Python API.

Footprint now matches the V3 SPEC's own main BODY_BOX exactly (params.CHASSIS_LENGTH x
CHASSIS_WIDTH = 220 x 130mm, centered at the body's own XY origin -- the geometric center
of the 4 hip points, same convention CHASSIS_LENGTH/WIDTH reuses directly), not a draft
CHAMP-stock 500x290mm footprint. Underside stays at global Z=0 (unchanged convention);
HIP_AXIS_Z=32mm above that is where the ab/ad servo shafts sit (params.py).

Still a plain THROUGH-FEATURES-ONLY 3mm sheet (3mm acrylic for the prototype,
params.DENSITY_ACRYLIC, cited; 5052 aluminium noted as the production upgrade, identical
geometry) -- same laser-cut-sheet convention as Chassis v2, just resized. Outer corners
rounded (DECK_CORNER_FILLET_R) before any hole is cut, per this project's fillet-robustness
convention.

Six things cut into the sheet:
  1. Ab/ad servo mount base-flange bolt holes (16 total, 4 per hip x 4 hips) -- positions
     RECOMPUTED here with the exact same formula build_abad_mount.py uses (both scripts
     build executable top-level code with side effects, per this project's no-__main__-guard
     convention, so importing one from the other to share a function would re-run its whole
     build+export -- inlining the small formula instead, same reasoning
     geometry_helpers.wall_flange_hole_xy's own docstring gives for why THAT one instead
     lives in a side-effect-free shared module). REPLACES the old HIP_X/Y_LENGTH-based
     hip-bracket bolt pattern (that whole mechanism moved outboard of the deck edge, see
     build_abad_mount.py).
  2. Standoff holes (4, params.STANDOFF_X/Y) for the real M3 hex standoffs
     (geometry_helpers.build_hex_standoff) that carry the top deck.
  3. Battery bay, centered at the origin for a low/central CG: 2 through strap slots.
  4. Sniffer-arm mount post bolt holes (4) -- build_sniffer_arm.py's own base post stands
     on the bottom deck at (SNIFFER_MOUNT_X, SNIFFER_MOUNT_Y); this cuts its matching
     4-corner bolt pattern.
  5. Body-wall flange bolt holes (8) -- shared with build_body_walls.py via
     geometry_helpers.wall_flange_hole_xy, resized for the new CHASSIS_WIDTH.
  6. IMU mounting hole -- within 30mm of the body's own XY center (V3 SPEC payload rule),
     clear of the battery bay footprint.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import fillet_vertical_edges, wall_flange_hole_xy

BASE_X = params.CHASSIS_LENGTH  # 220mm, V3 SPEC BODY_BOX X extent
BASE_Y = params.CHASSIS_WIDTH   # 130mm, V3 SPEC BODY_BOX Y extent
THICKNESS = params.BODY_PLATE_THICKNESS  # 3mm


def _abad_flange_hole_xy():
    """Must match build_abad_mount.py's own flange-hole formula exactly (see that file)."""
    wall, case_h, case_w = params.ABAD_MOUNT_WALL, params.SERVO_BODY_H, params.SERVO_BODY_W
    inset = params.ABAD_MOUNT_INSET
    pts = []
    for hip_x in (params.BASE_TO_HIP_X, -params.BASE_TO_HIP_X):
        sign = 1 if hip_x > 0 else -1
        for hip_y in (params.BASE_TO_HIP_Y, -params.BASE_TO_HIP_Y):
            block_x0 = hip_x - (case_h + wall) if sign > 0 else hip_x
            block_y0 = hip_y - (case_w / 2.0 + wall)
            for dx in (inset, (case_h + 2 * wall) - inset):
                for dy in (inset, (case_w + 2 * wall) - inset):
                    pts.append((block_x0 + dx, block_y0 + dy))
    return pts


def _sniffer_post_hole_xy():
    """Must match build_sniffer_arm.py's own mount_post_hole_xy() formula exactly."""
    boom_x0 = 100.0
    return [(boom_x0 + dx, sy) for dx in (4.0, 8.0) for sy in (-8.0, 8.0)]

doc = App.newDocument("bottom_deck")

plate = Part.makeBox(BASE_X, BASE_Y, THICKNESS, App.Vector(-BASE_X / 2.0, -BASE_Y / 2.0, 0))
plate = fillet_vertical_edges(plate, params.DECK_CORNER_FILLET_R)

# 1. Ab/ad servo mount base-flange bolt holes -- see build_abad_mount.py.
abad_holes = _abad_flange_hole_xy()
for x, y in abad_holes:
    hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, THICKNESS, App.Vector(x, y, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)

# 2. Standoff holes -- same 4 XY positions build_top_deck.py cuts.
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        hole = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, THICKNESS,
                                  App.Vector(sx, sy, 0), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

# 3. Battery bay, centered at plate origin -- low/central CG, 2 through strap slots.
strap_x = params.BATTERY_L / 2.0 + 8.0
for sx in (-strap_x, strap_x):
    slot = Part.makeBox(params.BATTERY_STRAP_SLOT_W, params.BATTERY_STRAP_SLOT_L, THICKNESS,
                         App.Vector(sx - params.BATTERY_STRAP_SLOT_W / 2.0,
                                    -params.BATTERY_STRAP_SLOT_L / 2.0, 0))
    plate = plate.cut(slot)

# 4. Sniffer-arm mount boom -- 4-corner bolt pattern, matches build_sniffer_arm.py's own
# boom footprint exactly (see that file's mount_post_hole_xy()).
for x, y in _sniffer_post_hole_xy():
    hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, THICKNESS, App.Vector(x, y, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)

# 5. Box-section body-wall flange bolt holes -- shared pattern, resized for CHASSIS_WIDTH.
wall_holes = wall_flange_hole_xy(params.WALL_SIDE_LENGTH, params.BULKHEAD_LENGTH,
                                  params.BULKHEAD_X, BASE_Y, params.WALL_HOLE_INSET,
                                  params.WALL_THICKNESS, params.WALL_FLANGE)
for x, y in wall_holes:
    hole = Part.makeCylinder(params.WALL_BOLT_DIA / 2.0, THICKNESS, App.Vector(x, y, 0), App.Vector(0, 0, 1))
    plate = plate.cut(hole)

# 6. MPU6050/GY-521 IMU mounting hole -- within 30mm of the body's XY center (V3 SPEC
# payload rule), clear of the battery bay (|Y|=21 > battery half-width 17mm).
imu_dist = (params.IMU_MOUNT_X ** 2 + params.IMU_MOUNT_Y ** 2) ** 0.5
assert imu_dist <= 30.0, f"IMU mount at {imu_dist:.1f}mm from center exceeds the 30mm V3 SPEC rule"
imu_hole = Part.makeCylinder(params.MPU6050_HOLE_DIA / 2.0, THICKNESS,
                              App.Vector(params.IMU_MOUNT_X, params.IMU_MOUNT_Y, 0), App.Vector(0, 0, 1))
plate = plate.cut(imu_hole)

part = doc.addObject("Part::Feature", "BottomDeck")
part.Shape = plate
doc.recompute()

bbox = plate.BoundBox
print(f"BottomDeck (CHASSIS V3) built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print(f"{THICKNESS:.0f}mm acrylic sheet (params.DENSITY_ACRYLIC, prototype; 5052 aluminium "
      f"production upgrade), through-features only. {len(abad_holes)} ab/ad flange holes, "
      f"{len(wall_holes)} body-wall flange holes cut. IMU at {imu_dist:.1f}mm from center.")

out_dir = params.CAD_DIR
doc.saveAs(f"{out_dir}/bottom_deck.FCStd")
Part.export([part], f"{out_dir}/bottom_deck.step")
Part.export([part], f"{out_dir}/bottom_deck.stl")
print("Saved: bottom_deck.FCStd, bottom_deck.step, bottom_deck.stl")
