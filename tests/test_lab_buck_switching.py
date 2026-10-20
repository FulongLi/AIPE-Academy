"""Tests for labs/power-electronics/buck_switching.py.

Covers the design point's analytical values, parameter-variation trends,
limiting cases (CCM/DCM boundary, DCM light load), input validation,
numerical robustness (stability guard, divergence, waveform output, missing
matplotlib) and the command line (exit codes 0 and 2, parseable JSON).
Standard library only; runs in a few seconds on Windows and Linux.
"""
import contextlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LAB_PATH = ROOT / "labs" / "power-electronics" / "buck_switching.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lab = load("buck_switching", "labs/power-electronics/buck_switching.py")
buck_open = load("buck_open", "labs/buck_open.py")


class DefaultCaseTests(unittest.TestCase):
    """24 V -> 12 V, 30 W, 100 kHz, 150 uH, 100 uF: the lesson's design point."""

    @classmethod
    def setUpClass(cls):
        cls.result = lab.simulate()
        cls.steady = cls.result["steady_state"]

    def test_metadata_units_and_serialisation(self):
        result = self.result
        self.assertEqual(result["model"], "ideal-buck-switching-simulation")
        self.assertEqual(result["validation_status"], "numerical-simulation")
        self.assertTrue(result["assumptions"])
        self.assertTrue(result["limitations"])
        self.assertEqual(self.steady["output_voltage_mean"]["unit"], "V")
        self.assertEqual(self.steady["inductor_current_mean"]["unit"], "A")
        self.assertEqual(result["inputs"]["load_resistance"]["unit"], "Ohm")
        self.assertEqual(result["inputs"]["inductance"]["unit"], "H")
        self.assertEqual(result["numerical_method"]["steps_on"] + result["numerical_method"]["steps_off"], 200)
        json.dumps(result, allow_nan=False)

    def test_settles_in_continuous_conduction(self):
        self.assertTrue(self.result["settling"]["settled"])
        self.assertGreater(self.result["settling"]["cycles_simulated"], 100)
        self.assertEqual(self.steady["conduction_mode"], "CCM")
        self.assertEqual(self.steady["zero_current_fraction"]["value"], 0.0)
        self.assertAlmostEqual(self.steady["diode_conduction_fraction"]["value"], 0.5, places=12)
        self.assertTrue(self.result["comparison"]["mode_agrees"])
        self.assertEqual(self.result["comparison"]["reference_model"], "analytical-ccm")
        self.assertEqual(self.result["warnings"], [])

    def test_matches_ideal_ccm_analysis(self):
        steady = self.steady
        self.assertAlmostEqual(steady["output_voltage_mean"]["value"], 12.0, places=3)
        self.assertAlmostEqual(steady["inductor_current_mean"]["value"], 2.5, places=3)
        self.assertAlmostEqual(steady["inductor_ripple_pp"]["value"], 0.4, places=3)
        self.assertAlmostEqual(steady["inductor_current_min"]["value"], 2.3, places=3)
        self.assertAlmostEqual(steady["inductor_current_max"]["value"], 2.7, places=3)
        self.assertAlmostEqual(steady["output_voltage_ripple_pp"]["value"], 0.005, delta=2.5e-5)
        self.assertAlmostEqual(steady["input_current_mean"]["value"], 1.25, places=3)
        self.assertAlmostEqual(steady["input_power"]["value"], 30.0, places=2)
        self.assertAlmostEqual(steady["power_balance_error"]["value"], 0.0, places=3)
        for name, value in self.result["comparison"]["relative_difference"].items():
            self.assertLess(abs(value["value"]), 5e-3, name)

    def test_analytical_block_reproduces_buck_open(self):
        reference = buck_open.calculate()
        analytical = self.result["analytical_ccm"]
        self.assertAlmostEqual(analytical["duty_ratio"]["value"], reference["duty_ratio"]["value"], places=12)
        self.assertAlmostEqual(analytical["inductor_current_mean"]["value"], reference["output_current"]["value"], places=12)
        self.assertAlmostEqual(analytical["inductor_ripple_pp"]["value"], reference["inductor_ripple_pp"]["value"], places=12)
        self.assertAlmostEqual(analytical["inductor_current_min"]["value"], reference["inductor_current_min"]["value"], places=12)
        self.assertAlmostEqual(analytical["load_resistance"]["value"], reference["load_resistance"]["value"], places=12)
        self.assertAlmostEqual(analytical["output_voltage_ripple_pp"]["value"], 0.005, places=12)

    def test_startup_overshoot_of_lightly_damped_filter(self):
        # zeta = sqrt(L/C) / (2R) = 0.128, so the cold-start peak is V (1 + exp(-pi zeta / sqrt(1 - zeta^2))).
        zeta = math.sqrt(0.00015 / 0.0001) / (2.0 * 4.8)
        expected = 12.0 * (1.0 + math.exp(-math.pi * zeta / math.sqrt(1.0 - zeta * zeta)))
        self.assertAlmostEqual(self.result["startup"]["peak_output_voltage"]["value"], expected, delta=0.1)
        self.assertGreater(self.result["startup"]["peak_inductor_current"]["value"], 2.7)

    def test_conduction_boundary_block(self):
        boundary = self.result["conduction_boundary"]
        self.assertAlmostEqual(boundary["k"]["value"], 6.25, places=9)
        self.assertAlmostEqual(boundary["k_critical"]["value"], 0.5, places=12)
        self.assertEqual(boundary["predicted_mode"], "CCM")
        self.assertAlmostEqual(boundary["boundary_output_current"]["value"], 0.2, places=12)
        self.assertAlmostEqual(boundary["boundary_load_resistance"]["value"], 60.0, places=9)
        self.assertAlmostEqual(boundary["boundary_power"]["value"], 2.4, places=9)
        self.assertIsNone(self.result["analytical_dcm"])


