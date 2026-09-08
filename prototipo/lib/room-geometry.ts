import * as THREE from 'three';
import {type Room,validateRoom} from './room.ts';
import type {IfcMesh} from '../app/viewport';
// Procedural rectangular prototype assembled with Three.js primitives, not an IFC calculation.
export function roomMeshes(r:Room):IfcMesh[]{validateRoom(r);const result:IfcMesh[]=[];const {width:w,depth:d,height:h,thickness:t}=r;
function box(id:string,x:number,y:number,z:number,a:number,b:number,c:number){if(a<=0||b<=0||c<=0)return;const g=new THREE.BoxGeometry(a,b,c);g.translate(x,y,z);const p=g.getAttribute('position');const vertices=Array.from({length:p.count},(_,i)=>[p.getX(i),-p.getZ(i),p.getY(i)]);const idx=Array.from(g.index!.array);const faces=Array.from({length:idx.length/3},(_,i)=>idx.slice(i*3,i*3+3));result.push({id,guid:id,vertices,faces,height:b});g.dispose();}
function opening(id:string,z:number,offset:number,width:number,sill:number,height:number){const left=-w/2+offset,right=left+width;box(id,(-w/2-t+left)/2,h/2,z,offset+t,h,t);box(id,(right+w/2+t)/2,h/2,z,w-offset-width+t,h,t);box(id,(left+right)/2,sill/2,z,width,sill,t);box(id,(left+right)/2,(sill+height+h)/2,z,width,h-sill-height,t);return (left+right)/2;}
const door=opening('P02',d/2+t/2,r.doorOffset,r.doorWidth,0,r.doorHeight);const win=opening('P01',-d/2-t/2,r.windowOffset,r.windowWidth,r.sill,r.windowHeight);
box('P03',-w/2-t/2,h/2,0,t,h,d);box('P04',w/2+t/2,h/2,0,t,h,d);box('F01',0,-r.floor/2,0,w+2*t,r.floor,d+2*t);
// Frames and a thin window pane. Door opening remains visible for inspection.
for(const [id,cx,z,width,sill,height] of [['D01',door,d/2+t/2,r.doorWidth,0,r.doorHeight],['J01',win,-d/2-t/2,r.windowWidth,r.sill,r.windowHeight]] as [string,number,number,number,number,number][]){box(id,cx-width/2+.025,sill+height/2,z,.05,height,t*.8);box(id,cx+width/2-.025,sill+height/2,z,.05,height,t*.8);box(id,cx,sill+height-.025,z,width,.05,t*.8);if(id==='J01'){box(id,cx,sill+.025,z,width,.05,t*.8);box(id,cx,sill+height/2,z,width-.1,height-.1,.012);}else{box(id,cx-width/2+.025,height/2,z-width/2,.04,height-.05,width-.05);}}
return result;}

