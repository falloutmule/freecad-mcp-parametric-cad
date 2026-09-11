"""Run under installed FreeCAD Python or on an isolated MCP GUI thread."""
import json
from pathlib import Path
import tempfile
import unittest
import FreeCAD as A
import Part
from fcskill import frames as F, geometry as G, session as S, recipes
from fcskill.contracts import Evidence, aggregate

def resolved(shape,name='fixture',frame='world'):
    return F.Resolved(shape=shape,occurrence={'path':name},source={'fixture':name},
                      frame=frame,transform=list(A.Matrix().A),status='RESOLVED')

class NativeTests(unittest.TestCase):
    def setUp(self):
        self.d=A.newDocument('NativeTest')
        self.frame=F.Frame('world',A.Matrix())
        self.tmp=tempfile.TemporaryDirectory(prefix='fcskill-test-')

    def tearDown(self):
        if self.d.Name in A.listDocuments(): A.closeDocument(self.d.Name)
        self.tmp.cleanup()

    def nested(self):
        r=self.d.addObject('App::Part','Root')
        r.Placement=A.Placement(A.Vector(100,20,0),A.Rotation(A.Vector(0,0,1),90))
        p=self.d.addObject('App::Part','Nested'); r.addObject(p); p.Placement.Base=A.Vector(3,0,0)
        b=self.d.addObject('Part::Feature','Asymmetric'); p.addObject(b); b.Shape=Part.makeBox(2,3,4)
        b.Placement.Base=A.Vector(1,2,0); self.d.recompute()
        return r,b

    def assertBox(self,s,expected):
        for a,b in zip(G.bounds(s),expected): self.assertAlmostEqual(a,b,places=6)

    def test_nested_independent_anchor(self):
        r,b=self.nested(); x=F.shape_in_frame(r,'Nested.Asymmetric.',self.frame)
        self.assertEqual(x.status,'RESOLVED',x.diagnostics)
        self.assertBox(x.shape,[95,24,0,98,26,4])
        self.assertAlmostEqual(x.transform[3],98); self.assertAlmostEqual(x.transform[7],24)
        self.assertEqual(F.shape_in_frame(b,'',self.frame).status,'UNVERIFIED')

    def test_nonorigin_rotation_and_target_frame(self):
        o=self.d.addObject('Part::Feature','Offset'); o.Shape=Part.makeBox(2,3,4)
        o.Placement=A.Placement(A.Vector(5,7,0),A.Rotation(A.Vector(0,0,1),90),A.Vector(2,0,0))
        self.d.recompute()
        m=A.Matrix(); m.move(A.Vector(-5,-7,0))
        x=F.shape_in_frame(o,'',F.Frame('local',m))
        self.assertEqual(x.status,'RESOLVED',x.diagnostics)
        self.assertBox(x.shape,[-1,-2,0,2,0,4])

    def test_baked_transform_applied_once(self):
        o=self.d.addObject('Part::Feature','Baked'); s=Part.makeBox(2,3,4)
        m=A.Matrix(); m.move(A.Vector(10,0,0)); o.Shape=s.transformGeometry(m)
        o.Placement.Base=A.Vector(5,0,0); self.d.recompute()
        x=F.shape_in_frame(o,'',self.frame); self.assertBox(x.shape,[15,0,0,17,3,4])

    def test_transform_semantics(self):
        s=Part.makeBox(1,2,3); m=A.Matrix(); m.move(A.Vector(10,0,0))
        new=s.transformGeometry(m)
        self.assertBox(s,[0,0,0,1,2,3]); self.assertBox(new,[10,0,0,11,2,3])
        returned=s.transformShape(m,False)
        self.assertBox(s,[10,0,0,11,2,3]); self.assertBox(returned,[10,0,0,11,2,3])

    def test_repeated_links_and_source_identity(self):
        r=self.d.addObject('App::Part','Root'); source=self.d.addObject('Part::Feature','Bolt')
        source.Shape=Part.makeBox(2,3,4)
        for i,x in enumerate([10,20]):
            link=self.d.addObject('App::Link','Link'+str(i)); link.setLink(source); r.addObject(link)
            link.Placement.Base=A.Vector(x,0,0)
        self.d.recompute()
        self.assertEqual(F.occurrence_paths(r),['Link0.','Link1.'])
        rows=[F.shape_in_frame(r,p,self.frame) for p in F.occurrence_paths(r)]
        for x,row in zip([10,20],rows):
            self.assertEqual(row.status,'RESOLVED',row.diagnostics)
            self.assertBox(row.shape,[x,0,0,x+2,3,4])
        self.assertEqual(rows[0].source,rows[1].source)
        self.assertNotEqual(rows[0].occurrence,rows[1].occurrence)

    def test_link_to_nested_container(self):
        source=self.d.addObject('App::Part','Source')
        nested=self.d.addObject('App::Part','Inner'); source.addObject(nested); nested.Placement.Base=A.Vector(3,0,0)
        b=self.d.addObject('Part::Feature','Solid'); nested.addObject(b); b.Shape=Part.makeBox(2,3,4)
        link=self.d.addObject('App::Link','Installed'); link.setLink(source); link.Placement.Base=A.Vector(10,0,0)
        self.d.recompute()
        self.assertEqual(F.occurrence_paths(link),['Inner.Solid.'])
        x=F.shape_in_frame(link,'Inner.Solid.',self.frame)
        self.assertEqual(x.status,'RESOLVED',x.diagnostics); self.assertBox(x.shape,[13,0,0,15,3,4])

    def test_body_tip_not_historical_features(self):
        r=self.d.addObject('App::Part','Root'); r.Placement.Base=A.Vector(100,0,0)
        body=self.d.addObject('PartDesign::Body','Body'); r.addObject(body); body.Placement.Base=A.Vector(4,0,0)
        tip=body.newObject('PartDesign::Feature','Tip'); tip.Shape=Part.makeBox(1,2,3); self.d.recompute()
        self.assertEqual(F.occurrence_paths(r),['Body.'])
        x=F.shape_in_frame(r,'Body.',self.frame); self.assertBox(x.shape,[104,0,0,105,2,3])

    def test_missing_mirror_scale_and_units(self):
        r,b=self.nested()
        self.assertEqual(F.shape_in_frame(r,'Missing.',self.frame).status,'UNVERIFIED')
        for scale in [-1,2]:
            m=A.Matrix(); m.A11=scale
            self.assertEqual(F.shape_in_frame(r,'Nested.Asymmetric.',F.Frame('bad',m)).status,'UNVERIFIED')
        self.assertEqual(F.shape_in_frame(r,'',F.Frame('inch',A.Matrix(),'inch')).status,'UNVERIFIED')
        source=self.d.addObject('Part::Feature','SourceScale'); source.Shape=Part.makeBox(1,2,3)
        link=self.d.addObject('App::Link','Scaled'); link.setLink(source); link.Scale=2; self.d.recompute()
        self.assertEqual(F.shape_in_frame(link,'',self.frame).status,'UNVERIFIED')

    def test_operation_local_reuse_defensive_copy(self):
        r,b=self.nested(); scope=F.ResolutionScope()
        scope.resolve(r,'Nested.Asymmetric.',self.frame); scope.resolve(r,'Nested.Asymmetric.',self.frame)
        self.assertEqual(scope.native_calls,2) # Unsaved source freshness is unknown.
        if not A.GuiUp: return
        task=S.OwnedDocument(self.d); task.save_new(Path(self.tmp.name)/'snapshot.FCStd')
        scope=F.ResolutionScope()
        a=scope.resolve(r,'Nested.Asymmetric.',self.frame); a.shape.translate(A.Vector(20,0,0))
        z=scope.resolve(r,'Nested.Asymmetric.',self.frame)
        self.assertBox(z.shape,[95,24,0,98,26,4]); self.assertEqual(scope.native_calls,1)
        b.Placement.Base=A.Vector(2,2,0); self.d.recompute()
        changed=scope.resolve(r,'Nested.Asymmetric.',self.frame)
        self.assertEqual(scope.native_calls,2); self.assertBox(changed.shape,[95,25,0,98,27,4])

    def test_containment_touch_and_separation(self):
        a=resolved(Part.makeBox(10,10,10),'outer'); b=resolved(Part.makeBox(1,1,1,A.Vector(2,2,2)),'inner')
        e=G.pair_measure(a,b,1e-6,1e-5,requirement='clear',minimum_clearance=0)
        self.assertEqual(e.status,'FAIL'); self.assertAlmostEqual(e.value['intersection_mm3'],1)
        b=resolved(Part.makeBox(2,2,2,A.Vector(12,0,0)),'separated')
        e=G.pair_measure(a,b,1e-6,1e-5,requirement='clear',minimum_clearance=1)
        self.assertEqual(e.status,'PASS'); self.assertAlmostEqual(e.value['minimum_distance_mm'],2)
        b=resolved(Part.makeBox(2,2,2,A.Vector(10,0,0)),'touch')
        self.assertEqual(G.pair_measure(a,b,1e-6,1e-5,requirement='clear',minimum_clearance=0).status,'FAIL')
        self.assertEqual(G.pair_measure(a,b,1e-6,1e-5,requirement='mate',intended_contact=True).status,'PASS')
        self.assertEqual(G.equivalent_solids(a,b,1e-6,1e-5,'equivalence').status,'FAIL')

    def test_ambiguity_kernel_failure_and_bounds(self):
        a=resolved(Part.makeBox(1,1,1)); b=resolved(Part.makeBox(1,1,1,A.Vector(3,0,0)))
        e=G.pair_measure(a,b,1e-6,1e-5,requirement='clear',minimum_clearance=2)
        self.assertEqual(e.status,'UNVERIFIED')
        bound=G.bounding_separation(a,b,0.1); self.assertAlmostEqual(bound.value['separation_lower_bound_mm'],1.8)
        class Broken:
            Solids=[1]
            def isNull(self): return False
            def isValid(self): return True
            def common(self,other): raise RuntimeError('injected kernel failure')
        a.shape=Broken()
        e=G.pair_measure(a,b,1e-6,1e-5,requirement='clear',minimum_clearance=0)
        self.assertEqual(e.status,'UNVERIFIED'); self.assertIsNone(e.value)
        self.assertTrue(any('injected kernel failure' in s for s in e.diagnostics))
        self.assertEqual(G.pair_measure(F.Resolved(),b,1e-6,1e-5).status,'UNVERIFIED')

    def test_invalid_source_and_frame_mismatch(self):
        a=resolved(Part.Shape(),'null'); b=resolved(Part.makeBox(1,2,3),'valid')
        self.assertEqual(G.pair_measure(a,b,1e-6,1e-5).status,'UNVERIFIED')
        a=resolved(Part.makeBox(1,2,3),'different-frame','other')
        self.assertEqual(G.pair_measure(a,b,1e-6,1e-5).status,'UNVERIFIED')
        a.frame=b.frame; a.target_from_world=list(A.Matrix().A)
        self.assertEqual(G.pair_measure(a,b,1e-6,1e-5).status,'UNVERIFIED')

    def test_wrong_face_and_degenerate_datums(self):
        points=[A.Vector(0,0,0),A.Vector(2,0,0),A.Vector(0,3,1)]
        wrong=A.Rotation(A.Vector(1,0,0),180).toMatrix()
        self.assertEqual(G.datum_residuals(wrong,points,points,1e-6,'face').status,'FAIL')
        line=[A.Vector(x,0,0) for x in (0,1,2)]
        self.assertEqual(G.datum_residuals(A.Matrix(),line,line,1e-6,'datum').status,'UNVERIFIED')

    @unittest.skipUnless(A.GuiUp,'GUI thread enforcement requires GUI process')
    def test_background_document_writer_rejected(self):
        import threading
        errors=[]
        def attempt():
            try:
                with S.writer(): pass
            except RuntimeError as exc: errors.append(str(exc))
        t=threading.Thread(target=attempt); t.start(); t.join(2)
        self.assertEqual(len(errors),1); self.assertIn('GUI thread',errors[0])

    def test_archive_checksum_and_partial_operation(self):
        import zipfile
        path=Path(self.tmp.name)/'invalid.FCStd'
        with zipfile.ZipFile(path,'w') as z: z.writestr('NotDocument.txt','fixture')
        with self.assertRaises(ValueError): S.preflight(path)
        with self.assertRaises(ValueError): S.preflight(path,'0'*64)
        op=S.Operation(self.tmp.name,'doc','input','not-yet-complete')
        op.run(lambda:None,lambda:False)
        self.assertEqual(json.loads(op.path.read_text())['state'],'UNRESOLVED')

    def test_narrow_opening_region(self):
        material=resolved(Part.makeBox(.01,1,1,A.Vector(.49,0,0)),'thin-obstruction')
        empty=resolved(Part.makeBox(1,1,1),'required-opening')
        e=G.empty_volume(material,empty,1e-6,'full-opening')
        self.assertEqual(e.status,'FAIL'); self.assertAlmostEqual(e.value['occupied_mm3'],.01)

    def test_independent_anchor_catches_common_wrong_transform(self):
        src=[A.Vector(0,0,0),A.Vector(2,0,0),A.Vector(0,3,1)]
        m=A.Matrix(); m.move(A.Vector(100,0,0))
        self.assertEqual(G.datum_residuals(m,src,src,1e-6,'registration').status,'FAIL')
        self.assertEqual(G.datum_residuals(A.Matrix(),src,src,1e-6,'registration').status,'PASS')

    def test_source_preflight_and_operation_recovery(self):
        tmp=Path(self.tmp.name)
        pointer=tmp/'x.step'; pointer.write_text('version https://git-lfs.github.com/spec/v1\n')
        with self.assertRaises(ValueError): S.preflight(pointer)
        with self.assertRaises(ValueError): S.outside_tree(tmp/'child',tmp)
        op=S.Operation(tmp,'task-doc','input-sha','output-path')
        self.assertEqual(S.recover_operation(op.path,lambda r:None)['state'],'UNRESOLVED')
        self.assertFalse(S.recover_operation(op.path,lambda r:False)['retry_safe'])
        self.assertEqual(S.recover_operation(op.path,lambda r:True)['state'],'COMPLETED')
        self.assertEqual(S.recover_operation(op.path,lambda r:True,True)['state'],'RUNNING')
        with self.assertRaises(FileExistsError): S.Operation(tmp,'x','y','z',op.id)
        op.run(lambda:None,lambda:True)
        self.assertEqual(json.loads(op.path.read_text())['state'],'COMPLETED')
        with self.assertRaises(RuntimeError): op.run(lambda:None,lambda:True)
        op2=S.Operation(tmp,'task-doc','input','output')
        with self.assertRaises(RuntimeError): op2.run(lambda:(_ for _ in ()).throw(RuntimeError('partial write')),lambda:False)
        self.assertEqual(json.loads(op2.path.read_text())['state'],'UNRESOLVED')

    def test_no_duplicate_or_missing_coverage(self):
        e=Evidence('fixture',[],'world','mm',{},status='PASS',requirement='one')
        self.assertEqual(aggregate([e],['one']),'PASS')
        self.assertEqual(aggregate([e],['one','two']),'UNVERIFIED')
        self.assertEqual(aggregate([e,e],['one']),'UNVERIFIED')
        with self.assertRaises(ValueError): Evidence('x',[],'w','mm',{},status='PASS').record()

    def test_mounting_plate_meaningful_parameter(self):
        body,tip=recipes.mounting_plate(self.d)
        for value,radius in [(4,2),(6,3),(4,2)]:
            body.HoleDiameter=value; self.d.recompute()
            self.assertTrue(tip.Shape.isValid()); self.assertEqual(len(tip.Shape.Solids),1)
            cylinders=[f.Surface for f in tip.Shape.Faces if isinstance(f.Surface,Part.Cylinder)]
            self.assertEqual(len(cylinders),4)
            self.assertTrue(all(abs(c.Radius-radius)<1e-6 for c in cylinders))
            self.assertEqual(self.d.HolePattern.FullyConstrained,True)
            self.assertEqual(self.d.PlateProfile.FullyConstrained,True)

    def test_bracket_datum_attachment_and_restore(self):
        body,base,plane,tip=recipes.bracket(self.d)
        for h in [4,6,4]:
            base.Height=h; self.d.recompute()
            self.assertTrue(tip.Shape.isValid()); self.assertEqual(len(tip.Shape.Solids),1)
            self.assertAlmostEqual(tip.Shape.BoundBox.ZMax,h+16)
            self.assertAlmostEqual(plane.Placement.Base.z,h)

    def test_enclosure_opening_and_wall_edit(self):
        body,tip=recipes.enclosure(self.d)
        for wall in [3,4,3]:
            body.Wall=wall; self.d.recompute()
            self.assertTrue(tip.Shape.isValid()); self.assertEqual(len(tip.Shape.Solids),1)
            self.assertAlmostEqual(tip.Shape.Volume,30*24*15-(30-2*wall)*(24-2*wall)*(15-wall),places=5)

    def test_step_occurrence_export_and_missing_part(self):
        from fcskill.exports import export_step
        a=resolved(Part.makeBox(2,3,4),'one')
        b=resolved(Part.makeBox(2,3,4,A.Vector(10,0,0)),'two')
        path=Path(self.tmp.name)/'two.step'
        report=export_step([a,b],path,1e-6,1e-5)
        self.assertEqual(report['status'],'PASS'); self.assertEqual(report['occurrences_matched'],2)
        self.assertEqual(len(Part.read(str(path)).Solids),2)
        with self.assertRaises(FileExistsError): export_step([a,b],path,1e-6,1e-5)
        with self.assertRaises(ValueError): export_step([a,a],Path(self.tmp.name)/'duplicate.step',1e-6,1e-5)
        missing=resolved(Part.makeCompound([a.shape,b.shape]),'expected-assembly')
        self.assertEqual(G.equivalent_solids(missing,a,1e-6,1e-5,'coverage').status,'FAIL')

    def test_print_frame_stl_and_source_unchanged(self):
        from fcskill.exports import export_stl
        a=resolved(Part.makeBox(2,3,4),'print-source')
        transform=A.Placement(A.Vector(0,4,0),A.Rotation(A.Vector(1,0,0),90)).toMatrix()
        report=export_stl(a,Path(self.tmp.name)/'part.stl',transform,
                          linear_deflection=.05,angular_deflection=.3,relative=False,
                          comparison_tolerance=.01,max_relative_volume_error=.001)
        self.assertEqual(report['status'],'PASS'); self.assertBox(a.shape,[0,0,0,2,3,4])
        self.assertGreater(report['sample_count'],0)

    def test_scaled_export_and_unmatched_geometry_rejected(self):
        source=resolved(Part.makeBox(2,3,4),'source')
        scaled=resolved(Part.makeBox(20,30,40),'wrong-units')
        self.assertEqual(G.equivalent_solids(source,scaled,1e-6,1e-5,'scale').status,'FAIL')

    @unittest.skipUnless(A.GuiUp,'GUI modification-state test requires GUI process')
    def test_save_reopen_preserves_unsaved_sentinel(self):
        import FreeCADGui as Gui
        sentinel=self.d.addObject('Part::Feature','UserUnsaved'); sentinel.Shape=Part.makeBox(1,2,3)
        self.d.recompute(); initial=S.inventory()
        task=S.OwnedDocument.create('OwnedFixture')
        try:
            body,tip=recipes.mounting_plate(task.doc)
            before=tip.Shape.copy(); path=Path(self.tmp.name)/'owned.FCStd'
            task.save_new(path)
            with self.assertRaises(FileExistsError): task.save_new(path)
            reopened=task.reopen()
            e=G.equivalent_solids(resolved(before),resolved(reopened.MountHoles.Shape),1e-6,1e-5,'reopen')
            self.assertEqual(e.status,'PASS',e.record())
            self.assertEqual([r for r in S.inventory() if r['name']==self.d.Name],
                             [r for r in initial if r['name']==self.d.Name])
            self.assertTrue(Gui.getDocument(self.d.Name).Modified)
        finally: A.closeDocument(task.doc.Name)

if __name__=='__main__': unittest.main()
