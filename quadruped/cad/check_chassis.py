"""
CHASSIS V3 verification script -- loads every exported chassis STEP file (all build_*.py
scripts must be re-run first if params.py changed) and runs the checks the task brief
requires:
  1. Every chassis part isValid().
  2. Chassis-only interference: sum of part volumes == volume of their fused union.
  3. V3 SPEC contract: every chassis solid vs geometry_helpers.leg_zone(HIP_AXIS_Z) <= 1mm^3
     (including the sniffer arm's DEPLOYED pose, not just the STOWED pose used in #2).
  4. LiDAR scan-band slab clear of every other chassis part.

Never loosens a check or drops a part to pass -- a real conflict is reported, not hidden.
Run standalone: freecadcmd check_chassis.py (no other script's objects are open).
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import load_step_solids, chassis_envelope, leg_zone, build_hex_standoff

CAD = params.CAD_DIR
TOL = 1.0   # mm^3, per the task's own "<=1mm^3" tolerance

doc = App.newDocument("check_chassis")

# ---- Load every chassis part (the STOWED sniffer pose, per the task's own "sniffer stowed"
# union member). build_top_deck.py and build_camera_pan_tilt.py each build in their OWN
# local frame (deck/mount-plate top at local Z=0) -- same "build" vs. "assemble" split this
# project's other build_*.py scripts use (e.g. build_upper_leg.py) -- so this script (which
# assembles the chassis-only subset for verification) applies the same global placement
# transforms an assemble_robot.py-style integration script would.
TOP_DECK_Z = params.BODY_PLATE_THICKNESS + params.STANDOFF_HEIGHT   # global Z of the top deck's own local Z=0
FRONT_X = params.CHASSIS_LENGTH / 2.0 - 20.0                        # must match build_top_deck.py's own FRONT_X
MAST_TOP_Z = TOP_DECK_Z + params.BODY_PLATE_THICKNESS + params.MAST_HEIGHT + params.MAST_FACE_THICKNESS

parts = {}
for stem, prefix in [("bottom_deck", "BottomDeck"), ("body_walls", "Wall"),
                      ("abad_mount", "AbadBracket"), ("payload", "Payload"),
                      ("skid_plate", "SkidPlate"), ("sniffer_arm", "SnifferStowed")]:
    for i, s in enumerate(load_step_solids(f"{CAD}/{stem}.step")):
        parts[f"{prefix}_{i}"] = s

# top_deck.step export order (build_top_deck.py): [TopDeckPlate, CameraMast, LidarPedestal,
# TopDeckLid] -- named explicitly here (not "TopDeck_i") so the mass breakdown below can
# correctly split the flat acrylic plate from the printed-PETG mast/pedestal/lid risers.
TOP_DECK_NAMES = ["TopDeckPlate", "CameraMast", "LidarPedestal", "TopDeckLid"]
for i, s in enumerate(load_step_solids(f"{CAD}/top_deck.step")):
    s.translate(App.Vector(0, 0, TOP_DECK_Z))
    name = TOP_DECK_NAMES[i] if i < len(TOP_DECK_NAMES) else f"TopDeck_{i}"
    parts[name] = s

for i, s in enumerate(load_step_solids(f"{CAD}/pan_tilt_head.step")):
    s.translate(App.Vector(FRONT_X, 0, MAST_TOP_Z))
    parts[f"PanTilt_{i}"] = s

# Real M3 hex standoffs (not their own build_*.py script -- built directly, same as
# assemble_robot.py's own convention).
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        standoff = build_hex_standoff(params.STANDOFF_HEX_ACROSS_FLATS, params.STANDOFF_HEIGHT,
                                       params.STANDOFF_HOLE_DIA,
                                       App.Vector(sx, sy, params.BODY_PLATE_THICKNESS))
        parts[f"Standoff_{sx:.0f}_{sy:.0f}"] = standoff

print(f"Loaded {len(parts)} chassis solids.\n")

# ---- Check 1: validity ----
print("--- Check 1: solid validity ---")
invalid = [name for name, s in parts.items() if not s.isValid()]
for name, s in parts.items():
    if not s.isValid():
        print(f"  INVALID: {name}")
if not invalid:
    print(f"  All {len(parts)} solids valid.")

# ---- Check 2: chassis-only interference (sum of volumes == volume of fused union) ----
print("\n--- Check 2: chassis-only interference ---")
solids_list = list(parts.values())
sum_vol = sum(s.Volume for s in solids_list)
fused = solids_list[0]
for s in solids_list[1:]:
    fused = fused.fuse(s)
union_vol = fused.Volume
diff = abs(sum_vol - union_vol)
print(f"  Sum of individual volumes: {sum_vol:.0f} mm^3")
print(f"  Volume of fused union:     {union_vol:.0f} mm^3")
print(f"  Difference: {diff:.2f} mm^3 (tolerance {TOL} mm^3): {'PASS' if diff <= TOL else 'FAIL'}")
if diff > TOL:
    print("  Isolating which parts overlap...")
    names = list(parts.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for s1 in parts[names[i]].Solids:
                for s2 in parts[names[j]].Solids:
                    v = s1.common(s2).Volume
                    if v > TOL:
                        print(f"    CLASH: {names[i]} x {names[j]} = {v:.0f} mm^3")

# ---- Check 3: V3 SPEC contract vs leg_zone(HIP_AXIS_Z) ----
print("\n--- Check 3: V3 SPEC envelope contract (vs leg_zone) ---")
zone = leg_zone(params.HIP_AXIS_Z)
contract_fail = []
for name, s in parts.items():
    v = s.common(zone).Volume
    status = "PASS" if v <= TOL else "FAIL"
    if v > TOL:
        contract_fail.append(name)
    if v > TOL:
        print(f"  {name}: {v:.1f} mm^3 in leg_zone -- {status}")
if not contract_fail:
    print(f"  All {len(parts)} chassis solids clear of leg_zone (<= {TOL} mm^3 each).")

# Sniffer arm DEPLOYED pose, checked the same way, separately (not part of the union above).
print("\n  Sniffer arm DEPLOYED pose (not part of the main chassis union):")
for i, s in enumerate(load_step_solids(f"{CAD}/sniffer_arm_extended.step")):
    v = s.common(zone).Volume
    print(f"    SnifferDeployed_{i}: {v:.1f} mm^3 in leg_zone -- {'PASS' if v <= TOL else 'FAIL'}")
    if v > TOL:
        contract_fail.append(f"SnifferDeployed_{i}")

# ---- Check 4: LiDAR scan-band clear of every other part ----
print("\n--- Check 4: LiDAR scan-band occlusion ---")
top_deck_top_z = 2 * params.BODY_PLATE_THICKNESS + params.STANDOFF_HEIGHT
lidar_base_z = top_deck_top_z + params.LIDAR_PEDESTAL_HEIGHT
band_z0 = lidar_base_z + params.LIDAR_SCAN_BAND_MIN_ABOVE_BASE
band_z1 = lidar_base_z + params.LIDAR_SCAN_BAND_MAX_ABOVE_BASE
R = params.LIDAR_SCAN_BAND_OUTER_RADIUS
band = Part.makeBox(2 * R, 2 * R, band_z1 - band_z0, App.Vector(-R, -R, band_z0))
print(f"  LiDAR's own base (pedestal top): Z={lidar_base_z:.1f}mm. Scan band: "
      f"Z=[{band_z0:.1f},{band_z1:.1f}]mm.")
occluded = []
for name, s in parts.items():
    if name.startswith("Payload_"):
        continue   # the LiDAR unit itself (and every other payload envelope) is checked below by name
    v = s.common(band).Volume
    if v > TOL:
        occluded.append((name, v))
# Re-check payload envelopes individually, skipping the RPLidarA1 envelope itself (identified
# by its own bbox ZMin matching lidar_base_z -- that IS the scanner, checking it against its
# own scan band is meaningless) rather than by name (avoids re-running build_payload.py just
# to recover its object-name order).
payload_solids = load_step_solids(f"{CAD}/payload.step")
for i, s in enumerate(payload_solids):
    if abs(s.BoundBox.ZMin - lidar_base_z) < 0.5:
        continue
    v = s.common(band).Volume
    if v > TOL:
        occluded.append((f"Payload_{i}", v))

if occluded:
    for name, v in occluded:
        print(f"  OCCLUDED: {name} = {v:.1f} mm^3 in the scan band")
else:
    print("  Scan band is CLEAR of every other chassis part.")

# ---- Mass breakdown (task item 9) ----
print("\n--- Chassis mass breakdown ---")

# Mass-review fix: only the FLAT SHEET decks are acrylic -- the mast/pedestal/lid are chunky
# printed risers, kept as SEPARATE objects in top_deck.step specifically so they price as
# printed PETG here, not (as an earlier pass wrongly did, by fusing them into one "TopDeck"
# solid) as 100%-solid acrylic sheet.
acrylic_names = [n for n in parts if n.startswith("BottomDeck") or n == "TopDeckPlate"]
printed_names = [n for n in parts if n.startswith("Wall") or n.startswith("AbadBracket")
                 or n.startswith("PanTilt") or n.startswith("SnifferStowed")
                 or n in ("CameraMast", "LidarPedestal", "TopDeckLid")]
acrylic_vol = sum(parts[n].Volume for n in acrylic_names)
printed_vol = sum(parts[n].Volume for n in printed_names)
uhmw_vol = sum(parts[n].Volume for n in parts if n.startswith("SkidPlate"))

acrylic_g = acrylic_vol * params.DENSITY_ACRYLIC
printed_g = printed_vol * params.DENSITY_PETG * 0.45   # ASSUMPTION: 45% of solid, per project convention
uhmw_g = uhmw_vol * params.DENSITY_UHMW
standoff_g = 4 * params.MASS_STANDOFF_G

bought_g = (params.MASS_BATTERY_G + params.MASS_SERVO_BEC_G + params.MASS_UBEC_G
            + params.MASS_MPU6050_G + 4 * params.MASS_DS3225_G + 4 * params.MASS_ABAD_HORN_G
            + params.MASS_PI4_G + params.MASS_PCA9685_G + params.MASS_RPLIDAR_A1_G
            + params.MASS_ESTOP_G + params.MASS_XT60_G + params.MASS_SWITCH_G
            + 4 * params.MASS_SG90_G)   # pan-tilt (2x) + sniffer (2x)

total_g = acrylic_g + printed_g + uhmw_g + standoff_g + bought_g

print(f"  Acrylic decks (flat sheet only -- bottom deck + top deck plate, 100% solid, "
      f"{params.DENSITY_ACRYLIC * 1000:.2f} g/cm^3, cited): {acrylic_g:.0f} g")
print(f"  Printed PETG parts (walls+bulkheads, ab/ad housings, camera mast, LiDAR pedestal, "
      f"avionics cover, pan-tilt, sniffer arm; 45% of solid {params.DENSITY_PETG * 1000:.2f} "
      f"g/cm^3, ASSUMPTION): {printed_g:.0f} g")
print(f"  UHMW skid plate ({params.DENSITY_UHMW * 1000:.2f} g/cm^3, cited): {uhmw_g:.0f} g")
print(f"  4x M3 hex standoffs ({params.MASS_STANDOFF_G:.0f}g each, ASSUMPTION): {standoff_g:.0f} g")
print(f"  Bought parts (battery, servo BEC, Pi UBEC, IMU, 4x DS3225+horn, Pi4, PCA9685, "
      f"RPLiDAR A1, E-stop, XT60, switch, 4x SG90): {bought_g:.0f} g")
print(f"  TOTAL chassis mass: {total_g:.0f} g ({total_g / 1000.0:.2f} kg)")
print(f"  MASS_TARGET_KG (whole robot): {params.MASS_TARGET_KG:.1f} kg -- legs (~4x0.25-0.3kg, "
      f"the other agent's own module) budgeted separately.")

if invalid or diff > TOL or contract_fail or occluded:
    print("\n=== SUMMARY: ONE OR MORE CHECKS FAILED -- see above. ===")
else:
    print("\n=== SUMMARY: all checks PASS. ===")
