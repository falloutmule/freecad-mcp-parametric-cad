"""Pure Python tests. These tests do not certify FreeCAD/OCCT geometry."""
import json
import math
import unittest
from unittest.mock import patch
from fcskill.modeling._core import Dim, ModelingError, dimension, finite, identifier
from fcskill.modeling.parameters import Parameter
from fcskill.modeling.sweeps import Domain, RestorationError, plan_samples, run_cases
from fcskill.runtime import capabilities


class InputTests(unittest.TestCase):
    def test_finite_number(self):
        self.assertEqual(finite(3, "n"), 3.0)

    def test_reject_nonfinite(self):
        for x in (math.nan, math.inf, -math.inf):
            with self.subTest(x=x), self.assertRaises(ValueError): finite(x, "n")

    def test_reject_bool_and_text(self):
        for x in (True, False, "3 mm", None, [], complex(1, 2)):
            with self.subTest(x=x), self.assertRaises(ValueError): finite(x, "n")

    def test_positive(self):
        for x in (0, -1):
            with self.assertRaises(ValueError): dimension(x, "n", positive=True)

    def test_offset_can_be_negative(self):
        self.assertEqual(Dim(-5).value, -5)

    def test_dim_expression(self):
        self.assertEqual(Dim(10, "Params.Width / 2").expression, "Params.Width / 2")

    def test_bad_expressions(self):
        for expr in ("", " ", 7, "x\ny", "x\x00", "x" * 4097):
            with self.subTest(expr=str(expr)[:10]), self.assertRaises(ValueError): Dim(1, expr)

    def test_identifiers(self):
        self.assertEqual(identifier("PlateWidth_2"), "PlateWidth_2")
        for name in ("", "123", "some name", "../p", "a.b", "a-b", None):
            with self.assertRaises(ValueError): identifier(name)

    def test_parameter_kinds(self):
        for kind in ("length", "angle", "integer", "number"):
            self.assertEqual(Parameter(5, 1, 10, kind).kind, kind)

    def test_parameter_bounds(self):
        for args in ((0, 1, 10), (11, 1, 10), (5, 10, 1)):
            with self.assertRaises(ValueError): Parameter(*args)

    def test_integer_constraints(self):
        with self.assertRaises(ValueError): Parameter(1.1, 0, 5, "integer")
        with self.assertRaises(ValueError): Parameter(1, 0, 2**40, "integer")
        with self.assertRaises(ValueError): Domain(0, 3, 1.5, "integer")

    def test_unknown_kind(self):
        with self.assertRaises(ValueError): Parameter(1, 0, 2, "meters")
        with self.assertRaises(ValueError): Domain(0, 1, .5, "log")

    def test_error_record_json(self):
        record = ModelingError("UNSUPPORTED", "Not implemented", api="thing").record()
        self.assertEqual(json.loads(json.dumps(record))["status"], "UNVERIFIED")


