# Trustworthy mechanical CAD workflow

Use this reference for fabricated interfaces, reference-derived parts, fit coupons, source corrections, assembly context, motion envelopes, or production-release decisions.

## 1. Source provenance and isolation

Prefer authoritative vendor or project repositories. For digital sources, record URL, repository, commit/ref, blob identity, exact archive/file/object, byte size, retrieval time, SHA-256, license/notice, role, and known limitations. For physical sources, record article/variant identity, measurement or scan method, calibration and uncertainty where relevant, governing datums, and measurement-record identity/hash. Propagate physical uncertainty into derived interfaces, surrogate/keepout envelopes, fit predicates, and clearance margins. A hash proves file identity, not dimensional authority. Preserve source files as immutable and never silently replace a STEP, Parasolid, FCStd, or archive.

Verify downloaded and repository-backed CAD is a hydrated binary rather than a Git LFS pointer. Authenticate the upstream provenance and exact object used; do not choose a body by filename proximity or appearance.

For investigation work, distinguish a required base commit from a requested final deliverable commit. Capture the initial full commit and dirty state, enforce any user-specified expected HEAD without changing the repository, and resolve the staging directory to prove it is outside the Git working tree. Use scratch copies of production CAD. Keep reports, temporary FCStd documents, screenshots, manifests, and derived exports in staging. If selected deliverables must enter the repository, audit both working and staged diffs and the proposed commit tree; selective staging does not neutralize unrelated changes already in the index. Do not unstage user work. Stop for reconciliation if a deliverable overlaps dirty user content or cannot be committed without including or excluding it, and verify all other pre-existing changes remain untouched.

## 2. Reference-document discipline

Create preserved reference FCStd documents and separate derivative/working documents. Keep source-object identity and hierarchy where useful. Use self-contained shape copies when the concept must survive without fragile external links. Do not use historical candidate solids as construction geometry merely because they are available.

If a source lacks authenticated fasteners, belts, wheels, or other hardware, do not reconstruct them from generic product knowledge. State the limitation and route the unresolved fact to physical testing or an independently sourced measurement.

## 3. Coordinate systems and transform contracts

Define the engineering frame before designing an adapter. Prefer functional datums such as an official mount plane, physical seating face, machine-up direction, bearing/wheel axes, hole-pattern centroids, travel axes, or tooling surfaces over candidate faces and arbitrary outline corners.

Record origin, positive axes, right-handed construction, mating plane, travel axis, source and target frames, and signed distances. If two convenient directions over-constrain the frame, derive the third with a cross product and measure the remaining sign rather than asserting it.

Represent transforms as `T_target<-source` in millimetres. Record nested parent placement, object placement, `Shape.Placement`, and any baked-transform policy. Validate the 4×4 homogeneous last row, rotation orthogonality, determinant near +1 for a rigid non-mirrored placement, and absence of unintended scale or shear. If mirroring is intentional, name it and do not hide the negative determinant.

Use independently derived datum chains for candidate and reference operands when a shared transform error could make a collision result look consistent.

## 4. Parametric architecture

Use named parameters for dimensions likely to change. Separate physical measurements, nominal source-CAD values, provisional estimates, design/process allowances, derived dimensions, and quality targets.

When topology must remain stable across iteration, freeze an architecture contract containing its structural systems, feature graph, allowed parameters, service-order assumptions, invariants, and forbidden topology changes. “Fixed” means not tunable in this phase, not physically verified truth. Give active parameters units, classification, baseline, justified bounds when known, and declared consumers. Representative bound or perturbation tests in disposable outputs must show that each active parameter changes the intended geometry or predicate without changing frozen topology. Restore the declared baseline or selected candidate, regenerate it, and rerun applicable gates before export; final hashes identify that restored state. Duplicated, derived, target-only, retired, and no-op values do not belong in the tunable interface. Generate deterministically from authenticated interfaces plus that contract. If parameter tuning cannot satisfy the requirements, record the proven conflict before defining a new architecture version.

Do not manually patch exported STEP files. Do not let a parameter remain advertised as effective after numerical testing shows it does not change the resulting solid.

## 5. Durable project knowledge

For multi-revision work, separate the permanent interface and knowledge from disposable candidate shapes. Useful knowledge classes include:

- `PHYSICAL_FACT`: exercised by real hardware or an accepted physical article;
- `KNOWN_BAD`: a specifically documented failure condition;
- `DESIGN_TARGET`: a chosen margin or preference that is not yet a physical law;
- `RETIRED`: a source, transform, assumption, feature, or architecture no longer allowed to control new work.

