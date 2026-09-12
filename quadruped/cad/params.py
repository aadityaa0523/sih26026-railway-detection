"""
Shared dimensions for the quadruped CAD scripts. Single source of truth so every
part script (upper leg, lower leg, hip bracket, body plate) cites the same numbers.

CHAMP stock reference numbers -- docs/champ-research.md #3.1, from
champ_description/urdf/properties.urdf.xacro (values there are in meters; converted
to mm here since FreeCAD's Part module and these scripts work in mm).
"""

# ---- CHAMP stock link/body dimensions (docs/champ-research.md #3.1) -------------------
BASE_TO_HIP_X = 175.0        # mm, base_to_hip_x = 0.175m
BASE_TO_HIP_Y = 105.0        # mm, base_to_hip_y = 0.105m

UPPER_LEG_LENGTH = 190.5     # mm, upper_leg_z_length = 0.1905m
LOWER_LEG_LENGTH = 156.0     # mm, lower_leg_z_length = 0.156m

HIP_X_LENGTH = 112.0         # mm, hip_x_length = 0.112m
HIP_Y_LENGTH = 80.0          # mm, hip_y_length = 0.08m
HIP_Z_LENGTH = 130.0         # mm, hip_z_length = 0.130m

BASE_X_LENGTH = 500.0        # mm, base_x_length = 0.5m
BASE_Y_LENGTH = 290.0        # mm, base_y_length = 0.29m
BASE_Z_LENGTH = 130.0        # mm, base_z_length = 0.130m

# ---- Standard-size hobby servo envelope (MG996R / DS3218 share this footprint) --------
SERVO_BODY_L = 40.5          # mm, along the leg's long axis
SERVO_BODY_W = 20.2          # mm
SERVO_BODY_H = 38.0          # mm, body height excluding mounting-tab flange
SERVO_TAB_SPACING = 49.5     # mm, hole-to-hole on the standard mounting tabs
SERVO_TAB_HOLE_DIA = 4.2     # mm, clears an M4 bolt/standard servo screw

# ---- Knee bolt-circle interface shared by upper_leg (knee end) and lower_leg (top end) --
KNEE_HORN_HOLE_DIA = 6.0     # mm, standard servo spline boss clearance at the knee joint
KNEE_BOLT_CIRCLE_DIA = 30.0  # mm, spacing for the 4 screws bolting the two links together

# ---- Bracket design parameters (3D-printed PETG, adjust wall thickness if it prints too flexy) --
WALL = 4.0                   # mm

# ---- Body plate (draft -- see build_body_plate.py header, NOT confirmed to fit battery + sensing head) --
BODY_PLATE_THICKNESS = 6.0   # mm, flat chassis plate thickness (BASE_Z_LENGTH=130mm above is the
                              # real CHAMP body block's full height / electronics clearance envelope,
                              # not the plate's own material thickness)

# Raspberry Pi 4 official mounting-hole spec: 58mm x 49mm rectangle, 2.7mm dia holes.
# https://www.raspberrypi.com/documentation/computers/images/Mechanical-Drawing-4B.pdf
PI4_MOUNT_X = 58.0            # mm
PI4_MOUNT_Y = 49.0            # mm
PI4_HOLE_DIA = 2.7            # mm

# 4 corner through-bolts that mount a hip bracket down onto the body plate -- inset from
# the hip bracket's own 112x80 footprint edge, M4 clearance (reuses SERVO_TAB_HOLE_DIA).
HIP_MOUNT_INSET = 10.0       # mm

# ---- Two-deck sandwich chassis: payload components (build_bottom_deck.py / build_top_deck.py) --
# Bottom deck is a flat plate (draft, same as the old body plate); top deck sits above it
# on standoffs, carrying the Pi4 + camera/thermal mast + LiDAR pedestal. See both scripts'
# module docstrings for the full placement rationale.

# Zeee 3S 2200mAh LiPo "shorty" pack -- real off-the-shelf product spec.
BATTERY_L = 75.0             # mm
BATTERY_W = 34.0             # mm
BATTERY_H = 26.5             # mm

# RPLIDAR A1 (Slamtec) -- official spec is 96.8 x 70.3 x 55mm, D-shaped housing. Modeled
# here as a simple cylinder -- a deliberate simplification of the real D-shaped housing,
# not itself a sourced cylindrical spec.
LIDAR_DIAMETER = 97.0        # mm, ~= 96.8mm official long dimension, rounded up
LIDAR_HEIGHT = 55.0          # mm, official spec

# Raspberry Pi Camera Module -- real Raspberry Pi Foundation mechanical spec: 25 x 24mm
# PCB, ~1mm thick, M2 mounting holes (~2mm dia).
PICAM_PCB_L = 25.0           # mm
PICAM_PCB_W = 24.0           # mm
PICAM_PCB_THICKNESS = 1.0    # mm
PICAM_HOLE_DIA = 2.0         # mm

# AMG8833 thermal camera breakout, Adafruit product 3538 -- real spec.
AMG8833_L = 25.6             # mm
AMG8833_W = 25.3             # mm
AMG8833_H = 6.0              # mm
AMG8833_HOLE_DIA = 2.0       # mm, assumed M2 clearance -- Adafruit's product page doesn't
                              # spec an exact mounting-hole diameter; design choice, not cited.

