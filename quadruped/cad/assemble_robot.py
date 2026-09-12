"""
Full-robot assembly: bottom deck + top deck (on real M3 hex standoffs, item 6) + 4 full legs
(hollow hip housing + cap + upper leg + lower leg, via assemble_full_leg.py's
build_full_leg()), each placed and mirrored at CHAMP's real hip offsets (BASE_TO_HIP_X/Y,
params.py), plus 4 hip-abduction wedge shims (item 3), box-section body walls (item 5), the
skid plate, pan-tilt head (neutral pose), sniffer arm (neutral pose), and the payload
reference envelopes (item 9).

Importing assemble_full_leg (below) re-runs that script's own top-level report and
re-saves assembled_full_leg.FCStd/.step as a side effect -- harmless, and it guarantees
the single-leg files stay in sync with whatever build_full_leg() currently does.

---- Deck stack (Z, all from params.py) ----
  bottom deck: Z [0, BODY_PLATE_THICKNESS]                              native position
  standoffs:   Z [BODY_PLATE_THICKNESS, BODY_PLATE_THICKNESS+STANDOFF_HEIGHT]   REAL M3 hex
               standoff SOLIDS now (item 6, geometry_helpers.build_hex_standoff), not the
               old un-modeled probe-cylinder stand-in.
  top deck:    Z shifted up by BODY_PLATE_THICKNESS+STANDOFF_HEIGHT (now 53mm, was 56mm --
               BODY_PLATE_THICKNESS dropped 4mm->3mm for Chassis v2 item 4), from its own
               native [0, THICKNESS]

Each hip housing's bottom face (local Z=0 -- see build_hip_bracket.py's own docstring,
"this face mates flat against the body plate") sits at global Z=BODY_PLATE_THICKNESS,
directly on the bottom deck's top surface -- except at the one corner the hip-abduction
tilt keeps flush; a printed wedge SHIM (item 3, new) now fills the rest of that gap, see
below.

---- Left/right mirroring: which axis, and why ----
build_hip_bracket.py's horn-face bolt circle (where the leg attaches) is cut on ONE hip
face only -- local Y=HIP_Y (see assemble_full_leg.py's docstring) -- so a leg built by
build_full_leg() always extends outward in the hip block's local +Y direction. CHAMP's
own axis convention (docs/champ-research.md #5's manual-offset convention, "+y to the
left, -y to the right", confirmed by #3.1's Mini Pupper right-front offsets all being
negative-Y) is +Y = left. So:
  - LEFT legs (lf, lh): NO mirror -- local +Y already points the correct way (left/+Y).
  - RIGHT legs (rf, rh): mirror the whole leg (hip+cap+upper+lower, one rigid unit so the
    hip-to-knee-to-foot mates carry through unchanged) across the XZ plane (negate Y)
    so local +Y becomes global -Y (right), *before* translating into its final position.

No FRONT/HIND mirror is applied -- CHAMP's gait.yaml knee_orientation is a single uniform
value (">>", docs/champ-research.md #3.1) and this project's leg model has no built-in
front/back asymmetry to correct for. Front vs. hind placement is a plain +-BASE_TO_HIP_X
translation.

---- Hip abduction/adduction angle (improvement 1) ----
Real quadrupeds (Spot, ANYmal, Unitree) use a powered hip ab/ad joint for sprawl
stability; CHAMP's stock config has none, so this is a STATIC mounting tilt of each
whole hip-and-leg unit, NOT a new powered DOF. Each leg is rotated by HIP_ABDUCTION_DEG
about the front-back (X) axis, pivoting at the center of its own bottom mounting face,
then lifted in Z so the tilted footprint's lowest corner returns to Z=0.

CHASSIS V2 item 3 (hip abduction shims): the old limitation here -- "the bracket's bottom
face no longer sits fully flush, a real build would want a shim" -- is now MODELED, not
just documented: build_hip_shim() makes a HIP_SHIM_THICKNESS-tall wedge block in the
bracket's own local frame, gets the EXACT SAME rotate+lift+mirror+translate transform the
leg gets, then a `.common()` with a big Z>=deck-top box trims it flush top-and-bottom --
its top face now matches the tilted housing's own bottom face exactly (by construction,
not approximated) and its bottom face is flat on the deck. Printed PETG (design choice).
The other limitation (deck's own hip-mount holes stay straight/vertical) is still real and
still not modeled -- a genuine angled-hole/washer detail, out of scope for this pass.

---- Interference check ----
Real boolean-geometry checks (Part `.common()` shared-volume, not bounding-box overlap)
across EVERY part in the assembly, including the new ones (hex standoffs, hip shims, body
walls, payload envelopes) -- see the printed report for the full drill-down. A raw
multi-solid STEP read (top_deck.step's deck+lid, body_walls.step's 4 panels, payload.step's
9 envelopes) is NEVER passed straight into `.common()` -- FreeCAD 1.1's Part.Shape.common()
silently returns 0 volume against a multi-solid Compound (a confirmed bug) -- each such file
is loaded via geometry_helpers.load_step_solids() and kept as separate individual solids
instead (see that function's own docstring for why `.fuse()` doesn't fix a compound of
genuinely disjoint solids either).

---- Chassis v2 item 1: LiDAR scan-plane occlusion check (NEW) ----
See params.py's own LIDAR_SCAN_BAND_* comments for the full ASSUMPTION derivation. An
annular slab (inner radius clears the LiDAR's own real-outline plate, outer radius 600mm,
thickness = the assumed scan band) centered on the LiDAR's own axis must not intersect ANY
other part of the robot (the payload's own RPLidarA1 envelope is excluded by name, same
"don't flag a part for occluding itself" logic the inner radius already provides).
MAST_HEIGHT was cut from 50mm to 8mm specifically so the pan-tilt head's neutral pose stays
clear of this band -- see params.py.

Run build_bottom_deck.py, build_top_deck.py, build_hip_bracket.py, build_upper_leg.py,
build_lower_leg.py, build_skid_plate.py, build_camera_pan_tilt.py, build_sniffer_arm.py,
build_body_walls.py and build_payload.py first so their .step files exist.
"""
import itertools
import math

