# Orientation is part of the joint design

| Strategy | Benefits | Costs and necessary evidence |
|---|---|---|
| Flat-back | Broad intentional contact; low print Z; compact footprint; selected horizontal hinges can use teardrop roofs; garments can conceal mechanics | First-layer separation, bridging journals/chambers, cap starts and contact surfaces must work in this exact orientation |
| Upright | Natural vertical silhouette; some axial swivels may have useful vertical axes | Taller/slender print, leg stability, horizontal shelves/caps, shoulders and underside of head; often more difficult support-free PIP geometry |
| Other justified orientation | May improve a chosen joint's roofs or layer strength | Re-prove datum/stability, all moving component starts, support accessibility, transformed overhangs and actual footprint |

Flat-back is a well-supported strategy, not a requirement for all characters. The reference has engineering X=lateral, Y=rear-to-front, Z=standing height. Its print transform is (X, 100−Z, Y). A different figure uses its own height and frame, resolved through the general skill's frame helpers.

Design a common rear datum from the start. The reference's 25 mm head depth and 14 mm torso depth share a rear plane without making every limb head-thick. Garment fronts provide depth where useful. Avoid accessories or cap features below the datum. Each intended body needs sensible first contact or a proven supported/captive start; “all objects touch the plate” alone proves neither anchoring nor viable toolpath order.

## Reference process starting point

Voxelab Aquila, original 220 × 220 × 250 mm class machine, PLA, 0.4 mm nozzle, 1.75 mm filament. Product Pass package used OrcaSlicer 2.4.2, 0.20 mm first and subsequent layers, 3 walls, 5 top/bottom layers, 20% gyroid, Arachne walls, 0.15 mm elephant-foot compensation, no supports/brim/raft/tower, one skirt. Temperatures: 210/205°C nozzle and 60/55°C bed (first/other). Outer/inner/infill/bridge speeds 25/35/40/20 mm/s, acceleration 500 mm/s², max volumetric flow 6 mm³/s. These are package settings, not independently measured machine telemetry.

The exact machine/profile copy remains in the owner-held reference ZIP; this public package includes nominal settings and provenance only. For another printer, confirm bed volume, firmware/start/end G-code, leveling, nozzle, filament and extrusion settings. Do not silently use the supplied G-code or alter saved user profiles. Create a run-specific profile copy; never send a print without user instruction.

## Layer review

Inspect first-layer toolpaths for gaps, elephant-foot expansion, skirt/brim separation and independent body islands. Check knees, hips, elbows, shoulders and neck at their actual start/roof heights, including caps/rings, guide lands, leaf roots/tips, release cuts and broad cams. Inspect layers before and after each feature; show the actual nozzle roads, not only mesh sections.

For the reference, journals begin around print Z2.2, cam lanes Z2.4, limb followers Z4–5, chamber roofs Z7.8–8.6, cap closure Z9.2; neck cam starts around Z7–7.6 and followers Z9.4–10.4. These are navigation hints for that file only. Bridge spans were about 3.5–3.9 mm and journal cantilevers about 1.6 mm. Record new spans and prior-layer anchors after every architecture change.

Look for unsupported starts, wholly unanchored extrusions, poor bridge endpoints/direction, missing thin leaves, gap-filling roads crossing moving clearances, fused first layers, trapped supports and roofs that sag into journals. A clean STL or slicer success message is insufficient. Trapped internal support is unacceptable; choose a different mechanism/orientation if the cavity cannot print without it.

The reference slice has 131 layers, 12.051 m filament, 28.99 cm³ deposited material, estimated 35.94 g and 5 h 38 m 45 s. Its nominal solid CAD volume is 54.765 cm³. These are mutually plausible with the stated infill, not physical measurements. A 397 g estimate for this configuration would fail the mass sanity gate and require investigating units, duplicate objects, purge/support and density. Check implausibly low values and missing limbs too.
