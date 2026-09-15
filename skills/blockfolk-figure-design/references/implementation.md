# Helper contract and native integration

The installed general skill was inspected at version 2.1.0.dev1. Its actual `fcskill.modeling.Parameter`, `create_parameters`, `Dim`, sketch/pad/pocket helpers and runtime capability reporting exist; joint creation/assembly solving are not supported helper APIs. Native CSG, constrained sketches, `Part::Mirroring`, `Part::Offset2D` and extrusions are available through ordinary FreeCAD operations. Do not invent a `fcskill.create_joint` or copy transport/document infrastructure here.

## Python entry points

Add this package's `scripts` directory to the controlled FreeCAD Python path. Importing `blockfolk` does not open documents or connect to a process.

```python
from blockfolk.parameters import Design, Hinge, Process
design = Design().resize_character(60)
assert design.process.clearance == 0.45
assert design.mechanism.leaf_thickness == 0.8

from blockfolk.joints import hinge
fixture = hinge(Hinge(), Process(), holding=True)
from blockfolk.validation import capture_shapes
evidence = capture_shapes(fixture.parent, fixture.child, fixture.witnesses,
                          fixture.projected_cap, fixture.opening)
```

`hinge` returns native OCCT shapes for a generic two-body coupon in local X-axle/Y-print-height coordinates. It has no document/file/GUI effects. It uses complete cap disks, a closed bearing with teardrop roof, optional chamber and opposed curved followers, a broad cam with Euclidean outward-offset release cuts, and a deliberate common rear datum. It refuses some dimensions that cannot fit a conservative capture witness. It is not a character generator, full parameter optimizer, editable FCStd constructor or slicer-certified model. The fixture geometry differs from the successful figure's garment shells and has **CAD VALIDATED**, not physical, status.

Native fixture tests exercise two separate solids, gap, complete capture witnesses, deliberately damaged retainers, free motion, centered intentional contact, and larger/gap variants. They do not establish robustness over all bearing offsets, elastic response, print release or strength. Documented neck/serial/detent options have no prebuilt constructors.

## Editable product implementation

Use `fcskill.modeling.create_parameters(doc, name, definitions)` with `Parameter(value, minimum, maximum, kind, description)` in an owned document. Choose truthful domain bounds; the parameter object's stored bounds do not make every combination safe. Connect native feature expressions to meaningful proportion, mechanism and process parameters. Ordinary native Part cylinders/CSG and fully constrained sketch profiles cover the shapes the helper layer does not expose. The successful reference does this without custom Python feature proxies.

For editable production geometry translate the fixture operations into native features, not a single frozen `Part::Feature.Shape` per character. Use whole native cap/journal cylinders, child bore/roof/chamber cuts, leaf sketch/extrusion and opposed mirror, release `Part::Offset2D` plus extrusion, and final garment unions/cuts. Leaf profile angle samples in the fixture define its arc approximation; they are not a required hair/pixel pattern. Release offsets must increase enclosed area, remain closed and preserve intended gap.

Keep body-shell construction separate from the mechanism, but link dimensions. Subtract moving envelopes from added shells; preserve full cap/hoop/guide witnesses and leaf chambers. Added geometry must connect to the intended body, avoid crossing the rear datum and survive useful sweeps. Do not fill intentional contact gaps while joining a cuff. The final native tree should expose a manageable parameter set, not thousands of decorative features.

`Design` independently stores `Proportions`, `Hinge` and `Process` with strict JSON schema version 1. `resize_character` changes only height and derived proportional dimensions. It intentionally does not resize the hinge or choose whether a mechanism fits: use envelope checks and judgment, then select a family/size. `Hinge.derived` checks local feasibility but is not a complete manufacturing gate.

## Poses and evidence

`poses.Joint` defines name, parent, child, rest-frame center, axis and limits. `transforms(joints, angles, root)` composes a rooted graph, rejects unknown joints/cycles/repeated children, and leaves source shapes alone. Centers/axes are expressed in the common rest frame. Apply matrices to resolved actual bodies using the general FreeCAD frame workflow. Do not apply transforms twice to already placed occurrences.

`semantic_checks` takes transformed landmarks in engineering coordinates and supplies ordinary humanoid cues only. Its visual-review flag cannot be cleared by passing landmark checks; collision checking is separate. `capture_shapes` is specifically a rigid capped-hinge material-witness check, not a generic socket theorem. `classify_contact` requires actual cam AND actual leaf containment. `mass_sanity` catches excessive mass against a conservative solid-volume upper bound; it cannot establish a correct sliced model on its own.

## Tests

Run the pure suite through `python -m unittest discover -s tests -p "test_*.py" -v`. Native tests require actual FreeCADCmd and the general skill's scripts path. See [installation/test commands](../README.md). Use a fresh unique evidence directory per run, isolated config files and one writer. Check the JSON `passed` field, not only the FreeCAD process exit code (FreeCAD may return zero after a Python error). No fixture launches a user GUI or edits the successful reference.
