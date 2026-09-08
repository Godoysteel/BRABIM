import assert from 'node:assert/strict';
import {initialRoom,validateRoom,parseRoom,serializeRoom} from '../lib/room.ts';
assert.deepEqual(parseRoom(serializeRoom(initialRoom)),initialRoom);
for(const patch of [{width:1},{height:2},{doorOffset:4.5},{windowOffset:-1},{sill:2.5},{floor:NaN},{thickness:0}])assert.throws(()=>validateRoom({...initialRoom,...patch}));
assert.throws(()=>parseRoom('{"format":"brabim-room","version":2}'));
assert.throws(()=>parseRoom('{"format":"brabim-room","version":1,"room":{}}'));
assert.equal(validateRoom({...initialRoom,width:8,depth:6}).width,8);
console.log('11 verificações: medidas, abertura fora da parede e arquivo de projeto.');
