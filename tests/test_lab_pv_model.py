"""Tests for labs/renewable-energy/pv_model.py (single-diode PV module model with P&O MPPT).

Run from the repository root with
    python -m unittest tests.test_lab_pv_model
or as part of
    python -m unittest discover -s tests -v
"""
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "labs/renewable-energy/pv_model.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lab = load("pv_model", "labs/renewable-energy/pv_model.py")

K_B = 1.380649e-23
Q_E = 1.602176634e-19
CONTRACT_KEYS = ("model", "validation_status", "assumptions", "limitations")


def residual(v, i, params, i_ph, i_0, a):
    """Kirchhoff current residual of the single-diode equation (r_sh None means no shunt)."""
    r_sh = params.get("r_sh")
    r_sh = math.inf if r_sh is None else r_sh
    v_d = v + i * params["r_s"]
    return i_ph - i_0 * math.expm1(v_d / a) - v_d / r_sh - i


def model_residual(v, i, params, irradiance=1000.0, temperature_c=25.0):
    """Residual evaluated with the lab's own I_ph, I_0(T) and a(T) for arbitrary parameters."""
    p = lab.validate_parameters(params)
    i_ph = lab.photocurrent(irradiance, temperature_c, p["i_sc_stc"], p["alpha_isc"])
    i_0 = lab.saturation_current(p, temperature_c)
    a = lab.thermal_voltage(temperature_c + 273.15, p["ideality"], p["cells_in_series"])
    return residual(v, i, p, i_ph, i_0, a)


