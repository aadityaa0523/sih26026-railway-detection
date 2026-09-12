"""
Payload reference envelopes for the quadruped (Chassis v2 item 9), built in FreeCAD's
Python API. These are simple bounding-box/cylinder ENVELOPES for bought electronics --
not detailed models of the parts themselves -- shown so the chassis reads as a real robot
and, more importantly, so assemble_robot.py's interference check actually verifies these
components physically fit where they're placed instead of just leaving empty space unchecked.

Every dimension is either CITED (a real part's spec) or an explicit ASSUMPTION (params.py
carries the sourcing note for each one) -- same convention as every other file in this
project. Placement rules (from the task brief), each satisfied by construction below:
  - IMU within 60mm of the body's XY center, screwed to a deck -- params.IMU_MOUNT_X/Y puts
    it at sqrt(40^2+40^2)=56.6mm from center, and build_bottom_deck.py cuts its mounting hole
    at the same position.
  - UBEC near the battery on the bottom deck.
  - PCA9685 under the avionics cover (build_top_deck.py's TopDeckLid).
  - E-stop reachable from above/behind and outside the LiDAR scan band -- mounted on the
    REAR bulkhead (build_body_walls.py), well below LIDAR_SCAN_BAND_MIN_ABOVE_BASE's global Z.

All envelopes are built already in the SAME global frame assemble_robot.py assembles
everything else in (bottom-deck-native Z=0 = the whole robot's own Z=0), so assemble_robot.py
only needs to read this file's payload.step and include it directly, no further placement math.

Exported as a SEPARATE payload.step (own object names) so it can be colored differently
from the structural parts in the renders (item 11).
"""
import FreeCAD as App
import Part

import params

out_dir = params.CAD_DIR

DECK_GAP = params.BODY_PLATE_THICKNESS + params.STANDOFF_HEIGHT
TOP_DECK_TOP_Z = DECK_GAP + params.BODY_PLATE_THICKNESS
BOTTOM_DECK_TOP_Z = params.BODY_PLATE_THICKNESS

doc = App.newDocument("payload")
envelopes = {}

# ---- Battery (Zeee 3S 2200mAh "shorty", cited) -- sits in the old battery-bay footprint,
# bottom deck, centered at the origin. ----
battery = Part.makeBox(params.BATTERY_L, params.BATTERY_W, params.BATTERY_H,
                        App.Vector(-params.BATTERY_L / 2.0, -params.BATTERY_W / 2.0, BOTTOM_DECK_TOP_Z))
envelopes["Battery"] = battery

# ---- UBEC (item 9: "near the battery on the bottom deck") ----
ubec_x = -(params.BATTERY_L / 2.0 + 8.0 + params.BATTERY_STRAP_SLOT_W + 10.0)   # mm, clear of the strap slot
ubec = Part.makeBox(params.UBEC_L, params.UBEC_W, params.UBEC_H,
                     App.Vector(ubec_x - params.UBEC_L / 2.0, -params.UBEC_W / 2.0, BOTTOM_DECK_TOP_Z))
envelopes["UBEC"] = ubec

# ---- IMU (GY-521/MPU6050, item 9: "within 60mm of body's XY center, screwed to a deck") ----
imu = Part.makeBox(params.MPU6050_L, params.MPU6050_W, params.MPU6050_H,
                    App.Vector(params.IMU_MOUNT_X - params.MPU6050_L / 2.0,
                               params.IMU_MOUNT_Y - params.MPU6050_W / 2.0, BOTTOM_DECK_TOP_Z))
envelopes["IMU"] = imu

# ---- Raspberry Pi 4B (real board outline + connector-height envelope) on 4 M2.5 standoffs,
# under the avionics cover (top deck). Centered at Y=0 -- MUST match build_top_deck.py's own
# UNCHANGED Pi4 mounting-hole pattern (PI4_MOUNT_X/Y, centered at the deck origin, hard
# constraint: keep every existing mount pattern). PCA9685 sits beside it at +Y. ----
pi4_cy = 0.0
pi4_standoff_z0 = TOP_DECK_TOP_Z
pi4_board_z = pi4_standoff_z0 + params.PI4_STANDOFF_HEIGHT
pi4_board = Part.makeBox(params.PI4_BOARD_L, params.PI4_BOARD_W,
                          params.PI4_CONNECTOR_HEIGHT,   # envelope height = tallest connector cluster
                          App.Vector(-params.PI4_BOARD_L / 2.0, pi4_cy - params.PI4_BOARD_W / 2.0, pi4_board_z))
