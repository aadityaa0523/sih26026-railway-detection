"""
Shared dimensions for the quadruped CAD scripts. Single source of truth so every
part script (upper leg, lower leg, hip bracket, body plate) cites the same numbers.

CHAMP stock reference numbers -- docs/champ-research.md #3.1, from
champ_description/urdf/properties.urdf.xacro (values there are in meters; converted
to mm here since FreeCAD's Part module and these scripts work in mm).
"""
import os

# Output directory = this file's own folder, so scripts write next to themselves in any
# checkout/worktree (freecadcmd scripts are run from this directory and import params).
CAD_DIR = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

# ==========================================================================================
# V3 SPEC -- SpotMicro-scale redesign (option B, 2026-09-12). This block is the CONTRACT the
# leg module, the chassis and the CHAMP/URDF config are built against in parallel. Change it
# only deliberately; every other section may be edited by its owning script.
# Why: check_mechanics.py showed the v2 leg can't walk (4/12 joints, coplanar knee, MG996R
# 3-9x under-rated at a 500x290mm / 4.7kg scale). See README "Mechanics check".
# ==========================================================================================
# Frame: body origin at the geometric centre of the 4 hip points, +X front, +Y left, +Z up.
# HIP POINT = centre of the hip ab/ad servo's horn face = CHAMP's <leg>_hip_joint origin.
# Ab/ad axis runs along X through the hip point; front ab/ad shafts point +X, hind -X.
BASE_TO_HIP_X = 110.0        # mm, design choice (SpotMicro-scale; body_length ~186mm in
                              # mike4192/spotMicro, stretched for the Pi4 + LiDAR + sensing payload)
BASE_TO_HIP_Y = 50.0         # mm, design choice (SpotMicro body_width 78mm -> +-39, widened to
                              # fit the Pi4's 56mm width between the ab/ad servos)

# Leg kinematics (CHAMP joint-to-joint distances -- NOT visual box sizes).
THIGH_LENGTH = 107.5         # mm, hip-pitch axis -> knee axis. Precedent: mike4192/spotMicro
                              # upper_leg_link_length 0.1075m (citation to be verified).
SHIN_LENGTH = 130.0          # mm, knee axis -> foot contact point. Precedent: spotMicro
                              # lower_leg_link_length 0.130m (citation to be verified).
HIP_TO_FOOT_Y_TARGET = 55.0  # mm, target lateral offset ab/ad axis -> foot centreline, +-10mm.
                              # Precedent: spotMicro hip_link_length 0.055m. Exact per-joint
                              # offsets are the leg module's OUTPUT (leg_kinematics.json).
# Required collision-free joint ranges (geometry only; the servo's own ~180 deg travel is
# placed inside these by horn indexing at assembly):
ABAD_RANGE_DEG = 25.0        # +-, hip ab/ad
HIP_PITCH_RANGE_DEG = 90.0   # +-, hip pitch
KNEE_RANGE_DEG = 150.0       # +-, knee (both fold directions geometrically free)

# Envelope contract, in the LF HIP FRAME (origin at the LF hip point, body axes). Mirror
# in X for hind legs and in Y for right legs. The leg module, in EVERY pose within the ranges
# above, must stay out of BODY_BOX and NOSE_BOX and below LEG_MAX_Z. The chassis must stay
# inside BODY_BOX + NOSE_BOX, or above LEG_MAX_Z (e.g. the LiDAR).
#   BODY_BOX: X [-2*BASE_TO_HIP_X, 0], Y [-(BASE_TO_HIP_Y+BODY_MAX_HALF_W), BODY_MAX_HALF_W-BASE_TO_HIP_Y],
#             Z [-BODY_MAX_BELOW_HIP, LEG_MAX_Z]
#   NOSE_BOX (between the two shoulders, front and rear): X [0, NOSE_MAX_X],
#             Y [-(BASE_TO_HIP_Y+NOSE_HALF_W), NOSE_HALF_W-BASE_TO_HIP_Y], Z [-NOSE_MAX_BELOW_HIP, LEG_MAX_Z]
BODY_MAX_HALF_W = 65.0       # mm, body |Y| limit
BODY_MAX_BELOW_HIP = 35.0    # mm, body may reach this far below the ab/ad axis
LEG_MAX_Z = 60.0             # mm above the ab/ad axis; above this belongs to the chassis
NOSE_HALF_W = 20.0           # mm, pan-tilt / sniffer arm zone between the shoulders
NOSE_MAX_X = 60.0            # mm beyond the hip horn-face plane
NOSE_MAX_BELOW_HIP = 120.0   # mm, sniffer arm deployed reach

