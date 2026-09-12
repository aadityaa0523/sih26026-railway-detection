"""
Full-robot assembly: bottom deck + top deck (on standoffs) + 4 full legs (hip bracket +
upper leg + lower leg, via assemble_full_leg.py's build_full_leg()), each placed and
mirrored at CHAMP's real hip offsets (BASE_TO_HIP_X/Y, params.py).

Importing assemble_full_leg (below) re-runs that script's own top-level report and
re-saves assembled_full_leg.FCStd/.step as a side effect -- harmless, and it guarantees
the single-leg files stay in sync with whatever build_full_leg() currently does.

---- Deck stack (Z, all from params.py) ----
  bottom deck: Z [0, BODY_PLATE_THICKNESS]                              native position
  standoffs:   Z [BODY_PLATE_THICKNESS, BODY_PLATE_THICKNESS+STANDOFF_HEIGHT]   not
               modeled as solids -- bought hardware, like every other un-modeled
               fastener in this project -- only their bolt holes are cut into both decks
               (build_bottom_deck.py / build_top_deck.py already share this XY pattern).
  top deck:    Z shifted up by BODY_PLATE_THICKNESS+STANDOFF_HEIGHT (56mm), from its own
               native [0, THICKNESS]

Each hip bracket's bottom face (local Z=0 -- see build_hip_bracket.py's own docstring,
"this face mates flat against the body plate") sits at global Z=BODY_PLATE_THICKNESS,
directly on the bottom deck's top surface.

---- Left/right mirroring: which axis, and why ----
build_hip_bracket.py's horn-face bolt circle (where the leg attaches) is cut on ONE hip
face only -- local Y=HIP_Y (see assemble_full_leg.py's docstring) -- so a leg built by
build_full_leg() always extends outward in the hip block's local +Y direction. CHAMP's
own axis convention (docs/champ-research.md #5's manual-offset convention, "+y to the
left, -y to the right", confirmed by #3.1's Mini Pupper right-front offsets all being
negative-Y) is +Y = left, -Y = right. So:
  - LEFT legs (lf, lh): NO mirror -- local +Y already points the correct way (left/+Y).
  - RIGHT legs (rf, rh): mirror the whole leg (hip+upper+lower, one rigid unit so the
    hip-to-knee-to-foot mates carry through unchanged) across the XZ plane (negate Y)
    so local +Y becomes global -Y (right), *before* translating into its final position.

No FRONT/HIND mirror is applied, for two independent reasons that agree:
  1. CHAMP's gait.yaml knee_orientation is a single uniform value, ">>" (docs/champ-
     research.md #3.1) -- the stock robot's front and hind knees fold the SAME
     rotational sense, unlike a horse's fore-aft-mirrored legs.
  2. This project's own leg model has no built-in front/back geometric asymmetry to
     correct for in the first place -- build_upper_leg.py / build_lower_leg.py are
     straight vertical bars, not pre-bent links.
Front vs. hind placement is therefore a plain +-BASE_TO_HIP_X translation, no mirror.

---- Interference check ----
Real boolean-geometry checks (Part `.common()` shared-volume, not bounding-box overlap)
between: every pair of legs, every leg vs. each deck, and a probe cylinder at each
standoff hole position (spanning the deck-to-deck gap, standing in for the un-modeled
standoff hardware itself) vs. every leg. See the printed report -- and the README's
"Full assembly" section -- for the result; it is not a clean pass.

Run build_bottom_deck.py, build_top_deck.py, build_hip_bracket.py, build_upper_leg.py
and build_lower_leg.py first so their .step files exist.
"""
import itertools

import FreeCAD as App
import Part

import params
import assemble_full_leg as leg

out_dir = "C:/Users/Aadityaa/iqoo/quadruped/cad"

doc = App.newDocument("assembled_robot")

# ---- Decks ----
bottom_deck_shape = Part.Shape()
bottom_deck_shape.read(f"{out_dir}/bottom_deck.step")   # native Z=[0, THICKNESS], no shift

top_deck_shape = Part.Shape()
top_deck_shape.read(f"{out_dir}/top_deck.step")
DECK_GAP = params.BODY_PLATE_THICKNESS + params.STANDOFF_HEIGHT   # 56mm, deck-to-deck
top_deck_shape.translate(App.Vector(0, 0, DECK_GAP))

HIP_BOTTOM_Z = params.BODY_PLATE_THICKNESS   # hip bracket's local Z=0 lands here


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

