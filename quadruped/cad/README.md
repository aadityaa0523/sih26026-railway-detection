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
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_skid_plate.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_camera_pan_tilt.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_sniffer_arm.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_body_walls.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" build_payload.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" assemble_leg.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" assemble_full_leg.py
"C:/Users/Aadityaa/AppData/Local/Programs/FreeCAD 1.1/bin/freecadcmd.exe" assemble_robot.py
```

**Chassis v2 note:** `build_shell_panels.py` is SUPERSEDED by `build_body_walls.py` (see
the "Chassis v2" section below) and is no longer part of this rebuild list or called from
`assemble_robot.py` -- left in the directory, not deleted, for history.

Run the 11 `build_*.py` scripts first -- `assemble_leg.py`, `assemble_full_leg.py` and
`assemble_robot.py` all read already-exported STEP files rather than rebuilding
geometry themselves. `assemble_full_leg.py` needs `hip_bracket.step`,
`hip_bracket_cap.step`, `upper_leg.step` and `lower_leg.step`; `assemble_robot.py` needs
those four plus `bottom_deck.step`, `top_deck.step`, `skid_plate.step`,
`pan_tilt_head.step`, `sniffer_arm.step`, `body_walls.step` and `payload.step` (it
imports `assemble_full_leg.py` directly for its `build_full_leg()` function, which as a
side effect re-runs that script's own report and re-saves `assembled_full_leg.*`). Each
`build_*.py` script prints a bounding box, a volume, and `Solid valid: True/False`;
every script in this directory, including both assembly scripts, was run for real via
`freecadcmd` and confirmed valid solids as of this writing. **Note:** `freecadcmd` sets
each script's own `__name__` to its module name, not `"__main__"` -- no script in this
directory uses an `if __name__ == "__main__":` guard for its top-level build/export code,
by design (an early version of `build_camera_pan_tilt.py` used one and its body silently
never ran; keep this in mind if adding new scripts).

## Files

| File | What it is |
|---|---|
| `params.py` | Single source of truth for every shared dimension (CHAMP stock numbers, servo envelope, knee bolt-circle, body-plate/Pi4 constants, and all 8 improvement constants below). |
| `geometry_helpers.py` | Shared cut/build helpers factored out once the same logic appeared in 3+ places: `cut_bolt_circle`, `cut_servo_pocket_with_tabs` (upper leg, lower leg, hip bracket), `build_sg90_mount_block` (pan-tilt head, sniffer arm), `build_deck_ribs` + `_rects_overlap` (both decks' stiffening ribs, improvement 6). |
| `build_upper_leg.py` | Upper leg ("femur") link. Now also carries a cable routing channel (improvement 7). |
| `build_lower_leg.py` | Lower leg ("tibia") link. Foot boss now widened/deepened for the compliant-foot spring+cap stack (improvement 3); also carries a cable routing channel (improvement 7). |
| `build_hip_bracket.py` | Hip bracket. **Chassis v2 item 8**: now a real hollow housing (4mm floor+walls, R6 outer fillets) with a separate 3mm cap and a real internal servo mounting web, instead of a solid block. Outer envelope + horn-face bolt circle UNCHANGED (hard constraint). The hip-abduction tilt (improvement 1) is still applied at assembly time in `assemble_robot.py`. |
| `build_bottom_deck.py` | Bottom deck of the two-deck sandwich chassis: hip mounts, standoff holes, battery bay (strap slots only now), sensing-bay mount, IMU mount, body-wall flange holes. **DRAFT footprint, see below.** **Chassis v2 item 4**: now a 3mm laser-cut sheet (Al5052/acrylic), through-features only, no ribs (superseded), outer corners filleted. |
| `build_top_deck.py` | Top deck: standoff holes, Pi4 mount, camera/thermal mast, LiDAR pedestal, body-wall flange holes. Sits above the bottom deck on 4 real M3 hex standoffs (item 6). **Chassis v2**: `MAST_HEIGHT` cut 50mm->8mm (item 1, LiDAR occlusion fix), LiDAR pedestal top plate rebuilt to the real A1M8 D-shape outline (item 7, old notched 100mm disc removed), avionics cover rebuilt from the real Pi4 85x56mm board outline + PCA9685 clearance with connector-side openings (item 2), cable pass-throughs + top-deck-only lightening cuts added, corners/hip-pockets filleted, ribs removed (superseded). |
| `build_skid_plate.py` | UHMW/HDPE ground-contact skid plate under the bottom deck's clear central gap. Unchanged by Chassis v2. |
| `build_camera_pan_tilt.py` | 2x SG90 pan-tilt camera/thermal head that bolts to the top-deck mast's mounting plate. Unchanged internals (hard constraint) -- only where it mounts moved (lower `MAST_HEIGHT`, item 1). |
| `build_sniffer_arm.py` | 2x SG90 dip+swing narcotics-sensing arm. Unchanged by Chassis v2. |
| `build_shell_panels.py` | **SUPERSEDED by `build_body_walls.py`** (Chassis v2 item 5) -- left in place for history, no longer called. |
| `build_body_walls.py` | **New (Chassis v2 item 5).** Box-section structural walls (2 side walls + front/rear bulkheads) closing the inter-deck bay, replacing the cosmetic shell panels. Rear bulkhead carries E-stop/XT60/switch cutouts; front bulkhead carries vent slots. |
| `build_payload.py` | **New (Chassis v2 item 9).** Reference envelope solids for every bought electronic part (battery, Pi4, PCA9685, RPLiDAR A1, IMU, UBEC, E-stop, XT60, switch), exported separately as `payload.step`, included in `assemble_robot.py`'s interference check. |
| `check_mechanics.py` | Motion check (run after `assemble_robot.py`): joint inventory vs CHAMP's 3 joints/leg, IK gait sweep of the LF leg through CHAMP's gait envelope with real boolean collision checks, hip ab/ad sweep, mass/CG/torque/ground clearance. See "Mechanics check" below. |
| `render_views.py` | **New (Chassis v2 item 11).** FreeCAD GUI macro (run with `freecad.exe`, not `freecadcmd`) producing the PNG renders in `renders/`. |
| `assemble_leg.py` | Loads the exported upper/lower leg STEP shapes into one document, positions the lower leg, reports assembled length. Does not touch either deck or the hip bracket. |
| `assemble_full_leg.py` | Extends `assemble_leg.py`: also loads `hip_bracket.step` (+ **Chassis v2**: `hip_bracket_cap.step`) and mates the upper leg to its horn-face bolt circle, via a reusable `build_full_leg()` function (imported by `assemble_robot.py`). Reports the full hip-to-foot-boss length and re-runs the nominal-height sanity check. Also builds the 2 dust bellows via `build_bellows()`. |
| `assemble_robot.py` | The full robot. **Chassis v2**: real M3 hex standoffs (item 6) replace the old probe cylinders; hip-abduction wedge shims (item 3) fill the tilt gap; body walls (item 5) replace shell panels; payload envelopes (item 9) are loaded and interference-checked; a new LiDAR scan-plane occlusion check (item 1) and a mass/torque sanity report (item 10) are printed. Reports the whole-robot bounding box and runs a real boolean-geometry interference check across every part. |

Each `build_*.py` also exports `<part>.FCStd` / `.step` / `.stl` into this directory.
`build_camera_pan_tilt.py` and `build_sniffer_arm.py` each export TWO sets (neutral pose
and `..._extended`) for their two demonstration poses.

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

**Added for the 8 real-quadruped-precedent improvements** (see the dedicated section below for the why/precedent of each; this table only covers the numbers):

| Constant (`params.py`) | Value | Source |
|---|---|---|
| `HIP_ABDUCTION_DEG` | 10 deg | Design choice (improvement 1) -- modest, real quadrupeds' ab/ad range is typically small. NOT a sourced number. |
| `HIP_ABDUCTION_CLEARANCE_EXTRA` | 12mm | Design choice, then CONFIRMED by re-running `assemble_robot.py`'s real interference check (see "Full assembly" below) -- widens the top deck's existing hip-clearance pocket for the new tilt. |
| `LIDAR_DISC_HIP_NOTCH_W` / `_D` | 80 / 25mm | Design choice, sized (with margin) to a SECOND real clash the same interference check found and a diagnostic isolated exactly (hind hip bracket vs. LiDAR top disc, see "Full assembly" below) -- not guessed. |
| `BELLOWS_ID` / `_OD` / `_LENGTH` | 34 / 42 / 30mm | Design choices (improvement 2) -- a simple cylindrical boot (the brief's own "fine CAD approximation"), sized to clear the 28.2x8mm leg bar's ~29.3mm diagonal. Represents a BOUGHT/MOLDED rubber part, not 3D-printed. |
| `TOPDECK_LID_WALL` / `_MARGIN` / `_HEIGHT` | 2 / 20 / 20mm | Design choices (improvement 2) -- geometric enclosure only, no gasket/seal modeled (no real IP rating). |
| `SPRING_BORE_DIA` / `_DEPTH` | 12 / 8mm | Design choice (improvement 3) -- "generic small compression spring, ~10mm dia range, exact spec TBD at purchase," same documented-assumption level as the rubber foot cap. Foot boss itself widened 18->22mm dia, deepened 10->16mm (local constants in `build_lower_leg.py`) to fit the stack. |
| `SG90_BODY_L/W/H`, `SG90_TAB_SPACING`, `SG90_TAB_HOLE_DIA` | 22.2 / 11.8 / 31.0mm, 28.0mm, 2.0mm | Real, standard, ubiquitous micro-servo spec (Tower Pro SG90 / generic clones) -- cited the same confidence level as the leg servos' own envelope, no further sourcing needed for this extremely common part. |
| `PANTILT_BASE_W/D/T`, `_LINK_LENGTH`, `_PAN_RANGE_DEG`, `_TILT_RANGE_DEG` | 36/36/8mm, 30mm, 45 deg, 30 deg | Design choices (improvement 4) -- bracket/link sizing and demonstration-pose angles for the pan-tilt head; NOT a fully kinematic mechanism, see the dedicated section below. |
| `SNIFFER_BASE_T`, `_LINK_LENGTH`, `_DIP_RANGE_DEG`, `_SWING_RANGE_DEG` | 8mm, 50mm, 60 deg, 30 deg | Design choices (improvement 4) -- the sniffer arm's own base footprint REUSES `SENSING_BAY_L/W` directly (so it lines up with holes the bottom deck already cuts) rather than a new size. |
| `SKID_PLATE_THICKNESS`, `_L`, `_W`, `_HOLE_DIA` | 3mm, 80 x 100mm, 3.4mm | Material is a design choice but a real, appropriate one: UHMW or HDPE, standard for RC-crawler/rover ground-contact skid plates. Footprint size+position confirmed (not guessed) by `build_skid_plate.py`'s own real geometric clearance check against the hip mounts/battery bay/sensing-bay mount. |
| `RIB_WIDTH`, `RIB_HEIGHT` | 3 x 10mm | Design choices (improvement 6) -- standard lightweighting/stiffening technique, no FEA run. Rib POSITIONS are computed+verified by `geometry_helpers.build_deck_ribs`'s own real overlap check against every existing hole/pocket/mount, not guessed (see "Full assembly" below for how many actually survived on each deck). |
| `BODY_PLATE_THICKNESS` | 4mm (was 6mm) | Design choice (improvement 6) -- reduced now that both decks gained stiffening ribs instead of relying on a thicker solid slab. |
| `CABLE_CHANNEL_WIDTH` / `_DEPTH` / `_END_MARGIN` | 5 / 2 / 25mm | Design choices (improvement 7) -- sized for a typical 3-4 servo signal wire bundle; end margins computed per-script from the real knee/hip-pocket geometry they must clear, not a blind flat number everywhere. |
| `SHELL_PANEL_THICKNESS`, `DECAL_W/H` | 2mm, 80 x 40mm | Design choices (improvement 8, cosmetic) -- thin, non-structural cover panels; the decal area is just a flat region on each panel, no extra geometry needed. |

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

## 8 real-quadruped-precedent improvements

After the first interference-free structural pass (legs, hip brackets, two-deck chassis,
full 4-leg assembly -- see "Full assembly" below), 8 further improvements were made, each
addressing a real weakness in that first pass and each modeled on a technique real deployed
quadrupeds (Boston Dynamics Spot, ANYmal, Unitree) actually use -- not invented. Implemented
in this order (each is a prerequisite for treating the later, more speculative ones safely):

**1. Hip abduction/adduction angle.** Real quadrupeds gain sprawl-stability without giving
up a mammalian trot gait via a hip ab/ad joint. CHAMP's stock config has none, so this is a
STATIC 10-degree outward mounting tilt of each whole hip-bracket-and-leg unit (a design
choice, not sourced -- "modest," matching real quadrupeds' typically small ab/ad range),
applied purely in `assemble_robot.py`'s leg-placement logic, NOT a new powered joint --
stated honestly, not overclaimed. **This is the one improvement that actually broke the
existing interference-free assembly** -- see "Full assembly" below for both real clashes it
introduced and how each was found and fixed (this is exactly the outcome the task predicted
and asked to be checked for, not assumed away).

**2. Dust bellows/gaiters + top-deck lid.** *(Lid geometry SUPERSEDED by Chassis v2 item 2 --
see the "Chassis v2" section below; the bellows are unchanged.)* Addresses a weakness the PS's own "tunnels,
platforms, coaches" operating environment implies: the knee and hip joints, and the
Pi4/wiring bay, were fully exposed. Bellows are simple cylindrical boots (the brief's own
"fine CAD approximation" of a real molded rubber/silicone part) bridging the knee-joint gap
and the hip-joint gap -- a BOUGHT or MOLDED part, not 3D-printed, same convention as the
existing foot-cap note. The top-deck lid is a GEOMETRIC ENCLOSURE ONLY -- no gasket/seal
modeled, so no real IP rating is achieved, stated directly rather than implied.

**3. Compliant foot.** Addresses a real robotics weakness: a rigid foot boss transmits every
footfall impact straight into the leg and hip servos. Real deployed quadrupeds use
compliant/sprung feet. Here: the same rigid boss, widened/deepened, PLUS a generic small
bought compression spring in a blind bore (no precise spec invented -- "generic small
compression spring, ~10mm dia range, exact spec TBD at purchase," matching how the rubber
foot cap was already handled), PLUS the same bought rubber foot cap on top.

**4. Pan-tilt camera/thermal mount + 2-DOF sniffer arm (2x SG90 each).** This is the
project's key differentiator, addressing the single weakness named earliest in this
project's own conversation: the original mounts were STATIC -- the camera/thermal package
only ever pointed one fixed direction, and the narcotics-sensing head could only sample
wherever the robot's BODY happened to be, not aim itself. Both new mechanisms use 2x SG90
micro servos (real, ubiquitous, well-documented spec -- ~22.2x11.8x31mm, ~9g, the
industry-standard micro servo, cited with the same confidence as the leg servos' own
envelope) -- much smaller/lighter than the leg's MG996R/DS3218, appropriate for these
low-torque jobs. **NOT a fully kinematic mechanism**, an honest simplification the brief
explicitly allows: simplified servo-pocket recesses (real SG90 shaft/spline geometry isn't
modeled) and two static poses -- NEUTRAL and EXTENDED (`build_camera_pan_tilt.py`,
`build_sniffer_arm.py` each export both) -- demonstrate the range of motion instead of a
simulated continuous mechanism. `assemble_robot.py` places the NEUTRAL pose of each into the
whole-robot model and interference-checks it there; the EXTENDED pose is a standalone
demonstration only, not itself checked against the rest of the chassis.

**5. Skid plate.** Addresses underframe-inspection duty cycle wear the PS implies (crawling
under coaches/wagons, over rail-yard ballast) that the original design had no answer for.
UHMW or HDPE -- a design choice, but a real, appropriate one: standard low-friction,
high-wear-resistance materials for exactly this ground-contact application on RC
crawlers/rovers. Placement (the clear XY gap between the battery bay and the sensing-bay
mount) was found and CONFIRMED by `build_skid_plate.py`'s own real geometric overlap check
against all 3 named keepouts, not eyeballed.

**6. Ribbed decks.** *(SUPERSEDED by Chassis v2 items 4/5 -- a laser-cut sheet deck can't
carry printed ribs; the box-section body walls now carry the stiffening load instead. Kept
here for history.)* Addresses the same weakness a solid, unribbed flat plate always has:
carrying the Pi4/mast/LiDAR/battery/leg loads on a thin slab either flexes or has to be made
needlessly thick. Standard lightweighting/stiffening technique (thin base plate + a grid of
perpendicular ribs), cited generically -- no FEA was run. Rib positions are computed AND
verified by `geometry_helpers.build_deck_ribs`'s own real overlap check against every
existing hole/pocket/mount on each deck (not assumed clear): the bottom deck (less crowded)
ends up with 4 ribs (2 longitudinal + 2 transverse); the top deck (Pi4 + lid + mast base +
LiDAR pedestal + hip pockets all competing for area) ends up with only 2 (both
longitudinal) -- reported honestly as fewer, not padded out to match.

**7. Cable routing channels.** Addresses a real build-quality gap: 12 servos' worth of
signal wire has nowhere planned to run along the leg links, inviting snagging/chafing
against the knee/hip joints. A shallow groove (design choice, sized for a 3-4 servo wire
bundle) along each leg link's front face, with its own end-clearance computed per script
from the real knee-bolt-circle / hip-pocket geometry it must avoid, not a blind flat margin.

**8. Shell/livery panels (cosmetic, done last).** *(SUPERSEDED by Chassis v2 item 5 --
`build_body_walls.py`'s structural box-section walls replace these cosmetic panels
entirely, keeping the same decal-area requirement. Kept here for history.)* Addresses the "looks like exposed
brackets, not a purpose-built platform" read a bare structural skeleton gives -- relevant
for a robot meant to read as an inspection tool that belongs in a rail environment, not a
hobby project. **PARTIAL IMPLEMENTATION, stated honestly**: only the two flat body-deck side
panels are modeled (each with a flat area sized for an RPF/security branding decal); leg
panels are explicitly SKIPPED -- the brief allows a partial implementation given this is the
lowest-priority, purely cosmetic item, and every structural/mechanical improvement above it
was prioritized and finished first.

**What's still simplified or not physically validated, across all 8:** none of the 8 has
been physically test-fitted or printed (same caveat as the rest of this project); the hip
abduction tilt leaves the deck's own mounting bolt holes straight/vertical (a real build
would want an angled shim or re-drilled holes) and lifts the bracket's bottom face off full
flush contact (a real build would want a shim/spacer there too); the pan-tilt head and
sniffer arm are demonstration poses, not simulated continuous mechanisms; the top-deck lid
and the bellows achieve no real sealing/IP rating; the skid plate and shell panels are not
bolted down with any modeled fastener detail beyond their own through-holes; and the ribbed
decks were sized by a generic rule of thumb, not FEA.

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
  from the old body plate), a front-edge mast (now topped with a PLAIN mounting plate for
  the pan-tilt head, see below, instead of the original tilted camera/thermal face), and a
  rear-center LiDAR pedestal raised 70mm with a 4-hole bolt pattern.
- One assembled leg (upper + lower, positioned via `assemble_leg.py`) -- see finding below.
- One full leg, hip-to-foot (hip bracket + upper + lower + 2 dust bellows, via
  `assemble_full_leg.py`) -- see "Assembly finding" below.
- The full robot: both decks (now ribbed, with a Pi4 lid) + all 4 full legs (now
  hip-abducted) mirrored/placed at CHAMP's real hip offsets, plus the skid plate,
  pan-tilt head, sniffer arm, and shell panels (via `assemble_robot.py`) -- see "Full
  assembly" below. **This is now both structurally complete AND interference-free**,
  confirmed by a real boolean-geometry check (see "Hip/deck interference fix" and "Two
  more real clashes found" below for the clashes that were found and fixed).
- The 8 real-quadruped-precedent improvements themselves (hip abduction, bellows + lid,
  compliant foot, pan-tilt head + sniffer arm, skid plate, ribbed decks, cable channels,
  shell panels) -- see the dedicated section above for what each is, why, and what's
  still simplified.

**Still needed / explicitly not done here:**
- The rubber foot cap itself is a **bought part** -- not modeled, same as before. The
  boss it presses onto (now stacked with a bought spring underneath, see improvement 3
  above) was widened/deepened from 18mm-dia x 10mm to 22mm-dia x 16mm to fit that stack.
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
the foot boss: full hip-to-foot-boss length = **343.5mm** (346.5mm raw upper+lower sum,
-19mm because the hip joint sits inside the upper leg's hip-end pocket rather than at
its physical top, +16mm for the foot boss -- widened from 10mm by improvement 3's
compliant-foot spring+cap stack). 200mm is **58%** of 343.5mm -- same
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

**Before the 8-improvement pass:** 500.0 x 316.0 x 367.5mm (X x Y x Z), Y range -158 to
158mm, Z range -231.5 to 136mm -- barely wider in Y than the decks' own 500x290mm plate
(the legs' 8mm hip-end pocket protrudes slightly past the hip bracket's own 80mm depth).

**After the 8-improvement pass: 500.0 x 402.9 x 415.4mm**, X range -250 to 250mm, Y range
-201.4 to 201.4mm, Z range -223.1 to 192.3mm. Y grew by ~87mm total (the biggest single
change) directly from improvement 1's hip-abduction tilt swinging every leg outward --
exactly the sprawl-stability effect that improvement is meant to produce, so a wider
footprint here is an expected result, not a regression. Z grew by ~48mm at the top from
the pan-tilt head and LiDAR pedestal stacking above the mast, and the bottom moved in
slightly (-223.1mm vs -231.5mm) because the hip-abduction tilt+lift changes exactly how
low the foot bosses reach in this static, fully-extended (no bend) pose. This is still a
static assembly, not a posed stance, and still not standing at `nominal_height`.

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

### Two more real clashes found -- from the hip-abduction tilt (improvement 1)

Adding the hip-abduction static tilt (improvement 1, see the improvements section above)
was explicitly expected to disturb this clean assembly, and it did -- **two** further real
clashes, both found the same way as the original one: run `assemble_robot.py`'s real
boolean-geometry check, then isolate exactly which two solids and which XYZ region overlap
with a small diagnostic script, then fix the real cause, then re-run and confirm zero.

**Clash A -- hind hip brackets vs. the LiDAR pedestal's top mounting disc, 1374mm^3 each
(LH and RH only, not LF/RF).** The tilt swings each hip bracket's own top-inner corner (near
its Z=130mm top, the tallest part of the block) inward by roughly 21mm at that height --
enough to reach into the LiDAR pedestal's 100mm-diameter top disc, which sits close to the
HIND hip mounts by construction (`REAR_X`=-195mm vs. hind hip X=-175mm, only 20mm nominal
separation -- already the minimum inset that keeps the disc's own 100mm diameter from
overhanging the deck's rear edge). Only the hind legs clash because the LiDAR pedestal is
only near the rear; the front hip mounts are ~370mm away from it. The disc can't shrink (it
must stay >= the real ~97mm `LIDAR_DIAMETER` it carries) or move further back (already at
its minimum edge-clearance inset), so `build_top_deck.py` instead cuts two small clearance
notches into the disc's own hip-facing edges (`LIDAR_DISC_HIP_NOTCH_W/D`, params.py), sized
with margin to the actual diagnosed clash region, not guessed.

**Clash B -- pan-tilt head base vs. the mast's own mounting plate, 5425mm^3.** A placement
bug in `assemble_robot.py`, not a design conflict: the pan-tilt head's base was positioned
flush with the BOTTOM of the mast's new mounting plate instead of on TOP of it, so the two
solids fully overlapped across the whole mounting-plate footprint. Fixed by adding
`MAST_FACE_THICKNESS` to the Z offset the head is placed at. Caught by the same
sum-of-volumes-vs-volume-of-union check that flagged everything else -- worth noting since
it shows the interference check catches ordinary assembly mistakes, not just genuinely new
physical conflicts from the abduction tilt.

**Re-running `assemble_robot.py` after both fixes confirms zero overlapping material
anywhere again**: sum of individual part volumes equals the volume of their union exactly
(6,104,242mm^3 both ways), and every leg-vs-leg, leg-vs-deck, standoff-vs-leg, and the new
leg-vs-skid-plate/pan-tilt/sniffer-arm/shell-panel checks all report `clear (0 mm^3)`.

## Is this a complete CAD model?

**Structurally: yes, every part exists and every part is placed** -- upper leg, lower
leg, hip bracket, bottom deck, top deck, a full hip-to-foot leg assembly (now with dust
bellows) and all 4 legs mirrored/placed (now with the hip-abduction static tilt) on the
two-deck chassis at CHAMP's real hip offsets, plus the skid plate, pan-tilt head (neutral
pose), sniffer arm (neutral pose), and shell panels from the 8-improvement pass. Every
part and every assembly script in this directory was run for real via `freecadcmd` and
produces valid solids.

**It is also now a physically consistent, interference-free model.** The
`assemble_robot.py` interference check originally found a real, confirmed clash (hip
bracket height vs. deck spacing) that no prior single-part validation could have caught
-- that clash was fixed (top-deck clearance pockets + a repositioned standoff) and
re-verified at zero overlapping material. Adding the hip-abduction tilt later
re-introduced two more real clashes (a hind-hip-vs-LiDAR-disc conflict and a placement
bug), both found and fixed the same way -- see "Two more real clashes found" above. The
whole robot, including all 8 improvements, is confirmed interference-free again as of
this writing.

Still outstanding, unchanged by these fixes (listed above in "What's built vs. still
needed" and in the 8-improvements section's own "still simplified" summary): the deck
footprint itself is an unreviewed draft, no part has been physically test-fitted or
printed, the foot cap/spring and standoff hardware are bought parts with no CAD of their
own, the narcotics-sensing-bay/sniffer-head interface is still a placeholder, no inverse
kinematics or posed/bent-leg stance has been modeled (this assembly is fully extended,
straight leg, not standing at `nominal_height`), and the pan-tilt head/sniffer arm are
demonstration poses rather than simulated continuous mechanisms. **Treat this as a
complete, interference-free structural-plus-8-improvements layout -- real dimensions,
real fit checks, nothing invented -- but still short of a physically test-fitted,
build-ready design.**

## Chassis v2 (senior-reviewer pass)

A second pass after rendering and visually inspecting the 8-improvement model above found
real defects the render/bbox checks alone hadn't caught (LiDAR occlusion, a Pi4 lid that
didn't fit the real board) plus structural/manufacturability gaps (a 500x290mm deck that
can't be 3D-printed, ribs that can't be laser-cut, no real standoffs, a solid hip-bracket
block, no payload actually modeled). Each item below is done/partial/skipped with why,
its sources, and the check result.

### Work items

1. **LiDAR scan-plane occlusion -- DONE.** The pan-tilt head's neutral pose used to rise
   to global Z=192mm, well inside the RPLIDAR A1's own body height above its pedestal
   (base at Z~130mm, 55mm tall) -- blocking part of its 360-degree scan. The Slamtec A1M8
   datasheet's own mechanical-dimension drawing (Chapter 5) didn't have a legible numeric
   callout for the exact scan-plane height in the text this pass could extract, so per
   this task's own documented fallback it's an ASSUMPTION: a 30-50mm band above the
   LiDAR's own base. Fixed by cutting `MAST_HEIGHT` from 50mm to 8mm (not by raising the
   LiDAR) -- the pan-tilt head's neutral top now sits at ~148mm, ~8mm clear of the band's
   own floor (156mm), and the robot's overall max Z actually **dropped** from 192mm to
   181mm (the LiDAR unit's own top is now the tallest point) -- a net win for the PS's
   under-carriage/tunnel/coach clearance requirement. A new real check in
   `assemble_robot.py` (an annular slab at the assumed scan-band height, `.common()`
   against every other part) confirms zero occlusion -- see the verbatim SUMMARY below.
   The front hip housings do NOT block the camera in this configuration (the mast sits
   further forward in +X than the hips, so they're behind the camera's forward view, not
   in front of it) -- reported for completeness, not a problem found.

2. **Pi4 lid rebuild -- DONE.** The old lid was sized from the 58x49mm mounting-hole
   rectangle + a flat 20mm margin (98x89mm) -- since the real Pi4B board is 85x56mm with
   its holes only 3.5mm from the short edges, the real board overhung the old lid on the
   connector side. Rebuilt from the Raspberry Pi 4 Model B Datasheet's own official
   mechanical drawing (Release 1.1, March 2024, Section 3): 85x56mm board, 3mm corner
   radius, and a "Z=16.0mm" drawing callout for the tallest connector cluster (the stacked
   USB2/USB3 sockets), rounded up to 17mm. The new "avionics cover" is sized to the real
   board outline + clearance, wide enough to also cover the PCA9685 mounted beside it
   (Adafruit product 815, ~62.5x25.4mm, commonly documented footprint), with a full-height
   opening on BOTH short edges (the real Pi4 has connectors on both -- USB-C power + 2x
   micro-HDMI + audio on one, Ethernet + 4x USB-A on the other) and top vent slots. The
   Pi4's own mounting-hole pattern stayed exactly where it was (hard constraint), so the
   cover is intentionally asymmetric about the deck's Y=0 centerline rather than moving
   the holes to fit a symmetric cover.

3. **Hip abduction shims -- DONE.** The 10-degree static hip tilt left each hip housing
   touching the deck on only one corner (documented as a limitation, never modeled). Now
   `assemble_robot.py`'s `build_hip_shim()` makes a 20mm-thick PETG wedge in the bracket's
   own local frame, applies the EXACT SAME rotate+lift+mirror+translate transform the leg
   itself gets, then `.common()`s it against a big Z>=deck-top box to trim it flush --
   its top face matches the tilted housing's bottom face by construction, its bottom face
   is flat on the deck. All 4 shims check `clear (flush fit)` against both their own leg
   and the bottom deck in the interference report. The other documented limitation (the
   deck's own hip-mount holes stay straight/vertical) is still real and still not
   modeled -- a genuine angled-hole/washer detail, correctly out of scope for a wedge shim.

4. **Decks -> laser-cut sheet -- DONE.** `BODY_PLATE_THICKNESS` is now 3.0mm (3mm 5052
   aluminium as production intent, 3mm acrylic acceptable for the prototype -- identical
   geometry, design choice). Ribs (improvement 6) are removed from both decks -- a
   laser-cut sheet can't carry printed ribs -- their stiffening goal is now met by the
   box-section body walls (item 5) instead, explicitly marked SUPERSEDED (not deleted)
   above. The battery bay's 2mm blind locating pocket is removed (through-features only);
   its 2 strap slots stay. Outer corners are filleted R15, hip-notch inner corners R8
   (both design choices, `geometry_helpers.fillet_vertical_edges`, applied before any
   other cut per this project's fillet-robustness convention). The top deck gained 2
   40x12mm cable pass-through slots near the avionics area and 4 lightening cut-outs in
   its own clear areas -- the bottom deck deliberately keeps none (ground-facing, dust).
   Every existing mount pattern (hip bolts, standoffs, Pi4, sensing bay, skid plate holes)
   is unchanged.

5. **Box-section body -- DONE.** `build_body_walls.py` (new) replaces
   `build_shell_panels.py`'s two cosmetic panels with 2 structural side walls (+-Y edges,
   the same 200mm clear-X-gap span the old panels already used) + front/rear bulkheads
   (+-100mm in X, spanning the clear Y gap between the hip footprints) -- 3D-printed PETG,
   3mm wall, 10mm top/bottom flanges bolted (M3) into BOTH decks via holes shared exactly
   between the 3 files (`geometry_helpers.wall_flange_hole_xy`, so they can't drift
   apart). Each panel's longest dimension (200mm / 110mm) is checked against a 220mm
   printer-bed cap -- both pass, no splitting needed. Each side wall keeps an 80x40mm flat
   decal area (reused from the old panels' own requirement). The rear bulkhead (facing the
   LiDAR/rear overhang) carries a 22mm-standard E-stop cutout (industry-standard, cited),
   an XT60 panel-mount cutout (22x18mm, cited), and a small rocker-switch cutout
   (19.2x13mm, common KCD1-mini size, cited) -- all 3 spread along the bulkhead's own Y
   axis (its available Z band is too tight to stack all 3 without overlap). The front
   bulkhead (facing the camera-mast overhang) carries 6 vent slots instead.

6. **Real standoffs -- DONE.** `geometry_helpers.build_hex_standoff()` models the 4
   inter-deck standoffs as real M3 hex standoff solids, 5.5mm across flats (cited --
   standard M3 hex standoff hardware) x `STANDOFF_HEIGHT` (50mm, unchanged design choice),
   replacing the old un-modeled probe-cylinder stand-in. All 4 check `clear` against every
   leg in the interference report.

7. **LiDAR pedestal top plate -- DONE.** Replaces the notched 100mm disc with a plate
   following the RPLIDAR A1's real base outline (96.8 x 70.3mm, Slamtec's own cited
   headline spec) -- a 70.3mm circle unioned with a rectangle extending the long axis out
   to 96.8mm total (the rectangle overlaps the circle's own center, not just its tangent
   edge -- an early version that only touched the circle's edge produced 2 disconnected
   solids, caught by a real `len(Solids)` check, not assumed fine). The rear inset moved
   from 55mm to 65mm so the real (larger-reach) D-shape still fits inside the deck's own
   footprint. The old `LIDAR_DISC_HIP_NOTCH_W/D` params are deleted (confirmed unused --
   the smaller real-outline plate clears the tilted hind hip housings without them, per
   the interference report's `LH`/`RH` vs `TopDeck` rows, both `clear`).

8. **Hip housings, hollowed -- DONE.** `build_hip_bracket.py` now builds a real housing:
   4mm floor + 4mm walls (open top), outer vertical edges filleted R6, a cable exit slot
   on the inboard face, and the 4 floor bolt holes now cut through the floor only (not the
   full former solid block). A separate 3mm cap screws onto 4 corner bosses (2mm boss +
   3mm cap = 5mm added above the old 130mm envelope -- unavoidable once the top is open
   and a physical cap has to sit somewhere; the hard-constrained envelope + horn bolt
   circle themselves are untouched). An internal horizontal servo web sits at the horn
   bolt-circle's own height (offset down by `SERVO_HORN_FLANGE_HEIGHT`, an ASSUMPTION --
   no MG996R drawing callout for this dimension was found) with a `SERVO_BODY_L x
   SERVO_BODY_W` clearance cutout + 2 tab holes, so the hip servo's own output shaft is
   coaxial with the horn bolt circle by construction, not implied. The cap follows the
   leg's own transform (`build_full_leg()` returns it, `assemble_robot.py` fuses it into
   each leg's structural shape) and is in the interference union -- all 4 legs (now
   "structural, incl. hip cap") check `clear` everywhere.

9. **Payload reference envelopes -- DONE.** `build_payload.py` (new) exports 9 envelope
   solids -- battery, Pi4 (board+connector height, on 4 M2.5-standoff stand-ins),
   RPLiDAR A1 (D-shape, on its item-7 plate), PCA9685, MPU6050/GY-521 IMU, a UBEC, E-stop,
   XT60, and power switch -- every dimension cited or ASSUMPTION-labeled in `params.py`.
   Placement rules all satisfied by construction: IMU at 56.6mm from the body's XY center
   (< 60mm), screwed to the bottom deck (1 real mounting hole cut there, matching most
   real GY-521 boards' own single-hole pattern); UBEC on the bottom deck near the battery;
   PCA9685 under the avionics cover, beside the Pi4; E-stop/XT60/switch on the rear
   bulkhead, reachable from behind/above and well below the LiDAR scan band (Z~28mm vs.
   the band's own 156-176mm). PCA9685 and UBEC are secured by adhesive/zip-tie in this
   pass (no bolt pattern was invented for either -- stated honestly as a partial detail,
   not silently skipped). Exported separately as `payload.step` with its own object names
   (for distinct render coloring) and included in `assemble_robot.py`'s interference
   union -- all 9 check `clear`.

10. **Mass + torque sanity report -- DONE.** See "Mass + torque finding" below.

11. **Renders -- DONE (see "Renders" below) / PARTIAL if GUI rendering was unavailable in
    this environment, see that section for the actual outcome.**

12. **README -- DONE (this section).**

### Verification -- `assemble_robot.py` SUMMARY (verbatim)

```
Full robot bounding box (mm): X=500.0 Y=402.9 Z=405.1
  X range -250.0 to 250.0, Y range -201.4 to 201.4, Z range -224.1 to 181.0