# Actuators: 12 leg servos, standard DS32xx case. DS3218 datasheet: 40 x 20 x 40.5mm body,
# 49.5mm hole spacing, 54.5mm tab span, shaft 10mm from one end, tab underside 27.7mm above
# the base (drawing read -- verify). DS3225 (25kg-cm) / DS3235 (35kg-cm) share the case.
LEG_SERVO = "DS3225"         # default; final pick by check_mechanics.py torque margin
SERVO_BODY_L = 40.0          # mm
SERVO_BODY_W = 20.0          # mm
SERVO_BODY_H = 40.5          # mm, base to top of case (excl. spline)
SERVO_TAB_SPACING = 49.5     # mm, hole-to-hole
SERVO_TAB_SPAN = 54.5        # mm, tab tip to tab tip
SERVO_TAB_HOLE_DIA = 4.2     # mm, M4 clearance (DS3218 listing: M4 bolts)
SERVO_SHAFT_OFFSET = 10.0    # mm, shaft axis to nearest body end
SERVO_TAB_HEIGHT = 27.7      # mm, base to tab underside (ASSUMPTION, drawing read)
# Torque design rule: static worst-case joint torque <= 0.4 x servo stall torque.
SERVO_DUTY_FACTOR = 0.4

# CHAMP gait targets (the config package's gait.yaml)
GAIT_NOMINAL_HEIGHT = 190.0  # mm, hip axis to ground
GAIT_SWING_HEIGHT = 30.0     # mm
GAIT_MAX_VEL_X = 0.25        # m/s
GAIT_MAX_VEL_Y = 0.12        # m/s
GAIT_MAX_ANG_Z = 0.8         # rad/s
GAIT_STANCE_DURATION = 0.25  # s
MASS_TARGET_KG = 2.6         # whole robot, incl. battery

# ---- v2 legacy (500x290 CHAMP-stock scale) -- remove each once no script uses it ---------
UPPER_LEG_LENGTH = 190.5     # mm, upper_leg_z_length = 0.1905m (CHAMP VISUAL box size)
LOWER_LEG_LENGTH = 156.0     # mm, lower_leg_z_length = 0.156m (CHAMP VISUAL box size)

HIP_X_LENGTH = 112.0         # mm, hip_x_length = 0.112m
HIP_Y_LENGTH = 80.0          # mm, hip_y_length = 0.08m
HIP_Z_LENGTH = 130.0         # mm, hip_z_length = 0.130m

BASE_X_LENGTH = 500.0        # mm, base_x_length = 0.5m
BASE_Y_LENGTH = 290.0        # mm, base_y_length = 0.29m
BASE_Z_LENGTH = 130.0        # mm, base_z_length = 0.130m

# ---- Knee bolt-circle interface shared by upper_leg (knee end) and lower_leg (top end) --
KNEE_HORN_HOLE_DIA = 6.0     # mm, standard servo spline boss clearance at the knee joint
KNEE_BOLT_CIRCLE_DIA = 30.0  # mm, spacing for the 4 screws bolting the two links together

# ---- Bracket design parameters (3D-printed PETG, adjust wall thickness if it prints too flexy) --
WALL = 4.0                   # mm

# ---- Body plate -- CHASSIS V2 (item 4): now a laser-cut sheet, not a printed/cast plate ----
# 500x290mm cannot be 3D-printed on a common bed and ribs (improvement 6, below) cannot be
# laser-cut -- so the deck material changed to 3mm 5052 aluminium sheet (production intent) or
# 3mm acrylic (prototype, identical geometry) -- DESIGN CHOICE, both through-feature-only,
# no ribs, no blind pockets. This SUPERSEDES the original 6.0mm-then-4.0mm plate+rib design
# (see "6. Ribbed decks" below, kept for history) -- stiffness now comes from the box-section
# body walls (item 5, build_body_walls.py) closing the inter-deck bay instead of ribs.
BODY_PLATE_THICKNESS = 3.0   # mm, was 4.0mm (see above). BASE_Z_LENGTH=130mm above is still the
                              # real CHAMP body block's full height / electronics clearance
                              # envelope, not this sheet's own thickness.

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
BATTERY_BAY_POCKET_DEPTH = 2.0   # mm, SUPERSEDED (Chassis v2 item 4): the sheet deck is only
                                   # BODY_PLATE_THICKNESS=3mm thick now, no blind pocket is cut
                                   # any more (through-features only on a laser-cut sheet) --
                                   # build_bottom_deck.py keeps only the 2 strap slots below.
                                   # Constant kept for history/reference, no longer read.
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
# MAST_HEIGHT CUT from 50.0mm to 8.0mm for Chassis v2 item 1 (LiDAR scan-plane occlusion,
# see "CHASSIS V2" section below for the full derivation) -- the pan-tilt head's own fixed
# local height above its mount (~79mm, build_camera_pan_tilt.py, unmodified) put its neutral
# pose top at global Z~192mm, well inside the LiDAR's assumed scan band (Z~156-176mm); with
# MAST_HEIGHT this short the head's neutral top lands at ~148mm, ~8mm clear of the band's own
# floor. This ALSO drops the robot's overall max Z from 192mm (old pan-tilt top) to ~181mm
# (LiDAR unit top, pedestal_top+LIDAR_HEIGHT) -- lower overall height, a net win for the PS's
# under-carriage/tunnel/coach clearance requirement, not just an occlusion fix.
MAST_HEIGHT = 8.0            # mm, was 50.0mm -- see note above.
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
LIDAR_PEDESTAL_HEIGHT = 70.0      # mm, clearly taller than MAST_HEIGHT so the LiDAR's
                                    # 360-degree scan plane clears the camera mast (even more
                                    # true now MAST_HEIGHT dropped to 8mm, see above).