class ParameterTrendTests(unittest.TestCase):
    def test_doubling_frequency_halves_both_ripples(self):
        result = lab.simulate(frequency=200000.0)
        steady = result["steady_state"]
        self.assertAlmostEqual(steady["inductor_ripple_pp"]["value"], 0.2, places=3)
        self.assertAlmostEqual(steady["inductor_current_min"]["value"], 2.4, places=3)
        self.assertAlmostEqual(steady["output_voltage_ripple_pp"]["value"], 0.00125, delta=1e-5)
        self.assertAlmostEqual(steady["output_voltage_mean"]["value"], 12.0, places=3)
        reference = buck_open.calculate(frequency=200000.0)
        self.assertAlmostEqual(result["analytical_ccm"]["inductor_ripple_pp"]["value"],
                               reference["inductor_ripple_pp"]["value"], places=12)

    def test_output_follows_input_voltage_at_fixed_duty(self):
        low = lab.simulate(v_in=20.0, duty=0.5, load_resistance=4.8)["steady_state"]
        high = lab.simulate(v_in=28.0, duty=0.5, load_resistance=4.8)["steady_state"]
        self.assertAlmostEqual(low["output_voltage_mean"]["value"], 10.0, places=3)
        self.assertAlmostEqual(high["output_voltage_mean"]["value"], 14.0, places=3)
        self.assertGreater(high["inductor_ripple_pp"]["value"], low["inductor_ripple_pp"]["value"])
        self.assertAlmostEqual(high["inductor_ripple_pp"]["value"] / low["inductor_ripple_pp"]["value"], 1.4, places=3)

    def test_output_and_ripple_independent_of_load_in_ccm(self):
        steady = lab.simulate(load_resistance=9.6)["steady_state"]
        self.assertEqual(steady["conduction_mode"], "CCM")
        self.assertAlmostEqual(steady["output_voltage_mean"]["value"], 12.0, places=3)
        self.assertAlmostEqual(steady["inductor_current_mean"]["value"], 1.25, places=3)
        self.assertAlmostEqual(steady["inductor_ripple_pp"]["value"], 0.4, places=3)
        self.assertAlmostEqual(steady["output_voltage_ripple_pp"]["value"], 0.005, delta=2.5e-5)

    def test_halving_inductance_doubles_ripple(self):
        steady = lab.simulate(inductance=0.000075)["steady_state"]
        self.assertAlmostEqual(steady["inductor_ripple_pp"]["value"], 0.8, places=3)
        self.assertAlmostEqual(steady["output_voltage_ripple_pp"]["value"], 0.01, delta=5e-5)
        self.assertAlmostEqual(steady["inductor_current_mean"]["value"], 2.5, places=3)

    def test_smaller_capacitance_raises_only_the_voltage_ripple(self):
        steady = lab.simulate(capacitance=0.00001)["steady_state"]
        self.assertAlmostEqual(steady["output_voltage_ripple_pp"]["value"], 0.05, delta=2.5e-4)
        self.assertAlmostEqual(steady["inductor_ripple_pp"]["value"], 0.4, places=2)
        self.assertAlmostEqual(steady["output_voltage_mean"]["value"], 12.0, places=3)

    def test_duty_ratio_sets_the_output(self):
        result = lab.simulate(duty=0.25)
        self.assertAlmostEqual(result["inputs"]["load_resistance"]["value"], 1.2, places=12)
        self.assertAlmostEqual(result["steady_state"]["output_voltage_mean"]["value"], 6.0, places=3)
        self.assertAlmostEqual(result["steady_state"]["inductor_current_mean"]["value"], 5.0, places=3)
        self.assertAlmostEqual(result["steady_state"]["inductor_ripple_pp"]["value"], 0.3, places=3)

    def test_step_refinement_changes_steady_state_only_slightly(self):
        fine = lab.simulate(steps_per_cycle=400)["steady_state"]
        for steps in (40, 100):
            coarse = lab.simulate(steps_per_cycle=steps)["steady_state"]
            for key in ("output_voltage_mean", "inductor_current_mean", "inductor_ripple_pp", "output_voltage_ripple_pp"):
                relative = abs(coarse[key]["value"] - fine[key]["value"]) / fine[key]["value"]
                self.assertLess(relative, 2e-3, f"{key} at {steps} steps")

    def test_odd_on_interval_step_count_is_less_accurate_but_bounded(self):
        # D*N odd (50 steps at D = 0.5) puts one ripple extremum between steps: a larger, still first-order, error.
        def ripple_error(steps):
            result = lab.simulate(steps_per_cycle=steps)
            return abs(result["comparison"]["relative_difference"]["output_voltage_ripple_pp"]["value"])
        twenty, fifty = ripple_error(20), ripple_error(50)
        self.assertLess(twenty, 2e-3)
        self.assertLess(fifty, 3e-3)
        self.assertGreater(fifty, twenty)


