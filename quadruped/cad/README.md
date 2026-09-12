# Quadruped CAD (FreeCAD Python / `Part` module)

Parametric leg + body parts for the SIH26026 quadruped, built with FreeCAD 1.1's
Python API. Every dimension below is either a real, sourced number or explicitly
flagged as a placeholder/draft -- nothing here is an invented guess.

## Rebuild everything

All scripts import shared constants from `params.py` and must be run from this
directory (`quadruped/cad`) with the confirmed-working FreeCAD install:

```
cd C:\Users\Aadityaa\iqoo\quadruped\cad
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_upper_leg.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_lower_leg.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_hip_bracket.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_bottom_deck.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_top_deck.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" assemble_leg.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" assemble_full_leg.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" assemble_robot.py
```

Run the 5 `build_*.py` scripts first -- `assemble_leg.py`, `assemble_full_leg.py` and
`assemble_robot.py` all read already-exported STEP files rather than rebuilding
geometry themselves. `assemble_full_leg.py` needs `hip_bracket.step`, `upper_leg.step`
and `lower_leg.step`; `assemble_robot.py` needs those three plus `bottom_deck.step` and
`top_deck.step` (it imports `assemble_full_leg.py` directly for its `build_full_leg()`
function, which as a side effect re-runs that script's own report and re-saves
`assembled_full_leg.*`). Each `build_*.py` script prints a bounding box, a volume, and
`Solid valid: True/False`; every script in this directory, including both assembly
scripts, was run for real via `freecadcmd` and confirmed valid solids as of this writing.

## Files

| File | What it is |
|---|---|
| `params.py` | Single source of truth for every shared dimension (CHAMP stock numbers, servo envelope, knee bolt-circle, body-plate/Pi4 constants). |
| `geometry_helpers.py` | Two small cut helpers (`cut_bolt_circle`, `cut_servo_pocket_with_tabs`) factored out once the same pocket/bolt-circle logic appeared in 3+ places (upper leg, lower leg, hip bracket). |
| `build_upper_leg.py` | Upper leg ("femur") link. |
| `build_lower_leg.py` | Lower leg ("tibia") link. |
| `build_hip_bracket.py` | Hip bracket (servo mount + body-plate interface + upper-leg horn interface). |
| `build_bottom_deck.py` | Bottom deck of the two-deck sandwich chassis: hip mounts, standoff holes, battery bay, sensing-bay mount. **DRAFT footprint, see below.** Replaces the old `build_body_plate.py`. |
| `build_top_deck.py` | Top deck: standoff holes, Pi4 mount, camera/thermal mast, LiDAR pedestal. Sits above the bottom deck on 4 standoffs. |
| `assemble_leg.py` | Loads the exported upper/lower leg STEP shapes into one document, positions the lower leg, reports assembled length. Does not touch either deck or the hip bracket. |
| `assemble_full_leg.py` | Extends `assemble_leg.py`: also loads `hip_bracket.step` and mates the upper leg to its horn-face bolt circle, via a reusable `build_full_leg()` function (imported by `assemble_robot.py`). Reports the full hip-to-foot-boss length and re-runs the nominal-height sanity check from the hip attachment point. |
| `assemble_robot.py` | The full robot: both decks (on standoffs) + 4 full legs (via `assemble_full_leg.py`), mirrored/placed at CHAMP's real hip offsets. Reports the whole-robot bounding box and runs a real boolean-geometry interference check. |

Each `build_*.py` also exports `<part>.FCStd` / `.step` / `.stl` into this directory.

## Real dimensions used, and their source

All CHAMP numbers are cited in `docs/champ-research.md` §3.1, itself sourced directly
from `champ_description/urdf/properties.urdf.xacro` in the `chvmp/champ` repo
(`ros2` branch). champ-research.md's numbers are in meters; `params.py` converts to mm.

