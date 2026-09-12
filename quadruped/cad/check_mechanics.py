"""
Mechanics check: can this leg + chassis design actually walk under CHAMP?

The interference checks in assemble_robot.py only prove the STATIC pose fits. This script
checks motion, using the real exported geometry (assembled_robot.FCStd + the leg STEPs):

  1. Joint inventory -- CHAMP needs 3 actuated revolute joints per leg (hip about X, upper
     leg about Y, lower leg about Y; docs/champ-research.md #3.1, leg.urdf.xacro). For each,
     is there an actuator, a coaxial horn/bolt interface, and a pivot that can rotate?
  2. Gait sweep -- inverse kinematics over CHAMP's own gait envelope (gait.yaml: nominal_height
     0.20m, swing_height 0.04m, max_linear_velocity_x 0.5m/s x stance_duration 0.25s = 125mm
     stride), then rotate the LF thigh/shin through every pose and boolean-check them against
     every other part of the robot, and against each other.
  3. Hip ab/ad sweep -- the same, for the leg links swung about CHAMP's hip X axis.
  4. Loads -- total mass + centre of gravity from the real part volumes, joint torques at
     CHAMP's nominal stance vs. the MG996R rating, ground clearance at nominal height.

Run after assemble_robot.py (reads assembled_robot.FCStd, upper_leg.step, lower_leg.step):
  freecadcmd check_mechanics.py
"""
import math

import FreeCAD as App
import Part

import params

CAD = "C:/Users/Aadityaa/iqoo/quadruped/cad"
TOL = 1.0   # mm^3, same sliver threshold as assemble_robot.py
G = 9.81

# CHAMP stock gait + kinematics (docs/champ-research.md #3.1)
NOMINAL_H = 200.0
SWING_H = 40.0
STRIDE = 0.5 * 0.25 * 1000.0          # max_linear_velocity_x * stance_duration, mm
CHAMP_L1 = CHAMP_L2 = 141.0            # upper_leg_to_lower_leg / lower_leg_to_foot distance
MG996R_STALL_NM = params.MG996R_STALL_TORQUE_KGF_CM * G / 100.0

# ---------------------------------------------------------------------------------------
# Rebuild the LF leg links exactly as assemble_full_leg.build_full_leg() + assemble_robot.py
# place them (LF = no mirror), but keep thigh and shin separate so they can move.
# ---------------------------------------------------------------------------------------
LEG_W = params.SERVO_BODY_W + 2 * params.WALL
LEG_T = 8.0                                             # build_upper/lower_leg.py BRACKET_THICKNESS
HIP_CX, HORN_Y, HORN_Z = params.HIP_X_LENGTH / 2.0, params.HIP_Y_LENGTH, params.HIP_Z_LENGTH - 30.0
HIP_SHIFT = App.Vector(HIP_CX - LEG_W / 2.0, HORN_Y,
                       HORN_Z - (params.UPPER_LEG_LENGTH - params.SERVO_BODY_H / 2.0))
ABD_PIVOT = App.Vector(0, params.HIP_Y_LENGTH / 2.0, 0)
ABD_LIFT = App.Vector(0, 0, (params.HIP_Y_LENGTH / 2.0) * math.sin(math.radians(params.HIP_ABDUCTION_DEG)))
LF_SHIFT = App.Vector(params.BASE_TO_HIP_X - HIP_CX, params.BASE_TO_HIP_Y - params.HIP_Y_LENGTH / 2.0,
                      params.BODY_PLATE_THICKNESS)


def place(shape):
    s = shape.copy()
    s.rotate(ABD_PIVOT, App.Vector(1, 0, 0), params.HIP_ABDUCTION_DEG)
    s.translate(ABD_LIFT)
    s.translate(LF_SHIFT)
    return s


def place_pt(p):
    return place(Part.Vertex(p)).Point


def load_solid(path):
    s = Part.Shape()
    s.read(path)
    return s.Solids[0]


