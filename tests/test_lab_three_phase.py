"""Tests for labs/power-systems/three_phase.py: analytical values, trends, limiting cases, invalid inputs and the CLI."""
import contextlib
import importlib.util
import io
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_PATH = ROOT / "labs" / "power-systems" / "three_phase.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lab = load("three_phase_lab", LAB_PATH)
HAVE_MPL = importlib.util.find_spec("matplotlib") is not None

Z_DEFAULT = complex(10.0, 5.0)
V_PHASE = 400.0 / math.sqrt(3.0)          # 230.94 V
I_DEFAULT = V_PHASE / abs(Z_DEFAULT)      # 20.656 A
PF_DEFAULT = 10.0 / abs(Z_DEFAULT)        # 0.894427 (2 / sqrt 5)
PHI_DEFAULT = math.degrees(math.atan2(5.0, 10.0))  # 26.565 deg


class PhasorHelperTests(unittest.TestCase):
    def test_phasor_round_trip(self):
        z = lab.phasor(230.0, -120.0)
        magnitude, angle = lab.polar(z)
        self.assertAlmostEqual(magnitude, 230.0, places=9)
        self.assertAlmostEqual(angle, -120.0, places=9)

    def test_wrap_degrees(self):
        self.assertAlmostEqual(lab.wrap_degrees(190.0), -170.0)
        self.assertAlmostEqual(lab.wrap_degrees(-190.0), 170.0)
        self.assertEqual(lab.wrap_degrees(180.0), 180.0)
        self.assertEqual(lab.wrap_degrees(-180.0), 180.0)
        self.assertAlmostEqual(lab.wrap_degrees(0.0), 0.0)

    def test_phasor_rejects_bad_inputs(self):
        for magnitude, angle in ((-1.0, 0.0), (float("nan"), 0.0), (1.0, float("inf")), (True, 0.0), ("1", 0.0)):
            with self.subTest(magnitude=magnitude, angle=angle), self.assertRaises(ValueError):
                lab.phasor(magnitude, angle)

    def test_quantity_normalises_negative_zero_and_rejects_non_finite(self):
        self.assertEqual(lab.quantity(-0.0, "W"), {"value": 0.0, "unit": "W"})
        with self.assertRaises(ValueError):
            lab.quantity(float("nan"), "W")