class DefaultExampleTests(unittest.TestCase):
    """Known analytical values of the lesson's synthetic 60-cell module at STC."""

    def setUp(self):
        self.params = lab.default_parameters()
        self.a_stc = 1.3 * 60 * K_B * 298.15 / Q_E

    def test_thermal_voltage(self):
        self.assertAlmostEqual(lab.thermal_voltage(298.15, 1.0, 1), 0.0256925791, places=9)
        self.assertAlmostEqual(lab.thermal_voltage(298.15, 1.3, 60), 2.00402117, places=7)
        self.assertAlmostEqual(lab.thermal_voltage(298.15, 1.3, 60), self.a_stc, places=12)

    def test_photocurrent(self):
        self.assertAlmostEqual(lab.photocurrent(1000.0, 25.0, 9.0, 0.0005), 9.0, places=12)
        self.assertAlmostEqual(lab.photocurrent(500.0, 25.0, 9.0, 0.0005), 4.5, places=12)
        self.assertAlmostEqual(lab.photocurrent(1000.0, 45.0, 9.0, 0.0005), 9.09, places=12)
        self.assertEqual(lab.photocurrent(0.0, 25.0, 9.0, 0.0005), 0.0)

    def test_saturation_current_from_open_circuit_voltage(self):
        expected = (9.0 - 37.5 / 300.0) / math.expm1(37.5 / self.a_stc)
        i_0 = lab.saturation_current_stc(self.params)
        self.assertAlmostEqual(i_0 / expected, 1.0, places=12)
        self.assertAlmostEqual(i_0, 6.6296e-8, delta=1e-11)
        self.assertAlmostEqual(lab.saturation_current(self.params, 25.0), i_0, places=20)

    def test_saturation_current_temperature_law_uses_band_gap_in_joules_over_k(self):
        # I_0(T) = I_0,STC (T/T_STC)^3 exp(q E_g[eV] / (n k_B) (1/T_STC - 1/T)); q E_g / (n k_B) = 9998 K.
        factor = Q_E * 1.12 / (1.3 * K_B)
        self.assertAlmostEqual(factor, 9997.74, delta=0.01)
        t_k, t_stc = 323.15, 298.15
        expected = lab.saturation_current_stc(self.params) * (t_k / t_stc) ** 3 * math.exp(factor * (1 / t_stc - 1 / t_k))
        self.assertAlmostEqual(lab.saturation_current(self.params, 50.0) / expected, 1.0, places=12)

    def test_open_circuit_and_short_circuit(self):
        self.assertAlmostEqual(lab.open_circuit_voltage(self.params), 37.5, places=7)
        self.assertAlmostEqual(lab.current_at_voltage(37.5, self.params), 0.0, places=7)
        i_sc = lab.current_at_voltage(0.0, self.params)
        # The model's I_sc is lower than the nominal 9.0 A by about R_s/R_sh = 0.1 %.
        self.assertAlmostEqual(i_sc, 8.9910, places=3)
        self.assertLess(i_sc, 9.0)
        self.assertGreater(i_sc, 9.0 * (1 - 0.0011))

    def test_current_satisfies_single_diode_equation(self):
        i_ph = lab.photocurrent(1000.0, 25.0, 9.0, 0.0005)
        i_0 = lab.saturation_current_stc(self.params)
        for v in (0.0, 10.0, 20.0, 29.6, 35.0, 37.5):
            i = lab.current_at_voltage(v, self.params)
            self.assertAlmostEqual(residual(v, i, self.params, i_ph, i_0, self.a_stc), 0.0, places=8)

    def test_solver_inverts_explicit_voltage_without_shunt(self):
        # Without a shunt path the voltage is explicit in the current:
        # V = a ln((I_ph - I)/I_0 + 1) - I R_s. The solver must invert it.
        params = dict(self.params, r_sh=None)
        i_0 = lab.saturation_current_stc(params)
        for i_target in (1.0, 4.0, 8.0, 8.9):
            v = self.a_stc * math.log1p((9.0 - i_target) / i_0) - i_target * params["r_s"]
            self.assertAlmostEqual(lab.current_at_voltage(v, params), i_target, places=8)

    def test_worked_example_current_at_30_v(self):
        i_30 = lab.current_at_voltage(30.0, self.params)
        self.assertAlmostEqual(i_30, 8.1766, places=4)
        self.assertAlmostEqual(30.0 * i_30, 245.30, places=2)

    def test_maximum_power_point_values(self):
        mpp = lab.maximum_power_point(self.params)
        self.assertAlmostEqual(mpp["v_mp"]["value"], 29.632, places=2)
        self.assertAlmostEqual(mpp["i_mp"]["value"], 8.288, places=2)
        self.assertAlmostEqual(mpp["p_mp"]["value"], 245.58, places=1)
        self.assertAlmostEqual(mpp["fill_factor"]["value"], 0.7284, places=3)
        self.assertAlmostEqual(mpp["p_mp"]["value"], mpp["v_mp"]["value"] * mpp["i_mp"]["value"], places=9)
        self.assertEqual(mpp["v_mp"]["unit"], "V")
        self.assertEqual(mpp["p_mp"]["unit"], "W")
        self.assertEqual(mpp["validation_status"], "numerical-simulation")
        self.assertEqual(mpp["search"]["grid_points"], 401)
        self.assertLess(mpp["search"]["function_evaluations"], 600)

    def test_maximum_power_point_is_a_stationary_maximum(self):
        mpp = lab.maximum_power_point(self.params)
        v_mp = mpp["v_mp"]["value"]
        h = 1e-3
        p_plus = (v_mp + h) * lab.current_at_voltage(v_mp + h, self.params)
        p_minus = (v_mp - h) * lab.current_at_voltage(v_mp - h, self.params)
        self.assertAlmostEqual((p_plus - p_minus) / (2 * h), 0.0, places=3)  # dP/dV = 0 at the MPP
        curve = lab.iv_curve(self.params, points=201)
        self.assertGreaterEqual(mpp["p_mp"]["value"], max(curve["power_w"]))
        self.assertLess(mpp["p_mp"]["value"] - max(curve["power_w"]), 0.5)

    def test_fill_factor(self):
        self.assertAlmostEqual(lab.fill_factor(245.5824, 37.5, 8.99101), 0.72838, places=4)
        self.assertAlmostEqual(lab.fill_factor(1.0, 2.0, 0.5), 1.0, places=12)

    def test_iv_curve_shape(self):
        curve = lab.iv_curve(self.params, points=101)
        self.assertEqual(curve["points"], 101)
        self.assertEqual(len(curve["voltage_v"]), 101)
        self.assertEqual(curve["voltage_v"][0], 0.0)
        self.assertAlmostEqual(curve["voltage_v"][-1], 37.5, places=7)
        self.assertAlmostEqual(curve["current_a"][-1], 0.0, places=7)
        # Current decreases monotonically with voltage.
        for earlier, later in zip(curve["current_a"], curve["current_a"][1:]):
            self.assertGreater(earlier, later)
        self.assertEqual(curve["units"]["power_w"], "W")

    def test_calculate_default_is_deterministic_and_json_safe(self):
        first = lab.calculate()
        second = lab.calculate()
        self.assertEqual(json.dumps(first, allow_nan=False), json.dumps(second, allow_nan=False))
        self.assertEqual(first["model"], "single-diode-pv-module")
        self.assertEqual(first["validation_status"], "numerical-simulation")
        self.assertNotIn("iv_curve", first)
        self.assertNotIn("mppt", first)
        self.assertAlmostEqual(first["key_points"]["p_mp"]["value"], 245.58, places=1)
        self.assertAlmostEqual(first["derived_parameters"]["thermal_voltage_module_a"]["value"], 2.00402, places=4)
        self.assertAlmostEqual(first["key_points"]["per_cell"]["open_circuit_voltage"]["value"], 0.625, places=9)
        self.assertEqual(len(first["iv_curve_samples"]), 11)