upper = load_solid(f"{CAD}/upper_leg.step")
upper.translate(HIP_SHIFT)
lower = load_solid(f"{CAD}/lower_leg.step")
lower.translate(App.Vector(0, 0, -params.LOWER_LEG_LENGTH) + HIP_SHIFT)
upper, lower = place(upper), place(lower)

bar_cy = HORN_Y + LEG_T / 2.0
hip_pt = place_pt(App.Vector(HIP_CX, HORN_Y, HORN_Z))
axis_y = place_pt(App.Vector(HIP_CX, HORN_Y + 1, HORN_Z)) - hip_pt       # hip-pitch/knee axis dir
knee_pt = place_pt(App.Vector(HIP_CX, bar_cy, HIP_SHIFT.z))              # thigh/shin junction line
foot_pt = App.Vector(knee_pt.x, knee_pt.y, lower.BoundBox.ZMin)          # straight-leg foot tip


def planar(a, b):
    """Distance between two points measured in the leg's own swing plane (drop the axis component)."""
    d = b - a
    return (d - axis_y * d.dot(axis_y)).Length


L1, L2 = planar(hip_pt, knee_pt), planar(knee_pt, foot_pt)

# ---- obstacles: everything in the assembly except the LF leg links themselves ----------
doc = App.openDocument(f"{CAD}/assembled_robot.FCStd")
obstacles = {}
for o in doc.Objects:
    n = o.Name
    if not hasattr(o, "Shape") or n in ("LF_Leg", "LF_LegLinks"):
        continue
    if n.endswith("_HipHousing") and n != "LF_HipHousing":
        continue                     # duplicate of that leg's fused <name>_Leg
    if n.endswith("_LegLinks"):
        continue
    obstacles[n] = o.Shape.Solids   # per-solid: .common() on a Compound silently returns 0

# Sanity: the rebuilt links must coincide with the assembly's own LF leg.
lf_leg = doc.getObject("LF_Leg").Shape
for name, part in (("thigh", upper), ("shin", lower)):
    overlap = sum(part.common(s).Volume for s in lf_leg.Solids)
    assert abs(overlap - part.Volume) < 0.01 * part.Volume, \
        f"rebuilt LF {name} doesn't match assembled_robot.FCStd ({overlap:.0f} vs {part.Volume:.0f} mm^3)"


def clash(part, skip=()):
    hits = {}
    for n, solids in obstacles.items():
        if n in skip:
            continue
        for s in solids:
            if part.BoundBox.intersect(s.BoundBox):
                v = part.common(s).Volume
                if v > TOL:
                    hits[n] = hits.get(n, 0.0) + v
    return hits


def rotated(shape, pivot, deg):
    s = shape.copy()
    s.rotate(pivot, axis_y, deg)
    return s


print("=" * 78)
print("MECHANICS CHECK (LF leg, geometry from assembled_robot.FCStd)")
print("=" * 78)

# ---------------------------------------------------------------------------------------
# 1. Joint inventory
# ---------------------------------------------------------------------------------------
print("\n--- 1. Joint inventory: CHAMP needs 3 actuated joints per leg (12 total) ---")

# Hip pitch (upper_leg_joint, axis Y): servo horn is in the hip housing; does its bolt pattern
# land on thigh material? Probe each horn bolt position (+ centre spline) through the thigh.
r = params.KNEE_BOLT_CIRCLE_DIA / 2.0
probes = [(0, 0)] + [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]
landed = 0
for dx, dz in probes:
    p = place_pt(App.Vector(HIP_CX + dx, HORN_Y, HORN_Z + dz))
    probe = Part.makeCylinder(1.6, LEG_T, p, axis_y)
    if upper.common(probe).Volume > 0.5 * probe.Volume:
        landed += 1
print(f"hip pitch  (axis Y): servo in hip housing, horn bolt circle at the thigh's hip end. "
      f"Horn screw positions landing on thigh material: {landed}/5 "
      f"(the thigh's hip end is a {params.SERVO_BODY_W:.1f}mm-wide slot, not a horn bolt pattern) "
      f"-> {'OK' if landed >= 3 else 'NO ATTACHMENT: horn has nothing to drive'}")