class BalancedWyeTests(unittest.TestCase):
    def setUp(self):
        self.result = lab.balanced_wye()

    def test_default_voltages_and_currents(self):
        r = self.result
        self.assertAlmostEqual(r["phase_voltage_rms"]["value"], 230.940107676, places=6)
        self.assertAlmostEqual(r["line_voltage_rms"]["value"], 400.0, places=9)
        self.assertAlmostEqual(r["line_to_phase_voltage_ratio"]["value"], math.sqrt(3.0), places=9)
        self.assertAlmostEqual(r["phase_current_rms"]["value"], 20.6559111798, places=6)
        self.assertAlmostEqual(r["line_current_rms"]["value"], r["phase_current_rms"]["value"], places=9)
        self.assertAlmostEqual(r["line_to_phase_current_ratio"]["value"], 1.0, places=9)
        self.assertAlmostEqual(r["impedance_per_phase"]["magnitude"]["value"], math.sqrt(125.0), places=9)
        self.assertAlmostEqual(r["impedance_per_phase"]["angle"]["value"], PHI_DEFAULT, places=9)

    def test_default_phasor_angles(self):
        ph = self.result["phasors"]
        self.assertAlmostEqual(ph["line_to_neutral_voltages"]["a"]["angle"]["value"], 0.0, places=9)
        self.assertAlmostEqual(ph["line_to_neutral_voltages"]["b"]["angle"]["value"], -120.0, places=6)
        self.assertAlmostEqual(ph["line_to_neutral_voltages"]["c"]["angle"]["value"], 120.0, places=6)
        self.assertAlmostEqual(ph["line_to_line_voltages"]["ab"]["magnitude"]["value"], 400.0, places=6)
        self.assertAlmostEqual(ph["line_to_line_voltages"]["ab"]["angle"]["value"], 30.0, places=6)
        self.assertAlmostEqual(ph["line_to_line_voltages"]["bc"]["angle"]["value"], -90.0, places=6)
        self.assertAlmostEqual(ph["line_to_line_voltages"]["ca"]["angle"]["value"], 150.0, places=6)
        self.assertAlmostEqual(ph["line_currents"]["a"]["angle"]["value"], -PHI_DEFAULT, places=6)
        self.assertAlmostEqual(ph["line_currents"]["b"]["angle"]["value"], -120.0 - PHI_DEFAULT, places=6)

    def test_default_powers(self):
        r = self.result
        self.assertAlmostEqual(r["per_phase"]["real_power"]["value"], 12800.0 / 3.0, places=6)
        self.assertAlmostEqual(r["per_phase"]["reactive_power"]["value"], 6400.0 / 3.0, places=6)
        self.assertAlmostEqual(r["total"]["real_power"]["value"], 12800.0, places=6)
        self.assertAlmostEqual(r["total"]["reactive_power"]["value"], 6400.0, places=6)
        self.assertAlmostEqual(r["total"]["apparent_power"]["value"], 6400.0 * math.sqrt(5.0), places=6)
        self.assertAlmostEqual(r["total"]["apparent_power_from_line_quantities"]["value"],
                               r["total"]["apparent_power"]["value"], places=6)
        self.assertAlmostEqual(r["power_factor"]["value"], 2.0 / math.sqrt(5.0), places=9)
        self.assertAlmostEqual(r["power_factor_angle"]["value"], PHI_DEFAULT, places=9)
        self.assertEqual(r["power_factor_type"], "lagging")

    def test_units_and_metadata(self):
        r = self.result
        self.assertEqual(r["validation_status"], "analytical-example")
        self.assertEqual(r["model"], "balanced-wye-load")
        self.assertEqual(r["total"]["reactive_power"]["unit"], "var")
        self.assertEqual(r["total"]["apparent_power"]["unit"], "VA")
        self.assertEqual(r["phase_voltage_rms"]["unit"], "V")
        self.assertEqual(r["impedance_per_phase"]["resistance"]["unit"], "Ohm")
        self.assertTrue(r["assumptions"])
        self.assertTrue(r["limitations"])
        json.dumps(r, allow_nan=False)

    def test_resistive_load_has_unity_power_factor(self):
        r = lab.balanced_wye(400.0, 10.0, 50.0)
        self.assertAlmostEqual(r["power_factor"]["value"], 1.0, places=12)
        self.assertAlmostEqual(r["total"]["reactive_power"]["value"], 0.0, places=9)
        self.assertEqual(r["power_factor_type"], "unity")

    def test_capacitive_load_is_leading(self):
        r = lab.balanced_wye(400.0, complex(10.0, -5.0), 50.0)
        self.assertEqual(r["power_factor_type"], "leading")
        self.assertLess(r["total"]["reactive_power"]["value"], 0.0)
        self.assertGreater(r["phasors"]["line_currents"]["a"]["angle"]["value"], 0.0)
        self.assertAlmostEqual(r["power_factor"]["value"], PF_DEFAULT, places=9)

    def test_purely_reactive_load_has_zero_real_power(self):
        r = lab.balanced_wye(400.0, complex(0.0, 5.0), 50.0)
        self.assertAlmostEqual(r["total"]["real_power"]["value"], 0.0, places=9)
        self.assertAlmostEqual(r["power_factor"]["value"], 0.0, places=12)
        self.assertAlmostEqual(r["power_factor_angle"]["value"], 90.0, places=9)

    def test_power_scales_with_voltage_squared_and_inversely_with_impedance(self):
        base = lab.balanced_wye(400.0, Z_DEFAULT, 50.0)["total"]["real_power"]["value"]
        doubled_v = lab.balanced_wye(800.0, Z_DEFAULT, 50.0)["total"]["real_power"]["value"]
        self.assertAlmostEqual(doubled_v / base, 4.0, places=9)
        doubled_z = lab.balanced_wye(400.0, 2 * Z_DEFAULT, 50.0)
        self.assertAlmostEqual(doubled_z["total"]["real_power"]["value"] / base, 0.5, places=9)
        self.assertAlmostEqual(doubled_z["line_current_rms"]["value"] / I_DEFAULT, 0.5, places=9)

    def test_more_reactance_lowers_power_factor(self):
        pfs = [lab.balanced_wye(400.0, complex(10.0, x), 50.0)["power_factor"]["value"]
               for x in (0.0, 2.0, 5.0, 10.0, 20.0)]
        self.assertEqual(pfs, sorted(pfs, reverse=True))

    def test_frequency_only_changes_angular_frequency(self):
        a = lab.balanced_wye(400.0, Z_DEFAULT, 50.0)
        b = lab.balanced_wye(400.0, Z_DEFAULT, 60.0)
        self.assertAlmostEqual(a["total"]["real_power"]["value"], b["total"]["real_power"]["value"], places=9)
        self.assertAlmostEqual(b["angular_frequency"]["value"], 2.0 * math.pi * 60.0, places=9)

    def test_invalid_inputs(self):
        cases = (
            {"v_line_rms": 0.0}, {"v_line_rms": -400.0}, {"v_line_rms": float("nan")}, {"v_line_rms": float("inf")},
            {"frequency": 0.0}, {"frequency": -50.0}, {"frequency": float("nan")},
            {"z_phase": 0}, {"z_phase": 0j}, {"z_phase": complex(float("nan"), 1.0)},
            {"z_phase": complex(1.0, float("inf"))}, {"z_phase": "10+5j"}, {"v_line_rms": True},
            {"z_phase": complex(-10.0, 5.0)}, {"z_phase": complex(1e308, 1e308)}, {"z_phase": 1e-12},
            {"v_line_rms": 1e200}, {"frequency": 1e13},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                lab.balanced_wye(**kwargs)

    def test_negative_resistance_is_rejected_as_non_passive(self):
        with self.assertRaisesRegex(ValueError, "resistance must be non-negative"):
            lab.balanced_wye(400.0, complex(-10.0, 5.0))
        with self.assertRaisesRegex(ValueError, "resistance must be non-negative"):
            lab.balanced_delta(400.0, complex(-1.0, 0.0))


class BalancedDeltaTests(unittest.TestCase):
    def test_default_delta_values(self):
        r = lab.balanced_delta()
        self.assertEqual(r["connection"], "delta")
        self.assertAlmostEqual(r["phase_voltage_rms"]["value"], 400.0, places=9)
        self.assertAlmostEqual(r["phase_current_rms"]["value"], 400.0 / abs(Z_DEFAULT), places=6)
        self.assertAlmostEqual(r["line_current_rms"]["value"], math.sqrt(3.0) * 400.0 / abs(Z_DEFAULT), places=6)
        self.assertAlmostEqual(r["line_to_phase_current_ratio"]["value"], math.sqrt(3.0), places=9)
        self.assertAlmostEqual(r["line_to_phase_voltage_ratio"]["value"], 1.0, places=9)
        self.assertAlmostEqual(r["total"]["real_power"]["value"], 38400.0, places=6)
        self.assertAlmostEqual(r["total"]["reactive_power"]["value"], 19200.0, places=6)
        self.assertAlmostEqual(r["total"]["apparent_power_from_line_quantities"]["value"],
                               r["total"]["apparent_power"]["value"], places=6)
        self.assertEqual(r["power_factor_type"], "lagging")

    def test_line_current_lags_branch_current_by_30_degrees(self):
        ph = lab.balanced_delta()["phasors"]
        branch = ph["phase_currents"]["ab"]["angle"]["value"]
        line = ph["line_currents"]["a"]["angle"]["value"]
        self.assertAlmostEqual(lab.wrap_degrees(branch - line), 30.0, places=6)
        self.assertAlmostEqual(line, -PHI_DEFAULT, places=6)

    def test_delta_draws_three_times_wye_power_for_same_impedance(self):
        wye = lab.balanced_wye()["total"]["real_power"]["value"]
        delta = lab.balanced_delta()["total"]["real_power"]["value"]
        self.assertAlmostEqual(delta / wye, 3.0, places=9)

    def test_delta_to_wye_equivalence(self):
        z_y = lab.delta_to_wye(Z_DEFAULT)
        self.assertAlmostEqual(z_y.real, 10.0 / 3.0, places=12)
        self.assertAlmostEqual(z_y.imag, 5.0 / 3.0, places=12)
        back = lab.wye_to_delta(z_y)
        self.assertAlmostEqual(back.real, 10.0, places=12)
        self.assertAlmostEqual(back.imag, 5.0, places=12)
        delta = lab.balanced_delta(400.0, Z_DEFAULT, 50.0)
        wye_eq = lab.balanced_wye(400.0, z_y, 50.0)
        self.assertAlmostEqual(delta["line_current_rms"]["value"], wye_eq["line_current_rms"]["value"], places=9)
        self.assertAlmostEqual(delta["total"]["real_power"]["value"], wye_eq["total"]["real_power"]["value"], places=6)
        self.assertAlmostEqual(delta["total"]["reactive_power"]["value"],
                               wye_eq["total"]["reactive_power"]["value"], places=6)
        self.assertAlmostEqual(delta["phasors"]["line_currents"]["a"]["angle"]["value"],
                               wye_eq["phasors"]["line_currents"]["a"]["angle"]["value"], places=9)

    def test_delta_invalid(self):
        for kwargs in ({"z_phase": 0.0}, {"v_line_rms": -1.0}, {"frequency": 0.0}, {"v_line_rms": float("nan")},
                       {"z_phase": complex(-1.0, 0.0)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                lab.balanced_delta(**kwargs)
        for bad in (0, float("nan"), complex(float("inf"), 0), None, "z", True, complex(1e308, 0), 1e-15):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                lab.delta_to_wye(bad)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                lab.wye_to_delta(bad)


class InstantaneousPowerTests(unittest.TestCase):
    def test_total_is_constant_and_phase_pulsates(self):
        r = lab.instantaneous_power(400.0, I_DEFAULT, PHI_DEFAULT, 50.0)
        self.assertEqual(r["validation_status"], "numerical-simulation")
        total = r["total"]
        self.assertAlmostEqual(total["analytical_constant"]["value"], 12800.0, places=6)
        self.assertAlmostEqual(total["sampled_mean"]["value"], 12800.0, places=6)
        self.assertAlmostEqual(total["sampled_min"]["value"], 12800.0, places=6)
        self.assertAlmostEqual(total["sampled_max"]["value"], 12800.0, places=6)
        self.assertLess(total["spread_relative_to_apparent_power"]["value"], 1e-9)
        a = r["phase_a"]
        s_phase = V_PHASE * I_DEFAULT
        self.assertAlmostEqual(a["analytical_max"]["value"], s_phase * (PF_DEFAULT + 1.0), places=6)
        self.assertAlmostEqual(a["analytical_min"]["value"], s_phase * (PF_DEFAULT - 1.0), places=6)
        self.assertLess(a["sampled_min"]["value"], 0.0)
        self.assertLessEqual(a["sampled_max"]["value"], a["analytical_max"]["value"] + 1e-9)
        self.assertGreaterEqual(a["sampled_min"]["value"], a["analytical_min"]["value"] - 1e-9)
        self.assertAlmostEqual(a["pulsation_frequency"]["value"], 100.0)
        self.assertEqual(r["samples_per_cycle"], 360)
        self.assertEqual(r["sample_count"], 360)

    def test_unity_pf_phase_power_never_negative(self):
        r = lab.instantaneous_power(400.0, 10.0, 0.0, 50.0)
        self.assertGreaterEqual(r["phase_a"]["sampled_min"]["value"], -1e-9)
        self.assertAlmostEqual(r["phase_a"]["analytical_min"]["value"], 0.0, places=9)
        self.assertAlmostEqual(r["total"]["analytical_constant"]["value"], 3.0 * V_PHASE * 10.0, places=6)

    def test_purely_reactive_total_is_zero(self):
        r = lab.instantaneous_power(400.0, 10.0, 90.0, 50.0)
        self.assertAlmostEqual(r["total"]["analytical_constant"]["value"], 0.0, places=9)
        self.assertAlmostEqual(r["total"]["sampled_mean"]["value"], 0.0, places=6)
        self.assertLess(r["total"]["spread_relative_to_apparent_power"]["value"], 1e-9)

    def test_more_samples_approach_the_analytical_extreme(self):
        coarse = lab.instantaneous_power(400.0, I_DEFAULT, PHI_DEFAULT, 50.0, n_points=36)
        fine = lab.instantaneous_power(400.0, I_DEFAULT, PHI_DEFAULT, 50.0, n_points=3600)
        target = coarse["phase_a"]["analytical_max"]["value"]
        gap_coarse = target - coarse["phase_a"]["sampled_max"]["value"]
        gap_fine = target - fine["phase_a"]["sampled_max"]["value"]
        self.assertGreaterEqual(gap_coarse, 0.0)
        self.assertLessEqual(gap_fine, gap_coarse)

    def test_explicit_times_and_samples(self):
        r = lab.instantaneous_power(400.0, 10.0, 30.0, 50.0, times=[0.0, 0.005, 0.01], include_samples=True)
        self.assertEqual(r["sample_count"], 3)
        self.assertNotIn("samples_per_cycle", r)
        self.assertEqual(r["samples"]["units"]["p_a"], "W")
        self.assertEqual(r["samples"]["units"]["time"], "s")
        self.assertEqual(len(r["samples"]["p_total"]), 3)
        self.assertEqual(len(r["samples"]["time"]), 3)

    def test_invalid(self):
        cases = (
            dict(v_line_rms=0.0, i_line_rms=1.0, pf_angle_deg=0.0),
            dict(v_line_rms=400.0, i_line_rms=-1.0, pf_angle_deg=0.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=95.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=-95.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=float("nan")),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, frequency=0.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, n_points=3),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, n_points=360.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, times=[]),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, times=[0.0, float("inf")]),
            dict(v_line_rms=float("inf"), i_line_rms=1.0, pf_angle_deg=0.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, times=5.0),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, times="abc"),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, times=[1e308]),
            dict(v_line_rms=400.0, i_line_rms=1.0, pf_angle_deg=0.0, n_points=10**7),
            dict(v_line_rms=1e-200, i_line_rms=1e-200, pf_angle_deg=0.0),
            dict(v_line_rms=400.0, i_line_rms=1e200, pf_angle_deg=0.0),
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                lab.instantaneous_power(**kwargs)


