"""Body-local origin/datum references. Generated faces are deliberately unsupported."""
from __future__ import annotations
from ._core import Dim, ModelingError, dimension, new_object, recompute_check, require_body, require_live

PLANE_ROLES = {"XY": "XY_Plane", "XZ": "XZ_Plane", "YZ": "YZ_Plane"}


def origin_plane(body, plane: str = "XY"):
    require_body(body)
    if plane not in PLANE_ROLES:
        raise ValueError("Origin plane must be exactly XY, XZ, or YZ")
    # Role is independent of auto-suffixed Name and translated/user-edited Label.
    origin = body.Origin
    matches = [o for o in origin.OriginFeatures if getattr(o, "Role", None) == PLANE_ROLES[plane]]
    if len(matches) != 1:
        raise ModelingError("ORIGIN_ROLE_UNAVAILABLE", "Cannot resolve an unambiguous body-local plane",
                            role=PLANE_ROLES[plane], matches=len(matches))
    return matches[0]


def resolve_support(body, support="XY"):
    doc = require_body(body)
    obj = origin_plane(body, support) if isinstance(support, str) else support
    if require_live(obj) != doc:
        raise ModelingError("CROSS_DOCUMENT_SUPPORT", "Attachment must stay in the same document")
    if obj in body.Origin.OriginFeatures and obj.TypeId == "App::Plane":
        return obj
    if obj in body.Group and obj.TypeId == "PartDesign::Plane":
        return obj
    raise ModelingError("UNSUPPORTED_ATTACHMENT", "Only this body's origin or datum planes are accepted")


def _attach_new(obj, support, offset: Dim) -> None:
    props = obj.PropertiesList
    prop = "AttachmentSupport" if "AttachmentSupport" in props else "Support" if "Support" in props else None
    if prop is None or "MapMode" not in props or "AttachmentOffset" not in props:
        raise ModelingError("ATTACHMENT_API_UNAVAILABLE", "Required attachment properties are missing")
    setattr(obj, prop, (support, [""]))
    obj.MapMode = "FlatFace"
    # Offset is along SUPPORT's local normal, not necessarily global Z.
    placement = obj.AttachmentOffset
    placement.Base.z = offset.value
    obj.AttachmentOffset = placement
    if offset.expression is not None:
        obj.setExpression("AttachmentOffset.Base.z", offset.expression)


def offset_plane(body, name: str, *, support="XY", offset=0):
    offset = dimension(offset, "offset")
    base = resolve_support(body, support)
    with new_object(body, "PartDesign::Plane", name) as obj:
        _attach_new(obj, base, offset)
        recompute_check(body.Document, [obj])
        return obj
