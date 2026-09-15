import hashlib,json,math,sys,unittest,zipfile
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from blockfolk.parameters import Design,Process,Hinge,Proportions,envelope_fits
from blockfolk.poses import Joint,transforms,turn,point,semantic_checks
from blockfolk.validation import REQUIRED,retention_decision,joint_claims,mass_sanity


class ParametersTests(unittest.TestCase):
    def test_height_scaling_keeps_manufacturing_and_mechanism(self):
        source=Design()
        for h in (60,150):
            scaled=source.resize_character(h)
            self.assertEqual(scaled.process,source.process)
            self.assertEqual(scaled.mechanism,source.mechanism)
            self.assertEqual(scaled.process.clearance,.45)
            self.assertAlmostEqual(scaled.proportions.dimensions()['head_width'],h*.34)

    def test_json_round_trip(self):
        d=Design(Proportions(height=80,head_width_ratio=.38),Hinge(),Process(clearance=.5))
        self.assertEqual(d,Design.loads(d.dumps()))

    def test_invalid_process_rejected(self):
        for v in (0,-.1,float('nan'),float('inf'),True):
            with self.assertRaises(ValueError): Process(clearance=v)

    def test_invalid_proportion_rejected(self):
        with self.assertRaises(ValueError): Proportions(head_width_ratio=1.2)

    def test_infeasible_mechanism_rejected(self):
        for s in (replace(Hinge(),cap_inner_half_span=1),replace(Hinge(),leaf_width=4),replace(Hinge(),tooth_radius=3)):
            with self.assertRaises(ValueError): s.derived(Process())

    def test_schema_is_strict(self):
        d=json.loads(Design().dumps())
        d['unexpected']=3
        with self.assertRaises(ValueError): Design.loads(json.dumps(d))

    def test_small_figure_needs_envelope_decision(self):
        d=Design().resize_character(60)
        self.assertFalse(envelope_fits(d.proportions.dimensions()['upper_arm'],4.6,4.6,1.2))
        self.assertTrue(envelope_fits(14.5,4.6,4.6,1.2))


class PoseTests(unittest.TestCase):
    def assertPoint(self,a,b):
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=9)

    def test_rotation_keeps_pivot_and_axis(self):
        t=turn((2,3,4),(1,0,0),90)
        self.assertPoint(point(t,(2,3,4)),(2,3,4))
        self.assertPoint(point(t,(6,3,4)),(6,3,4))
        self.assertPoint(point(t,(2,4,4)),(2,3,5))

    def test_semantic_sitting_from_real_joint_chain(self):
        joints=[]
        landmarks={}
        for side,x in [('L',7),('R',-7)]:
            joints += [Joint('hip'+side,'Torso','Thigh'+side,(x,4.6,33.5),(1,0,0),(0,90)),
                       Joint('knee'+side,'Thigh'+side,'Shin'+side,(x,4.6,17.5),(1,0,0),(-90,0))]
        m=transforms(joints,{'hipL':90,'hipR':90,'kneeL':-90,'kneeR':-90})
        for side,x in [('L',7),('R',-7)]:
            landmarks['hip'+side]=(x,4.6,33.5)
            landmarks['knee'+side]=point(m['Thigh'+side],(x,4.6,17.5))
            landmarks['ankle'+side]=point(m['Shin'+side],(x,4.6,2))
        self.assertTrue(semantic_checks('sitting',landmarks,100)['landmark_checks_pass'])
        self.assertAlmostEqual(landmarks['kneeR'][1],20.6)
        self.assertAlmostEqual(landmarks['ankleR'][2],18)

    def test_standing_does_not_pass_as_sitting(self):
        lm={k+s:(x,4.6,z) for s,x in [('L',7),('R',-7)] for k,z in [('hip',33.5),('knee',17.5),('ankle',2)]}
        lm['headTop']=(0,12,100)
        self.assertFalse(semantic_checks('sitting',lm,100)['landmark_checks_pass'])
        self.assertTrue(semantic_checks('standing',lm,100)['landmark_checks_pass'])

    def test_canted_raised_arm_is_above_shoulder(self):
        center=(-18.5,4.6,59)
        hand=point(turn(center,(math.cos(math.pi/8),0,math.sin(math.pi/8)),170),(-20.2,4.6,31))
        result=semantic_checks('raised_arm',dict(handR=hand,shoulderR=center),100)
        self.assertTrue(result['landmark_checks_pass'])
        self.assertTrue(result['visual_review_required'])
        self.assertEqual(result['collision_status'],'UNVERIFIED')

    def test_zero_axis_rejected(self):
        with self.assertRaises(ValueError): turn((0,0,0),(0,0,0),90)

    def test_graph_cycle_rejected(self):
        with self.assertRaises(ValueError): transforms([Joint('x','B','A',(0,0,0),(1,0,0),(0,90)),Joint('y','A','B',(0,0,0),(1,0,0),(0,90))],{})

    def test_unknown_angle_and_limits_rejected(self):
        joints=[Joint('x','Torso','Arm',(0,0,0),(1,0,0),(0,90))]
        for angles in ({'wrong':2},{'x':100}):
            with self.assertRaises(ValueError): transforms(joints,angles)


