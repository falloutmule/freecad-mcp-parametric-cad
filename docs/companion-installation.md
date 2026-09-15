# Independent skill installation

The old repository workflow was manual root copying. Its separately distributed 2.1.0.dev1 upgrade bundle used explicit targets, read-only plans, conflict checks, backups and rollback on failure. `install_skills.py` follows those conventions for full peer skill folders; it does not modify the existing CAD runtime or supersede the historical overlay installer.

Run with Python 3.10+ from a clean source checkout. `skill-packages.json` explicitly chooses each payload, so a core-only installation cannot accidentally include nested companion skills or their private development files.

## Destination and selection

Confirm the host's real discovery location using its available-skill catalog/configuration. [Official Codex guidance](https://learn.chatgpt.com/docs/build-skills) documents user/repository skill roots and matching by description; older/local hosts may expose another configured root. Pass that actual directory as `--skills-dir`. The directory must exist. No default path is guessed, no environment/configuration is rewritten, and linked roots/payload paths are refused by this conservative installer.

```text
python install_skills.py core --skills-dir <skills-root>
python install_skills.py blockfolk --skills-dir <skills-root>
python install_skills.py all --skills-dir <skills-root>
```

These are dry-runs. Apply the same selection with `--apply --backups-dir <backup-root>` where the existing backup root is separate from the discovery root. `blockfolk` checks for a peer `freecad-mcp-parametric-cad` entry point and helper package. It does not install or overwrite the core implicitly. It does not claim that presence alone establishes FreeCAD runtime compatibility; run the skill's native tests on the intended runtime.

## Existing copies and updates

An exact payload match is unchanged. A managed install has `.fcskill-install.json` recording its file hashes; additional, missing or modified payload files cause refusal. Bytecode/test caches are ignored. Git checkouts are not replaced. Unknown existing copies are refused unless their complete content matches a separately provided known baseline at `<baseline-root>/<skill-name>`.

To adopt the original Blockfolk v1.0.0 into the sanitized public distribution, compare it with the verified original package first, then use that package's parent as `--baseline-root`. Do not manufacture a baseline from arbitrary current edits to bypass conflict detection. The public package intentionally differs from the private original; see its publication manifest. Full old directories, including their original private artifacts, remain in local backups and must not be committed.

All selected packages are preflighted and staged before mutation. Publication is serialized by an exclusive lock in the destination root. Concurrent edits are checked again before replacement. Earlier successful publications are restored if a later publication fails; conflicting concurrent changes are preserved for review rather than overwritten.

## Rollback

Each applied installation reports a backup transaction directory containing `receipt.json` and exact `before/<skill-name>` directories for replacements. New installations have no prior directory. Inspect a rollback plan, then apply it:

```text
python install_skills.py rollback --receipt <transaction>/receipt.json
python install_skills.py rollback --receipt <transaction>/receipt.json --apply
```

Rollback refuses changed installed files or tampered backups. Replaced versions are kept under `rolled-back/` rather than deleted. Backups remain outside discovery. Do not run installers concurrently with editors updating the same skill files.

## Discovery acceptance

Verify two immediate peer directories with distinct frontmatter names at the actual discovery root. Then confirm the host lists both; repository structure alone is insufficient. A generic request such as “make an editable mounting plate” should select the general skill. A Blockfolk figure request should select the companion, which routes CAD/session/frame/export work through the general skill. Read the chosen entry points and exercise a small helper/parameter check; no full figure is needed. Capture the host catalog result separately from a filesystem smoke test.

## Hermes

No Hermes files, configuration or runtime are changed. If that installation supports the same SKILL.md format, the two folders can later be copied to its explicitly confirmed skill root as peers. Verify dependency availability and discovery there at that time; this repository makes no Hermes runtime acceptance claim.