class PowerFactorCorrectionTests(unittest.TestCase):
    def test_default_example(self):
        r = lab.pf_correction_capacitance(12800.0, PF_DEFAULT, 0.95, 400.0, 50.0)
        q_new = 12800.0 * math.tan(math.acos(0.95))
        q_c = 6400.0 - q_new
        c_wye = q_c / (2.0 * math.pi * 50.0 * 400.0 ** 2)
        self.assertAlmostEqual(r["reactive_power_before"]["value"], 6400.0, places=6)
        self.assertAlmostEqual(r["reactive_power_after"]["value"], q_new, places=6)
        self.assertAlmostEqual(r["capacitor_reactive_power_total"]["value"], q_c, places=6)
        self.assertAlmostEqual(r["capacitor_reactive_power_per_phase"]["value"], q_c / 3.0, places=6)
        self.assertAlmostEqual(r["capacitance_per_phase_wye"]["value"], c_wye, places=12)
        self.assertAlmostEqual(r["capacitance_per_phase_delta"]["value"], c_wye / 3.0, places=12)
        self.assertEqual(r["capacitance_per_phase_wye"]["unit"], "F")
        self.assertGreater(c_wye, 40e-6)
        self.assertLess(c_wye, 48e-6)
        self.assertAlmostEqual(r["apparent_power_before"]["value"], 6400.0 * math.sqrt(5.0), places=6)
        self.assertAlmostEqual(r["apparent_power_after"]["value"], 12800.0 / 0.95, places=6)
        self.assertAlmostEqual(r["line_current_before"]["value"], I_DEFAULT, places=6)
        self.assertLess(r["line_current_after"]["value"], r["line_current_before"]["value"])
        self.assertGreater(r["line_current_reduction"]["value"], 0.0)
        self.assertAlmostEqual(r["capacitor_voltage_wye"]["value"], V_PHASE, places=9)
        self.assertAlmostEqual(r["capacitor_current_per_phase_wye"]["value"], (q_c / 3.0) / V_PHASE, places=9)

    def test_capacitance_increases_with_target(self):
        caps = [lab.pf_correction_capacitance(12800.0, PF_DEFAULT, pf, 400.0, 50.0)["capacitance_per_phase_wye"]["value"]
                for pf in (0.9, 0.95, 0.98, 1.0)]
        self.assertEqual(caps, sorted(caps))
        self.assertTrue(all(c > 0.0 for c in caps))

    def test_unity_target_cancels_all_reactive_power(self):
        r = lab.pf_correction_capacitance(12800.0, PF_DEFAULT, 1.0, 400.0, 50.0)
        self.assertAlmostEqual(r["reactive_power_after"]["value"], 0.0, places=6)
        self.assertAlmostEqual(r["capacitor_reactive_power_total"]["value"], 6400.0, places=6)
        self.assertAlmostEqual(r["apparent_power_after"]["value"], 12800.0, places=6)

    def test_equal_power_factors_need_no_capacitance(self):
        r = lab.pf_correction_capacitance(12800.0, 0.9, 0.9, 400.0, 50.0)
        self.assertAlmostEqual(r["capacitance_per_phase_wye"]["value"], 0.0, places=15)
        self.assertAlmostEqual(r["line_current_reduction"]["value"], 0.0, places=15)

    def test_capacitance_falls_with_voltage_squared_and_frequency(self):
        c1 = lab.pf_correction_capacitance(12800.0, PF_DEFAULT, 0.95, 400.0, 50.0)["capacitance_per_phase_wye"]["value"]
        c2 = lab.pf_correction_capacitance(12800.0, PF_DEFAULT, 0.95, 800.0, 50.0)["capacitance_per_phase_wye"]["value"]
        c3 = lab.pf_correction_capacitance(12800.0, PF_DEFAULT, 0.95, 400.0, 60.0)["capacitance_per_phase_wye"]["value"]
        self.assertAlmostEqual(c2 / c1, 0.25, places=12)
        self.assertAlmostEqual(c3 / c1, 50.0 / 60.0, places=12)

    def test_invalid(self):
        cases = (
            (0.0, 0.8, 0.95, 400.0, 50.0), (-1.0, 0.8, 0.95, 400.0, 50.0), (float("inf"), 0.8, 0.95, 400.0, 50.0),
            (1000.0, 0.0, 0.95, 400.0, 50.0), (1000.0, 1.2, 0.95, 400.0, 50.0), (1000.0, -0.8, 0.95, 400.0, 50.0),
            (1000.0, 0.8, 0.0, 400.0, 50.0), (1000.0, 0.8, 1.05, 400.0, 50.0), (1000.0, 0.8, float("nan"), 400.0, 50.0),
            (1000.0, 0.95, 0.8, 400.0, 50.0),
            (1000.0, 0.8, 0.95, 0.0, 50.0), (1000.0, 0.8, 0.95, 400.0, 0.0), (1000.0, 0.8, 0.95, 400.0, -50.0),
            (1000.0, 0.8, 0.95, 1e200, 50.0), (1e200, 0.8, 0.95, 400.0, 50.0),
        )
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                lab.pf_correction_capacitance(*args)

    def test_lower_target_message_is_specific(self):
        with self.assertRaisesRegex(ValueError, "must not be lower"):
            lab.pf_correction_capacitance(1000.0, 0.95, 0.8, 400.0, 50.0)