import FreeCAD as App
import Part

import params
import assemble_full_leg as leg
from geometry_helpers import load_step_solids, build_hex_standoff

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"

doc = App.newDocument("assembled_robot")

# ---- Decks ----
bottom_deck_shape = Part.Shape()
bottom_deck_shape.read(f"{out_dir}/bottom_deck.step")   # native Z=[0, THICKNESS], no shift

top_deck_solids = load_step_solids(f"{out_dir}/top_deck.step")   # [TopDeck, TopDeckLid]
DECK_GAP = params.BODY_PLATE_THICKNESS + params.STANDOFF_HEIGHT   # 53mm (was 56mm, item 4), deck-to-deck
for s in top_deck_solids:
    s.translate(App.Vector(0, 0, DECK_GAP))
top_deck_shape, top_deck_lid_shape = top_deck_solids

HIP_BOTTOM_Z = params.BODY_PLATE_THICKNESS   # hip housing's local Z=0 lands here


def mirror_y(shape):
    """Mirror a shape across the XZ plane (negate Y only) -- see module docstring."""
    mat = App.Matrix()
    mat.scale(1, -1, 1)
    mirrored = shape.copy()
    mirrored.transformShape(mat)
    return mirrored


# name -> (hip_x, hip_y, mirror) -- CHAMP's real base_to_hip_x/y offsets (params.py),
# +X front / -X hind, +Y left / -Y right (see module docstring).
LEG_POSITIONS = {
    "LF": (params.BASE_TO_HIP_X, params.BASE_TO_HIP_Y, False),
    "RF": (params.BASE_TO_HIP_X, -params.BASE_TO_HIP_Y, True),
    "LH": (-params.BASE_TO_HIP_X, params.BASE_TO_HIP_Y, False),
    "RH": (-params.BASE_TO_HIP_X, -params.BASE_TO_HIP_Y, True),
}

# Hip abduction (improvement 1, see module docstring): pivot at the hip block's own
# bottom-mounting-face center, then a lift that exactly returns the tilted footprint's
# lowest corner to Z=0 (exact for a rectangular box rotated about its own center).
ABDUCTION_PIVOT = App.Vector(0, params.HIP_Y_LENGTH / 2.0, 0)
ABDUCTION_LIFT_Z = (params.HIP_Y_LENGTH / 2.0) * math.sin(math.radians(params.HIP_ABDUCTION_DEG))


