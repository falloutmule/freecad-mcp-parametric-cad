# Trustworthy mechanical CAD workflow

Use this reference for fabricated interfaces, reference-derived parts, fit coupons, source corrections, motion envelopes, or production-release decisions.

## 1. Source provenance

Prefer authoritative vendor or project repositories. Record URL, repository, commit/ref, blob identity, filename, byte size, retrieval time, SHA-256, license/notice, and role. Treat a generated hash as provenance, not proof of dimensional authority. Preserve downloaded source files as immutable and never silently replace a STEP, Parasolid, or archive.

If a source is community-authored, say so. If a design uses physically measured replacement geometry, retain the source CAD for non-critical context but mark which interface features no longer depend on it.

## 2. Reference-document discipline

Create preserved reference FCStd documents and separate derivative/working documents. Keep source-object identity and hierarchy where useful. Use self-contained shape copies when the concept must survive without fragile external links. Do not destroy source/reference hierarchy merely for convenience.

## 3. Coordinate systems before geometry

Define the reference frame before designing an adapter. Prefer functional datums such as contact planes, bearing or wheel axes, hole-pattern centroids, travel axes, or tooling surfaces over arbitrary outline corners.

Record the origin, positive axes, mating plane, travel axis, transformed component frame, and roll/pitch/yaw convention. Put the same definitions in the FreeCAD document and report.

## 4. Parametric design

Use named parameters for dimensions likely to change. Separate measured physical values, nominal source-CAD values, provisional estimates, design clearances/process allowances, and derived dimensions.

Do not silently bake a rough physical estimate into production geometry. Regenerate representative scenarios after changing major parameters and return the document to its declared baseline.

## 5. Physical evidence hierarchy

For fabricated fit, use this default authority order:

`real hardware > physically validated coupon > authoritative CAD > community CAD > visual estimate`

A lower-ranked source can still provide packaging context. It cannot override contradictory physical evidence for a controlling interface.

## 6. Cheap fit-check gating

Before a complex adapter:

1. validate the source geometry and selected object;
2. make the simplest coupon that answers the immediate question;
3. physically fit it;
4. correct only the demonstrated mismatch;
5. promote the validated features;
6. make a secondary coupon for the real mating component;
7. create production geometry only after the secondary gate passes.

The primary coupon should usually contain only the contact face, candidate fasteners, unavoidable reliefs, and orientation/datum marks. Do not add downstream geometry to a source-validation coupon.

## 7. Diagnose the right failure

When a coupon fails, classify whether the cause is the wrong source model or variant, wrong assembly object, wrong face, reversed orientation, transform/placement error, export/mesh error, printer/process compensation, or actual mechanical interference.

Compare source coordinates through parametric model, BRep, STEP, and STL before changing a hole or offset. Do not trial-and-error the wrong parameter.

## 8. CAD/export fidelity

For critical fit checks, validate `FCStd/BRep -> STEP -> STL`.

Check null geometry, appropriate topology, placement, scale, units, printable mesh manifoldness, and close/reopen/recompute persistence. Use tight digital tolerances to detect pipeline movement; do not confuse them with manufacturing tolerances.

Intentional compounds, shells, faces, wires, and reference geometry are valid when appropriate. Require a solid only when the deliverable is supposed to be a solid.

## 9. Collision hierarchy

Analyze static interface fit, local component clearance, service/tool access, motion envelope, end-of-travel hardware, wiring/cable flex, and manufacturing/assembly tolerance separately.

Use validated geometry for any collision conclusion that controls fabrication. Do not optimize a static interface around a hypothetical dynamic obstruction.

## 10. Clearance policy

Distinguish intentional mating contact, fastener contact, nominal model clearance, conservative-envelope clearance, and physically verified clearance. Record the actual result and target separately.

If a conservative target is missed slightly but there is no intersection, choose the next gate based on risk. A physical confirmation may be more informative than redesigning from an intentionally oversized envelope.

## 11. Orientation marks

Add obvious, durable marks to every orientation-sensitive coupon. Document each mark in the FCStd properties, render, report, and physical instructions. Use marks that remain understandable after flipping or rotating the part.

## 12. Versioned evidence

Never overwrite passed or failed coupons. Preserve versioned FCStd, STEP, STL, hashes, renders, physical result, and photographs where privacy permits. Mark superseded/rejected work and state what evidence remains useful.

## 13. Manufacturing-state labels

Use explicit state labels. A digital collision PASS does not imply fabrication or production release. Fit-check material, production material, and final loading assumptions are separate decisions.

## 14. Physical-measurement discipline

Record each measurement with value, datum, axis/direction, method, uncertainty or repeatability, confidence, and physical-verification state. If the datum is unresolved, say so.

For hole-center spacing, use known pins, bolts, or drill shanks and calculate from outside-to-outside or inside-to-inside measurements when that improves accuracy. Do not report a successful modeled clearance-pocket size as a measured hardware dimension unless the hardware was actually measured.

## 15. Scanner and photograph measurement

Prefer a flat scan when a part can lie in the controlling plane. Put independent X and Y calibration references in that same plane. Use scans for in-plane outline and feature evidence only.

For photographs, center the camera, increase distance to reduce perspective, include calibration in the same plane, and rectify only when a calibrated method is documented. Do not infer depth, bends, embossments, or stud height from a 2D image; use calipers or depth measurement.

## 16. Fastener and interface design

Check tool approach, nut access, head clearance, bearing/wheel access, assembly order, removable hardware, and structural material around holes. Use simple clearance volumes for tool axes and removal space rather than invented tool models.

Prefer a serviceable interface. Do not preserve one inconvenient stock fastener when that makes the adapter substantially weaker or harder to assemble, unless the project explicitly requires it.

## 17. Scoped physical promotion

A physical PASS promotes only the features actually exercised: for example, a contact plane, hole pattern, boss relief, or orientation. Unencountered outlines, depths, belt paths, and neighboring assembly objects remain at their prior authority level.

## 18. Stop gates

If the current physical gate has not passed, stop. List the blocked phases and exact next action. Do not build motion sweeps, production adapters, tooling, or downstream structures merely because CAD can continue.

## 19. MCP safety

Use the required FreeCAD MCP connection and keep it local-only when configured that way. Verify paths and versions instead of assuming them. Preserve unrelated open documents and configuration.

If RPC connectivity is lost, stop safely and provide only the minimum recovery instruction. Reconnect and verify the intended document before resuming.

## 20. Phase reports

For significant work, create a concise report containing objective/deliverables, source identity/authority, assumptions, frames, parameter and measurement state, digital checks/export fidelity, physical gate, manufacturing label, PASS/FAIL/CONDITIONAL result, blocked work, and the next exact action.

Report MCP or FreeCAD failures only when they materially affect the result.
