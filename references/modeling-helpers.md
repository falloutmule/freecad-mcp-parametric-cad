# Native modeling helpers — 2.1.0.dev1

**Experimental implementation, not native-accepted.** The Python and mocked-backend
checks are not FreeCAD geometry evidence. Run `scripts/run_modeling_tests.py` in a
fresh compatible FreeCAD host and review the native report before promoting this
upgrade. `fcskill.capabilities()` deliberately reports `native_acceptance: NOT_RUN`
for native operations; it does not self-certify from a version string.

This is a helper layer inside the existing skill, not an MCP server replacement.
Existing session, frame, geometry, export and mechanical-evidence contracts apply.

## Imports and scope

Resolve this checkout's absolute `scripts` directory before importing. In a fresh
FreeCAD host, on its GUI thread, with a task-owned document `doc`:

```python
from fcskill import identity, capabilities
from fcskill.modeling import (
    Parameter, Dim, create_parameters, reference, create_body,
    rectangle, circle, circles, offset_plane,
    pad, pocket, revolve, groove, additive_loft, subtractive_loft,
    inspect_sketch, solid_metrics,
)

params = create_parameters(doc, "PlateParams", {
    "Width": Parameter(40, 30, 60),
    "Height": Parameter(30, 20, 45),
    "Thickness": Parameter(5, 2, 10),
})
body = create_body(doc, "PlateBody")
outline = rectangle(body, "PlateOutline", reference(params, "Width"),
                    reference(params, "Height"))
result = pad(body, "PlatePad", outline, reference(params, "Thickness"))
print(solid_metrics(result))
```

These dimensions are demonstration fixtures, not fabrication requirements.
`reference(params, "Width")` creates a numeric seed plus the exact FreeCAD
expression `PlateParams.Width`. It does not rely on display labels. The complete
four-hole example is `scripts/examples/parametric_mounting_plate.py`; its `build(doc)`
function neither creates nor closes the supplied document and does not save/export.

## Units and declared parameters

Numeric geometry lengths, centers, radii and offsets are **millimeters**. Numeric
angles are **degrees**. `Dim(seed, expression)` is available when composing an
explicit FreeCAD expression, for example `Dim(2, "PlateParams.Thickness / 2")`.
A seed is only initialization: native recompute must evaluate the expression.
Strings are not guessed to be units or formulas. Boolean, NaN and infinite seeds
are rejected. Expression text is trusted FreeCAD expression input, not a sandbox.

`Parameter(value, minimum, maximum, kind="length", description="")` supports length,
angle, dimensionless number, and signed-32-bit integer properties. Metadata is
persisted as versioned JSON on the parameter object, with property types and unit
labels verified when reread. No custom Python Proxy is required.

**Bounds are declarations, not a global constraint system:** editing a property
manually does not automatically enforce the declared limits. The sample planner and
parameter-sweep bridge enforce them for their own calls. Bounds are not asserted
to be a physically safe or continuously valid design domain.

## Supported operations and deliberate limits

| API | Contract |
| --- | --- |
| `create_body(doc, name)` | New exact internal name only; no reuse or automatic suffixing. |
| `rectangle(body, name, width, height, centered=True, support="XY", offset=0)` | Four coincident, axis-aligned edges; named width/height dimensions; origin symmetry or lower-left origin coincidence. Never `Block`. |
| `circle(body, name, radius, center=(0,0), support="XY", offset=0)` | Radius dimension and explicit numeric center. Zero coordinates use coincidence/point-on-axis rather than zero distance constraints. |
| `circles(body, name, radius, centers, support="XY", offset=0)` | 1–64 disjoint, non-tangent equal-radius circles. Checks both seed and actual initial solved geometry. Centers are fixed numeric positions, not a native pattern. |
| `origin_plane(body, plane="XY")` | Exactly this body's XY/XZ/YZ origin feature, found by `Role`, not a global document name. |
| `offset_plane(body, name, support="XY", offset=0)` | Native datum attached to an origin/datum plane belonging to the same body. Offset is along the support's local normal. |
| `pad(...)`, `pocket(...)` | Finite positive length, explicit optional reversal. No through-all or up-to-face inference. |
| `revolve(...)`, `groove(...)` | Initial angle greater than zero and at most 360 degrees; explicit profile `H_Axis` or `V_Axis`, optional reversal. |
| `additive_loft(...)`, `subtractive_loft(...)` | 2–8 distinct, explicitly ordered profiles in one body; explicit ruled option; non-closed loft. |

All feature helpers return the native FreeCAD object. They do not replace an
existing feature or guess missing design dimensions. Internal identifiers are
restricted to ASCII letters, digits and underscores, beginning with a letter.

Existing native operations outside this table remain available through FreeCAD,
but are **not implemented/accepted by this new helper layer**. Hole, pipe/sweep,
patterns, fillet/chamfer, ShapeBinder, Assembly joint creation and Assembly solving
are explicitly deferred, not empty wrappers claiming support.

## Stable attachment policy

The default support is a body-local origin plane. A helper-created datum in the
same body is also accepted. Foreign-body support, cross-document support and
arbitrary generated-face references are refused. The property spelling is selected
from the native object's exposed `AttachmentSupport`/`Support` properties;
required attachment properties must actually exist.

There is no `Face17` inference. This reduces reference fragility but does not
claim that every upstream edit is topology-safe. Every intended edit still needs
recompute and affected-feature validation.

## Operational safeguards

New mutations use the existing `session.writer()` GUI-thread/one-writer gate.
They do not start an MCP server, alter network exposure, edit preferences, touch
hardware, save/close user documents or publish repository changes.

A helper failure removes only the exact object it just created, restores the
previous Body tip when applicable, and recomputes. An identity mismatch or failed
cleanup raises `ModelingError` instead of guessing that rollback succeeded.
**This is not a general transaction:** prior successful features in a multi-step
build remain, and native side effects outside the newly created object are not
promised to roll back. Existing user transactions are never committed or aborted
by the helper. New complex builds belong in task-owned scratch documents.

## What verification does and does not establish

Creation gates require a successful sketch solve, fresh object state, a fully
constrained valid closed profile, and valid positive-area per-wire faces. A
completed PartDesign operation must expose one non-null, valid, positive-volume
solid. Invalid/error/touched object states are refused even when FreeCAD retains
a geometrically valid last-good Shape.

`inspect_sketch()` is read-only. Unknown redundancy/conflict information and generic
self/inter-wire intersection information are reported as `None`, not fabricated
zero counts. Remaining degrees of freedom are reported as zero only for a fresh
sketch explicitly reporting `FullyConstrained=True`. This is not a full solver
explanation API. Circle separation checks apply at construction; subsequent
arbitrary edits must be checked again by an appropriate validator.

`solid_metrics()` has the narrow named requirement
`ONE_VALID_POSITIVE_VOLUME_SOLID`. Its PASS is **not** proof of correct dimensions,
hole locations, fit, clearance, printability, strength, or export fidelity. Add
independent task-specific predicates and use the existing frame/geometry/export
helpers for those claims. `recompute_check` checks its specified objects, not the
entire document's design correctness.

## Performance and recovery

Profile/case limits bound helper-side work, not OCCT wall time. A single native
Boolean, loft or recompute can still hang. No hard timeout, native cancellation,
watchdog, restart authority or RPC recovery implementation was added. Use a
separate disposable FreeCAD host for the new acceptance suite; never test a
suspected kernel hang in a production document session.

For sampled edits, read [Parameter testing](parameter-testing.md). Preserve the
existing [Session and recovery](session-and-recovery.md) and
[Modeling and export](modeling-and-export.md) rules.
