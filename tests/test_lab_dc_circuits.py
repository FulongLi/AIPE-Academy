"""Tests for labs/foundations/dc_circuits.py (DC circuit fundamentals lab).

Run from the repository root with
    python -m unittest tests.test_lab_dc_circuits -v
or as part of
    python -m unittest discover -s tests -v
"""
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_PATH = ROOT / "labs" / "foundations" / "dc_circuits.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lab = load("dc_circuits_lab", LAB_PATH)
NAN = float("nan")
INF = float("inf")


def quantity_ok(test, quantity, unit):
    """Assert the {"value", "unit"} shape with a finite float value."""
    test.assertEqual(set(quantity), {"value", "unit"})
    test.assertIsInstance(quantity["value"], float)
    test.assertEqual(quantity["unit"], unit)
    json.dumps(quantity, allow_nan=False)


def metadata_ok(test, result, status):
    test.assertIn("model", result)
    test.assertEqual(result["validation_status"], status)
    test.assertTrue(result["assumptions"])
    test.assertTrue(result["limitations"])
    json.dumps(result, allow_nan=False)


class OhmLawTests(unittest.TestCase):
    def test_default_example(self):
        result = lab.ohm(v=6.0, r=300.0)
        metadata_ok(self, result, "analytical-example")
        self.assertEqual(result["solved_for"], "i")
        self.assertAlmostEqual(result["current"]["value"], 0.02, places=12)
        self.assertAlmostEqual(result["power"]["value"], 0.12, places=12)
        quantity_ok(self, result["voltage"], "V")
        quantity_ok(self, result["current"], "A")
        quantity_ok(self, result["resistance"], "Ohm")
        quantity_ok(self, result["power"], "W")

    def test_solves_each_missing_quantity(self):
        self.assertAlmostEqual(lab.ohm(i=0.02, r=200.0)["voltage"]["value"], 4.0, places=12)
        self.assertEqual(lab.ohm(i=0.02, r=200.0)["solved_for"], "v")
        found = lab.ohm(v=8.0, i=0.02)
        self.assertEqual(found["solved_for"], "r")
        self.assertAlmostEqual(found["resistance"]["value"], 400.0, places=9)

    def test_first_lesson_numbers(self):
        # 4 V / 200 Ohm worked example and 8 V / 400 Ohm transfer check.
        self.assertAlmostEqual(lab.ohm(v=4.0, r=200.0)["current"]["value"], 0.02, places=12)
        self.assertAlmostEqual(lab.ohm(v=4.0, r=200.0)["power"]["value"], 0.08, places=12)
        self.assertAlmostEqual(lab.ohm(v=8.0, r=400.0)["current"]["value"], 0.02, places=12)
        self.assertAlmostEqual(lab.ohm(v=8.0, r=400.0)["power"]["value"], 0.16, places=12)

    def test_consistency_check_accepts_matching_triple(self):
        result = lab.ohm(v=6.0, i=0.02, r=300.0)
        self.assertTrue(result["solved_for"].startswith("none"))
        self.assertAlmostEqual(result["power"]["value"], 0.12, places=12)

    def test_doubling_resistance_halves_current_and_power(self):
        base = lab.ohm(v=6.0, r=300.0)
        doubled = lab.ohm(v=6.0, r=600.0)
        self.assertAlmostEqual(doubled["current"]["value"], base["current"]["value"] / 2, places=12)
        self.assertAlmostEqual(doubled["power"]["value"], base["power"]["value"] / 2, places=12)

    def test_halving_voltage_quarters_power(self):
        full = lab.ohm(v=8.0, r=400.0)
        half = lab.ohm(v=4.0, r=400.0)
        self.assertAlmostEqual(half["current"]["value"], full["current"]["value"] / 2, places=12)
        self.assertAlmostEqual(half["power"]["value"], full["power"]["value"] / 4, places=12)

    def test_current_monotonic_in_resistance(self):
        currents = [lab.ohm(v=6.0, r=r)["current"]["value"] for r in (100.0, 300.0, 1000.0, 1.0e6)]
        self.assertEqual(currents, sorted(currents, reverse=True))

    def test_negative_voltage_gives_negative_current_positive_power(self):
        result = lab.ohm(v=-6.0, r=300.0)
        self.assertAlmostEqual(result["current"]["value"], -0.02, places=12)
        self.assertGreater(result["power"]["value"], 0.0)

    def test_zero_resistance_with_current_is_a_wire(self):
        result = lab.ohm(i=0.5, r=0.0)
        self.assertEqual(result["voltage"]["value"], 0.0)
        self.assertEqual(result["power"]["value"], 0.0)

    def test_invalid_inputs_raise(self):
        cases = [
            dict(v=6.0), dict(), dict(r=300.0), dict(i=0.02),
            dict(v=6.0, r=0.0), dict(v=6.0, r=-300.0),
            dict(v=NAN, r=300.0), dict(v=INF, r=300.0), dict(v=6.0, i=NAN), dict(i=0.02, r=INF),
            dict(v=6.0, i=0.0), dict(v=6.0, i=-0.02),
            dict(v=6.0, i=0.02, r=400.0), dict(v=6.0, i=0.02, r=0.0),
            dict(v="6", r=300.0), dict(v=True, r=300.0), dict(v=6.0, r=None, i=None),
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    lab.ohm(**kwargs)

    def test_error_messages_are_specific(self):
        with self.assertRaisesRegex(ValueError, "under-determined"):
            lab.ohm(v=6.0)
        with self.assertRaisesRegex(ValueError, "0 Ohm"):
            lab.ohm(v=6.0, r=0.0)
        with self.assertRaisesRegex(ValueError, "negative"):
            lab.ohm(v=6.0, r=-1.0)
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            lab.ohm(v=6.0, i=0.02, r=400.0)
        with self.assertRaisesRegex(ValueError, "finite"):
            lab.ohm(v=NAN, r=300.0)

    def test_overflow_is_reported_as_value_error(self):
        # An int beyond the float range, and finite inputs whose result overflows.
        with self.assertRaisesRegex(ValueError, "too large"):
            lab.ohm(v=10 ** 400, r=300.0)
        with self.assertRaisesRegex(ValueError, "overflow"):
            lab.ohm(v=1.0e308, i=1.0e-308)
        with self.assertRaisesRegex(ValueError, "overflow"):
            lab.ohm(v=1.0e308, i=1.0e308)


class PowerEnergyTests(unittest.TestCase):
    def test_default_example_half_hour(self):
        result = lab.power_energy(6.0, 0.02, 0.5)
        metadata_ok(self, result, "analytical-example")
        self.assertAlmostEqual(result["power"]["value"], 0.12, places=12)
        self.assertAlmostEqual(result["duration"]["value"], 1800.0, places=9)
        self.assertAlmostEqual(result["energy"]["value"], 216.0, places=9)
        self.assertAlmostEqual(result["energy_watt_hours"]["value"], 0.06, places=12)
        quantity_ok(self, result["energy"], "J")
        quantity_ok(self, result["energy_watt_hours"], "Wh")
        quantity_ok(self, result["duration"], "s")

    def test_first_lesson_numbers(self):
        two_hours = lab.power_energy(4.0, 0.02, 2.0)
        self.assertAlmostEqual(two_hours["power"]["value"], 0.08, places=12)
        self.assertAlmostEqual(two_hours["energy_watt_hours"]["value"], 0.16, places=12)
        quarter = lab.power_energy(8.0, 0.02, 0.25)
        self.assertAlmostEqual(quarter["power"]["value"], 0.16, places=12)
        self.assertAlmostEqual(quarter["energy_watt_hours"]["value"], 0.04, places=12)
        self.assertAlmostEqual(quarter["energy"]["value"], 144.0, places=9)

    def test_joule_per_watt_hour_is_3600(self):
        result = lab.power_energy(6.0, 0.02, 0.5)
        self.assertAlmostEqual(result["energy"]["value"] / result["energy_watt_hours"]["value"], 3600.0, places=6)

    def test_energy_is_linear_in_time_and_zero_at_zero(self):
        short = lab.power_energy(6.0, 0.02, 0.5)["energy"]["value"]
        long = lab.power_energy(6.0, 0.02, 2.0)["energy"]["value"]
        self.assertAlmostEqual(long, 4.0 * short, places=9)
        self.assertEqual(lab.power_energy(6.0, 0.02, 0.0)["energy"]["value"], 0.0)

    def test_source_has_negative_power(self):
        result = lab.power_energy(6.0, -0.02, 1.0)
        self.assertAlmostEqual(result["power"]["value"], -0.12, places=12)
        self.assertLess(result["energy"]["value"], 0.0)

    def test_invalid_inputs_raise(self):
        cases = [
            (6.0, 0.02, -1.0), (NAN, 0.02, 1.0), (6.0, INF, 1.0), (6.0, 0.02, NAN), (6.0, 0.02, INF), ("6", 0.02, 1.0), (6.0, 0.02, None),
            (True, 0.02, 1.0), (6.0, False, 1.0), (6.0, 0.02, True), (1.0e300, 1.0e300, 1.0), (6.0, 0.02, 1.0e308),
        ]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    lab.power_energy(*args)
        with self.assertRaisesRegex(ValueError, "negative"):
            lab.power_energy(6.0, 0.02, -0.5)
        with self.assertRaisesRegex(ValueError, "overflow"):
            lab.power_energy(1.0e300, 1.0e300, 1.0)


class SeriesParallelTests(unittest.TestCase):
    def test_default_pair(self):
        series = lab.series_parallel([10000.0, 10000.0], "series")
        parallel = lab.series_parallel([10000.0, 10000.0], "parallel")
        metadata_ok(self, series, "analytical-example")
        metadata_ok(self, parallel, "analytical-example")
        self.assertAlmostEqual(series["equivalent_resistance"]["value"], 20000.0, places=9)
        self.assertAlmostEqual(parallel["equivalent_resistance"]["value"], 5000.0, places=9)
        self.assertAlmostEqual(parallel["equivalent_conductance"]["value"], 2.0e-4, places=15)
        quantity_ok(self, parallel["equivalent_resistance"], "Ohm")
        quantity_ok(self, parallel["equivalent_conductance"], "S")
        self.assertTrue(series["sanity_check"]["passes"])
        self.assertTrue(parallel["sanity_check"]["passes"])

    def test_three_resistors(self):
        values = [100.0, 200.0, 300.0]
        self.assertAlmostEqual(lab.series_parallel(values, "series")["equivalent_resistance"]["value"], 600.0, places=9)
        expected = 1.0 / (1 / 100 + 1 / 200 + 1 / 300)
        self.assertAlmostEqual(lab.series_parallel(values, "parallel")["equivalent_resistance"]["value"], expected, places=9)

    def test_bounds(self):
        values = [470.0, 1000.0, 2200.0]
        self.assertGreaterEqual(lab.series_parallel(values, "series")["equivalent_resistance"]["value"], max(values))
        self.assertLessEqual(lab.series_parallel(values, "parallel")["equivalent_resistance"]["value"], min(values))

    def test_equal_resistors_in_parallel_divide_by_count(self):
        self.assertAlmostEqual(lab.series_parallel([10000.0] * 3, "parallel")["equivalent_resistance"]["value"], 10000.0 / 3, places=9)
        self.assertAlmostEqual(lab.series_parallel([3000.0, 6000.0], "parallel")["equivalent_resistance"]["value"], 2000.0, places=9)

    def test_single_resistor_is_itself(self):
        for mode in ("series", "parallel"):
            self.assertAlmostEqual(lab.series_parallel([330.0], mode)["equivalent_resistance"]["value"], 330.0, places=12)

    def test_adding_parallel_branches_lowers_resistance(self):
        values = [lab.series_parallel([10000.0] * n, "parallel")["equivalent_resistance"]["value"] for n in (1, 2, 3, 4)]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_limiting_cases(self):
        self.assertAlmostEqual(lab.series_parallel([0.0, 100.0], "series")["equivalent_resistance"]["value"], 100.0, places=12)
        nearly = lab.series_parallel([100.0, 1.0e9], "parallel")["equivalent_resistance"]["value"]
        self.assertAlmostEqual(nearly / 100.0, 1.0, places=6)
        self.assertNotIn("equivalent_conductance", lab.series_parallel([0.0, 0.0], "series"))

    def test_accepts_tuple_and_mode_case(self):
        self.assertAlmostEqual(lab.series_parallel((100, 200), " Series ")["equivalent_resistance"]["value"], 300.0, places=12)

    def test_invalid_inputs_raise(self):
        cases = [
            ([], "series"), ([], "parallel"), ([100.0, -5.0], "series"), ([NAN], "parallel"), ([INF, 100.0], "series"),
            ([100.0, 0.0], "parallel"), ([100.0], "banana"), ("100", "series"), ([100.0, "200"], "series"), (None, "series"),
            ([True], "series"), ([100.0, False], "parallel"),
            ([1.0e308, 1.0e308], "series"), ([1.0e-320], "parallel"), ([1.0e-320, 1.0], "parallel"), ([1.0e-320], "series"),
        ]
        for resistances, mode in cases:
            with self.subTest(resistances=resistances, mode=mode):
                with self.assertRaises(ValueError):
                    lab.series_parallel(resistances, mode)
        with self.assertRaisesRegex(ValueError, "overflow"):
            lab.series_parallel([1.0e308, 1.0e308], "series")
        with self.assertRaisesRegex(ValueError, "too small"):
            lab.series_parallel([1.0e-320], "parallel")
        with self.assertRaisesRegex(ValueError, "empty"):
            lab.series_parallel([], "series")
        with self.assertRaisesRegex(ValueError, "short-circuits"):
            lab.series_parallel([100.0, 0.0], "parallel")
        with self.assertRaisesRegex(ValueError, "mode"):
            lab.series_parallel([100.0], "diagonal")


class VoltageDividerTests(unittest.TestCase):
    def test_default_loaded_divider(self):
        result = lab.voltage_divider(12.0, 10000.0, 10000.0, 10000.0)
        metadata_ok(self, result, "analytical-example")
        self.assertAlmostEqual(result["output_unloaded"]["value"], 6.0, places=12)
        self.assertAlmostEqual(result["output_loaded"]["value"], 4.0, places=12)
        self.assertAlmostEqual(result["loading_error"]["value"], -2.0, places=12)
        self.assertAlmostEqual(result["loading_error_relative"]["value"], -1.0 / 3.0, places=12)
        self.assertAlmostEqual(result["loading_error_percent"]["value"], -100.0 / 3.0, places=9)
        self.assertAlmostEqual(result["thevenin_voltage"]["value"], 6.0, places=12)
        self.assertAlmostEqual(result["thevenin_resistance"]["value"], 5000.0, places=9)
        self.assertAlmostEqual(result["r_bottom_parallel_load"]["value"], 5000.0, places=9)
        self.assertAlmostEqual(result["input_current_unloaded"]["value"], 0.0006, places=12)
        self.assertAlmostEqual(result["input_current_loaded"]["value"], 0.0008, places=12)
        self.assertAlmostEqual(result["load_current"]["value"], 0.0004, places=12)
        self.assertAlmostEqual(result["source_power_unloaded"]["value"], 0.0072, places=12)
        self.assertAlmostEqual(result["source_power_loaded"]["value"], 0.0096, places=12)
        quantity_ok(self, result["load_resistance"], "Ohm")
        quantity_ok(self, result["loading_error_relative"], "1")
        quantity_ok(self, result["loading_error_percent"], "%")

    def test_unloaded_divider(self):
        result = lab.voltage_divider(12.0, 10000.0, 10000.0)
        self.assertIsNone(result["load_resistance"])
        self.assertEqual(result["output_loaded"]["value"], result["output_unloaded"]["value"])
        self.assertEqual(result["loading_error"]["value"], 0.0)
        self.assertEqual(result["loading_error_relative"]["value"], 0.0)
        self.assertEqual(result["load_current"]["value"], 0.0)

    def test_thevenin_form_matches_direct_calculation(self):
        for r_load in (1000.0, 4700.0, 10000.0, 1.0e5):
            result = lab.voltage_divider(12.0, 10000.0, 10000.0, r_load)
            v_th = result["thevenin_voltage"]["value"]
            r_th = result["thevenin_resistance"]["value"]
            self.assertAlmostEqual(result["output_loaded"]["value"], v_th * r_load / (r_th + r_load), places=12)

    def test_loading_error_shrinks_as_load_grows(self):
        loads = (1000.0, 10000.0, 100000.0, 1.0e6, 1.0e9)
        errors = [abs(lab.voltage_divider(12.0, 10000.0, 10000.0, r)["loading_error"]["value"]) for r in loads]
        self.assertEqual(errors, sorted(errors, reverse=True))
        self.assertLess(errors[-1], 1.0e-4)
        self.assertAlmostEqual(lab.voltage_divider(12.0, 10000.0, 10000.0, 1000.0)["output_loaded"]["value"], 1.0, places=12)

    def test_relative_error_independent_of_input_voltage(self):
        twelve = lab.voltage_divider(12.0, 10000.0, 10000.0, 10000.0)["loading_error_relative"]["value"]
        five = lab.voltage_divider(5.0, 10000.0, 10000.0, 10000.0)["loading_error_relative"]["value"]
        self.assertAlmostEqual(twelve, five, places=12)

    def test_stiffer_divider_trades_error_for_power(self):
        soft = lab.voltage_divider(12.0, 10000.0, 10000.0, 10000.0)
        stiff = lab.voltage_divider(12.0, 1000.0, 1000.0, 10000.0)
        self.assertLess(abs(stiff["loading_error_relative"]["value"]), abs(soft["loading_error_relative"]["value"]))
        self.assertGreater(stiff["source_power_loaded"]["value"], soft["source_power_loaded"]["value"])
        self.assertAlmostEqual(stiff["output_loaded"]["value"], 12.0 * (1000.0 * 10000.0 / 11000.0) / (1000.0 + 1000.0 * 10000.0 / 11000.0), places=12)

    def test_limiting_ratios(self):
        self.assertLess(lab.voltage_divider(12.0, 1.0e9, 10.0)["output_unloaded"]["value"], 1.0e-6)
        self.assertAlmostEqual(lab.voltage_divider(12.0, 10.0, 1.0e9)["output_unloaded"]["value"] / 12.0, 1.0, places=6)
        zero = lab.voltage_divider(0.0, 10000.0, 10000.0, 10000.0)
        self.assertEqual(zero["output_loaded"]["value"], 0.0)
        self.assertAlmostEqual(zero["loading_error_relative"]["value"], -1.0 / 3.0, places=12)
        self.assertAlmostEqual(lab.voltage_divider(-12.0, 10000.0, 10000.0, 10000.0)["output_loaded"]["value"], -4.0, places=12)

    def test_invalid_inputs_raise(self):
        cases = [
            (12.0, 0.0, 10000.0, None), (12.0, 10000.0, 0.0, None), (12.0, 10000.0, 10000.0, 0.0),
            (12.0, -1.0, 10000.0, None), (12.0, 10000.0, -1.0, None), (12.0, 10000.0, 10000.0, -10.0),
            (NAN, 10000.0, 10000.0, None), (12.0, INF, 10000.0, None), (12.0, 10000.0, 10000.0, INF), (12.0, 10000.0, 10000.0, NAN),
            ("12", 10000.0, 10000.0, None),
            (True, 10000.0, 10000.0, None), (12.0, True, 10000.0, None), (12.0, 10000.0, 10000.0, False),
            (12.0, 1.0e308, 1.0e308, None), (12.0, 10000.0, 10000.0, 1.0e308), (12.0, 1.0e-320, 10000.0, None),
        ]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    lab.voltage_divider(*args)
        with self.assertRaisesRegex(ValueError, "r_load"):
            lab.voltage_divider(12.0, 10000.0, 10000.0, 0.0)
        with self.assertRaisesRegex(ValueError, "overflow"):
            lab.voltage_divider(12.0, 1.0e308, 1.0e308)


class NetworkSolverTests(unittest.TestCase):
    def test_loaded_divider_example(self):
        result = lab.solve_network(lab.example_network("loaded-divider"))
        metadata_ok(self, result, "numerical-simulation")
        self.assertEqual(result["unknowns"], 3)
        self.assertAlmostEqual(result["node_voltages"]["in"]["value"], 12.0, places=12)
        self.assertAlmostEqual(result["node_voltages"]["out"]["value"], 4.0, places=12)
        self.assertEqual(result["node_voltages"]["0"]["value"], 0.0)
        by_name = {b["name"]: b for b in result["branches"]}
        self.assertAlmostEqual(by_name["Rtop"]["current"]["value"], 0.0008, places=12)
        self.assertAlmostEqual(by_name["Rbottom"]["current"]["value"], 0.0004, places=12)
        self.assertAlmostEqual(by_name["Rload"]["current"]["value"], 0.0004, places=12)
        self.assertAlmostEqual(by_name["V1"]["current"]["value"], -0.0008, places=12)
        self.assertAlmostEqual(by_name["V1"]["power"]["value"], -0.0096, places=12)
        self.assertAlmostEqual(result["checks"]["power_dissipated_by_resistors"]["value"], 0.0096, places=12)
        self.assertAlmostEqual(result["checks"]["power_supplied_by_sources"]["value"], 0.0096, places=12)
        self.assertLess(result["checks"]["max_kcl_residual"]["value"], 1.0e-15)
        self.assertTrue(result["checks"]["passes"])
        quantity_ok(self, by_name["Rtop"]["value"], "Ohm")
        quantity_ok(self, by_name["V1"]["value"], "V")

    def test_nodal_matches_analytical_divider(self):
        for v_in, r_top, r_bottom, r_load in ((12.0, 10000.0, 10000.0, 10000.0), (5.0, 1000.0, 2200.0, 4700.0), (3.3, 470.0, 330.0, 1.0e6)):
            branches = [
                {"type": "V", "nodes": ["in", "0"], "value": v_in},
                {"type": "R", "nodes": ["in", "out"], "value": r_top},
                {"type": "R", "nodes": ["out", "0"], "value": r_bottom},
                {"type": "R", "nodes": ["out", "0"], "value": r_load},
            ]
            expected = lab.voltage_divider(v_in, r_top, r_bottom, r_load)["output_loaded"]["value"]
            self.assertAlmostEqual(lab.solve_network(branches)["node_voltages"]["out"]["value"], expected, places=10)

    def test_two_source_example_and_superposition(self):
        result = lab.solve_network(lab.example_network("two-source"))
        by_name = {b["name"]: b for b in result["branches"]}
        self.assertAlmostEqual(result["node_voltages"]["n2"]["value"], 10.0, places=10)
        self.assertAlmostEqual(by_name["R1"]["current"]["value"], 0.001, places=12)
        self.assertAlmostEqual(by_name["R2"]["current"]["value"], 0.0025, places=12)
        self.assertAlmostEqual(by_name["I1"]["power"]["value"], -0.015, places=12)
        self.assertAlmostEqual(by_name["V1"]["power"]["value"], -0.012, places=12)
        self.assertAlmostEqual(result["checks"]["power_dissipated_by_resistors"]["value"], 0.027, places=12)
        self.assertTrue(result["checks"]["passes"])
        voltage_only = lab.example_network("two-source")
        voltage_only[3]["value"] = 0.0
        current_only = lab.example_network("two-source")
        current_only[0]["value"] = 0.0
        v_alone = lab.solve_network(voltage_only)["node_voltages"]["n2"]["value"]
        i_alone = lab.solve_network(current_only)["node_voltages"]["n2"]["value"]
        self.assertAlmostEqual(v_alone, 8.0, places=10)
        self.assertAlmostEqual(i_alone, 2.0, places=10)
        self.assertAlmostEqual(v_alone + i_alone, 10.0, places=10)

    def test_single_resistor_example(self):
        result = lab.solve_network(lab.example_network("single-resistor"))
        by_name = {b["name"]: b for b in result["branches"]}
        self.assertAlmostEqual(by_name["R1"]["current"]["value"], 0.02, places=12)
        self.assertAlmostEqual(by_name["R1"]["power"]["value"], 0.12, places=12)

    def test_current_source_sign_convention(self):
        forward = lab.solve_network([{"type": "I", "nodes": ["0", "a"], "value": 0.001}, {"type": "R", "nodes": ["a", "0"], "value": 1000.0}])
        reverse = lab.solve_network([{"type": "I", "nodes": ["a", "0"], "value": 0.001}, {"type": "R", "nodes": ["a", "0"], "value": 1000.0}])
        self.assertAlmostEqual(forward["node_voltages"]["a"]["value"], 1.0, places=12)
        self.assertAlmostEqual(reverse["node_voltages"]["a"]["value"], -1.0, places=12)

    def test_integer_labels_and_alternative_ground(self):
        result = lab.solve_network([{"type": "V", "nodes": [1, 0], "value": 6.0}, {"type": "R", "nodes": [1, 0], "value": 300.0}], ground=0)
        self.assertAlmostEqual(result["node_voltages"]["1"]["value"], 6.0, places=12)
        shifted = lab.solve_network(lab.example_network("loaded-divider"), ground="in")
        self.assertAlmostEqual(shifted["node_voltages"]["out"]["value"], -8.0, places=12)
        self.assertAlmostEqual(shifted["node_voltages"]["0"]["value"], -12.0, places=12)
        self.assertTrue(shifted["checks"]["passes"])

    def test_ladder_network_is_monotonic_and_conservative(self):
        branches = [{"type": "V", "nodes": ["n0", "0"], "value": 10.0}]
        for k in range(1, 11):
            branches.append({"type": "R", "nodes": [f"n{k - 1}", f"n{k}"], "value": 100.0})
            branches.append({"type": "R", "nodes": [f"n{k}", "0"], "value": 1000.0})
        result = lab.solve_network(branches)
        voltages = [result["node_voltages"][f"n{k}"]["value"] for k in range(11)]
        self.assertEqual(voltages, sorted(voltages, reverse=True))
        self.assertGreater(voltages[-1], 0.0)
        self.assertTrue(result["checks"]["passes"])
        self.assertEqual(result["unknowns"], 12)

    def test_checks_report_tolerances_that_stay_small_at_teaching_scale(self):
        checks = lab.solve_network(lab.example_network("loaded-divider"))["checks"]
        quantity_ok(self, checks["kcl_tolerance"], "A")
        quantity_ok(self, checks["power_tolerance"], "W")
        # 1e-9 of the largest current (0.8 mA) plus a rounding floor far below it.
        self.assertGreater(checks["kcl_tolerance"]["value"], 8.0e-13)
        self.assertLess(checks["kcl_tolerance"]["value"], 1.0e-12)
        self.assertLess(checks["power_tolerance"]["value"], 1.0e-11)
        self.assertGreaterEqual(checks["kcl_tolerance"]["value"], checks["max_kcl_residual"]["value"])

    def test_checks_pass_for_widely_spread_resistances(self):
        # The node voltages are exact to rounding, but the small resistor's
        # current is the difference of two nearly equal voltages; the
        # tolerances must allow for that floor instead of flagging a correct
        # solution as a conservation failure.
        for r_small, r_large in ((1.0e-3, 1.0e5), (1.0, 1.0e8), (1.0, 1.0e9), (1.0, 1.0e10), (1.0, 1.0e12), (100.0, 1.0e12)):
            with self.subTest(r_small=r_small, r_large=r_large):
                result = lab.solve_network([
                    {"type": "V", "nodes": ["a", "0"], "value": 12.0},
                    {"type": "R", "nodes": ["a", "b"], "value": r_small},
                    {"type": "R", "nodes": ["b", "0"], "value": r_large},
                ])
                expected = lab.voltage_divider(12.0, r_small, r_large)["output_unloaded"]["value"]
                self.assertAlmostEqual(result["node_voltages"]["b"]["value"], expected, places=12)
                self.assertTrue(result["checks"]["passes"], result["checks"])
                self.assertIn("rounding floor", " ".join(result["limitations"]))

    def test_documented_pivot_boundary(self):
        def divider(r):
            return [
                {"type": "V", "nodes": ["in", "0"], "value": 12.0},
                {"type": "R", "nodes": ["in", "out"], "value": r},
                {"type": "R", "nodes": ["out", "0"], "value": r},
            ]
        self.assertAlmostEqual(lab.solve_network(divider(1.0e13))["node_voltages"]["out"]["value"], 6.0, places=9)
        with self.assertRaisesRegex(ValueError, "singular"):
            lab.solve_network(divider(1.0e14))
        lone = lab.solve_network([{"type": "V", "nodes": ["a", "0"], "value": 12.0}, {"type": "R", "nodes": ["a", "0"], "value": 1.0e14}])
        self.assertAlmostEqual(lone["branches"][1]["current"]["value"], 1.2e-13, places=20)
        self.assertTrue(lone["checks"]["passes"])

    def test_gaussian_elimination_directly(self):
        x = lab.gaussian_elimination([[2.0, 1.0], [1.0, 3.0]], [3.0, 5.0])
        self.assertAlmostEqual(x[0], 0.8, places=12)
        self.assertAlmostEqual(x[1], 1.4, places=12)
        pivoted = lab.gaussian_elimination([[0.0, 1.0], [1.0, 0.0]], [2.0, 3.0])
        self.assertAlmostEqual(pivoted[0], 3.0, places=12)
        self.assertAlmostEqual(pivoted[1], 2.0, places=12)
        with self.assertRaisesRegex(ValueError, "singular"):
            lab.gaussian_elimination([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
        with self.assertRaises(ValueError):
            lab.gaussian_elimination([[1.0, 2.0]], [1.0, 2.0])

    def test_node_currents_helper(self):
        result = lab.solve_network(lab.example_network("loaded-divider"))
        currents = lab.node_currents(result, "out")
        self.assertEqual(len(currents), 3)
        self.assertAlmostEqual(sum(currents), 0.0, places=15)
        self.assertAlmostEqual(min(currents), -0.0008, places=12)
        with self.assertRaises(ValueError):
            lab.node_currents(result, "nowhere")

    def test_example_network_returns_copies(self):
        first = lab.example_network("two-source")
        first[0]["value"] = 99.0
        first[0]["nodes"][0] = "changed"
        self.assertEqual(lab.example_network("two-source")[0]["value"], 12.0)
        self.assertEqual(lab.example_network("two-source")[0]["nodes"][0], "n1")
        with self.assertRaises(ValueError):
            lab.example_network("no-such-example")

    def test_invalid_networks_raise(self):
        chain = [{"type": "V", "nodes": ["n1", "0"], "value": 1.0}]
        chain += [{"type": "R", "nodes": [f"n{k}", f"n{k + 1}"], "value": 10.0} for k in range(1, 52)]
        cases = {
            "empty": [],
            "floating node": [{"type": "V", "nodes": ["a", "0"], "value": 6.0}, {"type": "R", "nodes": ["a", "b"], "value": 100.0}, {"type": "I", "nodes": ["b", "c"], "value": 0.001}],
            "voltage source loop": [{"type": "V", "nodes": ["a", "0"], "value": 6.0}, {"type": "V", "nodes": ["a", "0"], "value": 5.0}],
            "same node": [{"type": "R", "nodes": ["a", "a"], "value": 100.0}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "zero ohm": [{"type": "R", "nodes": ["a", "0"], "value": 0.0}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "negative ohm": [{"type": "R", "nodes": ["a", "0"], "value": -100.0}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "nan source": [{"type": "R", "nodes": ["a", "0"], "value": 100.0}, {"type": "V", "nodes": ["a", "0"], "value": NAN}],
            "inf resistor": [{"type": "R", "nodes": ["a", "0"], "value": INF}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "unknown type": [{"type": "X", "nodes": ["a", "0"], "value": 100.0}],
            "missing value": [{"type": "R", "nodes": ["a", "0"]}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "bad nodes": [{"type": "R", "nodes": ["a"], "value": 100.0}],
            "duplicate names": [{"name": "X", "type": "R", "nodes": ["a", "0"], "value": 100.0}, {"name": "X", "type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "not a dict": [("R", "a", "0", 100.0)],
            "string": "R,a,0,100",
            "too many unknowns": chain,
            "bool resistance": [{"type": "R", "nodes": ["a", "0"], "value": True}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "bool source": [{"type": "R", "nodes": ["a", "0"], "value": 100.0}, {"type": "V", "nodes": ["a", "0"], "value": False}],
            "subnormal resistor": [{"type": "R", "nodes": ["a", "0"], "value": 1.0e-320}, {"type": "V", "nodes": ["a", "0"], "value": 6.0}],
            "overflowing source": [{"type": "R", "nodes": ["a", "0"], "value": 100.0}, {"type": "V", "nodes": ["a", "0"], "value": 10 ** 400}],
        }
        for label, branches in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    lab.solve_network(branches)
        with self.assertRaisesRegex(ValueError, "ground"):
            lab.solve_network(lab.example_network("two-source"), ground="zz")
        with self.assertRaisesRegex(ValueError, "floating"):
            lab.solve_network(cases["floating node"])
        with self.assertRaisesRegex(ValueError, "loop"):
            lab.solve_network(cases["voltage source loop"])
        with self.assertRaisesRegex(ValueError, "limited"):
            lab.solve_network(chain)


class ConservationCheckTests(unittest.TestCase):
    def test_default_example_currents_and_loop(self):
        # Currents at the output node, positive when leaving it (the lab's
        # convention): 0.8 mA arrives through R_top, 0.4 mA leaves through each
        # lower branch.  The loop walks up through the source (a rise, negative)
        # and down through both drops.
        result = lab.kcl_kvl_check(branch_currents=[-0.0008, 0.0004, 0.0004], loop_voltages=[-12.0, 8.0, 4.0])
        metadata_ok(self, result, "analytical-example")
        self.assertTrue(result["passes"])
        self.assertTrue(result["kcl"]["passes"])
        self.assertTrue(result["kvl"]["passes"])
        self.assertAlmostEqual(result["kcl"]["sum"]["value"], 0.0, places=15)
        self.assertEqual(result["kcl"]["count"], 3)
        # Either consistent choice of positive direction passes.
        self.assertTrue(lab.kcl_kvl_check(branch_currents=[0.0008, -0.0004, -0.0004])["passes"])
        quantity_ok(self, result["kvl"]["sum"], "V")
        quantity_ok(self, result["kcl"]["tolerance"], "A")

    def test_failure_is_reported_not_raised(self):
        result = lab.kcl_kvl_check(branch_currents=[0.02, -0.01])
        self.assertFalse(result["passes"])
        self.assertFalse(result["kcl"]["passes"])
        self.assertNotIn("kvl", result)
        self.assertAlmostEqual(result["kcl"]["sum"]["value"], 0.01, places=12)

    def test_tolerance_controls_rounded_hand_values(self):
        rounded = [0.6667, -0.3333, -0.3333]
        self.assertFalse(lab.kcl_kvl_check(branch_currents=rounded)["passes"])
        self.assertTrue(lab.kcl_kvl_check(branch_currents=rounded, rel_tol=1e-3)["passes"])
        self.assertTrue(lab.kcl_kvl_check(loop_voltages=[-12.0, 8.0, 4.0], rel_tol=0.0, abs_tol=1e-12)["passes"])

    def test_invalid_inputs_raise(self):
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check()
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(branch_currents=[])
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(loop_voltages=[1.0, NAN])
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(branch_currents=[1.0, INF, -1.0])
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(branch_currents="0.1,-0.1")
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(branch_currents=[0.1, -0.1], rel_tol=-1.0)
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(branch_currents=[0.1, -0.1], abs_tol=NAN)
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(branch_currents=[True, -1.0])
        with self.assertRaises(ValueError):
            lab.kcl_kvl_check(loop_voltages=[1.0, -1.0], rel_tol=True)
        with self.assertRaisesRegex(ValueError, "overflow"):
            lab.kcl_kvl_check(branch_currents=[1.0e308, 1.0e308])


class DefaultExampleTests(unittest.TestCase):
    def test_default_example_values(self):
        result = lab.default_example()
        metadata_ok(self, result, "analytical-example")
        self.assertAlmostEqual(result["ohm"]["current"]["value"], 0.02, places=12)
        self.assertAlmostEqual(result["power_energy"]["energy"]["value"], 216.0, places=9)
        self.assertAlmostEqual(result["series"]["equivalent_resistance"]["value"], 20000.0, places=9)
        self.assertAlmostEqual(result["parallel"]["equivalent_resistance"]["value"], 5000.0, places=9)
        self.assertAlmostEqual(result["voltage_divider"]["output_loaded"]["value"], 4.0, places=12)
        self.assertAlmostEqual(result["network"]["node_voltages"]["out"]["value"], 4.0, places=12)
        self.assertEqual(result["network"]["validation_status"], "numerical-simulation")
        self.assertLess(abs(result["cross_check"]["difference"]["value"]), 1.0e-12)
        self.assertTrue(result["kcl_kvl_check"]["passes"])
        self.assertTrue(result["network"]["checks"]["passes"])

    def test_default_example_is_deterministic_and_json_safe(self):
        first = json.dumps(lab.default_example(), allow_nan=False, sort_keys=True)
        second = json.dumps(lab.default_example(), allow_nan=False, sort_keys=True)
        self.assertEqual(first, second)
        self.assertTrue(first.isascii())

    def test_every_result_carries_the_lab_version(self):
        results = [
            lab.ohm(v=6.0, r=300.0),
            lab.power_energy(6.0, 0.02, 0.5),
            lab.series_parallel([10000.0, 10000.0], "series"),
            lab.voltage_divider(12.0, 10000.0, 10000.0, 10000.0),
            lab.solve_network(lab.example_network("loaded-divider")),
            lab.kcl_kvl_check(branch_currents=[-0.0008, 0.0004, 0.0004]),
            lab.default_example(),
        ]
        for result in results:
            with self.subTest(model=result["model"]):
                self.assertEqual(result["lab_version"], lab.__version__)
        self.assertRegex(lab.__version__, r"^\d+\.\d+\.\d+$")


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(LAB_PATH), *args], capture_output=True, text=True, timeout=60, cwd=str(ROOT))

    def test_default_run_prints_json(self):
        completed = self.run_cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertAlmostEqual(payload["voltage_divider"]["output_loaded"]["value"], 4.0, places=12)
        self.assertAlmostEqual(payload["ohm"]["current"]["value"], 0.02, places=12)
        self.assertEqual(completed.stderr, "")

    def test_json_flag_and_subcommands(self):
        completed = self.run_cli("--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertAlmostEqual(json.loads(completed.stdout)["power_energy"]["energy_watt_hours"]["value"], 0.06, places=12)
        ohm = self.run_cli("ohm", "--v", "6", "--r", "300")
        self.assertEqual(ohm.returncode, 0, ohm.stderr)
        self.assertAlmostEqual(json.loads(ohm.stdout)["current"]["value"], 0.02, places=12)
        network = self.run_cli("network", "--example", "two-source")
        self.assertEqual(network.returncode, 0, network.stderr)
        self.assertAlmostEqual(json.loads(network.stdout)["node_voltages"]["n2"]["value"], 10.0, places=10)
        branches = self.run_cli("network", "--branch", "V,in,0,12", "--branch", "R,in,out,10000", "--branch", "R,out,0,10000,Rbottom")
        self.assertEqual(branches.returncode, 0, branches.stderr)
        self.assertAlmostEqual(json.loads(branches.stdout)["node_voltages"]["out"]["value"], 6.0, places=10)
        check = self.run_cli("check", "--currents", "-0.0008", "0.0004", "0.0004", "--voltages", "-12", "8", "4")
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertTrue(json.loads(check.stdout)["passes"])
        self.assertEqual(check.stderr, "")

    def test_invalid_input_exits_with_code_2(self):
        completed = self.run_cli("ohm", "--v", "6", "--r", "0")
        self.assertEqual(completed.returncode, 2)
        self.assertTrue(completed.stderr.startswith("error:"), completed.stderr)
        self.assertIn("0 Ohm", completed.stderr)
        self.assertEqual(completed.stdout, "")
        negative = self.run_cli("divider", "--r-load", "-5")
        self.assertEqual(negative.returncode, 2)
        self.assertTrue(negative.stderr.startswith("error:"), negative.stderr)

    def test_error_paths_exit_with_code_2_and_no_stdout(self):
        cases = {
            "fsum overflow": ["series", "1e308", "1e308"],
            "check overflow": ["check", "--currents", "1e308", "1e308"],
            "result overflow": ["ohm", "--v", "1e308", "--i", "1e-308"],
            "divider overflow": ["divider", "--r-top", "1e308", "--r-bottom", "1e308"],
            "subnormal resistance": ["parallel", "1e-320"],
            "network without input": ["network"],
            "example and branch": ["network", "--example", "two-source", "--branch", "R,a,0,100"],
            "short branch": ["network", "--branch", "R,a,0"],
            "non-numeric branch": ["network", "--branch", "R,a,0,abc"],
            "check without lists": ["check"],
        }
        for label, args in cases.items():
            with self.subTest(case=label):
                completed = self.run_cli(*args)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertEqual(completed.stdout, "")
                self.assertTrue(completed.stderr.startswith("error:"), completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)

    def test_help_exits_zero(self):
        completed = self.run_cli("--help")
        self.assertEqual(completed.returncode, 0)
        self.assertIn("divider", completed.stdout)

    def test_plot_without_target_is_harmless(self):
        completed = self.run_cli("--plot", "check", "--currents", "0.01", "-0.01")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("nothing to plot", completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["passes"])  # stdout stays pure JSON

    def test_out_without_plot_warns_on_stderr(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "ignored.png"
            completed = self.run_cli("--out", str(target), "ohm", "--v", "6", "--r", "300")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("--out has no effect without --plot", completed.stderr)
            self.assertFalse(target.exists())
            self.assertAlmostEqual(json.loads(completed.stdout)["current"]["value"], 0.02, places=12)

    def test_default_run_is_fast(self):
        started = time.perf_counter()
        completed = self.run_cli()
        elapsed = time.perf_counter() - started
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertLess(elapsed, 3.0, f"default run took {elapsed:.2f} s")

    def test_import_has_no_side_effects(self):
        code = (
            "import contextlib, importlib.util, io, sys\n"
            "out, err = io.StringIO(), io.StringIO()\n"
            "with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):\n"
            "    spec = importlib.util.spec_from_file_location('dc_circuits_import_check', sys.argv[1])\n"
            "    module = importlib.util.module_from_spec(spec)\n"
            "    spec.loader.exec_module(module)\n"
            "print(len(out.getvalue()), len(err.getvalue()), 'matplotlib' in sys.modules, module.__version__)\n"
        )
        completed = subprocess.run([sys.executable, "-c", code, str(LAB_PATH)], capture_output=True, text=True, timeout=60, cwd=str(ROOT))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.split(), ["0", "0", "False", lab.__version__])

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib not installed")
    def test_plot_writes_file_when_matplotlib_available(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "loading.png"
            notices = io.StringIO()
            with contextlib.redirect_stderr(notices):
                produced = lab.plot_loading_curve(12.0, 10000.0, 10000.0, 10000.0, out=str(target))
            self.assertTrue(produced)
            self.assertGreater(target.stat().st_size, 0)
            self.assertIn("plot written to", notices.getvalue())
            import matplotlib.pyplot as plt
            self.assertEqual(plt.get_fignums(), [])  # the figure was closed

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib not installed")
    def test_plot_flag_on_default_example_keeps_stdout_json(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "default.png"
            completed = self.run_cli("--plot", "--out", str(target))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertAlmostEqual(payload["voltage_divider"]["output_loaded"]["value"], 4.0, places=12)
            self.assertIn("plot written to", completed.stderr)
            self.assertGreater(target.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
