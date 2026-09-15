# Select joints by product, motion and process

Status labels are scoped to configurations:

- **PHYSICALLY VALIDATED:** one successful user-reported print of the exact Product Pass reference on Aquila/PLA/0.4 mm. Nominal dimensions are CAD values, not measured as-printed dimensions. No torque or endurance measurements.
- **CAD VALIDATED:** the named geometry and listed tests passed. This never implies printable release or physical holding.
- **EXPERIMENTAL:** a credible mechanism direction requiring design and verification; no successful native configuration is supplied for it.

The original reference's canted shoulders, straight elbows/hips/knees and neck yaw all use paired compliant followers against relieved broad cams. They are one proven mechanism/configuration family, not independent physical trials of every variation. The generic helper fixtures are new simplified geometry and are CAD VALIDATED only.

## Anatomy selection

| Location | First choices | When to choose an alternative |
|---|---|---|
| Neck | Paired-cam yaw swivel | A lateral nod hinge for an expressive nod; serial yaw/nod only if extra yoke/body is justified; fixed union when intentionally unarticulated |
| Shoulder | Compact or canted captive cam hinge, buried in sleeve | Straight axis for simpler motion; serial two-axis yoke for abduction plus flexion if silhouette permits; free hinge only when holding is not required |
| Elbow | Lateral captive cam hinge under sleeve/cuff | Free captive hinge for a deliberate freely swinging limb; larger same-family bearing for larger mass |
| Hip | Lateral captive cam hinge inside trouser/torso volume | Free-running hinge for animation/support use; indexed cam only after offset/contact validation |
| Knee | Lateral captive cam hinge inside trouser/boot transition | Simple free hinge where intentional; stronger resized same family for larger figures |

“Sleeve integrated” is a packaging strategy, not a new kinematic family. “Canted” changes the axis and swept envelope, not the basic capture principle. Increased range comes from axis placement and swept-volume clearance, not removing retaining walls.

## A. Capped free-running hinge — CAD VALIDATED fixture

**Use/axis/range:** one rotational DOF, typically lateral elbow/hip/knee or shoulder; local X in the helper. Coupon tested −180…180° at 5°; useful character range is set by real shells/stops. There is no pose holding. A low-complexity option only when freely swinging is intentional.

**Retention:** continuous parent journal through a closed child bearing, between two complete integral caps. Full cap and guide/hoop containment plus tilt/aperture bounds are required. Reference-sized starting geometry: journal diameter 5.10, caps diameter 9.20 × 1.30 thick, bearing width 5.50, radial and axial gap 0.45 mm. These dimensions inherit no physical status when the cam is omitted.

**Print:** lying-back lateral axle is horizontal to the bed. A 90° teardrop roof reduces the circular bore's unsupported crown. Both axial cap/journal starts and bore roof still need actual-layer review. Removing the cam changes deposition topology; the coupon is not slicer certified.

**Material/integration:** keep complete closed hoops and both guide lands. The helper uses an annular witness outside the entire opening, not a universal minimum wall. Reference end lands are 0.80 mm and cap thickness 1.30 mm; choose enough actual surrounding material for nozzle paths and handling, then verify it. Hide collar in sleeve/trouser volume.

**Failures/checks:** cut-away cap or hoop, thin root fracture, axial squeeze, elephant-foot fusion, roof droop and low holding by design. Require one solid/body, positive gap, multi-direction capture, sampled swept motion and slice inspection. Larger helper coupon (6.40 journal/11.20 cap diameters) also passed native capture; it is not a physically validated stronger joint.

## B. Broad cam + opposed compliant followers — PHYSICALLY VALIDATED reference

**Use/axis/range:** lateral elbows/hips/knees and straight or canted shoulders. Reference useful motion: shoulders 0…180°, elbows 0…100°, hips 0…90°, knees −90…0°. Native motion sampled at 5°. Shoulders have ±22.5° cant in the lateral/vertical plane. One raised-arm pose uses 170°, within a resistance region; 180° is a release orientation.

**Capture/clearance:** same full capped journal/closed bearing as A. Limb journal R2.55, cap R4.60, cap thickness 1.30, bore R3.00, axial face clearance 0.45. Chamber R3.70 × 3.90 wide separates two 0.80 guide lands. The 3.20-wide cam lane is relieved to R2.75 so a leftover journal rim cannot bypass the release cut. Do not confuse the 0.45 running gap with the 0.35 neutral release gap.

**Holding mechanics:** a broad R2.35 cam contains two outward-offset release windows. Two opposed curved followers have R2.50 inner arc, 0.80 radial thickness, 2.20 axial width and tip R2.00. Neutral has 0.35 mm Euclidean cam/leaf separation. Rotation brings the broad cam against a tip: nominal centered overlap is 2.35−2.00 = 0.35 mm, intended to deflect a leaf into its chamber and resist rotation. This is neither universal predictable torque nor uniform ratchet indexing. Neutral and exactly 180° are release orientations. Useful holding regions do not cover every possible angle.

**Play matters:** bearing centers can shift. One follower or narrow isolated cam lobes can be bypassed even when a centered drawing shows interference. Use opposed leaves plus a cam that still engages over feasible radial/axial play and tilt. Nominal axial margin each side is (3.20−2.20)/2 = 0.50 mm; 0.45 axial float leaves only 0.05 mm before considering tilt. Validate full 3D engagement, not only radial overlap. The successful reference has a separate detailed offset/tilt analysis; the generic fixture test only proves centered intentional contact.