class ContractTests(unittest.TestCase):
    """Every public result dict carries the lab contract keys and {value, unit} quantities."""

    def setUp(self):
        self.params = lab.default_parameters()

    def test_public_results_carry_contract_keys(self):
        results = {
            "maximum_power_point": lab.maximum_power_point(self.params),
            "perturb_and_observe": lab.perturb_and_observe(self.params, iterations=5),
            "irradiance_temperature_table": lab.irradiance_temperature_table(self.params),
            "calculate": lab.calculate(),
        }
        for name, result in results.items():
            with self.subTest(result=name):
                for key in CONTRACT_KEYS:
                    self.assertIn(key, result)
                self.assertEqual(result["model"], "single-diode-pv-module")
                self.assertEqual(result["validation_status"], "numerical-simulation")
                self.assertTrue(result["assumptions"] and result["limitations"])
                json.dumps(result, allow_nan=False)

    def test_quantities_have_si_units(self):
        result = lab.calculate()
        self.assertEqual(result["key_points"]["short_circuit_current"]["unit"], "A")
        self.assertEqual(result["key_points"]["open_circuit_voltage"]["unit"], "V")
        self.assertEqual(result["parameters"]["r_s"]["unit"], "Ohm")
        self.assertEqual(result["conditions"]["irradiance"]["unit"], "W/m2")
        self.assertEqual(result["conditions"]["cell_temperature"]["unit"], "degC")
        self.assertEqual(result["conditions"]["cell_temperature_kelvin"]["unit"], "K")
        self.assertEqual(result["parameters"]["band_gap"]["unit"], "eV")
        self.assertEqual(result["sensitivity"]["temperature_coefficients_at_stc"]["beta_voc_model"]["unit"], "%/K")


