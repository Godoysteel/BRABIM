"""Long-lived IfcOpenShell worker: reads room parameters as JSON lines on
stdin, returns real wall geometry (vertices/faces) as JSON on stdout. Pays
the ifcopenshell import/startup cost once, at launch.
"""
import sys, json, time
import ifcopenshell, ifcopenshell.api as api, ifcopenshell.geom
from ifcopenshell.api.geometry.add_wall_representation import add_wall_representation
import numpy as np

from OCP.gp import gp_Pnt, gp_Dir, gp_Pln, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
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


# Rough default tile size for a wall-layer texture (1 image = ~1m of wall),
# not a verified physical scale -- see public/texturas/LEIA-ME.md, which
# explicitly flags tiling/scale as unverified. UV comes straight from the
# already-exported world-space vertices, not from the OCCT triangulation
# used to build the IFC representation (that one gets discarded and
# re-triangulated by ifcopenshell.geom when read back for display, so
# baking UV any earlier than this would never survive the round trip).
TEXTURE_TILE_METERS = 1.0


def _wall_uv(v, wall_name):
    i, j = (0, 2) if wall_name in ('P01', 'P02') else (1, 2)
    return (v[:, [i, j]] / TEXTURE_TILE_METERS).tolist()


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


def _lintel_extents(axis_origin, along_offset, width, z0, z1, wall_thickness, bearing=LINTEL_BEARING):
    x0 = axis_origin[0] + along_offset - bearing
    x1 = x0 + width + 2 * bearing
    y0 = axis_origin[1] - wall_thickness / 2
    y1 = axis_origin[1] + wall_thickness / 2
    return x0, x1, y0, y1, z0, z1


def _tie_beam_extents(a, b, thickness, z0, z1):
    """Axis-aligned extents for one wall's tie beam (the 'cinta' at the
    top of the wall, see build_room's `structure` block) -- same
    corner-overlap padding as _wall_cap so two walls' beams meet flush at
    the corner (the corner column is cut out of the resulting box
    afterwards, since both are concrete and would otherwise coincide).
    """
    ax, ay = a; bx, by = b
    if ax == bx:  # east/west wall: thin in x, spans y
        y0, y1 = sorted((ay, by))
        return ax - thickness/2, ax + thickness/2, y0 - thickness/2, y1 + thickness/2, z0, z1
    x0, x1 = sorted((ax, bx))  # north/south wall: thin in y, spans x
    return x0 - thickness/2, x1 + thickness/2, ay - thickness/2, ay + thickness/2, z0, z1


def add_lintel(f, body, storey, name, box, predefined_type):
    """A concrete beam spanning an opening: `verga` above it (predefined_type
    'LINTEL') or `contraverga` below a window's sill (no matching
    IfcBeamTypeEnum value exists for that, so it's just 'BEAM'). `box`
    comes from _lintel_extents -- shared with build_room's layer cut so
    the layer material doesn't keep occupying the same space above the
    opening, which produced two exactly coincident faces there (the
    layer's own frame above the void, and the lintel on top of it) and
    z-fought on screen.
    """
    vertices, faces = _triangulate_occt(box)
    beam = api.run('root.create_entity', f, ifc_class='IfcBeam', name=name, predefined_type=predefined_type)
    api.run('spatial.assign_container', f, products=[beam], relating_structure=storey)
    rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
    api.run('geometry.assign_representation', f, product=beam, representation=rep)
    api.run('geometry.edit_object_placement', f, product=beam)
    return beam


REBAR_COVER = 0.025  # common concrete cover, not a calculated value


def _stirrup_ring(x, y0, y1, z0, z1, r):
    """A rectangular ring in the y-z cross-section at position x: four
    cylinder segments (an approximation of a single bent wire -- corners
    overlap rather than mitre, close enough at rebar scale to read
    correctly on screen), triangulated and merged in plain Python instead
    of an OCCT boolean Fuse. A real CAD union of four solids per stirrup,
    times a stirrup every ~15cm along every reinforced beam, measured at
    over 10 seconds for a single room -- far too slow for a UI that
    recomputes on every keystroke. The pieces don't need to be one
    topological solid to look right or to sit in one mesh representation,
    so skipping the boolean (and the per-call OCCT overhead that comes
    with it) is a straightforward, meaningful win, not a shortcut that
    costs correctness.
    """
    segments = [
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z0), gp_Dir(0, 1, 0)), r, y1 - y0).Shape(),
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z1), gp_Dir(0, 1, 0)), r, y1 - y0).Shape(),
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape(),
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y1, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape(),
    ]
    vertices, faces = [], []
    for seg in segments:
        v, fc = _triangulate_occt(seg)
        base = len(vertices)
        vertices.extend(v)
        faces.extend((a + base, b + base, c + base) for a, b, c in fc)
    return vertices, faces