LIDAR_RISER_DIA = 50.0            # mm, structural riser cylinder diameter.
# LIDAR_TOP_DISC_DIA/THICKNESS SUPERSEDED by Chassis v2 item 7's real-outline plate
# (LIDAR_PLATE_* below) -- kept here for history, no longer read by build_top_deck.py.
LIDAR_TOP_DISC_DIA = 100.0        # mm, top mounting disc, ~= LIDAR_DIAMETER(97mm) + 3mm margin.
LIDAR_TOP_DISC_THICKNESS = 8.0    # mm, top disc thickness (bolt holes are cut through this);
                                    # STILL USED as the new real-outline plate's thickness too.
LIDAR_BOLT_CIRCLE_DIA = 50.0      # mm, ASSUMPTION -- see note above. SHRUNK from 75.0mm for
                                    # Chassis v2 item 7: the new real-outline plate is only
                                    # LIDAR_PLATE_WIDTH=70.3mm across, so a 75mm bolt-circle
                                    # diameter would put 2 of the 4 holes outside the plate's
                                    # own material; 50mm (radius 25mm) fits inside 70.3mm width
                                    # with margin on both sides.
LIDAR_BOLT_HOLE_DIA = 2.9         # mm, M2.5 clearance -- see note above.

# Hip-bracket pass-through clearance in the top deck -- the real interference check in
# assemble_robot.py found the hip bracket's CHAMP-sourced 130mm height extends well above
# the top deck's own top surface (bracket spans deck-mount-Z to +130mm; the deck originally
# sat only 56mm above that mount point, now 53mm since Chassis v2 item 4 trimmed
# BODY_PLATE_THICKNESS 4mm->3mm -- still far short of 130mm either way), so it must pass
# THROUGH the top deck rather than stop below it. Fix chosen deliberately: cut clearance,
# not shrink the bracket or raise the deck --
# see quadruped/cad/README.md "Hip/deck interference fix" for the full reasoning (keeps the
# CHAMP-matched hip height intact, and keeps the robot's overall height unchanged, which
# matters for the PS's under-carriage/tunnel/coach clearance requirements).
HIP_CLEARANCE_MARGIN = 3.0   # mm, per side -- fit tolerance around the 112x80mm hip
                              # footprint so the bracket doesn't bind against the deck edge.
# Extra one-sided margin added on top of HIP_CLEARANCE_MARGIN once HIP_ABDUCTION_DEG (below)
# tilts the hip bracket -- the tilted footprint shifts laterally by roughly
# HIP_Z_LENGTH_at_deck * sin(HIP_ABDUCTION_DEG) at the height the top deck cuts through the
# bracket. Value below was arrived at the same way the original HIP_CLEARANCE_MARGIN /
# STANDOFF_X fix was: computed, then CONFIRMED against assemble_robot.py's real
# boolean-geometry interference check, not assumed.
HIP_ABDUCTION_CLEARANCE_EXTRA = 12.0   # mm, design choice, see above.

# A SECOND, separate clash was found and confirmed the same way (real assemble_robot.py
# boolean check, then a diagnostic isolating exactly which two solids and which XYZ region
# overlapped): the hip-abduction tilt swings each HIND hip bracket's own top-inner corner
# (near its Z=130mm top, the tallest part of the block) INWARD by ~21mm at that height --
# enough to reach into the LiDAR pedestal's own 100mm top mounting disc, which sits close
# to the hind hip mounts by construction (REAR_X=-195mm vs. hind hip X=-175mm, only 20mm
# nominal separation -- already the minimum the disc's own 100mm diameter and the deck's
# rear edge allow, see build_top_deck.py). REMOVED for Chassis v2 item 7: the notched 100mm
# disc is replaced by a plate that follows the LiDAR's own real (smaller, D-shaped) footprint
# -- see LIDAR_PLATE_* below -- which the interference check (assemble_robot.py) confirms
# clears the tilted hind hip brackets WITHOUT needing these notches at all (deleted per this
# file's own convention of removing a param once it's confirmed unused, not before).

# ==========================================================================================
# 8 real-quadruped-precedent improvements added after the first interference-free pass.
# Each constant below is either a real cited spec (SG90 servo) or an explicitly flagged
# design choice/assumption -- same convention as every constant above.
# ==========================================================================================

