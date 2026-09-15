"""Conservative rigid capture witnesses; absence of evidence cannot become PASS."""
import math

REQUIRED = {"cap_left", "cap_right", "closed_hoop", "guide_left", "guide_right"}


def retention_decision(coverage, projected_cap, opening):
    if not REQUIRED.issubset(coverage) or projected_cap is None or opening is None:
        return "UNVERIFIED"
    if not all(math.isfinite(v) and v > 0 for v in (projected_cap, opening)):
        raise ValueError("Positive finite capture dimensions required")
    return "PASS" if all(coverage[k] is True for k in REQUIRED) and projected_cap > opening else "FAIL"


def joint_claims(free_motion, retention, pose_holding="UNVERIFIED", holding_required=True):
    values = (free_motion, retention, pose_holding)
    if any(v not in {"PASS", "FAIL", "UNVERIFIED", "NOT_REQUESTED"} for v in values):
        raise ValueError("Unknown claim state")
    required = values if holding_required else values[:2]
    status = "PASS" if all(v == "PASS" for v in required) else "FAIL" if "FAIL" in required else "UNVERIFIED"
    return dict(free_motion=free_motion, retention=retention, pose_holding=pose_holding, requested_claims=status)


def capture_shapes(parent, child, witnesses, projected_cap, opening, tolerance=1e-6):
    for shape in (parent, child):
        if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
            return dict(status="FAIL", reason="Each rigid body must be one valid solid")
    coverage, missing = {}, {}
    for key, witness in witnesses.items():
        if key not in REQUIRED or witness.isNull() or not witness.isValid() or witness.Volume <= tolerance:
            raise ValueError("Invalid capture witness")
        owner = parent if key.startswith("cap_") else child
        missing[key] = witness.cut(owner).Volume
        coverage[key] = missing[key] <= tolerance
    return dict(status=retention_decision(coverage, projected_cap, opening), coverage=coverage,
                missing_volume_mm3=missing, projected_cap_mm=projected_cap, opening_mm=opening,
                scope="Rigid undeformed captive-hinge witness; excludes elastic rupture and arbitrary socket families")


def classify_contact(common, cam, leaf, tolerance=1e-7):
    intended = common.common(cam).common(leaf).Volume
    unintended = max(0.0, common.Volume-intended)
    return dict(intended_mm3=intended, unintended_mm3=unintended,
                pass_unintended=unintended <= tolerance)


def mass_sanity(native_volume_mm3, reported_grams, density=1.24, declared_auxiliary_grams=2.0):
    values = (native_volume_mm3, reported_grams, density)
    if not all(math.isfinite(v) and v > 0 for v in values) or not math.isfinite(declared_auxiliary_grams) or declared_auxiliary_grams < 0:
        raise ValueError("Finite positive volume/mass/density and nonnegative auxiliary mass required")
    bound = native_volume_mm3/1000*density + declared_auxiliary_grams
    return dict(plausible_upper_bound=reported_grams <= bound, solid_plus_auxiliary_grams=bound,
                scope="Conservative upper bound only; inspect low estimates, time, infill and purge separately")