def _reinforce_beam(u0, u1, v0, v1, z0, z1, long_diam, long_count, stirrup_diam, stirrup_spacing, axis='x'):
    """Real rebar geometry for any axis-aligned box-shaped concrete
    element, generic on purpose so the same function covers a future
    cinta/viga, not just today's verga/contraverga: longitudinal bars
    run the box's long (horizontal) axis, split evenly between a bottom
    and top row inset by REBAR_COVER from each face; stirrups are
    rectangular rings around the cross-section at `stirrup_spacing`
    along that axis. `u0,u1` is the range along the beam's length,
    `v0,v1` the range across its horizontal width -- `axis` says which
    world axis `u` actually is ('x', the default, for every north/south
    verga/contraverga; 'y' for a tie beam along an east/west wall, see
    build_room's `structure` block), `v` is always the other one. This
    is geometry and quantitative mass, not a structural calculation --
    bar count/diameter/spacing are the caller's choice, not something
    this derives from load or span.
    """
    vc0, vc1 = v0 + REBAR_COVER, v1 - REBAR_COVER
    zc0, zc1 = z0 + REBAR_COVER, z1 - REBAR_COVER
    def row(n, z):
        if n <= 0:
            return []
        if n == 1:
            return [((vc0 + vc1) / 2, z)]
        return [(vc0 + i * (vc1 - vc0) / (n - 1), z) for i in range(n)]
    bottom_n = (long_count + 1) // 2
    top_n = long_count - bottom_n
    long_r, length = long_diam / 2, u1 - u0
    direction = gp_Dir(1, 0, 0) if axis == 'x' else gp_Dir(0, 1, 0)
    def origin(v, z):
        return gp_Pnt(u0, v, z) if axis == 'x' else gp_Pnt(v, u0, z)
    longitudinal = [BRepPrimAPI_MakeCylinder(gp_Ax2(origin(v, z), direction), long_r, length).Shape() for v, z in row(bottom_n, zc0) + row(top_n, zc1)]
    stirrup_r = stirrup_diam / 2
    margin = max(REBAR_COVER, stirrup_r * 2)
    # Every stirrup along one beam shares the same cross-section -- build
    # the ring's geometry once (the OCCT construction + triangulation
    # that dominated the cost here) and just shift its position in plain
    # Python for each repeat, instead of re-running OCCT per ring.
    template_v, template_f = _stirrup_ring(0.0, vc0, vc1, zc0, zc1, stirrup_r)
    stirrups, u = [], u0 + margin
    while u <= u1 - margin:
        shifted = [(vx + u, vy, vz) for vx, vy, vz in template_v] if axis == 'x' else [(vy, vx + u, vz) for vx, vy, vz in template_v]
        stirrups.append((shifted, template_f))
        u += stirrup_spacing
    return longitudinal, stirrups


def _perimeter_points(n, x0, x1, y0, y1):
    """n points evenly spaced clockwise around a rectangle's perimeter,
    starting at a corner -- the common 4/6/8-bar column layout (bars at
    or near the corners), not an optimized cross-section design.
    """
    if n <= 0:
        return []
    if n == 1:
        return [((x0 + x1) / 2, (y0 + y1) / 2)]
    w, h = x1 - x0, y1 - y0
    perimeter = 2 * (w + h)
    points = []
    for i in range(n):
        d = i * perimeter / n
        if d < w:
            points.append((x0 + d, y0))
        elif d < w + h:
            points.append((x1, y0 + (d - w)))
        elif d < 2 * w + h:
            points.append((x1 - (d - w - h), y1))
        else:
            points.append((x0, y1 - (d - 2 * w - h)))
    return points


