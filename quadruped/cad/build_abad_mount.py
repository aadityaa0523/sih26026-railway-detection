"""
Hip ab/ad servo mounts (V3 SPEC item 2) -- 4 printed housings bolted to the bottom deck,
each holding one DS3225 (params.LEG_SERVO) lying on its SIDE so its output shaft/horn axis
runs horizontal through the hip point along +-X, at exactly (+-BASE_TO_HIP_X, +-BASE_TO_HIP_Y,
HIP_AXIS_Z) -- the CHAMP <leg>_hip_joint origin, and the boundary plane between BODY_BOX and
NOSE_BOX in the V3 SPEC envelope contract (params.py / geometry_helpers.py). The leg module
(the OTHER agent's own file) bolts onto this servo's output horn from the NOSE_BOX/leg_zone
side; everything this script builds stays on the BODY_BOX side (or just inside NOSE_BOX for
the small horn disc) by construction, verified by check_chassis.py.

Servo axis convention (standard hobby-servo case, flat-mount shaft-up: L=SERVO_BODY_L=40mm
runs horizontal carrying SERVO_SHAFT_OFFSET=10mm from one end to the shaft, W=SERVO_BODY_W=
20mm the other horizontal axis, H=SERVO_BODY_H=40.5mm vertical base-to-top with the shaft
protruding from the TOP). Rotating the whole servo 90deg about Y so its shaft points along
global +-X swaps L and H: **H (40.5mm) becomes the shaft/global-X axis, L (40mm, carrying the
10mm shaft offset) becomes the vertical/global-Z axis, W (20mm) stays global Y.** The case is
placed so the shaft lands exactly at global Z=HIP_AXIS_Z: chosen here 10mm above the case's
own bottom (case Z = [HIP_AXIS_Z-10, HIP_AXIS_Z-10+SERVO_BODY_L]) -- an arbitrary but
consistent choice of which case end is "near" (see params.py SERVO_SHAFT_OFFSET), documented
here since neither servo end is otherwise distinguished in this model.

Housing: a solid PETG block with a SERVO_BODY_H x SERVO_BODY_W x SERVO_BODY_L pocket cut
through it, OPEN at the horn-face end (the pocket reaches exactly to the housing's own outer
face there, so the servo/horn are inserted from and protrude out that side) and walled
(ABAD_MOUNT_WALL) everywhere else, standing on a base flange that continues down to the
bottom deck and bolts to it via 4 corner M4-clearance holes -- a documented simplification of
the servo's own real tab-ear geometry (its 4 "tab holes"), same honest-simplification
convention build_camera_pan_tilt.py/build_sniffer_arm.py already use for their SG90 pockets.
Mounts to the BOTTOM DECK ONLY (design choice, see params.py's own ABAD_MOUNT_WALL note) --
its own top (Z=65mm) sits well clear of the top deck (Z=73mm).

The servo body itself and its 25T aluminium horn are BOUGHT parts, not printed -- per the
task brief they're modeled in build_payload.py instead (named AbadServo_LF etc.), not here;
this file exports only the 4 printed housings (the thing that's actually fabricated).
"""
import FreeCAD as App
import Part

import params

out_dir = params.CAD_DIR

WALL = params.ABAD_MOUNT_WALL
CASE_L, CASE_W, CASE_H = params.SERVO_BODY_L, params.SERVO_BODY_W, params.SERVO_BODY_H
DECK_TOP = params.BODY_PLATE_THICKNESS

# Case Z-range (vertical, = the servo's own L axis with the 10mm shaft offset embedded) --
# shaft 10mm above the case's own chosen "bottom" end, see module docstring.
CASE_Z0 = params.HIP_AXIS_Z - params.SERVO_SHAFT_OFFSET
CASE_Z1 = CASE_Z0 + CASE_L
HOUSING_Z0 = CASE_Z0 - WALL
HOUSING_Z1 = CASE_Z1 + WALL

HIP_POINTS = []
for hip_x in (params.BASE_TO_HIP_X, -params.BASE_TO_HIP_X):
    sign = 1 if hip_x > 0 else -1
    for hip_y in (params.BASE_TO_HIP_Y, -params.BASE_TO_HIP_Y):
        HIP_POINTS.append((hip_x, hip_y, sign))


def _label(hip_x, hip_y):
    front = "F" if hip_x > 0 else "H"
    side = "L" if hip_y > 0 else "R"
    return f"{side}{front}"   # LF, RF, LH, RH


