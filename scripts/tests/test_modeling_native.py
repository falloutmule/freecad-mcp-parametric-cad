"""REAL FreeCAD acceptance fixtures. Skips are NOT native acceptance.

Creates and closes ONLY uniquely named test-owned documents. Never launches,
restarts, closes, saves, or recomputes the user's existing documents. Run on the
GUI thread or in a fresh compatible FreeCAD Python process. A kernel call can
still hang; use a disposable host, not your production FreeCAD session.
"""
import math
from pathlib import Path
import tempfile
import unittest
import uuid
try:
    import FreeCAD as App
    import Part
except ImportError:
    App = None

from fcskill import modeling as M
from fcskill.modeling._core import recompute_check
from fcskill.modeling.sweeps import parameter_domains, plan_samples, sweep_parameters


@unittest.skipUnless(App is not None, "Native FreeCAD/Part unavailable; no CAD geometry executed")
class NativeModelingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fcskill-native-upgrade-")
        self.documents = []
        self.doc = self.new_document()

    def new_document(self):
        doc = App.newDocument("FcskillNative_" + uuid.uuid4().hex)
        self.documents.append((doc.Name, doc))
        return doc

    def tearDown(self):
        for name, obj in reversed(self.documents):
            if name in App.listDocuments() and App.getDocument(name) == obj:
                App.closeDocument(name)
        self.temp.cleanup()

    def plate(self):
        from examples.parametric_mounting_plate import build
        return build(self.doc)

    def test_rectangle_pad_volume_and_edit(self):
        p = M.create_parameters(self.doc, "Params", {"Width": M.Parameter(40, 30, 60)})
        body = M.create_body(self.doc, "Body")
        profile = M.rectangle(body, "Outline", M.reference(p, "Width"), 30)
        feature = M.pad(body, "Pad", profile, 5)
        self.assertTrue(profile.FullyConstrained)
        self.assertAlmostEqual(feature.Shape.Volume, 6000, places=6)
        p.Width = 50
        recompute_check(self.doc, [profile, feature])
        self.assertAlmostEqual(feature.Shape.Volume, 7500, places=6)
        self.assertAlmostEqual(feature.Shape.BoundBox.XMin, -25, places=6)
        self.assertAlmostEqual(feature.Shape.BoundBox.XMax, 25, places=6)

    def test_rectangle_design_intent_constraints(self):
        body = M.create_body(self.doc, "Body")
        profile = M.rectangle(body, "Outline", 20, 10)
        types = [c.Type for c in profile.Constraints]
        self.assertNotIn("Block", types)
        self.assertIn("Symmetric", types)
        self.assertTrue(M.inspect_sketch(profile)["profile_closed"])
        self.assertEqual(M.inspect_sketch(profile)["remaining_dof"], 0)

    def test_corner_rectangle(self):
        body = M.create_body(self.doc, "Body")
        sketch = M.rectangle(body, "Corner", 20, 10, centered=False)
        result = M.pad(body, "Pad", sketch, 3)
        self.assertAlmostEqual(result.Shape.BoundBox.XMin, 0, places=6)
        self.assertAlmostEqual(result.Shape.BoundBox.YMin, 0, places=6)
        self.assertAlmostEqual(result.Shape.Volume, 600, places=6)

    def test_circle_origin_and_axis_centers(self):
        body = M.create_body(self.doc, "Body")
        sk = M.circles(body, "Circles", 1, [(0, 0), (0, 5), (5, 0), (-5, 0), (0, -5)])
        self.assertTrue(sk.FullyConstrained)
        self.assertEqual(len(sk.Shape.Wires), 5)

    def test_parameter_radius_edit(self):
        p = M.create_parameters(self.doc, "Params", {"Radius": M.Parameter(2, 1, 4)})
        body = M.create_body(self.doc, "Body")
        profile = M.circle(body, "Profile", M.reference(p, "Radius"))
        pad = M.pad(body, "Pad", profile, 5)
        p.Radius = 3
        recompute_check(self.doc, [profile, pad])
        self.assertAlmostEqual(pad.Shape.Volume, math.pi * 9 * 5, places=6)

    def test_body_local_origin_with_multiple_bodies(self):
        first = M.create_body(self.doc, "First")
        second = M.create_body(self.doc, "Second")
        first_plane, second_plane = M.origin_plane(first), M.origin_plane(second)
        self.assertNotEqual(first_plane, second_plane)
        self.assertIn(second_plane, second.Origin.OriginFeatures)
        sk = M.rectangle(second, "SecondSketch", 10, 8)
        property_name = "AttachmentSupport" if "AttachmentSupport" in sk.PropertiesList else "Support"
        support_entries = list(getattr(sk, property_name))
        self.assertEqual(len(support_entries), 1)
        self.assertEqual(support_entries[0][0], second_plane)

    def test_datum_moves_with_parameter(self):
        p = M.create_parameters(self.doc, "Params", {"Height": M.Parameter(5, 2, 10)})
        body = M.create_body(self.doc, "Body")
        plane = M.offset_plane(body, "Top", offset=M.reference(p, "Height"))
        sk = M.rectangle(body, "Profile", 10, 8, support=plane)
        p.Height = 9
        recompute_check(self.doc, [plane, sk])
        self.assertAlmostEqual(sk.Placement.Base.z, 9, places=6)

    def test_mounting_plate_analytic_volume(self):
        out = self.plate()
        expected = 40 * 30 * 5 - 4 * math.pi * 2**2 * 5
        self.assertAlmostEqual(out["result"].Shape.Volume, expected, places=5)
        self.assertEqual(M.solid_metrics(out["result"])["solid_count"], 1)

    def test_mounting_plate_parameter_edit(self):
        out = self.plate()
        p = out["parameters"]
        p.Width, p.Height, p.Thickness, p.HoleRadius = 36, 28, 6, 3
        recompute_check(self.doc, [out["profile"], out["hole_profiles"], out["result"]])
        self.assertAlmostEqual(out["result"].Shape.Volume, 36 * 28 * 6 - 4 * math.pi * 9 * 6, places=5)

    def test_duplicate_name_preserves_existing(self):
        body = M.create_body(self.doc, "Body")
        original = M.rectangle(body, "Outline", 10, 10)
        before = len(self.doc.Objects)
        with self.assertRaises(M.ModelingError): M.rectangle(body, "Outline", 30, 30)
        self.assertEqual(self.doc.getObject("Outline"), original)
        self.assertEqual(len(self.doc.Objects), before)

    def test_invalid_dimensions_do_not_create_objects(self):
        body = M.create_body(self.doc, "Body")
        before = len(self.doc.Objects)
        with self.assertRaises(ValueError): M.rectangle(body, "Bad", -1, 10)
        self.assertEqual(len(self.doc.Objects), before)

    def test_wrong_body_profile_is_rejected(self):
        first = M.create_body(self.doc, "First")
        second = M.create_body(self.doc, "Second")
        profile = M.rectangle(first, "Profile", 10, 10)
        with self.assertRaises(M.ModelingError): M.pad(second, "BadPad", profile, 5)
        self.assertIsNone(self.doc.getObject("BadPad"))

    def test_revolve_volume(self):
        body = M.create_body(self.doc, "Body")
        profile = M.rectangle(body, "Profile", 5, 10, centered=False, support="XZ")
        result = M.revolve(body, "Revolution", profile)
        self.assertAlmostEqual(result.Shape.Volume, math.pi * 25 * 10, places=5)

    def test_groove_volume(self):
        body = M.create_body(self.doc, "Body")
        profile = M.rectangle(body, "OuterProfile", 5, 10, centered=False, support="XZ")
        M.revolve(body, "OuterRevolution", profile)
        cut = M.rectangle(body, "InnerProfile", 2, 10, centered=False, support="XZ")
        result = M.groove(body, "Groove", cut)
        self.assertAlmostEqual(result.Shape.Volume, math.pi * (25 - 4) * 10, places=5)

    def test_additive_loft_volume(self):
        body = M.create_body(self.doc, "Body")
        a = M.rectangle(body, "Bottom", 20, 20)
        top = M.offset_plane(body, "TopPlane", offset=10)
        b = M.rectangle(body, "Top", 10, 10, support=top)
        result = M.additive_loft(body, "Loft", [a, b], ruled=True)
        self.assertAlmostEqual(result.Shape.Volume, 10 / 3 * (400 + 100 + 200), places=5)

    def test_subtractive_loft_volume(self):
        body = M.create_body(self.doc, "Body")
        outline = M.rectangle(body, "Outline", 20, 20)
        M.pad(body, "Base", outline, 10)
        a = M.circle(body, "LowerHole", 2)
        top = M.offset_plane(body, "TopPlane", offset=10)
        b = M.circle(body, "UpperHole", 2, support=top)
        result = M.subtractive_loft(body, "LoftCut", [a, b], ruled=True)
        self.assertAlmostEqual(result.Shape.Volume, 4000 - math.pi * 4 * 10, places=5)

    def test_sample_and_restore_geometry(self):
        out = self.plate()
        plan = plan_samples(parameter_domains(out["parameters"], ["Width", "HoleRadius"]), max_cases=9)
        before = out["result"].Shape.Volume
        def validate():
            p = out["parameters"]
            measured = M.solid_metrics(out["result"])
            expected = p.Width.Value * p.Height.Value * p.Thickness.Value - 4 * math.pi * p.HoleRadius.Value**2 * p.Thickness.Value
            measured.update(requirement="PLATE_ANALYTIC_VOLUME",
                            status="PASS" if abs(measured["volume_mm3"] - expected) < 1e-5 else "FAIL")
            return measured
        report = sweep_parameters(out["parameters"], plan, validate=validate, deadline_seconds=120)
        self.assertEqual(report["status"], "PASS", report)
        self.assertAlmostEqual(out["result"].Shape.Volume, before, places=5)

    def test_fcstd_reopen_and_edit(self):
        out = self.plate()
        path = Path(self.temp.name) / "plate.FCStd"
        self.doc.saveAs(str(path))
        old_name = self.doc.Name
        App.closeDocument(old_name)  # Explicitly test-owned document, just saved to a new owned path.
        self.doc = App.openDocument(str(path))
        self.documents.append((self.doc.Name, self.doc))
        p = self.doc.getObject("DemoParameters")
        feature = self.doc.getObject("DemoHoles")
        p.Width = 50
        recompute_check(self.doc, [feature])
        self.assertAlmostEqual(feature.Shape.Volume, 50 * 30 * 5 - 4 * math.pi * 4 * 5, places=5)
        self.assertEqual(p.getTypeIdOfProperty("Width"), "App::PropertyLength")

    def test_step_roundtrip(self):
        out = self.plate()
        path = Path(self.temp.name) / "plate.step"
        Part.export([out["result"]], str(path))
        shape = Part.Shape()
        shape.read(str(path))
        self.assertTrue(shape.isValid())
        self.assertEqual(len(shape.Solids), 1)
        self.assertAlmostEqual(shape.Volume, out["result"].Shape.Volume, places=4)


if __name__ == "__main__": unittest.main()
