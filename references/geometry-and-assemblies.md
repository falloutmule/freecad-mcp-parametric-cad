# Occurrences, frames and measurements

Use `Frame(name, target_from_world, units='mm')` and `shape_in_frame(top_level_root, 'Nested.Part.', frame)`. Empty path selects root. Paths use internal names, not labels; faces/edges are outside this helper's scope.

The adapter wraps native `Part.getShape(..., retType=2)` and returns a detached shape, source/occurrence identity, accumulated transform and diagnostics. Native shape includes root/parent/object placements: apply only world→target afterward. Column-vector convention: `p_target = T_target<-world * T_world<-source * p_source`. Record matrices row-major.

Supported: Part features, nested App::Part, evaluated PartDesign Body and single Links including nested Parts. Mirrored/scaled/sheared transforms, link arrays, broken links and unknown groups are unsupported/unverified. Link scale can be baked into geometry but absent from the returned matrix; link properties are checked too. Do not silently replace unsupported native resolution with hand-built placement formulas.

`occurrence_paths(root)` inventories evaluated leaves: a Body is one Tip, not its history. Nonshape children need explicit scope handling. Visibility never defines inventory. Repeated links share source identity, not occurrence identity.

`ResolutionScope` reuses only within a read-only operation on saved GUI-unmodified sources; returns copies. Unsaved/headless/modified sources disable reuse, file metadata changes invalidate keys. Discard scope before mutation/external-file activity. No persistent cache; metadata is not authenticity proof.

## Evidence API

Tolerances/requirements are caller inputs, not universal standards.

- `pair_measure`: common solid volume plus pair minimum distance. Declared-contact PASS proves touching/no material overlap only—not footprint, normal or engagement.
- `bounding_separation`: padded-box lower bound, not exact distance. Invalid geometry cannot prove its own exclusion.
- `empty_volume`: intersection across a full required solid keepout, not cylinder-face coverage or sampling.
- `equivalent_solids`: symmetric difference, bounding-box delta and solid count. Check design-specific axes/dimensions too; zero distance is not equality.
- `datum_residuals`: independent caller-supplied anchors. Does not fit registration or prove datum authority.

Registration needs independent anchors and holdouts. A common wrong rigid transform preserves pairwise distance; collision cannot prove world placement. Payload hashes provide traceability, not geometry/physical authority.

## Complete assembly claims

Freeze intended configuration, authoritative root, pose, uncertainty and datum chains. Reconcile occurrences against authenticated assembly/BOM or physical evidence. Each needs inclusion or evidence-backed exclusion; unmatched occurrences remain explicit. Source-tree counts alone do not prove machine completeness.

Separate validity, placement/scope and collision. Excluding invalid geometry requires independently justified enclosure/reachability evidence tied to the exact variant; otherwise include it as unverified. Declare contact pairs before evaluation.

`contracts.aggregate` rejects missing/duplicate predicates. Also reconcile requested occurrence/pair sets and exclusions. Report “12 occurrences accounted for, 4 pairs checked exactly, remaining pairs bounded” when appropriate—not “all pairs checked exactly.” Incomplete coverage supports subset claims only.

Records identify operands, frame, units, tolerance, method, values, coverage and unchecked scope. PASS/FAIL needs a named requirement. Sampled thickness/deviation never proves an unqualified global minimum.
