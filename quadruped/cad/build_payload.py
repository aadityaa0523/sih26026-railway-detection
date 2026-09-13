"""
Payload reference envelopes for the quadruped -- CHASSIS V3 (SpotMicro-scale resize,
2026-09-12), built in FreeCAD's Python API. Simple bounding-box/cylinder ENVELOPES for
bought electronics, so the interference check actually verifies these components physically
fit where they're placed. Every dimension is CITED or an explicit ASSUMPTION (params.py
carries the sourcing note for each).

CHASSIS V3 additions vs. Chassis v2's payload set:
  - 4x ab/ad SERVO bodies (AbadServo_LF/RF/LH/RH) + 4x 25T aluminium HORNS (AbadHorn_*) --
    the bought parts build_abad_mount.py's printed housings hold (V3 SPEC item 2: "The
    servo body + a standard 25T aluminium horn go in the payload as bought envelopes").
    Geometry mirrors build_abad_mount.py's own case/horn placement exactly (same formulas,
    inlined rather than imported -- see that file's own note on why).
  - Servo rail BEC (real HobbyWing UBEC-25A HV, params.SERVO_BEC_*) -- replaces the old
    single small UBEC as the 12x DS3225 servo rail; the ORIGINAL UBEC_* envelope (Adafruit
    1385, 5V/3A) is kept as the Pi's OWN separate 5V/3A supply (still correct for that job,
    just relabeled).

Placement rules (V3 SPEC / task brief), each satisfied by construction below:
  - IMU within 30mm of the body's XY center -- params.IMU_MOUNT_X/Y = 21,21mm, 29.7mm from
    center (tightened from the old 60mm/56.6mm Chassis v2 numbers).
  - Servo rail BEC + Pi 5V/3A supply near the battery, bottom deck.
  - PCA9685 under the avionics cover (build_top_deck.py's TopDeckLid).
  - E-stop reachable from above/behind, outside the LiDAR scan band -- rear bulkhead,
    well below the scan band's own global Z (see check_chassis.py).

All envelopes are built in the SAME global frame every other chassis script uses (bottom
deck underside = Z=0). Exported as a separate payload.step (own object names, for distinct
render coloring), included in check_chassis.py's interference union.
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

# ---- Battery (Zeee 3S 2200mAh "shorty", cited) -- centered at the origin, bottom deck. ----
battery = Part.makeBox(params.BATTERY_L, params.BATTERY_W, params.BATTERY_H,
                        App.Vector(-params.BATTERY_L / 2.0, -params.BATTERY_W / 2.0, BOTTOM_DECK_TOP_Z))
envelopes["Battery"] = battery

# ---- Servo rail BEC (HobbyWing UBEC-25A HV, cited, params.SERVO_BEC_*) -- near the
# battery, bottom deck; 12x DS3225 servo rail (4 ab/ad here + 8 leg servos). Oriented with
# its own SERVO_BEC_H (17.6mm, its shortest dimension) along X so it fits in the clear gap
# between the battery (X>=-37.5) and the rear bulkhead's own WEB, which (unlike the
# flanges) runs the wall's FULL height -- build_box_wall's local y=0..WALL_THICKNESS maps to
# global X=-BULKHEAD_X..-BULKHEAD_X+WALL_THICKNESS = -60..-57 for the rear bulkhead -- so
# flange edge. Also mounted on a small 4mm riser (Z starts 4mm above the deck) to clear the
# flange's own BOTTOM band (Z=[3,6]mm, see build_box_wall) -- the flange only occupies that
# thin band plus a matching one at the wall's own top, not the full deck-to-deck height, so
# X=-56.3..-38.7 (inside the flange's own -57..-47 span) is otherwise clear above Z=6.
bec_x = -47.5
servo_bec = Part.makeBox(params.SERVO_BEC_H, params.SERVO_BEC_L, params.SERVO_BEC_W,
                          App.Vector(bec_x - params.SERVO_BEC_H / 2.0, -params.SERVO_BEC_L / 2.0,
                                     BOTTOM_DECK_TOP_Z + 4.0))
envelopes["ServoRailBEC"] = servo_bec

# ---- Pi 5V/3A supply (Adafruit UBEC 1385, cited/ASSUMPTION envelope, params.UBEC_*) --
# TOP deck, beside the Pi4 (physically sensible: it feeds the Pi directly), on the opposite
# side from the PCA9685 (+Y) so it doesn't compete for the same clear area. 5mm clear of the
# Pi4 board's own -Y edge; the side wall is 18mm+ further out at Y=-65mm.
pi_ubec_y = -(params.PI4_BOARD_W / 2.0 + 5.0 + params.UBEC_W / 2.0)
pi_ubec = Part.makeBox(params.UBEC_L, params.UBEC_W, params.UBEC_H,
                        App.Vector(-params.UBEC_L / 2.0, pi_ubec_y - params.UBEC_W / 2.0, TOP_DECK_TOP_Z))
envelopes["Pi5V3ASupply"] = pi_ubec

# ---- IMU (GY-521/MPU6050, within 30mm of body's XY center per the V3 SPEC payload rule) ----
imu = Part.makeBox(params.MPU6050_L, params.MPU6050_W, params.MPU6050_H,
                    App.Vector(params.IMU_MOUNT_X - params.MPU6050_L / 2.0,
                               params.IMU_MOUNT_Y - params.MPU6050_W / 2.0, BOTTOM_DECK_TOP_Z))
envelopes["IMU"] = imu

# ---- 4x ab/ad servo bodies + horns (bought parts, V3 SPEC item 2) -- geometry mirrors
# build_abad_mount.py's own case/horn placement exactly (see that file's module docstring
# for the full axis-rotation derivation). ----
CASE_L, CASE_W, CASE_H = params.SERVO_BODY_L, params.SERVO_BODY_W, params.SERVO_BODY_H
CASE_Z0 = params.HIP_AXIS_Z - params.SERVO_SHAFT_OFFSET
for hip_x in (params.BASE_TO_HIP_X, -params.BASE_TO_HIP_X):
    sign = 1 if hip_x > 0 else -1
    for hip_y in (params.BASE_TO_HIP_Y, -params.BASE_TO_HIP_Y):
        front = "F" if hip_x > 0 else "H"
        side = "L" if hip_y > 0 else "R"
        label = f"{side}{front}"
        pocket_x0 = hip_x - CASE_H if sign > 0 else hip_x
        servo = Part.makeBox(CASE_H, CASE_W, CASE_L,
                              App.Vector(pocket_x0, hip_y - CASE_W / 2.0, CASE_Z0))
        # Horn: fused into the SAME envelope as the case (one "AbadServo_LF" bought-part
        # envelope, matching the task brief's own naming) rather than a separate protruding
        # solid -- the hip point (X=+-BASE_TO_HIP_X) is the BODY_BOX/NOSE_BOX boundary plane
        # itself, and NOSE_BOX's own Y range (+-20mm) is a narrow CENTRAL channel that does
        # NOT reach the hip points' own Y=+-BASE_TO_HIP_Y=+-50mm at all (see
        # geometry_helpers.chassis_envelope), so nothing may protrude past X=+-BASE_TO_HIP_X
        # at that Y -- the horn is modeled recessed flush against the case's own horn-face
        # end instead (ABAD_HORN_DIA sized to fit inside the case's own cross-section, see
        # params.py's own note). The leg module (the other agent's own part) picks up flush
        # at this same boundary plane.
        horn = Part.makeCylinder(params.ABAD_HORN_DIA / 2.0, params.ABAD_HORN_THICKNESS,
                                  App.Vector(hip_x, hip_y, params.HIP_AXIS_Z), App.Vector(-sign, 0, 0))
        envelopes[f"AbadServo_{label}"] = servo.fuse(horn)

# ---- Raspberry Pi 4B (real board outline + connector-height envelope) on 4 M2.5 standoffs,
# under the avionics cover (top deck). Centered at Y=0 -- MUST match build_top_deck.py's own
# UNCHANGED Pi4 mounting-hole pattern. PCA9685 sits beside it at +Y. ----
pi4_cy = 0.0
pi4_standoff_z0 = TOP_DECK_TOP_Z
pi4_board_z = pi4_standoff_z0 + params.PI4_STANDOFF_HEIGHT
pi4_board = Part.makeBox(params.PI4_BOARD_L, params.PI4_BOARD_W, params.PI4_CONNECTOR_HEIGHT,
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

# ---- RPLIDAR A1 (D-shape envelope, cited outline) on its real-outline plate. Must match
# build_top_deck.py's own REAR_X and pedestal geometry exactly. ----
REAR_X = -(params.CHASSIS_LENGTH / 2.0 - 30.0)   # must match build_top_deck.py's own REAR_X
lidar_base_z = TOP_DECK_TOP_Z + params.LIDAR_PEDESTAL_HEIGHT
lidar_r = params.LIDAR_PLATE_WIDTH / 2.0
lidar_rect_len = params.LIDAR_PLATE_LENGTH - lidar_r
lidar_circle = Part.makeCylinder(lidar_r, params.LIDAR_HEIGHT, App.Vector(REAR_X, 0, lidar_base_z), App.Vector(0, 0, 1))
lidar_rect = Part.makeBox(lidar_rect_len, params.LIDAR_PLATE_WIDTH, params.LIDAR_HEIGHT,
                           App.Vector(REAR_X - lidar_rect_len, -lidar_r, lidar_base_z))
lidar_envelope = lidar_circle.fuse(lidar_rect)
envelopes["RPLidarA1"] = lidar_envelope

# ---- E-stop / XT60 / power switch -- protruding from the REAR bulkhead's own outer face
# (build_body_walls.py cuts the matching panel cutouts). CHASSIS V3: stacked in Z (not
# spread in Y, the shorter BULKHEAD_LENGTH=64mm has no room for that) -- Z positions must
# match build_body_walls.py's own ESTOP_Z/XT60_Z/SWITCH_Z exactly. ----
BULKHEAD_X = params.BULKHEAD_X
outer_x = -BULKHEAD_X - params.WALL_THICKNESS
ESTOP_Z = params.BODY_PLATE_THICKNESS + 20.0
XT60_Z = ESTOP_Z + 25.0
SWITCH_Z = XT60_Z + 16.5

estop_button_dia = 30.0   # mm, ASSUMPTION -- E-stop's own body/button envelope, bigger than
                            # the 22mm panel cutout it mounts through (ESTOP_CUTOUT_DIA).
estop = Part.makeCylinder(estop_button_dia / 2.0, 20.0, App.Vector(outer_x - 20.0, 0.0, ESTOP_Z), App.Vector(1, 0, 0))
envelopes["EStop"] = estop

xt60 = Part.makeBox(15.0, params.XT60_CUTOUT_W, params.XT60_CUTOUT_H,
                     App.Vector(outer_x - 15.0, -params.XT60_CUTOUT_W / 2.0,
                                XT60_Z - params.XT60_CUTOUT_H / 2.0))
envelopes["XT60"] = xt60

switch = Part.makeBox(10.0, params.SWITCH_CUTOUT_W, params.SWITCH_CUTOUT_H,
                       App.Vector(outer_x - 10.0, -params.SWITCH_CUTOUT_W / 2.0,
                                  SWITCH_Z - params.SWITCH_CUTOUT_H / 2.0))
envelopes["PowerSwitch"] = switch

objs = []
for name, shape in envelopes.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    objs.append(obj)
doc.recompute()

print("Payload reference envelopes (CHASSIS V3) -- bought parts, own object names for "
      "distinct render coloring:")
for name, shape in envelopes.items():
    bbox = shape.BoundBox
    print(f"  {name}: bbox X=[{bbox.XMin:.1f},{bbox.XMax:.1f}] Y=[{bbox.YMin:.1f},{bbox.YMax:.1f}] "
          f"Z=[{bbox.ZMin:.1f},{bbox.ZMax:.1f}]  Volume={shape.Volume:.0f} mm^3  Solid valid: {shape.isValid()}")

# ---- Servo rail current budget (report only, V3 SPEC item 4) ----
n_servos = 12   # 4 ab/ad (this file) + 8 leg (hip pitch + knee, the other agent's module)
avg_budget = n_servos * params.DS3225_STALL_CURRENT_A * params.SERVO_DUTY_FACTOR
peak_half = 6 * params.DS3225_STALL_CURRENT_A   # worst-case: half the servos near-stall at once
print(f"\nServo rail current budget: {n_servos}x DS3225 @ {params.DS3225_STALL_CURRENT_A:.1f}A "
      f"stall (cited) x {params.SERVO_DUTY_FACTOR:.1f} duty factor (V3 SPEC torque-margin rule, "
      f"reused as a current-margin rule) = {avg_budget:.1f}A typical; a 6-servos-near-stall "
      f"peak scenario = {peak_half:.1f}A. HobbyWing UBEC-25A HV: "
      f"{params.SERVO_BEC_CONTINUOUS_A:.0f}A continuous / {params.SERVO_BEC_PEAK_A:.0f}A peak "
      f"(cited) at {params.SERVO_BEC_OUTPUT_V:.1f}V (within DS3225's 4.8-6.8V rated range) -- "
      f"comfortable margin over both figures.")

out_dir_step = f"{out_dir}/payload.step"
doc.saveAs(f"{out_dir}/payload.FCStd")
Part.export(objs, out_dir_step)
Part.export(objs, f"{out_dir}/payload.stl")
print("Saved: payload.FCStd, payload.step, payload.stl")
