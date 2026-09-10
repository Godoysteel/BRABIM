"""Long-lived IfcOpenShell worker: reads room parameters as JSON lines on
stdin, returns real wall geometry (vertices/faces) as JSON on stdout. Pays
the ifcopenshell import/startup cost once, at launch.
"""
import sys, json, time
import ifcopenshell, ifcopenshell.api as api, ifcopenshell.geom
from ifcopenshell.api.geometry.add_wall_representation import add_wall_representation
import numpy as np

from OCP.gp import gp_Pnt, gp_Dir, gp_Pln
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SHAPE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS


def _sloped_half_space(p, inward, slope, keep_point):
    nx, ny, nz = -inward[0] * slope, -inward[1] * slope, 1
    face = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(*p), gp_Dir(nx, ny, nz))).Face()
    return BRepPrimAPI_MakeHalfSpace(face, gp_Pnt(*keep_point)).Solid()


def _triangulate_occt(solid):
    """Triangulates every face of an OCCT solid into a flat vertex/face
    list. A face's stored triangulation always winds the same way as its
    underlying surface -- when the face itself is TopAbs_REVERSED (which
    a boolean like Cut or Common routinely produces for some faces of
    the result, not just a whole-shape flip), the correct outward
    winding needs two of the three indices swapped, or that face's
    normal points inward. Three.js renders single-sided by default, so
    an unswapped reversed face doesn't look subtly wrong -- it's just
    not there from most angles, e.g. a window cut through a thin wall
    layer where only some of the frame's faces reversed showed up as a
    piece of the frame missing/floating instead of a solid opening.
    """
    BRepMesh_IncrementalMesh(solid, 0.05, False, 0.3, False)
    vertices, faces = [], []
    exp = TopExp_Explorer(solid, TopAbs_FACE, TopAbs_SHAPE)
    while exp.More():
        face = TopoDS.Face(exp.Current())
        reversed_face = face.Orientation() == TopAbs_REVERSED
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            base = len(vertices)
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                vertices.append((p.X(), p.Y(), p.Z()))
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                if reversed_face:
                    a, b = b, a
                faces.append((base + a - 1, base + b - 1, base + c - 1))
        exp.Next()
    return vertices, faces


def _roof_mass(width, depth, eave_height, slope, sloped_edges, overhang, anchor_height):
    """The solid you get from intersecting a tall box with the sloped
    half-spaces, all anchored at `anchor_height` instead of the true eave
    height. Used twice in build_roof: once at the real eave height for the
    roof's top (outer) surface, once shifted down by the deck thickness for
    the underside -- subtracting the second from the first gives a shell of
    uniform thickness that stays flush with the wall top under the
    footprint and droops with the same slope over the overhang, instead of
    a single flat cut that either buries the overhang or pokes the wall
    through the ceiling.
    """
    w, d = width, depth
    ow, od = w / 2 + overhang, d / 2 + overhang
    box = BRepPrimAPI_MakeBox(gp_Pnt(-ow, -od, 0), gp_Pnt(ow, od, eave_height + max(w, d))).Shape()
    edges = {
        'north': ((0, d / 2, anchor_height), (0, -1)),
        'south': ((0, -d / 2, anchor_height), (0, 1)),
        'east': ((w / 2, 0, anchor_height), (-1, 0)),
        'west': ((-w / 2, 0, anchor_height), (1, 0)),
    }
    solid = box
    for name in sloped_edges:
        p, inward = edges[name]
        solid = BRepAlgoAPI_Common(solid, _sloped_half_space(p, inward, slope, (0, 0, anchor_height))).Shape()
    return solid