# ---- 1. Hip abduction/adduction angle (assemble_robot.py placement only, see its docstring) --
# Real quadrupeds (Spot, ANYmal, Unitree) use a powered hip ab/ad joint for sprawl stability.
# CHAMP's stock config has no such joint, so this is implemented as a STATIC mounting tilt of
# the whole hip-bracket-and-leg unit, NOT a new powered DOF -- an honest simplification, not
# an active joint. 10 degrees is a DESIGN CHOICE (not sourced): modest, since real
# quadrupeds' ab/ad range is typically small (a few to ~15 degrees), enough to add sprawl
# without turning the mammalian trot into a sprawling gait.
HIP_ABDUCTION_DEG = 10.0

# ---- 2. Dust bellows/gaiters + top-deck lid --------------------------------------------
# Bellows/gaiters are a BOUGHT or MOLDED rubber/silicone part (like the foot cap below),
# NOT 3D-printed -- modeled here as a simple cylindrical boot (the task's own "fine CAD
# approximation" of a real molded part). Same boot dimensions are reused at both the knee
# joint (upper/lower leg gap) and the hip joint (hip-bracket-horn/upper-leg-pocket gap) --
# same reuse-the-same-generic-interface approach already used for KNEE_BOLT_CIRCLE_DIA.
BELLOWS_ID = 34.0            # mm, design choice -- clears the 28.2x8mm leg bar's own
                              # diagonal (~29.3mm) and the 30mm knee bolt circle with margin.
BELLOWS_OD = 42.0            # mm, design choice -- thin-wall molded rubber boot.
BELLOWS_LENGTH = 30.0        # mm, design choice -- straddles the joint line by ~15mm/side.

# Top-deck lid: a simple snap-on cover over the Pi4/wiring area. GEOMETRIC ENCLOSURE ONLY --
# real IP-rating depends on gaskets/seals, not modelable here, stated honestly.
TOPDECK_LID_WALL = 2.0       # mm, thinner than the structural WALL (4mm) -- non-structural cover.
TOPDECK_LID_MARGIN = 20.0    # mm, clearance around the PI4_MOUNT_X/Y hole-to-hole spacing --
                              # sized generously since the real Pi4 board (85x56mm) overhangs
                              # its own mounting holes; this is a rough enclosure, not a
                              # tight-fit board outline.
TOPDECK_LID_HEIGHT = 20.0    # mm, design choice -- clears the Pi4 board + GPIO header + wiring.

# ---- 3. Compliant foot (rigid boss + bought spring + rubber cap stack) -------------------
# The compression spring is a BOUGHT part, same documented-assumption level as the existing
# rubber foot cap -- no precise spec invented.
SPRING_BORE_DIA = 12.0       # mm, "generic small compression spring, ~10mm dia range, exact
                              # spec TBD at purchase" -- matches how the rubber foot cap note
                              # was already handled.
SPRING_BORE_DEPTH = 8.0      # mm, design choice, blind bore depth in the (widened) foot boss.

# ---- 4. Pan-tilt camera/thermal mount + 2-DOF sniffer arm (2x SG90 each) -----------------
# SG90 micro servo: real, ubiquitous, well-documented spec (Tower Pro SG90 / generic clones) --
# ~22.2 x 11.8 x 31mm body, ~9g. Standard industry micro servo, cited the same way
# SERVO_BODY_* cites the MG996R/DS3218 envelope -- a well-known component, not needing
# further sourcing. Much smaller/lighter than the leg servos, appropriate for these
# low-torque pan/tilt and dip/swing mechanisms.
SG90_BODY_L = 22.2           # mm
SG90_BODY_W = 11.8           # mm
SG90_BODY_H = 31.0           # mm, body height excluding horn (same convention as SERVO_BODY_H)
SG90_TAB_SPACING = 28.0      # mm, commonly documented SG90 mounting-tab hole spacing.
SG90_TAB_HOLE_DIA = 2.0      # mm, standard SG90 mounting-screw clearance.

# Pan-tilt head (camera + thermal) -- design choices, bolts to the top-deck mast's now-plain
# mounting plate. NOT a fully kinematic mechanism (see README) -- a static "neutral" pose plus
# one "extended" pose (rotated copies) demonstrates the range of motion instead.
PANTILT_BASE_W = 36.0        # mm, base-bracket width -- clears one SG90 body (11.8mm) + walls.
PANTILT_BASE_D = 36.0        # mm, base-bracket depth.
PANTILT_BASE_T = 8.0         # mm, base-bracket plate thickness (matches BRACKET_THICKNESS elsewhere).
PANTILT_LINK_LENGTH = 30.0   # mm, pan-servo-axis to tilt-servo-axis link length.
PANTILT_PAN_RANGE_DEG = 45.0     # mm -> deg: demonstration pan angle for the "extended" pose.
PANTILT_TILT_RANGE_DEG = 30.0    # deg, demonstration tilt-down angle for the "extended" pose.

