# Three claims and two kinds of success

| Claim | Evidence required | Insufficient evidence |
|---|---|---|
| Free motion | Positive neutral manufacturing gaps; actual pose geometry; unintended intersections checked along useful motion; release-layer review | Valid solids, one static pose, a slicing completion message |
| Retention | Closed retaining topology, cap/hoop/guide material containment, plausible axial/radial/diagonal/tilt escape analysis | One blocked push, zero collision during rotation, attractive cap outlines |
| Pose holding | Deliberate friction/cam/detent mechanism; intended contact survives play; room for compliance; physical feedback | Retention, centered overlap alone, an arbitrary interference anywhere in the limb |

Keep three separate statuses. `joint_claims` returns no aggregate PASS while a required claim is UNVERIFIED. Free hinges may have holding NOT_REQUESTED, but cannot be advertised as holding gravity poses. Product appearance and mechanical validity are also independent; valid CAD can fail the character brief.

## Capture protocol

Resolve parent, child, witnesses and datum axes into one authoritative frame through `fcskill.frames`. For the capped-hinge family verify two complete integral cap disks, a complete child hoop across the bearing width, two closed guide lands and one connected solid per body. Compare actual final material with witness volumes after every clothing clearance cut. Tiny numerical tolerances are reported in mm³; they are not permission for an open half-ring.

For a teardrop bore of radius r, the apex reaches r√2, and a conservative maximum opening span is r(1+√2). Guide-constrained center play can conservatively use clearance × √2. Bound tilt from two guide locations separated by span L using atan(2×play/L); require the projected cap diameter to exceed both the physical opening and the witness hoop opening. Reference limb values: approximately 15.15° bound, 8.88 mm projected cap, 8.60 mm witness aperture and 7.24 mm bore opening. These describe the particular closed geometry. A projection number does not save missing material.

The helper uses an interior 0.001 mm guide witness inset to avoid coincident-face Boolean ambiguity and includes that inset in its conservative play/span calculation. Its full hoop and guide witnesses are sufficient geometry evidence for rigid undeformed capped hinges, not a proof for open sockets, flexible tabs, arbitrary bearings or fracture under force. Reject unsupported dimensions instead of lowering witness coverage requirements. Test deliberate half-cap and slit-hoop defects. A valid connected damaged solid must still fail capture.

At useful joint angles transform the actual child and its witness material together. Re-evaluate connectivity/capture after any non-rigid geometry change. Check cumulative compound poses for interference between unrelated bodies. Capture under elastic deformation, strength and pull-out force need separate physical evidence.

## Holding/contact protocol

Rotate actual solids about actual axes. Classify an overlap as intended only if it lies in **both the actual cam and the actual follower**. Intersections in a large named “joint region” are not automatically permitted. With rigid CAD leaves, intended overlap models elastic deflection; it is not an unintended-body collision, but it must fit the chamber and be physically credible.

Check radial bearing offsets, axial float and tilt that could bypass the cam or disengage a narrow leaf. State grid pitch, angle step, contour tessellation/erosion and tested ranges. The reference used 5° angles, 0.02 mm planar offset pitch and a separate conservative enlarged-offset/tilt analysis. Its finite result is not continuous proof or FEA. The reusable fixture's centered contact sweep is a regression test, not replacement evidence for offset-robust holding in a new product.

## Semantic poses

Use a directed rigid-body graph, explicit centers/axes and limits. All rest coordinates must use one frame; compose parent transform with child-local rest-axis rotation. Do not alter geometry to make a test pose look collision free.

- Standing: feet approximately level, legs descend beneath hips, head above torso, balanced-looking silhouette. Assess center of mass/support polygon separately if claiming freestanding stability.
- Sitting: both thighs extend forward with substantial hip flexion and both shins descend with substantial knee flexion. The reference uses hips +90°, knees −90°. Merely spreading the legs or rotating the whole model is not sitting.
- Raised arm: the hand visibly rises above the shoulder, with a recognizable arm and clearance to head/body. The reference uses the canted right shoulder at 170°. A head collision is not a completed gesture.

`semantic_checks` supplies ordinary-humanoid landmark cues in engineering coordinates; it always requires visual review and reports collision status UNVERIFIED. Adapt explicit thresholds for unusual characters; do not weaken them after a failed pose merely to obtain PASS. Keep intended contact, endpoint collision checks and sampled path checks separate. Record at least the chosen step (reference 5°) and number of samples; refine near collisions if needed, without claiming continuity.

## Native, export and manufacturing gates

Delegate generic ownership, one-writer locking, recovery, save/reopen, frames and export evidence to the general CAD skill. Two verifier processes must not write the same evidence. Each run uses a unique output directory and records artifact hashes/state. Do not reuse evidence after an untested geometry revision.

Require the requested height in neutral standing coordinates, expected body/joint counts from the graph, one valid connected solid per body, no unintended fragments/fusions, and all required visual/motion/capture/holding results. Save, close/reopen and make a meaningful reversible native parameter change, inspect its actual effect, restore and compare the final geometry. A shape-only fixture is not a complete editable character deliverable.

Export the complete assembly in its designed print orientation. Reread the mesh: dimensions/units, connected components, watertightness, consistent orientation, self-intersections, missing limbs, accidental fusions, volume and deviation from native surfaces. Do not count native tree objects as rigid bodies or mesh triangles as fragments. Review actual layers as described in [printing](flat-back-printing.md). A first-test-print readiness statement has exact limits; no physical release/strength/wear/torque claim precedes physical evidence.

## Stop unproductive CAD iteration

If product proportions or retention topology are wrong, redesign the architecture. Do not spend hours making local Booleans report PASS. Once digital gates pass and uncertainties are release/friction/PLA behavior, a controlled physical coupon or first figure print usually provides more information than another dense collision grid. Record the next physical test and change one purposeful variable at a time.
