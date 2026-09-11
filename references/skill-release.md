# Skill testing and installation

Preserve installed package and dirty development checkout. Stage outside discovery. Do not reset repositories, upgrade runtimes, modify MCP server or expand independent verifiers.

Record executable/build, OCCT/Python, MCP package/source identity, helper path/version/hash and documents. Match APIs to actual runtime. Format checks are not security validation.

`scripts/tests/test_native.py` covers independent coordinates, nested/repeated links, scale rejection, failure/ambiguity, containment, export coverage, meaningful parameters and document preservation. Run with installed FreeCAD Python; use a **fresh isolated GUI process** for GUI tests. Skips are not passes.

```python
import sys, unittest
sys.path.insert(0, '<absolute-skill-path>/scripts')
suite = unittest.defaultTestLoader.discover('<absolute-skill-path>/scripts/tests', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
assert result.wasSuccessful() and not result.skipped
```

Reload can retain old module references. Final integration uses a fresh process and `fcskill.identity()`, not an expected version string. Never restart the user's working session for test convenience.

Freeze expectations before implementation; derive coordinates independently. Add actual regression cases, not new product requirements. Prove native edit → restore → reopen → STEP/STL early, alongside an unchanged unsaved sentinel.

Match old/new inputs, outcomes and coverage. Separate cold/fresh-process from operation-local reuse. Report correctness with time/calls. Historical-helper benchmarks are not agent-productivity trials; do not claim fewer interruptions or task speedups without matched observations.

Run skill-creator metadata validation and inspect routes/scripts. Preserve invocation policy. Install only the tested manifest, retain rollback outside discovery, confirm loaded path/hash and unchanged sources. Remote publishing requires separate authorization.
