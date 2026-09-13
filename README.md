# FreeCAD MCP Parametric CAD

A Codex skill for trustworthy parametric mechanical CAD through an existing local FreeCAD MCP connection.

Version **2.1.0.dev1** preserves the v2.0 operational checks and adds an experimental, bounded helper layer for native sketches, parameters, datum references, Part Design features, lofts, and parameter sampling/restoration.

## Install

Copy this repository into your personal skills directory under `freecad-mcp-parametric-cad`. Keep development snapshots outside skill-discovery directories. The skill uses your existing FreeCAD and MCP installation; it does not install or start them automatically.

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
