"""
Parametric pan-tilt camera/thermal head for the quadruped (improvement 4), built in
FreeCAD's Python API. Bolts to build_top_deck.py's mast mounting plate (the old static
12-degree-tilted camera/thermal face was REMOVED from that script -- see its docstring).

Real precedent: this is the project's answer to "why no active camera aiming" -- real
deployed quadrupeds (Spot, ANYmal) carry actively-aimed sensor heads, not fixed ones. Uses
2x SG90 micro servos (real, ubiquitous, well-documented spec, see params.py) -- one for
pan (rotates the whole head about the mast's vertical/Z axis), one for tilt (rotates just
the camera/thermal face about a horizontal axis).

NOT a fully kinematic mechanism -- an honest simplification (explicitly allowed by the
brief): servo pockets are simplified recesses (real SG90 shaft/spline geometry is not
modeled), and instead of simulating continuous motion, this script builds TWO static
poses -- NEUTRAL (pan=0, tilt=0) and EXTENDED (pan=PANTILT_PAN_RANGE_DEG,
tilt=PANTILT_TILT_RANGE_DEG) -- as two separate rigid solids, demonstrating the range of
motion. assemble_robot.py uses the NEUTRAL pose (pan_tilt_head.step) as part of the
whole-robot model; the EXTENDED pose (pan_tilt_head_extended.step) is a standalone
demonstration only, not itself included in the whole-robot interference check.

Structure (base -> yoke -> tilt mount -> camera/thermal face):
  - Base: bolts to the mast's PANTILT_BASE_W x PANTILT_BASE_D mounting plate (same 4-hole
    inset pattern), with a shallow top-face pocket + 2 tab holes recessing the PAN servo.
  - Yoke: a simple post rising PANTILT_LINK_LENGTH from the base's top-center (where the
    pan servo's horn would be) -- this is what physically turns when the pan servo turns.
  - Tilt mount: an identical shallow-pocket bracket on top of the yoke, recessing the TILT
    servo the same way the base recesses the pan servo.
  - Camera/thermal face: the SAME Pi Camera + AMG8833 hole pattern the old top_deck mast
    face used, now standing on the tilt mount's front edge -- this is what physically tilts
    when the tilt servo turns.
"""
import FreeCAD as App
import Part

import params
from geometry_helpers import build_sg90_mount_block

out_dir = params.CAD_DIR

W, D, T = params.PANTILT_BASE_W, params.PANTILT_BASE_D, params.PANTILT_BASE_T
MOUNT_INSET = 6.0   # mm, matches build_top_deck.py's own mast mounting-plate inset
SHAFT_HOLE_DIA = 6.0   # mm, design choice, clears an SG90 spline + horn boss


def _servo_mount_block(w, d, t, cut_corner_bolts):
    return build_sg90_mount_block(w, d, t, params.SG90_BODY_L, params.SG90_BODY_W,
                                   params.SG90_TAB_SPACING, params.SG90_TAB_HOLE_DIA,
                                   SHAFT_HOLE_DIA, MOUNT_INSET, params.STANDOFF_HOLE_DIA,
                                   cut_corner_bolts)


def _camera_thermal_face():
    """The Pi Camera + AMG8833 mounting face -- same hole pattern build_top_deck.py's old
    static mast face used to cut, moved here now that it lives on the pan-tilt head instead.
    Built flat, standing on the XZ plane (normal along +Y, "facing forward") at the origin.
    """
    plate_w = params.PICAM_PCB_L + params.AMG8833_L + 6.0
    plate_h = max(params.PICAM_PCB_W, params.AMG8833_W) + 6.0
    ft = params.MAST_FACE_THICKNESS
    face = Part.makeBox(ft, plate_w, plate_h, App.Vector(-ft / 2.0, -plate_w / 2.0, -plate_h / 2.0))

    y_cam = -plate_w / 2.0 + params.PICAM_PCB_L / 2.0 + 3.0
    y_amg = plate_w / 2.0 - params.AMG8833_L / 2.0 - 3.0
    cam_spacing = params.PICAM_PCB_L - 6.0
    amg_spacing = params.AMG8833_L - 6.0
    for y in (y_cam - cam_spacing / 2.0, y_cam + cam_spacing / 2.0):
        hole = Part.makeCylinder(params.PICAM_HOLE_DIA / 2.0, ft, App.Vector(-ft / 2.0, y, 0), App.Vector(1, 0, 0))
        face = face.cut(hole)
    for y in (y_amg - amg_spacing / 2.0, y_amg + amg_spacing / 2.0):
        hole = Part.makeCylinder(params.AMG8833_HOLE_DIA / 2.0, ft, App.Vector(-ft / 2.0, y, 0), App.Vector(1, 0, 0))
        face = face.cut(hole)
    return face, plate_h