class TrendTests(unittest.TestCase):
    """Parameter-variation trends: irradiance, temperature, resistances and series scaling."""

    def setUp(self):
        self.params = lab.default_parameters()

    def test_short_circuit_current_proportional_to_irradiance(self):
        i_1000 = lab.current_at_voltage(0.0, self.params, 1000.0, 25.0)
        i_500 = lab.current_at_voltage(0.0, self.params, 500.0, 25.0)
        i_200 = lab.current_at_voltage(0.0, self.params, 200.0, 25.0)
        self.assertAlmostEqual(i_500 / i_1000, 0.5, places=6)
        self.assertAlmostEqual(i_200 / i_1000, 0.2, places=6)

    def test_open_circuit_voltage_logarithmic_in_irradiance(self):
        params = dict(self.params, r_sh=None)  # exact logarithm without the shunt path
        a = lab.thermal_voltage(298.15, 1.3, 60)
        v_1000 = lab.open_circuit_voltage(params, 1000.0, 25.0)
        v_500 = lab.open_circuit_voltage(params, 500.0, 25.0)
        self.assertAlmostEqual(v_1000 - v_500, a * math.log(2.0), places=5)
        # With the shunt, a tenfold drop costs a little more than a ln 10 (lesson misconception 3).
        v_100 = lab.open_circuit_voltage(self.params, 100.0, 25.0)
        self.assertAlmostEqual(v_100, 32.655, places=2)
        self.assertGreater(37.5 - v_100, a * math.log(10.0))

    def test_sweeps_are_monotonic(self):
        table = lab.irradiance_temperature_table(self.params)
        cols = table["columns"]
        rows_g = table["irradiance_sweep"]["rows"]
        rows_t = table["temperature_sweep"]["rows"]
        for key in ("i_sc", "v_oc", "p_mp", "i_mp"):
            values = [row[cols.index(key)] for row in rows_g]
            self.assertEqual(values, sorted(values), f"{key} should rise with irradiance")
        v_oc_t = [row[cols.index("v_oc")] for row in rows_t]
        p_mp_t = [row[cols.index("p_mp")] for row in rows_t]
        i_sc_t = [row[cols.index("i_sc")] for row in rows_t]
        self.assertEqual(v_oc_t, sorted(v_oc_t, reverse=True))
        self.assertEqual(p_mp_t, sorted(p_mp_t, reverse=True))
        self.assertEqual(i_sc_t, sorted(i_sc_t))
        self.assertEqual(len(rows_g), 5)
        self.assertEqual(len(rows_t), 4)

    def test_model_temperature_coefficients(self):
        coeffs = lab.irradiance_temperature_table(self.params)["temperature_coefficients_at_stc"]
        self.assertAlmostEqual(coeffs["alpha_isc_model"]["value"], 0.05, places=3)
        self.assertAlmostEqual(coeffs["beta_voc_model"]["value"], -0.3165, places=3)
        self.assertAlmostEqual(coeffs["gamma_pmp_model"]["value"], -0.4103, places=3)
        self.assertLess(coeffs["gamma_pmp_model"]["value"], coeffs["beta_voc_model"]["value"])
        self.assertEqual(coeffs["beta_voc_model"]["unit"], "%/K")

    def test_analytic_open_circuit_voltage_slope_matches_lesson(self):
        # dV_oc/dT = (V_oc - 3a - N_s E_g/q)/T + a alpha with E_g in joules: -0.1188 V/K, -0.317 %/K.
        a = lab.thermal_voltage(298.15, 1.3, 60)
        slope = (37.5 - 3 * a - 60 * 1.12) / 298.15 + a * 0.0005
        self.assertAlmostEqual(slope, -0.1188, places=4)
        self.assertAlmostEqual(100 * slope / 37.5, -0.317, places=3)
        v_plus = lab.open_circuit_voltage(self.params, 1000.0, 26.0)
        v_minus = lab.open_circuit_voltage(self.params, 1000.0, 24.0)
        self.assertAlmostEqual((v_plus - v_minus) / 2.0, slope, places=3)

    def test_open_circuit_voltage_falls_roughly_linearly_with_temperature(self):
        v_0 = lab.open_circuit_voltage(self.params, 1000.0, 0.0)
        v_25 = lab.open_circuit_voltage(self.params, 1000.0, 25.0)
        v_50 = lab.open_circuit_voltage(self.params, 1000.0, 50.0)
        drop_low = v_0 - v_25
        drop_high = v_25 - v_50
        self.assertGreater(drop_low, 0.0)
        self.assertGreater(drop_high, 0.0)
        self.assertLess(abs(drop_low - drop_high) / drop_low, 0.05)  # within 5 % of linear

    def test_series_resistance_lowers_power_and_fill_factor(self):
        base = lab.maximum_power_point(self.params)
        lossy = lab.maximum_power_point(dict(self.params, r_s=0.6))
        better = lab.maximum_power_point(dict(self.params, r_s=0.15))
        self.assertLess(lossy["p_mp"]["value"], base["p_mp"]["value"])
        self.assertGreater(better["p_mp"]["value"], base["p_mp"]["value"])
        self.assertLess(lossy["fill_factor"]["value"], base["fill_factor"]["value"])
        self.assertAlmostEqual(lossy["v_oc"]["value"], base["v_oc"]["value"], places=7)  # R_s does not change V_oc
        self.assertAlmostEqual(lossy["p_mp"]["value"], 225.24, places=1)
        self.assertAlmostEqual(better["p_mp"]["value"], 255.94, places=1)

    def test_shunt_resistance_lowers_power_mostly_at_low_irradiance(self):
        base = lab.maximum_power_point(self.params, 200.0, 25.0)["p_mp"]["value"]
        leaky = lab.maximum_power_point(dict(self.params, r_sh=50.0), 200.0, 25.0)["p_mp"]["value"]
        base_full = lab.maximum_power_point(self.params, 1000.0, 25.0)["p_mp"]["value"]
        leaky_full = lab.maximum_power_point(dict(self.params, r_sh=50.0), 1000.0, 25.0)["p_mp"]["value"]
        self.assertLess(leaky, base)
        self.assertLess(leaky_full, base_full)
        self.assertGreater((base - leaky) / base, (base_full - leaky_full) / base_full)

    def test_series_connection_scales_voltage_not_current(self):
        single = lab.maximum_power_point(self.params)
        double = lab.maximum_power_point(dict(self.params, cells_in_series=120, v_oc_stc=75.0, r_s=0.6, r_sh=600.0))
        self.assertAlmostEqual(double["v_mp"]["value"], 2 * single["v_mp"]["value"], places=4)
        self.assertAlmostEqual(double["i_mp"]["value"], single["i_mp"]["value"], places=6)
        self.assertAlmostEqual(double["p_mp"]["value"], 2 * single["p_mp"]["value"], places=3)
        self.assertAlmostEqual(double["fill_factor"]["value"], single["fill_factor"]["value"], places=6)

    def test_hot_hazy_afternoon_example(self):
        mpp = lab.maximum_power_point(self.params, 600.0, 50.0)
        self.assertAlmostEqual(mpp["v_oc"]["value"], 33.388, places=2)
        self.assertAlmostEqual(mpp["i_sc"]["value"], 5.462, places=2)
        self.assertAlmostEqual(mpp["v_mp"]["value"], 26.396, places=2)
        self.assertAlmostEqual(mpp["p_mp"]["value"], 130.67, places=1)
        self.assertAlmostEqual(mpp["fill_factor"]["value"], 0.7165, places=3)