pi4_standoffs = []
for dx in (-params.PI4_MOUNT_X / 2.0, params.PI4_MOUNT_X / 2.0):
    for dy in (pi4_cy - params.PI4_MOUNT_Y / 2.0, pi4_cy + params.PI4_MOUNT_Y / 2.0):
        pi4_standoffs.append(Part.makeCylinder(params.PI4_HOLE_DIA / 2.0 + 1.0, params.PI4_STANDOFF_HEIGHT,
                                                App.Vector(dx, dy, pi4_standoff_z0), App.Vector(0, 0, 1)))
pi4_envelope = pi4_board
for s in pi4_standoffs:
    pi4_envelope = pi4_envelope.fuse(s)
envelopes["Pi4"] = pi4_envelope

# ---- PCA9685 16-channel servo driver (Adafruit 815), under the avionics cover, beside the
# Pi4 (+Y side). ----
pca_cy = pi4_cy + params.PI4_BOARD_W / 2.0 + params.PI4_LID_BOARD_GAP + params.PCA9685_W / 2.0
pca = Part.makeBox(params.PCA9685_L, params.PCA9685_W, params.PCA9685_H + params.PCA9685_CONNECTOR_H,
                    App.Vector(-params.PCA9685_L / 2.0, pca_cy - params.PCA9685_W / 2.0, TOP_DECK_TOP_Z))
envelopes["PCA9685"] = pca

# ---- RPLIDAR A1 (D-shape envelope, cited outline) on its real-outline plate (item 7). ----
REAR_X = -(params.BASE_X_LENGTH / 2.0 - 65.0)   # must match build_top_deck.py's own REAR_X
lidar_base_z = TOP_DECK_TOP_Z + params.LIDAR_PEDESTAL_HEIGHT
lidar_r = params.LIDAR_PLATE_WIDTH / 2.0
lidar_rect_len = params.LIDAR_PLATE_LENGTH - lidar_r   # = L - r, see build_top_deck.py's own note
lidar_circle = Part.makeCylinder(lidar_r, params.LIDAR_HEIGHT, App.Vector(REAR_X, 0, lidar_base_z), App.Vector(0, 0, 1))
lidar_rect = Part.makeBox(lidar_rect_len, params.LIDAR_PLATE_WIDTH, params.LIDAR_HEIGHT,
                           App.Vector(REAR_X - lidar_rect_len, -lidar_r, lidar_base_z))
lidar_envelope = lidar_circle.fuse(lidar_rect)
envelopes["RPLidarA1"] = lidar_envelope

# ---- E-stop / XT60 / power switch -- small envelopes protruding from the REAR bulkhead's
# own outer face (build_body_walls.py cuts the matching panel cutouts, spread along Y at
# the same mid-height Z -- see that file's own comment for why), item 9's "reachable from
# above/behind and outside the LiDAR scan band" placement rule. ----
BULKHEAD_X = params.BULKHEAD_X
mid_z = params.BODY_PLATE_THICKNESS + params.STANDOFF_HEIGHT / 2.0
outer_x = -BULKHEAD_X - params.WALL_THICKNESS

estop_button_dia = 40.0   # mm, cited -- standard 22mm-body E-stop's own mushroom button head diameter.
estop = Part.makeCylinder(estop_button_dia / 2.0, 20.0, App.Vector(outer_x - 20.0, 0.0, mid_z), App.Vector(1, 0, 0))
envelopes["EStop"] = estop

xt60_y = -35.0   # mm, must match build_body_walls.py's own cutout position
xt60 = Part.makeBox(15.0, params.XT60_CUTOUT_W, params.XT60_CUTOUT_H,
                     App.Vector(outer_x - 15.0, xt60_y - params.XT60_CUTOUT_W / 2.0,
                                mid_z - params.XT60_CUTOUT_H / 2.0))
envelopes["XT60"] = xt60

switch_y = 35.0   # mm, must match build_body_walls.py's own cutout position
switch = Part.makeBox(10.0, params.SWITCH_CUTOUT_W, params.SWITCH_CUTOUT_H,
                       App.Vector(outer_x - 10.0, switch_y - params.SWITCH_CUTOUT_W / 2.0,
                                  mid_z - params.SWITCH_CUTOUT_H / 2.0))
envelopes["PowerSwitch"] = switch

objs = []
for name, shape in envelopes.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    objs.append(obj)
doc.recompute()

print("Payload reference envelopes (Chassis v2 item 9) -- bought parts, own object names for "
      "distinct render coloring:")
for name, shape in envelopes.items():
    bbox = shape.BoundBox
    print(f"  {name}: bbox X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}mm  "
          f"Volume={shape.Volume:.0f} mm^3  Solid valid: {shape.isValid()}")

out_dir_step = f"{out_dir}/payload.step"
doc.saveAs(f"{out_dir}/payload.FCStd")
Part.export(objs, out_dir_step)
Part.export(objs, f"{out_dir}/payload.stl")
print("Saved: payload.FCStd, payload.step, payload.stl")