# Sniffer arm (narcotics-sensing head, dip + swing) -- design choices, bolts to the bottom
# deck's EXISTING sensing-bay hole pattern (SENSING_BAY_L/W, already in params.py above --
# reused directly as the arm's base footprint so it actually lines up with the deck's
# already-cut holes, not a new mismatched pattern). Same "static neutral + extended pose"
# limitation as the pan-tilt head.
SNIFFER_BASE_T = 8.0         # mm, base-bracket plate thickness.
SNIFFER_LINK_LENGTH = 50.0   # mm, dip-servo-axis to swing-servo-axis link length -- longer
                              # than the pan-tilt link so the head can reach down toward a
                              # target instead of just aiming in place.
SNIFFER_DIP_RANGE_DEG = 60.0     # deg, demonstration "lowered toward target" angle.
SNIFFER_SWING_RANGE_DEG = 30.0   # deg, demonstration swing angle.

# ---- 5. Skid plate ------------------------------------------------------------------------
# UHMW or HDPE -- a design choice, but a real, appropriate one: both are standard low-friction,
# high-wear-resistance materials used for ground-contact skid plates on RC crawlers/rovers.
SKID_PLATE_THICKNESS = 3.0   # mm, within the requested 2-3mm range.
SKID_PLATE_L = 80.0          # mm, sized (with margin, confirmed by build_skid_plate.py's own
                              # geometric check) to the clear gap between the battery bay and
                              # the sensing-bay mount footprints.
SKID_PLATE_W = 100.0         # mm, sized (with margin, confirmed the same way) to the clear
                              # gap inside the two hip-mount Y-bands.
SKID_PLATE_HOLE_DIA = 3.4    # mm, M3 clearance, consistent with the rest of the project.

# ---- 6. Ribbed decks (structural stiffening) -- SUPERSEDED by Chassis v2 item 4/5 ----------
# Standard lightweighting/stiffening technique (thin base plate + a grid of perpendicular
# ribs) -- cited generically as a standard technique, no specific FEA was run.
# SUPERSEDED: a laser-cut sheet deck (Chassis v2 item 4) cannot carry printed ribs at all, so
# build_bottom_deck.py/build_top_deck.py no longer call geometry_helpers.build_deck_ribs --
# the same stiffening GOAL is now met by the box-section body walls (item 5,
# build_body_walls.py) closing the inter-deck bay instead. Constants + the helper function
# kept for history, not deleted (not currently called anywhere).
RIB_WIDTH = 3.0              # mm
RIB_HEIGHT = 10.0            # mm

# ---- 7. Cable routing channels -------------------------------------------------------------
# Shallow groove along each leg link, sized for a typical 3-4 servo signal wire bundle --
# design choice, no specific spec beyond "enough clearance for the wires."
CABLE_CHANNEL_WIDTH = 5.0    # mm
CABLE_CHANNEL_DEPTH = 2.0    # mm
CABLE_CHANNEL_END_MARGIN = 25.0  # mm, kept clear of each link's own servo pocket/bolt circle.

# ---- 8. Shell/livery panels (cosmetic) -- SUPERSEDED by Chassis v2 item 5 ------------------
# Simple flat cover panels over the body-deck sides only (see README for what was/wasn't
# done). Includes one flat area sized for an RPF/security branding decal.
# SUPERSEDED: build_shell_panels.py's two cosmetic, non-structural side panels are replaced by
# build_body_walls.py's structural box-section walls/bulkheads (item 5) -- DECAL_W/H are
# REUSED there (same flat decal area requirement), SHELL_PANEL_THICKNESS is no longer read
# (the new walls use WALL_THICKNESS below instead). build_shell_panels.py itself is left in
# place (not deleted) but no longer called from assemble_robot.py or the README rebuild list.
SHELL_PANEL_THICKNESS = 2.0  # mm, thin cosmetic cover, not structural. Superseded, see above.
DECAL_W = 80.0                # mm, flat branding-decal area width. Still used (item 5).
DECAL_H = 40.0                # mm, flat branding-decal area height. Still used (item 5).

# ==========================================================================================
# CHASSIS V2 -- senior-reviewer pass after rendering + inspecting the 8-improvement model
# above. Each new constant below is CITED (datasheet/URL), a DESIGN CHOICE, or an explicit
# ASSUMPTION, same convention as every constant above. See quadruped/cad/README.md's own
# "Chassis v2" section for the full per-item rationale and check results.
# ==========================================================================================

# ---- Item 1: LiDAR scan-plane occlusion check ----------------------------------------------
# RPLIDAR A1M8 official datasheet (Slamtec, rev 2016-07-04, "LD108_SLAMTEC_rplidar_datasheet_
# A1M8_v1.0_en.pdf") confirms the 96.8x70.3x55mm envelope (LIDAR_DIAMETER/LIDAR_HEIGHT above)
# and its own Chapter 5 mechanical-dimension drawing shows the rotating scanner head sitting
# near the TOP of the unit's housing (the "fixed platform" customization diagram, Figure 5-1,
# shows the customizable base as only the BOTTOM third of the assembly) -- but the drawing's
# own numeric callout for the exact scan-plane height above the unit's base was not legible in
# the extracted PDF text (dense CAD dimension lines, not a tabulated spec). Per this task's own
# documented fallback, treated as an ASSUMPTION: a conservative band from 30 to 50mm above the
# LiDAR's own base (i.e. above the pedestal's top surface, where the real A1M8 sits) --
# consistent with a rotating head near the top of a 55mm-tall unit, not at its base.
LIDAR_SCAN_BAND_MIN_ABOVE_BASE = 30.0    # mm, ASSUMPTION -- see above.
LIDAR_SCAN_BAND_MAX_ABOVE_BASE = 50.0    # mm, ASSUMPTION -- see above.
LIDAR_SCAN_BAND_OUTER_RADIUS = 600.0     # mm, design choice -- bigger than the robot's own
                                            # footprint (half-diagonal ~290mm) so the check
                                            # catches an occluder anywhere around the robot,
                                            # not just within its own footprint.
