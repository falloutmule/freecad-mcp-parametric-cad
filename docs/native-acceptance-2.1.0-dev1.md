# Native acceptance — 2.1.0.dev1

## Outcome

The 2.1.0.dev1 upgrade was native-accepted on 2026-09-13 before publication. Tests ran in fresh, isolated FreeCAD GUI processes. The tested payload was then installed and rerun from its installed location with zero failures, errors, or skips and unchanged document inventories.

The upgrade is an overlay on clean source commit `0d6399606812df75acb9a38fc50c46975dae0f64` (tree `298fc9b060369113da6c7eb1549f81889cc1f2cf`). The preserved native-accepted bundle has SHA-256 `f8fbf88635b53fed7e497fd4fa557d298014f50080acb52a8e20e80f1fc99b7d`.

## Test matrix

| Gate | Review copy | Installed path |
| --- | ---: | ---: |
| Unit and mocked-backend suite | 73 PASS | 73 PASS |
| New native modeling suite | 19 PASS | 19 PASS |
| Original native regression suite | 26 PASS | 26 PASS |
| Installer regression suite | 17 PASS | 17 PASS |
| Skill metadata validator | PASS | PASS |

Runtime: FreeCAD 1.1.3 build `145529fe741292ff0b3977a01195bf0247425794`, Python 3.11.14, OCCT 7.8.1, with the GUI available. Each task-owned process started from an empty isolated profile and was stopped only after its document inventory was empty. An unrelated existing FreeCAD process was left untouched.

## Acceptance repairs

Three acceptance findings were repaired before the final clean run:

1. The installer rollback-injection test now matches path components portably, so the intended second-write failure is exercised on Windows.
2. The native attachment assertion now handles FreeCAD 1.1.3's list-of-tuples `AttachmentSupport` representation. A focused probe confirmed the production helper selected the correct Body-local origin plane; production attachment code did not change.
3. Package provenance now distinguishes the source commit from its tree identity.

The repository payload keeps the exact accepted runtime and test bytes. This record is release documentation and is not part of the native execution path.

## Evidence scope

Native evidence covers constrained rectangles and circles, typed parameters, Body-local origin and datum attachment, Pad/Pocket, Revolution/Groove, additive/subtractive Loft, sampled parameter edits and restoration, FCStd reopen/edit, STEP round trip, plus the original occurrence/frame, geometry, export, recovery, and unsaved-sentinel regressions.

Still unsupported by this helper layer: native Hole, pipe/sweep, linear/polar patterns, fillet/chamfer, ShapeBinder, Assembly joint creation/solving, generated-face attachment, hard kernel cancellation, and continuous parameter-domain proof.

This is operational CAD evidence for the stated runtime and tested scope. It does not establish a specific product's fit, strength, printability, slicer result, or physical manufacturing readiness.
