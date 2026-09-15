"""Run with FreeCADCmd in a fresh process and isolated -u/-s config paths.

Writes evidence only under the explicitly supplied BLOCKFOLK_TEST_OUTPUT.
Does not connect to, open or modify the user's FreeCAD session.
"""
import hashlib, json, os, sys, traceback
from pathlib import Path
import FreeCAD as App, Part

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
OUT = Path(os.environ['BLOCKFOLK_TEST_OUTPUT']).resolve()
OUT.mkdir(parents=True, exist_ok=True)
with (OUT/'run-claim.json').open('x',encoding='utf-8') as claim:
    json.dump({'pid':os.getpid(),'source_hashes':{
        str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [Path(__file__),*(ROOT/'scripts/blockfolk').glob('*.py')]}},claim,indent=2)
from blockfolk.joints import hinge, rotated
from blockfolk.parameters import Hinge, Process
from blockfolk.validation import capture_shapes, classify_contact

results = []


def check(name, fn):
    try:
        data = fn()
        results.append(dict(name=name, passed=True, evidence=data))
    except Exception:
        results.append(dict(name=name, passed=False, error=traceback.format_exc()))


def evaluate(f):
    capture = capture_shapes(f.parent, f.child, f.witnesses, f.projected_cap, f.opening)
    assert capture['status'] == 'PASS', capture
    for shape in (f.parent, f.child):
        assert shape.isValid() and len(shape.Solids) == 1
    assert f.parent.common(f.child).Volume < 1e-6
    distance = f.parent.distToShape(f.child)[0]
    assert distance > .1, distance
    return dict(capture=capture, neutral_minimum_distance_mm=distance,
                parent_volume_mm3=f.parent.Volume, child_volume_mm3=f.child.Volume)


def moved_capture(f, child, angle):
    witnesses={k:(v if k.startswith('cap_') else rotated(v,f.metadata['center'],[1,0,0],angle))
               for k,v in f.witnesses.items()}
    evidence=capture_shapes(f.parent,child,witnesses,f.projected_cap,f.opening)
    assert evidence['status']=='PASS', (angle,evidence)


def default_free():
    f = hinge(holding=False)
    data = evaluate(f)
    collisions = []
    for angle in range(-180,181,5):
        child = rotated(f.child, f.metadata['center'], [1,0,0], angle)
        volume = f.parent.common(child).Volume
        assert volume < 1e-6, (angle, volume)
        moved_capture(f,child,angle)
        collisions.append(volume)
    data.update(sample_count=len(collisions), angle_step_degrees=5)
    return data


def paired():
    f = hinge()
    data = evaluate(f)
    samples = []
    for angle in range(0,181,5):
        child = rotated(f.child, f.metadata['center'], [1,0,0], angle)
        leaves = rotated(f.leaves, f.metadata['center'], [1,0,0], angle)
        contact = classify_contact(f.parent.common(child), f.cam, leaves)
        assert contact['pass_unintended'], (angle,contact)
        moved_capture(f,child,angle)
        samples.append(dict(angle=angle, **contact))
    assert any(v['intended_mm3'] > .001 for v in samples)
    data.update(samples=samples, angle_step_degrees=5,
                note='Centered rigid contact exists; follower elasticity/offset robustness and slicing not certified for this fixture')
    return data


def missing_cap():
    f = hinge(holding=False)
    # Remove half of one cap, leaving the journal intact and parent connected.
    cut = Part.makeBox(1.3,20,10,App.Vector(-4.5,-5.4,0))
    damaged = f.parent.cut(cut)
    assert damaged.isValid() and len(damaged.Solids)==1
    data = capture_shapes(damaged,f.child,f.witnesses,f.projected_cap,f.opening)
    assert data['status']=='FAIL' and not data['coverage']['cap_left']
    return data


def open_hoop():
    f = hinge(holding=False)
    cut = Part.makeBox(6,10,.8,App.Vector(-3,4.6,-.4))
    damaged = f.child.cut(cut)
    assert damaged.isValid() and len(damaged.Solids)==1
    data = capture_shapes(f.parent,damaged,f.witnesses,f.projected_cap,f.opening)
    assert data['status']=='FAIL' and not data['coverage']['closed_hoop']
    return data


