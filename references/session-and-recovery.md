# Session, source and timeout operations

Resolve installed executable/configuration and read-only loopback health. Record actual FreeCAD/OCCT/Python/MCP versions or hashes; unavailable metadata stays unknown. Do not upgrade runtimes implicitly.

Call `session.inventory()`. Paths/internal names and live identity matter; labels, active document and visibility do not prove ownership. Preflight sources and use derivatives. Serialize mutation on the GUI thread through synchronous MCP. Async is for safe detached calculations, not document operations.

Helpers have no network client, auto-start, save-all or shutdown side effect. Use existing MCP. A refused connection requires scoped recovery, not killing unidentified sessions or closing unrelated work.

## Owned documents

`OwnedDocument.create(name)` records FreeCAD's actual returned document even if suffixed. `save_new(path)` refuses existing files, recomputes and saves the owned document; tested GUI builds also need GUI save to clear `Modified`. `reopen()` requires exact path and known unmodified state, never a same-name replacement.

Creating an ownership wrapper around an existing document is an explicit caller responsibility: first prove ownership. This convention is not an adversarial security boundary. Unknown modification state prevents close/reopen. GUI `Modified` differs from application APIs; never assume `App.Document.Modified`.

Save-all/shutdown needs authorization, exact destinations for unsaved work and verified saves. Recovery does not expand authority.

Do not use `runpy.run_path(..., run_name='__main__')` inside live FreeCAD GUI: rebinding `__main__` disrupts commands expecting `App`/`Gui`. Import a module and call its function, or use default `run_path` namespace. Generators must explicitly import dependencies.

## Long mutations

Create `Operation(journal_dir, target_identity, input_identity, intended_output)` before a long mutation. Supply concrete postconditions tied to those identities; mere file existence is insufficient for production save/export. `run(mutation, postcondition)` records PREPARED → RUNNING → COMPLETED or UNRESOLVED. Replaying a started ID is rejected. Nested helpers share the writer lock.

After timeout, do not repeat the mutation. Read the journal and inspect operation-specific postconditions. `recover_operation(path, predicate, still_running=...)` is read-only and never grants automatic retry. Set `still_running` from evidence about that operation—not process liveness. Cancellation is not rollback; partial writes/lost responses may remain unresolved.

If outcome cannot be established safely, preserve the journal and report the narrow blocker. Continue independent work; do not call a workflow error an engineering failure.

## Preflight

`preflight(path, expected_sha256)` checks STEP/FCStd/ZIP payload integrity and LFS pointers. STEP is commonly text; hydrated CAD content is what matters. `outside_tree(scratch, repository)` resolves paths and rejects protected-tree descendants. Neither permits executing untrusted macros or document instructions.