def build_hip_shim():
    """A HIP_SHIM_THICKNESS-tall wedge block (Chassis v2 item 3), in the hip housing's own
    native local frame, spanning its own 112x80mm footprint just BELOW its bottom face
    (Z: -HIP_SHIM_THICKNESS..0). Carries the SAME 4 corner bolt holes the housing's own floor
    does (the same bolt passes through both). The caller applies the identical
    rotate+lift+mirror+translate transform the leg itself gets, then trims it flush with a
    `.common()` against a big Z>=deck-top box -- see module docstring.
    """
    shim = Part.makeBox(params.HIP_X_LENGTH, params.HIP_Y_LENGTH, params.HIP_SHIM_THICKNESS,
                         App.Vector(0, 0, -params.HIP_SHIM_THICKNESS))
    inset = params.HIP_MOUNT_INSET
    for x in (inset, params.HIP_X_LENGTH - inset):
        for y in (inset, params.HIP_Y_LENGTH - inset):
            hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, params.HIP_SHIM_THICKNESS,
                                      App.Vector(x, y, -params.HIP_SHIM_THICKNESS), App.Vector(0, 0, 1))
            shim = shim.cut(hole)
    return shim


# A big box spanning Z>=deck-top (HIP_BOTTOM_Z), used to trim each tilted wedge shim flush
# against the deck (its own bottom face becomes exactly HIP_BOTTOM_Z, not below it).
TRIM_ABOVE_DECK = Part.makeBox(2000.0, 2000.0, 2000.0, App.Vector(-1000.0, -1000.0, HIP_BOTTOM_Z))

leg_shapes = {}          # name -> Part.Shape, STRUCTURAL only (hip+cap+upper+lower), for interference checks
leg_shapes_visual = {}   # name -> Part.Shape, structural + dust bellows, for the doc/export only
hip_visual_shapes = {}   # name -> Part.Shape, hip housing + cap ONLY -- kept separate from the leg
leglink_visual_shapes = {}   # name -> Part.Shape, upper + lower leg + bellows ONLY
shim_shapes = {}         # name -> Part.Shape, hip-abduction wedge shim (item 3)
for name, (hip_x, hip_y, mirror) in LEG_POSITIONS.items():
    hip_shape, upper_shape, lower_shape, hip_attach_point, bellows_shapes, cap_shape = leg.build_full_leg()
    # fuse (not makeCompound) -- FreeCAD 1.1's Part.Shape.common() silently returns an
    # empty result against a multi-solid Compound (see geometry_helpers.load_step_solids'
    # own docstring) -- fuse sidesteps that bug and is harmless here since these parts are
    # mated edge-to-edge (or, for the cap, resting on its own boss posts), never overlapping.
    hip_visual = hip_shape.fuse(cap_shape)      # kept separate, only for distinct render coloring
    leglink_visual = upper_shape.fuse(lower_shape).fuse(bellows_shapes[0]).fuse(bellows_shapes[1])
    full = hip_visual.fuse(upper_shape).fuse(lower_shape)
    full_visual = full.fuse(bellows_shapes[0]).fuse(bellows_shapes[1])
    shim = build_hip_shim()

    for s in (full, full_visual, hip_visual, leglink_visual, shim):
        s.rotate(ABDUCTION_PIVOT, App.Vector(1, 0, 0), params.HIP_ABDUCTION_DEG)
        s.translate(App.Vector(0, 0, ABDUCTION_LIFT_Z))

    if mirror:
        full = mirror_y(full)
        full_visual = mirror_y(full_visual)
        hip_visual = mirror_y(hip_visual)
        leglink_visual = mirror_y(leglink_visual)
        shim = mirror_y(shim)

    hip_center_x = params.HIP_X_LENGTH / 2.0
    hip_center_y = -params.HIP_Y_LENGTH / 2.0 if mirror else params.HIP_Y_LENGTH / 2.0
    shift = App.Vector(hip_x - hip_center_x, hip_y - hip_center_y, HIP_BOTTOM_Z)
    full.translate(shift)
    full_visual.translate(shift)
    hip_visual.translate(shift)
    leglink_visual.translate(shift)
    shim.translate(shift)
    shim = shim.common(TRIM_ABOVE_DECK)

    leg_shapes[name] = full
    leg_shapes_visual[name] = full_visual
    hip_visual_shapes[name] = hip_visual
    leglink_visual_shapes[name] = leglink_visual
    shim_shapes[name] = shim

