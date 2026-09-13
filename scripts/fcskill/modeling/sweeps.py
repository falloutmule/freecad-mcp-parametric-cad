"""Bounded, deterministic parameter sampling with mandatory restoration.

A successful sample is evidence ONLY for that sample. It does not establish a
continuous valid parameter domain. The deadline is checked BETWEEN native calls;
it cannot interrupt an OCCT call or repair a crashed/hung FreeCAD process.
"""
from __future__ import annotations
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
import itertools
import json
import math
import random
import time
from ._core import ModelingError, finite, identifier, writer


@dataclass(frozen=True)
class Domain:
    minimum: float
    maximum: float
    baseline: float
    kind: str = "real"

    def __post_init__(self):
        for key in ("minimum", "maximum", "baseline"):
            finite(getattr(self, key), key)
        if self.kind not in ("real", "integer"):
            raise ValueError("Domain kind must be real or integer")
        if not self.minimum <= self.baseline <= self.maximum:
            raise ValueError("Require minimum <= baseline <= maximum")
        if self.kind == "integer" and any(float(v) != int(v) for v in
                                          (self.minimum, self.maximum, self.baseline)):
            raise ValueError("Integer domain has a non-integer value")

    def check(self, value, name):
        v = finite(value, name)
        if not self.minimum <= v <= self.maximum or (self.kind == "integer" and v != int(v)):
            raise ValueError(f"Out-of-domain value for {name}: {v}")
        return int(v) if self.kind == "integer" else v


def _domains(domains):
    if not isinstance(domains, Mapping) or not 1 <= len(domains) <= 64:
        raise ValueError("Provide 1..64 named domains")
    for name, value in domains.items():
        identifier(name)
        if not isinstance(value, Domain):
            raise ValueError("Each domain must be a Domain instance")
    return sorted(domains)


def _coverage(domains, cases):
    """Recalculate point coverage; never trust claimed flags from an input plan."""
    names = sorted(domains)
    baseline = {n: domains[n].baseline for n in names}
    seen = {tuple(c[n] for n in names) for c in cases}
    endpoints = [set((domains[n].minimum, domains[n].maximum)) for n in names]
    axis_keys = []
    for name in names:
        for endpoint in (domains[name].minimum, domains[name].maximum):
            c = {**baseline, name: endpoint}
            axis_keys.append(tuple(c[n] for n in names))
    corners = math.prod(len(values) for values in endpoints)
    actual = sum(all(value in endpoints[i] for i, value in enumerate(key)) for key in seen)
    return {"baseline_included": tuple(baseline[n] for n in names) in seen,
            "unique_case_count": len(seen),
            "all_axis_endpoints_included": all(key in seen for key in axis_keys),
            "theoretical_corner_count": corners, "sampled_corner_count": actual,
            "all_corners_included": actual == corners, "continuous_domain_proven": False}


def plan_samples(domains: Mapping[str, Domain], *, max_cases: int = 32, seed: int = 0) -> dict:
    names = _domains(domains)
    if type(max_cases) is not int or not 1 <= max_cases <= 256:
        raise ValueError("max_cases must be an integer from 1 through 256")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    baseline = {n: domains[n].check(domains[n].baseline, n) for n in names}
    cases, seen = [], set()

    def add(case):
        key = tuple(case[n] for n in names)
        if key not in seen and len(cases) < max_cases:
            cases.append(case.copy())
            seen.add(key)

    add(baseline)
    axis_cases = []
    for name in names:
        for endpoint in (domains[name].minimum, domains[name].maximum):
            case = {**baseline, name: domains[name].check(endpoint, name)}
            axis_cases.append(case)
            add(case)
    endpoints = [sorted({domains[n].check(domains[n].minimum, n),
                         domains[n].check(domains[n].maximum, n)}) for n in names]
    corner_count = math.prod(len(e) for e in endpoints)
    # No exponential enumeration when the entire corner set exceeds the budget.
    if corner_count <= max_cases:
        for values in itertools.product(*endpoints):
            add(dict(zip(names, values)))
    rng = random.Random(seed)
    attempts = 0
    while len(cases) < max_cases and attempts < max_cases * 20:
        attempts += 1
        case = {n: (rng.randint(int(domains[n].minimum), int(domains[n].maximum))
                    if domains[n].kind == "integer" else
                    rng.uniform(domains[n].minimum, domains[n].maximum)) for n in names}
        add(case)
    return {"schema_version": 1, "seed": seed, "requested_max_cases": max_cases,
            "domains": {n: asdict(domains[n]) for n in names}, "cases": cases,
            "coverage": _coverage(domains, cases),
            "limitations": ["Sampled configurations only; no inferred valid interval",
                            "Random-fill attempts are bounded; requested count may not be reached"]}