LIDAR_SCAN_BAND_CLEARANCE = 2.0          # mm, design choice -- the annulus's own inner radius
                                            # is LIDAR_PLATE_LENGTH/2 + this, so the check
                                            # doesn't flag the LiDAR's own mounting plate
                                            # immediately under it as a false "occlusion".

# ---- Item 2: Raspberry Pi 4B real board outline + connector envelope (avionics cover) ------
# Official mechanical drawing, Raspberry Pi 4 Model B Datasheet Release 1.1 (March 2024),
# Section 3 "Mechanical Specification", Figure 1 --
# https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-datasheet.pdf
PI4_BOARD_L = 85.0             # mm, real board length (the old lid derived its size from only
                                  # the 58x49mm mounting-hole rectangle + a flat margin, which
                                  # let the real 85x56mm board overhang it on one side).
PI4_BOARD_W = 56.0             # mm, real board width.
PI4_BOARD_CORNER_R = 3.0       # mm, official board corner radius (drawing callout "CORNER
                                  # RADIUS = 3.0mm").
PI4_CONNECTOR_HEIGHT = 17.0    # mm, tallest connector cluster (stacked USB2/USB3 sockets,
                                  # the drawing's own "Z=16.0" callout) above the board's top
                                  # surface, +1mm rounding for real-world fit margin.
PI4_STANDOFF_HEIGHT = 8.0      # mm, design choice -- M2.5 standoffs lifting the board off the
                                  # deck, clearing the underside micro-SD card + PMIC components.
PI4_LID_CLEARANCE = 5.0        # mm, design choice -- side clearance around the real 85x56mm
                                  # board outline (the old lid used a 20mm margin around the
                                  # much-smaller mounting-hole rectangle instead, which is what
                                  # let the real board overhang it).

# Adafruit PCA9685 16-channel PWM/servo driver (product 815) -- real board, commonly documented
# footprint (Adafruit product page / reseller listings): ~62.5 x 25.4mm, ~3mm PCB thickness.
PCA9685_L = 62.5               # mm
PCA9685_W = 25.4               # mm
PCA9685_H = 3.0                 # mm, bare PCB thickness.
PCA9685_CONNECTOR_H = 10.0     # mm, ASSUMPTION -- clearance for the terminal-block/header pins
                                  # + servo cable bundle standing proud of the board, Adafruit's
                                  # page does not spec an installed height.
PI4_LID_BOARD_GAP = 6.0        # mm, design choice -- clear gap between the Pi4 and PCA9685
                                  # footprints inside the shared avionics cover.

# ---- Item 3: Hip abduction shims ------------------------------------------------------------
# Printed PETG wedge shims filling the gap left by HIP_ABDUCTION_DEG's static tilt (see
# assemble_robot.py's own documented limitation) -- design choice, no vendor spec applies to a
# custom printed shim.
HIP_SHIM_THICKNESS = 20.0      # mm, design choice -- comfortably taller than the max gap the
                                  # 10-degree tilt opens up under the bracket's high corner
                                  # (HIP_Y_LENGTH * sin(10deg) ~= 13.9mm), then trimmed flush
                                  # by the deck-top boolean cut in assemble_robot.py.

# ---- Item 6: Real M3 hex standoffs -----------------------------------------------------------
# Standard M3 hex standoff hardware (widely sold, e.g. Vital Parts HMM-M3-*-S55) -- 5.5mm
# across-flats is the industry-standard M3 hex standoff size.
STANDOFF_HEX_ACROSS_FLATS = 5.5   # mm, cited -- standard M3 hex standoff, see above.

# ---- Item 7: LiDAR pedestal top plate, real A1M8 outline -------------------------------------
# RPLIDAR A1M8 official headline spec (Slamtec datasheet + product page): 96.8 x 70.3 x 55mm,
# D-shaped/rounded housing footprint -- approximated here as a 70.3mm-diameter circle unioned
# with a rectangle extending the long axis out to the full 96.8mm length (same
# circle+rectangle "stadium" approximation build_skid_plate.py-style parts already use for
# non-rectangular real footprints elsewhere in this project).
LIDAR_PLATE_LENGTH = 96.8      # mm, cited, real A1M8 long dimension.
LIDAR_PLATE_WIDTH = 70.3       # mm, cited, real A1M8 short dimension / circle diameter.