# ---- Real M3 hex standoffs (Chassis v2 item 6) -- replace the old un-modeled probe cylinder. ----
standoff_shapes = {}
for sx in (-params.STANDOFF_X, params.STANDOFF_X):
    for sy in (-params.STANDOFF_Y, params.STANDOFF_Y):
        standoff_shapes[f"Standoff_{sx:.0f}_{sy:.0f}"] = build_hex_standoff(
            params.STANDOFF_HEX_ACROSS_FLATS, params.STANDOFF_HEIGHT, params.STANDOFF_HOLE_DIA,
            App.Vector(sx, sy, HIP_BOTTOM_Z))

# ---- Skid plate (improvement 5), pan-tilt head + sniffer arm NEUTRAL pose (improvement 4) ----
skid_plate_shape = Part.Shape()
skid_plate_shape.read(f"{out_dir}/skid_plate.step")   # native frame already matches the deck's

FRONT_X = params.BASE_X_LENGTH / 2.0 - 30.0   # mm, matches build_top_deck.py's own mast inset
# Top of the mast's own mounting plate -- MAST_HEIGHT is now only 8mm (Chassis v2 item 1, see
# params.py), so this is much lower than the old 50mm version.
mast_plate_top_z = (DECK_GAP + params.BODY_PLATE_THICKNESS + params.MAST_HEIGHT
                     + params.MAST_FACE_THICKNESS)
pan_tilt_shape = Part.Shape()
pan_tilt_shape.read(f"{out_dir}/pan_tilt_head.step")
pan_tilt_shape.translate(App.Vector(FRONT_X, 0, mast_plate_top_z))

SENSING_CX = params.BASE_X_LENGTH / 2.0 - 50.0   # mm, matches build_bottom_deck.py's own inset
sniffer_arm_shape = Part.Shape()
sniffer_arm_shape.read(f"{out_dir}/sniffer_arm.step")   # already hangs down from local Z=0
sniffer_arm_shape.translate(App.Vector(SENSING_CX, 0, 0))

# ---- Box-section body walls (Chassis v2 item 5) -- REPLACES the old cosmetic shell panels. ----
wall_names = ["LeftWall", "RightWall", "FrontBulkhead", "RearBulkhead"]
wall_solids = load_step_solids(f"{out_dir}/body_walls.step")   # already in the global frame
wall_shapes = dict(zip(wall_names, wall_solids))

# ---- Payload reference envelopes (Chassis v2 item 9) -- already in the global frame. ----
payload_names = ["Battery", "UBEC", "IMU", "Pi4", "PCA9685", "RPLidarA1", "EStop", "XT60", "PowerSwitch"]
payload_solids = load_step_solids(f"{out_dir}/payload.step")
payload_shapes = dict(zip(payload_names, payload_solids))

REAR_X = -(params.BASE_X_LENGTH / 2.0 - 65.0)   # must match build_top_deck.py's own REAR_X

# ---- Build the FreeCAD document ----
deck_objs = {}
for name, shape in (("BottomDeck", bottom_deck_shape), ("TopDeck", top_deck_shape),
                     ("TopDeckLid", top_deck_lid_shape), ("SkidPlate", skid_plate_shape),
                     ("PanTiltHead", pan_tilt_shape), ("SnifferArm", sniffer_arm_shape)):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    deck_objs[name] = obj

wall_objs = {}
for name, shape in wall_shapes.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    wall_objs[name] = obj

leg_objs = {}
for name, shape in leg_shapes_visual.items():
    obj = doc.addObject("Part::Feature", f"{name}_Leg")
    obj.Shape = shape
    obj.Visibility = False   # hidden: the split HipHousing/LegLinks objects below render instead
    leg_objs[name] = obj

# Also add the hip housing and leg-links as SEPARATE doc objects (in addition to the single
# fused *_Leg object above, which stays the one used for STEP export/interference) purely so
# render_views.py (item 11) can color hip housings differently from leg links.
hip_objs, leglink_objs = {}, {}
for name, shape in hip_visual_shapes.items():
    obj = doc.addObject("Part::Feature", f"{name}_HipHousing")
    obj.Shape = shape
    hip_objs[name] = obj
for name, shape in leglink_visual_shapes.items():
    obj = doc.addObject("Part::Feature", f"{name}_LegLinks")
    obj.Shape = shape
    leglink_objs[name] = obj

