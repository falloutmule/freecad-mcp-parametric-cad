"""An editable native example. All dimensions are fixtures, not user requirements.

Call build(doc) on the GUI writer thread, passing a task-owned FreeCAD document.
This function does not create/close documents, save files, change settings, or print.
A failed multi-step build may leave earlier successful features for inspection.
"""
from fcskill.modeling import (Parameter, create_parameters, reference, create_body,
                              rectangle, circles, offset_plane, pad, pocket)


def build(doc):
    params = create_parameters(doc, "DemoParameters", {
        "Width": Parameter(40, 32, 60, description="Plate width, mm"),
        "Height": Parameter(30, 24, 45, description="Plate height, mm"),
        "Thickness": Parameter(5, 3, 10, description="Plate thickness, mm"),
        "HoleRadius": Parameter(2, 1, 3, description="Four-hole radius, mm")})
    body = create_body(doc, "DemoPlate")
    profile = rectangle(body, "DemoOutline", reference(params, "Width"), reference(params, "Height"))
    base = pad(body, "DemoBase", profile, reference(params, "Thickness"))
    top = offset_plane(body, "DemoTopDatum", offset=reference(params, "Thickness"))
    holes = circles(body, "DemoHoleProfiles", reference(params, "HoleRadius"),
                    [(-12, -7), (12, -7), (-12, 7), (12, 7)], support=top)
    result = pocket(body, "DemoHoles", holes, reference(params, "Thickness"))
    return {"parameters": params, "body": body, "base": base, "top_datum": top,
            "profile": profile, "hole_profiles": holes, "result": result}