# ---- Item 8: Hollow hip housing + cap, internal servo web ------------------------------------
HIP_HOUSING_FLOOR_T = 4.0      # mm, design choice, matches WALL elsewhere.
HIP_HOUSING_WALL_T = 4.0       # mm, design choice, matches WALL elsewhere.
HIP_CAP_THICKNESS = 3.0        # mm, design choice -- separate printed cap, thinner than the
                                  # housing's own structural walls (not load-bearing).
HIP_HOUSING_FILLET_R = 6.0     # mm, design choice -- rounds the 4 vertical outer edges.
HIP_CABLE_SLOT_W = 12.0        # mm, design choice -- inboard-face cable exit slot width.
HIP_CABLE_SLOT_H = 20.0        # mm, design choice -- inboard-face cable exit slot height.
HIP_CAP_SCREW_DIA = 2.5        # mm, M2.5 clearance -- 4 corner screws into the cap's own
                                  # boss posts (small, non-structural cap fastener).
HIP_CAP_BOSS_DIA = 6.0         # mm, design choice -- corner boss outer diameter for the cap screws.
# MG996R flange-to-spline-top height: a web search of the manufacturer/reseller datasheets
# (TowerPro, Handson Technology, components101, servodatabase) found overall body dimensions
# (40.7 x 19.7 x 42.9mm) but no drawing callout for this specific flange-to-spline dimension --
# ASSUMPTION, a typical standard-servo value (the spline boss commonly stands a few mm proud
# of the mounting-tab flange on this servo class).
SERVO_HORN_FLANGE_HEIGHT = 4.0   # mm, ASSUMPTION -- see above.

# ---- Item 5: Box-section body walls/bulkheads -------------------------------------------------
# Layout shared by build_body_walls.py AND both deck scripts (which must cut matching flange
# bolt holes) -- kept here, not recomputed independently in 3 files, so they can't drift apart.
WALL_SIDE_LENGTH = 200.0       # mm, design choice -- same span the old shell panels used
                                  # (PANEL_L), already confirmed clear of both hip footprints'
                                  # X-extent ([119,231]mm each side) by the existing
                                  # interference check.
BULKHEAD_LENGTH = 110.0        # mm, design choice -- comfortably inside the clear Y gap
                                  # between the left/right hip footprints' Y-extent
                                  # ([65,145]mm each side).
BULKHEAD_X = 100.0             # mm, design choice -- front bulkhead at +BULKHEAD_X (facing
                                  # the front overhang where the camera mast sits), rear
                                  # bulkhead at -BULKHEAD_X (facing the rear overhang where the
                                  # LiDAR pedestal sits); matches WALL_SIDE_LENGTH/2 so the two
                                  # side walls' own ends line up with the two bulkheads.
WALL_HOLE_INSET = 25.0         # mm, design choice -- flange bolt hole inset from each panel's
                                  # own end.
WALL_THICKNESS = 3.0           # mm, design choice -- 3D-printed PETG wall thickness.
WALL_FLANGE = 10.0             # mm, design choice -- top/bottom flange width carrying the M3
                                  # bolts into the decks.
WALL_BOLT_DIA = 3.4            # mm, M3 clearance, reuses STANDOFF_HOLE_DIA's own value.
WALL_MAX_PRINTABLE_SPAN = 220.0   # mm, design choice -- longest single dimension a wall/
                                     # bulkhead panel may span so it still fits a normal
                                     # 220x220mm printer bed (a common Ender-3/Prusa-class
                                     # bed size, cited as a general commodity-printer spec,
                                     # not one specific vendor's exact number).

# 22mm emergency-stop pushbutton: 22mm panel mounting-hole diameter is the industry-standard
# cutout for this whole product class (Schneider/IDEC/generic 22mm-series E-stops) -- cited.
ESTOP_CUTOUT_DIA = 22.0        # mm, cited, standard 22mm E-stop mounting cutout.

# XT60 panel-mount connector (e.g. AMASS XT60E-M): commonly documented panel cutout footprint.
XT60_CUTOUT_W = 22.0           # mm, cited.
XT60_CUTOUT_H = 18.0           # mm, cited.

# Small panel-mount rocker/toggle power switch (generic KCD1-mini-class switch, a common,
# widely-stocked size for this application) -- cited as a common standard size, not one
# specific vendor's part.
SWITCH_CUTOUT_W = 19.2         # mm, cited, common KCD1-mini rocker-switch cutout width.
SWITCH_CUTOUT_H = 13.0         # mm, cited, common KCD1-mini rocker-switch cutout height.

VENT_SLOT_W = 3.0              # mm, design choice, front-bulkhead vent slot width.
VENT_SLOT_L = 30.0             # mm, design choice, front-bulkhead vent slot length.
VENT_SLOT_PITCH = 8.0          # mm, design choice, spacing between vent slots.