--- Interference check ---
Sum of individual part volumes: 3410345 mm^3
Volume of their union (fused):  3410345 mm^3
FINDING: no overlapping material anywhere -- fully clear assembly.

--- LiDAR scan-plane occlusion check (Chassis v2 item 1) ---
Scan band: Z=[156.0, 176.0]mm (ASSUMPTION, 30-50mm above the LiDAR's own base at 126.0mm, see params.py), inner radius 50.4mm, outer radius 600mm.
  LiDAR scan band is CLEAR of every other part -- no occlusion (pan-tilt head neutral-pose top is well below the band's own floor, see MAST_HEIGHT note in params.py).

=== SUMMARY ===
Leg-vs-leg footprints: clear.
Leg-vs-decks: clear.
Leg-vs-new-parts: clear.
Standoffs (real hex solids): clear.
Hip shims: clear (flush fit as intended).
Payload envelopes: clear.
LiDAR scan-plane occlusion: CLEAR.

Assembly is fully interference-free (including all Chassis v2 parts) and the LiDAR scan-plane occlusion check passes.
```

Overall height dropped from 192mm (old pan-tilt-head top) to **181mm** (the LiDAR unit's
own top is now the tallest point) -- lower than the pre-Chassis-v2 model, not just
unchanged, directly helping the PS's under-carriage/tunnel/coach clearance requirement.

### Mass + torque finding

```
Fabricated-part mass (PETG 1.27g/cm^3, Al5052 2.68g/cm^3, UHMW 0.93g/cm^3, all cited): 4859 g
Bought-part mass (12x MG996R, 4x SG90, RPLIDAR A1, Pi4, battery, PCA9685, MPU6050, UBEC, E-stop, XT60, switch -- cited where a spec sheet publishes weight, ASSUMPTION otherwise): 1190 g
TOTAL estimated robot mass: 6049 g (6.05 kg)

Static torque sanity (2-leg/trot support, WORST CASE full-horizontal moment arm, not a dynamic gait analysis):
  Total weight: 59.3 N -> 29.7 N per supporting leg.
  Knee worst-case torque (arm=156mm): 4.63 N*m
  Hip worst-case torque  (arm=346mm): 10.28 N*m
  MG996R rated stall torque (cited, 11.0 kgf-cm @ 6V): 1.08 N*m
  FINDING: worst-case torque EXCEEDS the MG996R's rated stall torque.
```

**Reported honestly, NOT fixed:** the worst-case (fully horizontal leg, both supporting
legs sharing the full trotting load) knee and hip torques both exceed the MG996R's own
rated stall torque by a wide margin (4-10x). This is a genuine finding about the
CHAMP-derived leg geometry and servo choice, both explicitly out of scope for this pass
(hard constraint: don't change leg kinematics to fix a check). In practice a real
quadruped's stance is bent-kneed, not fully horizontal, and static stance load is shared
across all 4 feet most of the time (this worst case is specifically the 2-leg trot
moment, and specifically a fully-extended leg posture) -- so this is a conservative upper
bound, not a claim the robot cannot stand at all, but it is a real, unresolved
under-torque risk for anything approaching this worst case (e.g. a fast trot, or one leg
briefly bearing the full load on rough ballast) that a later pass should address by either
a higher-torque servo (e.g. DS3218MG, ~20kgf-cm) or a reduced worst-case moment arm
(a bent-knee stance limit in software), neither of which this pass's hard constraints
allow touching.

### New ASSUMPTIONs introduced this pass

- `LIDAR_SCAN_BAND_MIN/MAX_ABOVE_BASE` (30-50mm): the A1M8 datasheet's mechanical drawing
  didn't have a legible numeric scan-plane-height callout in the extracted text.
- `SERVO_HORN_FLANGE_HEIGHT` (4mm): no MG996R drawing callout found for the flange-to-
  spline-top height.
- UBEC envelope dimensions (25x20x7mm): the specific bought part (Adafruit 1385) has no
  published PCB envelope on its own product page; sized to the typical small-UBEC range
  reported across RC-hobby retailers for this product class.
- MPU6050/GY-521 hole diameter (2.0mm) and IMU/PCA9685/UBEC/E-stop/XT60/switch masses:
  typical-for-class values, no single official spec found across resellers.
- `LIDAR_BOLT_CIRCLE_DIA` (50mm, was 75mm): still an assumption (no official Slamtec
  bolt-spacing spec), resized only so the holes fit inside the new, narrower real-outline
  plate.

### Renders

Produced by `render_views.py` (GUI build, `freecad.exe render_views.py`, not
`freecadcmd`) -- see `renders/` for the PNG output: full robot iso/front/top/right,
a chassis-only iso with legs hidden, and a payload-highlighted view (decks made
semi-transparent, avionics cover hidden). Verified: all 6 PNGs render fully populated and
FreeCAD exits on its own (~10s).

Blank-render root cause, for anyone touching `render_views.py`: when a freecadcmd-saved
`.FCStd` (no `GuiDocument.xml`) is opened in the GUI build, every object reads back
`Visibility=False`. Copying that flag into the render scene gave an empty scene, so the
script skips the duplicate `<name>_Leg` bodies by name instead. The same effect means
`assembled_robot.FCStd` opened by hand in FreeCAD shows nothing at first -- select all in
the tree and press Space to show the parts. It also closes every document before closing
the window, since an unsaved document brings up a save prompt and FreeCAD never exits.

### Top-deck corner slivers (fixed after the Chassis v2 pass)

The hip clearance pockets' outer X edge (175 + 71 = 246mm) stopped 4mm short of the deck's
250mm end, leaving a 4 x 95mm sliver of 3mm sheet cantilevered off each corner (visible in
the renders as thin blades; present since the original pocket fix). `build_top_deck.py` now
runs each notch cutter straight out through the deck end, so the corners are open. Re-verified:
`assemble_robot.py` still reports fully interference-free with the LiDAR scan band clear.

### Obsolete files (not removed, flagged for a future cleanup)

- `build_shell_panels.py` and its own `shell_panels.*` exports -- superseded by
  `build_body_walls.py` / `body_walls.*`.
- `bottom_deck.*`, `top_deck.*`, `hip_bracket.*`, `assembled_robot.*` `.FCBak` files from
  before this pass are still on disk (this project's own convention is to never delete
  `.FCBak`/obsolete outputs, only flag them).

## Mechanics check (`check_mechanics.py`) -- the leg design cannot walk yet

Every interference check above verifies the static pose only. `check_mechanics.py` moves the
joints. Result as of 2026-09-12 (numbers from the script's own output):

- **Joints: 4 of 12 exist, and none can drive the leg.** CHAMP's `leg.urdf.xacro` has 3
  revolute joints per leg: hip ab/ad (axis X), upper leg (Y), lower leg (Y). An earlier note in
  this project said CHAMP has no ab/ad joint -- that was wrong; see docs/champ-research.md #3.1.
  - Hip ab/ad: the housing is bolted to the deck; the 10 deg tilt is a fixed shim.
  - Hip pitch: the servo sits in the hip housing, but 0/5 horn screw positions land on thigh
    material (the thigh's hip end is a servo-body slot, not a horn bolt pattern).
  - Knee: no servo, no linkage; the thigh/shin bolt circles are 39mm apart (a butt joint), and
    the links are coplanar, so any bend collides (209 mm^3 at 15 deg, 1,526 mm^3 at 90 deg).
- **Link lengths** come from CHAMP's visual box sizes (190.5/156mm), giving 171.5/168.7mm
  joint-to-joint, not CHAMP's 141/141mm kinematic distances.
- **Gait sweep** (x = +-62mm, h = 160..200mm): knees folding toward the body centre swing the
  thigh into the LeftWall (4,356 mm^3) and TopDeck (1,237 mm^3), because the 10 deg splay tilts
  the upper leg inboard over the deck. Knees folding away from the centre clear the chassis.
- **Torque** at nominal stance, static, 2 feet down: knee 3.68 N*m (4.73 kg as modelled) /
  2.67 N*m (acrylic decks, 3.43 kg) vs MG996R stall 1.08 N*m (~0.43 usable continuously).
  Printed parts are counted at 45% of solid PETG (ASSUMPTION); `assemble_robot.py`'s 6.04 kg
  counts them solid.
- **Ground clearance** at CHAMP's 200mm nominal height: deck underside 85mm, sniffer arm 6mm.
- **Centre of gravity**: X -20mm, 10-11mm off each trot diagonal (trimmable with CHAMP's
  `com_x_translation`).

The chassis (decks, walls, payload) is not the blocker; the leg mechanism and servo sizing are.
