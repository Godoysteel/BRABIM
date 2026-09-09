"""Long-lived IfcOpenShell worker: reads room parameters as JSON lines on
stdin, returns real wall geometry (vertices/faces) as JSON on stdout. Pays
the ifcopenshell import/startup cost once, at launch.
"""
import sys, json, time
import ifcopenshell, ifcopenshell.api as api, ifcopenshell.geom
import numpy as np

def build_room(width, depth, height, thickness):
    w, d, h, t = width, depth, height, thickness
    # Rectangle loop: north, south, west, east walls, joined at all 4 corners.
    base = [
        ((-w/2, d/2), (w/2, d/2)),   # P01 north
        ((-w/2, -d/2), (w/2, -d/2)), # P02 south
        ((-w/2, -d/2), (-w/2, d/2)), # P03 west
        ((w/2, -d/2), (w/2, d/2)),   # P04 east
    ]
    links = [(0, 2, 'ATSTART', 'ATEND'), (0, 3, 'ATEND', 'ATEND'), (1, 2, 'ATSTART', 'ATSTART'), (1, 3, 'ATEND', 'ATSTART')]

    f = ifcopenshell.file(schema='IFC4')
    project = api.run('root.create_entity', f, ifc_class='IfcProject', name='BRABIM')
    unit = api.run('unit.add_si_unit', f, unit_type='LENGTHUNIT')
    api.run('unit.assign_unit', f, units=[unit])
    model = api.run('context.add_context', f, context_type='Model')
    api.run('context.add_context', f, context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=model)
    plan = api.run('context.add_context', f, context_type='Plan')
    axis = api.run('context.add_context', f, context_type='Plan', context_identifier='Axis', target_view='GRAPH_VIEW', parent=plan)
    storey = api.run('root.create_entity', f, ifc_class='IfcBuildingStorey', name='Terreo')
    api.run('aggregate.assign_object', f, products=[storey], relating_object=project)

    walls = []
    for i, (a, b) in enumerate(base):
        wall = api.run('root.create_entity', f, ifc_class='IfcWall', name=f'P{i+1:02}')
        api.run('spatial.assign_container', f, products=[wall], relating_structure=storey)
        vec = np.array(b, dtype=float) - a
        length = float(np.linalg.norm(vec)); vec /= length
        mat = np.eye(4); mat[:2, 0] = vec; mat[:2, 1] = [-vec[1], vec[0]]; mat[:2, 3] = a
        api.run('geometry.edit_object_placement', f, product=wall, matrix=mat)
        rep = api.run('geometry.add_axis_representation', f, context=axis, axis=[(0., 0.), (length, 0.)])
        api.run('geometry.assign_representation', f, product=wall, representation=rep)
        material = f.create_entity('IfcMaterial', Name='Parede')
        layer = f.create_entity('IfcMaterialLayer', Material=material, LayerThickness=t, Priority=50)
        layers = f.create_entity('IfcMaterialLayerSet', MaterialLayers=[layer])
        usage = f.create_entity('IfcMaterialLayerSetUsage', ForLayerSet=layers, LayerSetDirection='AXIS2', DirectionSense='POSITIVE', OffsetFromReferenceLine=-t/2)
        f.create_entity('IfcRelAssociatesMaterial', GlobalId=ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingMaterial=usage)
        walls.append(wall)
    for a, b, ca, cb in links:
        api.run('geometry.connect_path', f, relating_element=walls[a], related_element=walls[b], relating_connection=ca, related_connection=cb)
    for wall in walls:
        api.run('geometry.regenerate_wall_representation', f, wall=wall, height=h)

    settings = ifcopenshell.geom.settings(); settings.set(settings.USE_WORLD_COORDS, True)
    meshes = []
    for wall in walls:
        shape = ifcopenshell.geom.create_shape(settings, wall)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        meshes.append({'id': wall.Name, 'guid': wall.GlobalId, 'vertices': v.tolist(), 'faces': faces.tolist()})
    return meshes

def main():
    print(json.dumps({'type': 'ready', 'startup_seconds': round(time.perf_counter() - START, 3), 'ifcopenshell_version': ifcopenshell.version}), flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            room = req.get('room', {})
            t0 = time.perf_counter()
            meshes = build_room(
                width=float(room.get('width', 5)),
                depth=float(room.get('depth', 4)),
                height=float(room.get('height', 2.8)),
                thickness=float(room.get('thickness', .2)),
            )
            print(json.dumps({'type': 'result', 'id': req.get('id'), 'elapsed_seconds': round(time.perf_counter() - t0, 3), 'meshes': meshes}), flush=True)
        except Exception as e:
            print(json.dumps({'type': 'error', 'id': req.get('id') if 'req' in dir() else None, 'message': str(e)}), flush=True)

START = time.perf_counter()
if __name__ == '__main__':
    main()