# ---- Item 4 (deck cleanup, cont'd): fillets, cable pass-throughs, lightening cuts -----------
DECK_CORNER_FILLET_R = 15.0       # mm, design choice, outer-corner rounding on both decks.
HIP_NOTCH_FILLET_R = 8.0          # mm, design choice, inner-corner rounding on the hip
                                     # clearance pockets (stress-riser reduction on a laser-cut
                                     # sheet's inside corners -- standard sheet-metal practice).
CABLE_PASSTHRU_W = 40.0           # mm, design choice, top-deck inter-deck cable pass-through
                                     # slot width.
CABLE_PASSTHRU_L = 12.0           # mm, design choice, slot length.
LIGHTENING_HOLE_DIA = 20.0        # mm, design choice, top-deck-only lightening cut-out
                                     # diameter (bottom deck keeps a solid ground-facing face,
                                     # see item 4 in the README).

# ---- Item 9: Payload reference envelopes (build_payload.py) --------------------------------
# GY-521 MPU6050 breakout board -- commonly documented footprint across resellers.
MPU6050_L = 21.0                # mm, cited.
MPU6050_W = 16.0                # mm, cited.
MPU6050_H = 3.0                  # mm, cited, bare PCB thickness (excludes the MPU6050 chip's
                                     # own small package height, negligible for an envelope).
MPU6050_HOLE_DIA = 2.0          # mm, ASSUMPTION -- M2 clearance, typical for this breakout
                                     # board class; no single official spec across resellers
                                     # (many GY-521 boards ship with a single mounting hole,
                                     # modeled here as one hole, not a 4-corner pattern).
IMU_MOUNT_X = 40.0              # mm, design choice -- within 60mm of the body's XY center
                                     # (placement rule, item 9), on the bottom deck, clear of
                                     # the battery bay and its strap slots.
IMU_MOUNT_Y = 40.0              # mm, design choice -- see above.

# UBEC 5V/3A step-down module (e.g. Adafruit product 1385) -- a real, commonly-stocked part,
# but its exact PCB envelope isn't published on the vendor's own product page; sized here to
# the typical small-UBEC envelope reported across several RC-hobby retailers for this product
# class -- ASSUMPTION on the exact envelope, not the part choice itself.
UBEC_L = 25.0                    # mm, ASSUMPTION -- see above.
UBEC_W = 20.0                    # mm, ASSUMPTION -- see above.
UBEC_H = 7.0                     # mm, ASSUMPTION -- see above.

# ---- Mass/torque sanity report (Chassis v2 item 10) -----------------------------------------
# Material densities -- standard published values, cited.
DENSITY_PETG = 1.27e-3           # g/mm^3 (1.27 g/cm^3) -- PETG filament, commonly cited.
DENSITY_AL5052 = 2.68e-3         # g/mm^3 (2.68 g/cm^3) -- 5052 aluminium alloy, standard spec.
DENSITY_UHMW = 0.93e-3           # g/mm^3 (0.93 g/cm^3) -- UHMWPE, standard spec.

# Bought-part masses -- cited where a spec sheet publishes weight, ASSUMPTION otherwise.
MASS_MG996R_G = 55.0             # g, cited, TowerPro MG996R datasheet ("55g").
MASS_SG90_G = 9.0                # g, cited, ubiquitous SG90 spec ("~9g").
MASS_RPLIDAR_A1_G = 190.0        # g, cited, Slamtec A1M8 datasheet MISC table ("190g typical").
MASS_PI4_G = 46.0                # g, cited, commonly published Pi 4B board weight (~46g, no
                                    # case/heatsink).
MASS_BATTERY_G = 190.0           # g, ASSUMPTION -- typical 3S 2200mAh "shorty" pack weight
                                    # class (Zeee-style packs of this capacity), vendor page
                                    # for the exact SKU not re-checked in this pass.
MASS_PCA9685_G = 10.0            # g, ASSUMPTION -- small bare PCB + header, typical for this
                                    # board class.
MASS_MPU6050_G = 5.0             # g, ASSUMPTION -- small breakout board, typical for this class.
MASS_UBEC_G = 15.0               # g, ASSUMPTION -- small potted module, typical for this class.
MASS_ESTOP_G = 30.0              # g, ASSUMPTION -- typical 22mm metal-bodied E-stop switch.
MASS_XT60_G = 3.0                # g, ASSUMPTION -- small panel-mount connector.
MASS_SWITCH_G = 5.0              # g, ASSUMPTION -- small rocker switch.
MASS_STANDOFF_G = 2.0            # g, ASSUMPTION -- small M3 hex standoff, brass/steel.

# MG996R rated stall torque -- cited, commonly published spec (e.g. servodatabase.com /
# component101): ~9.4 kgf-cm @ 4.8V, ~11 kgf-cm @ 6V. Using the higher (6V) rating -- the
# more optimistic, not the worst case for the servo -- so a torque check that still fails
# against it is a real finding, not one padded by picking the low-voltage number.
MG996R_STALL_TORQUE_KGF_CM = 11.0   # kgf-cm, cited.
