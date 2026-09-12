"""
FreeCAD GUI macro -- renders PNG views of assembled_robot.FCStd into renders/.
Run with the GUI build, NOT freecadcmd:
  Start-Process "C:\\Users\\Aadityaa\\AppData\\Local\\Programs\\FreeCAD 1.1\\bin\\freecad.exe" `
      -ArgumentList '"C:\\Users\\Aadityaa\\iqoo\\quadruped\\cad\\render_views.py"' -PassThru | Wait-Process -Timeout 120

Gotchas this layout avoids (each found the hard way):
  - view animation left on -> captures come out mid-rotation or blank; turned off below.
  - capturing before the window has laid out -> blank; one QTimer delay before everything.
  - closing the main window with an unsaved document open -> save prompt, FreeCAD never exits;
    every document is closed first.
"""
import os

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

SRC = "C:/Users/Aadityaa/iqoo/quadruped/cad/assembled_robot.FCStd"
OUT = "C:/Users/Aadityaa/iqoo/quadruped/cad/renders"

COLOR_RULES = [   # first substring match wins
    ("Deck", (0.35, 0.45, 0.65)),
    ("Wall", (0.30, 0.30, 0.32)),
    ("Bulkhead", (0.30, 0.30, 0.32)),
    ("HipHousing", (0.72, 0.72, 0.72)),
    ("HipShim", (0.55, 0.55, 0.58)),
    ("Standoff", (0.60, 0.55, 0.35)),
    ("Leg", (0.50, 0.50, 0.55)),
    ("PanTiltHead", (0.90, 0.45, 0.10)),
    ("SnifferArm", (0.20, 0.55, 0.25)),
    ("SkidPlate", (0.15, 0.15, 0.15)),
    ("Payload_", (0.85, 0.65, 0.15)),
]


def color_for(name):
    return next((rgb for key, rgb in COLOR_RULES if key in name), (0.7, 0.7, 0.7))


def go():
    os.makedirs(OUT, exist_ok=True)
    src = App.openDocument(SRC)
    doc = App.newDocument("snap")
    objs = []
    for o in src.Objects:
        # Skip the duplicate fused <name>_Leg bodies by NAME (assemble_robot.py also exports each
        # leg as HipHousing/LegLinks/HipShim). Don't filter on o.Visibility: in the GUI build every
        # object of a freecadcmd-saved file (no GuiDocument.xml) reads back Visibility=False,
        # which produced an empty scene and blank captures.
        if not hasattr(o, "Shape") or o.Name.endswith("_Leg"):
            continue
        n = doc.addObject("Part::Feature", o.Name)
        n.Shape = o.Shape
        objs.append(n)
    doc.recompute()
    Gui.setActiveDocument(doc.Name)
    v = Gui.activeDocument().activeView()
    v.setAnimationEnabled(False)
    v.setCameraType("Orthographic")
    for n in objs:
        n.ViewObject.ShapeColor = color_for(n.Name)

    def shot(name, view_fn):
        view_fn(); v.fitAll(); Gui.updateGui()
        v.saveImage(f"{OUT}/{name}.png", 1600, 1000, "White")

    shot("full_iso", v.viewIsometric)
    shot("full_front", v.viewFront)
    shot("full_top", v.viewTop)
    shot("full_right", v.viewRight)

    leg_parts = ("_Leg", "LegLinks", "HipHousing", "HipShim")
    for n in objs:
        n.ViewObject.Visibility = not any(k in n.Name for k in leg_parts)
    shot("chassis_only_iso", v.viewIsometric)

    for n in objs:
        n.ViewObject.Visibility = n.Name != "TopDeckLid"
        if "Deck" in n.Name:
            n.ViewObject.Transparency = 70
    shot("payload_view", v.viewIsometric)

    for d in list(App.listDocuments()):
        App.closeDocument(d)
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, go)
