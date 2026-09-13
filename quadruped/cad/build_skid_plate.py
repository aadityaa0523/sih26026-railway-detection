"""
Skid plate for the quadruped's bottom deck -- CHASSIS V3 (SpotMicro-scale resize,
2026-09-12), built in FreeCAD's Python API.

Kept (task item 8 allows dropping it with a one-line reason, but it's still worth keeping):
the new chassis is smaller, but the bottom deck's belly is still the one flat, low surface
that would scrape on uneven ground, curbs, or rail-yard ballast during underframe-inspection
duty -- same real justification as before. Material choice unchanged: UHMW or HDPE, a
design choice but a real, appropriate one for exactly this ground-contact application.

Placement: centered under the bottom deck, mounted BELOW it (Z<0) so it has no interference
constraint from the deck's own above-surface mounts (ab/ad housings, standoffs, sniffer
boom) -- sized generously within the V3 SPEC BODY_BOX's own X/Y range instead.

CHASSIS V3 fit: HIP_AXIS_Z=32mm puts the V3 SPEC envelope's own BODY_BOX floor at
Z=HIP_AXIS_Z-BODY_MAX_BELOW_HIP=-3mm -- exactly matching a 3mm-thick skid plate mounted
flush below the deck's own underside (Z=0), so it fills the envelope's own margin exactly,
no wasted clearance and no violation.
"""
import FreeCAD as App
import Part

import params

L = params.SKID_PLATE_L      # mm, along X
W = params.SKID_PLATE_W      # mm, along Y
T = params.SKID_PLATE_THICKNESS

doc = App.newDocument("skid_plate")

plate = Part.makeBox(L, W, T, App.Vector(-L / 2.0, -W / 2.0, -T))

inset = 10.0   # mm, design choice, consistent with ABAD_MOUNT_INSET elsewhere
for dx in (-L / 2.0 + inset, L / 2.0 - inset):
    for dy in (-W / 2.0 + inset, W / 2.0 - inset):
        hole = Part.makeCylinder(params.SKID_PLATE_HOLE_DIA / 2.0, T,
                                  App.Vector(dx, dy, -T), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

part = doc.addObject("Part::Feature", "SkidPlate")
part.Shape = plate
doc.recompute()

bbox = plate.BoundBox
print(f"SkidPlate (CHASSIS V3) built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print("Material: UHMW or HDPE (design choice) -- low-friction, high-wear-resistance, "
      "standard for RC-crawler/rover ground-contact skid plates.")

body_box_floor = params.HIP_AXIS_Z - params.BODY_MAX_BELOW_HIP
print(f"Sits at Z=[{bbox.ZMin:.1f},{bbox.ZMax:.1f}] -- BODY_BOX floor is "
      f"Z={body_box_floor:.1f}mm: {'flush, OK' if abs(bbox.ZMin - body_box_floor) < 0.01 else 'CHECK MARGIN'}.")

out_dir = params.CAD_DIR
doc.saveAs(f"{out_dir}/skid_plate.FCStd")
Part.export([part], f"{out_dir}/skid_plate.step")
Part.export([part], f"{out_dir}/skid_plate.stl")
print("Saved: skid_plate.FCStd, skid_plate.step, skid_plate.stl")