class SamplingTests(unittest.TestCase):
    def setUp(self):
        self.domains = {"Width": Domain(10, 30, 20), "Count": Domain(1, 5, 3, "integer")}

    def test_deterministic(self):
        self.assertEqual(plan_samples(self.domains, seed=21), plan_samples(self.domains, seed=21))

    def test_input_order_independent(self):
        self.assertEqual(plan_samples(self.domains), plan_samples(dict(reversed(list(self.domains.items())))))

    def test_seed_changes_random_fill(self):
        self.assertNotEqual(plan_samples(self.domains, seed=1)["cases"], plan_samples(self.domains, seed=2)["cases"])

    def test_baseline_first(self):
        self.assertEqual(plan_samples(self.domains)["cases"][0], {"Count": 3, "Width": 20})

    def test_all_values_in_domain(self):
        plan = plan_samples(self.domains, max_cases=80)
        for case in plan["cases"]:
            for key, value in case.items(): self.domains[key].check(value, key)
        self.assertFalse(plan["coverage"]["continuous_domain_proven"])

    def test_unique(self):
        rows = plan_samples(self.domains)["cases"]
        self.assertEqual(len(rows), len({tuple(sorted(row.items())) for row in rows}))

    def test_corners_covered(self):
        coverage = plan_samples(self.domains)["coverage"]
        self.assertTrue(coverage["all_corners_included"])
        self.assertTrue(coverage["all_axis_endpoints_included"])

    def test_tiny_budget_discloses_missing_coverage(self):
        plan = plan_samples(self.domains, max_cases=1)
        self.assertEqual(len(plan["cases"]), 1)
        self.assertFalse(plan["coverage"]["all_axis_endpoints_included"])
        self.assertFalse(plan["coverage"]["all_corners_included"])

    def test_many_dimensions_bounded(self):
        domains = {f"P{i}": Domain(0, 1, .5) for i in range(64)}
        result = plan_samples(domains, max_cases=16)
        self.assertEqual(len(result["cases"]), 16)
        self.assertEqual(result["coverage"]["theoretical_corner_count"], 2**64)
        self.assertFalse(result["coverage"]["all_corners_included"])

    def test_constant_domain(self):
        result = plan_samples({"X": Domain(2, 2, 2)}, max_cases=4)
        self.assertEqual(result["cases"], [{"X": 2}])
        self.assertTrue(result["coverage"]["all_corners_included"])

    def test_saturated_integer_domain(self):
        result = plan_samples({"X": Domain(0, 2, 1, "integer")})
        self.assertEqual(len(result["cases"]), 3)

    def test_invalid_budget(self):
        for count in (0, 257, 1.5, True):
            with self.assertRaises(ValueError): plan_samples(self.domains, max_cases=count)

    def test_invalid_domains(self):
        for domains in ({}, {"bad name": Domain(0, 1, 0)}, {"P": 1}):
            with self.assertRaises(ValueError): plan_samples(domains)

    def test_bad_seed(self):
        with self.assertRaises(ValueError): plan_samples(self.domains, seed=True)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.state = {"X": 5.0}
        self.domains = {"X": Domain(1, 9, 5)}
        self.writes = []

    def read(self): return self.state.copy()
    def apply(self, values):
        self.writes.append(values.copy())
        self.state.update(values)
    def validate(self): return {"status": "PASS", "requirement": "FIXTURE_PREDICATE", "x": self.state["X"]}
    def run_samples(self, cases=None, **overrides):
        options = dict(read_values=self.read, apply_values=self.apply, recompute=lambda: None, validate=self.validate)
        options.update(overrides)
        return run_cases(self.domains, cases or [{"X": 1}, {"X": 9}], **options)

    def test_success_and_restore(self):
        report = self.run_samples()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(self.state, {"X": 5.0})
        self.assertEqual(report["counts"]["PASS"], 2)

    def test_resets_between_samples(self):
        self.run_samples()
        self.assertEqual(self.writes, [{"X": 5.0}, {"X": 1.0}, {"X": 5.0}, {"X": 9.0}, {"X": 5.0}])

    def test_bad_case_rejected_before_mutation(self):
        with self.assertRaises(ValueError): self.run_samples([{"X": 1}, {"X": 10}])
        self.assertEqual(self.writes, [])

    def test_case_scope_exact(self):
        for cases in ([{}], [{"X": 1, "Extra": 2}]):
            with self.assertRaises(ValueError): self.run_samples(cases)
        self.assertEqual(self.writes, [])

    def test_stale_baseline_refused(self):
        self.state["X"] = 6
        with self.assertRaises(ValueError): self.run_samples()
        self.assertEqual(self.writes, [])

    def test_callback_error_is_not_pass(self):
        def error(): raise RuntimeError("validator broke")
        report = self.run_samples(validate=error)
        self.assertEqual(report["status"], "UNVERIFIED")
        self.assertEqual(report["restoration"]["status"], "PASS")
        self.assertEqual(self.state["X"], 5)

    def test_boolean_is_not_a_verdict(self):
        report = self.run_samples(validate=lambda: True)
        self.assertEqual(report["counts"]["UNVERIFIED"], 2)

    def test_missing_requirement_is_not_pass(self):
        report = self.run_samples(validate=lambda: {"status": "PASS"})
        self.assertEqual(report["status"], "UNVERIFIED")

    def test_nonfinite_evidence_rejected(self):
        report = self.run_samples(validate=lambda: {"status": "PASS", "requirement": "x", "value": math.nan})
        self.assertEqual(report["status"], "UNVERIFIED")

    def test_fail_preserved(self):
        def verdict(): return {"status": "FAIL" if self.state["X"] > 7 else "PASS", "requirement": "X_BELOW_8"}
        report = self.run_samples(validate=verdict)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["counts"]["FAIL"], 1)

    def test_unapplied_values_not_pass(self):
        report = self.run_samples(apply_values=lambda values: None)
        self.assertEqual(report["counts"]["UNVERIFIED"], 2)

    def test_restore_failure_raises_with_evidence(self):
        def partial(values):
            if values["X"] == 5 and self.state["X"] != 5: raise RuntimeError("restore failed")
            self.state.update(values)
        with self.assertRaises(RestorationError) as ctx:
            self.run_samples([{"X": 1}], apply_values=partial)
        self.assertEqual(ctx.exception.report["restoration"]["status"], "UNVERIFIED")

    def test_partial_write_exception_restored(self):
        def apply(values):
            self.state.update(values)
            if values["X"] == 1: raise RuntimeError("failure after write")
        report = self.run_samples(apply_values=apply)
        self.assertEqual(self.state["X"], 5)
        self.assertEqual(report["status"], "UNVERIFIED")

    def test_keyboard_interrupt_restores(self):
        def abort(): raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.run_samples(validate=abort)
        self.assertEqual(self.state["X"], 5)

    def test_soft_deadline_disclosed(self):
        with patch("fcskill.modeling.sweeps.time.monotonic", side_effect=[0.0, 10.0, 11.0]):
            report = self.run_samples(deadline_seconds=1)
        self.assertEqual(report["status"], "UNVERIFIED")
        self.assertEqual(report["not_run"], 2)
        self.assertEqual(report["stop_reason"], "SOFT_DEADLINE")
        self.assertEqual(self.state["X"], 5)

    def test_execution_coverage_is_recalculated(self):
        report = self.run_samples([{"X": 1}, {"X": 1}])
        self.assertEqual(report["attempted_coverage"]["unique_case_count"], 1)
        self.assertFalse(report["passing_coverage"]["all_corners_included"])

    def test_failed_samples_are_not_passing_coverage(self):
        report = self.run_samples(validate=lambda: {"status": "FAIL", "requirement": "FIXTURE"})
        self.assertTrue(report["attempted_coverage"]["all_corners_included"])
        self.assertEqual(report["passing_coverage"]["unique_case_count"], 0)

    def test_timeout_coverage_not_confused_with_plan(self):
        with patch("fcskill.modeling.sweeps.time.monotonic", side_effect=[0.0, 10.0, 11.0]):
            report = self.run_samples(deadline_seconds=1)
        self.assertTrue(report["planned_coverage"]["all_corners_included"])
        self.assertEqual(report["attempted_coverage"]["unique_case_count"], 0)

    def test_json_safe_report(self):
        json.dumps(self.run_samples(), allow_nan=False)


class CapabilityTests(unittest.TestCase):
    def test_absent_runtime_not_supported(self):
        with patch("fcskill.runtime.importlib.import_module", side_effect=ModuleNotFoundError("FreeCAD")):
            result = capabilities()
        self.assertFalse(result["freecad"]["available"])
        self.assertTrue(result["helpers"]["pad"]["implemented"])
        self.assertEqual(result["helpers"]["pad"]["native_acceptance"], "NOT_RUN")

    def test_deferred_not_advertised(self):
        result = capabilities()
        for name in ("assembly_solving", "linear_pattern", "hard_kernel_timeout"):
            self.assertFalse(result["deferred"][name]["implemented"])

    def test_report_json(self):
        json.dumps(capabilities(), allow_nan=False)


if __name__ == "__main__": unittest.main()