class PerUnitTests(unittest.TestCase):
    def test_default_bases(self):
        r = lab.per_unit(100e3, 11e3)
        self.assertAlmostEqual(r["z_base"]["value"], 1210.0, places=9)
        self.assertAlmostEqual(r["i_base"]["value"], 100e3 / (math.sqrt(3.0) * 11e3), places=9)
        self.assertAlmostEqual(r["i_base"]["value"], 5.24864, places=4)
        self.assertAlmostEqual(r["v_phase_base"]["value"], 11e3 / math.sqrt(3.0), places=9)
        self.assertAlmostEqual(r["y_base"]["value"], 1.0 / 1210.0, places=12)
        self.assertEqual(r["z_base"]["unit"], "Ohm")
        self.assertEqual(r["s_base"]["unit"], "VA")

    def test_z_base_scales_with_voltage_squared(self):
        z1 = lab.per_unit(100e3, 11e3)["z_base"]["value"]
        z2 = lab.per_unit(100e3, 22e3)["z_base"]["value"]
        z3 = lab.per_unit(200e3, 11e3)["z_base"]["value"]
        self.assertAlmostEqual(z2 / z1, 4.0, places=12)
        self.assertAlmostEqual(z3 / z1, 0.5, places=12)

    def test_to_pu_and_from_pu_round_trip(self):
        z_base = lab.per_unit(100e3, 400.0)["z_base"]["value"]
        self.assertAlmostEqual(z_base, 1.6, places=12)
        z_pu = lab.to_pu(Z_DEFAULT, z_base)
        self.assertAlmostEqual(z_pu.real, 6.25, places=12)
        self.assertAlmostEqual(z_pu.imag, 3.125, places=12)
        back = lab.from_pu(z_pu, z_base)
        self.assertAlmostEqual(back.real, 10.0, places=12)
        self.assertAlmostEqual(back.imag, 5.0, places=12)
        self.assertAlmostEqual(lab.to_pu(1210.0, 1210.0), 1.0, places=15)
        self.assertIsInstance(lab.to_pu(1210.0, 1210.0), float)
        self.assertIsInstance(lab.to_pu(Z_DEFAULT, 1.6), complex)
        self.assertAlmostEqual(lab.from_pu(0.04, 1210.0), 48.4, places=12)

    def test_impedance_pu_is_invariant_across_an_ideal_transformer(self):
        ratio = 11e3 / 400.0
        z_hv = Z_DEFAULT * ratio ** 2
        pu_lv = lab.to_pu(Z_DEFAULT, lab.per_unit(100e3, 400.0)["z_base"]["value"])
        pu_hv = lab.to_pu(z_hv, lab.per_unit(100e3, 11e3)["z_base"]["value"])
        self.assertAlmostEqual(pu_lv.real, pu_hv.real, places=9)
        self.assertAlmostEqual(pu_lv.imag, pu_hv.imag, places=9)

    def test_change_base(self):
        self.assertAlmostEqual(lab.change_base(0.04, 100e3, 11e3, 200e3, 11e3), 0.08, places=12)
        self.assertAlmostEqual(lab.change_base(0.04, 100e3, 11e3, 100e3, 22e3), 0.01, places=12)
        self.assertAlmostEqual(lab.change_base(0.04, 100e3, 11e3, 100e3, 11e3), 0.04, places=12)
        z = lab.change_base(complex(0.01, 0.03), 100e3, 11e3, 50e3, 11e3)
        self.assertAlmostEqual(z.real, 0.005, places=12)
        self.assertAlmostEqual(z.imag, 0.015, places=12)

    def test_invalid(self):
        for args in ((0.0, 11e3), (100e3, 0.0), (-1.0, 11e3), (float("nan"), 11e3), (100e3, float("inf"))):
            with self.subTest(args=args), self.assertRaises(ValueError):
                lab.per_unit(*args)
        for value, base in ((1.0, 0.0), (1.0, -5.0), (float("nan"), 1.0), (complex(float("inf"), 0), 1.0),
                            ("1", 1.0), (True, 1.0), (1.0, float("nan"))):
            with self.subTest(value=value, base=base), self.assertRaises(ValueError):
                lab.to_pu(value, base)
            with self.subTest(value=value, base=base), self.assertRaises(ValueError):
                lab.from_pu(value, base)
        for args in ((0.04, 0.0, 11e3, 100e3, 11e3), (0.04, 100e3, 11e3, 100e3, 0.0), (float("nan"), 100e3, 11e3, 100e3, 11e3)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                lab.change_base(*args)

    def test_overflow_and_out_of_range_bases_raise_instead_of_returning_infinity(self):
        with self.assertRaises(ValueError):
            lab.to_pu(1e308, 1e-10)
        with self.assertRaises(ValueError):
            lab.from_pu(1e308, 1e10)
        with self.assertRaises(ValueError):
            lab.change_base(0.04, 100e3, 1e200, 100e3, 1.0)
        with self.assertRaises(ValueError):
            lab.change_base(1e308, 1.0, 11e3, 1e12, 1.0)
        with self.assertRaises(ValueError):
            lab.per_unit(1e13, 11e3)
        self.assertAlmostEqual(lab.to_pu(5e14, 1e14), 5.0, places=12)  # a derived base may exceed 1e12


class BalanceCheckTests(unittest.TestCase):
    def test_balanced_set_is_detected_with_positive_sequence(self):
        phasors = list(lab.balanced_phase_voltages(230.0).values())
        r = lab.check_balanced(phasors)
        self.assertTrue(r["balanced"])
        self.assertIn("abc", r["phase_sequence"])
        self.assertLess(r["sum_residual"]["value"], 1e-12)
        self.assertLess(r["magnitude_spread"]["value"], 1e-12)
        self.assertLess(r["max_angle_error"]["value"], 1e-9)
        self.assertEqual(r["magnitudes"][0]["unit"], "1")
        self.assertAlmostEqual(r["magnitudes"][0]["value"], 230.0, places=9)
        self.assertEqual(lab.check_balanced(phasors, unit="V")["magnitudes"][0]["unit"], "V")

    def test_negative_sequence_is_identified(self):
        phasors = [lab.phasor(230.0, 0.0), lab.phasor(230.0, 120.0), lab.phasor(230.0, -120.0)]
        r = lab.check_balanced(phasors)
        self.assertTrue(r["balanced"])
        self.assertIn("acb", r["phase_sequence"])

    def test_unbalanced_magnitude_is_rejected_not_averaged(self):
        phasors = [lab.phasor(230.0, 0.0), lab.phasor(207.0, -120.0), lab.phasor(230.0, 120.0)]
        r = lab.check_balanced(phasors)
        self.assertFalse(r["balanced"])
        self.assertAlmostEqual(r["magnitude_spread"]["value"], 23.0 / ((230.0 + 207.0 + 230.0) / 3.0), places=9)
        self.assertGreater(r["sum_residual"]["value"], 0.05)

    def test_unbalanced_angle_is_rejected(self):
        phasors = [lab.phasor(230.0, 0.0), lab.phasor(230.0, -110.0), lab.phasor(230.0, 120.0)]
        r = lab.check_balanced(phasors)
        self.assertFalse(r["balanced"])
        self.assertAlmostEqual(r["max_angle_error"]["value"], 10.0, places=6)
        self.assertTrue(lab.check_balanced(phasors, angle_tolerance_deg=15.0)["balanced"])

    def test_zero_phasor_is_unbalanced_with_undetermined_sequence(self):
        r = lab.check_balanced([lab.phasor(230.0, 0.0), 0.0, lab.phasor(230.0, 120.0)])
        self.assertFalse(r["balanced"])
        self.assertEqual(r["phase_sequence"], "undetermined")

    def test_wrong_count_and_bad_values_raise(self):
        good = list(lab.balanced_phase_voltages(230.0).values())
        with self.assertRaises(ValueError):
            lab.check_balanced(good[:2])
        with self.assertRaises(ValueError):
            lab.check_balanced(good + [good[0]])
        with self.assertRaises(ValueError):
            lab.check_balanced([0, 0, 0])
        with self.assertRaises(ValueError):
            lab.check_balanced([complex(float("nan"), 0), 1, 1])
        with self.assertRaises(ValueError):
            lab.check_balanced(["a", 1, 1])
        with self.assertRaises(ValueError):
            lab.check_balanced(good, magnitude_tolerance=-0.1)
        with self.assertRaises(ValueError):
            lab.check_balanced(12.0)
        with self.assertRaises(ValueError):
            lab.check_balanced([complex(1.7e308, 1.7e308)] * 3)

    def test_complex_power_from_phasors_matches_balanced_wye(self):
        v = lab.balanced_phase_voltages(V_PHASE)
        i = {k: v[k] / Z_DEFAULT for k in "abc"}
        r = lab.complex_power_from_phasors(list(v.values()), list(i.values()))
        self.assertAlmostEqual(r["total_real_power"]["value"], 12800.0, places=6)
        self.assertAlmostEqual(r["total_reactive_power"]["value"], 6400.0, places=6)
        self.assertAlmostEqual(r["power_factor"]["value"], PF_DEFAULT, places=9)
        self.assertEqual(len(r["per_phase_complex_power"]), 3)

    def test_complex_power_refuses_unbalanced_currents_unless_told(self):
        v = list(lab.balanced_phase_voltages(230.0).values())
        i = [v[0] / Z_DEFAULT, v[1] / (2 * Z_DEFAULT), v[2] / Z_DEFAULT]
        with self.assertRaisesRegex(ValueError, "currents are not a balanced set"):
            lab.complex_power_from_phasors(v, i)
        r = lab.complex_power_from_phasors(v, i, require_balanced=False)
        self.assertEqual(len(r["per_phase_complex_power"]), 3)
        balanced_p = 3.0 * 230.0 ** 2 * 10.0 / 125.0
        self.assertLess(r["total_real_power"]["value"], balanced_p)


class AnalyseAndCliTests(unittest.TestCase):
    def test_default_analysis_is_json_serialisable_and_consistent(self):
        result = lab.analyse()
        text = json.dumps(result, allow_nan=False)
        self.assertIn('"wye_load"', text)
        self.assertEqual(result["inputs"]["v_line_rms"]["value"], 400.0)
        self.assertEqual(result["validation_status"], "analytical-example")
        self.assertEqual(result["instantaneous_power"]["validation_status"], "numerical-simulation")
        pu = result["per_unit"]
        self.assertAlmostEqual(pu["primary_base"]["z_base"]["value"], 1210.0, places=9)
        self.assertAlmostEqual(pu["load_side_base"]["z_base"]["value"], 1.6, places=12)
        self.assertAlmostEqual(pu["ideal_transformer_ratio"]["value"], 27.5, places=12)
        self.assertAlmostEqual(pu["load_impedance_pu_on_load_side_base"]["real"]["value"], 6.25, places=9)
        self.assertAlmostEqual(pu["load_impedance_pu_on_load_side_base"]["imag"]["value"], 3.125, places=9)
        self.assertAlmostEqual(pu["load_impedance_referred_to_primary"]["real"]["value"], 7562.5, places=6)
        self.assertAlmostEqual(pu["load_impedance_pu_on_primary_base"]["real"]["value"], 6.25, places=9)
        self.assertAlmostEqual(pu["load_impedance_pu_on_primary_base"]["imag"]["value"], 3.125, places=9)
        self.assertAlmostEqual(pu["load_complex_power_pu"]["real"]["value"], 0.128, places=12)
        self.assertAlmostEqual(pu["load_complex_power_pu"]["imag"]["value"], 0.064, places=12)
        self.assertAlmostEqual(pu["load_line_current_pu_load_side"]["value"],
                               pu["load_line_current_pu_primary"]["value"], places=9)
        equivalence = result["delta_to_wye_equivalent"]
        self.assertAlmostEqual(equivalence["delta_to_wye_power_ratio_same_impedance"]["value"], 3.0, places=9)
        self.assertAlmostEqual(equivalence["z_wye_equivalent"]["real"]["value"], 10.0 / 3.0, places=9)
        self.assertTrue(result["balance_check"]["balanced"])
        self.assertEqual(result["balance_check"]["magnitudes"][0]["unit"], "V")
        self.assertEqual(result["instantaneous_power"]["sample_count"], 360)
        correction = result["power_factor_correction"]
        self.assertEqual(correction["pf_new"]["value"], 0.95)
        self.assertIn("capacitance_per_phase_wye", correction)
        self.assertAlmostEqual(correction["pf_old"]["value"], PF_DEFAULT, places=9)

    def test_correction_not_applicable_for_resistive_leading_or_satisfied_loads(self):
        self.assertEqual(lab.analyse(reactance=0.0)["power_factor_correction"]["status"], "not-applicable")
        self.assertEqual(lab.analyse(reactance=-5.0)["power_factor_correction"]["status"], "not-applicable")
        self.assertEqual(lab.analyse(pf_target=0.5)["power_factor_correction"]["status"], "not-applicable")
        reactive_only = lab.analyse(resistance=0.0)
        self.assertEqual(reactive_only["power_factor_correction"]["status"], "not-applicable")
        json.dumps(reactive_only, allow_nan=False)
        record = lab.analyse(pf_target=0.5)["power_factor_correction"]
        for key in ("model", "validation_status", "assumptions", "limitations", "status", "reason", "pf_old", "pf_new"):
            self.assertIn(key, record)
        self.assertIn("already meets or exceeds", record["reason"])

    def test_analyse_invalid(self):
        cases = ({"resistance": 0.0, "reactance": 0.0}, {"pf_target": 0.0}, {"pf_target": 1.5},
                 {"frequency": 0.0}, {"s_base": 0.0}, {"v_base": -11e3}, {"v_line_rms": float("nan")},
                 {"resistance": float("inf")}, {"n_points": 2}, {"pf_target": float("nan")},
                 {"resistance": -10.0}, {"n_points": 10**7}, {"v_line_rms": 1e-200}, {"v_line_rms": 1e200},
                 {"resistance": 1e308, "reactance": 1e308}, {"v_line_rms": 1e12, "resistance": 1e-9, "reactance": 0.0})
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                lab.analyse(**kwargs)

    def test_analyse_negative_resistance_message_names_the_input(self):
        with self.assertRaisesRegex(ValueError, "^resistance must be non-negative"):
            lab.analyse(resistance=-10.0)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(LAB_PATH), *args], capture_output=True, text=True, timeout=60)

    def test_cli_default_prints_indented_json(self):
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, "")
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["wye_load"]["total"]["real_power"]["value"], 12800.0, places=6)
        self.assertAlmostEqual(data["wye_load"]["phase_voltage_rms"]["value"], 230.940107676, places=6)
        self.assertIn("\n  ", proc.stdout)

    def test_cli_json_flag_is_compact_and_parseable(self):
        proc = self.run_cli("--json", "--v-line", "400", "--resistance", "10", "--reactance", "5",
                            "--frequency", "50", "--pf-target", "0.95", "--s-base", "100000", "--v-base", "11000")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, "")
        data = json.loads(proc.stdout)
        self.assertEqual(proc.stdout.strip().count("\n"), 0)
        self.assertAlmostEqual(data["wye_load"]["power_factor"]["value"], PF_DEFAULT, places=9)
        self.assertAlmostEqual(data["per_unit"]["primary_base"]["i_base"]["value"], 5.24864, places=4)

    def test_cli_invalid_input_exits_2(self):
        proc = self.run_cli("--frequency", "0")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error:", proc.stderr)
        self.assertEqual(proc.stdout.strip(), "")
        proc = self.run_cli("--resistance", "0", "--reactance", "0")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("must not be zero", proc.stderr)

    def test_cli_rejects_further_invalid_inputs_with_exit_2(self):
        cases = (("--v-line", "nan"), ("--v-line", "inf"), ("--points", "3"), ("--resistance", "-10"),
                 ("--v-line", "1e-200"), ("--v-line", "1e200"), ("--points", "10000000"))
        for args in cases:
            with self.subTest(args=args):
                proc = self.run_cli(*args)
                self.assertEqual(proc.returncode, 2, proc.stdout)
                self.assertIn("error:", proc.stderr)
                self.assertEqual(proc.stdout, "")
                if args[0] == "--resistance":
                    self.assertIn("resistance must be non-negative", proc.stderr)

    def test_cli_is_deterministic(self):
        first, second = self.run_cli("--json"), self.run_cli("--json")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)

    @unittest.skipUnless(HAVE_MPL, "matplotlib is not installed")
    def test_cli_plot_writes_png_and_keeps_stdout_as_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "three_phase_test.png"
            proc = self.run_cli("--json", "--plot", "--out", str(out))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            json.loads(proc.stdout)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 0)
            self.assertIn("plot written", proc.stderr)

    @unittest.skipUnless(HAVE_MPL, "matplotlib is not installed")
    def test_cli_plot_into_missing_directory_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing" / "three_phase_test.png"
            proc = self.run_cli("--json", "--plot", "--out", str(out))
            self.assertEqual(proc.returncode, 2)
            self.assertIn("error:", proc.stderr)
            json.loads(proc.stdout)

    def test_plot_without_matplotlib_reports_on_stderr_and_keeps_json_on_stdout(self):
        saved = {name: sys.modules.get(name) for name in ("matplotlib", "matplotlib.pyplot")}
        sys.modules["matplotlib"] = None
        sys.modules["matplotlib.pyplot"] = None
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = lab.main(["--json", "--plot"])
        finally:
            for name, module in saved.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module
        self.assertEqual(code, 0)
        json.loads(out.getvalue())
        self.assertIn("matplotlib is not installed", err.getvalue())

    def test_cli_help(self):
        proc = self.run_cli("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--pf-target", proc.stdout)
        self.assertIn("--v-base", proc.stdout)


if __name__ == "__main__":
    unittest.main()
