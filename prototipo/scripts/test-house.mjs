import assert from 'node:assert/strict';
import {initialHouse,addHouseRoom,layoutHouse,parseHouse,serializeHouse,updateHouseRoom,validateHouse} from '../lib/house.ts';
import {serializeRoom,initialRoom} from '../lib/room.ts';
import {houseMeshes} from '../lib/house-geometry.ts';
const h=addHouseRoom(addHouseRoom(initialHouse));
assert.equal(h.rooms.length,3);
assert.deepEqual(parseHouse(serializeHouse(h)),h);
assert.deepEqual(parseHouse(serializeRoom(initialRoom)),initialHouse);
assert.equal(layoutHouse(h).width,15.4);
const meshes=houseMeshes(h);
assert.equal(new Set(meshes.filter(m=>m.id.startsWith('shared:')).map(m=>m.id)).size,2);
assert.equal(meshes.filter(m=>m.id.endsWith(':P03')).length,1);
assert.equal(meshes.filter(m=>m.id.endsWith(':P04')).length,1);
const bounds=m=>[0,1,2].map(axis=>[Math.min(...m.vertices.map(v=>v[axis])),Math.max(...m.vertices.map(v=>v[axis]))]);
const structural=meshes.filter(m=>m.id.includes(':P')||m.id.startsWith('shared:')||m.id.endsWith(':F01'));
for(let i=0;i<structural.length;i++)for(let j=i+1;j<structural.length;j++){
  const a=bounds(structural[i]),b=bounds(structural[j]);
  assert.ok(!a.every((v,k)=>Math.min(v[1],b[k][1])-Math.max(v[0],b[k][0])>1e-5),`Sobreposição: ${structural[i].id} / ${structural[j].id}`);
}
for(const m of meshes.filter(m=>m.id.startsWith('shared:'))){const b=bounds(m);assert.ok(!(b[1][0]<0 && b[1][1]>0 && b[2][0]<2),'Porta de ligação obstruída');}
const changed=updateHouseRoom(h,'r2','depth',6);
assert.ok(changed.rooms.every(e=>e.room.depth===6));
assert.equal(updateHouseRoom(h,'r2','width',6).rooms[0].room.width,5);
assert.throws(()=>updateHouseRoom(h,'r2','width',2));
assert.throws(()=>validateHouse({rooms:[]}));
assert.throws(()=>validateHouse({rooms:[h.rooms[0],h.rooms[0]]}));
assert.throws(()=>parseHouse('{"format":"brabim-house","version":2}'));
assert.throws(()=>validateHouse({rooms:[{...h.rooms[0],room:{}}]}));
assert.throws(()=>validateHouse({rooms:[{...h.rooms[0],name:''}]}));
let full=initialHouse;for(let i=1;i<8;i++)full=addHouseRoom(full);assert.throws(()=>addHouseRoom(full));
const removed={rooms:h.rooms.filter(e=>e.id!=='r2')};
assert.equal(new Set(houseMeshes(removed).filter(m=>m.id.startsWith('shared:')).map(m=>m.id)).size,1);
console.log('Casa: migração, salvamento, limites, edição, divisórias, passagens e ausência de sobreposição aprovados.');