def _stirrup_ring_xy(z, x0, x1, y0, y1, r):
    """Horizontal counterpart to _stirrup_ring: a rectangular ring in the
    x-y cross-section at height z, for a vertical column's stirrups.
    """
    segments = [
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y0, z), gp_Dir(1, 0, 0)), r, x1 - x0).Shape(),
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y1, z), gp_Dir(1, 0, 0)), r, x1 - x0).Shape(),
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y0, z), gp_Dir(0, 1, 0)), r, y1 - y0).Shape(),
        BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x1, y0, z), gp_Dir(0, 1, 0)), r, y1 - y0).Shape(),
    ]
    vertices, faces = [], []
    for seg in segments:
        v, fc = _triangulate_occt(seg)
        base = len(vertices)
        vertices.extend(v)
        faces.extend((a + base, b + base, c + base) for a, b, c in fc)
    return vertices, faces


def _reinforce_column(x0, x1, y0, y1, z0, z1, long_diam, long_count, stirrup_diam, stirrup_spacing):
    """Vertical counterpart to _reinforce_beam: longitudinal bars run the
    column's full height (z) at points around the cross-section's
    perimeter (see _perimeter_points), stirrups are rectangular rings in
    the x-y plane at `stirrup_spacing` along z. Same caveat as
    _reinforce_beam -- geometry and quantitative mass, not a structural
    design (bar count/diameter/spacing are the caller's choice).
    """
    xc0, xc1 = x0 + REBAR_COVER, x1 - REBAR_COVER
    yc0, yc1 = y0 + REBAR_COVER, y1 - REBAR_COVER
    long_r, length = long_diam / 2, z1 - z0
    longitudinal = [BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), long_r, length).Shape() for x, y in _perimeter_points(long_count, xc0, xc1, yc0, yc1)]
    stirrup_r = stirrup_diam / 2
    margin = max(REBAR_COVER, stirrup_r * 2)
    template_v, template_f = _stirrup_ring_xy(0.0, xc0, xc1, yc0, yc1, stirrup_r)
    stirrups, z = [], z0 + margin
    while z <= z1 - margin:
        stirrups.append(([(vx, vy, vz + z) for vx, vy, vz in template_v], template_f))
        z += stirrup_spacing
    return longitudinal, stirrups


def add_reinforcement(f, body, storey, name_prefix, longitudinal, stirrups):
    entities = []
    for i, bar in enumerate(longitudinal):
        vertices, faces = _triangulate_occt(bar)
        if not vertices:
            continue
        e = api.run('root.create_entity', f, ifc_class='IfcReinforcingBar', name=f'{name_prefix}-FERRO-{i+1}', predefined_type='MAIN')
        api.run('spatial.assign_container', f, products=[e], relating_structure=storey)
        rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
        api.run('geometry.assign_representation', f, product=e, representation=rep)
        api.run('geometry.edit_object_placement', f, product=e)
        entities.append(e)
    for i, (vertices, faces) in enumerate(stirrups):
        if not vertices:
            continue
        e = api.run('root.create_entity', f, ifc_class='IfcReinforcingBar', name=f'{name_prefix}-ESTRIBO-{i+1}', predefined_type='RING')
        api.run('spatial.assign_container', f, products=[e], relating_structure=storey)
        rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
        api.run('geometry.assign_representation', f, product=e, representation=rep)
        api.run('geometry.edit_object_placement', f, product=e)
        entities.append(e)
    return entities