class MpptTests(unittest.TestCase):
    """Perturb-and-observe behaviour: convergence, oscillation and the step-size trade-off."""

    def setUp(self):
        self.params = lab.default_parameters()

    def test_default_trajectory_starts_at_40_percent_of_v_oc(self):
        result = lab.perturb_and_observe(self.params, 1000.0, 25.0, step_v=0.5, iterations=40)
        traj = result["trajectory"]
        self.assertEqual(len(traj["voltage_v"]), 41)
        self.assertEqual(traj["voltage_v"][0], 15.0)
        self.assertEqual(result["settings"]["start_v"]["value"], 15.0)
        self.assertEqual(result["iterations_to_reach_mpp_band"], 29)
        self.assertEqual(sorted(set(traj["voltage_v"][-8:])), [29.0, 29.5, 30.0])
        self.assertAlmostEqual(result["steady_state"]["voltage_band"]["value"], 1.0, places=9)
        self.assertAlmostEqual(result["steady_state"]["mean_power"]["value"], 245.31, places=2)
        self.assertAlmostEqual(result["steady_state"]["tracking_efficiency"]["value"], 0.9989, places=4)
        self.assertLess(result["steady_state"]["tracking_efficiency"]["value"], 1.0)
        self.assertAlmostEqual(result["reference_mpp"]["p_mp"]["value"], 245.58, places=1)
        final_v = result["final_point"]["voltage"]["value"]
        self.assertIn(final_v, (29.0, 29.5, 30.0))  # the steady-state cycle around V_mp = 29.63 V
        self.assertLess(abs(final_v - result["reference_mpp"]["v_mp"]["value"]), 2 * 0.5)
        for p in traj["power_w"]:
            self.assertLessEqual(p, result["reference_mpp"]["p_mp"]["value"] + 1e-9)

    def test_explicit_start_voltage(self):
        result = lab.perturb_and_observe(self.params, step_v=0.5, iterations=40, start_v=20.0)
        self.assertEqual(result["trajectory"]["voltage_v"][0], 20.0)
        self.assertEqual(result["iterations_to_reach_mpp_band"], 19)
        self.assertAlmostEqual(result["steady_state"]["tracking_efficiency"]["value"], 0.9989, places=4)

    def test_step_size_trade_off(self):
        runs = {step: lab.perturb_and_observe(self.params, step_v=step, iterations=200) for step in (0.1, 0.5, 1.0, 2.0)}
        reached = [runs[s]["iterations_to_reach_mpp_band"] for s in (0.1, 0.5, 1.0, 2.0)]
        bands = [runs[s]["steady_state"]["power_band"]["value"] for s in (0.1, 0.5, 1.0, 2.0)]
        efficiencies = [runs[s]["steady_state"]["tracking_efficiency"]["value"] for s in (0.1, 0.5, 1.0, 2.0)]
        self.assertEqual(reached, [146, 29, 14, 7])
        self.assertEqual(bands, sorted(bands))
        self.assertEqual(efficiencies, sorted(efficiencies, reverse=True))
        self.assertAlmostEqual(bands[1], 0.70, places=2)
        self.assertAlmostEqual(efficiencies[2], 0.9942, places=4)

    def test_tracks_from_above_and_clamps_start(self):
        result = lab.perturb_and_observe(self.params, step_v=0.5, iterations=40, start_v=50.0)
        self.assertAlmostEqual(result["settings"]["start_v"]["value"], 37.5, places=7)
        self.assertIsNotNone(result["iterations_to_reach_mpp_band"])
        self.assertGreater(result["steady_state"]["tracking_efficiency"]["value"], 0.99)

    def test_tracks_at_other_conditions(self):
        result = lab.perturb_and_observe(self.params, 600.0, 50.0, step_v=0.5, iterations=60)
        self.assertGreater(result["steady_state"]["tracking_efficiency"]["value"], 0.99)
        self.assertLess(result["reference_mpp"]["v_mp"]["value"], 29.0)  # MPP voltage falls when hot

    def test_assessment_question_6_transfer_case(self):
        coarse = lab.perturb_and_observe(self.params, 600.0, 50.0, step_v=1.0, iterations=40, start_v=20.0)
        fine = lab.perturb_and_observe(self.params, 600.0, 50.0, step_v=0.5, iterations=40, start_v=20.0)
        self.assertEqual(coarse["iterations_to_reach_mpp_band"], 6)
        self.assertEqual(sorted(set(coarse["trajectory"]["voltage_v"][-8:])), [25.0, 26.0, 27.0])
        self.assertAlmostEqual(coarse["steady_state"]["mean_power"]["value"], 129.98, places=2)
        self.assertAlmostEqual(coarse["steady_state"]["tracking_efficiency"]["value"], 0.9947, places=4)
        self.assertEqual(fine["iterations_to_reach_mpp_band"], 12)
        self.assertAlmostEqual(fine["steady_state"]["tracking_efficiency"]["value"], 0.9987, places=4)

    def test_small_module_uses_a_scaled_default_start(self):
        small = {"cells_in_series": 1, "v_oc_stc": 0.62, "i_sc_stc": 0.5, "r_s": 0.05, "r_sh": 10.0}
        result = lab.perturb_and_observe(small, step_v=0.01, iterations=60)
        self.assertAlmostEqual(result["settings"]["start_v"]["value"], 0.248, places=9)
        self.assertGreater(result["steady_state"]["tracking_efficiency"]["value"], 0.99)


