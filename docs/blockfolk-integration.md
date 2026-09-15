# Blockfolk companion integration acceptance

Base: `codex/native-accepted-2.1.0-dev1` at `20261fd25aa2ec37834e96a75b18cd4213851205`. Integration branch: `codex/blockfolk-companion-skill-001`. No main-branch merge or unrelated history rewrite.

## Source and publication boundary

Blockfolk engineering version 1.0.0 was imported from the completed installed skill. All 37 original manifest files matched the completed workspace directory and versioned ZIP byte-for-byte. The original manifest SHA-256 is `b13491b9c18d3f6ff3c4ace6e29535ab6c9ed195b3a8cfd14ea18f599520d0c7`; the original skill ZIP SHA-256 is `49cc8e7e6885f8cade878b38eed85d49453a12bc0c5e74ceca49d8cf48309b1f`.

The companion source is `skills/blockfolk-figure-design`. Public packaging revision `monorepo-1` omits private photographs, the CAD/slicer delivery archive and raw local validation evidence. It retains sanitized nominal parameter/physical records and artifact hashes. Packaging docs and one metadata test were adapted; specialized helper code and the native runner remain byte-identical. See [publication details](../skills/blockfolk-figure-design/PUBLICATION.md) and its upstream/public manifests. The original successful figure and private source package remain unchanged.

The root `SKILL.md`, CAD runtime, existing tests and engineering references are unchanged from the base commit. Root changes are installation documentation, package selection/install tooling and integration tests/docs. General recommendations are preserved separately and not applied.

## Executed checks

| Suite | Result |
|---|---|
| General unit/mocked tests | 73/73 PASS |
| General new native modeling | 19/19 PASS, no failures/errors/skips |
| General original native regressions | 26/26 PASS, no failures/errors/skips |
| Historical 2.1.0.dev1 upgrade installer | 17/17 PASS; run from the preserved release bundle, not copied into the runtime |
| New peer installer | 25/25 PASS |
| Real repository payload installation | core-only, companion-only with dependency, and all: PASS; peer discovery, idempotence, exact payload hashes and rollback checked |
| Blockfolk pure tests, new source path | 23/23 PASS |
| Blockfolk native groups, new source path | 8/8 PASS |
| Blockfolk installed-location tests | 23/23 pure, 8/8 native PASS |

General native suites ran in a fresh isolated FreeCAD GUI process with empty before/after document inventories; the process exited after its owned work. Blockfolk native tests ran in separate FreeCADCmd processes with isolated configs. Runtime: FreeCAD 1.1.3, OCCT 7.8.1, native Python 3.11.14. No unrelated FreeCAD session was restarted or mutated.

The peer installer tests include local modifications/additions/deletions, unknown identity, duplicate names, dependency absence, traversal, lock contention, exact-baseline adoption, second-publication failure recovery, manual rollback failure recovery and tampered-backup refusal. Backup folders are outside discovery. Public source files and native helper scope remain separate from physical claims.

## Actual installation and discovery

The general skill was left at its existing actual user-discovery location. The companion was installed beside it using the verified original package as baseline. The entire original companion directory was moved into an exact rollback copy before the public package was published. Local receipts record resolved paths and hashes; those machine-specific receipts are intentionally not committed.

The actual current Codex available-skills catalog contains **two distinct entries**: `freecad-mcp-parametric-cad` and `blockfolk-figure-design`. The active assistant selected/read both installed entry points. A generic editable-cylinder/parameter smoke used the installed general helper; a small captive cam/follower fixture smoke used the installed companion together with the general helper. Both passed. This is current-host catalog and installed-code acceptance, not merely a repository directory test or a statistical routing benchmark in a new independent Codex process.

Source nesting is never used as the installation/discovery mechanism. The installer requires the host's explicitly confirmed discovery root; see [installation](companion-installation.md). Hermes was not modified or runtime-tested.

## Physical claim boundary

The companion retains one user-confirmed successful Aquila/PLA/0.4 mm reference configuration with packaged 0.20 mm layers, captive cam/follower joints, canted shoulders and neck yaw. It does not claim universal dimensions, measured torque/strength/wear, or physical validation of the new helper fixtures or experimental mechanisms. No full figure was built and no print was sent during this integration.
