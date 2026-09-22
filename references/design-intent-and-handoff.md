# Design intent, constraint economy and handoff

Use for a new design, substantial revision, or delegated CAD task. For a simple local edit, answer the relevant questions briefly; do not impose a program-sized specification. This reference owns the general design/handoff policy. Operational details remain in the existing session, modeling, geometry and release references.

## Specify the outcome; leave room to solve it

Establish intended use, appearance where relevant, critical external interfaces, assembly/service route, required behavior, manufacturing assumptions, requested editability and deliverable stage. Distinguish an inspection, a proposal and permission to modify. Ask only about missing information that materially changes these outcomes. State reversible minor assumptions and continue authorised work.

Review architecture before polishing features: can the proposed shape perform the function, be assembled, be manufactured in the intended orientation and be edited as requested? For visual products, review whole-object views and important regions, not topology alone. Inspect symmetry only where intended. For mechanisms, distinguish motion, retention and any holding requirement; these are examples of separate claims, not mandatory features of every CAD task.

A settled pose is not an assembly path. A valid solid is not proof of intended shape. A spreadsheet beside a stored shape does not make that shape parametrically driven. Choose the simplest appropriate architecture; do not force a feature tree or an external generator irrespective of the user's requested editability.

## Constraint economy

Classify the constraints that matter:
- **HARD:** explicit user requirement/prohibition, safety/preservation boundary, authenticated external interface or accepted essential design decision.
- **TARGET:** preferred outcome with an acceptable range or an openly unresolved tolerance.
- **FLEXIBLE:** implementation choice the builder owns inside the authorised envelope.
- **ASSUMPTION:** provisional input with its uncertainty and consequence.
- **OPEN:** unresolved decision, owner and whether it blocks the current action.

For a blocking constraint, identify its source, reason, scope, lifetime and verification method. Numeric constraints need units/frame and justified tolerance where applicable. An assistant's prior suggestion, example dimension, helper limitation or benchmark fixture is not automatically a user requirement. Do not invent physical limits to fill a template.

Protect functional interfaces rather than freezing every historical surface. State positive freedoms alongside exclusions. Do not freeze topology unless the task actually requires it. A parameter-only phase can be useful for a controlled comparison, but it is not a universal modeling rule.

When requirements conflict, identify the conflict and recommend the smallest tradeoff. Distinguish evidence of infeasibility from failure of one chosen method. Within declared freedoms, make and explain the choice without another approval. Changes to user prohibitions or accepted essential outcomes require resolution, not a silent waiver. Retire obsolete experiment-specific constraints explicitly; never retire a continuing user prohibition by inference.

**Overconstraint here means choking the problem-solving space with instructions.** Do not reinterpret a workflow complaint as a request to alter physical fits or joint clearances.

## Verification proportional to the claim

Select evidence for the actual outcome and change dependencies. A local repair does not require every test in the skill; a complete-assembly claim cannot borrow a subset result. Check directly and indirectly changed features; invalidate affected evidence, not unrelated accepted evidence.

Separate rest-state geometry, sampled behavior, assembly travel, manufacturing preparation and physical performance. Declare intended contact before tests. Neither zero overlap nor equal volume/bounds proves the broader claims of running clearance or shape equivalence. Report sampling resolution, evaluated coverage and unchecked scope. Required missing tests cannot produce PASS.

Do not add gates merely because tools exist. Do not equate one independent algorithm with an independent reviewer. When a separate checker is warranted, it reads saved artifacts against the contract and returns findings without repairing the candidate. Ordinary self-checks remain useful if labelled accurately.

## Compact task handoff

Fill only applicable fields; unresolved critical fields stay explicitly OPEN rather than invented.

1. **Outcome and why:** requested function/appearance and authoritative problem evidence.
2. **Inputs:** exact revision, files/identities, units/frame, relevant reference and evidence limitations.
3. **Scope:** authorised actions, continuing prohibitions, protected interfaces and editable region.
4. **Constraints and freedoms:** brief classification above; what the builder may decide without approval.
5. **Acceptance:** named claims, appropriate test/evidence, tolerances and coverage where needed. Distinguish digital acceptance from physical uncertainty.
6. **Deliverables:** primary format, contents/frame, required editability, native/source/export expectations and attachment route.
7. **Escalation:** only conflicts with hard requirements, out-of-scope changes, uncertain state or unavailable required evidence. Continue independent safe work.

Builder return: exact artifacts/hashes; intended versus actual change set; tests actually executed and coverage; deviations/uncertainties; concise current state. Checker return: exact reviewed candidate, criterion-specific result and smallest blocking finding. Session continuation: active request, retained prohibitions, canonical artifacts, evidence, failed approaches and next bounded action; application state must be rediscovered when stale.

Avoid 'fix everything', 'keep everything identical' or 'make print-ready' without defined outcomes. Prefer: 'Preserve the mounting pattern and external envelope; internal ribs are flexible. Resolve the interference, report dependency changes and verify fit against the supplied mating part.'

## Delivery and learning

One canonical current deliverable must be identifiable. Save/reopen and export checks follow modeling guidance. Finish the report before packaging, list exact paths/sizes/hashes and verify extracted members. Do not hash a manifest's own previous version as its current hash. Verify the actual attachment path, not a display label. Corrections must reach release documentation, not only chat. These checks apply when delivering a package; they are not a demand to package every edit.

Use difficult products as regression cases, not universal architecture templates. Promote general lessons into their owning reference; retain domain-specific details in domain skills. Test future behavioral improvements on different task families: a flexible-structure bracket, an enclosure/assembly, a moving mechanism and a local repair/export. Freeze each task's outcome and compare correctness, unnecessary restrictions/questions, retries and delivered artifacts. A prose revision alone is not evidence of improved agent performance.