def change_clearance():
    a,b,c = hinge(), hinge(process=Process(clearance=.5)), hinge()
    evaluate(b)
    assert b.child.Volume < a.child.Volume
    assert a.child.cut(c.child).Volume+c.child.cut(a.child).Volume < 1e-7
    return dict(before=a.child.Volume, changed=b.child.Volume, restored=c.child.Volume)


def larger_free():
    s=Hinge(journal_radius=3.2,cap_radius=5.6,cap_thickness=1.6,
            cap_inner_half_span=4,shell_radius=6.8)
    return evaluate(hinge(s,holding=False))


def canted_axis_and_frame():
    from blockfolk.poses import turn,point
    import math
    center=(18.5,4.6,59)
    axis=(math.cos(math.pi/8),0,-math.sin(math.pi/8))
    m=turn(center,axis,170)
    expected=App.Rotation(App.Vector(*axis),170).multVec(App.Vector(1,3,7))+App.Vector(*center)
    actual=point(m,tuple(center[i]+(1,3,7)[i] for i in range(3)))
    assert (App.Vector(*actual)-expected).Length<1e-9
    f=hinge(holding=False)
    def move(shape): return rotated(shape,[0,0,0],[0,1,0],22.5)
    evidence=capture_shapes(move(f.parent),move(f.child),{k:move(v) for k,v in f.witnesses.items()},f.projected_cap,f.opening)
    assert evidence['status']=='PASS'
    return dict(native_vector_error_mm=(App.Vector(*actual)-expected).Length,canted_capture=evidence)


def native_parameter_persistence():
    # The general helper owns the native parameter schema. No alternate proxy.
    sys.path.insert(0, os.environ['FCSKILL_SCRIPTS'])
    import fcskill
    from fcskill.modeling import create_parameters, Parameter
    doc=App.newDocument('BlockfolkDisposableParameters')
    try:
        p=create_parameters(doc,'Parameters',{'Clearance':Parameter(.45,.2,.8)})
        c=doc.addObject('Part::Cylinder','JournalEnvelope')
        c.setExpression('Radius','2.55 mm + Parameters.Clearance')
        c.Height=5.5
        doc.recompute()
        before=c.Shape.Volume
        target=OUT/'parameter_fixture.FCStd'
        doc.saveAs(str(target))
        name=doc.Name
        App.closeDocument(name)
        doc=App.openDocument(str(target))
        assert abs(doc.JournalEnvelope.Shape.Volume-before)<1e-7
        doc.Parameters.Clearance=.5
        doc.recompute()
        changed=doc.JournalEnvelope.Shape.Volume
        assert changed>before
        doc.Parameters.Clearance=.45
        doc.recompute()
        assert abs(doc.JournalEnvelope.Shape.Volume-before)<1e-7
        doc.save()
        return dict(before=before,changed=changed,restored=doc.JournalEnvelope.Shape.Volume,
                    fcskill_capabilities=fcskill.capabilities())
    finally:
        if doc and doc.Name in App.listDocuments():
            App.closeDocument(doc.Name)


for name, fn in [('free_hinge_motion',default_free),('paired_cam_contact',paired),
                 ('half_cap_rejected',missing_cap),('open_hoop_rejected',open_hoop),
                 ('clearance_rebuild',change_clearance),('larger_free_hinge',larger_free),
                 ('canted_axis_and_common_frame',canted_axis_and_frame),
                 ('native_parameter_save_reopen',native_parameter_persistence)]:
    check(name,fn)
report=dict(freecad_version=App.Version(),tests=results,passed=all(r['passed'] for r in results),
            physical_status='UNTESTED fixtures', isolation='Fresh FreeCADCmd; isolated user and system config')
(OUT/'native_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BLOCKFOLK_NATIVE_RESULTS',report['passed'],[(r['name'],r['passed']) for r in results])
