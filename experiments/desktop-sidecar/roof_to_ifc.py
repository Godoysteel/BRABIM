"""Bridges an OCP (OCCT) solid into a real IfcRoof entity inside an
ifcopenshell file, closing the last gap from roof_ocp.py: can the roof
geometry actually become IFC data, not just a standalone OCCT shape?
"""
import time
import ifcopenshell
import ifcopenshell.api as api
import ifcopenshell.geom

from OCP.gp import gp_Pnt, gp_Dir, gp_Pln
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SHAPE
from OCP.TopoDS import TopoDS


def sloped_half_space(p, inward, slope, keep_point):
    nx, ny, nz = -inward[0] * slope, -inward[1] * slope, 1
    face = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(*p), gp_Dir(nx, ny, nz))).Face()
    return BRepPrimAPI_MakeHalfSpace(face, gp_Pnt(*keep_point)).Solid()


def build_roof_solid(w, d, eave_height, slope, sloped_edges):
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
        solid = BRepAlgoAPI_Common(solid, sloped_half_space(p, inward, slope, (0, 0, eave_height))).Shape()
    bottom_cut = BRepPrimAPI_MakeBox(gp_Pnt(-w / 2, -d / 2, -1), gp_Pnt(w / 2, d / 2, eave_height)).Shape()
    return BRepAlgoAPI_Cut(solid, bottom_cut).Shape()


def triangulate(solid):
    """Extracts (vertices, faces) suitable for add_mesh_representation from
    an OCP solid, mirroring the same technique used in the JS experiment
    (experiments/opencascade-wasm) -- BRepMesh_IncrementalMesh then walk
    each face's Poly_Triangulation.
    """
    BRepMesh_IncrementalMesh(solid, 0.05, False, 0.3, False)
    vertices, faces = [], []
    exp = TopExp_Explorer(solid, TopAbs_FACE, TopAbs_SHAPE)
    while exp.More():
        face = TopoDS.Face(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            base = len(vertices)
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                vertices.append((p.X(), p.Y(), p.Z()))
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                faces.append((base + a - 1, base + b - 1, base + c - 1))
        exp.Next()
    return vertices, faces


def main():
    t0 = time.perf_counter()
    solid = build_roof_solid(8, 5, 3, 0.6, ['north', 'south', 'east', 'west'])
    vertices, faces = triangulate(solid)
    print(f'triangulated: {len(vertices)} vertices, {len(faces)} triangles ({time.perf_counter() - t0:.3f}s)')

    f = ifcopenshell.file(schema='IFC4')
    project = api.run('root.create_entity', f, ifc_class='IfcProject', name='BRABIM')
    unit = api.run('unit.add_si_unit', f, unit_type='LENGTHUNIT')
    api.run('unit.assign_unit', f, units=[unit])
    model = api.run('context.add_context', f, context_type='Model')
    body = api.run('context.add_context', f, context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=model)
    storey = api.run('root.create_entity', f, ifc_class='IfcBuildingStorey', name='Terreo')
    api.run('aggregate.assign_object', f, products=[storey], relating_object=project)

    roof = api.run('root.create_entity', f, ifc_class='IfcRoof', name='Telhado')
    api.run('spatial.assign_container', f, products=[roof], relating_structure=storey)
    rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
    api.run('geometry.assign_representation', f, product=roof, representation=rep)
    api.run('geometry.edit_object_placement', f, product=roof)

    # Round-trip: does ifcopenshell.geom (the IFC geometry engine, not OCP)
    # read this IfcRoof back out with sane geometry?
    settings = ifcopenshell.geom.settings(); settings.set(settings.USE_WORLD_COORDS, True)
    shape = ifcopenshell.geom.create_shape(settings, roof)
    v = shape.geometry.verts
    fc = shape.geometry.faces
    print(f'round-trip via ifcopenshell.geom: {len(v)//3} vertex coords, {len(fc)//3} triangles')
    print('z range:', min(v[2::3]), '..', max(v[2::3]), '(expect 0..3 eave + slope)')

    out = 'results_roof_ifc.ifc'
    f.write(out)
    print('wrote', out, 'ifc_class of roof entity:', roof.is_a())


if __name__ == '__main__':
    main()