class ClaimTests(unittest.TestCase):
    def test_one_push_cannot_prove_retention(self):
        self.assertEqual(retention_decision({'axial_push_blocked':True},8.8,8.6),'UNVERIFIED')

    def test_open_ring_fails_even_with_good_projection(self):
        coverage={k:True for k in REQUIRED}
        coverage['closed_hoop']=False
        self.assertEqual(retention_decision(coverage,8.8,8.6),'FAIL')

    def test_undersized_cap_fails(self):
        self.assertEqual(retention_decision({k:True for k in REQUIRED},8,8.6),'FAIL')

    def test_holding_and_retention_are_separate(self):
        self.assertEqual(joint_claims('PASS','PASS')['requested_claims'],'UNVERIFIED')
        self.assertEqual(joint_claims('PASS','UNVERIFIED','PASS')['requested_claims'],'UNVERIFIED')
        free=joint_claims('PASS','PASS','NOT_REQUESTED',holding_required=False)
        self.assertEqual(free['requested_claims'],'PASS')
        self.assertEqual(free['pose_holding'],'NOT_REQUESTED')

    def test_absurd_mass_rejected(self):
        self.assertFalse(mass_sanity(54765,397)['plausible_upper_bound'])
        self.assertTrue(mass_sanity(54765,35.94)['plausible_upper_bound'])


class ReferenceTests(unittest.TestCase):
    path=ROOT/'examples/physically-validated-100mm'

    def test_reference_metadata(self):
        record=json.loads((self.path/'physical-test.json').read_text())
        self.assertEqual(record['physical_print_count_reported'],1)
        self.assertTrue(all(record[k] for k in ('released','retained','pose_holding')))
        self.assertIn('holding torque',record['unmeasured'])
        self.assertIsNone(record['height_measured_mm'])

    def test_nominal_defaults_are_not_hard_limits(self):
        summary=json.loads((self.path/'parameter-summary.json').read_text())
        self.assertEqual(len(summary['native_parameters']),21)
        self.assertEqual(summary['native_parameters']['Clearance']['nominal_value'],.45)
        self.assertEqual(summary['numeric_hard_limits'],[])
        self.assertFalse(summary['slicer_estimates']['physically_measured'])

    def test_sample_round_trip(self):
        sample=Design.loads((self.path/'sample-design-parameters.json').read_text())
        self.assertEqual(Design.loads(sample.dumps()),sample)

    def test_preserved_archive_and_photos(self):
        provenance=json.loads((self.path/'provenance.json').read_text())
        # Public packaging preserves provenance, not private photographs/CAD/logs.
        self.assertEqual(provenance['publication']['distribution'],'sanitized-public-metadata')
        self.assertFalse(provenance['publication']['private_artifacts_included'])
        for artifact in [provenance['preserved_archive'],*provenance['photos']]:
            self.assertFalse(artifact['included'])
            self.assertEqual(len(artifact['sha256']),64)
            int(artifact['sha256'],16)
            self.assertFalse((self.path/artifact['path']).exists())
        self.assertNotIn('source_path',json.dumps(provenance))



if __name__=='__main__': unittest.main()