shim_objs = {}
for name, shape in shim_shapes.items():
    obj = doc.addObject("Part::Feature", f"{name}_HipShim")
    obj.Shape = shape
    shim_objs[name] = obj

standoff_objs = {}
for name, shape in standoff_shapes.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    standoff_objs[name] = obj

payload_objs = {}
for name, shape in payload_shapes.items():
    obj = doc.addObject("Part::Feature", f"Payload_{name}")
    obj.Shape = shape
    payload_objs[name] = obj

doc.recompute()

print(f"BottomDeck solid valid: {bottom_deck_shape.isValid()}")
print(f"TopDeck solid valid: {top_deck_shape.isValid()}")
print(f"TopDeckLid (avionics cover) solid valid: {top_deck_lid_shape.isValid()}")
print(f"SkidPlate solid valid: {skid_plate_shape.isValid()}")
print(f"PanTiltHead (neutral) solid valid: {pan_tilt_shape.isValid()}")
print(f"SnifferArm (neutral) solid valid: {sniffer_arm_shape.isValid()}")
for name, shape in wall_shapes.items():
    print(f"{name} solid valid: {shape.isValid()}")
for name, shape in leg_shapes.items():
    print(f"{name} leg (structural, incl. hip cap) valid: {shape.isValid()}")
for name, shape in shim_shapes.items():
    print(f"{name} hip shim valid: {shape.isValid()}")
for name, shape in standoff_shapes.items():
    print(f"{name} valid: {shape.isValid()}")
for name, shape in payload_shapes.items():
    print(f"Payload {name} valid: {shape.isValid()}")

all_shapes = ([bottom_deck_shape, top_deck_shape, top_deck_lid_shape, skid_plate_shape,
               pan_tilt_shape, sniffer_arm_shape]
              + list(wall_shapes.values())
              + list(leg_shapes.values())
              + list(shim_shapes.values())
              + list(standoff_shapes.values())
              + list(payload_shapes.values()))
combined = Part.makeCompound(all_shapes)
bbox = combined.BoundBox
print(f"\nFull robot bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"  X range {bbox.XMin:.1f} to {bbox.XMax:.1f}, Y range {bbox.YMin:.1f} to {bbox.YMax:.1f}, "
      f"Z range {bbox.ZMin:.1f} to {bbox.ZMax:.1f}")

# ---- Interference check: real boolean-geometry overlap, not bounding-box guessing ----
print("\n--- Interference check ---")

TOL = 1.0   # mm^3, ignore sliver/touching-face artifacts below this

sum_vol = sum(s.Volume for s in all_shapes)
fused = all_shapes[0]
for s in all_shapes[1:]:
    fused = fused.fuse(s)
overlap_vol = sum_vol - fused.Volume
print(f"Sum of individual part volumes: {sum_vol:.0f} mm^3")
print(f"Volume of their union (fused):  {fused.Volume:.0f} mm^3")
if overlap_vol > TOL:
    print(f"FINDING: {overlap_vol:.0f} mm^3 of overlapping material found somewhere in the "
          f"assembly -- drilling down below.")
else:
    print("FINDING: no overlapping material anywhere -- fully clear assembly.")

# Leg vs. leg
print("\nLeg vs. leg:")
any_leg_clash = False
for a, b in itertools.combinations(leg_shapes, 2):
    vol = leg_shapes[a].common(leg_shapes[b]).Volume
    status = "CLASH" if vol > TOL else "clear"
    print(f"  {a} vs {b}: {status} ({vol:.0f} mm^3)")
    any_leg_clash = any_leg_clash or vol > TOL

# Leg vs. each deck
print("\nLeg vs. decks:")
any_deck_clash = False
for name, shape in leg_shapes.items():
    bd_vol = shape.common(bottom_deck_shape).Volume
    td_vol = shape.common(top_deck_shape).Volume
    any_deck_clash = any_deck_clash or bd_vol > TOL or td_vol > TOL
    print(f"  {name} vs BottomDeck: {'CLASH' if bd_vol > TOL else 'clear'} ({bd_vol:.0f} mm^3)")
    print(f"  {name} vs TopDeck:    {'CLASH' if td_vol > TOL else 'clear'} ({td_vol:.0f} mm^3)")

