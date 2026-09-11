# Native modeling and faithful export

Read session guidance before mutation. Choose native editability versus generated snapshots from the requested output—not whether a script is used.

`recipes.py` has tested constrained mounting plate, datum bracket and hollow enclosure examples. Their dimensions/topologies are not requirements. They expect fresh documents and fixed internal names; do not insert wholesale into unrelated models.

Keep input properties separate from dependent features. Child references to containing Body properties can create cycles; examples use independent parameter objects with no Python proxy needed after reopen.

Check intended parameter effects and downstream validity, not merely volume. Restore the selected candidate before export. Ineffective parameters are not usable controls. Frozen architecture applies only when declared by the project.

## Persistence and STEP

Use owned-document save/reopen. Compare disk geometry to the selected state and verify native parameters still edit correctly. Valid geometry alone does not prove persistence/editability. Include relevant project dimensions, axes and planes.

`export_step(occurrences, path, length_tolerance, volume_tolerance)` supports one solid per resolved occurrence. It exports explicit staged shapes, reimports bytes, and matches geometry/count one-to-one. Missing/extra/mismatched occurrences fail closed. Identity is retained in its manifest, not inferred from STEP labels.

Multi-solid occurrences, surfaces and semantic assembly hierarchy exports need an explicitly scoped alternative; do not silently flatten and claim coverage. Byte integrity/readability differs from engineering equivalence. Do not require stable bytes/face numbers. Fixture tolerances are not design defaults.

## Print STL

`export_stl` requires explicit rigid `T_print<-engineering`, linear/angular deflection, relative flag, deviation tolerance and relative-volume tolerance. It leaves the engineering source unchanged.

It rereads delivered STL; checks closed/manifold/oriented/non-self-intersecting topology, bounds, volume, and distance from every vertex/triangle centroid to source surface. This is a **sampled one-way deviation check**, not global Hausdorff proof. Check critical openings/dimensions separately when needed.

Export helpers refuse existing paths. Preserve returned evidence, transforms/settings and hashes. They do not prove strength, printability, slicer correctness or physical fit; consult mechanical-evidence guidance for release.