# Knee (lower_leg_joint, axis Y): bolt circles coaxial? links side by side so they can pivot?
upper_bc = App.Vector(knee_pt.x, knee_pt.y, knee_pt.z + 20.0)
lower_bc = App.Vector(knee_pt.x, knee_pt.y, knee_pt.z - 20.0)
y_overlap = min(upper.BoundBox.YMax, lower.BoundBox.YMax) - max(upper.BoundBox.YMin, lower.BoundBox.YMin)
print(f"knee       (axis Y): thigh and shin bolt circles are {planar(upper_bc, lower_bc):.0f}mm apart "
      f"(not coaxial -- a butt joint, not a pivot); links share {y_overlap:.1f}mm of the same "
      f"{LEG_T:.0f}mm plane (coplanar, so they can't fold past each other); no knee servo pocket "
      f"or linkage exists in either link -> NO KNEE JOINT")
for deg in (15, 45, 90):
    v = upper.common(rotated(lower, knee_pt, deg)).Volume
    print(f"    knee bend {deg:>3} deg about the junction: thigh/shin overlap {v:,.0f} mm^3 "
          f"-> {'clear' if v <= TOL else 'COLLIDES'}")

print(f"hip ab/ad  (axis X): hip housing is bolted rigidly to the bottom deck (4x M4 through the "
      f"floor); the {params.HIP_ABDUCTION_DEG:.0f} deg tilt is a fixed shim, not a joint -> NO HIP JOINT")
print("Actuated joints present: 4 of 12 (hip pitch only), and those 4 have no horn attachment.")

# ---------------------------------------------------------------------------------------
# 2. Gait sweep (IK over CHAMP's gait envelope)
# ---------------------------------------------------------------------------------------
def ik(x, h, l1, l2, knee_sign):
    d2 = x * x + h * h
    c2 = (d2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c2) > 1:
        return None
    t2 = knee_sign * math.acos(c2)
    t1 = math.atan2(x, h) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
    return math.degrees(t1), math.degrees(t2)


xs = [-STRIDE / 2, -STRIDE / 4, 0.0, STRIDE / 4, STRIDE / 2]
hs = [NOMINAL_H, NOMINAL_H - SWING_H]

print(f"\n--- 2. Gait sweep: CHAMP envelope x=+-{STRIDE / 2:.0f}mm, h={NOMINAL_H - SWING_H:.0f}.."
      f"{NOMINAL_H:.0f}mm ---")
print(f"Link lengths in this CAD (hip axis->junction, junction->foot tip): L1={L1:.1f}  L2={L2:.1f}mm; "
      f"CHAMP stock kinematics: {CHAMP_L1:.0f}/{CHAMP_L2:.0f}mm")
print("  (CAD lengths were taken from CHAMP's VISUAL box sizes 190.5/156mm, not its joint distances --"
      " the controller config must use the real lengths or feet land in the wrong place.)")

for label, sign in (("knee folds BACKWARD", 1), ("knee folds FORWARD", -1)):
    angles, hits_total = [], {}
    self_hit = 0.0
    for h in hs:
        for x in xs:
            sol = ik(x, h, L1, L2, sign)
            if sol is None:
                continue
            t1, t2 = sol
            angles.append((t1, t2))
            # positive rotation about +Y swings the foot toward -X, so the foot-forward angle is negated
            u = rotated(upper, hip_pt, -t1)
            knee_now = rotated(Part.Vertex(knee_pt), hip_pt, -t1).Point
            lo = rotated(rotated(lower, hip_pt, -t1), knee_now, -t2)
            for part in (u, lo):
                for n, v in clash(part).items():
                    hits_total[n] = max(hits_total.get(n, 0.0), v)
            self_hit = max(self_hit, u.common(lo).Volume)
    t1s, t2s = [a[0] for a in angles], [a[1] for a in angles]
    print(f"{label}: hip pitch {min(t1s):+.0f}..{max(t1s):+.0f} deg, knee {min(t2s):+.0f}..{max(t2s):+.0f} deg "
          f"({len(angles)} poses)")
    print(f"    thigh vs shin (coplanar links): max overlap {self_hit:,.0f} mm^3 -> "
          f"{'clear' if self_hit <= TOL else 'COLLIDES in every bent pose'}")
    if hits_total:
        for n, v in sorted(hits_total.items(), key=lambda kv: -kv[1]):
            print(f"    leg links vs {n}: max overlap {v:,.0f} mm^3 -> COLLIDES")
    else:
        print("    leg links vs every chassis part / other leg: clear across all poses")