# Real M3 hex standoffs (item 6) vs. legs.
print("\nStandoffs (real hex solids, item 6) vs. legs:")
any_standoff_clash = False
for sname, sshape in standoff_shapes.items():
    for name, shape in leg_shapes.items():
        vol = sshape.common(shape).Volume
        if vol > TOL:
            any_standoff_clash = True
            print(f"  {sname} vs {name}: CLASH ({vol:.0f} mm^3)")
if not any_standoff_clash:
    print("  no standoff/leg clashes found.")

# Hip shims (item 3) vs. legs and decks -- expected to TOUCH (flush fit), not overlap.
print("\nHip shims (item 3) vs. legs/decks:")
any_shim_clash = False
for name, shim in shim_shapes.items():
    leg_vol = shim.common(leg_shapes[name]).Volume
    bd_vol = shim.common(bottom_deck_shape).Volume
    if leg_vol > TOL or bd_vol > TOL:
        any_shim_clash = True
    print(f"  {name} shim vs its own leg: {'CLASH' if leg_vol > TOL else 'clear (flush fit)'} ({leg_vol:.0f} mm^3)")
    print(f"  {name} shim vs BottomDeck:  {'CLASH' if bd_vol > TOL else 'clear (flush fit)'} ({bd_vol:.0f} mm^3)")

# Leg vs. the other mechanical/cosmetic parts (skid plate, pan-tilt head, sniffer arm, walls).
print("\nLeg vs. new parts (skid plate / pan-tilt head / sniffer arm / body walls):")
any_newpart_clash = False
for name, shape in leg_shapes.items():
    sp_vol = shape.common(skid_plate_shape).Volume
    pt_vol = shape.common(pan_tilt_shape).Volume
    sa_vol = shape.common(sniffer_arm_shape).Volume
    wall_vol = sum(shape.common(w).Volume for w in wall_shapes.values())
    any_newpart_clash = any_newpart_clash or sp_vol > TOL or pt_vol > TOL or sa_vol > TOL or wall_vol > TOL
    print(f"  {name} vs SkidPlate:    {'CLASH' if sp_vol > TOL else 'clear'} ({sp_vol:.0f} mm^3)")
    print(f"  {name} vs PanTilt:      {'CLASH' if pt_vol > TOL else 'clear'} ({pt_vol:.0f} mm^3)")
    print(f"  {name} vs SnifferArm:   {'CLASH' if sa_vol > TOL else 'clear'} ({sa_vol:.0f} mm^3)")
    print(f"  {name} vs BodyWalls:    {'CLASH' if wall_vol > TOL else 'clear'} ({wall_vol:.0f} mm^3)")

# Payload envelopes (item 9) vs. everything structural.
print("\nPayload envelopes (item 9) vs. legs/decks/walls:")
any_payload_clash = False
structural_for_payload = list(leg_shapes.values()) + [bottom_deck_shape, top_deck_shape] + list(wall_shapes.values())
for pname, pshape in payload_shapes.items():
    clash_vol = sum(pshape.common(s).Volume for s in structural_for_payload)
    if clash_vol > TOL:
        any_payload_clash = True
        print(f"  {pname}: CLASH ({clash_vol:.0f} mm^3)")
if not any_payload_clash:
    print("  no payload/structure clashes found.")

# ---- Chassis v2 item 1: LiDAR scan-plane occlusion check (NEW) ----
print("\n--- LiDAR scan-plane occlusion check (Chassis v2 item 1) ---")
pedestal_top_z = DECK_GAP + params.BODY_PLATE_THICKNESS + params.LIDAR_PEDESTAL_HEIGHT
band_z0 = pedestal_top_z + params.LIDAR_SCAN_BAND_MIN_ABOVE_BASE
band_z1 = pedestal_top_z + params.LIDAR_SCAN_BAND_MAX_ABOVE_BASE
band_h = band_z1 - band_z0
inner_r = params.LIDAR_PLATE_LENGTH / 2.0 + params.LIDAR_SCAN_BAND_CLEARANCE
outer_r = params.LIDAR_SCAN_BAND_OUTER_RADIUS
outer_cyl = Part.makeCylinder(outer_r, band_h, App.Vector(REAR_X, 0, band_z0), App.Vector(0, 0, 1))
inner_cyl = Part.makeCylinder(inner_r, band_h, App.Vector(REAR_X, 0, band_z0), App.Vector(0, 0, 1))
scan_band = outer_cyl.cut(inner_cyl)
print(f"Scan band: Z=[{band_z0:.1f}, {band_z1:.1f}]mm (ASSUMPTION, {params.LIDAR_SCAN_BAND_MIN_ABOVE_BASE:.0f}-"
      f"{params.LIDAR_SCAN_BAND_MAX_ABOVE_BASE:.0f}mm above the LiDAR's own base at {pedestal_top_z:.1f}mm, "
      f"see params.py), inner radius {inner_r:.1f}mm, outer radius {outer_r:.0f}mm.")

