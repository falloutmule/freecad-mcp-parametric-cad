"""Machine-readable helper availability, explicitly separate from native evidence."""
from __future__ import annotations
import importlib
import platform
import sys

IMPLEMENTED = ("parameter_objects", "rectangle_sketch", "circle_sketch", "disjoint_circle_profiles",
               "body_local_origin_planes", "offset_datum_planes", "pad", "pocket", "revolve", "groove",
               "additive_loft", "subtractive_loft", "parameter_sample_planning", "parameter_sample_execution")
DEFERRED = ("hole_feature", "pipe_sweep", "linear_pattern", "polar_pattern", "fillet", "chamfer",
            "shape_binder", "assembly_joint_creation", "assembly_solving", "generated_face_attachment",
            "hard_kernel_timeout", "continuous_parameter_domain_proof")


def capabilities() -> dict:
    """Imports FreeCAD when available; never creates a document or changes GUI state.

    Importability/version is NOT runtime acceptance. Native evidence remains
    NOT_RUN here; review a matching, hashed test report separately.
    """
    from . import __version__
    try:
        app = importlib.import_module("FreeCAD")
        runtime = {"available": True, "version": [str(v) for v in app.Version()],
                   "gui_up": bool(app.GuiUp)}
    except Exception as exc:
        runtime = {"available": False, "error_type": type(exc).__name__, "error": str(exc)}
    return {"schema_version": 1, "skill_version": __version__, "python": sys.version,
            "platform": platform.platform(), "freecad": runtime,
            "helpers": {name: {"implemented": True,
                               "native_acceptance": "NOT_RUN" if name != "parameter_sample_planning" else "NOT_APPLICABLE"}
                        for name in IMPLEMENTED},
            "deferred": {name: {"implemented": False} for name in DEFERRED},
            "scope": "Creation helper surface only; existing frame/geometry/export modules retain their own contracts",
            "limits": {"circle_profiles": 64, "loft_profiles": 8, "sample_cases": 256},
            "notes": ["No unverified helper is represented as native-tested",
                      "Capability discovery is not a license to mutate or a fit certificate",
                      "Timeouts between calls cannot interrupt a single native kernel call"]}
