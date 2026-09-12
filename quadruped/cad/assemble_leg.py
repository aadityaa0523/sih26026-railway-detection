"""
Assemble build_upper_leg.py's and build_lower_leg.py's already-exported STEP shapes
into one FreeCAD document, positioning the lower leg at the upper leg's knee end.

Axis convention (checked against both scripts): each link is a bar built along
local +Z, KNEE end at local Z=0 (upper leg) / local Z=LOWER_LEG_LENGTH (lower leg),
with its own bolt circle inset 20mm from that end. No rotation is needed -- both
links share the same X/Y cross-section convention (BRACKET_WIDTH x BRACKET_THICKNESS)
-- only a translation along Z to bring the lower leg's knee end flush against the
upper leg's knee end (global Z=0).

Run build_upper_leg.py and build_lower_leg.py first so their .step files exist.
"""
import FreeCAD as App
import Part

import params

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"

doc = App.newDocument("assembled_leg")

upper_shape = Part.Shape()
upper_shape.read(f"{out_dir}/upper_leg.step")

lower_shape = Part.Shape()
lower_shape.read(f"{out_dir}/lower_leg.step")
# Lower leg's knee end (top, local Z=LOWER_LEG_LENGTH) -> global Z=0, flush against
# the upper leg's own knee end (bottom, local/global Z=0). Legs hang down from there.
lower_shape.translate(App.Vector(0, 0, -params.LOWER_LEG_LENGTH))

upper_obj = doc.addObject("Part::Feature", "UpperLeg")
upper_obj.Shape = upper_shape
lower_obj = doc.addObject("Part::Feature", "LowerLeg")
lower_obj.Shape = lower_shape
doc.recompute()

print(f"UpperLeg solid valid: {upper_shape.isValid()}")
print(f"LowerLeg solid valid: {lower_shape.isValid()}")

combined = Part.makeCompound([upper_shape, lower_shape])
bbox = combined.BoundBox
print(f"Assembled leg bounding box (mm): X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")

structural_length = params.UPPER_LEG_LENGTH + params.LOWER_LEG_LENGTH
print(f"Structural leg length (hip end to knee-end-to-knee-end sum, excludes foot cap boss): "
      f"{structural_length:.1f}mm (upper {params.UPPER_LEG_LENGTH}mm + lower {params.LOWER_LEG_LENGTH}mm)")
print(f"Full tip-to-tip bounding box length (includes foot boss): {bbox.ZLength:.1f}mm")

nominal_height = 200.0  # mm, CHAMP gait.yaml nominal_height = 0.20m (docs/champ-research.md #3.1)
ratio = nominal_height / structural_length
print(f"\nCHAMP gait.yaml nominal_height = {nominal_height:.0f}mm vs. this leg's structural "
      f"length {structural_length:.1f}mm -> stance height is {ratio*100:.0f}% of full leg extension.")
if 0.4 <= ratio <= 0.85:
    print("FINDING: plausible. A bent-knee stance at ~50-70% of max leg reach is normal for "
          "legged robots (the knee folds to reach 200mm, it does not need to be near-straight) -- "
          "no bent/angled hip offset is required to make 200mm reachable.")
else:
    print("FINDING: needs a closer look -- this ratio is outside the normal bent-knee stance "
          "range for legged robots; consider a bent/angled hip offset or re-checking link lengths.")

doc.saveAs(f"{out_dir}/assembled_leg.FCStd")
print("Saved: assembled_leg.FCStd")
