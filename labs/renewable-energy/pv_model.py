"""Single-diode model of a photovoltaic (PV) module with perturb-and-observe MPPT.

AIPE Academy lab for the lesson "Solar PV fundamentals: from photons to the
maximum power point" (curriculum/renewable-energy/solar-photovoltaics/
solar-pv-fundamentals.md). Synthetic teaching module; standard library only.
This is an analytical/numerical teaching model, not validated hardware
performance.

Purpose
-------
* Build a synthetic 60-cell module from datasheet-style numbers (short-circuit
  current, open-circuit voltage, ideality factor, series and shunt resistance,
  temperature coefficient of the short-circuit current).
* Solve the implicit single-diode equation

      I = I_ph - I_0 * (exp((V + I*R_s) / a) - 1) - (V + I*R_s) / R_sh,
      a = n * N_s * k_B * T / q                      (module thermal voltage)

  numerically with a safeguarded Newton iteration (bisection fallback).
* Produce the I-V and P-V curves, the maximum power point (MPP), the fill
  factor, irradiance and temperature sweeps, and a perturb-and-observe (P&O)
  maximum power point tracking trajectory.

Inputs
------
SI units throughout; temperature is given in degrees Celsius because the
standard test condition (STC: 1000 W/m^2, 25 degC cell temperature) is
defined that way, and the argument names say so (``temperature_c``).

irradiance      plane-of-module irradiance G, W/m^2, 0 <= G <= 2000
temperature_c   cell temperature T, degC, -40 <= T <= 100
params          dictionary (see default_parameters()):
  cells_in_series  N_s      series-connected cells, integer 1..10000
  i_sc_stc         I_sc     short-circuit current at STC, A, >= 1e-6
  v_oc_stc         V_oc     open-circuit voltage at STC, V, >= 1e-3
  ideality         n        diode ideality factor, 0.5 < n < 3
  r_s              R_s      module series resistance, Ohm, > 0 and
                            R_s * I_sc < V_oc (see validation checks)
  r_sh             R_sh     module shunt resistance, Ohm, > 0, or None for
                            no shunt path (R_sh -> infinity)
  alpha_isc        alpha    relative temperature coefficient of I_sc, 1/K
                            (+0.05 %/K is written 0.0005), |alpha| <= 0.01
  band_gap_ev      E_g      band-gap energy used for I_0(T), eV, 0.3 < E_g < 4
P&O settings (perturb_and_observe(), calculate() and the CLI): step_v in V
(0 < step_v < V_oc,STC), iterations (integer 1..100000) and start_v in V
(0 <= start_v <= 2 V_oc,STC; None, the default, means 0.4 V_oc,STC, 15 V for
the default module). They are validated even when the tracker is not run.

Model assumptions
-----------------
* One lumped diode for the whole module; all N_s cells identical, equally
  illuminated and at the same temperature; one series string.
* Photocurrent proportional to irradiance and linear in temperature,
  I_ph = I_sc,STC * (G / 1000 W/m^2) * (1 + alpha * (T - 25 degC)).
  The photocurrent is identified with the STC short-circuit current: the
  diode and shunt currents at V = 0 are neglected. The relative error is about
  R_s / R_sh (0.1 % for the default module), so the model's own short-circuit
  current is 8.991 A rather than the nominal 9.000 A.
* Saturation current at STC derived from I(V_oc) = 0 at STC:
  I_0,STC = (I_ph,STC - V_oc,STC / R_sh) / (exp(V_oc,STC / a_STC) - 1).
* Temperature dependence of the saturation current (temperatures in kelvin,
  constant band gap, ideality factor inside the exponent as in the usual
  single-diode array models):
  I_0(T) = I_0,STC * (T / T_STC)^3 * exp((q E_g / (n k_B)) * (1/T_STC - 1/T)),
  where E_g is in electronvolts, so q E_g is the gap energy in joules and
  q E_g / (n k_B) = 9.998e3 K for the default module (1.12 eV, n = 1.3). With
  E_g written in joules the same factor reads E_g / (n k_B).
  The open-circuit voltage then falls with temperature through the logarithm
  V_oc ~ a * ln(I_ph / I_0 + 1); the model's own V_oc temperature coefficient
  is an output (reported in %/K), not an input.
* Constant R_s, R_sh and n; cell temperature is an input (no thermal model).
* Steady state (no capacitance, no converter dynamics): in the P&O
  demonstration the converter imposes each commanded voltage exactly, the
  module responds instantly and the power is measured without noise.

Outputs
-------
Dictionaries that serialise to JSON (json.dumps(..., allow_nan=False)).
Physical quantities are {"value": <float>, "unit": "<symbol>"} with units
A, V, W, Ohm, W/m2, degC, K, eV, 1 (dimensionless) and %/K. Every top-level
result carries "model", "validation_status" ("numerical-simulation"),
"assumptions" and "limitations".

Validation checks
-----------------
ValueError with a specific message for: boolean or non-finite inputs;
irradiance outside [0, 2000] W/m^2 (0 is allowed and gives an all-zero curve);
temperature outside [-40, 100] degC; I_sc below 1e-6 A, V_oc below 1e-3 V,
non-positive R_s, R_sh or cells_in_series; ideality outside (0.5, 3);
|alpha_isc| > 0.01 1/K; band gap outside (0.3, 4) eV; unknown parameter names;
voltage below 0 V (reverse bias is outside the model) or above 2 * V_oc,STC;
inconsistent combinations (V_oc / R_sh >= I_sc; R_s * I_sc >= V_oc, which
would make the diode conduct at short circuit so that I_sc could not equal the
datasheet value; V_oc / a_STC > 100, far beyond the 15 to 30 of real cells);
invalid sample counts, P&O steps, iteration counts or start voltages (checked
even without --mppt). fill_factor() raises ValueError when V_oc * I_sc = 0
(undefined in the dark). A root-finder that cannot converge raises ValueError
prefixed "numerical failure" instead of returning a wrong number. The command
line prints "error: <message>" to stderr and exits with code 2; the JSON is
written with allow_nan=False, so NaN or infinity can never be printed.

Numerical method and precision
------------------------------
Current at a given voltage: safeguarded Newton iteration on the Kirchhoff
current residual f(I) = I_ph - I_0 (exp((V + I R_s)/a) - 1) - (V + I R_s)/R_sh
- I, which is strictly decreasing in I, so the root is unique and bracketed
between I_lo = -(V / R_s + I_ph + 1 A) and I_hi = I_ph. A Newton step is taken
only when it stays inside the current bracket and shrinks it at least
geometrically (|2 f| <= |dx_old f'|, the classical "rtsafe" rule); otherwise
the step is a bisection, so the iteration cannot crawl down the exponential
wall one a/R_s at a time when R_s / a is large. Convergence: |f(I)| <= 1e-9 A,
scaled down in proportion to I_ph when I_ph < 1 A so that weak light still
gives a positive V_oc. Open-circuit voltage: the same solver on
g(V) = I_ph - I_0 (exp(V/a) - 1) - V/R_sh (R_s drops out at I = 0). Maximum
power point: P(V) evaluated on a 401-point grid over [0, V_oc], then
golden-section search in the bracket around the best sample until the bracket
is narrower than 1e-6 V. Precision of P_mp: the 1e-6 V bracket contributes
about 0.5 |P''| (5e-7 V)^2 = 5e-13 W (P'' = -4.0 W/V^2 for the default module);
the 1e-9 A current tolerance could contribute up to V_mp * 1e-9 A / |f'(I)| =
2.7e-8 W per power evaluation, but Newton's quadratic convergence normally
leaves the residual near 1e-15 A, so the measured error at STC against a
tightly converged reference is 3e-14 W (1.2e-7 V in V_mp).

Limits of the model
-------------------
Teaching model only. It reproduces the shape of real module curves but its
parameters are synthetic; it ignores spectrum, angle of incidence, soiling,
mismatch, partial shading, bypass diodes, wiring, converter losses and ageing;
and it has not been compared with any measured module. Do not use it to size
or guarantee a real PV system.

How to reproduce (from the repository root)
-------------------------------------------
python labs/renewable-energy/pv_model.py                     # default STC example
python labs/renewable-energy/pv_model.py --mppt              # add the P&O trajectory
python labs/renewable-energy/pv_model.py --irradiance 600 --temperature 50
python labs/renewable-energy/pv_model.py --json              # include I-V samples
python labs/renewable-energy/pv_model.py --plot --out pv.png # optional matplotlib
python -m unittest tests.test_lab_pv_model
"""
from __future__ import annotations

