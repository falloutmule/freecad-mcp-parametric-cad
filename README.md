# FreeCAD MCP Parametric CAD

A Codex skill for trustworthy parametric mechanical CAD through an existing local FreeCAD MCP connection.

The repository root remains the independently useful `freecad-mcp-parametric-cad` skill. Optional domain skills live under `skills/`; [Blockfolk Figure Design](skills/blockfolk-figure-design/README.md) adds articulated-character engineering and uses the general skill's CAD infrastructure. It is not required for ordinary CAD work.

Version **2.1.0.dev1** preserves the v2.0 operational checks and adds an experimental, bounded helper layer for native sketches, parameters, datum references, Part Design features, lofts, and parameter sampling/restoration.

## Install

Use the offline installer from this checkout. It is read-only unless `--apply` is supplied, following the previous upgrade bundle's conflict-aware workflow. Resolve your host's actual skill-discovery root first; the installer requires `--skills-dir` and never guesses or edits Codex configuration. Backups must be outside discovery.

```text
python install_skills.py core --skills-dir <confirmed-skills-root>
python install_skills.py blockfolk --skills-dir <confirmed-skills-root>
python install_skills.py all --skills-dir <confirmed-skills-root>
```

Add `--apply --backups-dir <separate-existing-backup-directory>` to perform a reviewed plan. `core` installs only the root skill, `blockfolk` requires the general skill already present, and `all` installs both as peer directories. Existing identical installations are no-ops. Modified managed files or unknown existing copies are refused; adopting a known unmodified copy requires an explicit matching `--baseline-root` containing peer skill folders. Every replacement preserves exact originals and a rollback receipt. See [installation and rollback](docs/companion-installation.md).

Manual root-skill copying remains supported: copy the root `SKILL.md`, `README.md`, `agents/`, `scripts/` and `references/` into a folder named `freecad-mcp-parametric-cad` (plus root architecture/native-acceptance docs if desired). Copy `skills/blockfolk-figure-design/` separately if wanted. Do not depend on nested `SKILL.md` discovery or copy the entire monorepo as an all-skills installation.

```text
<confirmed-skills-root>/
  freecad-mcp-parametric-cad/SKILL.md
  blockfolk-figure-design/SKILL.md
```

Keep development snapshots and rollback folders outside discovery. Neither skill installs/starts FreeCAD or MCP automatically. The [OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills) explains host discovery and explicit/implicit selection; confirm the configured location on your actual host rather than assuming a single path works for every version.

Invoke `$freecad-mcp-parametric-cad`, or let Codex select it for relevant CAD work. Start with [SKILL.md](SKILL.md).

## Architecture

The [interactive architecture diagram](docs/freecad-skill.architecture.html) and its [editable Archify source](docs/freecad-skill.architecture.json) describe the v2.0.0 core helper package. Download the HTML and open it locally; GitHub does not execute HTML previews.

Instructions route by the claim being made. `session` protects documents; `frames` resolves native occurrences; `geometry` records bounded or exact evidence; `exports` checks delivered bytes and scoped geometry; `recipes` demonstrates editable native parts. `contracts` carries explicit results. These checks are not an independent engineering verifier.

## Validation

Native acceptance for v2.1.0.dev1 used fresh isolated FreeCAD 1.1.3 GUI processes with OCCT 7.8.1 and Python 3.11.14. The accepted payload passed 73 unit/mocked tests, 19 new native modeling tests, 26 original native regressions, 17 installer tests, and metadata validation, with no failures, errors, or skips. See the [native acceptance record](docs/native-acceptance-2.1.0-dev1.md).

Read [testing and release guidance](references/skill-release.md). A normal Python installation cannot run FreeCAD-native tests without FreeCAD modules. GUI tests must not be counted as passes when skipped. Historical release results do not certify a different runtime or physical part.

## Deliberate limits

- Mirrored/scaled/sheared occurrences and Link arrays are explicitly unsupported.
- STEP helper scope is one solid per occurrence, not semantic assembly hierarchy preservation.
- STL deviation is sampled and one-way, not a global surface-error guarantee.
- Touching does not prove contact footprint, strength or physical fit.
- There is no persistent cache, automatic printing, runtime upgrade, or independent-verifier expansion.

This repository contains the skill and its tests, not EnderRack production geometry or private session records.

Blockfolk's physical claims apply to one confirmed Aquila/PLA reference configuration. Public examples contain sanitized nominal dimensions and provenance, not private photos, raw run logs, CAD/slicer archives or universal printer limits. [General FreeCAD recommendations](docs/FREECAD_SKILL_RECOMMENDATIONS.md) are preserved for separate review and are not applied by this integration.
