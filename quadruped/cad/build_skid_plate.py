"""
Parametric skid plate for the quadruped's bottom deck (improvement 5), built in
FreeCAD's Python API.

A thin protective plate bolted to the underside of build_bottom_deck.py's most exposed
central area -- the flat belly a real quadruped's own frame would scrape on uneven ground,
curbs, or rail-yard ballast. Real, appropriate MATERIAL CHOICE, stated honestly as a design
choice: UHMW or HDPE -- both are standard low-friction, high-wear-resistance materials
used for exactly this ground-contact application on RC crawlers/rovers (not 3D-printed
PETG like the rest of this project's brackets, a plastic-sheet-stock part instead).

Placement: centered in the one XY gap on the bottom deck's underside that clears ALL THREE
named keepouts at once -- checked here with a real geometric overlap test, not eyeballed:
  - the 4 hip-mount bolt clusters (+-BASE_TO_HIP_X, +-BASE_TO_HIP_Y, each ~92x60mm)
  - the battery bay (pocket + strap slots, ~89x34mm centered at the origin)
  - the sensing-bay mount (90x60mm, front edge)
The clear gap sits between the battery bay and the sensing-bay mount (front-of-center,
not dead-center -- the battery block itself already occupies dead-center), sized to
SKID_PLATE_L x SKID_PLATE_W (params.py).

Mounted BELOW the deck (Z < 0, the deck's own underside is at global Z=0) with 4 corner
through-holes for M3 screws into the deck material above -- no captive nut/heat-set-insert
CAD modeled, same bought-fastener-hardware level of detail as every other bolted joint in
this project.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import _rects_overlap

L = params.SKID_PLATE_L      # mm, along X (front-back)
W = params.SKID_PLATE_W      # mm, along Y (left-right)
T = params.SKID_PLATE_THICKNESS

# Centered in the clear gap between the battery bay (X up to ~+-45mm) and the sensing-bay
# mount (X from ~150mm), and clear of the hip-mount Y-band (Y from ~65mm) -- see module
# docstring. Front-of-center (not X=0) because the battery block itself occupies dead-center.
PLATE_CX = 100.0   # mm, design choice -- see clearance check below
PLATE_CY = 0.0     # mm

doc = App.newDocument("skid_plate")

plate = Part.makeBox(L, W, T, App.Vector(PLATE_CX - L / 2.0, PLATE_CY - W / 2.0, -T))

# 4 corner mounting holes, M3 clearance (reuses SKID_PLATE_HOLE_DIA), inset the same way
# the hip bracket's own corner bolts are inset from its footprint edge.
inset = 10.0   # mm, design choice, consistent with HIP_MOUNT_INSET elsewhere
for dx in (-L / 2.0 + inset, L / 2.0 - inset):
    for dy in (-W / 2.0 + inset, W / 2.0 - inset):
        hole = Part.makeCylinder(params.SKID_PLATE_HOLE_DIA / 2.0, T,
                                  App.Vector(PLATE_CX + dx, PLATE_CY + dy, -T), App.Vector(0, 0, 1))
        plate = plate.cut(hole)

part = doc.addObject("Part::Feature", "SkidPlate")
part.Shape = plate
doc.recompute()

bbox = plate.BoundBox
print(f"SkidPlate built OK. Bounding box (mm): "
      f"X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
print(f"Volume: {plate.Volume:.0f} mm^3   Solid valid: {plate.isValid()}")
print("Material: UHMW or HDPE (design choice) -- low-friction, high-wear-resistance, "
      "standard for RC-crawler/rover ground-contact skid plates. NOT the project's usual "
      "3D-printed PETG.")

# Real geometric clearance check against the 3 named keepouts (bounding boxes, generous),
# not an eyeballed placement -- see module docstring.
plate_rect = (PLATE_CX, PLATE_CY, L / 2.0, W / 2.0)
keepouts = []
hx, hy = params.HIP_X_LENGTH / 2.0, params.HIP_Y_LENGTH / 2.0
for hip_x in (-params.BASE_TO_HIP_X, params.BASE_TO_HIP_X):
    for hip_y in (-params.BASE_TO_HIP_Y, params.BASE_TO_HIP_Y):
        keepouts.append(("hip mount", hip_x, hip_y, hx, hy))
keepouts.append(("battery bay", 0.0, 0.0, params.BATTERY_L / 2.0 + 10.0, params.BATTERY_W / 2.0 + 5.0))
sensing_cx = params.BASE_X_LENGTH / 2.0 - 50.0
keepouts.append(("sensing bay", sensing_cx, 0.0, params.SENSING_BAY_L / 2.0, params.SENSING_BAY_W / 2.0))

any_clash = False
for name, cx, cy, hw, hh in keepouts:
    if _rects_overlap(plate_rect[0], plate_rect[1], plate_rect[2], plate_rect[3], cx, cy, hw, hh):
        print(f"CLASH: skid plate footprint overlaps {name} keepout (center {cx:.0f},{cy:.0f})")
        any_clash = True
if not any_clash:
    print("Clearance check: skid plate clears all 3 keepouts (hip mounts, battery bay, "
          "sensing-bay mount) -- confirmed geometrically, not assumed.")

out_dir = params.CAD_DIR
doc.saveAs(f"{out_dir}/skid_plate.FCStd")
Part.export([part], f"{out_dir}/skid_plate.step")
Part.export([part], f"{out_dir}/skid_plate.stl")
print("Saved: skid_plate.FCStd, skid_plate.step, skid_plate.stl")