def build_roof(f, body, storey, width, depth, eave_height, slope, sloped_edges, overhang=0.5, thickness=0.1):
    """Revit-style roof by footprint: each eave edge either has slope
    (an inward-rising half-space plane) or stays vertical (a gable end).
    Only rectangular footprints aligned to the world axes, for now.

    Modeled as a shell of real thickness: the UNDERSIDE is anchored at
    eave_height (flush with the wall top -- zero gap, zero overlap under
    the footprint), and the visible outer surface sits `thickness` above
    that. Anchoring the outer surface at eave_height instead (thickness
    downward) put the underside 'thickness' below the wall top, so the
    wall's own top sliver ended up inside the roof solid -- the "wall
    pokes through the roof" bug, confirmed by exporting real vertices via
    the debug panel (wall top z=2.8, roof underside z=2.7 in that case).
    `overhang` extends the visible eave (and its droop) past the wall face
    on all four sides.
    """
    inner = _roof_mass(width, depth, eave_height, slope, sloped_edges, overhang, eave_height)
    outer = _roof_mass(width, depth, eave_height, slope, sloped_edges, overhang, eave_height + thickness)
    solid = BRepAlgoAPI_Cut(outer, inner).Shape()

    vertices, faces = _triangulate_occt(solid)
    roof = api.run('root.create_entity', f, ifc_class='IfcRoof', name='Telhado')
    api.run('spatial.assign_container', f, products=[roof], relating_structure=storey)
    rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
    api.run('geometry.assign_representation', f, product=roof, representation=rep)
    api.run('geometry.edit_object_placement', f, product=roof)
    return roof, inner


def _wall_cap(inner, a, b, thickness, eave_height, tall_top):
    """The part of one wall's own footprint that sits between eave_height
    and the roof's underside (`inner`). Axis-aligned only, like the rest
    of build_room: tells apart a north/south run from an east/west run by
    which endpoint coordinate stays constant, then extends half a
    thickness past each end so neighbouring walls' caps overlap at the
    corner instead of leaving a sliver gap there.
    """
    ax, ay = a; bx, by = b
    if ax == bx:  # runs north-south (an east/west wall): thin in x, spans y
        y0, y1 = sorted((ay, by))
        pmin = gp_Pnt(ax - thickness / 2, y0 - thickness / 2, eave_height)
        pmax = gp_Pnt(ax + thickness / 2, y1 + thickness / 2, tall_top)
    else:  # runs east-west (a north/south wall): thin in y, spans x
        x0, x1 = sorted((ax, bx))
        pmin = gp_Pnt(x0 - thickness / 2, ay - thickness / 2, eave_height)
        pmax = gp_Pnt(x1 + thickness / 2, ay + thickness / 2, tall_top)
    box = BRepPrimAPI_MakeBox(pmin, pmax).Shape()
    return BRepAlgoAPI_Common(box, inner).Shape()


def attach_wall_to_roof(f, body, storey, name, inner, a, b, thickness, eave_height, tall_top):
    """Revit-style 'Attach Top/Base': instead of a special gable panel
    for two-water roofs, every wall's flat top gets reshaped to follow
    whatever roof sits above it -- a sloped edge picks up only the thin
    sliver across its own thickness (the roof plane rises slightly
    behind the eave line), an unsloped (gable) edge picks up the full
    triangular void up to the ridge. One mechanism, any roof shape.
    Returns None when the wall needs no cap (edge already flush the
    whole way, e.g. a hip hidden entirely under the eave line).
    """
    cap = _wall_cap(inner, a, b, thickness, eave_height, tall_top)
    vertices, faces = _triangulate_occt(cap)
    if not vertices:
        return None
    wall = api.run('root.create_entity', f, ifc_class='IfcWall', name=f'{name}-EMP')
    api.run('spatial.assign_container', f, products=[wall], relating_structure=storey)
    rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
    api.run('geometry.assign_representation', f, product=wall, representation=rep)
    api.run('geometry.edit_object_placement', f, product=wall)
    return wall

_WALL_OUTWARD = {0: (0, 1), 1: (0, -1), 2: (-1, 0), 3: (1, 0)}  # north, south, west, east


