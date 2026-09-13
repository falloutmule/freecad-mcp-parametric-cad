"""Small explicit native PartDesign vocabulary with per-feature solid gates."""
from __future__ import annotations
from ._core import (ModelingError, dimension, new_object, recompute_check, require_body,
                    require_live, set_dimension, solid_metrics, writer)
from .sketch import inspect_sketch


def create_body(doc, name: str):
    with new_object(doc, "PartDesign::Body", name) as body:
        recompute_check(doc, [body])
        return body


def _profile(body, profile) -> None:
    doc = require_body(body)
    if require_live(profile, type_id="Sketcher::SketchObject") != doc or profile not in body.Group:
        raise ModelingError("PROFILE_OWNERSHIP", "Profile must belong to the exact target body")
    recompute_check(doc, [profile])
    info = inspect_sketch(profile)
    if not (info["fresh"] and info["fully_constrained"] is True and
            info["profile_closed"] is True and info["shape_valid"] is True):
        raise ModelingError("PROFILE_UNVERIFIED", "Expected a fully constrained valid closed sketch", snapshot=info)


def _bool(value, name):
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool")
    return value


def _extrusion(body, name, profile, length, reversed, type_id):
    d = dimension(length, "length", positive=True)
    _bool(reversed, "reversed")
    with writer():
        _profile(body, profile)
        with new_object(body, type_id, name) as feature:
            feature.Profile = profile
            set_dimension(feature, "Length", d)
            feature.Reversed = reversed
            body.Tip = feature
            recompute_check(body.Document, [profile, feature])
            solid_metrics(feature)
            return feature


def pad(body, name: str, profile, length, *, reversed: bool = False):
    """One-sided native Pad. Length is in mm; no face-based termination inference."""
    return _extrusion(body, name, profile, length, reversed, "PartDesign::Pad")


def pocket(body, name: str, profile, length, *, reversed: bool = False):
    """One-sided finite-length native Pocket, not an unbounded through-all claim."""
    return _extrusion(body, name, profile, length, reversed, "PartDesign::Pocket")


def _revolution(body, name, profile, angle, axis, reversed, type_id):
    d = dimension(angle, "angle", positive=True)
    if d.value > 360:
        raise ValueError("Angle seed must be at most 360 degrees")
    if axis not in ("H_Axis", "V_Axis"):
        raise ValueError("Use the profile's explicit H_Axis or V_Axis")
    _bool(reversed, "reversed")
    with writer():
        _profile(body, profile)
        with new_object(body, type_id, name) as feature:
            feature.Profile = profile
            feature.ReferenceAxis = (profile, [axis])
            set_dimension(feature, "Angle", d)
            feature.Reversed = reversed
            body.Tip = feature
            recompute_check(body.Document, [profile, feature])
            solid_metrics(feature)
            return feature


def revolve(body, name: str, profile, angle=360, *, axis="V_Axis", reversed: bool = False):
    return _revolution(body, name, profile, angle, axis, reversed, "PartDesign::Revolution")


def groove(body, name: str, profile, angle=360, *, axis="V_Axis", reversed: bool = False):
    return _revolution(body, name, profile, angle, axis, reversed, "PartDesign::Groove")


def _loft(body, name, profiles, ruled, type_id):
    if not isinstance(profiles, (list, tuple)) or not 2 <= len(profiles) <= 8:
        raise ValueError("Provide 2..8 explicitly ordered profiles")
    _bool(ruled, "ruled")
    if len({p.Name for p in profiles}) != len(profiles):
        raise ValueError("Profiles must be distinct")
    with writer():
        for p in profiles:
            _profile(body, p)
        with new_object(body, type_id, name) as feature:
            feature.Profile = profiles[0]
            feature.Sections = list(profiles[1:])
            feature.Ruled = ruled
            feature.Closed = False
            body.Tip = feature
            recompute_check(body.Document, [*profiles, feature])
            solid_metrics(feature)
            return feature


def additive_loft(body, name: str, profiles, *, ruled: bool = False):
    return _loft(body, name, profiles, ruled, "PartDesign::AdditiveLoft")


def subtractive_loft(body, name: str, profiles, *, ruled: bool = False):
    return _loft(body, name, profiles, ruled, "PartDesign::SubtractiveLoft")