class ConductionModeTests(unittest.TestCase):
    def test_light_load_enters_dcm_and_matches_dcm_analysis(self):
        result = lab.simulate(load_resistance=120.0)
        steady = result["steady_state"]
        self.assertTrue(result["settling"]["settled"])
        self.assertEqual(steady["conduction_mode"], "DCM")
        self.assertEqual(steady["inductor_current_min"]["value"], 0.0)
        self.assertGreater(steady["zero_current_fraction"]["value"], 0.1)
        self.assertEqual(result["conduction_boundary"]["predicted_mode"], "DCM")
        self.assertEqual(result["comparison"]["reference_model"], "analytical-dcm")
        self.assertTrue(result["comparison"]["mode_agrees"])
        expected = 24.0 * lab.dcm_conversion_ratio(0.5, 0.25)
        self.assertAlmostEqual(steady["output_voltage_mean"]["value"], expected, delta=0.01)
        self.assertGreater(steady["output_voltage_mean"]["value"], 12.5)
        self.assertAlmostEqual(steady["inductor_current_max"]["value"], result["analytical_dcm"]["inductor_current_max"]["value"], places=3)
        for name, value in result["comparison"]["relative_difference"].items():
            self.assertLess(abs(value["value"]), 5e-3, name)

    def test_dcm_conversion_ratio_values_and_limits(self):
        self.assertAlmostEqual(lab.dcm_conversion_ratio(0.5, 0.25), 2.0 / (1.0 + math.sqrt(5.0)), places=12)
        self.assertAlmostEqual(lab.dcm_conversion_ratio(0.5, 0.5), 0.5, places=12)
        self.assertAlmostEqual(lab.dcm_conversion_ratio(0.25, 0.75), 0.25, places=12)
        self.assertLess(lab.dcm_conversion_ratio(0.5, 0.001), 1.0)
        self.assertGreater(lab.dcm_conversion_ratio(0.5, 0.01), lab.dcm_conversion_ratio(0.5, 0.1))
        for duty, k in ((0.0, 0.25), (1.0, 0.25), (0.5, 0.0), (0.5, -1.0), (0.5, float("nan")), (float("inf"), 0.25)):
            with self.subTest(duty=duty, k=k):
                with self.assertRaises(ValueError):
                    lab.dcm_conversion_ratio(duty, k)

    def test_ccm_boundary_helper(self):
        boundary = lab.ccm_boundary(24.0, 0.5, 4.8, 100000.0, 0.00015)
        self.assertEqual(boundary["predicted_mode"], "CCM")
        self.assertAlmostEqual(boundary["boundary_load_resistance"]["value"], 60.0, places=9)
        self.assertEqual(lab.ccm_boundary(24.0, 0.5, 60.0, 100000.0, 0.00015)["predicted_mode"], "CCM")
        self.assertEqual(lab.ccm_boundary(24.0, 0.5, 61.0, 100000.0, 0.00015)["predicted_mode"], "DCM")
        self.assertAlmostEqual(boundary["boundary_output_current"]["value"],
                               boundary["output_current_ccm"]["value"] * 4.8 / 60.0, places=12)
        with self.assertRaises(ValueError):
            lab.ccm_boundary(24.0, 1.0, 4.8, 100000.0, 0.00015)

    def test_dcm_steady_state_rejects_a_ccm_point(self):
        with self.assertRaisesRegex(ValueError, "CCM"):
            lab.dcm_steady_state(24.0, 0.5, 4.8, 100000.0, 0.00015)
        dcm = lab.dcm_steady_state(24.0, 0.5, 120.0, 100000.0, 0.00015)
        self.assertAlmostEqual(dcm["conversion_ratio"]["value"], 2.0 / (1.0 + math.sqrt(5.0)), places=12)
        self.assertAlmostEqual(dcm["diode_duty_ratio"]["value"] + dcm["zero_current_fraction"]["value"], 0.5, places=12)
        self.assertAlmostEqual(dcm["inductor_current_mean"]["value"] * 120.0, dcm["output_voltage"]["value"], places=12)

    def test_boundary_load_sits_between_the_modes(self):
        steady = lab.simulate(load_resistance=60.0)["steady_state"]
        self.assertAlmostEqual(steady["inductor_current_min"]["value"], 0.0, places=3)
        self.assertAlmostEqual(steady["inductor_current_mean"]["value"], 0.2, places=3)
        self.assertLess(steady["zero_current_fraction"]["value"], 0.01)
        self.assertAlmostEqual(steady["output_voltage_mean"]["value"], 12.0, places=2)