def _wall_layer_solids(a, b, layers, outward, height):
    """One thin OCCT box per layer, stacked along the wall's own
    thickness axis from the room-facing side outward -- `layers` is
    ordered inside to outside, e.g. [('Reboco interno',.02),
    ('Tijolo',.09),('Reboco externo',.025)]. Each box is extended past
    the wall's own ends by half the thickest layer, the same corner
    overlap trick as _wall_cap, so a corner never shows a sliver gap
    between two walls' layers.
    """
    ax, ay = a; bx, by = b
    ox, oy = outward
    total = sum(t for _, t in layers)
    pad = max((t for _, t in layers), default=0) / 2
    solids, offset = [], -total / 2
    for material, t in layers:
        lo, hi = offset, offset + t
        if ay == by:  # north/south wall: thickness runs along y
            y0, y1 = sorted((ay + lo * oy, ay + hi * oy))
            x0, x1 = sorted((ax, bx))
            box = BRepPrimAPI_MakeBox(gp_Pnt(x0 - pad, y0, 0), gp_Pnt(x1 + pad, y1, height)).Shape()
        else:  # east/west wall: thickness runs along x
            x0, x1 = sorted((ax + lo * ox, ax + hi * ox))
            y0, y1 = sorted((ay, by))
            box = BRepPrimAPI_MakeBox(gp_Pnt(x0, y0 - pad, 0), gp_Pnt(x1, y1 + pad, height)).Shape()
        solids.append((material, box))
        offset = hi
    return solids


def _opening_box_world(axis_origin, along_offset, width, height, sill, thickness_pad):
    """Same placement math as add_opening's matrix, but as a raw OCCT box
    instead of an IfcOpeningElement -- used to cut the *layer* slabs
    (add_opening only cuts the single parametric wall body, which the
    layers replace visually). Only meaningful for the north/south walls,
    the only ones build_room ever puts a door or window in.
    """
    x0 = axis_origin[0] + along_offset
    x1 = x0 + width
    y0 = axis_origin[1] - thickness_pad / 2
    y1 = axis_origin[1] + thickness_pad / 2
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, sill), gp_Pnt(x1, y1, sill + height)).Shape()


def attach_wall_layers(f, body, storey, name, a, b, layers, outward, height, opening_box=None):
    """Builds the layer slabs for one wall and returns their entities.
    The wall itself (`name`, P01..P04) keeps its normal single-box IFC
    representation for openings, corner joins and the roof attach --
    these layer entities are additional, purely for showing the
    sandwich; build_room skips exporting the plain wall's own mesh
    once layers exist for it, so the two don't render on top of each
    other.
    """
    entities = []
    for material, box in _wall_layer_solids(a, b, layers, outward, height):
        shape = BRepAlgoAPI_Cut(box, opening_box).Shape() if opening_box is not None else box
        vertices, faces = _triangulate_occt(shape)
        if not vertices:
            continue
        wall = api.run('root.create_entity', f, ifc_class='IfcWall', name=f'{name}-{material}')
        api.run('spatial.assign_container', f, products=[wall], relating_structure=storey)
        rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
        api.run('geometry.assign_representation', f, product=wall, representation=rep)
        api.run('geometry.edit_object_placement', f, product=wall)
        entities.append((material, wall))
    return entities


def add_opening(f, body, wall, axis_origin, along_offset, width, height, sill, wall_thickness):
    """Cuts a void into `wall` at `along_offset` (distance from the wall's
    start point, matching the app's doorOffset/windowOffset convention),
    `sill` above the floor. Assumes the wall runs along world X and starts
    at `axis_origin` (true for the north/south walls of build_room; not a
    general solution for arbitrary wall angles).
    """
    if width <= 0 or height <= 0:
        return
    opening = api.run('root.create_entity', f, ifc_class='IfcOpeningElement')
    # Thicker than the wall itself so the boolean cut has no float-precision gaps.
    opening_thickness = wall_thickness + 0.3
    rep = add_wall_representation(f, context=body, length=width, height=height, thickness=opening_thickness)
    api.run('geometry.assign_representation', f, product=opening, representation=rep)
    mat = np.eye(4)
    mat[0, 3] = axis_origin[0] + along_offset
    mat[1, 3] = axis_origin[1] - opening_thickness / 2
    mat[2, 3] = sill
    api.run('geometry.edit_object_placement', f, product=opening, matrix=mat)
    api.run('feature.add_feature', f, feature=opening, element=wall)

