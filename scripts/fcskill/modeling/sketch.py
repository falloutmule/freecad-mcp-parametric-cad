"""Constraint-driven rectangular and circular profiles; never Block fixtures."""
from __future__ import annotations
import math
from ._core import ModelingError, dimension, finite, new_object, recompute_check, require_live
from .datum import _attach_new, resolve_support


def inspect_sketch(sketch) -> dict:
    """Read-only snapshot. Unknown solver diagnostics are None, not invented zeros."""
    require_live(sketch, type_id="Sketcher::SketchObject")
    raw_state = getattr(sketch, "State", None)
    state = [str(v) for v in raw_state] if isinstance(raw_state, (list, tuple)) else []
    stale = not isinstance(raw_state, (list, tuple)) or any(
        word in s.lower() for s in state for word in ("invalid", "error", "touched"))
    fully = getattr(sketch, "FullyConstrained", None)
    result = {"object": sketch.Name, "state": state, "fresh": not stale,
              "fully_constrained": fully, "remaining_dof": 0 if fully is True and not stale else None,
              "redundant_constraints": None, "conflicting_constraints": None,
              "profile_closed": None, "shape_valid": None, "wire_count": None,
              "self_intersections": None,
              "unchecked": ["generic self/inter-wire intersections", "detailed solver diagnostics"]}
    try:
        shape = sketch.Shape
        wires = list(shape.Wires)
        result.update(shape_valid=not shape.isNull() and shape.isValid(), wire_count=len(wires),
                      profile_closed=bool(wires) and all(w.isClosed() for w in wires)
                      and sum(len(w.Edges) for w in wires) == len(shape.Edges))
    except Exception as exc:
        result["geometry_error"] = str(exc)
    return result


def _finish(sketch) -> None:
    import Part
    recompute_check(sketch.Document, [sketch])
    code = sketch.solve()
    if code != 0:
        raise ModelingError("SKETCH_SOLVER", "Sketch solver did not return success", solve_code=code)
    recompute_check(sketch.Document, [sketch])
    info = inspect_sketch(sketch)
    if not (info["fresh"] and info["fully_constrained"] is True and
            info["profile_closed"] is True and info["shape_valid"] is True):
        raise ModelingError("SKETCH_UNVERIFIED", "Sketch failed the fully-constrained closed-profile gate", snapshot=info)
    # This is a per-wire native check, not a proof about arbitrary multi-wire profiles.
    for wire in sketch.Shape.Wires:
        face = Part.Face(wire)
        if not face.isValid() or not math.isfinite(face.Area) or face.Area <= 0:
            raise ModelingError("INVALID_PROFILE", "Profile wire does not form a valid positive-area face")


def _dimension_constraint(sketch, constraint, label: str, dim) -> int:
    index = sketch.addConstraint(constraint)
    sketch.renameConstraint(index, label)
    if dim.expression is not None:
        sketch.setExpression(f"Constraints[{index}]", dim.expression)
    return index


def rectangle(body, name: str, width, height, *, centered: bool = True, support="XY", offset=0):
    """Create a new sketch centered on origin, or with its lower-left at origin.

    Width/height are in mm. Eight geometric constraints close/align the four
    lines; two dimensions and origin coincidence/symmetry express design intent.
    """
    import FreeCAD as App
    import Part
    import Sketcher
    if not isinstance(centered, bool):
        raise ValueError("centered must be bool")
    w, h = dimension(width, "width", positive=True), dimension(height, "height", positive=True)
    dz = dimension(offset, "offset")
    base = resolve_support(body, support)
    x, y = (-w.value / 2, -h.value / 2) if centered else (0, 0)
    points = [(x, y), (x + w.value, y), (x + w.value, y + h.value), (x, y + h.value)]
    with new_object(body, "Sketcher::SketchObject", name) as sketch:
        _attach_new(sketch, base, dz)
        edges = [sketch.addGeometry(Part.LineSegment(App.Vector(*points[i], 0),
                    App.Vector(*points[(i + 1) % 4], 0)), False) for i in range(4)]
        for i, edge in enumerate(edges):
            sketch.addConstraint(Sketcher.Constraint("Coincident", edge, 2, edges[(i + 1) % 4], 1))
            sketch.addConstraint(Sketcher.Constraint("Horizontal" if i % 2 == 0 else "Vertical", edge))
        _dimension_constraint(sketch, Sketcher.Constraint("Distance", edges[0], w.value), "Width", w)
        _dimension_constraint(sketch, Sketcher.Constraint("Distance", edges[1], h.value), "Height", h)
        if centered:
            sketch.addConstraint(Sketcher.Constraint("Symmetric", edges[0], 1, edges[2], 1, -1, 1))
        else:
            sketch.addConstraint(Sketcher.Constraint("Coincident", edges[0], 1, -1, 1))
        _finish(sketch)
        return sketch


def _locate_center(sketch, index: int, x: float, y: float, Sketcher) -> None:
    if x == 0 and y == 0:
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 3, -1, 1))
        return
    for value, dim_type, axis in ((x, "DistanceX", -2), (y, "DistanceY", -1)):
        # Avoid zero distance constraints; zero coordinates express point-on-axis.
        constraint = (Sketcher.Constraint("PointOnObject", index, 3, axis) if value == 0
                      else Sketcher.Constraint(dim_type, index, 3, value))
        sketch.addConstraint(constraint)


def circles(body, name: str, radius, centers=((0, 0),), *, support="XY", offset=0):
    """1..64 disjoint equal-radius circles at explicit numeric centers, in mm.

    Radius is parametric. Centers are intentionally fixed coordinates, not a
    native PartDesign pattern and not an inferred bolt-circle requirement.
    """
    import FreeCAD as App
    import Part
    import Sketcher
    r, dz = dimension(radius, "radius", positive=True), dimension(offset, "offset")
    if not isinstance(centers, (tuple, list)) or not 1 <= len(centers) <= 64:
        raise ValueError("Provide an explicit list/tuple of 1..64 centers")
    points = []
    for point in centers:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError("Each center must contain exactly x and y")
        points.append((finite(point[0], "center x"), finite(point[1], "center y")))
    _check_disjoint([(x, y, r.value) for x, y in points])
    base = resolve_support(body, support)
    with new_object(body, "Sketcher::SketchObject", name) as sketch:
        _attach_new(sketch, base, dz)
        indices = []
        for i, (x, y) in enumerate(points):
            index = sketch.addGeometry(Part.Circle(App.Vector(x, y, 0), App.Vector(0, 0, 1), r.value), False)
            indices.append(index)
            _locate_center(sketch, index, x, y, Sketcher)
            _dimension_constraint(sketch, Sketcher.Constraint("Radius", index, r.value), f"Radius{i + 1}", r)
        _finish(sketch)
        # Evaluate actual solved geometry, not merely the expression's numeric seed.
        actual = [(sketch.Geometry[i].Center.x, sketch.Geometry[i].Center.y, sketch.Geometry[i].Radius)
                  for i in indices]
        _check_disjoint(actual)
        return sketch


def _check_disjoint(circles_data) -> None:
    for i, (x, y, radius) in enumerate(circles_data):
        finite(radius, "solved radius", positive=True)
        for other_x, other_y, other_r in circles_data[:i]:
            if math.hypot(x - other_x, y - other_y) <= radius + other_r:
                raise ValueError("Circle profiles must be separate, non-tangent, and non-overlapping")


def circle(body, name: str, radius, *, center=(0, 0), support="XY", offset=0):
    return circles(body, name, radius, [center], support=support, offset=offset)