# Standoffs joining the two decks -- all design choices (no CHAMP/vendor spec applies to
# a sandwich-chassis standoff height/position).
STANDOFF_HEIGHT = 50.0       # mm, clears the 26.5mm battery plus wiring slack underneath
                              # the top deck -- a design choice, not a sourced spec.
STANDOFF_HOLE_DIA = 3.4      # mm, M3 clearance -- standard hobby standoff hardware size.
# STANDOFF_X/Y: the real interference check in assemble_robot.py found the original (150, 85)
# placement put every standoff INSIDE a hip bracket's own 112x80mm footprint (each hip
# bracket is centered at +-BASE_TO_HIP_X/Y, spanning +-HIP_X_LENGTH/2=+-56mm in X and
# +-HIP_Y_LENGTH/2=+-40mm in Y -- an X-band of [119,231]mm on each side). Any
# |STANDOFF_X| < 175-56=119mm clears ALL FOUR hip footprints' X-band at once regardless of
# Y, so Y no longer needs to dodge anything -- kept at 85mm purely for a wide, symmetric
# support spread under the top deck.
STANDOFF_X = 100.0           # mm, was 150.0 -- now < 119mm, clear of every hip footprint
                              # by construction, not just by re-running the check.
STANDOFF_Y = 85.0            # mm, unchanged -- no longer a clearance constraint, see above.

# Battery bay (bottom deck, centered at plate origin for a low/central CG) -- design
# choices: a shallow locating pocket sized to the battery's own footprint, plus 2
# full-thickness strap slots (one at each end) for a hook-and-loop or zip-tie strap.
BATTERY_BAY_POCKET_DEPTH = 2.0   # mm, shallow recess (< BODY_PLATE_THICKNESS=6mm so the
                                   # deck stays solid underneath).
BATTERY_STRAP_SLOT_W = 6.0        # mm, slot width (along the battery's long/X axis).
BATTERY_STRAP_SLOT_L = 20.0       # mm, slot length (along the battery's short/Y axis).

# Narcotics-sensing-bay mount (bottom deck, front edge, underside-facing) -- the fan + 3x
# MQ gas sensors + BME688 assembly's own CAD does not exist yet, so this is ONLY a
# placeholder mounting pattern (4 corner screw holes), sized generously -- a documented
# assumption pending the real sensing-head enclosure, not a real footprint.
SENSING_BAY_L = 90.0             # mm
SENSING_BAY_W = 60.0             # mm
SENSING_BAY_HOLE_DIA = 3.4       # mm, M3 clearance, consistent with the rest of the project.
SENSING_BAY_HOLE_INSET = 10.0    # mm, corner holes inset from the bay footprint's own edge.

# Camera/thermal mast (top deck, front edge) -- design choices; the mast itself has no
# sourced spec, only the two devices it carries (PICAM_*/AMG8833_* above) are sourced.
MAST_HEIGHT = 50.0           # mm
MAST_TILT_DEG = 12.0         # degrees, forward-and-down tilt of the mounting face
MAST_POST_W = 24.0           # mm, post cross-section along Y
MAST_POST_D = 15.0           # mm, post cross-section along X
MAST_FACE_THICKNESS = 5.0    # mm, mounting-face plate thickness

# LiDAR pedestal (top deck, rear-center) -- design choices. The bolt-circle diameter below
# is an ASSUMPTION: a quick web search found no exact official Slamtec bolt-spacing spec for
# the RPLIDAR A1 (only a RobotShop community-forum thread citing 4x M2.5 screws for its
# mounting adapter -- https://community.robotshop.com/forum/t/hole-pattern-and-dimensions-for-rplidar-a1m8-usb-adapter-board/41996
# -- which informs the hole COUNT/diameter here, not the spacing). Sized to fit within the
# LiDAR's ~97mm base with margin.
LIDAR_PEDESTAL_HEIGHT = 70.0      # mm, clearly taller than MAST_HEIGHT (50mm) so the
                                    # LiDAR's 360-degree scan plane clears the camera mast.
LIDAR_RISER_DIA = 50.0            # mm, structural riser cylinder diameter.
LIDAR_TOP_DISC_DIA = 100.0        # mm, top mounting disc, ~= LIDAR_DIAMETER(97mm) + 3mm margin.
LIDAR_TOP_DISC_THICKNESS = 8.0    # mm, top disc thickness (bolt holes are cut through this).
LIDAR_BOLT_CIRCLE_DIA = 75.0      # mm, ASSUMPTION -- see note above.
LIDAR_BOLT_HOLE_DIA = 2.9         # mm, M2.5 clearance -- see note above.

# Hip-bracket pass-through clearance in the top deck -- the real interference check in
# assemble_robot.py found the hip bracket's CHAMP-sourced 130mm height extends 74mm above
# the top deck's own top surface (bracket spans deck-mount-Z to +130mm; the deck sits only
# 56mm above that mount point), so it must pass THROUGH the top deck rather than stop below
# it. Fix chosen deliberately: cut clearance, not shrink the bracket or raise the deck --
# see quadruped/cad/README.md "Hip/deck interference fix" for the full reasoning (keeps the
# CHAMP-matched hip height intact, and keeps the robot's overall height unchanged, which
# matters for the PS's under-carriage/tunnel/coach clearance requirements).
HIP_CLEARANCE_MARGIN = 3.0   # mm, per side -- fit tolerance around the 112x80mm hip
                              # footprint so the bracket doesn't bind against the deck edge.