class RestorationError(ModelingError):
    def __init__(self, report):
        super().__init__("RESTORE_FAILED", "Parameter restoration is unverified; inspect before further work")
        self.report = report


def _verdict(validate: Callable[[], dict]) -> dict:
    verdict = validate()
    if not isinstance(verdict, dict) or verdict.get("status") not in ("PASS", "FAIL", "UNVERIFIED"):
        raise ValueError("Validator must return an explicit PASS/FAIL/UNVERIFIED record")
    if verdict["status"] in ("PASS", "FAIL") and not isinstance(verdict.get("requirement"), str):
        raise ValueError("PASS/FAIL requires a named requirement")
    if verdict["status"] in ("PASS", "FAIL") and not verdict["requirement"].strip():
        raise ValueError("Requirement must not be empty")
    # Snapshot mutable callback results and reject NaN/non-JSON evidence.
    return json.loads(json.dumps(verdict, allow_nan=False))


def run_cases(domains: Mapping[str, Domain], cases: list[dict], *,
              read_values: Callable[[], dict], apply_values: Callable[[dict], None],
              recompute: Callable[[], object], validate: Callable[[], dict],
              deadline_seconds: float = 60.0) -> dict:
    names = _domains(domains)
    deadline_seconds = finite(deadline_seconds, "deadline_seconds", positive=True)
    if not isinstance(cases, (list, tuple)) or not 1 <= len(cases) <= 256:
        raise ValueError("Provide 1..256 explicit complete cases")
    normalized = []
    for case in cases:
        if not isinstance(case, Mapping) or set(case) != set(names):
            raise ValueError("Every case must specify exactly the declared parameter names")
        normalized.append({n: domains[n].check(case[n], n) for n in names})
    # All cases are checked before the first mutation.
    baseline = read_values()
    if not isinstance(baseline, Mapping) or set(baseline) != set(names):
        raise ValueError("read_values returned an incomplete or excessive scope")
    baseline = {n: domains[n].check(baseline[n], n) for n in names}
    if any(baseline[n] != domains[n].baseline for n in names):
        raise ValueError("Plan baseline is stale; rebuild the plan from the current document")
    report = {"status": "UNVERIFIED", "baseline": baseline.copy(), "cases": [],
              "restoration": {"status": "NOT_RUN"}, "requested_cases": len(cases),
              "continuous_domain_proven": False, "deadline_seconds": deadline_seconds,
              "deadline_kind": "SOFT_BETWEEN_CALLS_NOT_KERNEL_CANCELLATION"}
    start = time.monotonic()
    try:
        for index, values in enumerate(normalized):
            if time.monotonic() - start >= deadline_seconds:
                report["stop_reason"] = "SOFT_DEADLINE"
                break
            row = {"index": index, "values": values, "status": "UNVERIFIED"}
            t0 = time.monotonic()
            try:
                # Isolate each sample from the previous sample's values.
                apply_values(baseline.copy())
                recompute()
                apply_values(values.copy())
                recompute()
                observed = read_values()
                if set(observed) != set(names) or any(not math.isclose(finite(observed[n], n), values[n],
                              rel_tol=1e-12, abs_tol=1e-9) for n in names):
                    raise ValueError("Requested values were not actually applied")
                row["verdict"] = _verdict(validate)
                row["status"] = row["verdict"]["status"]
            except Exception as exc:
                row.update(status="UNVERIFIED", error_type=type(exc).__name__, error=str(exc))
            row["elapsed_seconds"] = time.monotonic() - t0
            report["cases"].append(row)
    finally:
        try:
            apply_values(baseline.copy())
            recompute()
            observed = read_values()
            matches = set(observed) == set(names) and all(math.isclose(finite(observed[n], n), baseline[n],
                       rel_tol=1e-12, abs_tol=1e-9) for n in names)
            if not matches:
                raise ValueError("Restored values do not match the exact starting scope")
            report["restoration"] = {"status": "PASS", "values_match": True,
                                     "scope": "parameter values restored and recompute returned"}
        except Exception as exc:
            report["restoration"] = {"status": "UNVERIFIED", "error": str(exc)}
            report["elapsed_seconds"] = time.monotonic() - start
            raise RestorationError(report) from exc
    try:
        report["restoration"]["baseline_validation"] = _verdict(validate)
    except Exception as exc:
        report["restoration"]["baseline_validation"] = {"status": "UNVERIFIED", "error": str(exc)}
    report["counts"] = {s: sum(r["status"] == s for r in report["cases"])
                        for s in ("PASS", "FAIL", "UNVERIFIED")}
    report["not_run"] = len(cases) - len(report["cases"])
    report["planned_coverage"] = _coverage(domains, normalized)
    report["attempted_coverage"] = _coverage(domains, [r["values"] for r in report["cases"]])
    report["passing_coverage"] = _coverage(domains, [r["values"] for r in report["cases"] if r["status"] == "PASS"])
    baseline_ok = report["restoration"]["baseline_validation"]["status"] == "PASS"
    if report["counts"]["FAIL"] or report["restoration"]["baseline_validation"]["status"] == "FAIL":
        report["status"] = "FAIL"
    elif report["not_run"] == 0 and report["counts"]["UNVERIFIED"] == 0 and baseline_ok:
        report["status"] = "PASS"
    report["elapsed_seconds"] = time.monotonic() - start
    return report