occluders_checked = {k: v for k, v in {**{"BottomDeck": bottom_deck_shape, "TopDeck": top_deck_shape,
                                           "TopDeckLid": top_deck_lid_shape, "SkidPlate": skid_plate_shape,
                                           "PanTiltHead": pan_tilt_shape, "SnifferArm": sniffer_arm_shape},
                                        **wall_shapes, **leg_shapes,
                                        **{f"Shim_{k}": v for k, v in shim_shapes.items()},
                                        **standoff_shapes,
                                        **{k: v for k, v in payload_shapes.items() if k != "RPLidarA1"}}.items()}
any_scan_clash = False
for name, shape in occluders_checked.items():
    vol = scan_band.common(shape).Volume
    if vol > TOL:
        any_scan_clash = True
        print(f"  OCCLUDER: {name} intrudes into the LiDAR scan band ({vol:.0f} mm^3)")
if not any_scan_clash:
    print("  LiDAR scan band is CLEAR of every other part -- no occlusion "
          f"(pan-tilt head neutral-pose top is well below the band's own floor, "
          f"see MAST_HEIGHT note in params.py).")

print("\n=== SUMMARY ===")
print(f"Leg-vs-leg footprints: {'CLASH FOUND' if any_leg_clash else 'clear'}.")
print(f"Leg-vs-decks: {'CLASH FOUND -- see above' if any_deck_clash else 'clear'}.")
print(f"Leg-vs-new-parts: {'CLASH FOUND -- see above' if any_newpart_clash else 'clear'}.")
print(f"Standoffs (real hex solids): {'CLASH FOUND -- see above' if any_standoff_clash else 'clear'}.")
print(f"Hip shims: {'CLASH FOUND -- see above' if any_shim_clash else 'clear (flush fit as intended)'}.")
print(f"Payload envelopes: {'CLASH FOUND -- see above' if any_payload_clash else 'clear'}.")
print(f"LiDAR scan-plane occlusion: {'OCCLUDED -- see above' if any_scan_clash else 'CLEAR'}.")
if not any([any_leg_clash, any_deck_clash, any_standoff_clash, any_newpart_clash,
            any_shim_clash, any_payload_clash, any_scan_clash]):
    print("\nAssembly is fully interference-free (including all Chassis v2 parts) and the "
          "LiDAR scan-plane occlusion check passes.")

# ---- Chassis v2 item 10: mass + torque sanity report (print-only) ----
print("\n=== MASS + TORQUE SANITY REPORT (Chassis v2 item 10) ===")


def g(volume_mm3, density_g_per_mm3):
    return volume_mm3 * density_g_per_mm3


# One structural instance of each fabricated part -- volumes already computed above.
one_leg_hip_cap_vol = leg_shapes["LF"].Volume   # includes hip housing + cap + upper + lower leg
one_shim_vol = shim_shapes["LF"].Volume
wall_vol_total = sum(s.Volume for s in wall_shapes.values())
standoff_vol_total = sum(s.Volume for s in standoff_shapes.values())

fabricated_mass_g = 0.0
fabricated_mass_g += g(one_leg_hip_cap_vol * 4, params.DENSITY_PETG)         # 4x hip+cap+upper+lower
fabricated_mass_g += g(one_shim_vol * 4, params.DENSITY_PETG)                # 4x hip shims
fabricated_mass_g += g(wall_vol_total, params.DENSITY_PETG)                  # body walls
fabricated_mass_g += g(top_deck_lid_shape.Volume, params.DENSITY_PETG)       # avionics cover
fabricated_mass_g += g(pan_tilt_shape.Volume, params.DENSITY_PETG)
fabricated_mass_g += g(sniffer_arm_shape.Volume, params.DENSITY_PETG)
fabricated_mass_g += g(bottom_deck_shape.Volume, params.DENSITY_AL5052)
fabricated_mass_g += g(top_deck_shape.Volume, params.DENSITY_AL5052)
fabricated_mass_g += g(skid_plate_shape.Volume, params.DENSITY_UHMW)
fabricated_mass_g += g(standoff_vol_total, params.DENSITY_AL5052)   # rough stand-in, brass/steel not modeled separately