import argparse
import json
import math
import sys

# Physical constants (exact SI 2019 values).
BOLTZMANN_J_PER_K = 1.380649e-23
ELEMENTARY_CHARGE_C = 1.602176634e-19
KELVIN_OFFSET = 273.15

# Standard test conditions and validation ranges.
IRRADIANCE_STC = 1000.0          # W/m^2
TEMPERATURE_STC_C = 25.0         # degC
IRRADIANCE_MAX = 2000.0          # W/m^2, above any terrestrial value
TEMPERATURE_MIN_C = -40.0
TEMPERATURE_MAX_C = 100.0
IDEALITY_MIN = 0.5
IDEALITY_MAX = 3.0
ALPHA_ABS_MAX = 0.01             # 1/K
BAND_GAP_MIN_EV = 0.3
BAND_GAP_MAX_EV = 4.0
MAX_CELLS = 10000
MAX_POINTS = 100001
MAX_PNO_ITERATIONS = 100000
I_SC_MIN_A = 1e-6                # below this the diode model degenerates numerically
V_OC_MIN_V = 1e-3
VOC_OVER_A_MAX = 100.0           # V_oc / a at STC; real cells lie between 15 and 30
PNO_START_FRACTION = 0.4         # default P&O start voltage as a fraction of V_oc,STC

# Numerical settings.
CURRENT_TOLERANCE_A = 1e-9
VOLTAGE_TOLERANCE_V = 1e-6
MAX_SOLVER_ITERATIONS = 200
EXP_ARGUMENT_LIMIT = 700.0       # exp() argument clamp; not reachable for validated inputs
MPP_GRID_POINTS = 401
PNO_WINDOW = 8

MODEL_NAME = "single-diode-pv-module"
VALIDATION_STATUS = "numerical-simulation"
ASSUMPTIONS = [
    "single lumped diode for the whole module; identical, uniformly illuminated cells at one temperature",
    "photocurrent proportional to irradiance and linear in temperature: I_ph = I_sc,STC (G/1000) (1 + alpha (T - 25))",
    "photocurrent identified with the STC short-circuit current (diode and shunt currents at V = 0 neglected, error about R_s/R_sh)",
    "saturation current at STC derived so that I(V_oc,STC) = 0",
    "I_0(T) = I_0,STC (T/T_STC)^3 exp(q E_g/(n k_B) (1/T_STC - 1/T)) with a constant band gap E_g in eV (q E_g in joules)",
    "constant R_s, R_sh and ideality factor, independent of irradiance and temperature",
    "cell temperature is an input: no thermal model links it to ambient temperature, irradiance or wind",
    "steady state: no capacitance and no converter dynamics; in the P&O demonstration the converter imposes each commanded voltage exactly and the power is measured without noise",
]
LIMITATIONS = [
    "synthetic parameters; no comparison with a measured module (not validated hardware performance)",
    "no spectral or angle-of-incidence effects; irradiance is a single plane-of-module number",
    "no partial shading, bypass diodes, mismatch or reverse-bias breakdown (voltages below 0 V are rejected)",
    "no wiring, connector or converter losses; the MPPT demonstration is lossless",
    "cell-to-module scaling by series connection only (N_s identical cells, one string)",
    "no thermal model: cell temperature is an input, not computed from ambient temperature and wind",
]


def default_parameters():
    """Return the synthetic 60-cell module used by the lesson (STC datasheet-style values)."""
    return {
        "cells_in_series": 60,
        "i_sc_stc": 9.0,        # A
        "v_oc_stc": 37.5,       # V
        "ideality": 1.3,        # 1
        "r_s": 0.3,             # Ohm
        "r_sh": 300.0,          # Ohm
        "alpha_isc": 0.0005,    # 1/K  (+0.05 %/K)
        "band_gap_ev": 1.12,    # eV
    }


# --------------------------------------------------------------------------- #
# Validation helpers
# --------------------------------------------------------------------------- #
def _quantity(value, unit):
    return {"value": float(value), "unit": unit}


