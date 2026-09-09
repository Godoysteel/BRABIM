// Proof of concept: can OpenCascade.js (OCCT compiled to WASM) resolve wall joins
// via plain solid boolean union, with no bespoke join math and no server?
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import path from 'node:path';
import { writeFileSync, readFileSync } from 'node:fs';

const here = path.dirname(fileURLToPath(import.meta.url));
// The Emscripten-generated factory expects CommonJS globals (__dirname,
// require) even though the file itself uses `export default`. It targets
// bundlers (webpack/vite), which shim these; plain Node needs help too.
globalThis.__dirname = path.join(here, 'node_modules/opencascade.js/dist');
globalThis.__filename = path.join(globalThis.__dirname, 'opencascade.wasm.js');
globalThis.require = createRequire(import.meta.url);

const { default: opencascadeFactory } = await import('opencascade.js/dist/opencascade.wasm.js');

const wasmBinary = readFileSync(path.join(here, 'node_modules/opencascade.js/dist/opencascade.wasm.wasm'));

const t0 = performance.now();
const oc = await opencascadeFactory({ wasmBinary });
const loadMs = Math.round(performance.now() - t0);

// Same 5-wall scenario as the other experiments: a rectangle (P01-P04) plus a
// mid partition (P05) forming two T-junctions with the long walls (P01/P02).
// All axis-aligned here (rotation isn't needed to test fuse correctness/speed).
function pnt(x, y, z) { return new oc.gp_Pnt_3(x, y, z); }
function wallBox(x0, y0, x1, y1, thickness, height) {
  const halfX = x0 === x1 ? thickness / 2 : 0;
  const halfY = y0 === y1 ? thickness / 2 : 0;
  const lo = pnt(Math.min(x0, x1) - halfX, Math.min(y0, y1) - halfY, 0);
  const hi = pnt(Math.max(x0, x1) + halfX, Math.max(y0, y1) + halfY, height);
  return new oc.BRepPrimAPI_MakeBox_3(lo, hi).Shape();
}

const height = 2.8;
const walls = [
  wallBox(-4, -2.5, 4, -2.5, 0.2, height), // P01
  wallBox(-4, 2.5, 4, 2.5, 0.2, height), // P02
  wallBox(-4, -2.5, -4, 2.5, 0.2, height), // P03
  wallBox(4, -2.5, 4, 2.5, 0.2, height), // P04
  wallBox(1, -2.5, 1, 2.5, 0.15, height), // P05, T-junctions against P01/P02
];

const unionStart = performance.now();
let fused = walls[0];
for (let i = 1; i < walls.length; i++) {
  fused = new oc.BRepAlgoAPI_Fuse_3(fused, walls[i]).Shape();
}
const unionMs = Math.round(performance.now() - unionStart);

const meshStart = performance.now();
new oc.BRepMesh_IncrementalMesh_2(fused, 0.1, false, 0.1, false);
const meshMs = Math.round(performance.now() - meshStart);

// Count faces/solids to sanity-check the result is one coherent solid, not
// five disjoint boxes still overlapping (which would mean the fuse silently
// failed to merge coincident faces).
let solidCount = 0, faceCount = 0;
const solidExplorer = new oc.TopExp_Explorer_2(fused, oc.TopAbs_ShapeEnum.TopAbs_SOLID, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);
for (; solidExplorer.More(); solidExplorer.Next()) solidCount++;
const faceExplorer = new oc.TopExp_Explorer_2(fused, oc.TopAbs_ShapeEnum.TopAbs_FACE, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);
for (; faceExplorer.More(); faceExplorer.Next()) faceCount++;

const report = { loadMs, unionMs, meshMs, solidCount, faceCount, wallCount: walls.length };
writeFileSync(path.join(here, 'results.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