def build_pose(pan_deg, tilt_deg):
    """Build one static pose of the full pan-tilt head. Returns (shape, base_top_z) --
    base_top_z is where this head's base sits on the mast mounting plate (Z=0 locally)."""
    base = _servo_mount_block(W, D, T, cut_corner_bolts=True)

    yoke = Part.makeBox(15.0, 15.0, params.PANTILT_LINK_LENGTH,
                         App.Vector(-7.5, -7.5, T))

    tilt_mount = _servo_mount_block(W, D, T, cut_corner_bolts=False)
    tilt_mount.translate(App.Vector(0, 0, T + params.PANTILT_LINK_LENGTH))

    face, face_h = _camera_thermal_face()
    face_x = D / 2.0 - params.MAST_FACE_THICKNESS / 2.0 + 2.0   # sits just proud of the tilt mount's front edge
    face_z = T + params.PANTILT_LINK_LENGTH + T + face_h / 2.0 + 2.0
    face.translate(App.Vector(face_x, 0, face_z))

    # Tilt: rotate the face about the tilt servo's axis (local X, through the tilt mount's
    # own center) BEFORE composing with the pan rotation below.
    tilt_pivot = App.Vector(0, 0, T + params.PANTILT_LINK_LENGTH + T / 2.0)
    face.rotate(tilt_pivot, App.Vector(1, 0, 0), tilt_deg)

    moving = yoke.fuse(tilt_mount).fuse(face)
    # Pan: rotate everything above the base about the pan servo's axis (local Z, through
    # the base's own top-center).
    moving.rotate(App.Vector(0, 0, T), App.Vector(0, 0, 1), pan_deg)

    return base.fuse(moving), T


def _build_and_export(pan_deg, tilt_deg, name, doc_name, label):
    doc = App.newDocument(doc_name)
    shape, base_top_z = build_pose(pan_deg, tilt_deg)
    part = doc.addObject("Part::Feature", "PanTiltHead")
    part.Shape = shape
    doc.recompute()

    bbox = shape.BoundBox
    print(f"{label} (pan={pan_deg:.0f}deg, tilt={tilt_deg:.0f}deg) built OK. "
          f"Bounding box (mm): X={bbox.XLength:.1f} Y={bbox.YLength:.1f} Z={bbox.ZLength:.1f}")
    print(f"Volume: {shape.Volume:.0f} mm^3   Solid valid: {shape.isValid()}")

    doc.saveAs(f"{out_dir}/{name}.FCStd")
    Part.export([part], f"{out_dir}/{name}.step")
    Part.export([part], f"{out_dir}/{name}.stl")
    print(f"Saved: {name}.FCStd, {name}.step, {name}.stl")
    return shape, base_top_z


# freecadcmd sets __name__ to the script's own module name, not "__main__" -- no guard,
# same convention as every other script in this directory.
print("Pan-tilt camera/thermal head -- 2x SG90 (params.py), NOT a fully kinematic "
      "mechanism, see module docstring. Building NEUTRAL and EXTENDED demonstration poses.\n")
_build_and_export(0.0, 0.0, "pan_tilt_head", "pan_tilt_head", "NEUTRAL pose")
print()
_build_and_export(params.PANTILT_PAN_RANGE_DEG, params.PANTILT_TILT_RANGE_DEG,
                   "pan_tilt_head_extended", "pan_tilt_head_extended", "EXTENDED pose (demo only)")