class ValidationTests(unittest.TestCase):
    def test_invalid_inputs_raise_value_error(self):
        cases = [
            {"v_in": 0.0}, {"v_in": -24.0}, {"v_in": float("nan")}, {"v_in": float("inf")},
            {"v_out_target": 24.0}, {"v_out_target": 30.0}, {"v_out_target": 0.0}, {"v_out_target": -12.0},
            {"duty": 0.0}, {"duty": 1.0}, {"duty": 1.5}, {"duty": float("nan")},
            {"duty": 0.5, "v_out_target": 12.0}, {"power": 30.0, "load_resistance": 4.8},
            {"power": 0.0}, {"power": -1.0}, {"power": float("inf")},
            {"load_resistance": 0.0}, {"load_resistance": float("nan")},
            {"frequency": 0.0}, {"frequency": -1.0}, {"frequency": float("inf")},
            {"inductance": 0.0}, {"inductance": float("nan")}, {"capacitance": 0.0}, {"capacitance": -1e-6},
            {"cycles": 0}, {"cycles": -5}, {"cycles": 2.5}, {"cycles": True},
            {"steps_per_cycle": 1}, {"steps_per_cycle": 3}, {"steps_per_cycle": 100.0},
            {"tolerance": 0.0}, {"tolerance": -1e-6}, {"tolerance": float("nan")},
            {"v_in": True}, {"v_in": "24"},
        ]
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    lab.simulate(**kwargs)

    def test_error_messages_name_the_problem(self):
        with self.assertRaisesRegex(ValueError, "duty"):
            lab.simulate(duty=1.2)
        with self.assertRaisesRegex(ValueError, "steps down"):
            lab.simulate(v_out_target=30.0)
        with self.assertRaisesRegex(ValueError, "not both"):
            lab.simulate(power=30.0, load_resistance=4.8)
        with self.assertRaisesRegex(ValueError, "finite"):
            lab.simulate(frequency=float("inf"))
        with self.assertRaisesRegex(ValueError, "steps_per_cycle"):
            lab.simulate(steps_per_cycle=2)

    def test_resolve_operating_point(self):
        v_in, duty, target, resistance = lab.resolve_operating_point()
        self.assertEqual((v_in, duty, target), (24.0, 0.5, 12.0))
        self.assertAlmostEqual(resistance, 4.8, places=12)
        _, duty, target, resistance = lab.resolve_operating_point(24.0, duty=0.25, load_resistance=2.0)
        self.assertEqual((duty, target, resistance), (0.25, 6.0, 2.0))

    def test_results_never_contain_nan_or_infinity(self):
        for kwargs in ({}, {"load_resistance": 120.0}, {"duty": 0.75}, {"cycles": 3}):
            with self.subTest(**kwargs):
                result = lab.simulate(**kwargs)
                json.dumps(result, allow_nan=False)
        self.assertFalse(lab.simulate(cycles=3)["settling"]["settled"])
        self.assertTrue(lab.simulate(cycles=3)["warnings"])