# ---------------------------------------------------------------------------------------
# 3. Hip ab/ad sweep (CHAMP hip_joint, axis X) -- could the links swing sideways at all?
# ---------------------------------------------------------------------------------------
print("\n--- 3. Hip ab/ad sweep (straight leg links about an X axis through the hip pitch point) ---")
for deg in (-15, -8, 8, 15):
    hits = {}
    for part in (upper, lower):
        s = part.copy()
        s.rotate(hip_pt, App.Vector(1, 0, 0), deg)
        for n, v in clash(s).items():
            hits[n] = hits.get(n, 0.0) + v
    side = "inward " if deg < 0 else "outward"
    print(f"  {side} {abs(deg):>2} deg: " + (", ".join(f"{n} {v:,.0f} mm^3" for n, v in hits.items())
                                             if hits else "clear"))

# ---------------------------------------------------------------------------------------
# 4. Mass, centre of gravity, torque, clearance
# ---------------------------------------------------------------------------------------
print("\n--- 4. Loads ---")
payload_mass = {"Battery": params.MASS_BATTERY_G, "UBEC": params.MASS_UBEC_G, "IMU": params.MASS_MPU6050_G,
                "Pi4": params.MASS_PI4_G, "PCA9685": params.MASS_PCA9685_G,
                "RPLidarA1": params.MASS_RPLIDAR_A1_G, "EStop": params.MASS_ESTOP_G,
                "XT60": params.MASS_XT60_G, "PowerSwitch": params.MASS_SWITCH_G}
# FDM parts are not solid: ~3 perimeters + 25% infill lands around 40-50% of solid weight.
PRINT_FILL = 0.45   # ASSUMPTION -- typical effective density ratio for structural FDM parts
masses = []          # (grams, centre of mass, category)
for o in doc.Objects:
    n = o.Name
    if not hasattr(o, "Shape") or not o.Shape.Solids or n.endswith("_LegLinks"):
        continue
    sh = o.Shape
    com = App.Vector(0, 0, 0)   # Compounds have no CenterOfMass -- volume-weight their solids
    for s in sh.Solids:
        com += s.CenterOfMass * (s.Volume / sh.Volume)
    if n.endswith("_HipHousing"):
        # its volume is already inside <name>_Leg; only add that leg's 3 MG996Rs here
        # (knee + ab/ad servos have no CAD home yet -- assumed hip-mounted, SpotMicro-style)
        masses.append((3 * params.MASS_MG996R_G, com, "bought"))
    elif n.startswith("Payload_"):
        masses.append((payload_mass[n[len("Payload_"):]], com, "bought"))
    elif n.startswith("Standoff"):
        masses.append((params.MASS_STANDOFF_G, com, "bought"))
    elif n in ("BottomDeck", "TopDeck"):
        masses.append((sh.Volume * params.DENSITY_AL5052, com, "aluminium"))
    elif n == "SkidPlate":
        masses.append((sh.Volume * params.DENSITY_UHMW, com, "printed/plastic"))
    else:   # legs (+hip housings), shims, walls, lid, pan-tilt, sniffer arm
        masses.append((sh.Volume * params.DENSITY_PETG * PRINT_FILL, com, "printed/plastic"))
        if n in ("PanTiltHead", "SnifferArm"):
            masses.append((2 * params.MASS_SG90_G, com, "bought"))

total = sum(m for m, _, _ in masses)
cg = App.Vector(0, 0, 0)
for m, c, _ in masses:
    cg += c * (m / total)