def _check_finite(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    try:
        number = float(value)  # a huge int raises OverflowError here
    except (OverflowError, TypeError, ValueError):
        raise ValueError(f"{name} must be a finite number, got {value!r}") from None
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return number


def _check_positive(name, value, unit=""):
    number = _check_finite(name, value)
    if number <= 0:
        suffix = f" {unit}" if unit else ""
        raise ValueError(f"{name} must be positive, got {number}{suffix}")
    return number


def _check_int(name, value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, got {value!r}")
    if value < minimum or value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}, got {value}")
    return value


def validate_conditions(irradiance, temperature_c):
    """Validate operating conditions; return (irradiance in W/m^2, temperature in degC)."""
    irr = _check_finite("irradiance", irradiance)
    if irr < 0:
        raise ValueError(f"irradiance must be >= 0 W/m2, got {irr}")
    if irr > IRRADIANCE_MAX:
        raise ValueError(f"irradiance must be <= {IRRADIANCE_MAX:g} W/m2 (terrestrial range), got {irr}")
    temp = _check_finite("temperature_c", temperature_c)
    if temp < TEMPERATURE_MIN_C or temp > TEMPERATURE_MAX_C:
        raise ValueError(
            f"temperature_c must be within [{TEMPERATURE_MIN_C:g}, {TEMPERATURE_MAX_C:g}] degC, got {temp}"
        )
    return irr, temp


def validate_parameters(params=None):
    """Return a validated copy of the module parameters.

    Missing keys are filled from default_parameters(); unknown keys are
    rejected. r_sh may be None (no shunt path) and is then stored as math.inf.
    Raises ValueError for non-finite, non-positive, out-of-range or
    inconsistent values.
    """
    merged = default_parameters()
    if params is not None:
        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary of module parameters")
        unknown = sorted(set(params) - set(merged))
        if unknown:
            raise ValueError(f"unknown parameter name(s): {', '.join(unknown)}")
        merged.update(params)

    cells = merged["cells_in_series"]
    if isinstance(cells, float) and math.isfinite(cells) and cells.is_integer():
        cells = int(cells)
    cells = _check_int("cells_in_series", cells, 1, MAX_CELLS)
    i_sc = _check_positive("i_sc_stc", merged["i_sc_stc"], "A")
    if i_sc < I_SC_MIN_A:
        raise ValueError(f"i_sc_stc must be >= {I_SC_MIN_A:g} A, got {i_sc}")
    v_oc = _check_positive("v_oc_stc", merged["v_oc_stc"], "V")
    if v_oc < V_OC_MIN_V:
        raise ValueError(f"v_oc_stc must be >= {V_OC_MIN_V:g} V, got {v_oc}")
    ideality = _check_finite("ideality", merged["ideality"])
    if not (IDEALITY_MIN < ideality < IDEALITY_MAX):
        raise ValueError(f"ideality must lie in ({IDEALITY_MIN}, {IDEALITY_MAX}), got {ideality}")
    r_s = _check_positive("r_s", merged["r_s"], "Ohm")
    r_sh_raw = merged["r_sh"]
    if r_sh_raw is None or (isinstance(r_sh_raw, float) and math.isinf(r_sh_raw) and r_sh_raw > 0):
        r_sh = math.inf
    else:
        r_sh = _check_positive("r_sh", r_sh_raw, "Ohm")
    alpha = _check_finite("alpha_isc", merged["alpha_isc"])
    if abs(alpha) > ALPHA_ABS_MAX:
        raise ValueError(f"alpha_isc must satisfy |alpha_isc| <= {ALPHA_ABS_MAX} 1/K, got {alpha}")
    band_gap = _check_finite("band_gap_ev", merged["band_gap_ev"])
    if not (BAND_GAP_MIN_EV < band_gap < BAND_GAP_MAX_EV):
        raise ValueError(f"band_gap_ev must lie in ({BAND_GAP_MIN_EV}, {BAND_GAP_MAX_EV}) eV, got {band_gap}")

    clean = {
        "cells_in_series": cells,
        "i_sc_stc": i_sc,
        "v_oc_stc": v_oc,
        "ideality": ideality,
        "r_s": r_s,
        "r_sh": r_sh,
        "alpha_isc": alpha,
        "band_gap_ev": band_gap,
    }
    # Consistency: the shunt current at open circuit must leave a positive diode
    # current; the series drop at short circuit must stay below V_oc, otherwise
    # the diode would conduct at V = 0 and I_sc could not be identified with
    # I_ph; and V_oc / a must be physically plausible (real cells: 15 to 30),
    # which also keeps every exponential far from overflow at -40 degC, 2 V_oc.
    if v_oc / r_sh >= i_sc:
        raise ValueError(
            f"inconsistent parameters: V_oc/R_sh = {v_oc / r_sh:.4g} A is not smaller than I_sc = {i_sc:.4g} A"
        )
    if r_s * i_sc >= v_oc:
        raise ValueError(
            f"inconsistent parameters: R_s * I_sc = {r_s * i_sc:.4g} V is not smaller than V_oc = {v_oc:.4g} V; "
            "the diode would conduct at short circuit and I_sc could not equal the datasheet value"
        )
    a_stc = thermal_voltage(TEMPERATURE_STC_C + KELVIN_OFFSET, ideality, cells)
    if v_oc / a_stc > VOC_OVER_A_MAX:
        raise ValueError(
            f"inconsistent parameters: V_oc/a = {v_oc / a_stc:.4g} at STC exceeds {VOC_OVER_A_MAX:g} "
            "(real cells lie between 15 and 30); increase cells_in_series or the ideality factor, or reduce V_oc"
        )
    return clean


# --------------------------------------------------------------------------- #
# Physical building blocks
# --------------------------------------------------------------------------- #
def thermal_voltage(T_kelvin, n, cells_in_series):
    """Module thermal voltage a = n * N_s * k_B * T / q in volts.

    T_kelvin: absolute temperature in K (> 0); n: ideality factor (1);
    cells_in_series: N_s (integer >= 1). For one ideal cell (n = 1, N_s = 1)
    this is k_B T / q = 25.69 mV at 25 degC.
    """
    temp = _check_positive("T_kelvin", T_kelvin, "K")
    ideality = _check_finite("n", n)
    if not (IDEALITY_MIN < ideality < IDEALITY_MAX):
        raise ValueError(f"n must lie in ({IDEALITY_MIN}, {IDEALITY_MAX}), got {ideality}")
    cells = _check_int("cells_in_series", cells_in_series, 1, MAX_CELLS)
    return ideality * cells * BOLTZMANN_J_PER_K * temp / ELEMENTARY_CHARGE_C


def photocurrent(irradiance, temperature_c, i_sc_stc, alpha_isc):
    """Photocurrent I_ph in A.

    I_ph = i_sc_stc * (irradiance / 1000 W/m^2) * (1 + alpha_isc * (temperature_c - 25 degC)).
    irradiance in W/m^2 (0..2000), temperature_c in degC (-40..100), i_sc_stc in A,
    alpha_isc in 1/K. The photocurrent is identified with the STC short-circuit
    current (standard approximation; the diode and shunt currents at V = 0 are
    neglected, a relative error of about R_s/R_sh).
    """
    irr, temp = validate_conditions(irradiance, temperature_c)
    i_sc = _check_positive("i_sc_stc", i_sc_stc, "A")
    alpha = _check_finite("alpha_isc", alpha_isc)
    if abs(alpha) > ALPHA_ABS_MAX:
        raise ValueError(f"alpha_isc must satisfy |alpha_isc| <= {ALPHA_ABS_MAX} 1/K, got {alpha}")
    return i_sc * (irr / IRRADIANCE_STC) * (1.0 + alpha * (temp - TEMPERATURE_STC_C))


def saturation_current_stc(params=None):
    """Diode saturation current I_0 at STC in A, derived so that I(V_oc,STC) = 0.

    At open circuit no current flows through R_s, so the single-diode equation
    gives 0 = I_ph - I_0 (exp(V_oc/a) - 1) - V_oc/R_sh and therefore
    I_0 = (I_ph,STC - V_oc/R_sh) / (exp(V_oc/a_STC) - 1).
    Approximation: I_ph,STC is taken equal to I_sc,STC (see photocurrent()).
    The result is exact for the model's V_oc; the model's I_sc is then lower
    than the nominal value by about R_s/R_sh.
    """
    p = validate_parameters(params)
    a_stc = thermal_voltage(TEMPERATURE_STC_C + KELVIN_OFFSET, p["ideality"], p["cells_in_series"])
    i_ph_stc = photocurrent(IRRADIANCE_STC, TEMPERATURE_STC_C, p["i_sc_stc"], p["alpha_isc"])
    numerator = i_ph_stc - p["v_oc_stc"] / p["r_sh"]
    return numerator / math.expm1(p["v_oc_stc"] / a_stc)


def saturation_current(params=None, temperature_c=TEMPERATURE_STC_C):
    """Diode saturation current I_0(T) in A at cell temperature temperature_c (degC).

    I_0(T) = I_0,STC * (T/T_STC)^3 * exp((q E_g / (n k_B)) * (1/T_STC - 1/T)),
    with T in kelvin and a constant band gap E_g in eV, so that q E_g is the gap
    energy in joules and q E_g / (n k_B) is a temperature (9.998e3 K for
    1.12 eV and n = 1.3). Including the ideality factor in the exponent is the
    usual choice in single-diode array models and gives a realistic
    open-circuit voltage temperature coefficient.
    """
    p = validate_parameters(params)
    _, temp = validate_conditions(IRRADIANCE_STC, temperature_c)
    i_0_stc = saturation_current_stc(p)
    t_k = temp + KELVIN_OFFSET
    t_stc = TEMPERATURE_STC_C + KELVIN_OFFSET
    exponent = (ELEMENTARY_CHARGE_C * p["band_gap_ev"] / (p["ideality"] * BOLTZMANN_J_PER_K)) * (1.0 / t_stc - 1.0 / t_k)
    return i_0_stc * (t_k / t_stc) ** 3 * math.exp(exponent)


def _operating_state(p, irradiance, temperature_c):
    """Collect the quantities that fix the I-V curve at one operating condition."""
    t_k = temperature_c + KELVIN_OFFSET
    return {
        "a": thermal_voltage(t_k, p["ideality"], p["cells_in_series"]),
        "i_ph": photocurrent(irradiance, temperature_c, p["i_sc_stc"], p["alpha_isc"]),
        "i_0": saturation_current(p, temperature_c),
        "r_s": p["r_s"],
        "r_sh": p["r_sh"],
        "t_k": t_k,
        "irradiance": irradiance,
        "temperature_c": temperature_c,
    }


# --------------------------------------------------------------------------- #
# Numerical solvers
# --------------------------------------------------------------------------- #
def _safe_exp(x):
    return math.exp(min(x, EXP_ARGUMENT_LIMIT))


def _safe_expm1(x):
    return math.expm1(min(x, EXP_ARGUMENT_LIMIT))


def _current_tolerance(i_ph):
    """Absolute residual tolerance in A: 1e-9 A, scaled down with I_ph when I_ph < 1 A."""
    if i_ph > 0.0:
        return CURRENT_TOLERANCE_A * min(1.0, i_ph)
    return CURRENT_TOLERANCE_A


def _safeguarded_newton(residual, derivative, lo, hi, x0, tolerance, what="current"):
    """Root of a strictly decreasing residual on [lo, hi] (residual(lo) > 0 > residual(hi)).

    Newton's method with the classical "rtsafe" safeguard: a Newton step is
    taken only when it stays strictly inside the current bracket and satisfies
    |2 f(x)| <= |dx_old f'(x)|, i.e. it is at most half the step taken two
    iterations earlier, so the bracket shrinks at least geometrically;
    otherwise the step is a bisection. (Accepting any step that merely reduces
    |f| would let the iteration crawl down a steep exponential one a/R_s at a
    time and exhaust the iteration budget.) Returns (root, evaluations).
    Raises ValueError prefixed "numerical failure" if the root is not bracketed
    or the iteration budget is spent.
    """
    f_lo = residual(lo)
    f_hi = residual(hi)
    evaluations = 2
    if abs(f_lo) <= tolerance:
        return lo, evaluations
    if abs(f_hi) <= tolerance:
        return hi, evaluations
    if f_lo < 0.0 or f_hi > 0.0:
        raise ValueError(f"numerical failure: the {what} root is not bracketed")
    x = min(max(x0, lo), hi)
    fx = residual(x)
    evaluations += 1
    dx_old = hi - lo
    dx = dx_old
    for _ in range(MAX_SOLVER_ITERATIONS):
        if abs(fx) <= tolerance:
            return x, evaluations
        if fx > 0.0:
            lo = x
        else:
            hi = x
        slope = derivative(x)
        newton_x = None
        if slope != 0.0:
            candidate = x - fx / slope
            if lo < candidate < hi and abs(2.0 * fx) <= abs(dx_old * slope):
                newton_x = candidate
        dx_old = dx
        if newton_x is not None:
            dx = newton_x - x
            x = newton_x
        else:
            dx = 0.5 * (hi - lo)
            x = lo + dx
        fx = residual(x)
        evaluations += 1
        if hi - lo <= 1e-15 * max(1.0, abs(x)):
            return x, evaluations
    raise ValueError(
        f"numerical failure: the {what} solver did not converge in {MAX_SOLVER_ITERATIONS} iterations"
    )


def _solve_current(v, state):
    """Current in A at terminal voltage v (V) for the given operating state."""
    i_ph, i_0, a, r_s, r_sh = state["i_ph"], state["i_0"], state["a"], state["r_s"], state["r_sh"]

    def residual(i):
        v_d = v + i * r_s
        return i_ph - i_0 * _safe_expm1(v_d / a) - v_d / r_sh - i

    def derivative(i):
        v_d = v + i * r_s
        return -i_0 * (r_s / a) * _safe_exp(v_d / a) - r_s / r_sh - 1.0

    lo = -(v / r_s + i_ph + 1.0)
    hi = i_ph
    guess = i_ph - i_0 * _safe_expm1(v / a) - v / r_sh
    root, _ = _safeguarded_newton(residual, derivative, lo, hi, guess, _current_tolerance(i_ph), "current")
    return root


def _open_circuit_voltage(state):
    """Open-circuit voltage in V (0 in the dark)."""
    i_ph, i_0, a, r_sh = state["i_ph"], state["i_0"], state["a"], state["r_sh"]
    if i_ph <= 0.0:
        return 0.0
    v_hi = a * math.log1p(i_ph / i_0)  # exact for R_sh -> infinity, an upper bound otherwise
    if math.isinf(r_sh):
        return v_hi

    def residual(v):
        return i_ph - i_0 * _safe_expm1(v / a) - v / r_sh

    def derivative(v):
        return -i_0 * _safe_exp(v / a) / a - 1.0 / r_sh

    root, _ = _safeguarded_newton(residual, derivative, 0.0, v_hi, v_hi, _current_tolerance(i_ph),
                                  "open-circuit voltage")
    return root


def _golden_section_maximum(fn, lo, hi, tolerance):
    """Maximise a unimodal function on [lo, hi]; return (argmax, evaluations)."""
    inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
    x1 = hi - inv_phi * (hi - lo)
    x2 = lo + inv_phi * (hi - lo)
    f1, f2 = fn(x1), fn(x2)
    evaluations = 2
    while hi - lo > tolerance and evaluations < 10000:
        if f1 < f2:
            lo, x1, f1 = x1, x2, f2
            x2 = lo + inv_phi * (hi - lo)
            f2 = fn(x2)
        else:
            hi, x2, f2 = x2, x1, f1
            x1 = hi - inv_phi * (hi - lo)
            f1 = fn(x1)
        evaluations += 1
    return 0.5 * (lo + hi), evaluations


def _mpp(state, grid_points):
    """Maximum power point of the operating state; returns a plain dict of floats."""
    v_oc = _open_circuit_voltage(state)
    if v_oc <= 0.0:
        return {"v_mp": 0.0, "i_mp": 0.0, "p_mp": 0.0, "v_oc": 0.0, "evaluations": 0, "grid_points": grid_points}
    voltages = [v_oc * k / (grid_points - 1) for k in range(grid_points)]
    powers = [v * _solve_current(v, state) for v in voltages]
    best = max(range(grid_points), key=powers.__getitem__)
    lo = voltages[max(best - 1, 0)]
    hi = voltages[min(best + 1, grid_points - 1)]
    v_mp, evaluations = _golden_section_maximum(lambda v: v * _solve_current(v, state), lo, hi, VOLTAGE_TOLERANCE_V)
    i_mp = _solve_current(v_mp, state)
    return {
        "v_mp": v_mp,
        "i_mp": i_mp,
        "p_mp": v_mp * i_mp,
        "v_oc": v_oc,
        "evaluations": grid_points + evaluations + 1,
        "grid_points": grid_points,
    }


# --------------------------------------------------------------------------- #
# Public model functions
# --------------------------------------------------------------------------- #
def current_at_voltage(v, params=None, irradiance=IRRADIANCE_STC, temperature_c=TEMPERATURE_STC_C):
    """Terminal current I in A at terminal voltage v (V), 0 <= v <= 2 V_oc,STC.

    Solves the implicit single-diode equation by safeguarded Newton iteration
    (rtsafe rule, bisection fallback) to a Kirchhoff current residual below
    1e-9 A (scaled with I_ph below 1 A). Above V_oc the current is negative
    (the module absorbs power). Reverse bias (v < 0) is outside the model and
    raises ValueError.
    """
    p = validate_parameters(params)
    irr, temp = validate_conditions(irradiance, temperature_c)
    volt = _check_finite("v", v)
    if volt < 0:
        raise ValueError(f"v must be >= 0 V (reverse bias is outside this model), got {volt}")
    limit = 2.0 * p["v_oc_stc"]
    if volt > limit:
        raise ValueError(f"v must be <= 2 * V_oc,STC = {limit:g} V, got {volt}")
    return _solve_current(volt, _operating_state(p, irr, temp))


def open_circuit_voltage(params=None, irradiance=IRRADIANCE_STC, temperature_c=TEMPERATURE_STC_C):
    """Open-circuit voltage V_oc in V at the given conditions (0 V at zero irradiance)."""
    p = validate_parameters(params)
    irr, temp = validate_conditions(irradiance, temperature_c)
    return _open_circuit_voltage(_operating_state(p, irr, temp))


def iv_curve(params=None, irradiance=IRRADIANCE_STC, temperature_c=TEMPERATURE_STC_C, points=201):
    """Sample the I-V and P-V curves on `points` equally spaced voltages from 0 to V_oc.

    Returns {"voltage_v": [...], "current_a": [...], "power_w": [...], "units": {...},
    "points": n}. At zero irradiance every sample is zero.
    """
    p = validate_parameters(params)
    irr, temp = validate_conditions(irradiance, temperature_c)
    n_points = _check_int("points", points, 2, MAX_POINTS)
    state = _operating_state(p, irr, temp)
    v_oc = _open_circuit_voltage(state)
    voltages = [v_oc * k / (n_points - 1) for k in range(n_points)]
    currents = [_solve_current(v, state) for v in voltages]
    powers = [v * i for v, i in zip(voltages, currents)]
    return {
        "voltage_v": voltages,
        "current_a": currents,
        "power_w": powers,
        "units": {"voltage_v": "V", "current_a": "A", "power_w": "W"},
        "points": n_points,
    }


def maximum_power_point(params=None, irradiance=IRRADIANCE_STC, temperature_c=TEMPERATURE_STC_C,
                        grid_points=MPP_GRID_POINTS):
    """Maximum power point by grid search plus golden-section refinement.

    P(V) is sampled at `grid_points` voltages on [0, V_oc]; the bracket around
    the best sample is then narrowed by golden-section search to 1e-6 V, which
    fixes P_mp to about 1e-12 W. The 1e-9 A current tolerance bounds the power
    error of each evaluation to about V_mp * 1e-9 A, 3e-8 W in the worst case,
    although Newton's quadratic convergence normally leaves the residual near
    1e-15 A (measured P_mp error at STC: 3e-14 W).
    """
    p = validate_parameters(params)
    irr, temp = validate_conditions(irradiance, temperature_c)
    n_grid = _check_int("grid_points", grid_points, 3, MAX_POINTS)
    state = _operating_state(p, irr, temp)
    mpp = _mpp(state, n_grid)
    i_sc = _solve_current(0.0, state)
    ff = None
    if mpp["v_oc"] > 0.0 and i_sc > 0.0:
        ff = _quantity(fill_factor(mpp["p_mp"], mpp["v_oc"], i_sc), "1")
    return {
        "model": MODEL_NAME,
        "validation_status": VALIDATION_STATUS,
        "conditions": {"irradiance": _quantity(irr, "W/m2"), "cell_temperature": _quantity(temp, "degC")},
        "v_mp": _quantity(mpp["v_mp"], "V"),
        "i_mp": _quantity(mpp["i_mp"], "A"),
        "p_mp": _quantity(mpp["p_mp"], "W"),
        "v_oc": _quantity(mpp["v_oc"], "V"),
        "i_sc": _quantity(i_sc, "A"),
        "fill_factor": ff,
        "search": {
            "method": "grid search then golden-section refinement",
            "grid_points": n_grid,
            "voltage_tolerance": _quantity(VOLTAGE_TOLERANCE_V, "V"),
            "function_evaluations": mpp["evaluations"],
        },
        "assumptions": list(ASSUMPTIONS),
        "limitations": list(LIMITATIONS),
    }


def fill_factor(p_mp, v_oc, i_sc):
    """Fill factor FF = P_mp / (V_oc * I_sc), dimensionless.

    p_mp in W (>= 0), v_oc in V, i_sc in A. Raises ValueError when V_oc * I_sc
    is zero or negative (undefined in the dark) or when the inputs give FF > 1.
    """
    power = _check_finite("p_mp", p_mp)
    voltage = _check_finite("v_oc", v_oc)
    current = _check_finite("i_sc", i_sc)
    if power < 0:
        raise ValueError(f"p_mp must be >= 0 W, got {power}")
    denominator = voltage * current
    if denominator <= 0:
        raise ValueError("fill factor is undefined when V_oc * I_sc <= 0 (for example at zero irradiance)")
    ff = power / denominator
    if ff > 1.0:
        raise ValueError(f"inconsistent inputs: fill factor {ff:.4g} exceeds 1")
    return ff


def _resolve_pno_settings(p, step_v, iterations, start_v):
    """Validate the P&O settings against validated parameters p; return (step_v, iterations, start_v).

    step_v in V (0 < step_v < V_oc,STC), iterations an integer in 1..100000,
    start_v in V (0 <= start_v <= 2 V_oc,STC); start_v None means
    PNO_START_FRACTION * V_oc,STC (15 V for the default module).
    """
    step = _check_positive("step_v", step_v, "V")
    if step >= p["v_oc_stc"]:
        raise ValueError(f"step_v must be smaller than V_oc,STC = {p['v_oc_stc']:g} V, got {step}")
    n_iter = _check_int("iterations", iterations, 1, MAX_PNO_ITERATIONS)
    if start_v is None:
        v_start = PNO_START_FRACTION * p["v_oc_stc"]
    else:
        v_start = _check_finite("start_v", start_v)
        if v_start < 0:
            raise ValueError(f"start_v must be >= 0 V, got {v_start}")
        if v_start > 2.0 * p["v_oc_stc"]:
            raise ValueError(f"start_v must be <= 2 * V_oc,STC = {2.0 * p['v_oc_stc']:g} V, got {v_start}")
    return step, n_iter, v_start


def perturb_and_observe(params=None, irradiance=IRRADIANCE_STC, temperature_c=TEMPERATURE_STC_C,
                        step_v=0.5, iterations=40, start_v=None):
    """Perturb-and-observe MPPT on the model with a fixed voltage step.

    At each iteration the operating voltage moves by step_v (V) in the current
    direction; if the new power is lower than the previous one (or the voltage
    hit 0 V or V_oc) the direction reverses. The converter is assumed to impose
    each commanded voltage exactly, the module to respond instantly (steady
    state) and the power to be measured without noise. start_v (V) defaults to
    0.4 V_oc,STC (15 V for the default module) and is clamped to V_oc when it
    is higher. Returns the trajectory, the final tracked point, the reference
    MPP and steady-state statistics over the last min(8, iterations)
    iterations.
    """
    p = validate_parameters(params)
    irr, temp = validate_conditions(irradiance, temperature_c)
    step, n_iter, v_start = _resolve_pno_settings(p, step_v, iterations, start_v)

    state = _operating_state(p, irr, temp)
    mpp = _mpp(state, MPP_GRID_POINTS)
    v_oc = mpp["v_oc"]
    v = min(v_start, v_oc)
    v_start_used = v
    i = _solve_current(v, state)
    power = v * i
    direction = 1.0
    iterations_list, voltages, currents, powers = [0], [v], [i], [power]
    reached = None
    for k in range(1, n_iter + 1):
        v_new = v + direction * step
        clamped = False
        if v_new > v_oc:
            v_new, clamped = v_oc, True
        if v_new < 0.0:
            v_new, clamped = 0.0, True
        i_new = _solve_current(v_new, state)
        p_new = v_new * i_new
        if p_new < power or clamped:
            direction = -direction
        v, i, power = v_new, i_new, p_new
        iterations_list.append(k)
        voltages.append(v)
        currents.append(i)
        powers.append(power)
        if reached is None and abs(v - mpp["v_mp"]) <= step:
            reached = k

    window = min(PNO_WINDOW, n_iter)
    tail_p = powers[-window:]
    tail_v = voltages[-window:]
    mean_power = sum(tail_p) / window
    efficiency = _quantity(mean_power / mpp["p_mp"], "1") if mpp["p_mp"] > 0 else None
    return {
        "model": MODEL_NAME,
        "validation_status": VALIDATION_STATUS,
        "algorithm": "perturb-and-observe, fixed voltage step, power compared with the previous iteration",
        "conditions": {"irradiance": _quantity(irr, "W/m2"), "cell_temperature": _quantity(temp, "degC")},
        "settings": {"step_v": _quantity(step, "V"), "start_v": _quantity(v_start_used, "V"), "iterations": n_iter},
        "trajectory": {
            "iteration": iterations_list,
            "voltage_v": voltages,
            "current_a": currents,
            "power_w": powers,
            "units": {"voltage_v": "V", "current_a": "A", "power_w": "W"},
        },
        "final_point": {"voltage": _quantity(v, "V"), "current": _quantity(i, "A"), "power": _quantity(power, "W")},
        "reference_mpp": {"v_mp": _quantity(mpp["v_mp"], "V"), "p_mp": _quantity(mpp["p_mp"], "W")},
        "iterations_to_reach_mpp_band": reached,
        "steady_state": {
            "window_iterations": window,
            "mean_power": _quantity(mean_power, "W"),
            "tracking_efficiency": efficiency,
            "voltage_band": _quantity(max(tail_v) - min(tail_v), "V"),
            "power_band": _quantity(max(tail_p) - min(tail_p), "W"),
        },
        "assumptions": ASSUMPTIONS,
        "limitations": LIMITATIONS,
    }


def _key_points(p, irradiance, temperature_c):
    state = _operating_state(p, irradiance, temperature_c)
    mpp = _mpp(state, MPP_GRID_POINTS)
    i_sc = _solve_current(0.0, state)
    ff = fill_factor(mpp["p_mp"], mpp["v_oc"], i_sc) if (mpp["v_oc"] > 0 and i_sc > 0) else None
    return {"irradiance": irradiance, "temperature_c": temperature_c, "i_sc": i_sc, "v_oc": mpp["v_oc"],
            "v_mp": mpp["v_mp"], "i_mp": mpp["i_mp"], "p_mp": mpp["p_mp"], "fill_factor": ff}


TABLE_COLUMNS = ["irradiance", "temperature_c", "i_sc", "v_oc", "v_mp", "i_mp", "p_mp", "fill_factor"]
TABLE_UNITS = ["W/m2", "degC", "A", "V", "V", "A", "W", "1"]


def irradiance_temperature_table(params=None, irradiances=(200.0, 400.0, 600.0, 800.0, 1000.0),
                                 temperatures=(0.0, 25.0, 50.0, 75.0),
                                 sweep_temperature_c=TEMPERATURE_STC_C, sweep_irradiance=IRRADIANCE_STC):
    """Effect of irradiance (at sweep_temperature_c) and temperature (at sweep_irradiance) on the key points.

    Returns two tables of rows [G, T, I_sc, V_oc, V_mp, I_mp, P_mp, FF] with the
    column units, plus the model's own temperature coefficients at STC from a
    central difference of +/-1 K: alpha (I_sc), beta (V_oc) and gamma (P_mp) in %/K.
    """
    p = validate_parameters(params)
    if not isinstance(irradiances, (list, tuple)) or not isinstance(temperatures, (list, tuple)):
        raise ValueError("irradiances and temperatures must be lists or tuples of numbers")
    if not irradiances or not temperatures:
        raise ValueError("irradiances and temperatures must be non-empty sequences")
    _, t_sweep = validate_conditions(IRRADIANCE_STC, sweep_temperature_c)
    g_sweep, _ = validate_conditions(sweep_irradiance, TEMPERATURE_STC_C)
    rows_g = []
    for g in irradiances:
        irr, _ = validate_conditions(g, t_sweep)
        kp = _key_points(p, irr, t_sweep)
        rows_g.append([kp[c] for c in TABLE_COLUMNS])
    rows_t = []
    for t in temperatures:
        _, temp = validate_conditions(g_sweep, t)
        kp = _key_points(p, g_sweep, temp)
        rows_t.append([kp[c] for c in TABLE_COLUMNS])

    plus = _key_points(p, IRRADIANCE_STC, TEMPERATURE_STC_C + 1.0)
    minus = _key_points(p, IRRADIANCE_STC, TEMPERATURE_STC_C - 1.0)
    stc = _key_points(p, IRRADIANCE_STC, TEMPERATURE_STC_C)

    def coefficient(key):
        return 100.0 * (plus[key] - minus[key]) / 2.0 / stc[key]

    return {
        "model": MODEL_NAME,
        "validation_status": VALIDATION_STATUS,
        "columns": TABLE_COLUMNS,
        "units": TABLE_UNITS,
        "irradiance_sweep": {"cell_temperature": _quantity(t_sweep, "degC"), "rows": rows_g},
        "temperature_sweep": {"irradiance": _quantity(g_sweep, "W/m2"), "rows": rows_t},
        "temperature_coefficients_at_stc": {
            "method": "central difference over +/-1 K at 1000 W/m2, relative to the STC value",
            "alpha_isc_model": _quantity(coefficient("i_sc"), "%/K"),
            "beta_voc_model": _quantity(coefficient("v_oc"), "%/K"),
            "gamma_pmp_model": _quantity(coefficient("p_mp"), "%/K"),
        },
        "assumptions": list(ASSUMPTIONS),
        "limitations": list(LIMITATIONS),
    }


def calculate(irradiance=IRRADIANCE_STC, temperature_c=TEMPERATURE_STC_C, points=201, params=None,
              mppt=False, include_curve=False, step_v=0.5, iterations=40, start_v=None):
    """Complete lesson result for one operating condition (the CLI prints this as JSON).

    The P&O settings are validated even when mppt is False, so an invalid
    --step-v, --iterations or --start-v is always rejected (ValueError).
    """
    p = validate_parameters(params)
    irr, temp = validate_conditions(irradiance, temperature_c)
    n_points = _check_int("points", points, 2, MAX_POINTS)
    step, n_iter, v_start = _resolve_pno_settings(p, step_v, iterations, start_v)
    state = _operating_state(p, irr, temp)
    state_stc = _operating_state(p, IRRADIANCE_STC, TEMPERATURE_STC_C)
    mpp = maximum_power_point(p, irr, temp)
    curve = iv_curve(p, irr, temp, n_points)
    table = irradiance_temperature_table(p)
    cells = p["cells_in_series"]
    kt_over_q = BOLTZMANN_J_PER_K * state["t_k"] / ELEMENTARY_CHARGE_C

    sample_index = [round(k * (n_points - 1) / 10) for k in range(11)]
    samples = [
        {"voltage": _quantity(curve["voltage_v"][k], "V"), "current": _quantity(curve["current_a"][k], "A"),
         "power": _quantity(curve["power_w"][k], "W")}
        for k in sample_index
    ]

    result = {
        "model": MODEL_NAME,
        "validation_status": VALIDATION_STATUS,
        "lesson": "solar-pv-fundamentals",
        "assumptions": ASSUMPTIONS,
        "limitations": LIMITATIONS,
        "parameters": {
            "cells_in_series": cells,
            "i_sc_stc": _quantity(p["i_sc_stc"], "A"),
            "v_oc_stc": _quantity(p["v_oc_stc"], "V"),
            "ideality": _quantity(p["ideality"], "1"),
            "r_s": _quantity(p["r_s"], "Ohm"),
            "r_sh": (_quantity(p["r_sh"], "Ohm") if math.isfinite(p["r_sh"])
                     else {"value": None, "unit": "Ohm", "note": "no shunt path"}),
            "alpha_isc": _quantity(p["alpha_isc"], "1/K"),
            "band_gap": _quantity(p["band_gap_ev"], "eV"),
        },
        "conditions": {"irradiance": _quantity(irr, "W/m2"), "cell_temperature": _quantity(temp, "degC"),
                       "cell_temperature_kelvin": _quantity(state["t_k"], "K")},
        "derived_parameters": {
            "thermal_voltage_cell_kT_over_q": _quantity(kt_over_q, "V"),
            "thermal_voltage_module_a": _quantity(state["a"], "V"),
            "thermal_voltage_module_a_stc": _quantity(state_stc["a"], "V"),
            "photocurrent": _quantity(state["i_ph"], "A"),
            "saturation_current_stc": _quantity(state_stc["i_0"], "A"),
            "saturation_current": _quantity(state["i_0"], "A"),
        },
        "key_points": {
            "short_circuit_current": _quantity(mpp["i_sc"]["value"], "A"),
            "open_circuit_voltage": _quantity(mpp["v_oc"]["value"], "V"),
            "v_mp": mpp["v_mp"],
            "i_mp": mpp["i_mp"],
            "p_mp": mpp["p_mp"],
            "fill_factor": mpp["fill_factor"],
            "per_cell": {
                "open_circuit_voltage": _quantity(mpp["v_oc"]["value"] / cells, "V"),
                "v_mp": _quantity(mpp["v_mp"]["value"] / cells, "V"),
                "p_mp": _quantity(mpp["p_mp"]["value"] / cells, "W"),
            },
            "search": mpp["search"],
        },
        "iv_curve_samples": samples,
        "sensitivity": table,
        "reproducibility": {
            "python_version": sys.version.split()[0],
            "current_tolerance": _quantity(CURRENT_TOLERANCE_A, "A"),
            "voltage_tolerance": _quantity(VOLTAGE_TOLERANCE_V, "V"),
        },
    }
    if mppt:
        result["mppt"] = perturb_and_observe(p, irr, temp, step, n_iter, v_start)
    if include_curve:
        result["iv_curve"] = curve
    return result


# --------------------------------------------------------------------------- #
# Command line
# --------------------------------------------------------------------------- #
def build_parser():
    parser = argparse.ArgumentParser(
        prog="pv_model.py",
        description=("Single-diode PV module model with maximum power point and perturb-and-observe "
                     "MPPT (AIPE Academy teaching lab, standard library only; not validated hardware "
                     "performance). Prints indented JSON."),
    )
    parser.add_argument("--irradiance", type=float, default=IRRADIANCE_STC,
                        help="plane-of-module irradiance in W/m2 (default 1000)")
    parser.add_argument("--temperature", type=float, default=TEMPERATURE_STC_C,
                        help="cell temperature in degC (default 25)")
    parser.add_argument("--points", type=int, default=201,
                        help="number of I-V samples from 0 V to V_oc (default 201; the MPP search uses "
                             "its own 401-point grid)")
    parser.add_argument("--mppt", action="store_true",
                        help="run the perturb-and-observe tracker and include its trajectory")
    parser.add_argument("--step-v", type=float, default=0.5,
                        help="P&O voltage step in V (default 0.5; validated even without --mppt)")
    parser.add_argument("--iterations", type=int, default=40, help="P&O iterations (default 40)")
    parser.add_argument("--start-v", type=float, default=None,
                        help="P&O starting voltage in V (default 0.4 * V_oc,STC, i.e. 15 V for the default "
                             "module; values above V_oc are clamped to V_oc)")
    parser.add_argument("--json", action="store_true",
                        help="include the full I-V curve samples in the JSON (the default output is the "
                             "same JSON without the long arrays)")
    parser.add_argument("--plot", action="store_true",
                        help="draw the I-V and P-V curves with matplotlib (optional; exits 0 with a "
                             "message if it is missing)")
    parser.add_argument("--out", default=None, help="with --plot: save the figure to this file instead of showing it")
    group = parser.add_argument_group("module parameter overrides (defaults: the lesson's synthetic 60-cell module)")
    group.add_argument("--cells", type=int, default=None, help="cells in series (default 60)")
    group.add_argument("--i-sc", type=float, default=None, help="short-circuit current at STC in A (default 9.0)")
    group.add_argument("--v-oc", type=float, default=None, help="open-circuit voltage at STC in V (default 37.5)")
    group.add_argument("--ideality", type=float, default=None, help="diode ideality factor (default 1.3)")
    group.add_argument("--r-s", type=float, default=None, help="series resistance in Ohm (default 0.3)")
    group.add_argument("--r-sh", type=float, default=None,
                       help="shunt resistance in Ohm (default 300; use inf for no shunt path)")
    group.add_argument("--alpha-isc", type=float, default=None,
                       help="temperature coefficient of I_sc in 1/K (default 0.0005)")
    group.add_argument("--band-gap", type=float, default=None, help="band gap in eV (default 1.12)")
    return parser


def _params_from_args(args):
    params = default_parameters()
    mapping = {"cells": "cells_in_series", "i_sc": "i_sc_stc", "v_oc": "v_oc_stc", "ideality": "ideality",
               "r_s": "r_s", "r_sh": "r_sh", "alpha_isc": "alpha_isc", "band_gap": "band_gap_ev"}
    for arg_name, key in mapping.items():
        value = getattr(args, arg_name)
        if value is not None:
            params[key] = value
    return params


def _plot(result, out_path):
    """Draw the I-V and P-V curves (and the P&O trajectory if present). Lazy matplotlib import."""
    try:
        import matplotlib
        if out_path:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; skipping the plot. Install it with "
              "'python -m pip install matplotlib' or read the JSON output instead.", file=sys.stderr)
        return 0
    curve = result["iv_curve"]
    fig, ax_i = plt.subplots(figsize=(7, 4.5))
    ax_i.plot(curve["voltage_v"], curve["current_a"], label="I-V")
    ax_i.set_xlabel("module voltage V (V)")
    ax_i.set_ylabel("current I (A)")
    ax_p = ax_i.twinx()
    ax_p.plot(curve["voltage_v"], curve["power_w"], linestyle="--", label="P-V")
    ax_p.set_ylabel("power P (W)")
    kp = result["key_points"]
    ax_p.plot([kp["v_mp"]["value"]], [kp["p_mp"]["value"]], marker="o", label="MPP")
    if "mppt" in result:
        traj = result["mppt"]["trajectory"]
        ax_p.plot(traj["voltage_v"], traj["power_w"], marker=".", linewidth=0.8, label="P&O trajectory")
    cond = result["conditions"]
    ax_i.set_title(f"Single-diode PV module model, {cond['irradiance']['value']:g} W/m2, "
                   f"{cond['cell_temperature']['value']:g} degC (teaching model)")
    handles = ax_i.get_legend_handles_labels()[0] + ax_p.get_legend_handles_labels()[0]
    labels = ax_i.get_legend_handles_labels()[1] + ax_p.get_legend_handles_labels()[1]
    ax_i.legend(handles, labels, loc="lower left")
    fig.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=120)
        print(f"plot saved to {out_path}", file=sys.stderr)  # keep stdout pure JSON
    else:
        plt.show()
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = calculate(
            irradiance=args.irradiance,
            temperature_c=args.temperature,
            points=args.points,
            params=_params_from_args(args),
            mppt=args.mppt,
            include_curve=args.json or args.plot,
            step_v=args.step_v,
            iterations=args.iterations,
            start_v=args.start_v,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (ZeroDivisionError, OverflowError) as exc:  # backstop: never print a traceback
        print(f"error: numerical failure: {exc}", file=sys.stderr)
        return 2
    output = dict(result)
    if args.plot and not args.json:
        output.pop("iv_curve", None)
    print(json.dumps(output, indent=2, allow_nan=False))
    if args.plot:
        return _plot(result, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