# Lintel defaults -- common, not normative: 10 cm tall, bearing 15 cm past
# each side of the opening so the beam actually rests on solid wall.
# Adjustable later; not sourced from a specific standard.
LINTEL_HEIGHT = 0.1
LINTEL_BEARING = 0.15


def add_lintel(f, body, storey, name, axis_origin, along_offset, width, z0, z1, wall_thickness, predefined_type, bearing=LINTEL_BEARING):
    """A concrete beam spanning an opening: `verga` above it (predefined_type
    'LINTEL') or `contraverga` below a window's sill (no matching
    IfcBeamTypeEnum value exists for that, so it's just 'BEAM'). Reuses
    the exact opening position/width already computed for the void cut --
    extends `bearing` past each side so it actually rests on wall, not
    just spans the hole.
    """
    x0 = axis_origin[0] + along_offset - bearing
    x1 = x0 + width + 2 * bearing
    y0 = axis_origin[1] - wall_thickness / 2
    y1 = axis_origin[1] + wall_thickness / 2
    box = BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()
    vertices, faces = _triangulate_occt(box)
    beam = api.run('root.create_entity', f, ifc_class='IfcBeam', name=name, predefined_type=predefined_type)
    api.run('spatial.assign_container', f, products=[beam], relating_structure=storey)
    rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
    api.run('geometry.assign_representation', f, product=beam, representation=rep)
    api.run('geometry.edit_object_placement', f, product=beam)
    return beam