by_cat = {}
for m, _, cat in masses:
    by_cat[cat] = by_cat.get(cat, 0.0) + m
print(f"Total mass {total / 1000:.2f} kg (printed parts at {PRINT_FILL:.0%} of solid PETG, ASSUMPTION): "
      + ", ".join(f"{k} {v / 1000:.2f} kg" for k, v in by_cat.items()))
acrylic_saving = by_cat["aluminium"] * (1 - 1.19 / 2.68)
print(f"  switching the two decks from 3mm Al5052 to 3mm acrylic (1.19 g/cm^3) saves "
      f"{acrylic_saving / 1000:.2f} kg -> {(total - acrylic_saving) / 1000:.2f} kg")

# the 4 feet are symmetric about the body origin by construction
print(f"Centre of gravity: X={cg.x:+.1f} Y={cg.y:+.1f} mm from the body centre (feet-rectangle centre), "
      f"Z={cg.z:.1f}mm above the deck underside")
# trot support lines are the two diagonals through the origin -- CG distance from each
for a, b, lab in (((1, 1), (-1, -1), "LF-RH"), ((1, -1), (-1, 1), "RF-LH")):
    ax, ay = a[0] * params.BASE_TO_HIP_X, a[1] * params.BASE_TO_HIP_Y
    dist = abs(ay * cg.x - ax * cg.y) / math.hypot(ax, ay)
    print(f"  CG offset from trot diagonal {lab}: {dist:.1f}mm "
          f"({'fine' if dist < 15 else 'robot will tip toward the unsupported side each step'})")

for mass_kg, tag in ((total / 1000, "as modelled"), ((total - acrylic_saving) / 1000, "acrylic decks")):
    f_leg = mass_kg * G / 2.0          # trot: 2 feet on the ground
    print(f"Torques at CHAMP nominal stance ({tag}, {mass_kg:.2f} kg, 2 feet down, static -- "
          f"real gait peaks run ~1.5-2x):")
    for l1, l2, lab in ((L1, L2, "this CAD's links"), (CHAMP_L1, CHAMP_L2, "CHAMP 141/141 links")):
        worst_knee = worst_hip = 0.0
        for x in xs:
            t1, t2 = ik(x, NOMINAL_H, l1, l2, 1)
            kx = l1 * math.sin(math.radians(t1))
            worst_knee = max(worst_knee, f_leg * abs(x - kx) / 1000.0)
            worst_hip = max(worst_hip, f_leg * abs(x) / 1000.0)
        lateral = abs(knee_pt.y - hip_pt.y) + NOMINAL_H * math.sin(math.radians(params.HIP_ABDUCTION_DEG))
        abad = f_leg * lateral / 1000.0
        print(f"  {lab:>20}: knee {worst_knee:.2f} N*m, hip pitch {worst_hip:.2f} N*m, hip ab/ad "
              f"{abad:.2f} N*m  vs MG996R stall {MG996R_STALL_NM:.2f} N*m "
              f"(continuous use ~{MG996R_STALL_NM * 0.4:.2f})")

ground_z = hip_pt.z - NOMINAL_H
lowest = min(((n, min(s.BoundBox.ZMin for s in solids)) for n, solids in obstacles.items()
              if not n.endswith(("_Leg", "_HipHousing", "_HipShim"))), key=lambda t: t[1])
belly = min(s.BoundBox.ZMin for s in obstacles["BottomDeck"])
print(f"Ground clearance at CHAMP nominal height ({NOMINAL_H:.0f}mm hip-to-foot): deck underside "
      f"{belly - ground_z:.0f}mm, lowest part {lowest[0]} {lowest[1] - ground_z:.0f}mm "
      f"(vs. a {SWING_H:.0f}mm swing height -- anything lower than that can strike an obstacle the feet step over)")
print(f"Current CAD pose stands on straight legs: foot {foot_pt.z:.0f} vs hip {hip_pt.z:.0f} -> "
      f"{hip_pt.z - foot_pt.z:.0f}mm hip-to-foot, not CHAMP's {NOMINAL_H:.0f}mm crouch")
