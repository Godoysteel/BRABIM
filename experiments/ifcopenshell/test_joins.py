"""Reproducible IFC wall-join experiment; no custom join algorithm."""
import sys, pathlib, time, json, itertools, math
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.runtime/python'))
import ifcopenshell, ifcopenshell.api as api, ifcopenshell.geom
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
OUT = pathlib.Path(__file__).parent / 'results'
OUT.mkdir(exist_ok=True)
BASE = [((-4,-2.5),(4,-2.5)),((-4,2.5),(4,2.5)),((-4,-2.5),(-4,2.5)),((4,-2.5),(4,2.5)),((1,-2.5),(1,2.5))]
LINKS = [(0,2,'ATSTART','ATSTART'),(0,3,'ATEND','ATSTART'),(1,2,'ATSTART','ATEND'),(1,3,'ATEND','ATEND'),(0,4,'ATPATH','ATSTART'),(1,4,'ATPATH','ATEND')]
def run(name, thicknesses, heights):
    start=time.perf_counter()
    f=ifcopenshell.file(schema='IFC4')
    project=api.run('root.create_entity', f, ifc_class='IfcProject',name='BRABIM test')
    unit=api.run('unit.add_si_unit',f,unit_type='LENGTHUNIT')
    api.run('unit.assign_unit',f,units=[unit])
    model=api.run('context.add_context',f,context_type='Model')
    body=api.run('context.add_context',f,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=model)
    plan=api.run('context.add_context',f,context_type='Plan')
    axis=api.run('context.add_context',f,context_type='Plan',context_identifier='Axis',target_view='GRAPH_VIEW',parent=plan)
    storey=api.run('root.create_entity',f,ifc_class='IfcBuildingStorey',name='Terreo')
    api.run('aggregate.assign_object',f,products=[storey],relating_object=project)
    walls=[]
    for i,((a,b),t,h) in enumerate(zip(BASE,thicknesses,heights)):
        wall=api.run('root.create_entity',f,ifc_class='IfcWall',name=f'P{i+1:02}')
        api.run('spatial.assign_container',f,products=[wall],relating_structure=storey)
        d=np.array(b,dtype=float)-a; length=float(np.linalg.norm(d));d/=length
        mat=np.eye(4);mat[:2,0]=d;mat[:2,1]=[-d[1],d[0]];mat[:2,3]=a
        api.run('geometry.edit_object_placement',f,product=wall,matrix=mat)
        rep=api.run('geometry.add_axis_representation',f,context=axis,axis=[(0.,0.),(length,0.)])
        api.run('geometry.assign_representation',f,product=wall,representation=rep)
        material=f.create_entity('IfcMaterial',Name='Example')
        layer=f.create_entity('IfcMaterialLayer',Material=material,LayerThickness=t,Priority=50)
        layers=f.create_entity('IfcMaterialLayerSet',MaterialLayers=[layer])
        usage=f.create_entity('IfcMaterialLayerSetUsage',ForLayerSet=layers,LayerSetDirection='AXIS2',DirectionSense='POSITIVE',OffsetFromReferenceLine=-t/2)
        f.create_entity('IfcRelAssociatesMaterial',GlobalId=ifcopenshell.guid.new(),RelatedObjects=[wall],RelatingMaterial=usage)
        walls.append(wall)
    for a,b,ca,cb in LINKS:
        api.run('geometry.connect_path',f,relating_element=walls[a],related_element=walls[b],relating_connection=ca,related_connection=cb)
    for w,h in zip(walls,heights):
        api.run('geometry.regenerate_wall_representation',f,wall=w,height=h)
    settings=ifcopenshell.geom.settings();settings.set(settings.USE_WORLD_COORDS,True)
    def extract():
        polys=[];meshes=[]
        for w in walls:
            shape=ifcopenshell.geom.create_shape(settings,w)
            v=np.array(shape.geometry.verts).reshape(-1,3);faces=np.array(shape.geometry.faces).reshape(-1,3)
            tris=[Polygon(v[face,:2]) for face in faces]
            p=unary_union([p for p in tris if p.area>1e-10]);polys.append(p)
            meshes.append({'id':w.Name,'guid':w.GlobalId,'vertices':v.tolist(),'faces':faces.tolist(),'height':float(np.ptp(v[:,2]))})
        return polys,meshes
    polys,meshes=extract(); ids=[w.GlobalId for w in walls]
    overlaps=[{'a':walls[a].Name,'b':walls[b].Name,'area':polys[a].intersection(polys[b]).area} for a,b in itertools.combinations(range(5),2)]
    gaps=[{'a':walls[a].Name,'b':walls[b].Name,'distance':polys[a].distance(polys[b])} for a,b,_,_ in LINKS]
    for w,h in zip(walls,heights):api.run('geometry.regenerate_wall_representation',f,wall=w,height=h)
    repeated,_=extract()
    checks={'five_walls':len(f.by_type('IfcWall'))==5,'six_connections':len(f.by_type('IfcRelConnectsPathElements'))==6,'valid_footprints':all(p.is_valid and p.area>0 for p in polys),'no_plan_overlap':all(p['area']<1e-7 for p in overlaps),'joined_contacts':all(p['distance']<1e-7 for p in gaps),'heights_preserved':all(abs(m['height']-h)<1e-7 for m,h in zip(meshes,heights)),'stable_regeneration':all(a.symmetric_difference(b).area<1e-7 for a,b in zip(polys,repeated)),'ids_preserved':ids==[w.GlobalId for w in walls]}
    f.write(str(OUT/f'{name}.ifc'))
    (OUT/f'{name}.json').write_text(json.dumps({'meshes':meshes,'footprints':[p.__geo_interface__ for p in polys]},indent=2))
    return {'case':name,'checks':checks,'passed':all(checks.values()),'elapsed_seconds':round(time.perf_counter()-start,3),'overlaps':overlaps,'gaps':gaps}
if __name__=='__main__':
    results=[run('baseline',[.2,.2,.2,.2,.15],[2.8]*5),run('different-thickness',[.3,.2,.25,.15,.1],[2.8]*5),run('different-height',[.2,.2,.2,.2,.15],[2.8,3.2,2.5,2.8,2.1])]
    report={'ifcopenshell':ifcopenshell.version,'cases':results,'limits':['Projected overlap checks cover these vertical extrusions only.','No sloped walls, layers with different materials, openings or arbitrary angles tested.','Memory not measured. Time includes IFC generation, meshing and serialization; not a production benchmark.']}
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    sys.exit(0 if all(r['passed'] for r in results) else 1)