class SolverTests(unittest.TestCase):
    """The safeguarded Newton solver must not crawl down steep exponentials."""

    def test_stiff_exponential_residual_converges_quickly(self):
        # Plain Newton on 2 - exp(k x) - x shrinks the residual only e-fold per step from the
        # steep side; the rtsafe rule bisects instead, so the budget of 200 iterations holds.
        for k in (400.0, 1000.0, 5000.0):
            with self.subTest(k=k):
                def res(x, k=k):
                    return 2.0 - math.exp(min(k * x, 700.0)) - x

                def der(x, k=k):
                    return -k * math.exp(min(k * x, 700.0)) - 1.0

                root, evaluations = lab._safeguarded_newton(res, der, -10.0, 1.0, -10.0, 1e-12)
                self.assertAlmostEqual(root, math.log(2.0 - root) / k, places=12)
                self.assertLess(evaluations, 60)

    def test_unbracketed_root_raises_value_error(self):
        with self.assertRaises(ValueError):
            lab._safeguarded_newton(lambda x: 1.0 + x, lambda x: 1.0, 0.0, 1.0, 0.5, 1e-12)

    def test_steep_but_consistent_modules_satisfy_the_equation(self):
        cases = (
            (dict(lab.default_parameters(), i_sc_stc=0.1, r_s=300.0, r_sh=3000.0), 75.0),   # R_s / a = 150
            (dict(lab.default_parameters(), r_s=4.0), 75.0),                                  # R_s I_sc just below V_oc
            ({"cells_in_series": 1, "v_oc_stc": 0.62, "i_sc_stc": 0.5, "r_s": 1.0, "r_sh": 10.0}, 1.24),
            (dict(lab.default_parameters(), v_oc_stc=200.0, r_s=22.0, r_sh=30.0), 400.0),    # V_oc / a = 99.8
        )
        for params, v_max in cases:
            for fraction in (0.0, 0.5, 0.95, 1.0):
                for irradiance, temperature in ((1000.0, 25.0), (2000.0, -40.0), (50.0, 100.0)):
                    v = fraction * v_max
                    with self.subTest(params=params, v=v, irradiance=irradiance, temperature=temperature):
                        i = lab.current_at_voltage(v, params, irradiance, temperature)
                        self.assertTrue(math.isfinite(i))
                        self.assertLess(abs(model_residual(v, i, params, irradiance, temperature)), 1e-9)
                mpp = lab.maximum_power_point(params, irradiance, temperature)
                self.assertGreater(mpp["p_mp"]["value"], 0.0)


class LimitingCaseTests(unittest.TestCase):
    def setUp(self):
        self.params = lab.default_parameters()

    def test_zero_irradiance_gives_zero_curve_without_nan(self):
        curve = lab.iv_curve(self.params, 0.0, 25.0, points=11)
        self.assertEqual(curve["voltage_v"], [0.0] * 11)
        self.assertEqual(curve["current_a"], [0.0] * 11)
        self.assertEqual(curve["power_w"], [0.0] * 11)
        mpp = lab.maximum_power_point(self.params, 0.0, 25.0)
        self.assertEqual(mpp["p_mp"]["value"], 0.0)
        self.assertIsNone(mpp["fill_factor"])
        self.assertEqual(lab.open_circuit_voltage(self.params, 0.0, 25.0), 0.0)
        tracked = lab.perturb_and_observe(self.params, 0.0, 25.0, step_v=0.5, iterations=5)
        self.assertIsNone(tracked["steady_state"]["tracking_efficiency"])
        full = lab.calculate(irradiance=0.0, mppt=True, include_curve=True)
        json.dumps(full, allow_nan=False)
        # The saturation current is a diode property and must still be finite and positive in the dark.
        self.assertGreater(full["derived_parameters"]["saturation_current"]["value"], 0.0)

    def test_weak_light_keeps_a_positive_open_circuit_voltage(self):
        # I_ph = 9e-11 A: the shunt dominates, V_oc ~ I_ph R_sh = 2.7e-8 V, not zero.
        v_oc = lab.open_circuit_voltage(self.params, 1e-8, 25.0)
        self.assertGreater(v_oc, 0.0)
        self.assertAlmostEqual(v_oc, 9e-11 * 300.0, delta=1e-10)
        result = lab.calculate(irradiance=1e-8)
        json.dumps(result, allow_nan=False)
        self.assertGreater(result["key_points"]["p_mp"]["value"], 0.0)

    def test_no_shunt_path_recovers_nominal_short_circuit_current(self):
        for no_shunt in (None, float("inf")):
            params = dict(self.params, r_sh=no_shunt)
            self.assertEqual(lab.validate_parameters(params)["r_sh"], math.inf)
            self.assertAlmostEqual(lab.current_at_voltage(0.0, params), 9.0, delta=1e-6)
            result = lab.calculate(params=params)
            self.assertIsNone(result["parameters"]["r_sh"]["value"])
            json.dumps(result, allow_nan=False)
        self.assertAlmostEqual(lab.maximum_power_point(dict(self.params, r_sh=None))["p_mp"]["value"], 248.26, places=1)

    def test_ideal_module_matches_the_lesson_sanity_check(self):
        ideal = lab.maximum_power_point(dict(self.params, r_s=1e-9, r_sh=None))
        self.assertAlmostEqual(ideal["v_mp"]["value"], 31.836, places=2)
        self.assertAlmostEqual(ideal["p_mp"]["value"], 269.55, places=1)
        self.assertAlmostEqual(ideal["fill_factor"]["value"], 0.7987, places=3)

    def test_above_open_circuit_voltage_current_is_negative(self):
        self.assertLess(lab.current_at_voltage(40.0, self.params), 0.0)
        self.assertLess(lab.current_at_voltage(75.0, self.params), -50.0)

    def test_extreme_but_valid_conditions(self):
        for irradiance, temperature in ((1.0, 25.0), (2000.0, 100.0), (1000.0, -40.0), (50.0, -40.0)):
            result = lab.maximum_power_point(self.params, irradiance, temperature)
            self.assertGreater(result["p_mp"]["value"], 0.0)
            self.assertGreater(result["v_oc"]["value"], 0.0)
            self.assertTrue(math.isfinite(result["fill_factor"]["value"]))
            self.assertLess(result["fill_factor"]["value"], 1.0)

    def test_two_point_curve(self):
        curve = lab.iv_curve(self.params, points=2)
        self.assertEqual(len(curve["voltage_v"]), 2)
        self.assertAlmostEqual(curve["current_a"][1], 0.0, places=7)


