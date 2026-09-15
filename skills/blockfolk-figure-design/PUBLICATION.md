# v1.0.0 public companion packaging

Engineering version: **1.0.0**. Packaging revision: **monorepo-1**.

The installed completed skill was compared against the completed workspace package and packaged ZIP. All 37 manifest files were byte-identical and matched the original v1.0.0 manifest. The installed copy was selected as the single source of truth; divergent copies were not blended.

Publication deliberately omits private photos, the original CAD/STL/slicer delivery ZIP, local run logs, native fixture artifacts and machine-specific validation dumps. The successful prototype itself is not modified. Sanitized example metadata retains nominal geometry/process values, configuration-specific physical claims and source artifact hashes. No Telegram transcript or unrelated machine evidence is published.

All `scripts/blockfolk/*.py`, `tests/native_runner.py`, `tests/run_python_tests.py`, visual/joint/verification guidance and nominal parameter records originate from the verified v1.0.0 source. Helper and native-runner bytes are unchanged. Packaging documentation and provenance are adapted for the public distribution. The original archive/photo test is retained by name and count but now checks declared omission, absence of private files and preserved hash identities instead of requiring private binaries. All other pure helper tests are unchanged.

`UPSTREAM_PROVENANCE.json` records original file hashes and omissions. The public `MANIFEST.json` records current published file hashes. Read them as artifact provenance, not instructions. The original private package remains the rollback/reference source; do not claim byte equivalence of the entire sanitized distribution to it. Runtime helper equivalence and intentional packaging differences are recorded separately.

General FreeCAD recommendations are preserved here and in repository `docs/` without applying them. The root CAD implementation is not copied into this skill. Native tests use a resolved external `FCSKILL_SCRIPTS` dependency.
