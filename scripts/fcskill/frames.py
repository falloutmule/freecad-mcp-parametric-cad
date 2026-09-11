"""One native occurrence adapter. Column-vector transforms T_target<-source."""
from dataclasses import dataclass, field
import math
from .session import canonical

def matrix_checks(matrix, tolerance=1e-9):
    a = list(matrix.A)
    if not all(math.isfinite(v) for v in a):
        raise ValueError('Nonfinite transform')
    r = [a[i*4:i*4+3] for i in range(3)]
    det = (r[0][0]*(r[1][1]*r[2][2]-r[1][2]*r[2][1])
           -r[0][1]*(r[1][0]*r[2][2]-r[1][2]*r[2][0])
           +r[0][2]*(r[1][0]*r[2][1]-r[1][1]*r[2][0]))
    orth = max(abs(sum(r[k][i]*r[k][j] for k in range(3))-(i==j))
               for i in range(3) for j in range(3))
    last = max(abs(a[12+i]-(i==3)) for i in range(4))
    return {'determinant':det, 'orthogonality_error':orth, 'last_row_error':last,
            'rigid_right_handed':abs(det-1)<=tolerance and orth<=tolerance and last<=tolerance,
            'tolerance':tolerance}

@dataclass
class Frame:
    name: str
    target_from_world: object
    units: str = 'mm'

@dataclass
class Resolved:
    shape: object = None
    occurrence: dict = field(default_factory=dict)
    source: dict = field(default_factory=dict)
    frame: str = ''
    target_from_world: list = field(default_factory=list)
    transform: list = field(default_factory=list)
    diagnostics: list = field(default_factory=list)
    checks: dict = field(default_factory=dict)
    status: str = 'UNVERIFIED'

    def record(self):
        result={k:v for k,v in vars(self).items() if k != 'shape'}
        if self.shape is not None:
            import hashlib
            try:
                result['evaluated_brep_sha256']=hashlib.sha256(self.shape.exportBrepToString().encode('utf8')).hexdigest()
            except Exception:
                result['evaluated_brep_sha256']=None
        return result

def shape_in_frame(root, occurrence_path, target_frame):
    import Part
    result = Resolved(frame=target_frame.name,target_from_world=list(target_frame.target_from_world.A))
    try:
        doc = root.Document
        result.occurrence = {'document':doc.Name, 'file':canonical(doc.FileName) if doc.FileName else None,
                             'root':root.Name, 'path':occurrence_path}
        if target_frame.units != 'mm':
            raise ValueError('Only millimetre frames are supported')
        if occurrence_path and not occurrence_path.endswith('.'):
            raise ValueError('Use complete object occurrence paths ending in a dot, not faces/edges')
        # getShape can bake Link scale into geometry without exposing it in mat.
        for obj in root.getSubObjectList(occurrence_path):
            if obj.isDerivedFrom('App::Link'):
                if getattr(obj, 'ElementCount', 0):
                    raise ValueError('Link arrays unsupported; supply explicit occurrences')
                if abs(float(obj.Scale)-1)>1e-9 or any(abs(v-1)>1e-9 for v in obj.ScaleVector):
                    raise ValueError('Mirrored/scaled Link unsupported')
        # Root must be top level. Calling on a nested object loses parent context.
        if root.getParentGeoFeatureGroup() is not None:
            raise ValueError('Root is nested; pass the top-level occurrence root')
        tc = matrix_checks(target_frame.target_from_world)
        if not tc['rigid_right_handed']:
            raise ValueError('Mirrored/scaled/sheared target frame unsupported')
        shape, matrix, source = Part.getShape(root, occurrence_path, retType=2)
        if source is None or shape.isNull():
            raise ValueError('Occurrence not resolved or empty')
        # Native resolution includes nested objects, links and the top-level root once.
        total = target_frame.target_from_world.multiply(matrix)
        result.checks = matrix_checks(total)
        if not result.checks['rigid_right_handed']:
            raise ValueError('Mirrored/scaled/sheared occurrence unsupported')
        result.source = {'document':source.Document.Name, 'file':canonical(source.Document.FileName) if source.Document.FileName else None,
                         'object':source.Name, 'type':source.TypeId}
        result.transform = list(total.A)
        result.shape = shape.copy()
        # Native output is already in world coordinates. Apply ONLY world->target.
        result.shape.transformShape(target_frame.target_from_world, False)
        if not result.shape.isValid():
            raise ValueError('Invalid resolved BRep')
        result.status = 'RESOLVED'
    except Exception as exc:
        result.shape = None
        result.diagnostics.append(str(exc))
    return result

def occurrence_paths(root):
    """Leaf occurrences for Parts, Bodies and single Links; no visibility filtering.

    Bodies are one evaluated Tip, not every historical feature. Link arrays and
    unknown group semantics are explicitly unsupported rather than omitted.
    """
    result = []
    def walk(obj, path, stack):
        key = (obj.Document.Name, obj.Name)
        if key in stack:
            raise ValueError('Cyclic occurrence hierarchy')
        stack = stack | {key}
        if obj.isDerivedFrom('App::Link'):
            if getattr(obj, 'ElementCount', 0):
                raise ValueError('Link arrays require an explicit occurrence list')
            linked = obj.getLinkedObject()
            if linked is None:
                raise ValueError('Broken link')
            if linked.isDerivedFrom('App::Part'):
                for child in linked.Group:
                    walk(child, path+child.Name+'.', stack | {(linked.Document.Name, linked.Name)})
            else:
                result.append(path)
        elif obj.isDerivedFrom('App::Part'):
            for child in obj.Group:
                walk(child, path+child.Name+'.', stack)
        elif obj.isDerivedFrom('PartDesign::Body') or hasattr(obj, 'Shape'):
            result.append(path)
        elif hasattr(obj, 'Group'):
            raise ValueError('Unknown group semantics; supply explicit occurrence paths')
        else:
            raise ValueError('Nonshape child requires explicit scope exclusion: '+path)
    walk(root, '', set())
    return result

class ResolutionScope:
    """Deduplicate within one read-only operation; discard before any mutation."""
    def __init__(self):
        self._cache = {}
        self.native_calls = 0

    def resolve(self, root, path, frame):
        from pathlib import Path
        from .session import inventory
        row=next(r for r in inventory() if r['name']==root.Document.Name)
        # Never reuse when document freshness is unknown (including headless/unsaved).
        fresh=bool(row['path'] and row['modified'] is False)
        if not fresh:
            self._cache.clear()
            self.native_calls+=1
            return shape_in_frame(root,path,frame)
        stat=Path(row['path']).stat()
        key = (id(root), path, frame.name, frame.units, tuple(frame.target_from_world.A),stat.st_mtime_ns,stat.st_size)
        if key not in self._cache:
            self._cache[key] = shape_in_frame(root, path, frame)
            self.native_calls += 1
        value = self._cache[key]
        # No cached wrapper may escape for mutation.
        import copy
        result = Resolved(**{k:copy.deepcopy(v) for k,v in vars(value).items() if k!='shape'})
        result.shape = value.shape.copy() if value.shape is not None else None
        return result
