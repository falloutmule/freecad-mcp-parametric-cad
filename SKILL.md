---
name: freecad-mcp-parametric-cad
description: Design, edit, inspect, and validate parametric mechanical CAD through local FreeCAD MCP. Use for fabricated interfaces, fit coupons, coordinate frames, complete-assembly context, export fidelity, collision evidence, and CAD handoff. Not for purely visual modeling or generic FreeCAD UI help.
---

# FreeCAD MCP Parametric CAD

Deliver the requested mechanical outcome with reusable native operations and evidence proportional to the claim. Do not turn ordinary CAD into a new verifier or workflow-development project.

## Essential safeguards

- Resolve outcome, affected objects, authorized changes, and required editability. Preserve sources, unrelated documents, dirty repository work, and the user's machine/configuration.
- Choose verification from the **claim**, not merely the action. Read-only “does it fit?” needs fit evidence; a verified local edit does not verify the assembly.
- Before live CAD, require read-only MCP loopback health and inventory exact document paths and modification state. One writer per FreeCAD process; mutations, recompute and save stay on its GUI thread.
- Use the tested occurrence/frame helpers instead of inventing parent-placement formulas. Derive frames from authoritative datums, not candidate faces. Keep `T_target<-source` and print transforms explicit.
- Distinguish requirements, targets, constructed keepouts and physical facts. Missing identity/coverage, invalid geometry and failed calculations remain `UNVERIFIED`, never zero interference. Photos establish dimensions/handedness only when separately calibrated.
- Preserve feature-scoped physical evidence. A waiver is not physical PASS. Tool recovery cannot change architecture, printer identity, or requirements.
- Continue safe requested digital work without unnecessary approval stops. Do not expand authorization to unrelated overwrites, save-all/shutdown, repository publishing, or printing.

## Load only relevant operations

| Task/claim | Read |
|---|---|
| Connect, inspect documents, import, save, recover | [Session and recovery](references/session-and-recovery.md) |
| Construct/edit, test parameters, reopen/export | [Modeling and export](references/modeling-and-export.md) |
| Reusable native creation helpers (experimental) | [Modeling helpers](references/modeling-helpers.md) |
| Bounded parameter sampling and restoration | [Parameter testing](references/parameter-testing.md) |
| Register, measure fit/contact, account for assemblies | [Geometry and assemblies](references/geometry-and-assemblies.md) |
| Source/physical authority, fabrication release | [Mechanical evidence](references/trustworthy-mechanical-cad.md) |
| Multi-revision program or frozen topology | [Interface programs](references/interface-program-workflow.md) |
| Maintain/test/install this skill | [Skill release](references/skill-release.md) |

## Helpers

Add this skill's **resolved absolute** `scripts` directory to `sys.path`; import `fcskill` and record `fcskill.identity()` for version-sensitive work. Do not rely on a same-name module already loaded from another checkout.

Use `fcskill.capabilities()` for helper availability; capability flags are not native-test evidence. Prefer the new creation helpers only within their documented scope and verify them on the installed FreeCAD build before adoption.

Use `frames.shape_in_frame`, `session.OwnedDocument`/`Operation`, geometry evidence functions, and the explicitly scoped exporters. References specify contracts and limitations. These are native operational checks—not the independent verifier. Use project verifiers only for capabilities their pinned release demonstrably supports.

Report the result, measured scope, limitations, exact artifacts, and next meaningful action. Screenshots aid inspection; hashes identify payloads; neither proves fit.
