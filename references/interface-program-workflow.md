# Durable interface-program workflow

Use this reference when a project spans multiple fit articles or revisions, combines authenticated source assemblies with physical evidence, or needs a fixed-architecture parameter loop and an independent STEP gate. Do not impose this structure on a simple standalone part.

## Durable objects

Keep durable knowledge independent of disposable revision CAD. Names may vary, but the responsibilities should remain distinct:

| Object | Contains | Excludes |
|---|---|---|
| Source/occurrence inventory | Exact source identities, hierarchy, validity, placements, authority, installed/excluded roles | Promoted interface meaning and candidate requirements |
| Interface definition | Registered frame, contact/mount planes, authenticated axes, required empty volumes, direction conventions, provenance | Candidate outline, selector geometry, legacy marks |
| Knowledge ledger | Physical facts, known failures, design targets, retired assumptions | Candidate construction parameters |
| Artifact brief | What the current object must answer, applicable interface, physical test, allowed freedom | Unnecessary modeling recipe |
| Object requirements | Deterministic `PASS` / `FAIL` / `UNVERIFIED` predicates for the artifact class | Candidate-owned requirements and quality preferences |
| Print configuration | Effective machine/material/process used for the physical article | Mechanical interface authority |

Revisions are evidence. They do not automatically become ancestors. A physically passed article contributes only the features its test exercised; a failed article contributes specific negative knowledge without forcing its whole topology into the next design.

For physical inputs, preserve article/variant identity, measurement method, calibration and uncertainty where relevant, governing datums, and measurement-record identity. Propagate those uncertainties into derived interfaces, surrogate/keepout envelopes, fit predicates, and clearance margins.

## Architecture contract

When uncontrolled topology drift has occurred or comparable iteration matters, define:

- fixed structural systems and their count;
- a feature graph mapping every structural feature to a requirement and function;
- named parameters with units, classification, initial values, justified ranges when known, and declared geometry or predicate consumers;
- forbidden topology changes;
- a deterministic topology signature or equivalent construction description.

Ordinary iterations change parameters only. “Fixed” means not tunable in this phase, not physically verified truth. Perturb active parameters at representative values or bounds in disposable outputs and confirm that each changes its declared consumer without changing the frozen topology. Restore the declared baseline or selected candidate, regenerate it, and rerun applicable gates before export; final hashes identify that restored state. Remove duplicated, derived, target-only, retired, or no-op values from the tunable interface. If a feature has no current function or requirement, remove it. If the architecture cannot satisfy authenticated requirements, preserve the evidence of the conflict, mark the architecture unsatisfiable, explicitly define the next version, and continue from the durable interface—not from a patched export.

## Deterministic generator contract

The generator consumes:

`authenticated interfaces + architecture + parameters + applicable requirements`

and produces:

`FCStd/BRep + canonical STEP + print transform + STL + measurements + hashes`

The same inputs must produce geometrically equivalent output. Reusable code may handle datum math, primitive construction, Boolean utilities, exports, and verifier invocation. Do not import or Boolean against rejected historical candidates unless the historical shape itself is an explicitly authenticated interface input.

Declare one regeneration authority: the FCStd dependency graph or an external generator plus state files. If external, label FCStd as a derived snapshot and embed generator, architecture, parameter, and dependency hashes. Record CAD/kernel/runtime versions, all input and imported-module hashes, exact invocation, and controlled export/mesh settings. Treat an exported STEP as an output, never an editable source of truth. A live interpreter cache is not an input file: do not require undeclared session globals or execute a prefix sliced from another generator. Claim deterministic reproducibility only after two independently started clean-process builds from the same manifest, or a clean build compared with a separately preserved prior clean run. Reopen/import every compared FCStd, STEP, and STL from delivered on-disk bytes in fresh documents and compare semantic geometry; byte equality is helpful identity evidence but not the only test.

## Interface construction

An interface states where material must contact, where axes must resolve, and which volumes must remain empty. It should not preserve the historical way an old coupon implemented those facts. For example, a required boss keepout does not require recreating a stepped blind pocket or annular shelf.

Construct the simplest printable clearance that satisfies the empty-volume and fastening requirements. Preserve the keepout, not archaeological topology.

## Whole-assembly context

Build and preserve one persistent master context after upstream registration is authenticated. Inventory exact source documents, component objects, hashes, placements, authority classes, and occurrence roles. Place the current candidate and mating assembly at a clearly labeled candidate relationship.

Before making a “complete assembly” claim, freeze the authoritative root, source hash/revision, pose or sweep range, uncertainty margin, and transform chain, then reconcile all shape-bearing leaf occurrences in the master document. For every stable occurrence path/internal name, record geometry hash, source-geometry validity, units, source/transformed placements, scope/reachability (`INCLUDED` or evidence-backed `EXCLUDED`), and the included collision predicate (`INTENDED CONTACT`, `SEPARATED`, `INTERFERENCE`, `UNEXPECTED CONTACT`, or `UNVERIFIED`). Validity counts must equal the source census; `INCLUDED + EXCLUDED` must equal it; included predicate counts must equal `INCLUDED`. A source-object count alone is insufficient when the master contains transformed copies or context positions. Source-census closure proves completeness only relative to that root: reconcile it against an authenticated configuration/BOM or physical inventory and list omitted fasteners, belts, cables, covers, and envelopes. Any installed/reachable occurrence lacking adequate evidence is `INCLUDED/UNVERIFIED`. Hidden state, visibility, or selection never defines scope; an unreconciled census permits only an explicitly incomplete claim.

