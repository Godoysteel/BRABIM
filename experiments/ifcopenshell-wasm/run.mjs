// Proof of concept: run IfcOpenShell 0.8.5 compiled to WASM (via Pyodide) in Node,
// as a stand-in for running it in the visitor's browser with no server.
// Wheel source: https://github.com/IfcOpenShell/wasm-wheels (actively maintained).
import { loadPyodide } from 'pyodide';
import { writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const OUT = path.join(path.dirname(fileURLToPath(import.meta.url)), 'results');
mkdirSync(OUT, { recursive: true });

const WHEEL_URL = 'https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl';

const started = performance.now();
const pyodide = await loadPyodide();
const pyodideReady = performance.now();

await pyodide.loadPackage(['micropip', 'numpy']);
const micropip = pyodide.pyimport('micropip');

let wheelInstalled = true, wheelError = null;
const wheelStart = performance.now();
try {
  await micropip.install(WHEEL_URL);
} catch (e) {
  wheelInstalled = false;
  wheelError = String(e);
}
const wheelReady = performance.now();

const report = {
  pyodideLoadMs: Math.round(pyodideReady - started),
  wheelInstallMs: Math.round(wheelReady - wheelStart),
  wheelInstalled,
  wheelError,
};

if (wheelInstalled) {
  const execStart = performance.now();
  const result = await pyodide.runPythonAsync(`
import ifcopenshell, ifcopenshell.api as api, ifcopenshell.geom
import numpy as np, json

f = ifcopenshell.file(schema='IFC4')
project = api.run('root.create_entity', f, ifc_class='IfcProject', name='BRABIM wasm test')
unit = api.run('unit.add_si_unit', f, unit_type='LENGTHUNIT')
api.run('unit.assign_unit', f, units=[unit])
model = api.run('context.add_context', f, context_type='Model')
body = api.run('context.add_context', f, context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=model)
plan = api.run('context.add_context', f, context_type='Plan')
axis = api.run('context.add_context', f, context_type='Plan', context_identifier='Axis', target_view='GRAPH_VIEW', parent=plan)
storey = api.run('root.create_entity', f, ifc_class='IfcBuildingStorey', name='Terreo')
api.run('aggregate.assign_object', f, products=[storey], relating_object=project)

BASE = [((-4,-2.5),(4,-2.5)),((-4,2.5),(4,2.5)),((-4,-2.5),(-4,2.5)),((4,-2.5),(4,2.5)),((1,-2.5),(1,2.5))]
LINKS = [(0,2,'ATSTART','ATSTART'),(0,3,'ATEND','ATSTART'),(1,2,'ATSTART','ATEND'),(1,3,'ATEND','ATEND'),(0,4,'ATPATH','ATSTART'),(1,4,'ATPATH','ATEND')]
thicknesses = [.2,.2,.2,.2,.15]
heights = [2.8]*5

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
    meshes.append({'id': w.Name, 'guid': w.GlobalId, 'vertex_count': len(v), 'face_count': len(faces), 'height': float(np.ptp(v[:,2])), 'bbox_min': v.min(axis=0).tolist(), 'bbox_max': v.max(axis=0).tolist()})

json.dumps({'ifcopenshell_version': ifcopenshell.version, 'wall_count': len(f.by_type('IfcWall')), 'connection_count': len(f.by_type('IfcRelConnectsPathElements')), 'meshes': meshes})
`);
  report.executionMs = Math.round(performance.now() - execStart);
  report.pythonResult = JSON.parse(result);
}

writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
process.exit(wheelInstalled ? 0 : 1);