Requirements reject unacceptable objects. Quality metrics help choose margin. Do not promote a convenient historical dimension or a verifier proxy into a requirement without explicit authority.

## 6. Physical evidence hierarchy

For fabricated fit, use this default authority order for the feature at issue when the evidence quality supports it:

`real hardware > physically exercised article > authenticated source CAD > reference-only/community CAD > visual estimate`

A lower-ranked source may provide packaging context but cannot override better, repeatable physical evidence for the controlling interface. Mere possession or an uncalibrated photograph is not superior dimensional evidence. A physical PASS promotes only what the test exercised.

A correlated photograph may identify which physical face is involved. Unless calibrated for the measurement at issue, it does not establish dimensions, stand-off, depth, or lateral handedness.

## 7. Focused physical gates

Before a complex adapter, identify the next physical unknown and build the smallest robust article that answers it. Do not carry legacy contours, marks, or downstream geometry into the article without a current function.

After a failure, distinguish a local feature error from an architectural conflict. Preserve individually passed evidence; regenerate from the durable interface while changing only the failed or coupled feature. Do not redesign a sound architecture because one mark is wrong.

A user may explicitly waive a confirmation witness article. Record the waiver and exact risk accepted; do not label it a physical PASS or promote untested features. Enumerate every dependent datum/claim and its surviving non-waived authority before continuing, so the record proves the witness was confirmatory. A waiver cannot supply an unknown physical datum that controls the next design.

## 8. Diagnose the right failure

Classify failures as wrong source/variant, wrong assembly object, wrong physical face, reversed orientation, transform/placement error, candidate architecture conflict, parameter error, export/mesh error, slicer/process issue, or real interference.

Compare source coordinates through parametric model, BRep, STEP, print transform, STL, and G-code before changing a hole, stand-off, or clearance. Do not trial-and-error the wrong variable.

## 9. CAD/export fidelity and FreeCAD state

For critical fit checks, validate `FCStd/BRep -> STEP -> print transform -> STL`. Check non-null geometry, appropriate topology, placement, scale, units, printable mesh solidity/manifoldness, and close/reopen/recompute persistence. Freeze each comparison method and tolerance before seeing its result. Use a meaningful STEP/BRep metric such as symmetric difference when distance zero alone could merely indicate touching or overlap; do not demand literal representation or byte equality. For STL, use a named mesh-to-source deviation metric and threshold in addition to manifoldness and controlled tessellation. Record exact export lineage and settings.

Intentional compounds, shells, faces, wires, and reference geometry are valid when appropriate. Require a solid only when the deliverable is supposed to be a solid.

Treat persistent FreeCAD sessions and copied context documents as untrusted mutable state. Inventory open documents and unsaved state; never rely on `activeDocument`, selection, labels, visibility, or a same-name document resident in memory. FreeCAD document labels are not reliable identity. `newDocument()` can suffix a duplicate name, and `openDocument()` can resolve to an already-open document. For persistence tests:

1. record canonical file path and expected object name;
2. close only a task-owned derivative document whose canonical path is that exact path; if unrelated or unsaved work collides by internal name, abort this session path and use a clean process;
3. reopen the canonical file;
4. assert `Document.FileName` and object identity;
5. recompute;
6. compare the reopened shape to the pre-save shape and the exports.

## 10. Collision evidence and complete assemblies

Separate intentional mating contact, static fit, local component clearance, fastener/tool access, motion envelope, end-of-travel hardware, belts, cable flex, and manufacturing tolerance.

When a claim concerns a stock assembly, freeze the authoritative root, source hash/revision, evaluated pose or sweep range, uncertainty margin, and transform chain. Inventory and hash the authenticated components and check the complete relevant installed assembly—not only the convenient mating body. Source-census closure proves completeness only relative to that root; reconcile it against an authenticated configuration/BOM or physical inventory and list omitted fasteners, belts, cables, covers, and envelopes. Reconcile every shape-bearing leaf occurrence, not merely each unique geometry, against a machine-readable ledger. For each stable path/internal name, record geometry hash, source-geometry validity, units, source/transformed placements, scope/reachability (`INCLUDED` or evidence-backed `EXCLUDED`), and the included collision predicate (`INTENDED CONTACT`, `SEPARATED`, `INTERFERENCE`, `UNEXPECTED CONTACT`, or `UNVERIFIED`). Validity counts must equal the source census; `INCLUDED + EXCLUDED` must equal it; included predicate counts must equal `INCLUDED`. Any installed/reachable occurrence lacking adequate evidence is `INCLUDED/UNVERIFIED`. Hidden state or GUI selection never defines scope. An unreconciled census permits only a narrower, explicitly incomplete claim. Preserve the current candidate placement as a candidate relationship rather than validated truth.