Before calling a selector, carriage, cover, gearbox, or similar stock assembly “clear,” evaluate every authenticated component that can reach the candidate. A convenient mating body is insufficient if the physical stock assembly contains covers, screws, gears, cable guides, or neighboring carriage bodies.

For each operand, preserve an independent datum chain:

1. exact source document and object;
2. source BRep identity;
3. nested global placement and shape placement;
4. target transform with source/target frames and units;
5. whether placements were retained or baked;
6. transformed object hash or equivalent geometry identity.

Do not let both operands inherit the same unverified transform simply because that makes their relationship look consistent.

## Verification capability map

Before CAD iteration, make a small table:

| Requirement | Existing verifier operator | Authority if unsupported |
|---|---|---|
| Valid connected solid | supported/unsupported | export prerequisite |
| Mount axes and planes | supported/unsupported | construction assertion or physical gate |
| Required empty volume | supported/unsupported | construction assertion or physical gate |
| Mating-body relationship | supported/unsupported | assembly check or physical gate |
| Mark meaning/readability | usually unsupported | physical gate |

Use only operators the pinned release actually supports. Do not fake-PASS unsupported semantics. A verifier may prove object conformance without proving design quality or real-world fit. If no independent verifier exists, use named native geometric checks and disclose that limitation rather than inventing an independent-verifier PASS.

Declare intended contacts before evaluation. Any undeclared contact is `UNEXPECTED CONTACT` and blocks clearance PASS until classified through a reviewed requirement change. Missing or ambiguous objects, invalid/null BReps, unknown units or placements, unrun predicates, exceptions, timeouts, and failed Boolean/distance operations produce collision result `UNVERIFIED`, never zero. An invalid occurrence may be excluded from a narrowly stated collision scope only through an independent reachability envelope tied to the exact variant, source/hash, enclosure proof, uncertainty budget, pose range, and transform chain; the source-geometry validity remains invalid/unknown. If exclusion is not proved, keep it included and `UNVERIFIED`. Aggregate over included required predicates: `FAIL` if a forbidden or unexpected predicate occurs; otherwise `UNVERIFIED` if any is unverified; otherwise `PASS`. With incomplete coverage, report “no interference found in the verified subset,” not “assembly clear.” If an approved architecture or service-order change changes applicability, freeze and hash a new reviewed requirement bundle before generating and evaluating the next candidate; never alter a bundle after seeing the result to make it pass.

## Controlled automatic loop

Use this loop when the user asks for straight-through execution:

1. compile the approved interface, knowledge, brief, architecture, parameters, and immutable requirements;
2. generate from scratch;
3. export canonical STEP;
4. run the frozen existing verifier, or the frozen named native-check set when no independent verifier exists;
5. inspect numerically any important architecture relationships the verifier cannot express;
6. check the complete authenticated assembly;
7. if a required predicate is `FAIL`, correct only permitted geometry/parameters and regenerate; if it is `UNVERIFIED`, repair provenance, operands, coverage, verifier, or tool state without geometry tuning;
8. if topology repeatedly causes the failure, prove the architecture conflict before defining a new version;
9. after digital PASS, close/reopen/recompute and validate STEP/STL fidelity;
10. update the versioned master-context copy and remove or refresh stale contracts, diagnostics, labels, hashes, and result text;
11. reopen the context and search for old candidate identities or contradictory status metadata;
12. apply the recorded print transform, slice with the effective machine profile, and analyze G-code;
13. emit `READY FOR PHYSICAL TEST` only when every digital prerequisite required for safe test fabrication is `PASS` or explicitly waived without being relabeled PASS.

Do not stop for approval at every arrow unless the user requested staged review. Tool crashes and temporary connection failures are workflow errors to recover from, not engineering outcomes.

CAD/export PASS ends at the hash-identified engineering and print-oriented geometry. Slicing is a separate gate: record `T_print<-engineering`, units/scale, critical-face orientation, tessellation, slicer version, effective merged configuration hash, fabrication machine/nozzle/material identity, warnings, and G-code hash. Static G-code analysis proves only the commands and profile properties it explicitly checks. Any upstream geometry, orientation, tessellation, or configuration change invalidates downstream artifacts. Never upload, queue, or start a print without explicit authorization.

## Physical result ingestion

Link the physical record to exact STEP, STL, G-code, interface, and requirement-bundle hashes. Ask only questions the article can answer. Promote each independently passed fact; preserve each independently failed fact.

If one local item fails while seating, hole alignment, and stiffness pass, correct the local or coupled feature while preserving the passed evidence. Regenerate from the durable interface and architecture inputs rather than editing the printed article’s STEP.

An explicit owner waiver is a workflow decision, not physical evidence. Record it verbatim, retain physical status as unverified, and avoid using the waived article to authorize claims it never exercised. Before continuing, enumerate each dependent datum/claim and its surviving non-waived authority; a waiver cannot fill a missing design-controlling physical datum.
