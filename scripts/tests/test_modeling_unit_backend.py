"""Mock-backend API contract tests. NOT solver, topology, or geometry evidence."""
from contextlib import ExitStack
import math
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from fcskill.modeling import _core, datum, parameters, sketch
from fcskill.modeling.sweeps import parameter_domains, plan_samples, sweep_parameters


class Obj:
    def __init__(self, doc, type_id, name):
        self.Document, self.TypeId, self.Name = doc, type_id, name
        self.Label, self.State, self.PropertiesList = name, [], ["Name", "Label"]
        self.Group, self.Tip, self.ExpressionEngine = [], None, []
        self.types, self.Geometry, self.Constraints, self.labels = {}, [], [], {}
        self.FullyConstrained = False
        if type_id in ("Sketcher::SketchObject", "PartDesign::Plane"):
            self.PropertiesList += ["AttachmentSupport", "MapMode", "AttachmentOffset"]
            self.AttachmentOffset = SimpleNamespace(Base=SimpleNamespace(z=0))
        if type_id == "PartDesign::Body":
            self.Origin = SimpleNamespace(OriginFeatures=[])
            for role in datum.PLANE_ROLES.values():
                plane = doc.addObject("App::Plane", name + role)
                plane.Role = role
                self.Origin.OriginFeatures.append(plane)
    def newObject(self, type_id, name):
        obj = self.Document.addObject(type_id, name)
        self.Group.append(obj)
        return obj
    def addProperty(self, type_id, name, *args):
        self.PropertiesList.append(name)
        self.types[name] = type_id
        setattr(self, name, None)
    def getTypeIdOfProperty(self, name): return self.types[name]
    def setEditorMode(self, *args): pass
    def setExpression(self, path, expr): self.ExpressionEngine.append((path, expr))
    def addGeometry(self, geometry, construction):
        self.Geometry.append(geometry)
        return len(self.Geometry) - 1
    def addConstraint(self, constraint):
        self.Constraints.append(constraint)
        return len(self.Constraints) - 1
    def renameConstraint(self, index, name): self.labels[index] = name


class Doc:
    Name = "MockDocument"
    def __init__(self): self.items, self.removed = {}, []
    def addObject(self, type_id, name):
        obj = Obj(self, type_id, name)
        self.items[name] = obj
        return obj
    def getObject(self, name): return self.items.get(name)
    def removeObject(self, name):
        self.removed.append(name)
        obj = self.items.pop(name)
        for other in self.items.values():
            if obj in other.Group: other.Group.remove(obj)
    def recompute(self): pass


def vector(x, y, z): return SimpleNamespace(x=x, y=y, z=z)


class MockBackendContractTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(sys.modules, {
            "FreeCAD": SimpleNamespace(GuiUp=False, Vector=vector),
            "Part": SimpleNamespace(LineSegment=lambda a, b: (a, b),
                                    Circle=lambda c, normal, r: SimpleNamespace(Center=c, Radius=r)),
            "Sketcher": SimpleNamespace(Constraint=lambda *args: args)}))
        self.doc = Doc()
        self.body = self.doc.addObject("PartDesign::Body", "Body")

    def test_stale_shape_never_passes(self):
        obj = self.body.newObject("PartDesign::Pad", "Stale")
        obj.State = ["Invalid"]
        obj.Shape = SimpleNamespace(isNull=lambda: False, isValid=lambda: True, Solids=[1], Volume=100)
        with self.assertRaises(_core.ModelingError) as ctx: _core.solid_metrics(obj)
        self.assertEqual(ctx.exception.code, "STALE_OR_INVALID_FEATURE")

    def test_unknown_state_never_passes(self):
        obj = self.body.newObject("PartDesign::Pad", "Unknown")
        del obj.State
        with self.assertRaises(_core.ModelingError): _core.solid_metrics(obj)

    def test_duplicate_name_preserved(self):
        existing = self.doc.addObject("Part::Feature", "Thing")
        with self.assertRaises(_core.ModelingError):
            with _core.new_object(self.doc, "Part::Feature", "Thing"): pass
        self.assertIs(self.doc.getObject("Thing"), existing)
        self.assertEqual(self.doc.removed, [])

    def test_failed_creation_removes_only_new(self):
        old = self.body.newObject("PartDesign::Pad", "Old")
        self.body.Tip = old
        with self.assertRaises(RuntimeError):
            with _core.new_object(self.body, "PartDesign::Pad", "New") as new:
                self.body.Tip = new
                raise RuntimeError("injected failure")
        self.assertIs(self.body.Tip, old)
        self.assertIs(self.doc.getObject("Old"), old)
        self.assertEqual(self.doc.removed, ["New"])

    def test_identity_change_not_removed(self):
        with self.assertRaises(_core.ModelingError) as ctx:
            with _core.new_object(self.doc, "Part::Feature", "New"):
                self.doc.items["New"] = Obj(self.doc, "Part::Feature", "New")
                raise RuntimeError("identity replaced")
        self.assertEqual(ctx.exception.code, "CLEANUP_FAILED")
        self.assertEqual(self.doc.removed, [])

    def test_body_local_origin_not_global_name(self):
        second = self.doc.addObject("PartDesign::Body", "Second")
        plane = datum.origin_plane(second, "XY")
        self.assertIn(plane, second.Origin.OriginFeatures)
        self.assertNotIn(plane, self.body.Origin.OriginFeatures)

    def test_ambiguous_role_refused(self):
        self.body.Origin.OriginFeatures.append(self.body.Origin.OriginFeatures[0])
        with self.assertRaises(_core.ModelingError): datum.origin_plane(self.body)

    def test_missing_role_refused(self):
        self.body.Origin.OriginFeatures.clear()
        with self.assertRaises(_core.ModelingError): datum.origin_plane(self.body)

    def test_wrong_body_support_refused(self):
        second = self.doc.addObject("PartDesign::Body", "Second")
        with self.assertRaises(_core.ModelingError): datum.resolve_support(self.body, datum.origin_plane(second))

    def test_generated_face_attachment_refused(self):
        solid = self.body.newObject("PartDesign::Pad", "Pad")
        with self.assertRaises(_core.ModelingError): datum.resolve_support(self.body, solid)

    def test_offset_expression_attaches_to_local_normal(self):
        plane = datum.offset_plane(self.body, "Top", offset=_core.Dim(5, "Params.Thickness"))
        self.assertEqual(plane.MapMode, "FlatFace")
        self.assertEqual(plane.AttachmentOffset.Base.z, 5)
        self.assertIn(("AttachmentOffset.Base.z", "Params.Thickness"), plane.ExpressionEngine)

    def test_rectangle_constraints_no_block(self):
        with patch.object(sketch, "_finish"):
            obj = sketch.rectangle(self.body, "Rectangle", _core.Dim(40, "Params.Width"), 30)
        types = [c[0] for c in obj.Constraints]
        self.assertNotIn("Block", types)
        self.assertEqual(types.count("Coincident"), 4)
        self.assertEqual(types.count("Horizontal"), 2)
        self.assertEqual(types.count("Vertical"), 2)
        self.assertIn("Symmetric", types)
        self.assertEqual(set(obj.labels.values()), {"Width", "Height"})
        self.assertIn(("Constraints[8]", "Params.Width"), obj.ExpressionEngine)

    def test_corner_rectangle_anchors_to_origin(self):
        with patch.object(sketch, "_finish"):
            obj = sketch.rectangle(self.body, "Rectangle", 40, 30, centered=False)
        self.assertNotIn("Symmetric", [c[0] for c in obj.Constraints])
        self.assertEqual(obj.Constraints[-1], ("Coincident", 0, 1, -1, 1))

    def test_circle_origin_and_axes(self):
        with patch.object(sketch, "_finish"):
            obj = sketch.circles(self.body, "Holes", 1, [(0, 0), (0, 5), (5, 0)])
        kinds = [c[0] for c in obj.Constraints]
        self.assertEqual(kinds.count("Radius"), 3)
        self.assertEqual(kinds.count("PointOnObject"), 2)
        self.assertNotIn("Block", kinds)

    def test_overlap_refused_without_new_object(self):
        before = set(self.doc.items)
        with self.assertRaises(ValueError): sketch.circles(self.body, "Bad", 2, [(0, 0), (3, 0)])
        self.assertEqual(before, set(self.doc.items))

    def test_touching_circles_refused(self):
        with self.assertRaises(ValueError): sketch._check_disjoint([(0, 0, 1), (2, 0, 1)])

    def test_parameter_metadata_roundtrip_and_reference(self):
        obj = parameters.create_parameters(self.doc, "Params", {"Width": parameters.Parameter(40, 30, 60)})
        self.assertEqual(parameters.read_schema(obj)["Width"].value, 40)
        self.assertEqual(parameters.reference(obj, "Width"), _core.Dim(40, "Params.Width"))

    def test_native_property_collision_cleanup(self):
        with self.assertRaises(ValueError):
            parameters.create_parameters(self.doc, "Params", {"Name": parameters.Parameter(1, 0, 2)})
        self.assertIsNone(self.doc.getObject("Params"))

    def test_parameter_type_drift_refused(self):
        obj = parameters.create_parameters(self.doc, "Params", {"Width": parameters.Parameter(40, 30, 60)})
        obj.types["Width"] = "App::PropertyFloat"
        with self.assertRaises(_core.ModelingError): parameters.read_schema(obj)

    def test_expression_driven_parameter_refused(self):
        obj = parameters.create_parameters(self.doc, "Params", {"Width": parameters.Parameter(40, 30, 60)})
        obj.setExpression("Width", "Other.Width")
        with self.assertRaises(_core.ModelingError): parameter_domains(obj)

    def test_parameter_selection_requires_explicit_sequence(self):
        obj = parameters.create_parameters(self.doc, "Params", {"X": parameters.Parameter(4, 3, 6)})
        with self.assertRaises(ValueError): parameter_domains(obj, "X")
        self.assertEqual(list(parameter_domains(obj, ["X"])), ["X"])

    def test_supplied_coverage_cannot_fabricate_evidence(self):
        obj = parameters.create_parameters(self.doc, "Params", {"Width": parameters.Parameter(40, 30, 60)})
        plan = plan_samples(parameter_domains(obj), max_cases=1)
        plan["coverage"]["all_corners_included"] = True
        plan["coverage"]["continuous_domain_proven"] = True
        result = sweep_parameters(obj, plan, validate=lambda: {"status": "PASS", "requirement": "MOCK_ONLY"})
        self.assertFalse(result["planned_coverage"]["all_corners_included"])
        self.assertFalse(result["passing_coverage"]["continuous_domain_proven"])

    def test_native_bridge_restores_mock_values(self):
        obj = parameters.create_parameters(self.doc, "Params", {"Width": parameters.Parameter(40, 30, 60)})
        plan = plan_samples(parameter_domains(obj), max_cases=4)
        result = sweep_parameters(obj, plan, validate=lambda: {"status": "PASS", "requirement": "MOCK_ONLY"})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(obj.Width, 40)

    def test_native_bridge_stale_plan_refused(self):
        obj = parameters.create_parameters(self.doc, "Params", {"Width": parameters.Parameter(40, 30, 60)})
        plan = plan_samples(parameter_domains(obj), max_cases=4)
        obj.Width = 45
        with self.assertRaises(ValueError): sweep_parameters(obj, plan, validate=lambda: {})
        self.assertEqual(obj.Width, 45)


if __name__ == "__main__": unittest.main()
