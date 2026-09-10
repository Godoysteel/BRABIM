// Validates the Revit-style roof mechanism with OCCT: each eave edge gets an
// inward-sloping half-space plane; the roof solid is the intersection of a
// tall box with all the sloped half-spaces. Edges left out of the slope list
// stay vertical (gable ends) -- hip and gable use the exact same mechanism,
// just a different set of sloped edges, matching how Revit's "roof by
// footprint" works (per-edge "defines slope" toggle).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
globalThis.__dirname = path.join(here, 'node_modules/opencascade.js/dist');
globalThis.require = (await import('node:module')).createRequire(import.meta.url);
const { default: opencascadeFactory } = await import('opencascade.js/dist/opencascade.wasm.js');
const wasmBinary = readFileSync(path.join(here, 'node_modules/opencascade.js/dist/opencascade.wasm.wasm'));
const oc = await opencascadeFactory({ wasmBinary });

function pnt(x, y, z) { return new oc.gp_Pnt_3(x, y, z); }
function dir(x, y, z) { return new oc.gp_Dir_4(x, y, z); }

// A roof plane through world point `p`, tilted so it rises by `slope`
// (rise/run) moving in direction `inward` (a unit 2D vector pointing from
// the eave toward the building interior). `outwardNormal` points away from
// the kept (below-the-roof) material, matching MakeHalfSpace's convention:
// the reference point passed to MakeHalfSpace should be on the material we
// keep, i.e. below/inside.
function slopedHalfSpace(p, inward, slope, keepPoint) {
  const n = [-inward[0] * slope, -inward[1] * slope, 1]; // plane normal (unnormalized is fine for gp_Dir, it normalizes)
  const pln = new oc.gp_Pln_3(pnt(...p), dir(...n));
  const face = new oc.BRepBuilderAPI_MakeFace_3(pln).Face();
  return new oc.BRepPrimAPI_MakeHalfSpace_1(face, pnt(...keepPoint)).Solid();
}

function buildRoof(w, d, eaveHeight, slope, slopedEdges) {
  // Footprint centered at origin: x in [-w/2,w/2], y in [-d/2,d/2].
  const box = new oc.BRepPrimAPI_MakeBox_3(pnt(-w / 2, -d / 2, 0), pnt(w / 2, d / 2, eaveHeight + Math.max(w, d))).Shape();
  const edges = {
    north: { p: [0, d / 2, eaveHeight], inward: [0, -1] },
    south: { p: [0, -d / 2, eaveHeight], inward: [0, 1] },
    east: { p: [w / 2, 0, eaveHeight], inward: [-1, 0] },
    west: { p: [-w / 2, 0, eaveHeight], inward: [1, 0] },
  };
  let solid = box;
  for (const name of slopedEdges) {
    const e = edges[name];
    const hs = slopedHalfSpace([...e.p], e.inward, slope, [0, 0, eaveHeight]);
    solid = new oc.BRepAlgoAPI_Common_3(solid, hs).Shape();
  }
  // Clip off the bottom (below eaveHeight) so we only keep the roof volume.
  const bottomCut = new oc.BRepPrimAPI_MakeBox_3(pnt(-w / 2, -d / 2, -1), pnt(w / 2, d / 2, eaveHeight)).Shape();
  solid = new oc.BRepAlgoAPI_Cut_3(solid, bottomCut).Shape();
  return solid;
}

function report(label, solid) {
  new oc.BRepMesh_IncrementalMesh_2(solid, 0.05, false, 0.3, false);
  const exp = new oc.TopExp_Explorer_2(solid, oc.TopAbs_ShapeEnum.TopAbs_FACE, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);
  let faces = 0; for (; exp.More(); exp.Next()) faces++;
  const gprops = new oc.GProp_GProps_1();
  oc.BRepGProp.VolumeProperties_1(solid, gprops, false, false, false);
  console.log(label, '-> faces:', faces, 'volume:', gprops.Mass().toFixed(3));
}

const t0 = performance.now();
report('Hip (4 águas)   ', buildRoof(8, 5, 3, 0.6, ['north', 'south', 'east', 'west']));
report('Gable (2 águas) ', buildRoof(8, 5, 3, 0.6, ['north', 'south']));
report('Shed (1 água)   ', buildRoof(8, 5, 3, 0.3, ['north']));
report('Misto (3+1)     ', buildRoof(8, 5, 3, 0.6, ['north', 'east', 'west']));
console.log('total ms:', Math.round(performance.now() - t0));
