"""Validates that OCP (OCCT for Python, the CadQuery binding) can run the
same half-space-intersection roof technique as the JS/WASM experiment
(experiments/opencascade-wasm/roof.mjs), in the SAME process as
ifcopenshell -- proving the two can be combined in one worker.
"""
import time
import ifcopenshell  # imported first, mirrors the real worker.py

from OCP.gp import gp_Pnt, gp_Dir, gp_Pln
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SHAPE


def sloped_half_space(p, inward, slope, keep_point):
    nx, ny, nz = -inward[0] * slope, -inward[1] * slope, 1
    pln = gp_Pln(gp_Pnt(*p), gp_Dir(nx, ny, nz))
    face = BRepBuilderAPI_MakeFace(pln).Face()
    return BRepPrimAPI_MakeHalfSpace(face, gp_Pnt(*keep_point)).Solid()


def build_roof(w, d, eave_height, slope, sloped_edges):
    box = BRepPrimAPI_MakeBox(gp_Pnt(-w / 2, -d / 2, 0), gp_Pnt(w / 2, d / 2, eave_height + max(w, d))).Shape()
    edges = {
        'north': ((0, d / 2, eave_height), (0, -1)),
        'south': ((0, -d / 2, eave_height), (0, 1)),
        'east': ((w / 2, 0, eave_height), (-1, 0)),
        'west': ((-w / 2, 0, eave_height), (1, 0)),
    }
    solid = box
    for name in sloped_edges:
        p, inward = edges[name]
        hs = sloped_half_space(p, inward, slope, (0, 0, eave_height))
        solid = BRepAlgoAPI_Common(solid, hs).Shape()
    bottom_cut = BRepPrimAPI_MakeBox(gp_Pnt(-w / 2, -d / 2, -1), gp_Pnt(w / 2, d / 2, eave_height)).Shape()
    return BRepAlgoAPI_Cut(solid, bottom_cut).Shape()


def report(label, solid):
    exp = TopExp_Explorer(solid, TopAbs_FACE, TopAbs_SHAPE)
    faces = 0
    while exp.More():
        faces += 1
        exp.Next()
    gprops = GProp_GProps()
    BRepGProp.VolumeProperties_s(solid, gprops, False, False, False)
    print(f"{label} -> faces: {faces} volume: {gprops.Mass():.3f}")


t0 = time.perf_counter()
report('Hip (4 aguas)   ', build_roof(8, 5, 3, 0.6, ['north', 'south', 'east', 'west']))
report('Gable (2 aguas) ', build_roof(8, 5, 3, 0.6, ['north', 'south']))
report('Shed (1 agua)   ', build_roof(8, 5, 3, 0.3, ['north']))
print('total seconds:', round(time.perf_counter() - t0, 3))
print('ifcopenshell still usable:', ifcopenshell.file(schema='IFC4'))
