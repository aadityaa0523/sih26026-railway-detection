"""
Shell/livery side panels for the quadruped's body (improvement 8, cosmetic, lowest
priority -- implemented LAST and kept deliberately simple per the brief).

PARTIAL IMPLEMENTATION, stated honestly: only the two body-deck side panels are modeled
here. Leg panels (covers over the exposed upper/lower leg brackets) are explicitly SKIPPED
-- the brief allows this ("a partial implementation... is acceptable") given this is the
lowest-priority, purely cosmetic improvement, and every structural improvement (1, 3, 5, 6,
7) plus the other two mechanisms (2, 4) were prioritized first.

Two simple flat panels (SHELL_PANEL_THICKNESS=2mm, cosmetic only, not structural) along the
+-Y outer edges of the deck-to-deck gap, mounted flush with the deck edge, spanning the
CLEAR mid-body gap between the front and hind hip-mount X-bands (X=+-119 to +-231mm) so they
don't clash with either hip bracket's own footprint (checked the same way every other new
part in this pass was checked -- see assemble_robot.py's interference check). Purpose: make
the framework read as a purpose-built enclosure rather than exposed brackets, per the brief.
Each panel's flat 200x50mm area comfortably fits the DECAL_W x DECAL_H (80x40mm) branding
decal area the brief asks for -- no extra geometry needed for that, a flat panel already
provides it.
"""
import FreeCAD as App
import Part

import params

out_dir = params.CAD_DIR

PANEL_L = 200.0   # mm, design choice -- spans the clear mid-body gap between the front/hind
                   # hip-mount X-bands (+-119 to +-231mm) with margin on both sides.
PANEL_H = params.STANDOFF_HEIGHT   # mm, spans the deck-to-deck gap height exactly.
T = params.SHELL_PANEL_THICKNESS

doc = App.newDocument("shell_panels")

panel_z0 = params.BODY_PLATE_THICKNESS   # sits on top of the bottom deck's own top surface
panels = []
for y_sign, name in ((1.0, "LeftPanel"), (-1.0, "RightPanel")):
    y0 = params.BASE_Y_LENGTH / 2.0 if y_sign > 0 else -params.BASE_Y_LENGTH / 2.0 - T
    panel = Part.makeBox(PANEL_L, T, PANEL_H, App.Vector(-PANEL_L / 2.0, y0, panel_z0))
    panels.append((name, panel))

objs = []
for name, shape in panels:
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    objs.append(obj)
doc.recompute()

for name, shape in panels:
    bbox = shape.BoundBox
    print(f"{name} built OK. Bounding box (mm): X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
    print(f"  Volume: {shape.Volume:.0f} mm^3   Solid valid: {shape.isValid()}")

print(f"\nDecal area check: each panel is {PANEL_L:.0f}x{PANEL_H:.0f}mm, comfortably fits "
      f"the {params.DECAL_W:.0f}x{params.DECAL_H:.0f}mm branding decal area.")
print("PARTIAL IMPLEMENTATION: body-deck side panels only -- leg panels explicitly SKIPPED, "
      "see module docstring.")

out_dir_step = f"{out_dir}/shell_panels.step"
doc.saveAs(f"{out_dir}/shell_panels.FCStd")
Part.export(objs, out_dir_step)
Part.export(objs, f"{out_dir}/shell_panels.stl")
print("Saved: shell_panels.FCStd, shell_panels.step, shell_panels.stl")
