---
name: freecad-mcp-parametric-cad
description: Design, modify, validate, and hand off trustworthy parametric mechanical CAD through a local FreeCAD MCP workflow. Use for fabricated interfaces, reference-derived parts, fit-check coupons, coordinate frames, export fidelity, collision analysis, physical validation gates, and auditable FreeCAD deliverables. Do not use for purely visual modeling or generic FreeCAD UI help.
---

# FreeCAD MCP Parametric CAD

Use FreeCAD MCP to produce mechanical CAD whose sources, coordinate systems, parameters, exports, and physical validation state remain explicit.

For fabricated interfaces, reference-derived geometry, fit coupons, or substantial design phases, read [trustworthy-mechanical-cad.md](references/trustworthy-mechanical-cad.md) before changing geometry.

## Establish authority before modeling

Classify each input as authoritative vendor/project CAD, community CAD, physically measured geometry, physically validated fit geometry, or a provisional estimate.

Record source URL, repository/ref/blob when available, filename, size, SHA-256, license/notice, and intended role. Preserve source downloads and reference documents; work in derivative documents.

Do not treat source availability as dimensional authority. For a fabricated interface, real hardware outranks a physically validated coupon, which outranks authoritative CAD, community CAD, and visual estimates.

## Define the frame and parameter contract

Before adapter or mating geometry, document the origin and datum features, +X/+Y/+Z, contact plane, travel or functional axis, and source/transformed component frames.

Use named parameters for values expected to change. Keep measured values, source-CAD nominal values, estimates, design clearances, and derived values distinguishable. Every physical value needs a datum, direction, method, uncertainty/confidence, and verification status.

## Gate fabricated interfaces with simple coupons

Use the smallest coupon that can answer the current physical question:

1. validate the source object, face, orientation, units, and transform;
2. create a minimal coupon with durable orientation marks;
3. verify FCStd/BRep to STEP to STL fidelity;
4. physically test it;
5. classify any failure before changing dimensions;
6. promote only the features physically exercised by a PASS;
7. create dependent geometry only after the gate passes.

A failed coupon is useful evidence. Do not enlarge holes, add offsets, or redesign surrounding geometry until the failure is classified as a source, object, face, orientation, transform, export, process, or real-interference problem.

## Separate validation domains

Report intentional mating and fastener contact, static fit, service/tool access, motion envelope, end-of-travel collision, wiring/cable envelope, and manufacturing tolerance separately.

Do not redesign a validated static interface to solve an unmodeled dynamic collision. A small shortfall against a conservative clearance target is a qualified result, not automatically a redesign, when physical testing is the correct next gate.

## Validate deliverables

In proportion to risk, verify non-null geometry, topology appropriate to the object type, units, scale, placement, coordinate persistence, recompute/reopen persistence, printable solidity/manifoldness where required, export fidelity, representative parameter regeneration, and hashes.

Do not fail intentional compounds, shells, faces, or wires merely because they are not solids.

## Preserve evidence and stop gates

Never overwrite passed or failed coupons. Version FCStd, STEP, STL, hashes, renders, physical result, and relevant photographs. Mark rejected or superseded work clearly.

Use explicit states such as `REFERENCE ONLY`, `PROVISIONAL - FIT-CHECK FABRICATION ONLY`, `PROVISIONAL - STATIC FIT-CHECK ONLY`, `PHYSICAL FIT-CHECK PASS`, `PRODUCTION GEOMETRY NOT RELEASED`, and `PRODUCTION RELEASED`.

If a required physical gate has not passed, stop dependent CAD work and list the blocked phases and exact next action.

## MCP boundaries

Use the project-required local FreeCAD MCP connection. Keep RPC loopback-only when configured that way. Do not change unrelated FreeCAD documents, Codex configuration, or MCP entries.

If connectivity is lost, stop safely and request only the minimum recovery action. Do not continue by guessing CAD state.

## Report the engineering state

For significant phases, record objective, source identity, assumptions, frames, parameters, measurements, digital checks, physical gate, PASS/FAIL/CONDITIONAL result, blocked work, and the next exact action. Emphasize engineering evidence rather than RPC ceremony.
