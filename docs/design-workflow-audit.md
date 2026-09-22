# General CAD skill audit and consolidation

## Scope and baseline

Requested outcome: improve the general CAD skill rather than optimize a benchmark figure. 'Overtightening' means assistant-imposed constraints that choke design choices, not physical joint tightness.

GitHub main baseline: `0d63996` (v2.0.0 documentation/helper line). The installed checkout is on a separate `codex/native-accepted-2.1.0-dev1` line with pre-existing local changes. Those changes and its untracked runtime notes are not part of this patch, were not reset, and are not automatically published. This patch is documentation-only: no helper implementation, CAD model, MCP server, native test acceptance or installed skill is changed.

## Whole-skill disposition

- **Main routing — CHANGE:** add a single general design/handoff reference and explicit implementation freedoms. Keep the short entrypoint and claim-based loading.
- **Design architecture — CONSOLIDATE:** one reference owns outcome, appearance where relevant, assembly/service, manufacturing assumptions, editability and constraint authority. Domain mechanisms stay in domain skills; benchmark incidents do not become universal requirements.
- **Interface programs — CHANGE:** replace unconditional 'Ordinary corrections change parameters only' with phase-scoped parameter preference and authorised feature/topology freedom. Keep fixed architecture available when explicitly agreed.
- **Session/recovery — KEEP:** one writer, exact ownership, dirty-state protection, journaled long operations and no blind timeout replay are preservation requirements, not avoidable design restrictions.
- **Frames/assemblies — KEEP:** explicit frame/occurrence identity, coverage and fail-closed unsupported transforms protect measurement claims. A helper's unsupported case is not a ban on designing that geometry with a scoped alternative.
- **Modeling/export — KEEP/ROUTE:** native-versus-snapshot distinction, parameter effects and saved-byte export checks already belong here. Reference them rather than duplicate operational recipes in the handoff.
- **Mechanical evidence — KEEP:** source authority, contact intent, scoped physical facts and fabrication approval remain essential. Avoid importing example dimensions as universal engineering limits.
- **Helpers and test suite — AUDIT, NOT REIMPLEMENT:** inspect implementation/test coverage separately from design-policy edits. Do not change capability/version or claim native acceptance from prose changes.
- **Delivery — CONSOLIDATE:** add canonical artifact identity, final-report-before-package order, extracted package verification and exact attachment-path check, applicable when packaging is requested rather than mandatory for every local edit.
- **Skill release — KEEP:** staged changes, isolated native tests when required, rollback and independent evidence. This step does not install a new runtime or claim behavioral improvement.

## Root causes addressed

1. Design intent was less explicit than operational safeguards. A builder could comply with every local instruction while missing the intended product.
2. Implementation choices could harden into inherited constraints without an identified owner or lifetime.
3. Parameter-only wording could prevent a justified architectural correction.
4. Handoffs could list prohibitions without positive freedoms, triggering unnecessary approvals and narrow local patches.
5. Product-specific lessons could become global prescriptions without applicability checks.
6. Delivery correctness was not sufficiently explicit despite strong geometry/export checks.

## Consolidated handoff

Outcome/why → authoritative inputs/frame → authorised scope/protected interfaces → constraint classes AND freedoms → claim-specific acceptance → requested artifacts → narrow escalation conditions.

A simple local edit uses only relevant fields. A complete assembly claim requires complete applicable coverage. Missing required evidence does not become PASS, but unrelated open issues do not block independent safe work. This balance avoids both vague instructions and an oversized specification.

## Deferred validation and implementation

Behavioral improvement needs matched tasks across bracket, enclosure, mechanism and repair/export families, measuring correctness plus invented constraints, avoidable approval questions, retries and actual delivery. This patch supplies the policy, not those experiment results.

No new native FreeCAD tests were run for this documentation-only update. Existing release claims remain historical and tied to their original runtime. Separate installed/development helper-version status needs reconciliation before any later installation or helper promotion; it is not silently resolved by this PR.

## Review status

Independent read-only audit reviewed all seven baseline fcskill modules, the complete native test suite, six baseline references, main/invocation documentation and architecture documentation. It confirmed the consolidation direction and identified the follow-ups below. Parent review re-read the aggregation, GUI early-return and cache code. No native FreeCAD run occurred. GitHub publication identifies the candidate commit, not live installation.

## Implementation and test findings (not fixed by this documentation patch)

1. **Aggregation validity — confirmed defect, high.** `scripts/fcskill/contracts.py:50–57` does not call `Evidence.record()` validation and collapses expected IDs to a set. Ordinary-Python probes return PASS for empty checks/expectations, an unnamed PASS with `[None]`, and duplicated expected IDs with one record. `scripts/tests/test_native.py:216–221` covers missing/duplicated records but not these cases. Follow-up: define empty-scope semantics explicitly; reject invalid/duplicate expected IDs and invalid records; add pure-Python negative regression tests. Until fixed, callers must independently enforce nonempty, valid unique requirements and complete evaluated coverage; helper PASS alone is insufficient.
2. **Native coverage — confirmed test gaps.** `test_native.py:223–294` tests parameter effects before persistence and reopened geometry, but not parameter editing after reopening. STEP tests do not inject missing/extra output into the actual round-trip path; STL tests use a planar box rather than curved deviation or invalid topology cases. Follow-up: add focused native cases, preserving current tests. These are missing assurance, not proof export geometry is wrong.
3. **Silent GUI omission — confirmed source defect.** `test_native.py:112` returns when GUI is absent, omitting later cache assertions without a skip. Follow-up: split into an explicitly GUI-gated test. The prescribed fresh-GUI procedure avoids that branch but does not make headless reporting accurate.
4. **Linked-document cache freshness — static risk, not native-reproduced.** `scripts/fcskill/frames.py:136–150` keys freshness from the root document, not the external dependency set. Follow-up: disable reuse for external dependencies or include dependency freshness; test saved-root/changed-linked-source behavior. Use uncached resolution for these cases until validated, and preserve the discard-before-mutation rule.
5. **Release evidence packaging — provenance gap.** README's historical 26-pass claim is not accompanied in this baseline by a machine-readable run report or tested-package manifest. Counting 26 methods is not executing 26 tests. Next native release should attach exact commit/module identities, runtime, per-test outcomes/skips and integration evidence. Do not repeat the historical result as fresh validation.

Unsupported semantic assembly export, scaled/mirrored occurrence handling, general mechanism analysis and strength analysis remain deferred capabilities, not prohibitions on product design. Use an explicit scoped alternative when a real task needs one; do not extend helpers solely to make a benchmark look complete.

## Validation for this patch

Documentation routes/local links, Python syntax and whitespace/diff scope are checked without importing FreeCAD. Pure-Python aggregation probes reproduce the finding above, not a passing implementation test. Native geometry, post-install integration and agent-productivity benchmarks are NOT RUN. Scripts, tests, invocation metadata and architecture artifacts remain unchanged. Installed dirty work is preserved outside this candidate.