def build_room(width, depth, height, thickness, door=None, window=None, roof=None, layers=None, contraverga=False):
    w, d, h, t = width, depth, height, thickness
    # Rectangle loop: north, south, west, east walls, joined at all 4 corners.
    base = [
        ((-w/2, d/2), (w/2, d/2)),   # P01 north (window wall)
        ((-w/2, -d/2), (w/2, -d/2)), # P02 south (door wall)
        ((-w/2, -d/2), (-w/2, d/2)), # P03 west
        ((w/2, -d/2), (w/2, d/2)),   # P04 east
    ]
    links = [(0, 2, 'ATSTART', 'ATEND'), (0, 3, 'ATEND', 'ATEND'), (1, 2, 'ATSTART', 'ATSTART'), (1, 3, 'ATEND', 'ATSTART')]

    f = ifcopenshell.file(schema='IFC4')
    project = api.run('root.create_entity', f, ifc_class='IfcProject', name='BRABIM')
    unit = api.run('unit.add_si_unit', f, unit_type='LENGTHUNIT')
    api.run('unit.assign_unit', f, units=[unit])
    model = api.run('context.add_context', f, context_type='Model')
    body = api.run('context.add_context', f, context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=model)
    plan = api.run('context.add_context', f, context_type='Plan')
    axis = api.run('context.add_context', f, context_type='Plan', context_identifier='Axis', target_view='GRAPH_VIEW', parent=plan)
    storey = api.run('root.create_entity', f, ifc_class='IfcBuildingStorey', name='Terreo')
    api.run('aggregate.assign_object', f, products=[storey], relating_object=project)

    walls = []
    for i, (a, b) in enumerate(base):
        wall = api.run('root.create_entity', f, ifc_class='IfcWall', name=f'P{i+1:02}')
        api.run('spatial.assign_container', f, products=[wall], relating_structure=storey)
        vec = np.array(b, dtype=float) - a
        length = float(np.linalg.norm(vec)); vec /= length
        mat = np.eye(4); mat[:2, 0] = vec; mat[:2, 1] = [-vec[1], vec[0]]; mat[:2, 3] = a
        api.run('geometry.edit_object_placement', f, product=wall, matrix=mat)
        rep = api.run('geometry.add_axis_representation', f, context=axis, axis=[(0., 0.), (length, 0.)])
        api.run('geometry.assign_representation', f, product=wall, representation=rep)
        material = f.create_entity('IfcMaterial', Name='Parede')
        layer = f.create_entity('IfcMaterialLayer', Material=material, LayerThickness=t, Priority=50)
        layer_set = f.create_entity('IfcMaterialLayerSet', MaterialLayers=[layer])
        usage = f.create_entity('IfcMaterialLayerSetUsage', ForLayerSet=layer_set, LayerSetDirection='AXIS2', DirectionSense='POSITIVE', OffsetFromReferenceLine=-t/2)
        f.create_entity('IfcRelAssociatesMaterial', GlobalId=ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingMaterial=usage)
        walls.append(wall)
    for a, b, ca, cb in links:
        api.run('geometry.connect_path', f, relating_element=walls[a], related_element=walls[b], relating_connection=ca, related_connection=cb)
    for wall in walls:
        api.run('geometry.regenerate_wall_representation', f, wall=wall, height=h)

    # Named VERGA-/CONTRAVERGA-prefixed (not P0X-suffixed) so they never
    # collide with the P0X-<material> id scheme wall layers use -- the
    # plan view's window/door gap-split logic keys off that "P0X-" prefix
    # and would otherwise slice a lintel in half at the opening's gap.
    lintel_entities = []
    if door:
        add_opening(f, body, walls[1], base[1][0], door['offset'], door['width'], door['height'], 0, t)
        lintel_entities.append(add_lintel(f, body, storey, 'VERGA-P02', base[1][0], door['offset'], door['width'], door['height'], door['height'] + LINTEL_HEIGHT, t, 'LINTEL'))
    if window:
        add_opening(f, body, walls[0], base[0][0], window['offset'], window['width'], window['height'], window['sill'], t)
        top = window['sill'] + window['height']
        lintel_entities.append(add_lintel(f, body, storey, 'VERGA-P01', base[0][0], window['offset'], window['width'], top, top + LINTEL_HEIGHT, t, 'LINTEL'))
        if contraverga:
            lintel_entities.append(add_lintel(f, body, storey, 'CONTRAVERGA-P01', base[0][0], window['offset'], window['width'], window['sill'] - LINTEL_HEIGHT, window['sill'], t, 'BEAM'))

    # Layer entities per wall -- each wall can carry its own sandwich
    # (e.g. render only on the street-facing side), keyed by name so a
    # wall with no entry just keeps its plain single-box representation.
    # Openings cut through every layer of whichever wall has them.
    layer_entities = {}
    if layers:
        opening_thickness_pad = t + 0.3
        openings = {
            'P01': _opening_box_world(base[0][0], window['offset'], window['width'], window['height'], window['sill'], opening_thickness_pad) if window else None,
            'P02': _opening_box_world(base[1][0], door['offset'], door['width'], door['height'], 0, opening_thickness_pad) if door else None,
        }
        for i, (a, b) in enumerate(base):
            name = f'P{i+1:02}'
            wall_layers = layers.get(name)
            if wall_layers:
                layer_entities[name] = attach_wall_layers(f, body, storey, name, a, b, wall_layers, _WALL_OUTWARD[i], h, openings.get(name))

    roof_entity, cap_entities = None, []
    if roof:
        # width/depth are the room's *internal* clear dimensions; the wall's
        # actual outer face sits half a wall-thickness further out. The
        # roof's zero-overhang reference edge needs to be that outer face
        # (matching the wall corner exactly), not the internal footprint --
        # otherwise the wall corner sits inside the droop zone instead of
        # at its start (confirmed via the debug panel: corner fell 0.1m,
        # half the wall thickness, into the overhang before this fix).
        roof_entity, inner = build_roof(f, body, storey, w + t, d + t, h, roof['slope'], roof['slopedEdges'], roof.get('overhang', 0.5))
        # Attach every wall's top to the roof's underside (see
        # attach_wall_to_roof): the same mechanism closes the gable
        # triangle on an unsloped edge and trims the tiny sliver a
        # sloped edge picks up across its own thickness.
        tall_top = h + max(w, d) + t
        for i, (a, b) in enumerate(base):
            cap = attach_wall_to_roof(f, body, storey, f'P{i+1:02}', inner, a, b, t, h, tall_top)
            if cap:
                cap_entities.append(cap)

    settings = ifcopenshell.geom.settings(); settings.set(settings.USE_WORLD_COORDS, True)
    meshes = []
    for wall in walls:
        if wall.Name in layer_entities:
            continue  # shown as its layer sandwich below instead of one slab
        shape = ifcopenshell.geom.create_shape(settings, wall)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        meshes.append({'id': wall.Name, 'guid': wall.GlobalId, 'vertices': v.tolist(), 'faces': faces.tolist()})
    for wall_entities in layer_entities.values():
        for material, layer_wall in wall_entities:
            shape = ifcopenshell.geom.create_shape(settings, layer_wall)
            v = np.array(shape.geometry.verts).reshape(-1, 3)
            faces = np.array(shape.geometry.faces).reshape(-1, 3)
            meshes.append({'id': layer_wall.Name, 'guid': layer_wall.GlobalId, 'material': material, 'vertices': v.tolist(), 'faces': faces.tolist()})
    if roof_entity:
        shape = ifcopenshell.geom.create_shape(settings, roof_entity)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        meshes.append({'id': 'TELHADO', 'guid': roof_entity.GlobalId, 'vertices': v.tolist(), 'faces': faces.tolist()})
    for cap in cap_entities:
        shape = ifcopenshell.geom.create_shape(settings, cap)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        meshes.append({'id': cap.Name, 'guid': cap.GlobalId, 'vertices': v.tolist(), 'faces': faces.tolist()})
    for beam in lintel_entities:
        shape = ifcopenshell.geom.create_shape(settings, beam)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        meshes.append({'id': beam.Name, 'guid': beam.GlobalId, 'material': 'Concreto', 'vertices': v.tolist(), 'faces': faces.tolist()})
    return meshes