| Constant (`params.py`) | Value | Source |
|---|---|---|
| `UPPER_LEG_LENGTH` | 190.5mm | champ-research.md §3.1, `upper_leg_z_length = 0.1905` |
| `LOWER_LEG_LENGTH` | 156.0mm | champ-research.md §3.1, `lower_leg_z_length = 0.156` |
| `HIP_X_LENGTH` / `HIP_Y_LENGTH` / `HIP_Z_LENGTH` | 112 / 80 / 130mm | champ-research.md §3.1, `hip_x/y/z_length` |
| `BASE_X_LENGTH` / `BASE_Y_LENGTH` / `BASE_Z_LENGTH` | 500 / 290 / 130mm | champ-research.md §3.1, `base_x/y/z_length` |
| `BASE_TO_HIP_X` / `BASE_TO_HIP_Y` | 175 / 105mm | champ-research.md §3.1, `base_to_hip_x/y` |
| Gait `nominal_height` (used in `assemble_leg.py`'s sanity check, not a params.py constant) | 200mm | champ-research.md §3.1, `champ_config/config/gait/gait.yaml`, `nominal_height: 0.20` |
| `SERVO_BODY_L/W/H`, `SERVO_TAB_SPACING`, `SERVO_TAB_HOLE_DIA` | 40.5 / 20.2 / 38.0mm, 49.5mm, 4.2mm | Standard-size analog/digital hobby servo envelope shared by the MG996R and DS3218 (both drop-in "standard size" servos on the same JR/Futaba mounting-tab spacing) -- a real, widely-used hobby-servo footprint, not CHAMP-specific. |
| `KNEE_HORN_HOLE_DIA` / `KNEE_BOLT_CIRCLE_DIA` | 6.0mm / 30.0mm | Chosen to clear a standard servo spline/horn boss and its 4 mounting screws -- a design choice (not from champ-research.md), reused identically at the knee (upper/lower leg) and the hip (hip bracket's horn face) so the interface is the same standard part everywhere. |
| `PI4_MOUNT_X/Y`, `PI4_HOLE_DIA` | 58 x 49mm, 2.7mm | Real official Raspberry Pi 4 mechanical mounting-hole spec (Raspberry Pi Foundation's Mechanical Drawing for the 4B). Now on the **top deck**. |
| `WALL`, `BRACKET_THICKNESS`, `BODY_PLATE_THICKNESS`, `HIP_MOUNT_INSET`, foot-boss dims | 4.0mm, 8.0mm, 6.0mm, 10.0mm, 18/10mm | Design choices for a 3D-printed PETG part -- not from champ-research.md, called out inline in each script's comments. |
| `BATTERY_L/W/H` | 75 x 34 x 26.5mm | Real off-the-shelf spec: Zeee 3S 2200mAh LiPo "shorty" pack. |
| `LIDAR_DIAMETER`, `LIDAR_HEIGHT` | 97mm (cylinder) x 55mm | RPLIDAR A1 official Slamtec spec is 96.8 x 70.3 x 55mm (D-shaped housing) -- modeled here as a simple ~97mm-dia cylinder, a **documented simplification** of the real housing, not itself a sourced cylindrical spec. |
| `PICAM_PCB_L/W`, `PICAM_HOLE_DIA` | 25 x 24mm, 2.0mm | Real official Raspberry Pi Foundation mechanical spec for the Camera Module (M2 mounting holes). |
| `AMG8833_L/W/H` | 25.6 x 25.3 x 6.0mm | Real spec, Adafruit product 3538 (thermal camera breakout). `AMG8833_HOLE_DIA` (2.0mm) is an assumed M2 clearance -- Adafruit's page doesn't spec an exact hole diameter, a design choice. |
| `STANDOFF_HEIGHT`, `STANDOFF_X/Y`, `STANDOFF_HOLE_DIA` | 50mm, 100/85mm, 3.4mm | Design choices: standoff height clears the 26.5mm battery + wiring slack. `STANDOFF_X` was moved from an original 150mm to 100mm after the interference check (see "Hip/deck interference fix" below) found 150mm fell inside every hip bracket's own 112x80mm footprint -- 100mm falls outside every hip bracket's X-band (119-231mm) by construction. |
| `HIP_CLEARANCE_MARGIN` | 3mm/side | Design choice: fit-tolerance margin around the 112x80mm hip-bracket pass-through pocket cut in the top deck (see "Hip/deck interference fix"). |
| `BATTERY_BAY_POCKET_DEPTH`, strap-slot dims | 2mm, 6 x 20mm | Design choices -- a shallow locating pocket + 2 strap slots, not a sourced battery-mount spec. |
| `SENSING_BAY_L/W`, hole dia/inset | 90 x 60mm, 3.4mm, 10mm | Explicit assumption/placeholder -- the real fan+3xMQ+BME688 sensing-head enclosure has no CAD yet; sized generously pending that design. |
| `MAST_HEIGHT`, `MAST_TILT_DEG`, post/face dims | 50mm, 12 deg, 24/15/5mm | Design choices for the camera/thermal mast -- no sourced spec for the mast itself, only the two devices it carries. |
| `LIDAR_PEDESTAL_HEIGHT`, riser/disc dims, bolt circle | 70mm, 50/100/8mm, 75mm bolt circle, 2.9mm holes | Design choices; the 4-hole/M2.5 count comes from a RobotShop community-forum thread on the RPLIDAR A1's mounting adapter (no official Slamtec bolt-spacing spec was found), the 75mm bolt-circle diameter itself is an **assumption** sized to fit inside the ~97mm LiDAR base. |

## Two-deck chassis: why, and exact placement

The single flat body plate had no room for the battery + LiDAR + camera/thermal payload
the SIH26026 problem statement requires, once you actually lay all of it out on one
500x290mm plate alongside 4 hip mounts and a Pi4. The fix is the standard one real hobby
quadrupeds (SpotMicroAI, Mini Pupper) use for exactly this problem: split the single
plate into two decks on standoffs, so the payload spreads across two layers of usable
area instead of fighting for space on one.

- **Battery: bottom deck, dead center.** The heaviest single part (a 2200mAh 3S pack)
  sits as low and as close to the robot's geometric center as possible -- this directly
  minimizes the height and offset of the overall center of gravity, which matters more
  for a walking quadruped's stability than for a wheeled robot.
- **Sensing bay: bottom deck, front edge, underside-facing.** The narcotics-sniffing
  fan+sensor head needs to (a) sample air near the ground/under vehicles it's inspecting
  and (b) sit near the front where the robot approaches a target -- underside-facing at
  the front puts its intake close to whatever the robot is walking up to and under.
- **LiDAR: top deck, rear-center, elevated on its own pedestal.** A 2D LiDAR needs an
  unobstructed 360-degree horizontal scan plane -- rear-center keeps it away from the
  front-mounted mast, and raising it 70mm (vs. the mast's 50mm) means nothing else on the
  robot pokes up into its scan plane. This LiDAR is also this robot's primary
  obstacle-avoidance sensor (see below).
- **Camera + thermal: top deck, front edge, angled mast.** Facial recognition needs the
  camera roughly at a person's face height and pointed forward, not straight up -- the
  mast tilts both sensors 12 degrees forward-and-down so they look at what the robot is
  approaching, not the ceiling.
- **Standoffs (50mm) tie the two decks together** near the 4 hip-mount corners (inset
  toward center to clear the hip bolt circles), so the top deck's weight (Pi4 + mast +
  LiDAR) still loads down through the same structural corners the legs bolt to.

**Sensor swap, already decided:** the original brief's ultrasonic obstacle sensors are
replaced by the RPLIDAR A1 (2D LiDAR) -- a single LiDAR gives full 360-degree coverage
for obstacle avoidance where multiple point-sensor ultrasonics would need several units
aimed in different directions, and CHAMP's own `champ_navigation` package (see
`docs/champ-research.md` #2) is built around a real 2D-scan-based Nav2/SLAM stack, so a
LiDAR is also the natural sensor for that software path -- this is a final user decision,
not open for reconsideration here.

## What's built vs. still needed

**Built and validated (real solid, exported FCStd/STEP/STL):**
- Upper leg link, with hip-end servo pocket + tab holes and a knee-end bolt circle.
- Lower leg link, with a top-end bolt circle that mates 1:1 with the upper leg's knee
  bolt circle, and a bottom-end foot-tip boss.
- Hip bracket: servo pocket + tab holes and 4 vertical plate-mounting bolts on the
  bottom face, servo-horn bolt circle on the front face (where the upper leg attaches).
- Bottom deck (**draft footprint**, see below): 4 hip-mounting bolt patterns at the real
  CHAMP hip offsets, 4 standoff holes, a battery bay (locating pocket + strap slots)
  centered at the origin, and a placeholder narcotics-sensing-bay mount at the front edge.
- Top deck: matching 4 standoff holes, the Raspberry Pi 4 mounting pattern (moved here
  from the old body plate), a front-edge camera/thermal mast tilted 12 degrees
  forward-and-down, and a rear-center LiDAR pedestal raised 70mm with a 4-hole bolt
  pattern.
- One assembled leg (upper + lower, positioned via `assemble_leg.py`) -- see finding below.
- One full leg, hip-to-foot (hip bracket + upper + lower, via `assemble_full_leg.py`) --
  see "Assembly finding" below.
- The full robot: both decks + all 4 full legs, mirrored/placed at CHAMP's real hip
  offsets (via `assemble_robot.py`) -- see "Full assembly" below. **This is now both
  structurally complete AND interference-free**, confirmed by a real boolean-geometry
  check (see "Hip/deck interference fix" below for the clash that was found and fixed).

**Still needed / explicitly not done here:**
- The rubber foot cap itself is a **bought part** -- not modeled. `build_lower_leg.py`
  only models the 18mm-dia x 10mm boss it presses onto.
- **The deck's overall 500x290mm footprint is still a DRAFT / starting point only.** The
  two-deck split gives the payload room, but the footprint itself has NOT been physically
  test-fit. Unlike the leg and hip parts (fixed by servo geometry + CHAMP's own hip
  offsets, no review needed), **review and approve final chassis sizing before treating
  either deck as final.**
- The narcotics-sensing-bay mount is an explicit **assumption/placeholder** (90x60mm,
  4 corner holes) -- the real fan+3xMQ+BME688 assembly has no CAD of its own yet.
- The RPLIDAR A1 bolt-circle spacing (75mm) on the top deck's pedestal is an
  **assumption** -- no exact official Slamtec mounting-hole-spacing spec was found (only
  a community-forum reference to 4x M2.5 screws, which informed hole count/diameter, not
  spacing).
- No servo-horn-to-3D-print adapter clearances have been physically test-fitted anywhere
  in this model -- `KNEE_HORN_HOLE_DIA`/`KNEE_BOLT_CIRCLE_DIA` and the servo pocket
  dimensions are sized from spec sheets, not from a printed-and-measured test part.
- `assemble_leg.py` only assembles the upper+lower leg pair; it does not attach the hip
  bracket or place all 4 legs on either deck, and it does no inverse kinematics. (This is
  no longer the last word -- `assemble_full_leg.py` and `assemble_robot.py` now cover
  the hip bracket and all 4 legs; see "Full assembly" below. Neither does any kinematics.)
- **(Fixed -- see "Hip/deck interference fix" below.)** The hip bracket's own 130mm
  height (`HIP_Z_LENGTH`, CHAMP's own stock number) doesn't fit inside the original 56mm
  bottom-to-top deck gap, so every leg's hip bracket physically passed through the top
  deck plate, and the standoff posts (un-modeled hardware) passed through the hip
  bracket's own block -- a real, confirmed interference (not a guess), found by
  `assemble_robot.py`. This was not caught earlier because `build_hip_bracket.py`,
  `build_bottom_deck.py`, and `build_top_deck.py` were each validated in isolation --
  none of the individual part scripts places a hip bracket between the two decks, so
  this only became visible once all the pieces were actually assembled together. Both
  the top-deck clash and the standoff clash are now resolved; re-running
  `assemble_robot.py` confirms zero overlapping material anywhere in the assembly.

## Assembly finding (leg length vs. CHAMP stance height)

`assemble_leg.py` positions the lower leg so its knee end sits flush against the upper
leg's knee end (translate only, no rotation -- both links share the same local-Z-axis
convention). Result: structural leg length (upper + lower, excluding the foot boss) =
**346.5mm**, matching `190.5 + 156 = 346.5mm` exactly.

Compared against CHAMP's own `gait.yaml` `nominal_height: 0.20` (200mm stance height,
champ-research.md §3.1): 200mm is **58%** of this leg's full 346.5mm extension. That
ratio is a normal bent-knee stance fraction for legged robots (most quadrupeds stand at
roughly 50-70% of max leg reach, not near-fully-extended) -- **plausible as modeled, no
bent/angled hip offset needed** just to make a 200mm stance height geometrically
reachable. This is a length/ratio sanity check only, not a solved inverse-kinematics
result.

`assemble_full_leg.py` re-runs the same sanity check from the actual hip joint (the hip
bracket's horn bolt-circle center) instead of the raw upper-leg top, now also including
the foot boss: full hip-to-foot-boss length = **337.5mm** (346.5mm raw upper+lower sum,
-19mm because the hip joint sits inside the upper leg's hip-end pocket rather than at
its physical top, +10mm for the foot boss). 200mm is **59%** of 337.5mm -- same
plausible-bent-knee-stance finding as above, materially unchanged by using the real hip
joint as the reference point instead of the raw leg top.

## Full assembly (`assemble_full_leg.py` + `assemble_robot.py`)

### Hip-to-upper-leg mate

`build_hip_bracket.py`'s horn-face bolt circle (where the leg attaches, local
`X=HIP_X/2, Y=HIP_Y, Z=HIP_Z-30`) and `build_upper_leg.py`'s hip-end servo pocket (a
box, not a bolt circle -- that end holds the servo body, not its horn) don't share an
identical hole pattern the way the knee joint's two bolt circles do, so there's no
inset-symmetry trick to lean on. `assemble_full_leg.py` instead aligns the CENTER of the
upper leg's hip-end pocket to the hip bracket's horn bolt-circle center -- the pocket's
own natural stand-in for "where the hip servo roughly sits," since neither script models
an explicit shaft/horn hole inside that pocket. Both parts already share the same X
(width) / Y (bore axis) / Z (length or height) convention, so -- exactly like the knee
mate -- translation only, no rotation, is needed.

### Left/right mirroring

A leg built by `build_full_leg()` always extends outward in the hip bracket's local +Y
direction (that's the one face its horn bolt circle is cut on). CHAMP's own axis
convention (docs/champ-research.md §5's manual actuator-offset convention, "+y to the
left, -y to the right", confirmed by §3.1's Mini Pupper right-front leg offsets all being
negative-Y) means:
- **Left legs (lf, lh): no mirror** -- local +Y is already the correct direction (left).
- **Right legs (rf, rh): mirrored across the XZ plane** (Y negated via an `App.Matrix`
  scale + `transformShape`, applied to the whole hip+upper+lower unit so the hip-to-knee
  mate carries through unchanged) so local +Y becomes global -Y (right).

**No front/hind mirror is applied.** Two independent reasons agree on this: (1) CHAMP's
`gait.yaml` `knee_orientation` is a single uniform value, `">>"` (docs/champ-research.md
§3.1) -- the stock robot's front and hind knees fold the same rotational sense, not
mirrored fore-aft like a horse's legs; (2) this project's own leg model has no built-in
front/back asymmetry to correct for in the first place -- `build_upper_leg.py` /
`build_lower_leg.py` are straight vertical bars, not pre-bent links. Front vs. hind
placement is therefore a plain `+-BASE_TO_HIP_X` translation, no mirror.

### Whole-robot bounding box

**500.0 x 316.0 x 367.5mm** (X x Y x Z), X range -250 to 250mm, Y range -158 to 158mm, Z
range -231.5 to 136mm. The 500x316mm footprint is barely wider (in Y) than the decks'
own 500x290mm plate -- the legs' 8mm hip-end pocket protrudes slightly past the hip
bracket's own 80mm depth, adding 26mm total (13mm/side) beyond the plate edge. The
367.5mm overall height runs from the foot bosses (lowest point, standing leg fully
extended, no bend applied -- this is a static assembly, not a posed stance) up to the
tallest hip bracket corner at Z=136mm, which is even taller than the top deck's own
LiDAR pedestal (Z=132mm) -- see interference finding below for why that number matters.

### Interference check -- now clean

`assemble_robot.py` runs real boolean-geometry checks (`Part.Shape.common()` shared
volume, not bounding-box guessing) between every pair of legs, every leg vs. each deck,
and a probe cylinder at each standoff hole position (standing in for the un-modeled
standoff hardware) vs. every leg.

**Original finding (now fixed, kept here for the record):**
- **Leg vs. leg: clear.** All 4 hip-bracket-and-leg footprints have wide clearance from
  each other (the closest gap, between left/right legs at the same front/hind station,
  is 130mm) -- expected, since `BASE_TO_HIP_X/Y` and `HIP_X/Y_LENGTH` are both real CHAMP
  numbers sized not to overlap.
- **Leg vs. bottom deck: clear** at all 4 corners -- confirms the hip bracket's bottom
  face sits flush on the deck's top surface with no interpenetration.
- **Leg vs. top deck: CLASH, all 4 corners, 53,373mm^3 each.** The hip bracket
  (`HIP_Z_LENGTH` = 130mm tall, standing in Z=[6, 136]) is taller than the original 56mm
  gap between the two decks (`BODY_PLATE_THICKNESS` + `STANDOFF_HEIGHT`), so it
  physically passed straight through the top deck plate (Z=[56, 62]) at all 4 hip
  corners.
- **Standoff posts vs. hip brackets: CLASH, all 4, 420mm^3 each.** `params.py`'s original
  comment on `STANDOFF_X/Y` said the standoffs were inset from the hip corners "clear of
  the hip bolt circles" -- true of the small 4-bolt pattern, but **not** of the hip
  bracket's full 112x80mm block footprint, which the original standoff XY position
  (150, 85mm) fell inside of.
- **Net result at the time:** sum of individual part volumes minus the volume of their
  union = 213,492mm^3 (= 4 x 53,373mm^3, exactly the leg-vs-top-deck figure -- the
  standoff clash was a subset of that same overlapping material, not additional volume),
  confirming the leg-vs-top-deck interference was the only real clash in the assembly.

**The fix chosen, and why:** three options existed -- (a) a taller `STANDOFF_HEIGHT`
(needs a >130mm total deck gap, i.e. `STANDOFF_HEIGHT` >= 124mm, roughly 2.5x the
original value), (b) a clearance pocket cut through the top deck at each hip position, or
(c) shortening the hip bracket below CHAMP's real 130mm `HIP_Z_LENGTH`. **(b) was chosen**
because it's the only option that changes neither the robot's overall height nor a
CHAMP-sourced dimension: the PS explicitly requires "underframe inspection of
coaches/wagons" and operation in "tunnels, platforms, and coaches," so a taller robot
(option a) works directly against the one requirement the PS names by name; shortening
the hip bracket (option c) would break the CHAMP-matched dimension that keeps this
physical model and the already-running Gazebo simulation describing the same robot, and
risks the bracket no longer actually housing the real servo it was sized around.

Implemented as two changes:
1. `build_top_deck.py` now cuts a straight rectangular through-pocket at each of the 4
   real hip positions, sized to the hip bracket's 112x80mm footprint plus
   `HIP_CLEARANCE_MARGIN` (3mm/side) for fit tolerance -- the hip bracket's tall body
   passes through this pocket rather than colliding with solid plate.
2. `params.py`'s `STANDOFF_X` moved from 150mm to 100mm, so it falls outside every hip
   bracket's X-band (`BASE_TO_HIP_X +- HIP_X_LENGTH/2` = 119 to 231mm on each side) by
   construction -- any `|STANDOFF_X| < 119` clears all 4 hip footprints regardless of Y,
   so `STANDOFF_Y` (85mm) is unchanged.

**Re-running `assemble_robot.py` after the fix confirms zero overlapping material
anywhere**: sum of individual part volumes equals the volume of their union exactly, and
every leg-vs-leg, leg-vs-deck, and standoff-vs-leg check reports `clear (0 mm^3)`.

## Is this a complete CAD model?

**Structurally: yes, every part exists and every part is placed** -- upper leg, lower
leg, hip bracket, bottom deck, top deck, and now a full hip-to-foot leg assembly and all
4 legs mirrored/placed on the two-deck chassis at CHAMP's real hip offsets. Every part
and every assembly script in this directory was run for real via `freecadcmd` and
produces valid solids.

**It is also now a physically consistent, interference-free model.** The
`assemble_robot.py` interference check originally found a real, confirmed clash (hip
bracket height vs. deck spacing) that no prior single-part validation could have caught
-- that clash has since been fixed (top-deck clearance pockets + a repositioned standoff)
and re-verified at zero overlapping material.

Still outstanding, unchanged by this fix (listed above in "What's built vs. still
needed"): the deck footprint itself is an unreviewed draft, no part has been physically
test-fitted or printed, the foot cap and standoff hardware are bought parts with no CAD
of their own, the narcotics-sensing-bay mount is a placeholder, and no inverse kinematics
or posed/bent-leg stance has been modeled -- this assembly is fully extended (straight
leg), not standing at `nominal_height`. **Treat this as a complete, interference-free
first-pass structural layout -- real dimensions, real fit checks, nothing invented -- but
still short of a physically test-fitted, build-ready design.**
