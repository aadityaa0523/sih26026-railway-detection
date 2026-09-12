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

import params


def chassis_envelope(z0=0.0):
    """The v3 envelope contract (params.py V3 SPEC) as one solid, in the body frame with the
    hip ab/ad axis at Z=z0: the body box plus the front and rear nose boxes. Chassis parts
    live inside this (or above z0+LEG_MAX_Z); leg modules must never enter it."""
    hx, top = params.BASE_TO_HIP_X, z0 + params.LEG_MAX_Z
    body_bot = z0 - params.BODY_MAX_BELOW_HIP
    nose_bot = z0 - params.NOSE_MAX_BELOW_HIP
    env = Part.makeBox(2 * hx, 2 * params.BODY_MAX_HALF_W, top - body_bot,
                       App.Vector(-hx, -params.BODY_MAX_HALF_W, body_bot))
    for x0 in (hx, -hx - params.NOSE_MAX_X):
        env = env.fuse(Part.makeBox(params.NOSE_MAX_X, 2 * params.NOSE_HALF_W, top - nose_bot,
                                    App.Vector(x0, -params.NOSE_HALF_W, nose_bot)))
    return env


def leg_zone(z0=0.0, reach=600.0):
    """Where the leg modules may move: everything below z0+LEG_MAX_Z that is outside
    chassis_envelope(). Any chassis solid with a non-zero .common() against this breaks the
    contract."""
    top = z0 + params.LEG_MAX_Z
    zone = Part.makeBox(2 * reach, 2 * reach, reach + params.LEG_MAX_Z,
                        App.Vector(-reach, -reach, top - reach - params.LEG_MAX_Z))
    return zone.cut(chassis_envelope(z0))


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


def build_sg90_mount_block(w, d, t, sg90_body_l, sg90_body_w, tab_spacing, tab_hole_dia,
                            shaft_hole_dia, mount_inset, standoff_hole_dia, cut_corner_bolts):
    """A w x d x t block with a shallow top-face SG90 servo pocket + 2 tab holes + a center
    shaft-clearance hole -- shared by build_camera_pan_tilt.py (pan + tilt mounts) and
    build_sniffer_arm.py (dip + swing mounts), improvement 4. Factored out once the same
    "recess a micro servo into a small mounting block" logic appeared in both new scripts,
    same reasoning as this module's original two helpers.

    `cut_corner_bolts`: also cut the 4-corner mount_inset bolt pattern used to bolt this
    block down to whatever it sits on (the deck/mast plate for a base block; left False for
    a block that instead gets bolted to FROM the arm/yoke above/below it).
    """
    block = Part.makeBox(w, d, t, App.Vector(-w / 2.0, -d / 2.0, 0))
    pocket = Part.makeBox(sg90_body_l, sg90_body_w, t - 2.0,
                           App.Vector(-sg90_body_l / 2.0, -sg90_body_w / 2.0, 2.0))
    block = block.cut(pocket)
    for x in (-tab_spacing / 2.0, tab_spacing / 2.0):
        hole = Part.makeCylinder(tab_hole_dia / 2.0, t, App.Vector(x, 0, 0), App.Vector(0, 0, 1))
        block = block.cut(hole)
    shaft_hole = Part.makeCylinder(shaft_hole_dia / 2.0, t, App.Vector(0, 0, 0), App.Vector(0, 0, 1))
    block = block.cut(shaft_hole)
    if cut_corner_bolts:
        for dx in (-(w / 2.0 - mount_inset), w / 2.0 - mount_inset):
            for dy in (-(d / 2.0 - mount_inset), d / 2.0 - mount_inset):
                hole = Part.makeCylinder(standoff_hole_dia / 2.0, t, App.Vector(dx, dy, 0), App.Vector(0, 0, 1))
                block = block.cut(hole)
    return block


def _rects_overlap(cx1, cy1, hw1, hh1, cx2, cy2, hw2, hh2):
    """True if two axis-aligned XY rectangles (center + half-width/half-height) overlap."""
    return abs(cx1 - cx2) < (hw1 + hw2) and abs(cy1 - cy2) < (hh1 + hh2)


def load_step_solids(path):
    """Read a STEP file and return its individual solids as a plain list (Part.Shape.Solids),
    NEVER the raw multi-solid Compound `Part.Shape().read()` hands back. FreeCAD 1.1's
    Part.Shape.common() silently returns 0 volume against a multi-solid Compound (a confirmed
    bug, see README) -- parts this project mates edge-to-edge into one physical unit (e.g. a
    leg's hip+upper+lower) are `.fuse()`d into one genuine solid by their own assembly code;
    parts that are genuinely SEPARATE, non-touching solids exported together for convenience
    (a deck + its lid, the 4 body-wall panels, the payload envelopes) can't be turned into one
    real solid by fuse() at all (fuse of disjoint solids is still a multi-solid compound
    internally) -- so those are kept as separate list entries instead, each a real solid, so
    every `.common()` call in assemble_robot.py's interference check operates on a genuine
    solid either way.
    """
    shape = Part.Shape()
    shape.read(path)
    return list(shape.Solids)


