"""Explicit evidence on resolved operands; no invented contact intent or tolerances."""
import math
from .contracts import Evidence, positive

def bounds(shape):
    b=shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]

def _operands(a,b,method,tolerances,units='mm'):
    e=Evidence(method,[a.record(),b.record()],a.frame,units,tolerances)
    if a.status!='RESOLVED' or b.status!='RESOLVED' or a.frame!=b.frame or a.target_from_world!=b.target_from_world:
        raise ValueError('Operands must be valid, resolved and in the same declared frame')
    if any(x.shape is None or x.shape.isNull() or not x.shape.isValid() for x in (a,b)):
        raise ValueError('Operand geometry is null or invalid at measurement time')
    return e

def pair_measure(a,b,length_tolerance,volume_tolerance,*,requirement=None,
                 minimum_clearance=None,intended_contact=False):
    """Measure pair; judge only a caller-declared clearance or contact requirement."""
    positive(length_tolerance,'length tolerance'); positive(volume_tolerance,'volume tolerance')
    if minimum_clearance is not None:
        positive(minimum_clearance,'minimum clearance',allow_zero=True)
    e=Evidence('OCCT common volume + minimum distance',[a.record(),b.record()],a.frame,'mm;mm^3',
               {'length_mm':length_tolerance,'volume_mm3':volume_tolerance},requirement=requirement)
    try:
        _operands(a,b,e.method,e.tolerance)
        if not a.shape.Solids or not b.shape.Solids:
            raise ValueError('Solid material intersection requires solid operands')
        common=a.shape.common(b.shape)
        if not common.isNull() and not common.isValid():
            raise ValueError('Invalid Boolean result')
        overlap=0.0 if common.isNull() else common.Volume
        distance=a.shape.distToShape(b.shape)[0]
        if not all(math.isfinite(v) and v>=0 for v in (overlap,distance)):
            raise ValueError('Invalid measurement')
        relation=('INTERFERENCE' if overlap>volume_tolerance else
                  'CONTACT_WITHIN_TOLERANCE' if distance<=length_tolerance else 'SEPARATED')
        e.value={'intersection_mm3':overlap,'minimum_distance_mm':distance,'relation':relation}
        e.status='MEASURED'
        if requirement:
            if minimum_clearance is None and not intended_contact:
                raise ValueError('Declare clearance or intended contact to judge a pair')
            if intended_contact and minimum_clearance not in (None,0):
                raise ValueError('Contact and positive clearance requirements conflict')
            if overlap>volume_tolerance:
                e.status='FAIL'
            elif intended_contact:
                e.status='PASS' if relation=='CONTACT_WITHIN_TOLERANCE' else 'FAIL'
                e.unchecked.append('Contact footprint/normal/area not checked; only pair touching and no material overlap')
            elif distance<=length_tolerance and minimum_clearance==0:
                e.status='FAIL'; e.diagnostics.append('Unexpected contact; no mating intent was declared')
            elif distance-length_tolerance>=minimum_clearance:
                e.status='PASS'
            elif distance+length_tolerance<minimum_clearance:
                e.status='FAIL'
            else:
                e.status='UNVERIFIED'; e.diagnostics.append('Threshold lies within measurement tolerance')
    except Exception as exc:
        e.status='UNVERIFIED'; e.diagnostics.append(str(exc))
    return e

def bounding_separation(a,b,padding_mm):
    positive(padding_mm,'box padding',allow_zero=True)
    e=Evidence('expanded axis-aligned bounding-box distance',[a.record(),b.record()],a.frame,'mm',
               {'padding_per_operand_mm':padding_mm},coverage='CONSERVATIVE_BOUND')
    try:
        _operands(a,b,e.method,e.tolerance)
        aa,bb=bounds(a.shape),bounds(b.shape)
        gaps=[max(0,aa[i]-bb[i+3]-2*padding_mm,bb[i]-aa[i+3]-2*padding_mm) for i in range(3)]
        e.value={'separation_lower_bound_mm':math.sqrt(sum(x*x for x in gaps))}
        e.status='MEASURED'
        e.unchecked=['Not an exact minimum distance; overlapping boxes prove no intersection result']
    except Exception as exc: e.diagnostics.append(str(exc))
    return e

