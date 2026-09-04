---
name: freecad-mcp-parametric-cad
description: Design, modify, validate, and hand off trustworthy parametric mechanical CAD through a local FreeCAD MCP workflow. Use for fabricated interfaces, reference-derived parts, fit coupons, coordinate frames, complete-assembly context, export fidelity, collision analysis, physical gates, and auditable CAD deliverables. Do not use for purely visual modeling or generic FreeCAD UI help.
---

# FreeCAD MCP Parametric CAD

Use FreeCAD MCP to produce mechanical CAD whose authority, frames, construction choices, exports, and validation state remain explicit.

For fabricated interfaces, source-derived geometry, fit coupons, collision claims, or production-release decisions, read [trustworthy-mechanical-cad.md](references/trustworthy-mechanical-cad.md) completely before changing geometry. For multi-revision interface programs, fixed-architecture parameter loops, complete-assembly contexts, or independent STEP gates, also read [interface-program-workflow.md](references/interface-program-workflow.md).

## Establish authority and protect the workspace

Classify source CAD, physical evidence, constructed keepouts, design targets, and unsupported estimates separately. Digital inputs need exact file/object provenance and hashes. Physical inputs need article identity, datums, method, calibration/uncertainty where relevant, and a measurement-record identity. Propagate physical uncertainty into derived interfaces, keepouts, predicates, and clearance margins. Evidence authority is feature-scoped; mere possession or a photograph is not superior dimensional evidence.

For repository-backed work, distinguish a required base commit from a requested deliverable commit. Record the initial full commit and both working/staged dirty state. Honor an expected-HEAD gate without changing the repository to reach it. Use scratch copies of production CAD and keep investigative artifacts outside the Git tree when isolation matters. Verify FCStd, STEP, and archive inputs are hydrated binaries, not Git LFS pointer text. If a deliverable must enter a dirty repository, follow the staged-diff, overlap, and proposed-tree safeguards in the detailed reference.

Do not synthesize absent fasteners, belts, wheels, or other hardware from generic machine knowledge.

## Define frames before geometry

Derive the engineering frame from authenticated functional datums such as an official mount plane, machine-up direction, travel axis, and outward contact normal—not from a candidate adapter face. State a right-handed origin and axes, then measure rather than assume any remaining functional sign.

Define every transform as `T_target<-source`, with units, source/target frames, nested parent/object/shape placements, and baked-transform policy. Check the homogeneous last row, rotation orthogonality, determinant, scale, and shear. A correlated photograph may establish face identity only unless separately calibrated for dimensions or handedness.

## Preserve knowledge and freeze architecture deliberately

Treat historical solids as evidence unless their architecture was explicitly validated for reuse. Keep interfaces, physical facts, known failures, design targets, retired assumptions, and disposable candidates distinct. A documented failed dimension proves that failure case; it does not prove the next increment passes or make a later target mandatory.

When topology drift would make iterations incomparable, define a feature graph and architecture contract. Ordinary corrections change named parameters only. Active parameters need units, classification, baseline, justified bounds when known, and declared consumers. Test their sensitivity in disposable outputs, then restore and reverify the selected state. No-op, duplicated, derived, target-only, and retired values are not tunable inputs. Prove a specific conflict before declaring an architecture unsatisfiable or defining its successor. Never patch an exported STEP manually.

## Use physical gates honestly

Use the smallest robust article that answers the next unknown physical question. Preserve individually exercised PASS evidence and change only a failed or coupled feature. A physical PASS promotes only what the test exercised.

An owner may waive a confirmation witness. Record `PHYSICAL TEST WAIVED BY OWNER`, enumerate every dependent datum/claim and its surviving non-waived authority, never relabel the waiver as PASS, and never use it to supply a missing design-controlling physical datum.

## Make evidence and collision claims fail closed

For complete-assembly claims, establish the intended installed configuration as well as the authenticated CAD root. Use the occurrence-census, independent-transform, predeclared-contact, reachability/exclusion, and aggregation procedure in the detailed reference. Source-geometry validity, scope/reachability, and collision result are separate fields. Every installed or reachable occurrence must be included or excluded with adequate evidence; hidden state and GUI selection never define scope.

Missing identity, units, placement, operands, coverage, or supported calculations—and invalid BReps, exceptions, kernel failures, and timeouts—produce `UNVERIFIED`, never zero geometry. A required `FAIL` or `UNVERIFIED` blocks dependent stages. `FAIL` may trigger permitted geometry correction; `UNVERIFIED` requires evidence, identity, coverage, verifier, or tool-state repair and must not trigger geometry tuning. Incomplete coverage supports only a narrower statement such as “no interference found in the verified subset.” Keep object integrity, static collision, motion, slicing, and physical-fit states separate.

## Use verifiers without inventing proof

Map each requirement to an operator demonstrably supported by the pinned verifier release. Unsupported semantics remain construction assertions or physical checks. Keep requirement bundles immutable from candidate-side files; review and freeze any legitimate applicability change before evaluating the next candidate. Never change a requirement after seeing a result to manufacture PASS.

If no independent verifier exists, use a frozen, named set of native geometric checks and disclose that limitation. Do not invent an independent-verifier PASS or block ordinary CAD solely because such a tool is absent.

## Use FreeCAD deterministically

Make a read-only MCP loopback health call before CAD work and verify FreeCAD/MCP versions, the intended object, canonical file path, open documents, and unsaved state. Never rely on `activeDocument`, labels, selection, visibility, or a same-name in-memory document. Close only a positively identified task-owned derivative at the exact path; if identity or ownership is ambiguous, use a clean process and leave unrelated user documents untouched.

Declare exactly one regeneration authority: the FCStd dependency graph or an external generator plus state files. External generation makes FCStd a derived snapshot. Use explicit files/modules and a hash-closed manifest covering inputs, imported code, architecture, parameters, CAD/kernel/runtime versions, invocation, and export/mesh settings. Do not depend on interpreter globals, `builtins` caches, in-memory-only sources, or sliced-source `exec`. When claiming deterministic reproducibility, compare on-disk reimports from two independent clean-process builds as described in the detailed reference.

Keep document mutation, recompute, GUI actions, and save on the FreeCAD GUI thread. Use asynchronous execution only for background-safe calculations on already-fetched shapes.

## Validate and hand off

In proportion to risk, verify topology, placements, units/scale, recompute/reopen persistence, and tolerance-bounded FCStd/BRep-to-STEP equivalence with methods and thresholds frozen before evaluation. Verify STL with a named mesh-to-source deviation metric as well as controlled tessellation and manifoldness. Update or quarantine stale contracts, diagnostics, hashes, labels, measurements, and status text in every copied master context; contradictory embedded state makes the affected claim `UNVERIFIED` until reopened and rechecked. Renders support inspection but are not conformance evidence.

For print handoff, record `T_print<-engineering`, units, orientation, tessellation, effective machine/material/process configuration, and G-code checks. CAD/export, slicing, G-code, and physical release are separate gates. Any upstream geometry, orientation, tessellation, or effective-configuration change invalidates downstream artifacts. Never upload, queue, or start a print without explicit authorization.

Continue automatically through safe requested digital repairs. Emit `READY FOR PHYSICAL TEST` only when every prerequisite required for safe test fabrication is `PASS` or explicitly waived without being relabeled PASS. Stop when the next action is genuinely human, a controlling physical fact is missing, authenticated requirements conflict, or a required failure/uncertainty cannot be resolved within scope. Report the engineering outcome, not tool ceremony.
