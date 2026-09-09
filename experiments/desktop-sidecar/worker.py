"""Proof of concept: a long-lived IfcOpenShell worker process, talking JSON
lines over stdin/stdout, as a stand-in for a Tauri sidecar. Pays the
ifcopenshell import/startup cost once, then answers requests without
re-paying it -- unlike spawning a fresh process per edit.
"""
import sys, json, time
import ifcopenshell, ifcopenshell.api as api, ifcopenshell.geom
import numpy as np

BASE = [((-4,-2.5),(4,-2.5)),((-4,2.5),(4,2.5)),((-4,-2.5),(-4,2.5)),((4,-2.5),(4,2.5)),((1,-2.5),(1,2.5))]
LINKS = [(0,2,'ATSTART','ATSTART'),(0,3,'ATEND','ATSTART'),(1,2,'ATSTART','ATEND'),(1,3,'ATEND','ATEND'),(0,4,'ATPATH','ATSTART'),(1,4,'ATPATH','ATEND')]

def run(thicknesses, heights):
    f = ifcopenshell.file(schema='IFC4')
    project = api.run('root.create_entity', f, ifc_class='IfcProject', name='BRABIM sidecar test')
    unit = api.run('unit.add_si_unit', f, unit_type='LENGTHUNIT')
    api.run('unit.assign_unit', f, units=[unit])
    model = api.run('context.add_context', f, context_type='Model')
    body = api.run('context.add_context', f, context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=model)
    plan = api.run('context.add_context', f, context_type='Plan')
    axis = api.run('context.add_context', f, context_type='Plan', context_identifier='Axis', target_view='GRAPH_VIEW', parent=plan)
    storey = api.run('root.create_entity', f, ifc_class='IfcBuildingStorey', name='Terreo')
    api.run('aggregate.assign_object', f, products=[storey], relating_object=project)
    walls = []
    for i, ((a, b), t, h) in enumerate(zip(BASE, thicknesses, heights)):
        wall = api.run('root.create_entity', f, ifc_class='IfcWall', name=f'P{i+1:02}')
        api.run('spatial.assign_container', f, products=[wall], relating_structure=storey)
        d = np.array(b, dtype=float) - a
        length = float(np.linalg.norm(d)); d /= length
        mat = np.eye(4); mat[:2,0] = d; mat[:2,1] = [-d[1], d[0]]; mat[:2,3] = a
        api.run('geometry.edit_object_placement', f, product=wall, matrix=mat)
        rep = api.run('geometry.add_axis_representation', f, context=axis, axis=[(0.,0.),(length,0.)])
        api.run('geometry.assign_representation', f, product=wall, representation=rep)
        material = f.create_entity('IfcMaterial', Name='Example')
        layer = f.create_entity('IfcMaterialLayer', Material=material, LayerThickness=t, Priority=50)
        layers = f.create_entity('IfcMaterialLayerSet', MaterialLayers=[layer])
        usage = f.create_entity('IfcMaterialLayerSetUsage', ForLayerSet=layers, LayerSetDirection='AXIS2', DirectionSense='POSITIVE', OffsetFromReferenceLine=-t/2)
        f.create_entity('IfcRelAssociatesMaterial', GlobalId=ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingMaterial=usage)
        walls.append(wall)
    for a, b, ca, cb in LINKS:
        api.run('geometry.connect_path', f, relating_element=walls[a], related_element=walls[b], relating_connection=ca, related_connection=cb)
    for w, h in zip(walls, heights):
        api.run('geometry.regenerate_wall_representation', f, wall=w, height=h)
    settings = ifcopenshell.geom.settings(); settings.set(settings.USE_WORLD_COORDS, True)
    meshes = []
    for w in walls:
        shape = ifcopenshell.geom.create_shape(settings, w)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        meshes.append({'id': w.Name, 'guid': w.GlobalId, 'vertices': v.tolist(), 'faces': faces.tolist()})
    return meshes

def main():
    ready_at = time.perf_counter()
    print(json.dumps({'type': 'ready', 'startup_seconds': round(ready_at - START, 3), 'ifcopenshell_version': ifcopenshell.version}), flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            t0 = time.perf_counter()
            meshes = run(req.get('thicknesses', [.2,.2,.2,.2,.15]), req.get('heights', [2.8]*5))
            print(json.dumps({'type': 'result', 'id': req.get('id'), 'elapsed_seconds': round(time.perf_counter() - t0, 3), 'wall_count': len(meshes), 'vertex_count': sum(len(m['vertices']) for m in meshes)}), flush=True)
        except Exception as e:
            print(json.dumps({'type': 'error', 'message': str(e)}), flush=True)

START = time.perf_counter()
if __name__ == '__main__':
    main()