def empty_volume(material,keepout,volume_tolerance,requirement):
    """Full solid-volume intersection, not cylindrical-face or sparse-sample proxy."""
    positive(volume_tolerance,'volume tolerance')
    e=Evidence('required empty volume intersection',[material.record(),keepout.record()],material.frame,
               'mm^3',{'volume_mm3':volume_tolerance},requirement=requirement)
    try:
        _operands(material,keepout,e.method,e.tolerance)
        if not material.shape.Solids or not keepout.shape.Solids:
            raise ValueError('Solid operands required')
        c=material.shape.common(keepout.shape)
        if not c.isNull() and not c.isValid(): raise ValueError('Invalid Boolean')
        v=0.0 if c.isNull() else c.Volume
        if not math.isfinite(v) or v<0: raise ValueError('Invalid volume')
        e.value={'occupied_mm3':v}
        e.status='PASS' if v<=volume_tolerance else 'FAIL'
        e.unchecked=['Sub-tolerance occupied material; fastening strength; printability']
    except Exception as exc: e.diagnostics.append(str(exc))
    return e

def equivalent_solids(a,b,length_tolerance,volume_tolerance,requirement):
    """Solid equivalence metric, not face-number or minimum-distance equality."""
    positive(length_tolerance,'length tolerance'); positive(volume_tolerance,'volume tolerance')
    e=Evidence('symmetric difference + bbox + solid count',[a.record(),b.record()],a.frame,'mm;mm^3',
               {'length_mm':length_tolerance,'volume_mm3':volume_tolerance},requirement=requirement)
    try:
        _operands(a,b,e.method,e.tolerance)
        if not a.shape.Solids or not b.shape.Solids: raise ValueError('Solid comparison only')
        diffs=[a.shape.cut(b.shape),b.shape.cut(a.shape)]
        if any(not d.isNull() and not d.isValid() for d in diffs): raise ValueError('Invalid difference')
        volume=sum(0 if d.isNull() else d.Volume for d in diffs)
        deviation=max(abs(x-y) for x,y in zip(bounds(a.shape),bounds(b.shape)))
        if not all(math.isfinite(v) for v in (volume,deviation)): raise ValueError('Nonfinite metric')
        same_count=len(a.shape.Solids)==len(b.shape.Solids)
        e.value={'symmetric_difference_mm3':volume,'bbox_max_delta_mm':deviation,
                 'solid_counts':[len(a.shape.Solids),len(b.shape.Solids)]}
        e.status='PASS' if volume<=volume_tolerance and deviation<=length_tolerance and same_count else 'FAIL'
        e.unchecked=['Caller must also check design-specific axes, dimensions and interfaces']
    except Exception as exc: e.diagnostics.append(str(exc))
    return e

def datum_residuals(transform,source_points,target_points,tolerance,requirement):
    """Independent holdout anchors supplied by caller, not fitted here."""
    from .frames import matrix_checks
    positive(tolerance,'datum tolerance')
    e=Evidence('independent datum residuals',[], 'caller-declared source->target','mm',
               {'length_mm':tolerance},requirement=requirement)
    try:
        if not matrix_checks(transform)['rigid_right_handed']: raise ValueError('Non-rigid registration')
        if len(source_points)!=len(target_points) or len(source_points)<3: raise ValueError('At least three matched independent anchors required')
        for points in (source_points,target_points):
            if not any((points[i]-points[0]).cross(points[j]-points[0]).Length>tolerance*tolerance
                       for i in range(1,len(points)) for j in range(i+1,len(points))):
                raise ValueError('Degenerate/collinear datum anchors')
        deltas=[(transform.multVec(s)-t).Length for s,t in zip(source_points,target_points)]
        e.value={'residuals_mm':deltas,'source_points':[list(p) for p in source_points],
                 'target_points':[list(p) for p in target_points],'transform':list(transform.A)}
        e.status='PASS' if max(deltas)<=tolerance else 'FAIL'
        e.unchecked=['Caller must establish provenance, independence and non-degenerate datum selection']
    except Exception as exc: e.diagnostics.append(str(exc))
    return e
