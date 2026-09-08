import {initialRoom, parseRoom, validateRoom, type Room} from './room.ts';
export type HouseRoom = {id:string; name:string; room:Room};
export type House = {rooms:HouseRoom[]};
export const initialHouse:House = {rooms:[{id:'r1',name:'Ambiente 01',room:{...initialRoom}}]};
export const commonKeys = ['depth','height','thickness','floor'] as const;
export function validateHouse(h:House):House {
  if(!h || !Array.isArray(h.rooms) || h.rooms.length<1 || h.rooms.length>8) throw Error('O projeto deve ter de 1 a 8 cômodos.');
  const ids=new Set<string>();
  for(const entry of h.rooms){
    if(!entry || typeof entry.id!=='string' || !/^[a-zA-Z0-9-]{1,50}$/.test(entry.id) || ids.has(entry.id)) throw Error('Identificação de cômodo inválida ou repetida.');
    ids.add(entry.id);
    if(typeof entry.name!=='string'||!entry.name.trim()||entry.name.length>50) throw Error('Informe um nome de até 50 caracteres para cada cômodo.');
    if(!entry.room || Object.keys(initialRoom).some(k=>typeof entry.room[k as keyof Room]!=='number')) throw Error('Medidas do cômodo incompletas.');
    validateRoom(entry.room);
    if(commonKeys.some(k=>entry.room[k]!==h.rooms[0].room[k])) throw Error('Profundidade, altura, parede e piso devem ser iguais no conjunto.');
  }
  return h;
}
export function layoutHouse(h:House){
  validateHouse(h);
  const t=h.rooms[0].room.thickness;
  const width=h.rooms.reduce((sum,e)=>sum+e.room.width,0)+(h.rooms.length-1)*t;
  let left=-width/2;
  return {width, rooms:h.rooms.map(e=>{const placement={...e,left,center:left+e.room.width/2};left+=e.room.width+t;return placement;})};
}
export function updateHouseRoom(h:House,id:string,key:keyof Room,value:number):House {
  return validateHouse({rooms:h.rooms.map(e=>e.id===id || (commonKeys as readonly string[]).includes(key)?{...e,room:{...e.room,[key]:value}}:e)});
}
export function addHouseRoom(h:House):House {
  const id=`r${Math.max(0,...h.rooms.map(e=>Number(e.id.slice(1))||0))+1}`;
  const last=h.rooms.at(-1)!;
  return validateHouse({rooms:[...h.rooms,{id,name:`Ambiente ${String(h.rooms.length+1).padStart(2,'0')}`,room:{...last.room}}]});
}
export function parseHouse(text:string):House {
  const data=JSON.parse(text);
  if(data?.format==='brabim-room') return {rooms:[{id:'r1',name:'Ambiente 01',room:parseRoom(text)}]};
  if(data?.format!=='brabim-house'||data.version!==1) throw Error('Arquivo BRABIM incompatível.');
  return validateHouse(data.house);
}
export const serializeHouse=(house:House)=>JSON.stringify({format:'brabim-house',version:1,house:validateHouse(house)},null,2);
