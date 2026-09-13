#!/usr/bin/env python3
"""Run only the new unit or native suite; write a new evidence file, never overwrite.

CLI: python scripts/run_modeling_tests.py unit --output /new/path/report.json
FreeCAD GUI Python console (scripts already on sys.path):
    import run_modeling_tests
    run_modeling_tests.run('native', r'C:\\scratch\\new-native-report.json')
A skipped native suite is UNVERIFIED, never an accepted release.
"""
from __future__ import annotations
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent


def run(kind: str, output: str | Path) -> dict:
    if kind not in ("unit", "native"):
        raise ValueError("kind must be unit or native")
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise FileExistsError("Choose a new report path; existing evidence is preserved")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import fcskill
    expected = ROOT / "fcskill"
    if Path(fcskill.__file__).resolve().parent != expected:
        raise RuntimeError("A different fcskill checkout is already imported; use a fresh host")
    runtime = fcskill.capabilities()
    old_active, before = None, None
    if kind == "native" and runtime["freecad"]["available"]:
        import FreeCAD as App
        from fcskill.session import gui_thread, inventory
        gui_thread()
        before = inventory()
        old_active = App.ActiveDocument
    log = io.StringIO()
    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern=f"test_modeling_{kind}*.py")
    try:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    finally:
        if old_active is not None:
            import FreeCAD as App
            if App.getDocument(old_active.Name) == old_active:
                App.setActiveDocument(old_active.Name)
    after = None
    if before is not None:
        from fcskill.session import inventory
        after = inventory()
    inventory_unchanged = before == after if before is not None else None
    status = "PASS" if result.wasSuccessful() and not result.skipped and result.testsRun > 0 else "UNVERIFIED"
    if result.failures or result.errors:
        status = "FAIL"
    if inventory_unchanged is False:
        status = "FAIL"
    report = {"schema_version": 1, "suite": kind, "status": status,
              "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped],
              "elapsed_seconds": time.monotonic() - started, "identity": fcskill.identity(),
              "runtime": runtime, "inventory_before": before, "inventory_after": after,
              "inventory_unchanged": inventory_unchanged,
              "native_acceptance": status if kind == "native" else "NOT_TESTED_BY_UNIT_SUITE",
              "log": log.getvalue()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf8") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
    print(log.getvalue())
    print(json.dumps({k: report[k] for k in ("suite", "status", "tests_run", "failures", "errors", "native_acceptance")}, indent=2))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("unit", "native"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return 0 if run(args.kind, args.output)["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
