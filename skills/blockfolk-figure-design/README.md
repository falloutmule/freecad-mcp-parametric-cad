# Blockfolk Figure Design 1.0.0

An optional Codex/Hermes-format domain skill for character-first print-in-place articulated figures. It cooperates with `freecad-mcp-parametric-cad` for generic CAD infrastructure. The engineering version remains 1.0.0; public packaging revision is `monorepo-1`.

## Use and installation

Ask: “Use $blockfolk-figure-design with freecad-mcp-parametric-cad to design a 90 mm Blockfolk character with a coat, yaw neck and pose-holding limbs.” Start with [SKILL.md](SKILL.md). Other sizes, costumes and intentionally omitted joints are design decisions; physical status is configuration-specific.

From the repository root, run `python install_skills.py blockfolk --skills-dir <confirmed-skills-root>` for a dry-run. The general FreeCAD skill must already exist as a peer. Use `all` to install both. Add `--apply --backups-dir <separate-existing-backup-root>` to apply with rollback. See the repository's `docs/companion-installation.md` for conflict detection and baseline adoption. Installed copies remain independently discoverable folders; nested source discovery is not assumed.

Manual installation: copy this directory as `blockfolk-figure-design` into the confirmed skill root, separately from `freecad-mcp-parametric-cad`. Preserve a rollback copy before any replacement. Hermes may use the same folder only if its configured loader supports this format; Hermes installation/runtime is not tested and is not changed by the repository installer.

## Contents and tests

The compact router links six engineering references. Four specialized helper modules provide parameters, generic two-body joint fixtures, poses and claim/capture checks. They do not build a character or duplicate generic CAD sessions/frames/exports. Native shape fixtures are not finished editable figure documents.

From this directory, run `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v` (23 tests). To write new machine-readable evidence, run `python -X utf8 tests/run_python_tests.py --output <new-report.json>`.

For eight native groups, set `FCSKILL_SCRIPTS` to the resolved general skill's `scripts` path and `BLOCKFOLK_TEST_OUTPUT` to a fresh unique output directory. Launch a new FreeCADCmd process with isolated user/system configurations:

```text
<FreeCADCmd> -u <run>/user.cfg -s <run>/system.cfg <this-skill>/tests/native_runner.py
```

Require `passed: true` in the new `native_results.json`; process exit zero alone is insufficient. Do not execute the runner in an unrelated GUI session. The script claims its evidence path exclusively and does not overwrite earlier runs. Tests require Python 3.10+ for pure helpers and a compatible native FreeCAD runtime for native geometry.

## Reference and claims

See [physical reference](examples/physically-validated-100mm/README.md), [publication changes](PUBLICATION.md), [validation](VALIDATION_REPORT.md), and [general recommendations](FREECAD_SKILL_RECOMMENDATIONS.md). The confirmed reference has one successful user-reported Aquila/PLA print. Photos and the original delivery remain private with the owner; this repository publishes sanitized nominal parameters and provenance only. It does not publish private logs or CAD/slicer archives. New generic fixtures remain CAD-tested only; experimental options are labeled explicitly.
