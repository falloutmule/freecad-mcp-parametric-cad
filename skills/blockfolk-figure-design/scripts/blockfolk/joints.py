"""Generic native-OCCT two-body fixtures, not a character/document builder.

Local X is the axle; Y is print height, with the rear datum at Y=0.
Return shapes for engineering evaluation. For editable deliverables, rebuild
these operations as native features with fcskill parameters (see implementation).
No document, session, file, transport or GUI side effects occur here.
"""
from dataclasses import dataclass
import math
from .parameters import Hinge, Process


@dataclass
class Fixture:
    parent: object
    child: object
    cam: object
    leaves: object
    witnesses: dict
    projected_cap: float
    opening: float
    metadata: dict


def hinge(spec=None, process=None, holding=True):
    import FreeCAD as App
    import Part
    s, p = spec or Hinge(), process or Process()
    d = s.derived(p, holding)
    V = App.Vector
    h, width, bore = d['axis_height'], d['bearing_width'], d['bore']

    def cylinder(radius, start, length):
        return Part.makeCylinder(radius, length, V(start, h, 0), V(1, 0, 0))

    def profile(points, x):
        vertices = [V(x, h+y, z) for y, z in points]
        return Part.makePolygon(vertices + [vertices[0]])

    def prism(points, start, length):
        return Part.Face(profile(points, start)).extrude(V(length, 0, 0))

    left = cylinder(s.cap_radius, -s.cap_inner_half_span-s.cap_thickness, s.cap_thickness)
    right = cylinder(s.cap_radius, s.cap_inner_half_span, s.cap_thickness)
    journal = cylinder(s.journal_radius, -s.cap_inner_half_span-.1, 2*s.cap_inner_half_span+.2)
    q = bore / math.sqrt(2)
    roof_points = [(q, -q), (bore*math.sqrt(2), 0), (q, q)]
    bore_tool = cylinder(bore, -width/2-.1, width+.2).fuse(prism(roof_points, -width/2-.1, width+.2))
    outer = cylinder(s.shell_radius, -width/2, width)
    child = outer.cut(bore_tool)
    cam, leaves = Part.Shape(), Part.Shape()
    if holding:
        child = child.cut(cylinder(s.chamber_radius, -s.chamber_width/2, s.chamber_width))
        ri, ro = s.leaf_inner_radius, s.leaf_inner_radius+s.leaf_thickness
        # Root extends into the bearing shell. Scale root reach with the journal,
        # independently of character height. Both opposed leaves root at the rear.
        root = min(s.shell_radius-.3, h+.1)
        pts = [(-root, 0)]
        pts += [(ri*math.cos(math.radians(a)), ri*math.sin(math.radians(a))) for a in (170,158,146,134,122,110,100)]
        pts += [(0, s.tooth_radius), (0, ro)]
        pts += [(ro*math.cos(math.radians(a)), ro*math.sin(math.radians(a))) for a in (100,110,122,134,146,158,170)]
        pts += [(-root-.1, s.leaf_thickness)]
        all_leaves, reliefs = [], []
        for sign in (1, -1):
            points = [(y, sign*z) for y,z in pts]
            wire = profile(points, -s.leaf_width/2)
            all_leaves.append(Part.Face(wire).extrude(V(s.leaf_width,0,0)))
            expanded = wire.makeOffset2D(p.release_gap, join=0)
            if len(expanded.Wires) != 1 or Part.Face(expanded.Wires[0]).Area <= Part.Face(wire).Area:
                raise ValueError('Release offset failed to expand the entire follower')
            expanded.translate(V(-(s.cam_width-s.leaf_width)/2-.1,0,0))
            reliefs.append(Part.Face(expanded.Wires[0]).extrude(V(s.cam_width+.2,0,0)))
        leaves = all_leaves[0].fuse(all_leaves[1])
        cam = cylinder(s.cam_radius, -s.cam_width/2, s.cam_width)
        for tool in reliefs:
            cam = cam.cut(tool)
        # Relieve journal material in the cam lane; otherwise it bypasses reliefs.
        journal = journal.cut(cylinder(s.journal_radius+.2, -s.cam_width/2, s.cam_width))
        child = child.fuse(leaves)
    parent = left.fuse(right).fuse(journal)
    if holding:
        parent = parent.fuse(cam)
    extent = max(s.shell_radius, s.cap_radius)*4
    datum = Part.makeBox(extent, extent, 2*extent, V(-extent/2,0,-extent))
    child = child.common(datum).removeSplitter()
    if holding:
        leaves = leaves.common(datum)
    parent = parent.removeSplitter()
    # Complete annulus outside every opening is a sufficient rigid witness.
    # Refuse dimensions for which this conservative proof cannot be constructed.
    hoop_inner = max(bore*math.sqrt(2), s.chamber_radius if holding else 0)+.06
    hoop_outer = min(s.cap_radius, h)-.05
    if hoop_outer <= hoop_inner:
        raise ValueError('No complete capture-hoop witness fits; redesign or provide another proof')
    hoop = cylinder(hoop_outer, -width/2, width).cut(cylinder(hoop_inner, -width/2, width))
    land = d['guide_land']
    guides = {}
    # Interior witnesses avoid coincident Boolean faces. Account for their
    # 0.001 mm inset in the conservative play and span bounds below.
    inset = .001
    guide_bore = cylinder(bore+inset, -width/2-.1, width+.2)
    gq = (bore+inset)/math.sqrt(2)
    guide_bore = guide_bore.fuse(prism([(gq,-gq),((bore+inset)*math.sqrt(2),0),(gq,gq)], -width/2-.1,width+.2))
    for key, start in [('guide_left', -width/2), ('guide_right', width/2-land)]:
        guides[key] = cylinder(hoop_outer, start+inset, land-2*inset).cut(guide_bore)
    play = (p.clearance+inset)*math.sqrt(2)
    tilt = math.atan2(2*play, width-land-2*inset)
    projected = 2*s.cap_radius*math.cos(tilt)
    opening = max(bore*(1+math.sqrt(2)), 2*hoop_inner)
    return Fixture(parent, child, cam, leaves,
                   dict(cap_left=left, cap_right=right, closed_hoop=hoop, **guides),
                   projected, opening,
                   dict(holding=holding, axis=[1,0,0], center=[0,h,0],
                        rear_datum_y=0, radial_clearance=p.clearance,
                        neutral_release_gap=p.release_gap if holding else None,
                        guide_span=width-land-2*inset, guide_witness_inset_mm=inset,
                        tilt_bound_degrees=math.degrees(tilt),
                        status='CAD FIXTURE ONLY; new geometry has no physical print record'))


def rotated(shape, center, axis, angle):
    """Rotate a copy in an already resolved common frame; input is unchanged."""
    import FreeCAD as App
    result = shape.copy()
    result.rotate(App.Vector(*center), App.Vector(*axis), angle)
    return result
