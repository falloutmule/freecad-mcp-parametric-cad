# Blockfolk v1.0.0 — public packaging validation

The completed private source passed 23 pure Python tests and eight native FreeCAD groups. This monorepo packaging reruns both suites from the companion's new source location; current integration results are recorded in the repository's `docs/blockfolk-integration.md`.

The pure suite covers independent character/process scaling, parameter round trips, invalid dimensions, joint graph transforms, semantic poses, separate motion/retention/holding claims, rejected incomplete capture evidence, mass sanity and reference metadata. Its private archive/photo test now checks public omission and provenance instead of requiring excluded private files. There remain 23 tests.

The unchanged native runner tests free and paired-cam fixtures, full capture witnesses, half-cap/slit-hoop rejection, clearance rebuild, larger free hinge, canted axes and native parameter save/reopen/change/restore. Free motion is sampled at 73 angles, paired contact/capture at 37 angles, both at 5° spacing. These are finite centered tests, not all-offset holding certification or physical force evidence. Eight groups must pass without skipped native work.

**Physical scope:** one confirmed successful user-reported Product Pass print on Aquila/PLA/0.4 mm, with packaged 0.20 mm layers. Release, retention and pose holding were reported; actual torque, release force, wear, repeatability and as-printed dimensions were not measured. Generic fixtures are CAD-tested only. Nodding-neck integration, serial two-axis yokes and indexed opposed cams remain experimental.

Private raw evidence and original fabrication artifacts remain with the owner and are not published. See [publication record](PUBLICATION.md) for exact source/packaging boundaries and [parameter summary](examples/physically-validated-100mm/parameter-summary.json) for configuration-specific nominal starting values. Hermes discovery/runtime is not tested; no Hermes changes are made.
