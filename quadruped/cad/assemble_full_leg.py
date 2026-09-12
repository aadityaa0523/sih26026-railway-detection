"""
Extends assemble_leg.py: attaches the hip bracket to the upper leg's hip end, then
mates the lower leg at the knee exactly as assemble_leg.py already did. Result is one
hip-to-foot leg (hip bracket + upper leg + lower leg with its foot boss).

---- Hip-to-upper-leg mate (new) ----
build_hip_bracket.py cuts the hip-axis servo's output-horn bolt circle on the block's
front face: local (X=HIP_X/2, Y=HIP_Y, Z=HIP_Z-30) -- bored through Y, same "bolt circle
lies in the local XZ plane" convention geometry_helpers.py uses everywhere (knee joint
included). That front face is cut through the FULL Y depth (Y=0 to Y=HIP_Y), so either
Y=0 or Y=HIP_Y works geometrically as the mating plane -- Y=HIP_Y (the face further from
the block's own origin) is picked here as an arbitrary-but-documented choice with no
physical consequence for a single leg (assemble_robot.py mirrors the whole leg for
left/right anyway, so "which face" only matters relative to that mirror, not in isolation).

Unlike the knee, the upper leg's OWN hip end has no bolt circle to match against -- per
build_upper_leg.py it only cuts a servo-BODY pocket (a box, not a circle) there, because
that end holds the hip servo's body rather than bolting to its horn. So there is no
"identical bolt pattern on both sides" trick to lean on like the knee mate's 20mm-inset
symmetry (see assemble_leg.py's docstring). The mating reference point used here instead
is the CENTER of that pocket (X=BRACKET_WIDTH/2, Z=UPPER_LEG_LENGTH-SERVO_BODY_H/2) --
the pocket's own natural stand-in for "where the hip servo roughly sits," since neither
script models an explicit shaft/horn hole inside that pocket (same documented-
approximation level as the rest of this project, e.g. the un-modeled foot cap).

Axis convention check (same reasoning as assemble_leg.py's knee mate): the hip block
(X=width, Y=depth/bore axis, Z=height) and the leg bar (X=width, Y=thickness/bore axis,
Z=length) already share the same X/Y/Z semantics -- bore axis Y, hole/pocket pattern in
the local XZ plane -- for both the hip's horn interface and the leg's hip-end pocket. So,
exactly like the knee mate, NO ROTATION is needed, only translation.

Run build_hip_bracket.py, build_upper_leg.py and build_lower_leg.py first so their
.step files exist.
"""
import FreeCAD as App
import Part

import params

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"

# Upper leg's own bracket width -- must match build_upper_leg.py exactly.
LEG_BRACKET_WIDTH = params.SERVO_BODY_W + 2 * params.WALL  # 28.2mm


def build_full_leg():
    """Load the 3 STEP shapes fresh and mate them into one hip-to-foot leg.

    Returns (hip_shape, upper_shape, lower_shape, hip_attach_point):
    - hip_shape is returned UNTRANSLATED, still in its own native local frame
      (X:[0,HIP_X], Y:[0,HIP_Y], Z:[0,HIP_Z]) -- callers (this script's __main__ and
      assemble_robot.py) both need that native frame to then place the whole leg at a
      body-mount position, so translating it here would just have to be undone.
    - upper_shape / lower_shape are positioned relative to that same hip-local frame.
    - hip_attach_point is the App.Vector of the hip horn bolt-circle center in that
      frame -- the "hip joint" reference used for the hip-to-foot length sanity check.
    """
    hip_shape = Part.Shape()
    hip_shape.read(f"{out_dir}/hip_bracket.step")

    upper_shape = Part.Shape()
    upper_shape.read(f"{out_dir}/upper_leg.step")

    lower_shape = Part.Shape()
    lower_shape.read(f"{out_dir}/lower_leg.step")

    # Hip bracket's horn bolt-circle center (build_hip_bracket.py) -- see module docstring.
    hip_cx = params.HIP_X_LENGTH / 2.0
    hip_horn_y = params.HIP_Y_LENGTH
    hip_horn_z = params.HIP_Z_LENGTH - 30.0
    hip_attach_point = App.Vector(hip_cx, hip_horn_y, hip_horn_z)

    # Upper leg's hip-end pocket center (build_upper_leg.py) -- see module docstring.
    leg_cx = LEG_BRACKET_WIDTH / 2.0
    leg_pocket_center_z = params.UPPER_LEG_LENGTH - params.SERVO_BODY_H / 2.0

    # Translate only (no rotation, see docstring): X/Z bring the leg's pocket center to
    # the hip's horn center; Y brings the leg's own Y=0 face flush against the hip's
    # Y=HIP_Y front face.
    hip_shift = App.Vector(hip_cx - leg_cx, hip_horn_y, hip_horn_z - leg_pocket_center_z)
    upper_shape.translate(hip_shift)

    # Knee mate -- unchanged from assemble_leg.py, then carried along by the same
    # hip_shift so it stays flush against the (now hip-mated) upper leg.
    lower_shape.translate(App.Vector(0, 0, -params.LOWER_LEG_LENGTH))
    lower_shape.translate(hip_shift)

    return hip_shape, upper_shape, lower_shape, hip_attach_point


