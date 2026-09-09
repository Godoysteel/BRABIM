'use client';
import {useEffect,useMemo,useRef,useState} from 'react';
import Viewport, {type IfcMesh} from './viewport';
import {type Room} from '@/lib/room';
import {initialHouse,validateHouse,parseHouse,serializeHouse,layoutHouse,updateHouseRoom,addHouseRoom,commonKeys,type House} from '@/lib/house';
import {houseMeshes} from '@/lib/house-geometry';
import {sitePath} from '@/lib/site-path';
import {computeRoomMeshes,isEngineAvailable} from '@/lib/engine-client';
import {Tabs,TabsList,TabsTrigger} from '@/components/ui/tabs';
const labels:Record<keyof Room,string>={width:'Largura interna',depth:'Profundidade interna',height:'Altura das paredes',thickness:'Espessura das paredes',floor:'Espessura do piso',doorWidth:'Largura da porta externa',doorHeight:'Altura da porta externa',doorOffset:'Porta: distância da esquerda',windowWidth:'Largura da janela',windowHeight:'Altura da janela',sill:'Peitoril da janela',windowOffset:'Janela: distância da esquerda'};
const elementNames:Record<string,string>={P01:'Parede norte',P02:'Parede sul',P03:'Parede oeste',P04:'Parede leste',D01:'Porta externa',J01:'Janela',F01:'Piso'};
export default function RoomEditor(){
  const [house,setHouse]=useState<House>(initialHouse),[active,setActive]=useState('r1'),[selected,select]=useState('r1:P01'),[history,setHistory]=useState<House[]>([]),[view,setView]=useState('split'),[reset,setReset]=useState(0),[message,setMessage]=useState('Adicione cômodos à direita para ampliar o projeto.');
  const input=useRef<HTMLInputElement>(null);
  const planRef=useRef<SVGSVGElement>(null);
  const dragRef=useRef<{roomId:string;key:'doorOffset'|'windowOffset';width:number}|null>(null);
  const [engineOn,setEngineOn]=useState(false),[engineStatus,setEngineStatus]=useState(''),[engineMeshes,setEngineMeshes]=useState<Record<string,IfcMesh[]>>({});
  const meshes=useMemo(()=>houseMeshes(house),[house]);
  const layout=useMemo(()=>layoutHouse(house),[house]);
  const current=house.rooms.find(e=>e.id===active)??house.rooms[0];
  const room=current.room, t=room.thickness, d=room.depth;
  useEffect(()=>{
    if(!engineOn)return;
    const roomId=current.id, entry=layout.rooms.find(e=>e.id===roomId); if(!entry)return;
    const params={width:room.width,depth:room.depth,height:room.height,thickness:room.thickness};
    setEngineStatus('Calculando no motor IFC...');
    const timer=setTimeout(()=>{
      computeRoomMeshes(params).then(result=>{
        const shifted=result.map(m=>({...m,vertices:m.vertices.map(([x,y,z])=>[x+entry.center,y,z])}));
        setEngineMeshes(prev=>({...prev,[roomId]:shifted}));
        setEngineStatus('Motor IFC atualizado.');
      }).catch(e=>setEngineStatus('Erro no motor: '+(e as Error).message));
    },250);
    return ()=>clearTimeout(timer);
  },[engineOn,current.id,room.width,room.depth,room.height,room.thickness,layout]);
  const displayMeshes=useMemo(()=>{
    if(!engineOn||!Object.keys(engineMeshes).length)return meshes;
    const engineIds=new Set(Object.keys(engineMeshes).flatMap(roomId=>['P01','P02','P03','P04'].map(w=>`${roomId}:${w}`)));
    return [...meshes.filter(m=>!engineIds.has(m.id)),...Object.entries(engineMeshes).flatMap(([roomId,rm])=>rm.map(m=>({...m,id:`${roomId}:${m.id}`,guid:m.guid})))];
  },[meshes,engineOn,engineMeshes]);
  function pick(id:string){select(id);const owner=id.startsWith('shared:')||id.startsWith('link:')?id.split(':')[1]:id.split(':')[0];setActive(owner);}
  function beginDrag(e:React.PointerEvent,roomId:string,key:'doorOffset'|'windowOffset',width:number){e.currentTarget.setPointerCapture(e.pointerId);setHistory(h=>[...h.slice(-49),house]);dragRef.current={roomId,key,width};pick(`${roomId}:${key==='doorOffset'?'D01':'J01'}`);moveDrag(e);}
  function moveDrag(e:React.PointerEvent){const drag=dragRef.current,svg=planRef.current;if(!drag||!svg)return;const pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;const ctm=svg.getScreenCTM();if(!ctm)return;const p=pt.matrixTransform(ctm.inverse());const entry=layout.rooms.find(r=>r.id===drag.roomId);if(!entry)return;const raw=p.x-entry.center+entry.room.width/2-drag.width/2;const value=Math.round(Math.min(Math.max(raw,.1),entry.room.width-drag.width-.1)*100)/100;try{setHouse(updateHouseRoom(house,drag.roomId,drag.key,value));}catch{}}
  function endDrag(){if(dragRef.current){dragRef.current=null;setMessage('Posição ajustada por arraste. Enquadre em planta para conferir.');}}
  function apply(change:()=>House,focus?:string){try{const next=validateHouse(change());setHistory(h=>[...h.slice(-49),house]);setHouse(next);const target=next.rooms.find(e=>e.id===(focus??current.id))??next.rooms[0];setActive(target.id);select(`${target.id}:F01`);setMessage('Projeto atualizado em planta e 3D.');if(next.rooms.length!==house.rooms.length)setReset(v=>v+1);return true;}catch(e){setMessage((e as Error).message);return false;}}
  function save(){try{localStorage.setItem('brabim-house-v1',serializeHouse(house));setMessage('Projeto salvo neste navegador. Exporte um arquivo para compartilhar.');}catch{setMessage('Não foi possível salvar neste navegador. Use Exportar arquivo.');}}
  function restore(){try{const text=localStorage.getItem('brabim-house-v1')??localStorage.getItem('brabim-room-v1');if(!text)throw Error('Nenhum projeto salvo neste navegador.');apply(()=>parseHouse(text));setReset(v=>v+1);}catch(e){setMessage((e as Error).message);}}
  function download(){const url=URL.createObjectURL(new Blob([serializeHouse(house)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='projeto.brabim.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setMessage('Arquivo do projeto preparado para download.');}
  const items=[...new Set(meshes.map(m=>m.id))].filter(id=>id.split(':').includes(current.id));
  const area=house.rooms.reduce((sum,e)=>sum+e.room.width*e.room.depth,0);
  function name(id:string){if(id.startsWith('shared:'))return 'Parede compartilhada';if(id.startsWith('link:'))return 'Porta de ligação';return elementNames[id.split(':')[1]]??id;}
  return <main className="editor">
    <header className="titlebar"><strong><span className="brandmark">B</span> BRABIM</strong><span>Casa · ambientes conectados</span><a href={sitePath('/ensaios/')}>Ensaios IFC →</a></header>
    <div className="tools" style={{flexWrap:'wrap',background:'#fafbfc'}}>
      <button onClick={save}>Salvar no navegador</button><button onClick={restore}>Reabrir salvo</button><button onClick={download}>Exportar arquivo</button><button onClick={()=>input.current?.click()}>Abrir arquivo</button>
      <button disabled={!history.length} onClick={()=>{const previous=history.at(-1)!;setHouse(previous);setActive(previous.rooms[0].id);select(`${previous.rooms[0].id}:F01`);setHistory(h=>h.slice(0,-1));setReset(v=>v+1);setMessage('Última alteração desfeita.');}}>Desfazer</button><button onClick={()=>setReset(v=>v+1)}>Enquadrar 3D</button>
      <input ref={input} hidden type="file" accept=".json" onChange={async e=>{const file=e.target.files?.[0];if(file)try{if(file.size>100000)throw Error('Arquivo muito grande.');const text=await file.text();apply(()=>parseHouse(text));setReset(v=>v+1);}catch(error){setMessage((error as Error).message);}e.target.value='';}}/>
      {isEngineAvailable()&&<label style={{display:'flex',alignItems:'center',gap:'.4em',marginLeft:'auto'}}><input type="checkbox" checked={engineOn} onChange={e=>{setEngineOn(e.target.checked);if(!e.target.checked)setEngineStatus('');}}/>Motor real (IFC) · {current.name}{engineStatus?` · ${engineStatus}`:''}</label>}
    </div>
    <div className="workspace"><aside className="properties"><h2>Ambientes · {house.rooms.length} de 8</h2>
      <section className="navigator">{house.rooms.map(e=><button key={e.id} className={current.id===e.id?'selected':''} onClick={()=>pick(`${e.id}:F01`)}>{e.name}<small>{(e.room.width*e.room.depth).toFixed(2)} m²</small></button>)}
        <button disabled={house.rooms.length>=8} onClick={()=>{try{const next=addHouseRoom(house);apply(()=>next,next.rooms.at(-1)!.id);}catch(e){setMessage((e as Error).message);}}}>+ Cômodo à direita</button>
        <button disabled={house.rooms.length===1} onClick={()=>apply(()=>({rooms:house.rooms.filter(e=>e.id!==current.id)}))}>Remover cômodo selecionado</button>
      </section>
      <section><label htmlFor="room-name">Nome do ambiente</label><input id="room-name" key={`${current.id}:${current.name}`} defaultValue={current.name} maxLength={50} onBlur={e=>{const value=e.target.value.trim();if(value!==current.name)apply(()=>({rooms:house.rooms.map(r=>r.id===current.id?{...r,name:value}:r)}));e.target.value=current.name;}} onKeyDown={e=>{if(e.key==='Enter')e.currentTarget.blur();}}/>
      {(Object.keys(labels) as (keyof Room)[]).map(key=><div key={key}><label htmlFor={key}>{labels[key]}{(commonKeys as readonly string[]).includes(key)?' · todos':''}</label><input id={key} key={`${current.id}:${room[key]}`} type="number" step="0.05" defaultValue={room[key]} onBlur={e=>{const value=Number(e.target.value);if(e.target.value.trim()!==''&&value!==room[key])apply(()=>updateHouseRoom(house,current.id,key,value));e.target.value=String(room[key]);}} onKeyDown={e=>{if(e.key==='Enter')e.currentTarget.blur();}}/></div>)}
      <p className="hint">Medidas em metros. Arraste a porta ou a janela na planta para reposicionar; os campos de distância continuam disponíveis para ajuste fino. Enter aplica. Cada divisão tem uma porta central de 0,90 m.</p><p className="hint">Nesta etapa, cômodos alinhados lado a lado. Remover um ambiente aproxima os restantes.</p></section>
      <section className="navigator">{items.map(id=><button key={id} className={selected===id?'selected':''} onClick={()=>pick(id)}>{name(id)}<small>{id}</small></button>)}</section>
    </aside><div className="drawing"><div className="viewbar"><Tabs value={view} onValueChange={v=>setView(String(v))}><TabsList><TabsTrigger value="plan">Planta</TabsTrigger><TabsTrigger value="3d">3D</TabsTrigger><TabsTrigger value="split">Lado a lado</TabsTrigger></TabsList></Tabs><span>{area.toFixed(2)} m² internos</span></div>
    <div className={`views ${view==='split'?'split':''}`}>
      {view!=='3d'&&<section className="view plan"><div className="view-title">Planta · {current.name}</div><svg ref={planRef} className="plan-svg" viewBox={`${-layout.width/2-t-1} ${-d/2-t-1} ${layout.width+2*t+2} ${d+2*t+2}`} aria-label="Planta dos ambientes conectados" onPointerMove={moveDrag} onPointerUp={endDrag}>
        {layout.rooms.map(e=><rect key={e.id} x={e.left} y={-d/2} width={e.room.width} height={d} fill={current.id===e.id?'#e1eff6':'#f2f4f5'} onClick={()=>pick(`${e.id}:F01`)}/>)}
        {displayMeshes.map((m,i)=>{const zs=m.vertices.map(v=>v[2]);if(Math.min(...zs)>1.2||Math.max(...zs)<1.2)return null;const xs=m.vertices.map(v=>v[0]),ys=m.vertices.map(v=>-v[1]);const opening=m.id.includes(':D01')||m.id.includes(':J01')||m.id.startsWith('link:');return <rect key={i} x={Math.min(...xs)} y={Math.min(...ys)} width={Math.max(...xs)-Math.min(...xs)} height={Math.max(...ys)-Math.min(...ys)} fill={selected===m.id?'#168ac0':opening?'#a38b6b':'#657a88'} onClick={()=>pick(m.id)}/>;})}
        {layout.rooms.map(e=><g key={`${e.id}-drag`}>
          <rect x={e.left} y={d/2} width={e.room.width} height={t} fill="transparent" style={{cursor:'ew-resize',touchAction:'none'}} pointerEvents="all" onPointerDown={ev=>beginDrag(ev,e.id,'doorOffset',e.room.doorWidth)}/>
          <rect x={e.left} y={-d/2-t} width={e.room.width} height={t} fill="transparent" style={{cursor:'ew-resize',touchAction:'none'}} pointerEvents="all" onPointerDown={ev=>beginDrag(ev,e.id,'windowOffset',e.room.windowWidth)}/>
        </g>)}
        {layout.rooms.map(e=><g key={e.id} onClick={()=>pick(`${e.id}:F01`)} style={{cursor:'pointer'}}><text x={e.center} y="-.15" fontSize=".22" textAnchor="middle" fill="#425d6d">{e.name}</text><text x={e.center} y=".2" fontSize=".18" textAnchor="middle" fill="#687e8d">{e.room.width.toFixed(2)} × {d.toFixed(2)} m</text></g>)}
      </svg></section>}
      {view!=='plan'&&<section className="view three"><Viewport walls={[]} meshes={displayMeshes} selected={selected} onSelect={pick} reset={reset} hideFloor/><div className="view-caption">Arraste para orbitar · roda para aproximar</div></section>}
    </div></div></div><footer><span role="status">{message}</span><span className="footer-right">Geometria demonstrativa · sem recálculo IFC</span></footer>
  </main>;
}