def build_one(hip_x, hip_y, sign):
    """Housing + base flange + servo pocket, for one hip point (printed part only -- the
    servo body/horn themselves are bought parts, modeled in build_payload.py instead)."""
    # Housing X-extent: from the horn face (hip_x) inboard by CASE_H+WALL.
    if sign > 0:
        block_x0, block_x1 = hip_x - (CASE_H + WALL), hip_x
    else:
        block_x0, block_x1 = hip_x, hip_x + (CASE_H + WALL)
    block_y0, block_y1 = hip_y - (CASE_W / 2.0 + WALL), hip_y + (CASE_W / 2.0 + WALL)

    housing = Part.makeBox(block_x1 - block_x0, block_y1 - block_y0, HOUSING_Z1 - HOUSING_Z0,
                            App.Vector(block_x0, block_y0, HOUSING_Z0))

    # Servo pocket -- open at the horn face (flush with the housing's own outer face there).
    if sign > 0:
        pocket_x0 = hip_x - CASE_H
    else:
        pocket_x0 = hip_x
    pocket = Part.makeBox(CASE_H, CASE_W, CASE_L,
                           App.Vector(pocket_x0, hip_y - CASE_W / 2.0, CASE_Z0))
    housing = housing.cut(pocket)

    # Base flange: same XY footprint, from the deck top up to the housing's own bottom.
    flange = Part.makeBox(block_x1 - block_x0, block_y1 - block_y0, HOUSING_Z0 - DECK_TOP,
                           App.Vector(block_x0, block_y0, DECK_TOP))
    inset = params.ABAD_MOUNT_INSET
    for dx in (inset, (block_x1 - block_x0) - inset):
        for dy in (inset, (block_y1 - block_y0) - inset):
            hole = Part.makeCylinder(params.SERVO_TAB_HOLE_DIA / 2.0, HOUSING_Z0 - DECK_TOP,
                                      App.Vector(block_x0 + dx, block_y0 + dy, DECK_TOP), App.Vector(0, 0, 1))
            flange = flange.cut(hole)

    bracket = housing.fuse(flange)
    return bracket


def flange_hole_xy():
    """Global (x, y) positions of all 16 base-flange bolt holes (4 per hip x 4 hips) --
    shared with build_bottom_deck.py so the two files can't drift apart, same convention as
    geometry_helpers.wall_flange_hole_xy."""
    pts = []
    inset = params.ABAD_MOUNT_INSET
    for hip_x, hip_y, sign in HIP_POINTS:
        if sign > 0:
            block_x0 = hip_x - (CASE_H + WALL)
        else:
            block_x0 = hip_x
        block_y0 = hip_y - (CASE_W / 2.0 + WALL)
        for dx in (inset, (CASE_H + 2 * WALL) - inset):
            for dy in (inset, (CASE_W + 2 * WALL) - inset):
                pts.append((block_x0 + dx, block_y0 + dy))
    return pts


doc = App.newDocument("abad_mount")
brackets = {}
for hip_x, hip_y, sign in HIP_POINTS:
    label = _label(hip_x, hip_y)
    brackets[f"AbadBracket_{label}"] = build_one(hip_x, hip_y, sign)

objs = []
for name, shape in brackets.items():
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    objs.append(obj)
doc.recompute()

print(f"Ab/ad servo mount housings (printed PETG, V3 SPEC item 2) -- 4x, hip axis "
      f"Z={params.HIP_AXIS_Z:.1f}mm. Housing Z=[{HOUSING_Z0:.1f},{HOUSING_Z1:.1f}]mm, base "
      f"flange bolts to the bottom deck only (design choice, see params.py). Servo body + "
      f"horn (bought parts) are in build_payload.py instead.")
for name, shape in brackets.items():
    bbox = shape.BoundBox
    print(f"  {name}: bbox X=[{bbox.XMin:.1f},{bbox.XMax:.1f}] Y=[{bbox.YMin:.1f},{bbox.YMax:.1f}] "
          f"Z=[{bbox.ZMin:.1f},{bbox.ZMax:.1f}]  Volume={shape.Volume:.0f}mm^3  Solid valid: {shape.isValid()}")

out_dir = params.CAD_DIR
doc.saveAs(f"{out_dir}/abad_mount.FCStd")
Part.export(objs, f"{out_dir}/abad_mount.step")
Part.export(objs, f"{out_dir}/abad_mount.stl")
print("Saved: abad_mount.FCStd, abad_mount.step, abad_mount.stl")