def main():
    print(json.dumps({'type': 'ready', 'startup_seconds': round(time.perf_counter() - START, 3), 'ifcopenshell_version': ifcopenshell.version}), flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            room = req.get('room', {})
            t0 = time.perf_counter()
            meshes = build_room(
                width=float(room.get('width', 5)),
                depth=float(room.get('depth', 4)),
                height=float(room.get('height', 2.8)),
                thickness=float(room.get('thickness', .2)),
                door={'offset': float(room['doorOffset']), 'width': float(room['doorWidth']), 'height': float(room['doorHeight'])} if 'doorOffset' in room else None,
                window={'offset': float(room['windowOffset']), 'width': float(room['windowWidth']), 'height': float(room['windowHeight']), 'sill': float(room.get('sill', 1))} if 'windowOffset' in room else None,
                roof=req['roof'] if req.get('roof') else None,
                layers={name: [(l['material'], float(l['thickness'])) for l in wl] for name, wl in req['wallLayers'].items()} if req.get('wallLayers') else None,
                contraverga=bool(req.get('contraverga', False)),
            )
            print(json.dumps({'type': 'result', 'id': req.get('id'), 'elapsed_seconds': round(time.perf_counter() - t0, 3), 'meshes': meshes}), flush=True)
        except Exception as e:
            print(json.dumps({'type': 'error', 'id': req.get('id') if 'req' in dir() else None, 'message': str(e)}), flush=True)

START = time.perf_counter()
if __name__ == '__main__':
    main()
