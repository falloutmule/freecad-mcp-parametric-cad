"""Typed parameter objects with persisted declared bounds; no Python proxy needed."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from collections.abc import Mapping
from ._core import Dim, ModelingError, finite, identifier, new_object, recompute_check, require_live

KINDS = {"length": "App::PropertyLength", "angle": "App::PropertyAngle",
         "number": "App::PropertyFloat", "integer": "App::PropertyInteger"}
UNITS = {"length": "mm", "angle": "deg", "number": "1", "integer": "1"}
SCHEMA_PROPERTY = "FcskillParameterSchema"


@dataclass(frozen=True)
class Parameter:
    value: float
    minimum: float
    maximum: float
    kind: str = "length"
    description: str = ""

    def __post_init__(self):
        for key in ("value", "minimum", "maximum"):
            finite(getattr(self, key), key)
        if self.kind not in KINDS:
            raise ValueError(f"Unsupported parameter kind: {self.kind}")
        if not self.minimum <= self.value <= self.maximum:
            raise ValueError("Require minimum <= initial value <= maximum")
        if self.kind == "integer" and any(float(v) != int(v) for v in
                                          (self.minimum, self.value, self.maximum)):
            raise ValueError("Integer parameters need integer values and bounds")
        if self.kind == "integer" and not -(2**31) <= self.minimum <= self.maximum < 2**31:
            raise ValueError("Integer bounds must fit a signed 32-bit FreeCAD property")
        if not isinstance(self.description, str):
            raise ValueError("Description must be text")


def create_parameters(doc, name: str, definitions: Mapping[str, Parameter]):
    if not isinstance(definitions, Mapping) or not 1 <= len(definitions) <= 64:
        raise ValueError("Provide 1..64 explicit parameter definitions")
    for key, spec in definitions.items():
        identifier(key)
        if not isinstance(spec, Parameter) or key == SCHEMA_PROPERTY:
            raise ValueError("Each parameter needs a Parameter definition and a nonreserved name")
    with new_object(doc, "App::FeaturePython", name) as obj:
        for key in definitions:
            if key in obj.PropertiesList or hasattr(obj, key):
                raise ValueError(f"Parameter name collides with a native property: {key}")
        for key, spec in definitions.items():
            obj.addProperty(KINDS[spec.kind], key, "Parameters", spec.description)
            setattr(obj, key, int(spec.value) if spec.kind == "integer" else float(spec.value))
        obj.addProperty("App::PropertyString", SCHEMA_PROPERTY, "SkillMetadata")
        setattr(obj, SCHEMA_PROPERTY, json.dumps({"schema_version": 1,
                "parameters": {k: {**asdict(v), "units": UNITS[v.kind]} for k, v in definitions.items()}},
                sort_keys=True, allow_nan=False))
        obj.setEditorMode(SCHEMA_PROPERTY, 1)
        recompute_check(doc, [obj])
        return obj


def read_schema(obj) -> dict[str, Parameter]:
    require_live(obj)
    try:
        raw = json.loads(getattr(obj, SCHEMA_PROPERTY))
        if raw["schema_version"] != 1 or not isinstance(raw["parameters"], dict):
            raise ValueError("Unsupported schema")
        result = {}
        for name, value in raw["parameters"].items():
            identifier(name)
            data = dict(value)
            units = data.pop("units")
            spec = Parameter(**data)
            if units != UNITS[spec.kind] or obj.getTypeIdOfProperty(name) != KINDS[spec.kind]:
                raise ValueError(f"Property type or unit mismatch: {name}")
            result[name] = spec
        if not 1 <= len(result) <= 64:
            raise ValueError("Invalid parameter count")
        return result
    except Exception as exc:
        raise ModelingError("PARAMETER_SCHEMA", "Cannot trust this parameter object", error=str(exc)) from exc


def value_of(obj, name: str) -> float:
    value = getattr(obj, name)
    return finite(getattr(value, "Value", value), name)


def reference(obj, name: str) -> Dim:
    specs = read_schema(obj)
    if name not in specs:
        raise ValueError(f"Undeclared parameter: {name}")
    return Dim(value_of(obj, name), f"{obj.Name}.{name}")
