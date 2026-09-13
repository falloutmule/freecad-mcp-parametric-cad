# Bounded parameter testing

The implementation is `fcskill.modeling.sweeps`. The planner works in ordinary
Python. The native parameter bridge requires FreeCAD and the existing skill's
writer/GUI-thread contract. Native behavior is experimental until acceptance runs.

## Minimal native workflow

On the FreeCAD GUI thread, with an already built task-owned model `out` from
`scripts/examples/parametric_mounting_plate.py`:

```python
from fcskill.modeling import solid_metrics
from fcskill.modeling.sweeps import (
    parameter_domains, plan_samples, sweep_parameters, RestorationError,
)

params = out["parameters"]
domains = parameter_domains(params, ["Width", "HoleRadius"])
plan = plan_samples(domains, max_cases=16, seed=7)
report = sweep_parameters(
    params, plan,
    validate=lambda: solid_metrics(out["result"]),
    deadline_seconds=60,
)
```

This validator establishes only one valid positive-volume solid. For meaningful
mechanical claims use a task-specific function returning a JSON-safe record:

```python
def validate_requested_volume():
    import math
    measured = solid_metrics(out["result"])
    expected = (params.Width.Value * params.Height.Value * params.Thickness.Value
                - 4 * math.pi * params.HoleRadius.Value**2 * params.Thickness.Value)
    error = abs(measured["volume_mm3"] - expected)
    return {
        "status": "PASS" if error <= 1e-5 else "FAIL",
        "requirement": "DEMO_FOUR_HOLE_PLATE_ANALYTIC_VOLUME",
        "expected_mm3": expected,
        "measured_mm3": measured["volume_mm3"],
        "absolute_tolerance_mm3": 1e-5,
        "unchecked": ["hole positions", "clearance", "strength", "manufacturing"],
    }
```

Even the analytic volume equation does not independently prove the hole positions.
Its numeric tolerance is a fixture assertion, not an application-wide tolerance.

## Domains and planner

`Domain(minimum, maximum, baseline, kind="real")` also supports `kind="integer"`.
All values must be finite, baseline inside the declared bounds, and integer values
integral when requested. Explicit parameter names are required. Native bridge
selection takes `None` (all declared parameters) or a list/tuple of names, not a
string or generator. It refuses selected expression-driven properties instead of
silently replacing their expressions.

`plan_samples(domains, max_cases=32, seed=0)` accepts 1–64 domains and at most 256
cases. It produces the baseline, one-at-a-time endpoints, corners only when their
entire candidate count fits the configured budget, and deterministic seeded random
fill. Every stage shares the same total case cap. Duplicate cases are removed and
random attempts are capped. A saturated/constant discrete domain can yield fewer
cases than requested. No exponential enumeration of an oversized corner set occurs.

Coverage records expose baseline inclusion, unique point count, endpoint inclusion,
theoretical corner count and actually included corners. Requesting enough slots
for the corner count alone does not guarantee all corners if earlier cases consume
slots; actual coverage is calculated rather than assumed.

## Execution and evidence

`run_cases(...)` is a reusable Python engine with explicit `read_values`,
`apply_values`, `recompute` and `validate` callbacks. Callbacks are trusted; this is
not a general code execution sandbox. The FreeCAD-specific `sweep_parameters`
bridge limits property writes to the selected declared parameters.

Before mutation, every case is checked against the exact declared scope/bounds and
the observed baseline must match the plan. A stale plan is refused. Between
samples, baseline values are reapplied and recomputed; the requested sample is
then applied and recomputed. Property readback must match within explicit numeric
comparison tolerances (relative 1e-12, absolute 1e-9 in native property units).
Boolean/empty validator results, missing requirement names, exceptions and non-JSON
or nonfinite evidence do not become PASS.

The report separates:

| Field | Meaning |
| --- | --- |
| `planned_coverage` | Point coverage recalculated from the actual submitted cases. Supplied plan flags are not trusted. |
| `attempted_coverage` | Cases reached by the execution loop, including unsuccessful attempts. Not a correctness claim. |
| `passing_coverage` | Only cases whose validator explicitly returned PASS. Not a continuous-domain proof. |
| `counts`, `not_run` | PASS/FAIL/UNVERIFIED case counts and cases not reached. |
| `restoration` | Parameter-value readback/recompute result, separately from baseline geometric validation. |

A failed requirement remains FAIL. Exceptions remain UNVERIFIED. Full sample-run
PASS requires all requested cases to reach PASS, plus a passing baseline validator
after restoration. None of these records certify the original unsampled range.
Every coverage record states `continuous_domain_proven: false`.

## Restoration and failure boundaries

A `finally` block restores the actual starting values, recomputes and verifies
readback. This also runs during `KeyboardInterrupt`. A failed restore raises
`RestorationError`; its `.report` preserves the incomplete evidence. Stop and
inspect that document rather than blindly replaying the operation.

Restored values are distinguished from restored design validity. A validator
failure can leave restoration-of-values PASS but baseline-validity UNVERIFIED/FAIL.
The helper cannot promise to reverse arbitrary callback side effects, undo native
topology changes outside the intended parameter graph, or recover a crashed host.
Save evidence only to a task-owned new path under the existing session rules.

`deadline_seconds` is a **soft deadline checked between sample iterations**, not an
OCCT timeout. Restoring baseline can itself call the kernel after the deadline.
It cannot interrupt a native call that is already blocked, and a process crash
cannot execute a Python `finally` block. Use an isolated host for expensive or
untrusted geometry experiments.

## Acceptance

Unit/mocked tests exercise planner bounds, stale-plan rejection, failures,
readback, interrupted restoration and evidence semantics. They do not solve a
FreeCAD sketch. Native fixtures additionally test an analytic four-hole plate
across samples and verify its baseline geometry after restoration. Run them using
`scripts/run_modeling_tests.py` in a fresh matching FreeCAD host.