leg_shapes = {}   # name -> Part.Shape (hip+upper+lower fused into one solid), placed in the body frame
for name, (hip_x, hip_y, mirror) in LEG_POSITIONS.items():
    hip_shape, upper_shape, lower_shape, _ = leg.build_full_leg()
    # fuse (not makeCompound) -- FreeCAD 1.1's Part.Shape.common() silently returns an
    # empty result against a multi-solid Compound (confirmed while writing this script:
    # a translated 3-solid compound's .common() gave 0 while the identical geometry
    # fused into one solid gave the correct nonzero volume) -- fuse sidesteps that bug
    # and is harmless here since the 3 parts are mated edge-to-edge, never overlapping.
    full = hip_shape.fuse(upper_shape).fuse(lower_shape)
    if mirror:
        full = mirror_y(full)

    hip_center_x = params.HIP_X_LENGTH / 2.0
    hip_center_y = -params.HIP_Y_LENGTH / 2.0 if mirror else params.HIP_Y_LENGTH / 2.0
    shift = App.Vector(hip_x - hip_center_x, hip_y - hip_center_y, HIP_BOTTOM_Z)
    full.translate(shift)
    leg_shapes[name] = full

# ---- Build the FreeCAD document ----
deck_objs = {}
for name, shape in (("BottomDeck", bottom_deck_shape), ("TopDeck", top_deck_shape)):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    deck_objs[name] = obj

leg_objs = {}
for name, shape in leg_shapes.items():
    obj = doc.addObject("Part::Feature", f"{name}_Leg")
    obj.Shape = shape
    leg_objs[name] = obj

doc.recompute()

print(f"BottomDeck solid valid: {bottom_deck_shape.isValid()}")
print(f"TopDeck solid valid: {top_deck_shape.isValid()}")
for name, shape in leg_shapes.items():
    print(f"{name} leg valid: {shape.isValid()}")

all_shapes = [bottom_deck_shape, top_deck_shape] + list(leg_shapes.values())
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

# Leg vs. leg (do the 4 hip-bracket-and-leg footprints clear each other?)
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
    print(f"  {name} vs TopDeck:    {'CLASH' if td_vol > TOL else 'clear'} ({td_vol:.0f} mm^3) "
          f"-- hip bracket is {params.HIP_Z_LENGTH:.0f}mm tall and stands in Z=[{HIP_BOTTOM_Z:.0f}, "
          f"{HIP_BOTTOM_Z + params.HIP_Z_LENGTH:.0f}]; it passes through the top deck's own "
          f"Z=[{DECK_GAP:.0f}, {DECK_GAP + params.BODY_PLATE_THICKNESS:.0f}] via the hip-clearance "
          f"pocket build_top_deck.py now cuts there, rather than colliding with solid material.")

# Standoff posts (un-modeled hardware -- probe cylinders standing in for them, see
# module docstring) vs. each leg's hip bracket footprint.
print("\nStandoff-post probes (un-modeled hardware, see docstring) vs. legs:")
standoff_positions = [(sx, sy) for sx in (-params.STANDOFF_X, params.STANDOFF_X)
                                for sy in (-params.STANDOFF_Y, params.STANDOFF_Y)]
any_standoff_clash = False
for sx, sy in standoff_positions:
    probe = Part.makeCylinder(params.STANDOFF_HOLE_DIA / 2.0, params.STANDOFF_HEIGHT,
                               App.Vector(sx, sy, HIP_BOTTOM_Z), App.Vector(0, 0, 1))
    for name, shape in leg_shapes.items():
        vol = probe.common(shape).Volume
        if vol > TOL:
            any_standoff_clash = True
            print(f"  standoff ({sx:.0f},{sy:.0f}) vs {name}: CLASH ({vol:.0f} mm^3 of the "
                  f"standoff's own column falls inside {name}'s hip bracket)")

if not any_standoff_clash:
    print("  no standoff-post/leg clashes found.")

print("\n=== SUMMARY ===")
print(f"Leg-vs-leg footprints: {'CLASH FOUND' if any_leg_clash else 'clear'}.")
print(f"Leg-vs-decks: {'CLASH FOUND -- see above' if any_deck_clash else 'clear'} -- each hip "
      f"bracket's {params.HIP_Z_LENGTH:.0f}mm-tall body passes through build_top_deck.py's "
      f"hip-clearance pocket rather than colliding with it.")
print(f"Standoff posts: {'CLASH FOUND -- see above' if any_standoff_clash else 'clear'} -- "
      f"STANDOFF_X was moved from 150mm to 100mm (see params.py) specifically so it falls "
      f"outside every hip bracket's 112x80mm footprint, not just its small bolt-circle "
      f"pattern.")
if not any_leg_clash and not any_deck_clash and not any_standoff_clash:
    print("\nAssembly is fully interference-free: every part fits together as modeled.")

doc.saveAs(f"{out_dir}/assembled_robot.FCStd")
Part.export(list(deck_objs.values()) + list(leg_objs.values()), f"{out_dir}/assembled_robot.step")
print("\nSaved: assembled_robot.FCStd, assembled_robot.step")
