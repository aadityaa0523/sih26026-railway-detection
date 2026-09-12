"""
Small geometry helpers factored out once the same pocket/bolt-circle cutting logic
started showing up in 3+ places (upper_leg knee end, lower_leg knee end, hip_bracket
horn face / servo pocket). Not a general-purpose CAD library on purpose -- both
helpers hardcode the same "holes lie in the local XZ plane, bored through +Y" axis
convention used by every part script in this project so callers stay one-liners.
"""
import math

import FreeCAD as App
import Part


def cut_bolt_circle(shape, cx, z_center, bracket_width, thickness, hole_dia, bolt_circle_dia, n=4):
    """Cut a center clearance hole plus an n-hole bolt circle around it, all bored
    through +Y starting at y=0. Mirrors the identical logic previously duplicated in
    build_upper_leg.py's knee end and build_lower_leg.py's knee end -- the same
    standard-servo-horn interface reused at both the knee and hip joints.
    Holes whose X falls outside (0, bracket_width) are skipped (would clip the part's edge).
    """
    center_hole = Part.makeCylinder(hole_dia / 2.0, thickness, App.Vector(cx, 0, z_center), App.Vector(0, 1, 0))
    shape = shape.cut(center_hole)
    for i in range(n):
        angle = math.radians(i * 360.0 / n)
        x = cx + (bolt_circle_dia / 2.0) * math.cos(angle)
        z = z_center + (bolt_circle_dia / 2.0) * math.sin(angle)
        if 0 < x < bracket_width:
            hole = Part.makeCylinder(1.6, thickness,  # M3 clearance
                                      App.Vector(x, 0, z), App.Vector(0, 1, 0))
            shape = shape.cut(hole)
    return shape


def cut_servo_pocket_with_tabs(shape, bracket_width, bracket_thickness, pocket_z_start,
                                servo_w, servo_h, tab_spacing, tab_hole_dia):
    """Recess a servo body into `shape`: a pocket_z_start..pocket_z_start+servo_h slot,
    centered in X, cut the full bracket_thickness through Y, plus the 2 standard
    mounting-tab bolt holes straddling the pocket at its mid-height. Mirrors the
    hip-end pocket previously duplicated inline in build_upper_leg.py.
    """
    pocket_margin = (bracket_width - servo_w) / 2.0
    pocket = Part.makeBox(servo_w, bracket_thickness, servo_h,
                           App.Vector(pocket_margin, 0, pocket_z_start))
    shape = shape.cut(pocket)
    hole_z = pocket_z_start + servo_h / 2.0
    for x_offset in (-tab_spacing / 2.0, tab_spacing / 2.0):
        x = bracket_width / 2.0 + x_offset
        if 0 < x < bracket_width:
            hole = Part.makeCylinder(tab_hole_dia / 2.0, bracket_thickness,
                                      App.Vector(x, 0, hole_z), App.Vector(0, 1, 0))
            shape = shape.cut(hole)
    return shape