def fillet_vertical_edges(shape, radius):
    """Fillet every vertical (Z-parallel) edge of `shape` by `radius`. Reused (Chassis v2)
    by build_bottom_deck.py and build_top_deck.py (outer plate corners, R15) and
    build_top_deck.py's hip-pocket cutter (inner corners, R8) and build_hip_bracket.py's
    housing (outer corners, R6) -- 4+ call sites, past this file's own 3+ reuse threshold.
    Per the project's fillet-robustness convention, filleting is done on a plain box/cutter
    BEFORE any other feature is cut into it, not on a feature-riddled final shape -- callers
    are expected to call this first. Falls back to returning the unfilleted shape (rather
    than raising) if FreeCAD's makeFillet throws, so a fillet failure never blocks a build.
    """
    verticals = [e for e in shape.Edges
                 if e.BoundBox.XLength < 1e-6 and e.BoundBox.YLength < 1e-6 and e.BoundBox.ZLength > 1e-6]
    if not verticals:
        return shape
    try:
        return shape.makeFillet(radius, verticals)
    except Exception as exc:
        print(f"  WARNING: fillet_vertical_edges(radius={radius}) failed ({exc}) -- "
              f"returning the unfilleted shape instead of crashing the build.")
        return shape


def build_hex_standoff(across_flats, height, hole_dia, origin):
    """A real M3 hex standoff SOLID (Chassis v2 item 6) -- across_flats (e.g. 5.5mm, standard
    M3 hex standoff hardware, params.STANDOFF_HEX_ACROSS_FLATS) x height, with a through-bore
    for the M3 bolt. Reused 4x (one per inter-deck standoff position) by assemble_robot.py,
    replacing the old un-modeled probe-cylinder stand-in.
    `origin`: App.Vector, the standoff's own base center (its own local Z=0), bore along +Z.
    """
    # Regular hexagon, flat-to-flat = across_flats -> circumradius = across_flats / sqrt(3).
    r = across_flats / math.sqrt(3)
    pts = []
    for i in range(6):
        angle = math.radians(60 * i + 30)   # +30 deg so a flat (not a vertex) faces +X
        pts.append(App.Vector(origin.x + r * math.cos(angle), origin.y + r * math.sin(angle), origin.z))
    pts.append(pts[0])
    wire = Part.makePolygon(pts)
    face = Part.Face(wire)
    hex_solid = face.extrude(App.Vector(0, 0, height))
    bore = Part.makeCylinder(hole_dia / 2.0, height, origin, App.Vector(0, 0, 1))
    return hex_solid.cut(bore)


def build_box_wall(length, height, thickness, flange, hole_dia, hole_inset):
    """A straight structural wall/bulkhead panel (Chassis v2 item 5): a vertical web
    (length x thickness x height, centered on its own local X=0) whose OUTER face sits at
    local y=0 (this is the edge that sits flush with the deck's own outer edge), with a
    WALL_FLANGE-wide mounting foot continuing INWARD (local +y) from the web at both the
    bottom (local Z=0..thickness) and top (local Z=height-thickness..height) -- a flat tab a
    real bolted/bonded 3D-printed panel would carry, not a bent-sheet flange. Reused 4x (2
    side walls + front/rear bulkheads) by build_body_walls.py -- callers rotate/translate
    this local frame (local +y = inward) into its final global position: a side wall at the
    +Y deck edge needs a Y-mirror (local +y=inward=global -Y) before translating; a side wall
    at the -Y edge needs only a translate (local +y=inward=global +y already); a bulkhead
    rotates +-90 degrees about Z first. See build_body_walls.py for the actual placement math.

    Returns (shape, hole_centers) -- hole_centers is a list of 4 local (x, y, z) points (2 per
    flange, inset `hole_inset` from each end) where an M3 bolt bore is cut through both this
    wall's own flange and the matching deck it bolts to.
    """
    web = Part.makeBox(length, thickness, height, App.Vector(-length / 2.0, 0, 0))
    flange_bot = Part.makeBox(length, flange, thickness, App.Vector(-length / 2.0, thickness, 0))
    flange_top = Part.makeBox(length, flange, thickness,
                               App.Vector(-length / 2.0, thickness, height - thickness))
    shape = web.fuse(flange_bot).fuse(flange_top)

    fy = thickness + flange / 2.0
    holes = []
    for x in (-length / 2.0 + hole_inset, length / 2.0 - hole_inset):
        for z in (0.0, height - thickness):
            holes.append((x, fy, z))
    for x, y, z in holes:
        hole = Part.makeCylinder(hole_dia / 2.0, thickness, App.Vector(x, y, z), App.Vector(0, 0, 1))
        shape = shape.cut(hole)
    return shape, holes


