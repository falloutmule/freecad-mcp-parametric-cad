# Evidence, not universal constants

The user reports one successful physical print of the **later Product Pass package**, explicitly confirmed in this task. Printer: Voxelab Aquila. Material: PLA. Nozzle: 0.4 mm. Nominal character height: 100 mm. The three owner-supplied photos and the user's statement are the physical evidence; the owner-held preserved package is the source of nominal geometry and process settings. Private photos, raw logs and the original delivery ZIP are not distributed in this public repository.

## What is physically established

User-reported: the figure printed flat on its back already connected, joints released, limbs remained attached during handling, pose holding resisted free flopping, and no pins/screws/magnets/glue/post-print assembly were needed. Photos corroborate a connected figure on the plate and in hand, changed joint positions, broad printed backs and surviving face, stepped hair, vest/belt, sleeves, chunky hands and boots. The photos do not measure every joint's range or holding force.

This supports **PHYSICALLY VALIDATED** for the specific paired-cam/follower family/configuration in that one figure. It does not establish universal dimensions, all-angle holding, quantitative release force, torque, strength, wear, lifetime, exact as-printed clearance or repeatability across printers. Filament brand, exact blend, humidity, calibration, release technique, physical print duration and mass were not reported. Do not infer a “silk PLA” formulation from the blue/magenta appearance.

## What remains CAD/slicer evidence

100.000 mm is nominal CAD height, not a caliper measurement. The 0.45 running gap, 0.35 neutral cam gap, 0.80 leaf thickness, cap dimensions and all other engineering values are nominal design dimensions associated with the confirmed successful package. Useful poses, 5° collision samples, guide/hoop containment, mesh topology, offset-contact analysis, native save/reopen and detailed path anchoring are digital records. The estimated 35.94 g and 5 h 38 m 45 s are slicer numbers, not physical measurements.

The original report still correctly records its historical pre-print state as PHYSICAL: UNTESTED. Do not rewrite it. The new [physical record](../examples/physically-validated-100mm/physical-test.json) supplements it with the later user report and confirmed provenance.

## How to reuse dimensions

The [parameter summary](../examples/physically-validated-100mm/parameter-summary.json) classifies nominal values by process, mechanism and character. Running/release gaps, leaf dimensions, cap thickness, guide lands, chamber and bridge spans are **validated starting points for this configuration on this equipment**, not printer-independent hard limits. Head width, torso depth, joint centers, clothing and exact angles are **design-specific examples**. Positive separation, connected closed retaining topology, adequate follower engagement and no trapped support are **requirements**, but they do not imply one universal numerical minimum.

Changes in figure scale, material, nozzle, layer height, printer, shell mass, lever arm or orientation require renewed digital checks and physical tuning. Do not automatically shrink a 0.45 mm gap to 0.27 mm for a 60 mm figure. Do not claim the new helper coupon has been printed just because its dimensions resemble the reference.

## Lightweight test records

Copy [the blank record](../examples/physical-test-record.json) into each new project's evidence folder. Give it an ID/date, source artifact hashes, printer/material/nozzle/layers, joint family and nominal gaps, release/retention/holding outcomes, fit impression, damage and notes. Use null/unknown for unmeasured values; keep user reports, observed photos, digital estimates and physical measurements distinct. Add a new immutable record for a revision instead of overwriting an earlier outcome.

Next useful physical work: a coupon with the intended new joint dimensions/process and actual cam/follower contact zones, recording release damage, retained handling and which poses hold. If quantitative comparison matters, measure release force/holding torque with a described method and uncertainty. One successful figure is a strong starting point; it is not a statistical tolerance study.