**Material/printing:** leave the complete caps, closed hoop, both guide lands, leaf roots and travel chamber intact. Reference clothing cup walls are 0.90 mm; do not treat that as a strength limit. Leaves are curved in the plane perpendicular to the lateral axle, spanning actual print layers. Their rear roots meet the intentional datum; release cuts must not detach the roots. Reference journal begins slicing at Z2.2 and cam at Z2.4, allowing support from earlier journal deposition. Equal journal/cam radii produced an unanchored start during development. Inspect toolpath order, not only layer silhouettes.

**Failure modes:** stiff/short leaves can seize, break or overload PLA; weak/thin leaves can disappear in slicing or fail to hold; large chamber travel can allow bypass; axial play can lose engagement; narrow lobes can evade both leaves; malformed release cuts can fuse or remove the cam; shell fill can block deflection. Re-test after scale, material, nozzle/layer, printer, orientation or limb-mass changes. Use geometry plus slice evidence then a physical coupon/figure. No closed-form CAD torque claim is supported.

## C. Neck yaw swivel — PHYSICALLY VALIDATED reference

**Use/axis/range:** head rotation about standing vertical Z; ±30° sampled at 5°. In flat-back printing this axis lies parallel to the bed. Larger yaw range is a new shell/collision design, not inherited from the reference.

**Retention/running:** closed head bearing between complete lower/upper caps R6.10/R5.90, each 2.00 thick. Journal R3.20, bore R3.65, radial/axial clearance 0.45. Bearing width 3.40, two 0.65 guide lands, chamber R4.80 × 2.10. A circular bore here has different roof behavior from the limb teardrop; inspect the exact print layers.

**Holding:** opposed 0.80-thick, 1.00-wide followers, tip R2.90, broad cam R3.20 × 2.00 wide. Nominal overlap 0.30, neutral release gap 0.35. The reference's conservative combined axial/tilt engagement lower bound is about 0.030 mm: a small configuration-specific margin, not a recommended safety factor.

**Material/integration/failures:** bury caps in collar and head underside while preserving full rings, guide lands and neck clearance. Head leverage makes wall/root strength and resistance tuning consequential. Head collision, circular-roof droop, bearing play and weak follower engagement are key risks. Re-prove capture, head poses, offset contact and layer support if changing it. No neck constructor is supplied; consult native reference features, then implement fresh editable features through the general CAD skill.

## D. Nod hinge — EXPERIMENTAL anatomical integration

**Use/axis/range:** lateral head pitch; initially target a useful small range such as ±20°, then establish actual limits from collar/head sweeps. Use A or B capture, not an open ball socket. A reference-family lateral hinge is credible, but a nodding neck configuration has not been printed or natively verified here.

**Print/clearance/material:** flat-back lateral axle favors the teardrop strategy. Begin with process gaps near the reference only on comparable equipment; allocate the chosen family's complete caps, guide lands, root and chamber dimensions. A smaller collar may not fit them. Keep the head's rear datum and head leverage in view.

**Holding/integration/failures/checks:** choose B for resistance, A for intentionally free nodding. Hide the yoke under hair/collar without trapping support. Watch chin/collar collision, cap exposure, insufficient neck walls and lost sitting gaze. Full capture, contact under play, motion, visual and slice gates are required; there is no tested default nod range.

## E. Serial two-axis captured yoke — EXPERIMENTAL

**Use/axis/range:** two orthogonal captured hinges for shoulder flexion/abduction or combined neck yaw/nod. Ranges are independently designed from useful pose targets; no numeric range has passed here. Requires another rigid body and another joint, so change the graph/component count.

**Print/retention/clearance:** each axis must retain both caps and closed bearing. An axis normal to the plate has different layer starts/overhangs from one parallel to it. Rotate/reposition the assembly or use a stepped self-supporting cap geometry only after new layer evidence. Start running gaps from process calibration, not from a supposed universal ball-joint allowance.

**Holding/material/integration:** A or B per axis. Reserve two complete bearing envelopes plus a connected load-bearing yoke; no tested minimum yoke wall is available. Larger sleeves/collars can bury the yoke, but reject it if it dominates the character. Simplicity often wins at 100 mm.

**Failures/checks:** extra bulk, disconnected yoke, collision between axes, trapped support, tilt escape, extra friction or unsupported vertical caps. Requires both-axis capture, combined multi-axis sampled motion, independent holding/contact tests, all-view product gate and new slice/physical tests. No constructor or validation claim.

## F. Indexed opposed cam — EXPERIMENTAL

**Use/axis/range:** deliberately selected angle stops in a captive hinge, when discrete postures are preferable to broad friction regions. Same single axis as A/B; indexing pitch and motion range are design inputs, not claimed 30° defaults.

**Retention/holding:** A-style full caps remain independent of a lobed cam and opposing spring tips. Valleys provide rest positions, lobes a compliant energy barrier. Verify that the barrier exists throughout feasible bearing offsets; adding decorative teeth is insufficient.

**Print/clearance/material/integration:** process gaps and material envelope start with B, but tooth pitch/height and leaf travel must survive the actual nozzle/layers. Hide inside cuffs/pants. Too-small teeth disappear; large lobes overstress leaves or permit lateral bypass. Require native angle/offset/contact sweeps, preserved guide material, slice paths and physical tuning before use. No indexed geometry is supplied as CAD validated.

## Fixed and size variants

An intentionally fixed neck is a connected rigid union and removes an articulated location. It needs no moving clearance or holding mechanism; verify one connected solid and update body counts. This is an ordinary rigid construction choice, not a physically tested joint option in this package.

For stronger/larger variants, enlarge journal, cap thickness/diameter, guide span and supporting shell together as needed; keep manufacturing gaps independently selected. Increase chamber/follower space with actual expected travel and mass. Do not label “stronger” from diameter alone: material orientation, neck leverage, root section and physical load tests matter.