Classify collision operands:

- authenticated source solid or authenticated fastener present in source;
- physically correlated geometry;
- reference-only screen or conservative envelope;
- constructed design keepout/tool approach;
- unsupported or guessed geometry.

Only geometry with adequate authority may block the corresponding fabrication decision. Conservative reference-only wheel or belt screens are normally informational until correlated. A tool-access cylinder constructed by the designer is a design keepout, not upstream source truth.

Declare intended contacts before evaluation. Any undeclared contact is `UNEXPECTED CONTACT` and blocks clearance PASS until classified through a reviewed requirement change. Missing or ambiguous objects, unknown units or placement, unrun predicates, exceptions, timeouts, Boolean/distance/kernel failure, invalid BRep, or missing components produce collision result `UNVERIFIED`, never zero. An occurrence may retain invalid/unknown source-geometry status while an independent reachability proof excludes it from a narrowly stated collision scope. The exclusion record must identify the alternate envelope source/hash, exact variant correlation, enclosure proof, uncertainty budget, pose range, transform chain, and passing exclusion predicate; a box computed only from the same invalid BRep is not independent. If exclusion is not proved, keep the occurrence included and its collision predicate `UNVERIFIED`. Aggregate over all included required predicates: `FAIL` when a forbidden or unexpected result exists; otherwise `UNVERIFIED` when any is unverified; otherwise `PASS`. With incomplete coverage, say “no interference found in the verified subset,” not “assembly clear.” Keep geometry integrity, static collision, motion, slicing, and physical-fit statuses separate. `CONDITIONAL` may describe a decision but must cite its underlying predicate states.

## 11. Clearance and structural material

Distinguish intentional contact, nominal model clearance, conservative-envelope clearance, design target, known-bad condition, and physically verified clearance. Record achieved value and target separately.

A documented failed ligament prohibits recurrence of that failure condition; it does not prove the next larger value passes or turn a later target into a universal minimum. Prefer an architecture that eliminates an accidental tangent bridge. Numerically inspect hole-to-edge, hole-to-window, and keepout-to-material relationships so partial holes, edge breakouts, and isolated slivers are intentional or absent.

## 12. Fasteners and service order

Check tool approach, nut access, head clearance, wheel access, assembly order, removable hardware, and structural material around openings. Use simple constructed clearance volumes rather than invented tool models.

Explicitly classify every fastener axis near raised structure as deliberate through-access or completely outside that structure. Avoid near-tangent edges and accidental half-holes. If the selector or cover is removable for service, record the service order rather than preserving incompatible full-height access material.

## 13. Orientation marks and print orientation

Use obvious, durable, functional marks only when physical orientation is otherwise ambiguous. Document their meaning. If the authoritative marked face prints against the bed, make the geometry robust to first-layer contact or add a redundant functional edge cue without changing the validated interface.

## 14. External verifier discipline

Create a small capability map from each applicable object requirement to an operator supported by the pinned verifier release. Unsupported facts remain construction assertions or physical checks. Do not expand the verifier during an ordinary object iteration unless a genuinely blocking requirement cannot otherwise be evaluated.

Freeze expected canary outcomes before running a new verifier implementation. Candidate-side files must not alter the approved requirement bundle or reference identities. If a reviewed architecture or service-order change changes requirement applicability, freeze and hash a new bundle before evaluating the next candidate. Never tune applicability or tolerances after observing a result to manufacture PASS. Kernel/reference failures fail closed to `UNVERIFIED`. If no independent verifier exists, use named native geometric checks and disclose the limitation rather than inventing an independent-verifier PASS or blocking ordinary CAD solely on its absence.

A deterministic verification ID should hash semantic evidence such as candidate, verifier/runtime, bundle/reference identities, rule IDs/results, and normalized measurements. Exclude timestamps, durations, absolute paths, PIDs, temporary names, and host metadata.

## 15. Print handoff