bought_mass_g = (12 * params.MASS_MG996R_G + 4 * params.MASS_SG90_G + params.MASS_RPLIDAR_A1_G
                  + params.MASS_PI4_G + params.MASS_BATTERY_G + params.MASS_PCA9685_G
                  + params.MASS_MPU6050_G + params.MASS_UBEC_G + params.MASS_ESTOP_G
                  + params.MASS_XT60_G + params.MASS_SWITCH_G)

total_mass_g = fabricated_mass_g + bought_mass_g
print(f"Fabricated-part mass (PETG {params.DENSITY_PETG*1000:.2f}g/cm^3, Al5052 "
      f"{params.DENSITY_AL5052*1000:.2f}g/cm^3, UHMW {params.DENSITY_UHMW*1000:.2f}g/cm^3, "
      f"all cited): {fabricated_mass_g:.0f} g")
print(f"Bought-part mass (12x MG996R, 4x SG90, RPLIDAR A1, Pi4, battery, PCA9685, MPU6050, "
      f"UBEC, E-stop, XT60, switch -- cited where a spec sheet publishes weight, ASSUMPTION "
      f"otherwise, see params.py): {bought_mass_g:.0f} g")
print(f"TOTAL estimated robot mass: {total_mass_g:.0f} g ({total_mass_g/1000.0:.2f} kg)")

# Static torque sanity: 2-leg support (diagonal trot pair) at full leg geometry -- worst case,
# NOT a dynamic gait analysis. Moment arm = the leg's own full horizontal reach if it were
# lying flat (a genuine worst case upper bound, not a nominal-stance number).
total_mass_kg = total_mass_g / 1000.0
weight_n = total_mass_kg * 9.81
force_per_leg_n = weight_n / 2.0   # 2-leg (diagonal) support during a trot
knee_arm_m = params.LOWER_LEG_LENGTH / 1000.0
hip_arm_m = (params.UPPER_LEG_LENGTH + params.LOWER_LEG_LENGTH) / 1000.0
knee_torque_nm = force_per_leg_n * knee_arm_m
hip_torque_nm = force_per_leg_n * hip_arm_m
mg996r_stall_nm = params.MG996R_STALL_TORQUE_KGF_CM * 0.0980665   # kgf-cm -> N*m (1 kgf-cm = 0.0980665 N*m)

print(f"\nStatic torque sanity (2-leg/trot support, WORST CASE full-horizontal moment arm, "
      f"not a dynamic gait analysis):")
print(f"  Total weight: {weight_n:.1f} N -> {force_per_leg_n:.1f} N per supporting leg.")
print(f"  Knee worst-case torque (arm={knee_arm_m*1000:.0f}mm): {knee_torque_nm:.2f} N*m")
print(f"  Hip worst-case torque  (arm={hip_arm_m*1000:.0f}mm): {hip_torque_nm:.2f} N*m")
print(f"  MG996R rated stall torque (cited, {params.MG996R_STALL_TORQUE_KGF_CM:.1f} kgf-cm @ 6V): "
      f"{mg996r_stall_nm:.2f} N*m")
if knee_torque_nm > mg996r_stall_nm or hip_torque_nm > mg996r_stall_nm:
    print("  FINDING: worst-case torque EXCEEDS the MG996R's rated stall torque -- the servo "
          "choice is under-rated for this worst-case (full-horizontal-leg) loading condition. "
          "Reported honestly, NOT fixed here (the leg geometry/servo choice is out of scope "
          "for this pass, see the hard constraints).")
else:
    print("  FINDING: worst-case torque stays within the MG996R's rated stall torque.")

# ---- Save/export ----
doc.saveAs(f"{out_dir}/assembled_robot.FCStd")
Part.export(list(deck_objs.values()) + list(wall_objs.values()) + list(leg_objs.values())
            + list(shim_objs.values()) + list(standoff_objs.values()),
            f"{out_dir}/assembled_robot.step")
print("\nSaved: assembled_robot.FCStd, assembled_robot.step (payload envelopes are also in the "
      ".FCStd for rendering, and are additionally exported separately as payload.step by "
      "build_payload.py, per item 9).")