class RobustnessTests(unittest.TestCase):
    def test_unstable_step_is_rejected_before_integration(self):
        cases = ({"capacitance": 1e-9}, {"frequency": 10.0}, {"inductance": 1e-12}, {"power": 1e6},
                 {"duty": 0.001}, {"frequency": 1.0})
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaisesRegex(ValueError, "steps-per-cycle"):
                    lab.simulate(**kwargs)

    def test_rejection_names_a_step_count_that_works(self):
        with self.assertRaises(ValueError) as caught:
            lab.simulate(capacitance=1e-9, cycles=20)
        needed = int(re.search(r"--steps-per-cycle >= (\d+)", str(caught.exception)).group(1))
        result = lab.simulate(capacitance=1e-9, cycles=20, steps_per_cycle=needed)
        json.dumps(result, allow_nan=False)
        self.assertTrue(all(math.isfinite(v["value"]) for v in result["steady_state"].values() if isinstance(v, dict)))

    def test_refining_the_step_lifts_the_rejection(self):
        result = lab.simulate(capacitance=1e-8, steps_per_cycle=4000, cycles=50)
        self.assertTrue(all(math.isfinite(v["value"]) for v in result["steady_state"].values() if isinstance(v, dict)))
        json.dumps(result, allow_nan=False)

    def test_divergence_is_reported_as_value_error(self):
        # Defeat the step guard to reach the second line of defence.
        with mock.patch.object(lab, "STABILITY_MARGIN", 1e12):
            with self.assertRaisesRegex(ValueError, "diverged"):
                lab.simulate(frequency=10.0)

    def test_documented_examples_pass_the_stability_guard(self):
        for kwargs in ({"power": 0.01}, {"capacitance": 1e-5}, {"inductance": 75e-6}, {"frequency": 200000.0},
                       {"load_resistance": 240.0}, {"steps_per_cycle": 20}):
            with self.subTest(**kwargs):
                self.assertTrue(lab.simulate(cycles=2, **kwargs)["settling"]["cycles_simulated"] == 2)

    def test_single_period_reports_null_changes(self):
        settling = lab.simulate(cycles=1)["settling"]
        self.assertFalse(settling["settled"])
        self.assertIsNone(settling["last_cycle_change_output_voltage"]["value"])
        self.assertIsNone(settling["last_cycle_change_inductor_current"]["value"])
        self.assertEqual(settling["last_cycle_change_output_voltage"]["unit"], "1")
        two = lab.simulate(cycles=2)["settling"]
        self.assertIsInstance(two["last_cycle_change_output_voltage"]["value"], float)

    def test_not_settled_warning_reports_the_filter_time_constant(self):
        warnings = lab.simulate(cycles=3)["warnings"]
        self.assertTrue(any("2RC" in w and "--cycles" in w for w in warnings), warnings)

    def test_waveform_samples_cover_the_last_period(self):
        result = lab.simulate(waveform=True, cycles=3, steps_per_cycle=50)
        wave = result["waveform"]
        for key in ("time", "inductor_current", "output_voltage"):
            self.assertEqual(len(wave[key]["values"]), 51, key)
            self.assertTrue(all(math.isfinite(x) for x in wave[key]["values"]), key)
        self.assertEqual(len(wave["cycle_mean_output_voltage"]["values"]), 3)
        self.assertEqual(wave["time"]["values"][0], 0.0)
        self.assertAlmostEqual(wave["time"]["values"][-1], 1e-5, places=12)
        self.assertEqual(wave["time"]["unit"], "s")
        self.assertNotIn("waveform", lab.simulate(cycles=3))

    def test_plot_without_matplotlib_is_graceful(self):
        result = lab.simulate(waveform=True, cycles=3)
        err = io.StringIO()
        with mock.patch.dict(sys.modules, {"matplotlib": None, "matplotlib.pyplot": None}):
            with contextlib.redirect_stderr(err):
                self.assertEqual(lab.plot(result, None), 0)
        self.assertIn("matplotlib is not installed", err.getvalue())


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(LAB_PATH), *args], capture_output=True, text=True, timeout=120)

    def test_default_run_prints_indented_json_and_exits_zero(self):
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["steady_state"]["conduction_mode"], "CCM")
        self.assertAlmostEqual(data["steady_state"]["output_voltage_mean"]["value"], 12.0, places=3)
        self.assertAlmostEqual(data["steady_state"]["inductor_ripple_pp"]["value"], 0.4, places=3)
        self.assertGreater(len(proc.stdout.strip().splitlines()), 10)

    def test_json_flag_prints_compact_json(self):
        proc = self.run_cli("--json", "--frequency", "200000")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = proc.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1)
        data = json.loads(lines[0])
        self.assertAlmostEqual(data["steady_state"]["inductor_ripple_pp"]["value"], 0.2, places=3)

    def test_invalid_input_exits_with_code_2(self):
        proc = self.run_cli("--v-out", "30")
        self.assertEqual(proc.returncode, 2)
        self.assertTrue(proc.stderr.startswith("error:"), proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_help_exits_zero(self):
        proc = self.run_cli("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--steps-per-cycle", proc.stdout)

    def test_unstable_step_exits_with_code_2(self):
        proc = self.run_cli("--capacitance", "1e-9")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertTrue(proc.stderr.startswith("error:"), proc.stderr)
        self.assertIn("--steps-per-cycle", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_argparse_rejects_non_numeric_values_with_exit_2(self):
        proc = self.run_cli("--cycles", "2.5")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error:", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_negative_exponent_form_value_reaches_validation_with_equals(self):
        proc = self.run_cli("--capacitance=-1e-6")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("must be positive", proc.stderr)
        self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