doc = App.newDocument("assembled_full_leg")

hip_shape, upper_shape, lower_shape, hip_attach_point = build_full_leg()

hip_obj = doc.addObject("Part::Feature", "HipBracket")
hip_obj.Shape = hip_shape
upper_obj = doc.addObject("Part::Feature", "UpperLeg")
upper_obj.Shape = upper_shape
lower_obj = doc.addObject("Part::Feature", "LowerLeg")
lower_obj.Shape = lower_shape
doc.recompute()

print(f"HipBracket solid valid: {hip_shape.isValid()}")
print(f"UpperLeg solid valid: {upper_shape.isValid()}")
print(f"LowerLeg solid valid: {lower_shape.isValid()}")

combined = Part.makeCompound([hip_shape, upper_shape, lower_shape])
bbox = combined.BoundBox
print(f"Full leg (hip+upper+lower) bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")

# Full hip-to-foot-boss length: from the hip attachment point (the horn bolt-circle
# center -- the actual hip-joint reference, not the raw upper-leg top) down to the
# foot boss's bottom tip (the assembly's lowest Z).
hip_to_foot_length = hip_attach_point.z - bbox.ZMin
raw_sum = params.UPPER_LEG_LENGTH + params.LOWER_LEG_LENGTH
# The hip attach point sits SERVO_BODY_H/2 below the upper leg's own raw top (it's
# the pocket's center, not the physical end of the bar) -- that inset shortens the
# measured length vs. assemble_leg.py's raw sum, while the foot boss (unmodeled in
# assemble_leg.py's structural_length) lengthens it back by FOOT_BOSS_HEIGHT (10mm).
hip_inset_below_raw_top = params.SERVO_BODY_H / 2.0
print(f"\nHip attachment point (horn bolt-circle center) Z = {hip_attach_point.z:.1f}mm")
print(f"Foot boss bottom Z = {bbox.ZMin:.1f}mm")
print(f"Full hip-to-foot-boss length: {hip_to_foot_length:.1f}mm "
      f"(vs. assemble_leg.py's raw upper+lower sum of {raw_sum:.1f}mm: "
      f"-{hip_inset_below_raw_top:.1f}mm because the hip attach point sits inside the "
      f"upper leg's hip-end pocket, not at its raw top, +10.0mm for the foot boss "
      f"assemble_leg.py's structural_length excluded)")

nominal_height = 200.0  # mm, CHAMP gait.yaml nominal_height = 0.20m (docs/champ-research.md #3.1)
ratio = nominal_height / hip_to_foot_length
print(f"\nCHAMP gait.yaml nominal_height = {nominal_height:.0f}mm vs. this leg's full "
      f"hip-to-foot-boss length {hip_to_foot_length:.1f}mm -> stance height is "
      f"{ratio*100:.0f}% of full leg extension (measured from the actual hip joint, "
      f"not the raw upper-leg top).")
if 0.4 <= ratio <= 0.85:
    print("FINDING: plausible. A bent-knee stance at ~50-70% of max leg reach is normal for "
          "legged robots (the knee folds to reach 200mm, it does not need to be near-straight) -- "
          "no bent/angled hip offset is required to make 200mm reachable.")
else:
    print("FINDING: needs a closer look -- this ratio is outside the normal bent-knee stance "
          "range for legged robots; consider a bent/angled hip offset or re-checking link lengths.")

doc.saveAs(f"{out_dir}/assembled_full_leg.FCStd")
Part.export([hip_obj, upper_obj, lower_obj], f"{out_dir}/assembled_full_leg.step")
print("\nSaved: assembled_full_leg.FCStd, assembled_full_leg.step")