def parameter_domains(obj, names=None) -> dict[str, Domain]:
    from .parameters import read_schema, value_of
    specs = read_schema(obj)
    if names is not None and (not isinstance(names, (list, tuple)) or
                              any(not isinstance(n, str) for n in names)):
        raise ValueError("names must be an explicit list/tuple of parameter names, not a string or generator")
    selected = list(specs) if names is None else list(names)
    if not selected or len(set(selected)) != len(selected) or any(n not in specs for n in selected):
        raise ValueError("Select unique, declared parameter names")
    driven = {row[0] for row in obj.ExpressionEngine}
    if any(n in driven for n in selected):
        raise ModelingError("DRIVEN_PARAMETER", "Refusing to override expression-driven parameters")
    return {n: Domain(specs[n].minimum, specs[n].maximum, value_of(obj, n),
                      "integer" if specs[n].kind == "integer" else "real") for n in selected}


def sweep_parameters(obj, plan: dict, *, validate: Callable[[], dict], deadline_seconds=60.0) -> dict:
    """Run only the named parameter scope, on the existing skill writer thread."""
    from .parameters import value_of
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        raise ValueError("Expected a version-1 sample plan")
    with writer():
        domains = parameter_domains(obj, list(plan["domains"]))
        if {n: asdict(d) for n, d in domains.items()} != plan["domains"]:
            raise ValueError("Parameter values or bounds changed since planning")
        def read():
            return {n: value_of(obj, n) for n in domains}
        def apply(values):
            for n, value in values.items():
                setattr(obj, n, value)
        report = run_cases(domains, plan["cases"], read_values=read, apply_values=apply,
                           recompute=obj.Document.recompute, validate=validate,
                           deadline_seconds=deadline_seconds)
        report["parameter_object"] = {"document": obj.Document.Name, "name": obj.Name}
        return report
