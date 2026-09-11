"""Explicit single-solid occurrence STEP export and print-frame STL checks."""
import json
from pathlib import Path
from .contracts import file_hash, positive
from .frames import Resolved, matrix_checks
from .geometry import bounds, equivalent_solids
from .session import OwnedDocument, preflight, writer

def _shape_operand(shape, identity, frame, target_from_world):
    return Resolved(shape=shape,occurrence=identity,source=identity,frame=frame,
                    target_from_world=target_from_world,status='RESOLVED')

def export_step(occurrences,path,length_tolerance,volume_tolerance):
    import FreeCAD as A
    import Part
    positive(length_tolerance,'length tolerance'); positive(volume_tolerance,'volume tolerance')
    target=Path(path).resolve()
    if target.exists(): raise FileExistsError(target)
    if not occurrences: raise ValueError('No occurrences requested')
    if any(x.status!='RESOLVED' or len(x.shape.Solids)!=1 for x in occurrences):
        raise ValueError('This exporter supports resolved single-solid occurrences only')
    if len({(x.frame,tuple(x.target_from_world)) for x in occurrences})!=1: raise ValueError('Export operands must share one frame')
    ids=[json.dumps(x.occurrence,sort_keys=True) for x in occurrences]
    if len(set(ids))!=len(ids): raise ValueError('Duplicate occurrence identity')
    target.parent.mkdir(parents=True,exist_ok=True)
    owned=OwnedDocument.create('StepExportStaging')
    try:
        with writer():
            objects=[]
            for i,x in enumerate(occurrences):
                obj=owned.doc.addObject('Part::Feature',f'Occurrence_{i:04d}')
                obj.Shape=x.shape.copy(); objects.append(obj)
            owned.doc.recompute()
            Part.export(objects,str(target))
        integrity=preflight(target)
        # Read delivered bytes, not a live in-memory export shape.
        shape=Part.read(str(target))
        if shape.isNull() or not shape.isValid(): raise RuntimeError('Invalid STEP reimport')
        unmatched=list(enumerate(shape.Solids)); evidence=[]
        for x in occurrences:
            selected=None
            for i,s in unmatched:
                candidate=_shape_operand(s,{'STEP':integrity['sha256'],'solid_index':i},x.frame,x.target_from_world)
                e=equivalent_solids(x,candidate,length_tolerance,volume_tolerance,'exported-occurrence-equivalence')
                if e.status=='PASS': selected=(i,s,e); break
            if selected is None:
                raise RuntimeError('STEP occurrence coverage/equivalence not established')
            unmatched=[item for item in unmatched if item[0]!=selected[0]]
            evidence.append(selected[2].record())
        if unmatched: raise RuntimeError('STEP contains extra solid occurrences')
        return {'integrity':integrity,'engineering':evidence,'occurrences_requested':len(occurrences),
                'occurrences_matched':len(evidence),'status':'PASS',
                'scope':'single-solid occurrence geometry/count; source identity retained in this manifest, not STEP names',
                'unchecked':['Design-specific interfaces must be checked by caller','No face-number identity guarantee']}
    finally:
        A.closeDocument(owned.doc.Name)

def export_stl(operand,path,print_from_engineering,*,linear_deflection,angular_deflection,
               relative,comparison_tolerance,max_relative_volume_error):
    import FreeCAD as A
    import Part
    import Mesh
    import MeshPart
    for name,value in [('linear deflection',linear_deflection),('angular deflection',angular_deflection),
                       ('comparison tolerance',comparison_tolerance),('volume error',max_relative_volume_error)]:
        positive(value,name)
    if type(relative) is not bool: raise ValueError('Relative mode must be explicit boolean')
    if operand.status!='RESOLVED' or len(operand.shape.Solids)!=1:
        raise ValueError('Print export requires one resolved solid')
    if not matrix_checks(print_from_engineering)['rigid_right_handed']:
        raise ValueError('Print transform must be rigid and right handed')
    target=Path(path).resolve()
    if target.exists(): raise FileExistsError(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    shape=operand.shape.copy(); shape.transformShape(print_from_engineering,False)
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=linear_deflection,
                              AngularDeflection=angular_deflection,Relative=relative)
    mesh.write(str(target))
    reopened=Mesh.Mesh(str(target))
    checks={'closed':reopened.isSolid(),'nonmanifold':reopened.hasNonManifolds(),
            'self_intersections':reopened.hasSelfIntersections(),
            'inconsistent_orientation':reopened.hasNonUniformOrientedFacets()}
    if not checks['closed'] or any(v for k,v in checks.items() if k!='closed'):
        raise RuntimeError('Delivered mesh topology failed: '+repr(checks))
    # Every mesh vertex and triangle centroid: explicitly sampled, not Hausdorff proof.
    vertices,triangles=reopened.Topology
    samples=list(vertices)+[sum((vertices[i] for i in tri),A.Vector())/3 for tri in triangles]
    surface=Part.makeCompound(shape.Faces)
    max_deviation=max(Part.Vertex(p).distToShape(surface)[0] for p in samples)
    mesh_bbox=[reopened.BoundBox.XMin,reopened.BoundBox.YMin,reopened.BoundBox.ZMin,
               reopened.BoundBox.XMax,reopened.BoundBox.YMax,reopened.BoundBox.ZMax]
    bbox_delta=max(abs(x-y) for x,y in zip(bounds(shape),mesh_bbox))
    volume_error=abs(abs(reopened.Volume)-shape.Volume)/shape.Volume
    passed=max_deviation<=comparison_tolerance and bbox_delta<=comparison_tolerance and volume_error<=max_relative_volume_error
    return {'status':'PASS' if passed else 'FAIL','requirement':'declared mesh topology and sampled-export tolerances',
            'sha256':file_hash(target),'path':str(target),'source':operand.record(),
            'transform_direction':f'T_print<-{operand.frame}','T_print_from_engineering':list(print_from_engineering.A),'units':'mm',
            'meshing':{'linear_deflection':linear_deflection,'angular_deflection_radians':angular_deflection,'relative':relative},
            'topology':checks,'method':'all delivered vertices and triangle centroids to source surface; bbox; enclosed volume',
            'sample_count':len(samples),'max_sampled_deviation_mm':max_deviation,'bbox_delta_mm':bbox_delta,
            'relative_volume_error':volume_error,'tolerances':{'distance_mm':comparison_tolerance,'relative_volume':max_relative_volume_error},
            'unchecked':['Not a global surface-deviation bound','No printability/strength/physical-fit proof']}