def wall_flange_hole_xy(side_wall_length, bulkhead_length, bulkhead_x, base_y_length, hole_inset,
                         wall_thickness, wall_flange):
    """Global (x, y) positions of the box-section body walls' own flange bolt holes (Chassis
    v2 item 5) -- 8 total, 2 per wall x 4 walls (top and bottom flange share the same XY, only
    Z differs). Shared by build_body_walls.py (builds the walls) AND both deck scripts (which
    must cut MATCHING holes) so the 3 files can't drift apart on the hole pattern -- past this
    file's own 3+ reuse threshold.

    Each wall's web OUTER face sits flush at the deck's own edge (Y=+-base_y_length/2 for a
    side wall, X=+-bulkhead_x for a bulkhead); the flange -- and so its bolt holes -- sits
    INWARD of that edge by `wall_thickness + wall_flange/2` (see build_box_wall's own
    docstring for the local-frame derivation this mirrors).
    """
    inset_from_edge = wall_thickness + wall_flange / 2.0
    half_y = base_y_length / 2.0 - inset_from_edge
    bx = bulkhead_x - inset_from_edge
    pts = []
    for y in (half_y, -half_y):
        for x in (-side_wall_length / 2.0 + hole_inset, side_wall_length / 2.0 - hole_inset):
            pts.append((x, y))
    for x in (bx, -bx):
        for y in (-bulkhead_length / 2.0 + hole_inset, bulkhead_length / 2.0 - hole_inset):
            pts.append((x, y))
    return pts


def build_deck_ribs(rib_specs, keepouts, thickness, rib_width, rib_height, z_dir=1):
    """Build a fused Part.Shape of perpendicular stiffening ribs for a deck plate (improvement
    6, "Ribbed decks" -- standard lightweighting/stiffening technique, no FEA run).

    `rib_specs`: list of (axis, position, span_start, span_end) -- axis 'x' means a rib
    running along Y at fixed X=position spanning Y in [span_start, span_end]; axis 'y' means
    a rib running along X at fixed Y=position spanning X in [span_start, span_end].
    `keepouts`: list of (cx, cy, half_w, half_h) rectangles (existing holes/pockets/mounts)
    ribs must not overlap -- each candidate rib's own XY bounding box is checked against
    every keepout (real geometric check, not an assumption) and SKIPPED (with a printed
    warning) if it would overlap one, rather than silently cutting through a mount.
    `z_dir`: +1 to project ribs upward from the plate's top face (Z=thickness upward),
    -1 to project downward from the plate's bottom face (Z=0 downward).

    Returns (fused_ribs_shape_or_None, n_built, n_skipped).
    """
    z0 = thickness if z_dir > 0 else -rib_height
    ribs = []
    skipped = 0
    for axis, pos, s0, s1 in rib_specs:
        length = s1 - s0
        if axis == 'x':
            cx, cy = pos, (s0 + s1) / 2.0
            hw, hh = rib_width / 2.0, length / 2.0
            origin = App.Vector(pos - rib_width / 2.0, s0, z0)
            box = Part.makeBox(rib_width, length, rib_height, origin)
        elif axis == 'y':
            cx, cy = (s0 + s1) / 2.0, pos
            hw, hh = length / 2.0, rib_width / 2.0
            origin = App.Vector(s0, pos - rib_width / 2.0, z0)
            box = Part.makeBox(length, rib_width, rib_height, origin)
        else:
            raise ValueError(f"axis must be 'x' or 'y', got {axis!r}")

        clash = next((k for k in keepouts if _rects_overlap(cx, cy, hw, hh, *k)), None)
        if clash is not None:
            print(f"  SKIPPED rib axis={axis} pos={pos:.0f} span=[{s0:.0f},{s1:.0f}] -- "
                  f"overlaps keepout {clash}")
            skipped += 1
            continue
        ribs.append(box)

    if not ribs:
        return None, 0, skipped
    fused = ribs[0]
    for r in ribs[1:]:
        fused = fused.fuse(r)
    return fused, len(ribs), skipped
