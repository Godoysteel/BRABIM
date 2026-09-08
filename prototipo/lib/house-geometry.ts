import {layoutHouse,type House} from './house.ts';
import {roomMeshes} from './room-geometry.ts';
import type {IfcMesh} from '../app/viewport';
// Restricted row layout: each partition belongs to the project only once.
export function houseMeshes(h:House):IfcMesh[]{
  const layout=layoutHouse(h), out:IfcMesh[]=[];
  for(const [i,e] of layout.rooms.entries()){
    const {width:w,depth:d,height:height,thickness:t}=e.room;
    for(const mesh of roomMeshes(e.room)){
      if((mesh.id==='P03'&&i>0)||(mesh.id==='P04'&&i<layout.rooms.length-1))continue;
      const trim=mesh.id==='P01'||mesh.id==='P02'||mesh.id==='F01';
      const vertices=mesh.vertices.map(([x,y,z])=>[e.center+(trim?Math.max(i>0?-w/2-t/2:-Infinity,Math.min(i<layout.rooms.length-1?w/2+t/2:Infinity,x)):x),y,z]);
      out.push({...mesh,id:`${e.id}:${mesh.id}`,guid:`${e.id}:${mesh.id}`,vertices});
    }
    if(i===layout.rooms.length-1)continue;
    const id=`shared:${e.id}:${layout.rooms[i+1].id}`,x=e.left+w+t/2;
    const doorWidth=.9, doorHeight=Math.min(2.1,height-.1);
    // Box coordinates are x, plan-y, height; doorway is centred in the partition.
    function box(key:string,x0:number,x1:number,y0:number,y1:number,z0:number,z1:number){
      const vertices=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
      out.push({id:key,guid:key,vertices,height:z1-z0,faces:[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]});
    }
    box(id,x-t/2,x+t/2,-d/2,-doorWidth/2,0,height);
    box(id,x-t/2,x+t/2,doorWidth/2,d/2,0,height);
    box(id,x-t/2,x+t/2,-doorWidth/2,doorWidth/2,doorHeight,height);
    const door=`link:${e.id}:${layout.rooms[i+1].id}`;
    box(door,x-t*.4,x+t*.4,-doorWidth/2,-doorWidth/2+.05,0,doorHeight);
    box(door,x-t*.4,x+t*.4,doorWidth/2-.05,doorWidth/2,0,doorHeight);
    box(door,x-t*.4,x+t*.4,-doorWidth/2,doorWidth/2,doorHeight-.05,doorHeight);
    box(door,x,x+doorWidth-.05,-doorWidth/2,-doorWidth/2+.04,0,doorHeight-.05);
  }
  return out;
}