Record one explicit `T_print<-engineering` transform, units/scale, critical-face orientation, and tessellation settings; validate the print-oriented STEP/STL against them. CAD/export PASS ends at hash-identified engineering and print-oriented geometry. Slicing is a separate downstream gate and does not prove fit, strength, collision clearance, serviceability, or physical release. Use the actual physical printer identity separately from the mechanical donor or source-machine identity.

Record effective nozzle, material, temperatures, bed/build volume, layer height, walls, top/bottom layers, infill, supports, extrusion mode, start/end G-code, and any setting substitutions. Preset lineage supplies defaults but does not redefine the machine.

Analyze the generated G-code for scale, extrusion bounds, bed limits, layer count, temperatures, supports, extrusion mode, homing, shutdown, and unresolved blocking warnings. Static G-code analysis proves only the commands, bounds, and effective profile properties it explicitly checks. Treat informational warnings as informational. Do not interpret missing filament metadata reported as `0 g` as a zero-material print. Any upstream geometry, print orientation, tessellation, or effective configuration change invalidates downstream artifacts; never upload, queue, or start a print without explicit authorization.

## 16. Versioned evidence and states

Never overwrite passed or failed articles. Preserve versioned generator/parameters, explicit dependency hashes, FCStd, STEP, STL, G-code, hashes, renders, reports, physical record, and relevant photographs. Keep a persistent complete-machine context once its upstream registration is established.

When replacing a candidate in a context copy, treat embedded metadata as part of the artifact. Update or visibly quarantine stale context contracts, diagnostic intersections, object labels, source hashes, status properties, derived measurements, and summary text. After reopening, search the document for old candidate hashes and contradictory PASS/FAIL language before calling the context current. Conflicting embedded and external state makes the affected claim `UNVERIFIED` until the exact file is closed, reopened, recomputed, and rechecked.

Use explicit states such as `REFERENCE ONLY`, `CANDIDATE RELATIONSHIP`, `PROVISIONAL`, `UNVERIFIED`, `DIGITAL OBJECT PASS`, `PHYSICAL TEST WAIVED BY OWNER`, `PHYSICAL PASS`, `READY FOR PHYSICAL TEST`, `PRODUCTION GEOMETRY NOT RELEASED`, and `PRODUCTION RELEASED`.

## 17. MCP execution and recovery

Use the required local FreeCAD MCP connection and make a read-only health call before CAD work. Verify FreeCAD/MCP versions, intended document, object, and file path. Keep RPC loopback-only when configured that way.

Run document mutation, GUI actions, recompute, and save on the GUI thread. Use asynchronous MCP execution only for background-safe calculations that do not touch documents or GUI state.

Do not make a persistent Python session part of the generator's hidden input. Avoid undeclared `builtins` caches, in-memory-only source bodies, and `exec` of sliced source text. Declare one regeneration authority: the FCStd dependency graph or an external generator plus state files. If external, label FCStd as a derived snapshot and embed generator, architecture, parameter, and dependency hashes. Put reusable construction code in explicit modules. A significant build manifest records CAD/kernel/runtime versions, every input/import hash, exact invocation, and controlled export/mesh settings. Claim deterministic reproducibility only after two independently started clean-process builds from the same manifest, or a clean build compared with a separately preserved prior clean run. Reopen/import every compared FCStd, STEP, and STL from delivered on-disk bytes in fresh documents and compare semantic geometry; matching byte hashes alone are not sufficient proof.

If connectivity is lost, recover only the minimum needed state. Do not guess which document is active or continue against a stale copy. Tool crashes are workflow errors, not engineering PASS or FAIL.

## 18. Stop gates and phase reports

Every required `FAIL` or `UNVERIFIED` blocks dependent stages and release claims. A `FAIL` may trigger permitted geometry or parameter correction; `UNVERIFIED` requires provenance, operand, coverage, verifier, or tool-state recovery and must not trigger geometry tuning. Continue independent work and safe automatic repairs when the user requested a straight-through workflow. Emit `READY FOR PHYSICAL TEST` only when every digital prerequisite required for safe test fabrication is `PASS` or explicitly waived without being relabeled PASS. Stop at the next required physical action, a missing physical fact that controls the design, contradictory authenticated requirements, or an unresolved required failure/uncertainty outside scope.

For significant work, report objective, source identities, frames/transforms, architecture and parameter identities, measurements, verifier capability and results, whole-assembly limitations, export/print fidelity, hashes, physical status, blocked downstream work, and the next exact action. Emphasize evidence rather than screenshots or RPC ceremony.