def build_room(width, depth, height, thickness, door=None, window=None, roof=None, layers=None, contraverga=False, rebar=None, structure=None):
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
    # A lintel spans the wall's own thickness, not the room's nominal `t` --
    # once a wall has layers, its real (visual) thickness can differ from
    # `t` (shown in the UI as "espessura oficial" vs "soma das camadas"),
    # and a lintel still sized to `t` then juts out past a thinner layered
    # face or sits recessed behind a thicker one.
    def _wall_thickness(name):
        wall_layers = (layers or {}).get(name)
        return sum(l[1] for l in wall_layers) if wall_layers else t

    def _reinforce(name_prefix, extents):
        if not rebar:
            return
        long_diam, long_count = rebar['longitudinal']
        stirrup_diam, spacing = rebar['stirrup']
        longitudinal, stirrups = _reinforce_beam(*extents, long_diam, long_count, stirrup_diam, spacing)
        lintel_entities.extend(add_reinforcement(f, body, storey, name_prefix, longitudinal, stirrups))

    def _box_from_extents(extents):
        x0, x1, y0, y1, z0, z1 = extents
        return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()

    lintel_entities, lintel_boxes = [], {}
    if door:
        add_opening(f, body, walls[1], base[1][0], door['offset'], door['width'], door['height'], 0, t)
        extents = _lintel_extents(base[1][0], door['offset'], door['width'], door['height'], door['height'] + LINTEL_HEIGHT, _wall_thickness('P02'))
        verga_box = _box_from_extents(extents)
        lintel_entities.append(add_lintel(f, body, storey, 'VERGA-P02', verga_box, 'LINTEL'))
        lintel_boxes.setdefault('P02', []).append(verga_box)
        _reinforce('VERGA-P02', extents)
    if window:
        add_opening(f, body, walls[0], base[0][0], window['offset'], window['width'], window['height'], window['sill'], t)
        top = window['sill'] + window['height']
        window_thickness = _wall_thickness('P01')
        extents = _lintel_extents(base[0][0], window['offset'], window['width'], top, top + LINTEL_HEIGHT, window_thickness)
        verga_box = _box_from_extents(extents)
        lintel_entities.append(add_lintel(f, body, storey, 'VERGA-P01', verga_box, 'LINTEL'))
        lintel_boxes.setdefault('P01', []).append(verga_box)
        _reinforce('VERGA-P01', extents)
        if contraverga:
            contra_extents = _lintel_extents(base[0][0], window['offset'], window['width'], window['sill'] - LINTEL_HEIGHT, window['sill'], window_thickness)
            contra_box = _box_from_extents(contra_extents)
            lintel_entities.append(add_lintel(f, body, storey, 'CONTRAVERGA-P01', contra_box, 'BEAM'))
            lintel_boxes.setdefault('P01', []).append(contra_box)
            _reinforce('CONTRAVERGA-P01', contra_extents)

    # Layer entities per wall -- each wall can carry its own sandwich
    # (e.g. render only on the street-facing side), keyed by name so a
    # wall with no entry just keeps its plain single-box representation.
    # The cut region for each wall's layers is the door/window void fused
    # with that wall's own lintel boxes -- without the fuse, the layer's
    # own frame material still filled the band above/below the opening
    # where a verga/contraverga now also sits, two exactly coincident
    # faces in the same place that z-fought on screen.
    layer_entities = {}
    if layers:
        opening_thickness_pad = t + 0.3
        def _cut_region(name, base_opening):
            boxes = ([base_opening] if base_opening is not None else []) + lintel_boxes.get(name, [])
            if not boxes:
                return None
            region = boxes[0]
            for b in boxes[1:]:
                region = BRepAlgoAPI_Fuse(region, b).Shape()
            return region
        openings = {
            'P01': _cut_region('P01', _opening_box_world(base[0][0], window['offset'], window['width'], window['height'], window['sill'], opening_thickness_pad) if window else None),
            'P02': _cut_region('P02', _opening_box_world(base[1][0], door['offset'], door['width'], door['height'], 0, opening_thickness_pad) if door else None),
        }
        for i, (a, b) in enumerate(base):
            name = f'P{i+1:02}'
            wall_layers = layers.get(name)
            if wall_layers:
                layer_entities[name] = attach_wall_layers(f, body, storey, name, a, b, wall_layers, _WALL_OUTWARD[i], h, openings.get(name))

    # Pilares (IfcColumn) at the 4 corners and a tie beam ('cinta',
    # IfcBeam) running the top of every wall, the concrete frame a real
    # alvenaria-de-vedação house is normally built on -- independent of
    # the roof block below (columns always run 0..h, matching wall
    # height; the roof, if any, sits on top the same way it already does
    # on the walls). Columns and beams are both concrete and share the
    # corner, so each tie beam is cut by the fused column boxes to avoid
    # two coincident faces there (the same z-fight this file already
    # avoids for the layer/lintel overlap above).
    structure_entities = []
    if structure:
        col_size = structure.get('columnSize', t)
        beam_height = structure.get('beamHeight', .2)
        corners = [('NO', -w/2, d/2), ('NE', w/2, d/2), ('SO', -w/2, -d/2), ('SE', w/2, -d/2)]
        column_boxes = []
        for name, cx, cy in corners:
            box = BRepPrimAPI_MakeBox(gp_Pnt(cx - col_size/2, cy - col_size/2, 0), gp_Pnt(cx + col_size/2, cy + col_size/2, h)).Shape()
            column_boxes.append(box)
            vertices, faces = _triangulate_occt(box)
            col = api.run('root.create_entity', f, ifc_class='IfcColumn', name=f'PILAR-{name}')
            api.run('spatial.assign_container', f, products=[col], relating_structure=storey)
            rep = api.run('geometry.add_mesh_representation', f, context=body, vertices=[vertices], faces=[faces])
            api.run('geometry.assign_representation', f, product=col, representation=rep)
            api.run('geometry.edit_object_placement', f, product=col)
            structure_entities.append(col)
            if rebar:
                long_diam, long_count = rebar['longitudinal']
                stirrup_diam, spacing = rebar['stirrup']
                longitudinal, stirrups = _reinforce_column(cx - col_size/2, cx + col_size/2, cy - col_size/2, cy + col_size/2, 0, h, long_diam, long_count, stirrup_diam, spacing)
                structure_entities.extend(add_reinforcement(f, body, storey, f'PILAR-{name}', longitudinal, stirrups))
        columns_fused = column_boxes[0]
        for b in column_boxes[1:]:
            columns_fused = BRepAlgoAPI_Fuse(columns_fused, b).Shape()
        for i, (a, b) in enumerate(base):
            name = f'P{i+1:02}'
            axis_horizontal = 'y' if a[0] == b[0] else 'x'
            extents = _tie_beam_extents(a, b, _wall_thickness(name), h - beam_height, h)
            beam_shape = BRepAlgoAPI_Cut(_box_from_extents(extents), columns_fused).Shape()
            structure_entities.append(add_lintel(f, body, storey, f'CINTA-{name}', beam_shape, 'BEAM'))
            if rebar:
                long_diam, long_count = rebar['longitudinal']
                stirrup_diam, spacing = rebar['stirrup']
                reinforce_extents = (extents[2], extents[3], extents[0], extents[1], extents[4], extents[5]) if axis_horizontal == 'y' else extents
                longitudinal, stirrups = _reinforce_beam(*reinforce_extents, long_diam, long_count, stirrup_diam, spacing, axis=axis_horizontal)
                structure_entities.extend(add_reinforcement(f, body, storey, f'CINTA-{name}', longitudinal, stirrups))

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
    for wall_name, wall_entities in layer_entities.items():
        for material, layer_wall in wall_entities:
            shape = ifcopenshell.geom.create_shape(settings, layer_wall)
            v = np.array(shape.geometry.verts).reshape(-1, 3)
            faces = np.array(shape.geometry.faces).reshape(-1, 3)
            meshes.append({'id': layer_wall.Name, 'guid': layer_wall.GlobalId, 'material': material, 'vertices': v.tolist(), 'faces': faces.tolist(), 'uv': _wall_uv(v, wall_name)})
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
        is_rebar = beam.is_a('IfcReinforcingBar')
        material = 'Aço' if is_rebar else 'Concreto'
        mesh = {'id': beam.Name, 'guid': beam.GlobalId, 'material': material, 'vertices': v.tolist(), 'faces': faces.tolist()}
        if not is_rebar:
            # Verga/contraverga are always north-south oriented (only P01/P02
            # ever get a door or window), so the P01 axis pair (x, height)
            # is correct here regardless of which wall the beam belongs to.
            mesh['uv'] = _wall_uv(v, 'P01')
        meshes.append(mesh)
    for elem in structure_entities:
        shape = ifcopenshell.geom.create_shape(settings, elem)
        v = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        material = 'Aço' if elem.is_a('IfcReinforcingBar') else 'Concreto'
        meshes.append({'id': elem.Name, 'guid': elem.GlobalId, 'material': material, 'vertices': v.tolist(), 'faces': faces.tolist()})
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
                rebar={'longitudinal': (float(req['rebar']['longitudinal']['diameter']), int(req['rebar']['longitudinal']['count'])), 'stirrup': (float(req['rebar']['stirrup']['diameter']), float(req['rebar']['stirrup']['spacing']))} if req.get('rebar') else None,
                structure={'columnSize': float(req['structure']['columnSize']), 'beamHeight': float(req['structure']['beamHeight'])} if req.get('structure') else None,
            )
            print(json.dumps({'type': 'result', 'id': req.get('id'), 'elapsed_seconds': round(time.perf_counter() - t0, 3), 'meshes': meshes}), flush=True)
        except Exception as e:
            print(json.dumps({'type': 'error', 'id': req.get('id') if 'req' in dir() else None, 'message': str(e)}), flush=True)

START = time.perf_counter()
if __name__ == '__main__':
    main()
