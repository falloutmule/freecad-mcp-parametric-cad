"""Create-only native helpers. No saves, closes, global transactions, or GUI selection."""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import math
from numbers import Real
import re
from typing import Any, Iterator


class ModelingError(RuntimeError):
    """A structured operational failure, not an engineering fit judgment."""
    def __init__(self, code: str, message: str, **details: Any):
        super().__init__(message)
        self.code, self.details = code, details

    def record(self) -> dict:
        return {"status": "UNVERIFIED", "code": self.code,
                "message": str(self), "details": self.details}


def finite(value: Real, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a number, not a bool, string, or quantity")
    number = float(value)
    if not math.isfinite(number) or (positive and number <= 0):
        raise ValueError(f"{label} must be finite" + (" and positive" if positive else ""))
    return number


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        raise ValueError("Use an explicit ASCII internal identifier: letters, digits, underscores")
    return value


@dataclass(frozen=True)
class Dim:
    """Numeric seed in mm (length/offset) or degrees (angle), with optional expression.

    An expression is trusted FreeCAD expression text, NOT Python and NOT a sandbox.
    The seed initializes geometry; FreeCAD evaluates the expression on recompute.
    """
    value: float
    expression: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "value", finite(self.value, "dimension"))
        if self.expression is not None:
            if not isinstance(self.expression, str) or not self.expression.strip():
                raise ValueError("Expression must be nonempty text")
            if len(self.expression) > 4096 or any(c in self.expression for c in "\r\n\x00"):
                raise ValueError("Expression is too long or contains a line break/NUL")


def dimension(value: Real | Dim, label: str, *, positive: bool = False) -> Dim:
    result = value if isinstance(value, Dim) else Dim(value)
    finite(result.value, label, positive=positive)
    return result


def set_dimension(obj: Any, prop: str, value: Dim) -> None:
    setattr(obj, prop, value.value)
    if value.expression is not None:
        obj.setExpression(prop, value.expression)


def writer():
    # Preserve the established skill's GUI-thread and one-writer policy.
    from ..session import writer as existing_writer
    return existing_writer()


def require_live(obj: Any, *, type_id: str | None = None) -> Any:
    doc = getattr(obj, "Document", None)
    if doc is None or doc.getObject(obj.Name) != obj:
        raise ModelingError("STALE_OBJECT", "Expected a live, exact document object")
    if type_id is not None and obj.TypeId != type_id:
        raise ModelingError("WRONG_TYPE", f"Expected {type_id}, received {obj.TypeId}")
    return doc


def require_body(body: Any) -> Any:
    return require_live(body, type_id="PartDesign::Body")


@contextmanager
def new_object(container: Any, type_id: str, name: str) -> Iterator[Any]:
    """Own only the newly created object; clean it up on failure.

    Does NOT open/commit/abort a user transaction. Native side effects on other
    properties are not a general rollback guarantee. Never use this as a wrapper
    around arbitrary mutations. A cleanup failure remains explicit.
    """
    identifier(name)
    body = container if getattr(container, "TypeId", None) == "PartDesign::Body" else None
    doc = require_body(body) if body is not None else container
    with writer():
        if doc.getObject(name) is not None:
            raise ModelingError("NAME_EXISTS", f"Refusing to reuse or auto-rename {name}")
        old_tip = body.Tip if body is not None else None
        obj = body.newObject(type_id, name) if body is not None else doc.addObject(type_id, name)
        try:
            if obj.Name != name:
                raise ModelingError("UNEXPECTED_NAME", "FreeCAD changed the requested internal name")
            yield obj
        except BaseException as original:
            errors = []
            try:
                if doc.getObject(obj.Name) != obj:
                    raise RuntimeError("New object identity changed; refusing removal")
                doc.removeObject(obj.Name)
                if body is not None:
                    body.Tip = old_tip
                doc.recompute()
            except Exception as cleanup_error:
                errors.append(str(cleanup_error))
            if errors:
                raise ModelingError("CLEANUP_FAILED", "Inspect the document; do not replay blindly",
                                    original_error=str(original), cleanup_errors=errors) from original
            raise


def object_state(obj: Any) -> list[str]:
    raw = getattr(obj, "State", None)
    if not isinstance(raw, (list, tuple)):
        raise ModelingError("STATE_UNAVAILABLE", "Cannot establish current object state", object=obj.Name)
    state = [str(v) for v in raw]
    if any(word in s.lower() for s in state for word in ("invalid", "error", "touched")):
        raise ModelingError("STALE_OR_INVALID_FEATURE", "Do not validate a retained last-good shape",
                            object=obj.Name, state=state)
    return state


def recompute_check(doc: Any, objects: list[Any]) -> None:
    """Recompute and check the affected scope, not unrelated document geometry."""
    doc.recompute()
    for obj in objects:
        require_live(obj)
        object_state(obj)


def solid_metrics(obj: Any) -> dict:
    """One non-null valid positive-volume solid; no fit/manufacturing claim."""
    require_live(obj)
    state = object_state(obj)
    try:
        shape = obj.Shape
        valid = not shape.isNull() and shape.isValid()
        count = len(shape.Solids)
        volume = float(shape.Volume)
        if not valid or count != 1 or not math.isfinite(volume) or volume <= 0:
            raise ValueError(f"valid={valid}, solids={count}, volume={volume}")
        return {"status": "PASS", "requirement": "ONE_VALID_POSITIVE_VOLUME_SOLID",
                "volume_mm3": volume, "solid_count": count, "object": obj.Name, "object_state": state,
                "scope": "affected native shape only; not design intent or fit"}
    except Exception as exc:
        raise ModelingError("INVALID_SOLID", f"Invalid solid at {obj.Name}", error=str(exc)) from exc