class InvalidInputTests(unittest.TestCase):
    def setUp(self):
        self.params = lab.default_parameters()

    def assertRaisesValueError(self, fn, *args, **kwargs):
        with self.assertRaises(ValueError):
            fn(*args, **kwargs)

    def test_conditions(self):
        nan, inf = float("nan"), float("inf")
        for irradiance in (-1.0, nan, inf, -inf, 2500.0, True, 10 ** 400):
            self.assertRaisesValueError(lab.iv_curve, self.params, irradiance, 25.0)
        for temperature in (-41.0, 101.0, nan, inf, True):
            self.assertRaisesValueError(lab.iv_curve, self.params, 1000.0, temperature)
        self.assertRaisesValueError(lab.photocurrent, 1000.0, 25.0, 0.0, 0.0005)
        self.assertRaisesValueError(lab.photocurrent, 1000.0, 25.0, 9.0, 0.5)
        self.assertRaisesValueError(lab.photocurrent, 1000.0, 25.0, nan, 0.0005)

    def test_parameters(self):
        nan = float("nan")
        bad = (
            {"r_s": 0.0}, {"r_s": -0.3}, {"r_s": nan},
            {"r_s": 5.0}, {"r_s": 50.0},                              # R_s I_sc >= V_oc
            {"r_sh": 0.0}, {"r_sh": -5.0}, {"r_sh": 2.0},            # 2 Ohm: V_oc/R_sh exceeds I_sc
            {"ideality": 0.5}, {"ideality": 3.0}, {"ideality": 0.2}, {"ideality": nan},
            {"i_sc_stc": 0.0}, {"i_sc_stc": -1.0}, {"i_sc_stc": nan}, {"i_sc_stc": float("inf")},
            {"i_sc_stc": 1e-10, "r_sh": 1e12},                        # below the 1e-6 A lower bound
            {"v_oc_stc": 0.0}, {"v_oc_stc": -37.5}, {"v_oc_stc": 5e-324}, {"v_oc_stc": 1e-4},
            {"cells_in_series": 0}, {"cells_in_series": 1.5}, {"cells_in_series": True},
            {"cells_in_series": 1, "v_oc_stc": 37.5},                   # V_oc/a far above 100
            {"cells_in_series": 10},                                    # V_oc/a = 112
            {"cells_in_series": 1, "v_oc_stc": 0.62, "r_s": 1.0, "r_sh": 10.0},  # 9 A through 1 Ohm in a 0.62 V cell
            {"i_sc_stc": 1e8, "r_sh": None},
            {"alpha_isc": 0.02}, {"alpha_isc": nan},
            {"band_gap_ev": 0.1}, {"band_gap_ev": 5.0},
            {"unknown": 1.0},
        )
        for change in bad:
            with self.subTest(change=change):
                self.assertRaisesValueError(lab.validate_parameters, dict(self.params, **change))
        self.assertRaisesValueError(lab.validate_parameters, "not a dict")

    def test_voltage_and_sampling(self):
        self.assertRaisesValueError(lab.current_at_voltage, -1.0, self.params)
        self.assertRaisesValueError(lab.current_at_voltage, 100.0, self.params)  # above 2 V_oc
        self.assertRaisesValueError(lab.current_at_voltage, float("nan"), self.params)
        self.assertRaisesValueError(lab.current_at_voltage, True, self.params)
        self.assertRaisesValueError(lab.iv_curve, self.params, points=1)
        self.assertRaisesValueError(lab.iv_curve, self.params, points=2.5)
        self.assertRaisesValueError(lab.iv_curve, self.params, points=True)
        self.assertRaisesValueError(lab.iv_curve, self.params, points=10 ** 7)
        self.assertRaisesValueError(lab.maximum_power_point, self.params, grid_points=2)
        self.assertRaisesValueError(lab.thermal_voltage, 0.0, 1.0, 1)
        self.assertRaisesValueError(lab.thermal_voltage, 300.0, 1.0, 0)
        self.assertRaisesValueError(lab.thermal_voltage, 300.0, 3.5, 1)

    def test_mppt_settings_rejected_by_tracker_and_by_calculate(self):
        bad_settings = (
            {"step_v": 0.0}, {"step_v": -0.5}, {"step_v": 40.0}, {"step_v": True},
            {"iterations": 0}, {"iterations": 2.0}, {"iterations": True},
            {"start_v": -1.0}, {"start_v": 1000.0}, {"start_v": float("nan")}, {"start_v": True},
        )
        for change in bad_settings:
            with self.subTest(change=change):
                self.assertRaisesValueError(lab.perturb_and_observe, self.params, **change)
                self.assertRaisesValueError(lab.calculate, params=self.params, **change)  # even without mppt
                self.assertRaisesValueError(lab.calculate, params=self.params, mppt=True, **change)

    def test_fill_factor_domain(self):
        self.assertRaisesValueError(lab.fill_factor, 1.0, 0.0, 1.0)        # undefined in the dark
        self.assertRaisesValueError(lab.fill_factor, 10.0, 1.0, 1.0)       # FF > 1 is inconsistent
        self.assertRaisesValueError(lab.fill_factor, -1.0, 1.0, 1.0)
        self.assertRaisesValueError(lab.fill_factor, float("nan"), 1.0, 1.0)

    def test_table_inputs(self):
        self.assertRaisesValueError(lab.irradiance_temperature_table, self.params, irradiances=())
        self.assertRaisesValueError(lab.irradiance_temperature_table, self.params, irradiances=5.0)
        self.assertRaisesValueError(lab.irradiance_temperature_table, self.params, temperatures="25")
        self.assertRaisesValueError(lab.irradiance_temperature_table, self.params, irradiances=(-5.0,))
        self.assertRaisesValueError(lab.irradiance_temperature_table, self.params, temperatures=(150.0,))


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=60)

    def test_default_run_prints_json(self):
        completed = self.run_cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        data = json.loads(completed.stdout)
        self.assertEqual(data["model"], "single-diode-pv-module")
        self.assertAlmostEqual(data["key_points"]["p_mp"]["value"], 245.58, places=1)
        self.assertAlmostEqual(data["key_points"]["open_circuit_voltage"]["value"], 37.5, places=6)
        self.assertNotIn("iv_curve", data)
        self.assertIn("sensitivity", data)
        for key in CONTRACT_KEYS:
            self.assertIn(key, data)

    def test_json_flag_includes_curve_and_mppt_flag_includes_trajectory(self):
        completed = self.run_cli("--json", "--mppt", "--points", "51")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        data = json.loads(completed.stdout)
        self.assertEqual(len(data["iv_curve"]["voltage_v"]), 51)
        self.assertEqual(data["mppt"]["settings"]["start_v"]["value"], 15.0)
        self.assertGreater(data["mppt"]["steady_state"]["tracking_efficiency"]["value"], 0.998)
        self.assertEqual(data["mppt"]["iterations_to_reach_mpp_band"], 29)

    def test_other_conditions(self):
        completed = self.run_cli("--irradiance", "600", "--temperature", "50")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        data = json.loads(completed.stdout)
        self.assertAlmostEqual(data["key_points"]["p_mp"]["value"], 130.67, places=1)

    def test_no_shunt_path_flag(self):
        completed = self.run_cli("--r-sh", "inf")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        data = json.loads(completed.stdout)
        self.assertIsNone(data["parameters"]["r_sh"]["value"])
        self.assertAlmostEqual(data["key_points"]["short_circuit_current"]["value"], 9.0, places=6)

    def test_invalid_inputs_exit_with_code_2(self):
        cases = (
            ("--temperature", "150"), ("--irradiance", "-5"), ("--r-sh", "2"), ("--ideality", "0.5"),
            ("--r-s", "50"), ("--cells", "10"), ("--i-sc", "1e-10", "--r-sh", "1e12"),
            ("--step-v", "0"), ("--iterations", "0"), ("--start-v", "-1"),     # P&O settings without --mppt
        )
        for args in cases:
            with self.subTest(args=args):
                completed = self.run_cli(*args)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertTrue(completed.stderr.startswith("error:"), completed.stderr)
                self.assertEqual(completed.stdout, "")

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib is not installed")
    def test_plot_keeps_stdout_as_json(self):
        with tempfile.TemporaryDirectory() as folder:
            out = os.path.join(folder, "pv.png")
            completed = self.run_cli("--plot", "--out", out, "--points", "11")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(completed.stdout)  # the "plot saved" message goes to stderr
            self.assertNotIn("iv_curve", data)
            self.assertTrue(os.path.exists(out))
            self.assertGreater(os.path.getsize(out), 0)

    def test_help(self):
        completed = self.run_cli("--help")
        self.assertEqual(completed.returncode, 0)
        self.assertIn("--irradiance", completed.stdout)
        self.assertIn("--start-v", completed.stdout)


if __name__ == "__main__":
    unittest.main()
