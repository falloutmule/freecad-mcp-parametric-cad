"""Small native modeling examples; dimensions are fixtures, not design requirements."""
import FreeCAD as A
import Part
import Sketcher

def fixed_rectangle(sk,x,y,w,h):
    points=[A.Vector(x,y,0),A.Vector(x+w,y,0),A.Vector(x+w,y+h,0),A.Vector(x,y+h,0)]
    for i in range(4):
        edge=sk.addGeometry(Part.LineSegment(points[i],points[(i+1)%4]),False)
        sk.addConstraint(Sketcher.Constraint('Block',edge))

def mounting_plate(doc):
    body=doc.addObject('PartDesign::Body','MountingPlate')
    params=doc.addObject('App::FeaturePython','PlateParameters')
    params.addProperty('App::PropertyLength','HoleDiameter','Parameters'); params.HoleDiameter=4
    sk=body.newObject('Sketcher::SketchObject','PlateProfile'); fixed_rectangle(sk,0,0,40,30)
    pad=body.newObject('PartDesign::Pad','PlatePad'); pad.Profile=sk; pad.Length=5
    holes=body.newObject('Sketcher::SketchObject','HolePattern')
    holes.setExpression('Placement.Base.z','PlatePad.Length')
    for x,y in [(8,8),(32,8),(8,22),(32,22)]:
        i=holes.addGeometry(Part.Circle(A.Vector(x,y,0),A.Vector(0,0,1),2),False)
        holes.addConstraint(Sketcher.Constraint('DistanceX',i,3,x))
        holes.addConstraint(Sketcher.Constraint('DistanceY',i,3,y))
        c=holes.addConstraint(Sketcher.Constraint('Radius',i,2))
        holes.setExpression(f'Constraints[{c}]','PlateParameters.HoleDiameter / 2')
    pocket=body.newObject('PartDesign::Pocket','MountHoles'); pocket.Profile=holes
    pocket.setExpression('Length','PlatePad.Length')
    doc.recompute()
    return params,pocket

def bracket(doc):
    body=doc.addObject('PartDesign::Body','DatumBracket')
    base=body.newObject('PartDesign::AdditiveBox','BracketBase'); base.Length=30; base.Width=20; base.Height=4
    plane=body.newObject('PartDesign::Plane','SecondaryDatum')
    plane.AttachmentSupport=(doc.getObject('XY_Plane'),[''])
    plane.MapMode='FlatFace'
    plane.setExpression('AttachmentOffset.Base.z','BracketBase.Height')
    profile=body.newObject('Sketcher::SketchObject','UprightProfile')
    profile.AttachmentSupport=(plane,['']); profile.MapMode='FlatFace'
    fixed_rectangle(profile,0,0,30,4)
    pad=body.newObject('PartDesign::Pad','Upright'); pad.Profile=profile; pad.Length=16
    doc.recompute()
    return body,base,plane,pad

def enclosure(doc):
    body=doc.addObject('PartDesign::Body','Enclosure')
    params=doc.addObject('App::FeaturePython','EnclosureParameters')
    params.addProperty('App::PropertyLength','Wall','Parameters'); params.Wall=3
    outer=body.newObject('PartDesign::AdditiveBox','Outer'); outer.Length=30; outer.Width=24; outer.Height=15
    cavity=body.newObject('PartDesign::SubtractiveBox','Cavity')
    for axis in ('x','y','z'): cavity.setExpression('Placement.Base.'+axis,'EnclosureParameters.Wall')
    cavity.setExpression('Length','Outer.Length - 2 * EnclosureParameters.Wall')
    cavity.setExpression('Width','Outer.Width - 2 * EnclosureParameters.Wall')
    cavity.setExpression('Height','Outer.Height')
    doc.recompute()
    return params,cavity
