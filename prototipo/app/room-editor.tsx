'use client';
import {useEffect,useMemo,useRef,useState} from 'react';
import Viewport, {type IfcMesh, materialColor} from './viewport';
import {type Room} from '@/lib/room';
import {initialHouse,validateHouse,parseHouse,serializeHouse,layoutHouse,updateHouseRoom,addHouseRoom,updateWallLayers,commonKeys,type House,type WallId,type WallLayer} from '@/lib/house';
import {houseMeshes} from '@/lib/house-geometry';
import {sitePath} from '@/lib/site-path';
import {computeRoomMeshes,isEngineAvailable} from '@/lib/engine-client';
import {brickCatalog,rebarCatalog,initialRebarSpec,type RebarSpec} from '@/lib/materials';
import {Tabs,TabsList,TabsTrigger} from '@/components/ui/tabs';
import {Square,DoorOpen,AppWindow,Triangle,LayoutGrid,TrendingUp,Lock,Save,FolderOpen,Undo2,Scan,BrickWall,Columns3} from 'lucide-react';
const labels:Record<keyof Room,string>={width:'Largura interna',depth:'Profundidade interna',height:'Altura das paredes',thickness:'Espessura das paredes',floor:'Espessura do piso',doorWidth:'Largura da porta externa',doorHeight:'Altura da porta externa',doorOffset:'Porta: distância da esquerda',windowWidth:'Largura da janela',windowHeight:'Altura da janela',sill:'Peitoril da janela',windowOffset:'Janela: distância da esquerda'};
const elementNames:Record<string,string>={P01:'Parede norte',P02:'Parede sul',P03:'Parede oeste',P04:'Parede leste',D01:'Porta externa',J01:'Janela',F01:'Piso'};
export default function RoomEditor(){
  const [house,setHouse]=useState<House>(initialHouse),[active,setActive]=useState('r1'),[selected,select]=useState('r1:P01'),[history,setHistory]=useState<House[]>([]),[view,setView]=useState('split'),[reset,setReset]=useState(0),[message,setMessage]=useState('Adicione cômodos à direita para ampliar o projeto.');
  const [pickHistory,setPickHistory]=useState<[number,number,number][]>([]);
  const [debugOpen,setDebugOpen]=useState(false),[wireframeOn,setWireframeOn]=useState(false),[sectionCutOn,setSectionCutOn]=useState(false);
  function onPick(point:[number,number,number]){setPickHistory(h=>[point,...h].slice(0,5));}
  const input=useRef<HTMLInputElement>(null);
  const planRef=useRef<SVGSVGElement>(null);
  const dragRef=useRef<{roomId:string;key:'doorOffset'|'windowOffset';width:number}|null>(null);
  // Inside the desktop app the real engine is the whole point of running it --
  // demonstrative geometry is only a fallback for contexts without it (the web
  // prototype), so default to on instead of making every session re-enable it.
  const [engineOn,setEngineOn]=useState(isEngineAvailable),[engineStatus,setEngineStatus]=useState(''),[engineMeshes,setEngineMeshes]=useState<Record<string,IfcMesh[]>>({});
  const [roofOn,setRoofOn]=useState(false);
  const [roofType,setRoofType]=useState<'quatro'|'duas-ns'|'duas-leo'>('quatro');
  const [contravergaOn,setContravergaOn]=useState(false);
  const [rebarOn,setRebarOn]=useState(false);
  const [rebarSpec,setRebarSpec]=useState<RebarSpec>(initialRebarSpec);
  const [structureOn,setStructureOn]=useState(false);
  const [columnSize,setColumnSize]=useState(.2);
  const [beamHeight,setBeamHeight]=useState(.2);
  // Extra (intermediate) columns along a wall, on top of the 4 automatic
  // corners -- keyed by room id like engineMeshes, since the real engine
  // only ever computes the active room. Not part of House/serializeHouse
  // yet (same limitation as roof/rebar/structure itself: real-engine-only
  // options don't survive save/reload today).
  const [extraColumns,setExtraColumns]=useState<Record<string,Partial<Record<WallId,number[]>>>>({});
  const roofEdgesByType:Record<typeof roofType,('north'|'south'|'east'|'west')[]>={quatro:['north','south','east','west'],'duas-ns':['north','south'],'duas-leo':['east','west']};
  const meshes=useMemo(()=>houseMeshes(house),[house]);
  const layout=useMemo(()=>layoutHouse(house),[house]);
  const current=house.rooms.find(e=>e.id===active)??house.rooms[0];
  const room=current.room, t=room.thickness, d=room.depth;
  useEffect(()=>{
    if(!engineOn)return;
    const roomId=current.id, entry=layout.rooms.find(e=>e.id===roomId); if(!entry)return;
    const {width,depth,height,thickness,doorWidth,doorHeight,doorOffset,windowWidth,windowHeight,windowOffset,sill}=room;
    setEngineStatus('Calculando no motor IFC...');
    const timer=setTimeout(()=>{
      const roof=roofOn?{slope:.6,slopedEdges:roofEdgesByType[roofType]}:undefined;
      const nonEmpty=Object.fromEntries(Object.entries(current.wallLayers??{}).filter(([,list])=>list&&list.length>0));
      const wallLayers=Object.keys(nonEmpty).length?nonEmpty:undefined;
      const rebar=rebarOn?{longitudinal:{diameter:rebarCatalog.find(r=>r.id===rebarSpec.longitudinal)!.diameter,count:rebarSpec.longitudinalCount},stirrup:{diameter:rebarCatalog.find(r=>r.id===rebarSpec.stirrup)!.diameter,spacing:rebarSpec.stirrupSpacing}}:undefined;
      const nonEmptyColumns=Object.fromEntries(Object.entries(extraColumns[roomId]??{}).filter(([,list])=>list&&list.length>0));
      const structure=structureOn?{columnSize,beamHeight,extraColumns:Object.keys(nonEmptyColumns).length?nonEmptyColumns:undefined}:undefined;
      computeRoomMeshes({width,depth,height,thickness,doorWidth,doorHeight,doorOffset,windowWidth,windowHeight,windowOffset,sill},roof,wallLayers,contravergaOn,rebar,structure).then(result=>{
        const shifted=result.map(m=>({...m,vertices:m.vertices.map(([x,y,z])=>[x+entry.center,y,z])}));
        setEngineMeshes(prev=>({...prev,[roomId]:shifted}));
        setEngineStatus('Motor IFC atualizado.');
      }).catch(e=>setEngineStatus('Erro no motor: '+(e as Error).message));
    },250);
    return ()=>clearTimeout(timer);
  },[engineOn,roofOn,roofType,contravergaOn,rebarOn,rebarSpec,structureOn,columnSize,beamHeight,extraColumns,current.id,current.wallLayers,room.width,room.depth,room.height,room.thickness,room.doorWidth,room.doorHeight,room.doorOffset,room.windowWidth,room.windowHeight,room.windowOffset,room.sill,layout]);
  const displayMeshes=useMemo(()=>{
    if(!engineOn||!Object.keys(engineMeshes).length)return meshes;
    const engineIds=new Set(Object.keys(engineMeshes).flatMap(roomId=>['P01','P02','P03','P04','D01','J01'].map(w=>`${roomId}:${w}`)));
    return [...meshes.filter(m=>!engineIds.has(m.id)),...Object.entries(engineMeshes).flatMap(([roomId,rm])=>rm.map(m=>({...m,id:`${roomId}:${m.id}`,guid:m.guid})))];
  },[meshes,engineOn,engineMeshes]);
  function pick(id:string){select(id);const owner=id.startsWith('shared:')||id.startsWith('link:')?id.split(':')[1]:id.split(':')[0];setActive(owner);}
  const [selRoomId,selPart]=selected.split(':');
  const wallIds:WallId[]=['P01','P02','P03','P04'];
  const isWallSelected=isEngineAvailable()&&engineOn&&selRoomId===current.id&&(wallIds as string[]).includes(selPart);
  const selectedLayers=isWallSelected?(current.wallLayers?.[selPart as WallId]??[]):[];
  const selectedColumns=isWallSelected?(extraColumns[current.id]?.[selPart as WallId]??[]):[];
  function wallLength(wallId:WallId){return wallId==='P01'||wallId==='P02'?room.width:room.depth;}
  function setColumnsFor(wallId:WallId,list:number[]){setExtraColumns(prev=>({...prev,[current.id]:{...(prev[current.id]??{}),[wallId]:list}}));}
  function addColumn(){const wallId=selPart as WallId,length=wallLength(wallId);setColumnsFor(wallId,[...selectedColumns,Math.round(length/2*100)/100]);setMessage('Pilar adicionado no meio da parede. Ajuste a distância pelo campo.');}
  function updateColumn(i:number,value:number){setColumnsFor(selPart as WallId,selectedColumns.map((v,idx)=>idx===i?value:v));}
  function removeColumn(i:number){setColumnsFor(selPart as WallId,selectedColumns.filter((_,idx)=>idx!==i));setMessage('Pilar removido.');}
  function setWallLayers(list:WallLayer[]){try{const next=updateWallLayers(house,current.id,selPart as WallId,list);setHistory(h=>[...h.slice(-49),house]);setHouse(next);setMessage('Camadas da parede atualizadas.');}catch(e){setMessage((e as Error).message);}}
  function addLayer(){setWallLayers([...selectedLayers,{material:'Novo material',thickness:.1}]);}
  function addBrickLayer(brick:typeof brickCatalog[number]){setWallLayers([...selectedLayers,{material:brick.name,thickness:brick.width}]);}
  function updateLayer(i:number,patch:Partial<WallLayer>){setWallLayers(selectedLayers.map((l,idx)=>idx===i?{...l,...patch}:l));}
  function removeLayer(i:number){setWallLayers(selectedLayers.filter((_,idx)=>idx!==i));}
  function beginDrag(e:React.PointerEvent,roomId:string,key:'doorOffset'|'windowOffset',width:number){e.currentTarget.setPointerCapture(e.pointerId);setHistory(h=>[...h.slice(-49),house]);dragRef.current={roomId,key,width};pick(`${roomId}:${key==='doorOffset'?'D01':'J01'}`);moveDrag(e);}
  function moveDrag(e:React.PointerEvent){const drag=dragRef.current,svg=planRef.current;if(!drag||!svg)return;const pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;const ctm=svg.getScreenCTM();if(!ctm)return;const p=pt.matrixTransform(ctm.inverse());const entry=layout.rooms.find(r=>r.id===drag.roomId);if(!entry)return;const raw=p.x-entry.center+entry.room.width/2-drag.width/2;const value=Math.round(Math.min(Math.max(raw,.1),entry.room.width-drag.width-.1)*100)/100;try{setHouse(updateHouseRoom(house,drag.roomId,drag.key,value));}catch{}}
  function endDrag(){if(dragRef.current){dragRef.current=null;setMessage('Posição ajustada por arraste. Enquadre em planta para conferir.');}}
  function apply(change:()=>House,focus?:string){try{const next=validateHouse(change());setHistory(h=>[...h.slice(-49),house]);setHouse(next);const target=next.rooms.find(e=>e.id===(focus??current.id))??next.rooms[0];setActive(target.id);select(`${target.id}:F01`);setMessage('Projeto atualizado em planta e 3D.');if(next.rooms.length!==house.rooms.length)setReset(v=>v+1);return true;}catch(e){setMessage((e as Error).message);return false;}}
  function save(){try{localStorage.setItem('brabim-house-v1',serializeHouse(house));setMessage('Projeto salvo neste navegador. Exporte um arquivo para compartilhar.');}catch{setMessage('Não foi possível salvar neste navegador. Use Exportar arquivo.');}}
  function restore(){try{const text=localStorage.getItem('brabim-house-v1')??localStorage.getItem('brabim-room-v1');if(!text)throw Error('Nenhum projeto salvo neste navegador.');apply(()=>parseHouse(text));setReset(v=>v+1);}catch(e){setMessage((e as Error).message);}}
  function download(){const url=URL.createObjectURL(new Blob([serializeHouse(house)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='projeto.brabim.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setMessage('Arquivo do projeto preparado para download.');}
  function downloadDebug(){
    const payload={geradoEm:new Date().toISOString(),cômodoAtivo:current.id,motorReal:engineOn,telhado:roofOn?roofType:false,estrutura:structureOn?{columnSize,beamHeight,pilaresIntermediarios:extraColumns[current.id]}:false,camadasDeParede:current.wallLayers,parâmetrosDoCômodo:room,malhasExibidas:displayMeshes};
    const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='brabim-depuracao.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    setMessage('Dados de depuração exportados (vértices/faces reais na tela).');
  }
  const items=[...new Set(meshes.map(m=>m.id))].filter(id=>id.split(':').includes(current.id));
  const area=house.rooms.reduce((sum,e)=>sum+e.room.width*e.room.depth,0);
  function name(id:string){if(id.startsWith('shared:'))return 'Parede compartilhada';if(id.startsWith('link:'))return 'Porta de ligação';return elementNames[id.split(':')[1]]??id;}
  return <main className="editor">
    <header className="titlebar"><strong><span className="brandmark">B</span> BRABIM</strong><span>Casa · ambientes conectados</span><a href={sitePath('/ensaios/')}>Ensaios IFC →</a></header>
    <div className="tabs-row">
      <div className="disc-tab active">Arquitetura</div>
      <div className="disc-tab locked">Estrutura<Lock className="lock" size={11}/></div>
      <div className="disc-tab locked">Instalações<Lock className="lock" size={11}/></div>
      <div className="disc-tab locked">Documentação<Lock className="lock" size={11}/></div>
    </div>
    <div className="ribbon">
      <div className="tools">
        <div className="toolgroup">
          <button onClick={save} title="Salvar no navegador"><Save size={16}/></button>
          <button onClick={restore} title="Reabrir salvo"><FolderOpen size={16}/></button>
          <button onClick={download} title="Exportar arquivo">Exportar</button>
          <button onClick={()=>input.current?.click()} title="Abrir arquivo">Abrir</button>
        </div>
        <div className="toolgroup">
          <button disabled={!history.length} title="Desfazer" onClick={()=>{const previous=history.at(-1)!;setHouse(previous);setActive(previous.rooms[0].id);select(`${previous.rooms[0].id}:F01`);setHistory(h=>h.slice(0,-1));setReset(v=>v+1);setMessage('Última alteração desfeita.');}}><Undo2 size={16}/></button>
          <button onClick={()=>setReset(v=>v+1)} title="Enquadrar 3D"><Scan size={16}/></button>
        </div>
        <input ref={input} hidden type="file" accept=".json" onChange={async e=>{const file=e.target.files?.[0];if(file)try{if(file.size>100000)throw Error('Arquivo muito grande.');const text=await file.text();apply(()=>parseHouse(text));setReset(v=>v+1);}catch(error){setMessage((error as Error).message);}e.target.value='';}}/>
        <div className="toolgroup">
          <button className={`tool${isWallSelected?' active':''}`} onClick={()=>{const at=isWallSelected?wallIds.indexOf(selPart as WallId):-1;pick(`${current.id}:${wallIds[(at+1)%wallIds.length]}`);}} title="Parede (clique de novo para alternar)"><BrickWall/>Parede</button>
          <button className={`tool${selPart==='F01'?' active':''}`} onClick={()=>pick(`${current.id}:F01`)} title="Ambiente"><Square/>Ambiente</button>
          <button className={`tool${selPart==='D01'?' active':''}`} onClick={()=>pick(`${current.id}:D01`)} title="Porta"><DoorOpen/>Porta</button>
          <button className={`tool${selPart==='J01'?' active':''}`} onClick={()=>pick(`${current.id}:J01`)} title="Janela"><AppWindow/>Janela</button>
          {isEngineAvailable()&&<button className={`tool${roofOn?' active':''}`} onClick={()=>setRoofOn(v=>!v)} title="Telhado"><Triangle/>Telhado</button>}
          {isEngineAvailable()&&<button className={`tool${structureOn?' active':''}`} onClick={()=>setStructureOn(v=>!v)} title="Pilares nos 4 cantos e viga de cinta no topo das paredes"><Columns3/>Estrutura</button>}
          <button className="tool locked" disabled title="Laje (em breve)"><LayoutGrid/>Laje</button>
          <button className="tool locked" disabled title="Escada (em breve)"><TrendingUp/>Escada</button>
        </div>
        {isEngineAvailable()&&roofOn&&<select value={roofType} onChange={e=>setRoofType(e.target.value as typeof roofType)}>
          <option value="quatro">Quatro águas</option>
          <option value="duas-ns">Duas águas (cumeeira leste-oeste)</option>
          <option value="duas-leo">Duas águas (cumeeira norte-sul)</option>
        </select>}
        {isEngineAvailable()&&structureOn&&<>
          <label title="Lado da seção do pilar (m)">Pilar <input type="number" min={.1} max={.4} step={.01} value={columnSize} onChange={e=>setColumnSize(Number(e.target.value))} style={{width:'4em'}} aria-label="Lado do pilar em metros"/></label>
          <label title="Altura da viga de cinta no topo da parede (m)">Cinta <input type="number" min={.1} max={.4} step={.01} value={beamHeight} onChange={e=>setBeamHeight(Number(e.target.value))} style={{width:'4em'}} aria-label="Altura da viga de cinta em metros"/></label>
        </>}
        {isEngineAvailable()&&<label title="Verga fica sempre sobre porta e janela; contraverga abaixo do peitoril é opcional."><input type="checkbox" checked={contravergaOn} onChange={e=>setContravergaOn(e.target.checked)}/>Contraverga</label>}
        {isEngineAvailable()&&<label title="Ferro real dentro da verga/contraverga e, se ligados, dos pilares e vigas (geometria e quantitativo, não dimensionamento estrutural)."><input type="checkbox" checked={rebarOn} onChange={e=>setRebarOn(e.target.checked)}/>Armação</label>}
        {isEngineAvailable()&&rebarOn&&<>
          <select value={rebarSpec.longitudinal} onChange={e=>setRebarSpec(s=>({...s,longitudinal:e.target.value}))} title="Bitola das barras longitudinais">
            {rebarCatalog.map(r=><option key={r.id} value={r.id}>Ø{r.id} {r.steelClass}</option>)}
          </select>
          <input type="number" min={2} max={8} step={1} value={rebarSpec.longitudinalCount} onChange={e=>setRebarSpec(s=>({...s,longitudinalCount:Number(e.target.value)}))} style={{width:'3.5em'}} title="Quantidade de barras longitudinais" aria-label="Quantidade de barras longitudinais"/>
          <select value={rebarSpec.stirrup} onChange={e=>setRebarSpec(s=>({...s,stirrup:e.target.value}))} title="Bitola do estribo">
            {rebarCatalog.map(r=><option key={r.id} value={r.id}>estribo Ø{r.id}</option>)}
          </select>
          <input type="number" min={.05} max={.4} step={.01} value={rebarSpec.stirrupSpacing} onChange={e=>setRebarSpec(s=>({...s,stirrupSpacing:Number(e.target.value)}))} style={{width:'4em'}} title="Espaçamento do estribo (m)" aria-label="Espaçamento do estribo em metros"/>
        </>}
        <div className="field" style={{marginLeft:'auto'}}>
          {isEngineAvailable()&&<label><input type="checkbox" checked={engineOn} onChange={e=>{setEngineOn(e.target.checked);if(!e.target.checked)setEngineStatus('');}}/>Motor real (IFC){engineStatus?` · ${engineStatus}`:''}</label>}
          <button onClick={()=>setDebugOpen(v=>!v)}>{debugOpen?'Fechar ferramentas':'Ferramentas de depuração'}</button>
        </div>
      </div>
    </div>
    {debugOpen&&<div className="debug-panel">
      <div className="tools">
        <label><input type="checkbox" checked={wireframeOn} onChange={e=>setWireframeOn(e.target.checked)}/>Wireframe</label>
        <label><input type="checkbox" checked={sectionCutOn} onChange={e=>setSectionCutOn(e.target.checked)}/>Corte (metade frontal)</label>
        <button onClick={downloadDebug}>Baixar dados de depuração (JSON)</button>
        <button onClick={()=>setPickHistory([])} disabled={!pickHistory.length}>Limpar cliques</button>
        {pickHistory.length>0&&<div style={{display:'flex',flexDirection:'column',gap:'.15em',fontSize:'.85em',fontFamily:'monospace'}}>
          {pickHistory.map((p,i)=><span key={i}>#{pickHistory.length-i} x={p[0].toFixed(3)} y={p[1].toFixed(3)} altura={p[2].toFixed(3)}{i===0&&pickHistory[1]?` · dist. do #${pickHistory.length-1}=${Math.hypot(p[0]-pickHistory[1][0],p[1]-pickHistory[1][1],p[2]-pickHistory[1][2]).toFixed(3)}m`:''}</span>)}
        </div>}
      </div>
    </div>}
    <div className="workspace">
      <aside className="properties nav"><h2>Navegador do projeto</h2>
      <section className="navigator">{house.rooms.map(e=><button key={e.id} className={current.id===e.id?'selected':''} onClick={()=>pick(`${e.id}:F01`)}>{e.name}<small>{(e.room.width*e.room.depth).toFixed(2)} m²</small></button>)}
        <button disabled={house.rooms.length>=8} onClick={()=>{try{const next=addHouseRoom(house);apply(()=>next,next.rooms.at(-1)!.id);}catch(e){setMessage((e as Error).message);}}}>+ Cômodo à direita</button>
        <button disabled={house.rooms.length===1} onClick={()=>apply(()=>({rooms:house.rooms.filter(e=>e.id!==current.id)}))}>Remover cômodo selecionado</button>
        <div className="nav-branch">Estrutura<Lock className="lock" size={11}/></div>
        <div className="nav-branch">Instalações<Lock className="lock" size={11}/></div>
      </section>
      <section><h3>Parâmetros · {current.name}</h3><label htmlFor="room-name">Nome do ambiente</label><input id="room-name" key={`${current.id}:${current.name}`} defaultValue={current.name} maxLength={50} onBlur={e=>{const value=e.target.value.trim();if(value!==current.name)apply(()=>({rooms:house.rooms.map(r=>r.id===current.id?{...r,name:value}:r)}));e.target.value=current.name;}} onKeyDown={e=>{if(e.key==='Enter')e.currentTarget.blur();}}/>
      {(Object.keys(labels) as (keyof Room)[]).map(key=><div key={key}><label htmlFor={key}>{labels[key]}{(commonKeys as readonly string[]).includes(key)?' · todos':''}</label><input id={key} key={`${current.id}:${room[key]}`} type="number" step="0.05" defaultValue={room[key]} onBlur={e=>{const value=Number(e.target.value);if(e.target.value.trim()!==''&&value!==room[key])apply(()=>updateHouseRoom(house,current.id,key,value));e.target.value=String(room[key]);}} onKeyDown={e=>{if(e.key==='Enter')e.currentTarget.blur();}}/></div>)}
      <p className="hint">Medidas em metros. Arraste a porta ou a janela na planta para reposicionar; os campos de distância continuam disponíveis para ajuste fino. Enter aplica. Cada divisão tem uma porta central de 0,90 m.</p><p className="hint">Nesta etapa, cômodos alinhados lado a lado. Remover um ambiente aproxima os restantes.</p></section>
      <section className="navigator"><h3>Elementos</h3>{items.map(id=><button key={id} className={selected===id?'selected':''} onClick={()=>pick(id)}>{name(id)}<small>{id}</small></button>)}</section>
    </aside>
    <div className="drawing"><div className="viewbar"><Tabs value={view} onValueChange={v=>setView(String(v))}><TabsList><TabsTrigger value="plan">Planta</TabsTrigger><TabsTrigger value="3d">3D</TabsTrigger><TabsTrigger value="split">Lado a lado</TabsTrigger></TabsList></Tabs><span>{area.toFixed(2)} m² internos</span></div>
    <div className={`views ${view==='split'?'split':''}`}>
      {view!=='3d'&&<section className="view plan"><div className="view-title">Planta · {current.name}</div><svg ref={planRef} className="plan-svg" viewBox={`${-layout.width/2-t-1} ${-d/2-t-1} ${layout.width+2*t+2} ${d+2*t+2}`} aria-label="Planta dos ambientes conectados" onPointerMove={moveDrag} onPointerUp={endDrag}>
        {layout.rooms.map(e=><rect key={e.id} x={e.left} y={-d/2} width={e.room.width} height={d} fill={current.id===e.id?'#262b30':'#1e2226'} onClick={()=>pick(`${e.id}:F01`)}/>)}
        {displayMeshes.flatMap((m,i)=>{const zs=m.vertices.map(v=>v[2]);if(Math.min(...zs)>1.2||Math.max(...zs)<1.2)return[];const xs=m.vertices.map(v=>v[0]),ys=m.vertices.map(v=>-v[1]);const opening=m.id.includes(':D01')||m.id.includes(':J01')||m.id.startsWith('link:');const fill=selected===m.id?'#3fa9e0':(m as IfcMesh).material?materialColor((m as IfcMesh).material!):opening?'#8a6f52':'#5b6771';
          const [roomId,part]=m.id.split(':');const engineRoom=engineMeshes[roomId]&&house.rooms.find(r=>r.id===roomId)?.room;
          if(engineRoom&&(part==='P01'||part==='P02'||part.startsWith('P01-')||part.startsWith('P02-'))){const entry=layout.rooms.find(e=>e.id===roomId)!;const {offset,width}=part.startsWith('P01')?{offset:engineRoom.windowOffset,width:engineRoom.windowWidth}:{offset:engineRoom.doorOffset,width:engineRoom.doorWidth};const gapLeft=entry.center-engineRoom.width/2+offset,gapRight=gapLeft+width,minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);return[<rect key={`${i}a`} x={minX} y={minY} width={gapLeft-minX} height={maxY-minY} fill={fill} onClick={()=>pick(m.id)}/>,<rect key={`${i}b`} x={gapRight} y={minY} width={maxX-gapRight} height={maxY-minY} fill={fill} onClick={()=>pick(m.id)}/>];}
          return[<rect key={i} x={Math.min(...xs)} y={Math.min(...ys)} width={Math.max(...xs)-Math.min(...xs)} height={Math.max(...ys)-Math.min(...ys)} fill={fill} onClick={()=>pick(m.id)}/>];})}
        {layout.rooms.map(e=><g key={`${e.id}-drag`}>
          <rect x={e.left} y={d/2} width={e.room.width} height={t} fill="transparent" style={{cursor:'ew-resize',touchAction:'none'}} pointerEvents="all" onPointerDown={ev=>beginDrag(ev,e.id,'doorOffset',e.room.doorWidth)}/>
          <rect x={e.left} y={-d/2-t} width={e.room.width} height={t} fill="transparent" style={{cursor:'ew-resize',touchAction:'none'}} pointerEvents="all" onPointerDown={ev=>beginDrag(ev,e.id,'windowOffset',e.room.windowWidth)}/>
        </g>)}
        {layout.rooms.map(e=><g key={e.id} onClick={()=>pick(`${e.id}:F01`)} style={{cursor:'pointer'}}><text x={e.center} y="-.15" fontSize=".22" textAnchor="middle" fill="#c3ccd3">{e.name}</text><text x={e.center} y=".2" fontSize=".18" textAnchor="middle" fill="#8b95a0">{e.room.width.toFixed(2)} × {d.toFixed(2)} m</text></g>)}
      </svg></section>}
      {view!=='plan'&&<section className="view three"><Viewport walls={[]} meshes={displayMeshes} selected={selected} onSelect={pick} onPick={onPick} reset={reset} hideFloor wireframe={wireframeOn} sectionCut={sectionCutOn}/><div className="view-caption">Arraste para orbitar · roda para aproximar · clique num elemento mostra a coordenada exata (abra "Ferramentas de depuração")</div></section>}
    </div></div>
    <aside className="properties inspector"><h2>Propriedades<span>{isWallSelected?elementNames[selPart]:name(selected)}</span></h2>
      {isWallSelected?<>
        <section>
          <h3>Camadas</h3>
          {selectedLayers.map((l,i)=><div key={i} className="layer-row">
            <input className="layer-name" value={l.material} onChange={e=>updateLayer(i,{material:e.target.value})} aria-label="Material da camada"/>
            <input type="number" step="0.005" min="0.005" max="0.5" value={l.thickness} onChange={e=>updateLayer(i,{thickness:Number(e.target.value)})} aria-label="Espessura da camada (m)"/>
            <button onClick={()=>removeLayer(i)} title="Remover camada">×</button>
          </div>)}
          <button onClick={addLayer} style={{marginTop:'8px'}}>+ Camada em branco</button>
          {selectedLayers.length>0&&<p className="hint">Espessura oficial (layout/telhado): {t.toFixed(2)} m · soma das camadas (visual): {selectedLayers.reduce((s,l)=>s+l.thickness,0).toFixed(3)} m</p>}
        </section>
        <section aria-label="Catálogo de tijolos e blocos"><h3>Catálogo</h3>
          <div className="brick-strip">
            {brickCatalog.map(brick=><button key={brick.id} className="brick-card" onClick={()=>addBrickLayer(brick)} title={`Adicionar camada: ${brick.name} (${(brick.width*100).toFixed(1)} cm)`}>
              <span className="brick-thumb"><img src={sitePath(brick.image)} alt={brick.name} onError={e=>{(e.target as HTMLImageElement).style.display='none';}}/></span>
              <span className="name">{brick.name}</span>
              <span className="meta">{(brick.width*100).toFixed(1)} cm · {brick.piecesPerM2}/m²</span>
            </button>)}
          </div>
        </section>
        {structureOn&&<section>
          <h3>Pilares intermediários</h3>
          {selectedColumns.map((offset,i)=><div key={i} className="layer-row">
            <input type="number" step="0.05" min={0} max={wallLength(selPart as WallId)} value={offset} onChange={e=>updateColumn(i,Number(e.target.value))} aria-label={`Distância do pilar ${i+1} até o início da parede (m)`}/>
            <button onClick={()=>removeColumn(i)} title="Remover pilar">×</button>
          </div>)}
          <button onClick={addColumn} style={{marginTop:'8px'}}>+ Pilar nesta parede</button>
          <p className="hint">Distância do início da parede, mesmo referencial de porta/janela. Os 4 pilares de canto são automáticos e não aparecem aqui.</p>
        </section>}
        <section><h3>Material estrutural</h3><label style={{opacity:.4}}><span>Resistência</span><Lock size={13}/></label></section>
      </>:<div className="empty-inspector">{isEngineAvailable()?'Selecione uma parede (P01-P04) para editar as camadas e pilares.':'Ligue o motor real (IFC) para editar camadas de parede.'}</div>}
    </aside>
    </div>
    <footer><span role="status">{message}</span><span className="footer-right">{pickHistory[0]?`Último clique: x=${pickHistory[0][0].toFixed(3)} y=${pickHistory[0][1].toFixed(3)} z(altura)=${pickHistory[0][2].toFixed(3)}`:'Geometria demonstrativa · sem recálculo IFC'}</span></footer>
  </main>;
}
