"""Balanced three-phase circuits, complex power, power-factor correction and per-unit bases.

Purpose
-------
Reproducible teaching calculations for the AIPE Academy lesson "Three-phase
system fundamentals: balanced operation, power and the per-unit system"
(curriculum/power-systems/ac-power-networks/three-phase-fundamentals.md).
Everything here is an analytical/numerical teaching model.  It describes an
idealised balanced circuit; it is not a validated model of any real
installation and nothing in it has been checked against hardware.

Inputs (SI units)
-----------------
v_line_rms      line-to-line RMS voltage, V
z_phase         load impedance per phase, Ohm, as a complex number R + jX
frequency       supply frequency, Hz
i_line_rms      line RMS current, A (instantaneous-power evaluation)
pf_angle_deg    angle by which the current lags the phase voltage, deg
p_w             three-phase real power of the load to be corrected, W
pf_old, pf_new  power factors, dimensionless, each in (0, 1]
s_base          three-phase apparent-power base, VA
v_base          line-to-line voltage base, V

Model assumptions
-----------------
* Sinusoidal steady state at one frequency: no harmonics, no transients.
* A balanced positive-sequence (abc) source.  V_an = V_phase at 0 deg is the
  angle reference, V_bn is at -120 deg and V_cn at +120 deg.
* Three identical linear time-invariant impedances; an ideal source with zero
  internal impedance and zero line impedance.
* Load (passive) sign convention: per phase S = V I*, so Q > 0 is reactive
  power absorbed by an inductive load (current lags, "lagging" power factor)
  and Q < 0 is capacitive (current leads, "leading").
* Three-phase per-unit convention: S_base is the three-phase apparent power
  and V_base the line-to-line voltage, so Z_base = V_base**2 / S_base and
  I_base = S_base / (sqrt(3) * V_base).  Line-to-line and line-to-neutral
  voltages then have the same per-unit value.

Outputs
-------
Dictionaries.  Physical quantities are {"value": float, "unit": "<SI symbol>"}
("1" marks a dimensionless ratio, "pu" a per-unit value).  Each result carries
"model", "validation_status" ("analytical-example" for closed-form phasor
results, "numerical-simulation" for the sampled instantaneous-power
evaluation), "assumptions" and "limitations".

Validation checks
-----------------
ValueError with a specific message for: non-finite numbers; non-positive
voltages, currents, powers, frequencies or bases, or any of these above 1e12
in SI units; a negative resistance (the load must be passive); zero or
non-finite impedances, or an impedance magnitude outside [1e-9, 1e12] Ohm;
inputs so small that the computed power underflows to zero; power factors
outside (0, 1]; a correction target below the existing power factor when
pf_correction_capacitance() is called directly (analyse() reports a
"not-applicable" record instead); power-factor angles outside [-90, 90] deg;
sample counts outside [4, 1000000]; fewer or more than three phasors; and
unbalanced phasor sets where a balanced set is required.  No result ever
contains NaN or infinity (json.dumps(..., allow_nan=False)); the bare-number
helpers delta_to_wye, wye_to_delta, to_pu, from_pu and change_base raise
ValueError instead of returning infinity.  The CLI prints "error: <message>"
to standard error and exits with code 2 for every rejected input.

Limits of the model
-------------------
No harmonics, no unbalanced-load solution (unbalanced sets are detected and
rejected, never silently averaged), no line, source or transformer impedance,
lossless correction capacitors, no temperature or frequency dependence of the
load, and no hardware validation of any kind.

Reproduce
---------
    python labs/power-systems/three_phase.py
    python labs/power-systems/three_phase.py --json
    python labs/power-systems/three_phase.py --v-line 400 --resistance 10 --reactance 5 --frequency 50 --pf-target 0.95 --s-base 100000 --v-base 11000
    python labs/power-systems/three_phase.py --plot --out three_phase.png
    python -m unittest tests.test_lab_three_phase
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
import sys

SQRT2 = math.sqrt(2.0)
SQRT3 = math.sqrt(3.0)
PHASE_OFFSETS_DEG = {"a": 0.0, "b": -120.0, "c": 120.0}
DEFAULT_V_LINE = 400.0
DEFAULT_Z_PHASE = complex(10.0, 5.0)
DEFAULT_FREQUENCY = 50.0
DEFAULT_PF_TARGET = 0.95
DEFAULT_S_BASE = 100_000.0
DEFAULT_V_BASE = 11_000.0
PLAUSIBLE_MAX = 1e12          # upper bound for positive SI inputs; keeps every product finite
IMPEDANCE_MIN = 1e-9          # Ohm; a smaller magnitude is treated as a short circuit
MAX_SAMPLES = 1_000_000       # upper bound for n_points and explicit instants (memory, run time)
MAX_PHASE_RAD = 1e9           # bound on |2 pi f t| for explicit sample instants

SIGN_CONVENTION = (
    "Load convention, S = V I* per phase: Q > 0 means the load absorbs reactive "
    "power (inductive, current lags voltage, 'lagging' power factor); Q < 0 means "
    "the load supplies reactive power (capacitive, current leads, 'leading')."
)


# --------------------------------------------------------------------------- #
# Validation helpers
# --------------------------------------------------------------------------- #
def _is_real(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_finite(name: str, value) -> float:
    """Return value as float; raise ValueError unless it is a finite real number."""
    if not _is_real(value) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite real number, got {value!r}")
    return float(value)


def _require_positive(name: str, value, maximum: float = PLAUSIBLE_MAX) -> float:
    """Return value as float; raise ValueError unless it is finite, > 0 and <= maximum."""
    number = _require_finite(name, value)
    if number <= 0.0:
        raise ValueError(f"{name} must be positive, got {value!r}")
    if number > maximum:
        raise ValueError(f"{name} must be at most {maximum:g} (numerical range of this model), got {value!r}")
    return number


def _require_power_factor(name: str, value) -> float:
    """Return value as float; raise ValueError unless it lies in (0, 1]."""
    number = _require_finite(name, value)
    if not 0.0 < number <= 1.0:
        raise ValueError(f"{name} must lie in the interval (0, 1], got {value!r}")
    return number


def _require_complex(name: str, value) -> complex:
    """Return value as complex; raise ValueError if it is not a finite real or complex number."""
    if isinstance(value, bool) or not isinstance(value, (int, float, complex)):
        raise ValueError(f"{name} must be a real or complex number, got {value!r}")
    z = complex(value)
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ValueError(f"{name} must have finite real and imaginary parts, got {value!r}")
    return z


def _require_impedance(name: str, value) -> complex:
    """Return value as complex ohm; raise ValueError if non-finite, zero or outside [IMPEDANCE_MIN, PLAUSIBLE_MAX] Ohm."""
    z = _require_complex(name, value)
    if z == 0:
        raise ValueError(f"{name} must not be zero: a short circuit has no finite current in this model")
    try:
        magnitude = abs(z)
    except OverflowError:
        magnitude = math.inf
    if not IMPEDANCE_MIN <= magnitude <= PLAUSIBLE_MAX:
        raise ValueError(
            f"{name} magnitude must lie between {IMPEDANCE_MIN:g} and {PLAUSIBLE_MAX:g} Ohm "
            f"(numerical range of this model), got {value!r}"
        )
    return z


def _require_passive_impedance(name: str, value) -> complex:
    """Like _require_impedance, and the real part (resistance) must be non-negative: a passive load."""
    z = _require_impedance(name, value)
    if z.real < 0.0:
        raise ValueError(f"{name} resistance must be non-negative for a passive load, got {value!r}")
    return z


def _guard_underflow(what: str, value: float) -> float:
    """Return value; raise ValueError if a derived quantity underflowed to zero."""
    if value == 0.0:
        raise ValueError(f"{what} underflowed to zero: the inputs are outside the numerical range of this model")
    return value


def _finite_result(name: str, value):
    """Return value; raise ValueError if the arithmetic overflowed to infinity or produced NaN."""
    z = complex(value)
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ValueError(f"{name}: result is not finite; the inputs are outside the numerical range of this model")
    return value


def _require_int(name: str, value, minimum: int, maximum=None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, got {value!r}")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value!r}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}, got {value!r}")
    return value


def _require_three_phasors(name: str, phasors) -> list:
    try:
        items = list(phasors)
    except TypeError as exc:
        raise ValueError(f"{name} must be a sequence of three phasors") from exc
    if len(items) != 3:
        raise ValueError(f"{name} must contain exactly three phasors, got {len(items)}")
    return [_require_complex(f"{name}[{index}]", item) for index, item in enumerate(items)]


# --------------------------------------------------------------------------- #
# Phasor helpers
# --------------------------------------------------------------------------- #
def phasor(magnitude, angle_deg) -> complex:
    """Build the complex phasor magnitude * exp(j * angle).

    magnitude: RMS magnitude in the quantity's own unit (V, A, ...), >= 0.
    angle_deg: angle in degrees relative to the reference phasor.
    """
    mag = _require_finite("magnitude", magnitude)
    if mag < 0.0:
        raise ValueError(f"magnitude must be non-negative, got {magnitude!r}")
    angle = _require_finite("angle_deg", angle_deg)
    return cmath.rect(mag, math.radians(angle))


def wrap_degrees(angle_deg: float) -> float:
    """Wrap an angle in degrees into the interval (-180, 180]."""
    wrapped = (angle_deg + 180.0) % 360.0 - 180.0
    return 180.0 if wrapped == -180.0 else wrapped


def polar(value) -> tuple:
    """Return (magnitude, angle_deg) of a complex phasor, angle in (-180, 180]."""
    z = _require_complex("value", value)
    magnitude, angle = cmath.polar(z)
    return magnitude, wrap_degrees(math.degrees(angle))


def _tidy_angle(angle_deg: float) -> float:
    """Round floating-point dust in an angle (e.g. -1e-14 deg) to 0.0 for display."""
    rounded = round(angle_deg, 9)
    return 0.0 if rounded == 0 else rounded


def quantity(value, unit: str) -> dict:
    """Wrap a finite number as {"value": float, "unit": unit}; -0.0 becomes 0.0."""
    number = float(value) + 0.0
    if not math.isfinite(number):
        raise ValueError(f"result in unit {unit} is not finite: the inputs are outside the numerical range of this model")
    return {"value": number, "unit": unit}


def phasor_dict(value: complex, unit: str) -> dict:
    """Describe a phasor by RMS magnitude (unit) and angle (deg)."""
    magnitude, angle = polar(value)
    return {"magnitude": quantity(magnitude, unit), "angle": quantity(_tidy_angle(angle), "deg")}


def complex_dict(value: complex, unit: str) -> dict:
    """Describe a complex quantity by rectangular and polar components."""
    z = complex(value)
    magnitude, angle = polar(z)
    return {
        "real": quantity(z.real, unit),
        "imag": quantity(z.imag, unit),
        "magnitude": quantity(magnitude, unit),
        "angle": quantity(_tidy_angle(angle), "deg"),
    }


def balanced_phase_voltages(v_phase_rms) -> dict:
    """Balanced positive-sequence line-to-neutral phasors {a, b, c} in V (RMS)."""
    v_phase = _require_positive("v_phase_rms", v_phase_rms)
    return {name: phasor(v_phase, offset) for name, offset in PHASE_OFFSETS_DEG.items()}


def line_voltages_from_phase(v_phase: dict) -> dict:
    """Line-to-line phasors {ab, bc, ca} from line-to-neutral phasors {a, b, c}."""
    return {
        "ab": v_phase["a"] - v_phase["b"],
        "bc": v_phase["b"] - v_phase["c"],
        "ca": v_phase["c"] - v_phase["a"],
    }


# --------------------------------------------------------------------------- #
# Balance check
# --------------------------------------------------------------------------- #
def check_balanced(phasors, magnitude_tolerance=0.01, angle_tolerance_deg=1.0, unit="1") -> dict:
    """Report whether three phasors form a balanced set within the given tolerances.

    phasors: sequence of three complex phasors in any one unit.
    magnitude_tolerance: allowed (max - min) / mean of the magnitudes, dimensionless.
    angle_tolerance_deg: allowed deviation of the displacements from +/-120 deg.
    unit: SI symbol of the phasors ("V" or "A") used to label the reported
    magnitudes; "1" when unknown.

    A balanced set has equal magnitudes and displacements of exactly 120 deg;
    its three phasors sum to zero.  The report also identifies the phase
    sequence (abc = positive, acb = negative).  Nothing is averaged: an
    unbalanced set is reported as unbalanced so a caller can refuse it.
    """
    items = _require_three_phasors("phasors", phasors)
    mag_tol = _require_finite("magnitude_tolerance", magnitude_tolerance)
    ang_tol = _require_finite("angle_tolerance_deg", angle_tolerance_deg)
    if mag_tol < 0.0 or ang_tol < 0.0:
        raise ValueError("tolerances must be non-negative")
    try:
        magnitudes = [abs(z) for z in items]
    except OverflowError as exc:
        raise ValueError("phasor magnitudes overflow: the inputs are outside the numerical range of this model") from exc
    mean = sum(magnitudes) / 3.0
    if mean <= 0.0:
        raise ValueError("phasors must not all be zero")
    magnitude_spread = (max(magnitudes) - min(magnitudes)) / mean
    residual = abs(sum(items)) / mean
    if min(magnitudes) == 0.0:
        sequence, angle_error = "undetermined", 180.0
    else:
        angles = [math.degrees(cmath.phase(z)) for z in items]
        d_ab = wrap_degrees(angles[1] - angles[0])
        d_ac = wrap_degrees(angles[2] - angles[0])
        error_abc = max(abs(wrap_degrees(d_ab + 120.0)), abs(wrap_degrees(d_ac - 120.0)))
        error_acb = max(abs(wrap_degrees(d_ab - 120.0)), abs(wrap_degrees(d_ac + 120.0)))
        if error_abc <= error_acb:
            sequence, angle_error = "abc (positive sequence)", error_abc
        else:
            sequence, angle_error = "acb (negative sequence)", error_acb
    balanced = magnitude_spread <= mag_tol and angle_error <= ang_tol
    return {
        "model": "three-phasor-balance-check",
        "validation_status": "analytical-example",
        "assumptions": ["single-frequency phasors", "the first phasor is phase a"],
        "limitations": ["reports balance only; it does not resolve an unbalanced set into symmetrical components"],
        "balanced": balanced,
        "phase_sequence": sequence,
        "magnitude_spread": quantity(magnitude_spread, "1"),
        "max_angle_error": quantity(angle_error, "deg"),
        "sum_residual": quantity(residual, "1"),
        "magnitude_tolerance": quantity(mag_tol, "1"),
        "angle_tolerance": quantity(ang_tol, "deg"),
        "magnitudes": [quantity(m, unit) for m in magnitudes],
    }


def complex_power_from_phasors(voltages, currents, require_balanced=True,
                               magnitude_tolerance=0.01, angle_tolerance_deg=1.0) -> dict:
    """Total complex power S = sum(V_k * conj(I_k)) of three phase voltage/current pairs.

    voltages: three line-to-neutral RMS phasors in V; currents: three RMS phasors in A.
    With require_balanced=True (default) both sets must pass check_balanced();
    otherwise a ValueError names the unbalanced set.  The balanced-only
    shortcut S = 3 V_a I_a* is therefore never applied to an unbalanced set.
    """
    v = _require_three_phasors("voltages", voltages)
    i = _require_three_phasors("currents", currents)
    if require_balanced:
        for label, items in (("voltages", v), ("currents", i)):
            report = check_balanced(items, magnitude_tolerance, angle_tolerance_deg,
                                    unit="V" if label == "voltages" else "A")
            if not report["balanced"]:
                raise ValueError(
                    f"{label} are not a balanced set (magnitude spread "
                    f"{report['magnitude_spread']['value']:.4g}, angle error "
                    f"{report['max_angle_error']['value']:.4g} deg); refusing the balanced-set formula"
                )
    per_phase = [vk * ik.conjugate() for vk, ik in zip(v, i)]
    total = sum(per_phase)
    apparent = abs(total)
    return {
        "model": "complex-power-from-phasors",
        "validation_status": "analytical-example",
        "assumptions": ["load sign convention S = V I*", "RMS phasors"],
        "limitations": ["sinusoidal steady state only"],
        "per_phase_complex_power": [complex_dict(s, "VA") for s in per_phase],
        "total_real_power": quantity(total.real, "W"),
        "total_reactive_power": quantity(total.imag, "var"),
        "total_apparent_power": quantity(apparent, "VA"),
        "power_factor": quantity(total.real / apparent if apparent > 0 else 1.0, "1"),
        "sign_convention": SIGN_CONVENTION,
    }


# --------------------------------------------------------------------------- #
# Balanced loads
# --------------------------------------------------------------------------- #
def _power_factor_type(q: float, s: float) -> str:
    if abs(q) <= 1e-12 * s:
        return "unity"
    return "lagging" if q > 0 else "leading"


def _load_result(connection, v_line, v_phase_rms, z, f, v_phase, v_lines,
                 i_phase, i_line, s_phase_a, first_phase, branch_voltages) -> dict:
    s_total = 3.0 * s_phase_a
    p, q = s_total.real, s_total.imag
    s_mag = _guard_underflow("the load's apparent power", abs(s_total))
    i_phase_rms = _guard_underflow("the phase current", abs(i_phase[first_phase]))
    i_line_rms = abs(i_line["a"])
    z_mag, z_angle = polar(z)
    return {
        "model": f"balanced-{connection}-load",
        "validation_status": "analytical-example",
        "assumptions": [
            "sinusoidal steady state at a single frequency",
            "balanced positive-sequence (abc) source, V_an as the angle reference",
            "three identical linear impedances",
            "ideal source, zero line impedance",
        ],
        "limitations": [
            "no harmonics, transients, line drop or transformer model",
            "not validated against hardware",
        ],
        "connection": connection,
        "frequency": quantity(f, "Hz"),
        "angular_frequency": quantity(2.0 * math.pi * f, "rad/s"),
        "impedance_per_phase": {
            "resistance": quantity(z.real, "Ohm"),
            "reactance": quantity(z.imag, "Ohm"),
            "magnitude": quantity(z_mag, "Ohm"),
            "angle": quantity(_tidy_angle(z_angle), "deg"),
        },
        "line_voltage_rms": quantity(v_line, "V"),
        "phase_voltage_rms": quantity(v_phase_rms, "V"),
        "phase_current_rms": quantity(i_phase_rms, "A"),
        "line_current_rms": quantity(i_line_rms, "A"),
        "line_to_phase_voltage_ratio": quantity(v_line / v_phase_rms, "1"),
        "line_to_phase_current_ratio": quantity(i_line_rms / i_phase_rms, "1"),
        "phasors": {
            "line_to_neutral_voltages": {k: phasor_dict(v, "V") for k, v in v_phase.items()},
            "line_to_line_voltages": {k: phasor_dict(v, "V") for k, v in v_lines.items()},
            "branch_voltages": {k: phasor_dict(v, "V") for k, v in branch_voltages.items()},
            "phase_currents": {k: phasor_dict(i, "A") for k, i in i_phase.items()},
            "line_currents": {k: phasor_dict(i, "A") for k, i in i_line.items()},
        },
        "per_phase": {
            "real_power": quantity(s_phase_a.real, "W"),
            "reactive_power": quantity(s_phase_a.imag, "var"),
            "apparent_power": quantity(abs(s_phase_a), "VA"),
        },
        "total": {
            "real_power": quantity(p, "W"),
            "reactive_power": quantity(q, "var"),
            "apparent_power": quantity(s_mag, "VA"),
            "apparent_power_from_line_quantities": quantity(SQRT3 * v_line * i_line_rms, "VA"),
        },
        "power_factor": quantity(p / s_mag, "1"),
        "power_factor_angle": quantity(_tidy_angle(math.degrees(cmath.phase(s_total))), "deg"),
        "power_factor_type": _power_factor_type(q, s_mag),
        "sign_convention": SIGN_CONVENTION,
    }


def balanced_wye(v_line_rms=DEFAULT_V_LINE, z_phase=DEFAULT_Z_PHASE, frequency=DEFAULT_FREQUENCY) -> dict:
    """Solve a balanced wye (star) load.

    v_line_rms: line-to-line RMS voltage, V.  z_phase: impedance per phase, Ohm
    (complex R + jX with R >= 0: a passive load).  frequency: Hz.  Returns phase and line voltages and
    currents (RMS magnitude and angle), per-phase and total P (W), Q (var),
    S (VA), the power factor and its lagging/leading label.  In a wye the line
    current equals the phase current and V_line = sqrt(3) * V_phase.
    """
    v_line = _require_positive("v_line_rms", v_line_rms)
    z = _require_passive_impedance("z_phase", z_phase)
    f = _require_positive("frequency", frequency)
    v_phase_rms = v_line / SQRT3
    v_phase = balanced_phase_voltages(v_phase_rms)
    v_lines = line_voltages_from_phase(v_phase)
    currents = {name: v_phase[name] / z for name in "abc"}
    s_phase_a = v_phase["a"] * currents["a"].conjugate()
    return _load_result("wye", v_line, v_phase_rms, z, f, v_phase, v_lines,
                        currents, currents, s_phase_a, "a", v_phase)


def balanced_delta(v_line_rms=DEFAULT_V_LINE, z_phase=DEFAULT_Z_PHASE, frequency=DEFAULT_FREQUENCY) -> dict:
    """Solve a balanced delta (mesh) load.

    Same inputs and output structure as balanced_wye().  Each branch sees the
    full line-to-line voltage; the line current is sqrt(3) times the branch
    (phase) current and lags it by 30 deg.
    """
    v_line = _require_positive("v_line_rms", v_line_rms)
    z = _require_passive_impedance("z_phase", z_phase)
    f = _require_positive("frequency", frequency)
    v_phase = balanced_phase_voltages(v_line / SQRT3)
    v_lines = line_voltages_from_phase(v_phase)
    branch = {name: v_lines[name] / z for name in ("ab", "bc", "ca")}
    lines = {
        "a": branch["ab"] - branch["ca"],
        "b": branch["bc"] - branch["ab"],
        "c": branch["ca"] - branch["bc"],
    }
    s_branch_ab = v_lines["ab"] * branch["ab"].conjugate()
    return _load_result("delta", v_line, v_line, z, f, v_phase, v_lines,
                        branch, lines, s_branch_ab, "ab", v_lines)


def delta_to_wye(z_delta) -> complex:
    """Wye impedance per phase equivalent to a balanced delta of z_delta per branch: Z_Y = Z_delta / 3 (Ohm)."""
    return _finite_result("delta_to_wye", _require_impedance("z_delta", z_delta) / 3.0)


def wye_to_delta(z_wye) -> complex:
    """Delta impedance per branch equivalent to a balanced wye of z_wye per phase: Z_delta = 3 Z_Y (Ohm)."""
    return _finite_result("wye_to_delta", 3.0 * _require_impedance("z_wye", z_wye))


# --------------------------------------------------------------------------- #
# Instantaneous power
# --------------------------------------------------------------------------- #
def instantaneous_power(v_line_rms, i_line_rms, pf_angle_deg, frequency=DEFAULT_FREQUENCY,
                        times=None, n_points=360, include_samples=False) -> dict:
    """Sample the instantaneous power of each phase and of the three-phase total.

    v_line_rms: line-to-line RMS voltage, V (phase voltage = v_line / sqrt(3)).
    i_line_rms: line RMS current, A.  pf_angle_deg: angle by which the current
    lags its phase voltage, deg, in [-90, 90].  frequency: Hz.  times: optional
    sequence of instants in s (at most MAX_SAMPLES, each with |2 pi f t| <= 1e9
    rad); by default n_points instants (4 to MAX_SAMPLES) spanning one cycle.
    The report gives sample_count always and samples_per_cycle only for that
    default one-cycle grid.
    Each phase power pulsates at twice the supply frequency between
    V I (cos(phi) - 1) and V I (cos(phi) + 1) (per-phase V and I); the total of
    the three phases is the constant 3 V I cos(phi).  Returns the sampled
    minima and maxima, the analytical values and the numerical spread of the
    total, which should be at floating-point level.
    """
    v_line = _require_positive("v_line_rms", v_line_rms)
    i_line = _require_positive("i_line_rms", i_line_rms)
    phi_deg = _require_finite("pf_angle_deg", pf_angle_deg)
    if abs(phi_deg) > 90.0:
        raise ValueError(f"pf_angle_deg must lie in [-90, 90] for a passive load, got {pf_angle_deg!r}")
    f = _require_positive("frequency", frequency)
    omega = 2.0 * math.pi * f
    if times is None:
        n = _require_int("n_points", n_points, 4, MAX_SAMPLES)
        period = 1.0 / f
        sample_times = [k * period / n for k in range(n)]
    else:
        if isinstance(times, (str, bytes)):
            raise ValueError("times must be a sequence of instants in seconds")
        try:
            sample_times = [_require_finite(f"times[{k}]", t) for k, t in enumerate(times)]
        except TypeError as exc:
            raise ValueError("times must be a sequence of instants in seconds") from exc
        if not sample_times:
            raise ValueError("times must contain at least one instant")
        if len(sample_times) > MAX_SAMPLES:
            raise ValueError(f"times must contain at most {MAX_SAMPLES} instants, got {len(sample_times)}")
        for k, t in enumerate(sample_times):
            if abs(t) * omega > MAX_PHASE_RAD:
                raise ValueError(
                    f"times[{k}] is too large for the sampled model: |2 pi f t| must not exceed {MAX_PHASE_RAD:g} rad"
                )
    v_phase = v_line / SQRT3
    v_peak, i_peak = SQRT2 * v_phase, SQRT2 * i_line
    phi = math.radians(phi_deg)
    samples = {name: [] for name in "abc"}
    total = []
    for t in sample_times:
        running = 0.0
        for name, offset in PHASE_OFFSETS_DEG.items():
            theta = omega * t + math.radians(offset)
            p = v_peak * math.cos(theta) * i_peak * math.cos(theta - phi)
            samples[name].append(p)
            running += p
        total.append(running)
    apparent = _guard_underflow("the apparent power", 3.0 * v_phase * i_line)
    constant = apparent * math.cos(phi)
    spread = max(total) - min(total)
    counts = {"sample_count": len(sample_times)}
    if times is None:
        counts["samples_per_cycle"] = n
    result = {
        "model": "sampled-instantaneous-power",
        "validation_status": "numerical-simulation",
        "assumptions": [
            "balanced sinusoidal voltages and currents",
            "phase voltage = line voltage / sqrt(3) (wye or wye-equivalent)",
        ],
        "limitations": [
            "sampled extremes lie inside the analytical extremes unless a sample hits the peak",
            "no harmonics; one cycle only when times is not given",
        ],
        "frequency": quantity(f, "Hz"),
        **counts,
        "phase_a": {
            "sampled_min": quantity(min(samples["a"]), "W"),
            "sampled_max": quantity(max(samples["a"]), "W"),
            "analytical_min": quantity(v_phase * i_line * (math.cos(phi) - 1.0), "W"),
            "analytical_max": quantity(v_phase * i_line * (math.cos(phi) + 1.0), "W"),
            "pulsation_frequency": quantity(2.0 * f, "Hz"),
        },
        "total": {
            "sampled_min": quantity(min(total), "W"),
            "sampled_max": quantity(max(total), "W"),
            "sampled_mean": quantity(sum(total) / len(total), "W"),
            "analytical_constant": quantity(constant, "W"),
            "numerical_spread": quantity(spread, "W"),
            "spread_relative_to_apparent_power": quantity(spread / apparent, "1"),
        },
    }
    if include_samples:
        result["samples"] = {
            "units": {"time": "s", "p_a": "W", "p_b": "W", "p_c": "W", "p_total": "W"},
            "time": sample_times, "p_a": samples["a"], "p_b": samples["b"], "p_c": samples["c"], "p_total": total,
        }
    return result


# --------------------------------------------------------------------------- #
# Power-factor correction
# --------------------------------------------------------------------------- #
def pf_correction_capacitance(p_w, pf_old, pf_new, v_line_rms=DEFAULT_V_LINE, frequency=DEFAULT_FREQUENCY) -> dict:
    """Shunt capacitance that raises a lagging power factor from pf_old to pf_new.

    p_w: three-phase real power, W (unchanged by the capacitors).  pf_old and
    pf_new: power factors in (0, 1], pf_new >= pf_old.  v_line_rms: V.
    frequency: Hz.  Returns the reactive power to be supplied Q_c (var) and the
    capacitance per phase for wye-connected capacitors (each at V_line/sqrt(3)),
    C_Y = Q_c / (omega V_line**2), plus the delta alternative C_D = C_Y / 3 at
    full line voltage, and the apparent power and line current before and after.
    """
    p = _require_positive("p_w", p_w)
    pf_o = _require_power_factor("pf_old", pf_old)
    pf_n = _require_power_factor("pf_new", pf_new)
    if pf_n < pf_o:
        raise ValueError(
            f"pf_new ({pf_n}) must not be lower than pf_old ({pf_o}): "
            "shunt capacitors can only raise a lagging power factor"
        )
    v_line = _require_positive("v_line_rms", v_line_rms)
    f = _require_positive("frequency", frequency)
    omega = 2.0 * math.pi * f
    q_old = p * math.tan(math.acos(pf_o))
    q_new = p * math.tan(math.acos(pf_n))
    q_c = q_old - q_new
    c_wye = q_c / (omega * (v_line * v_line))
    c_delta = c_wye / 3.0
    s_old, s_new = p / pf_o, p / pf_n
    i_old = _guard_underflow("the line current", s_old / (SQRT3 * v_line))
    i_new = s_new / (SQRT3 * v_line)
    v_phase = v_line / SQRT3
    return {
        "model": "shunt-capacitor-power-factor-correction",
        "validation_status": "analytical-example",
        "assumptions": [
            "lagging (inductive) load whose real power is unchanged by the capacitors",
            "stiff supply: the line voltage does not change",
            "lossless capacitors at the supply frequency only",
        ],
        "limitations": [
            "no harmonic resonance check, no capacitor tolerance or ageing, no switching transients",
            "not validated against hardware",
        ],
        "real_power": quantity(p, "W"),
        "pf_old": quantity(pf_o, "1"),
        "pf_new": quantity(pf_n, "1"),
        "reactive_power_before": quantity(q_old, "var"),
        "reactive_power_after": quantity(q_new, "var"),
        "capacitor_reactive_power_total": quantity(q_c, "var"),
        "capacitor_reactive_power_per_phase": quantity(q_c / 3.0, "var"),
        "capacitance_per_phase_wye": quantity(c_wye, "F"),
        "capacitor_voltage_wye": quantity(v_phase, "V"),
        "capacitor_current_per_phase_wye": quantity((q_c / 3.0) / v_phase, "A"),
        "capacitance_per_phase_delta": quantity(c_delta, "F"),
        "capacitor_voltage_delta": quantity(v_line, "V"),
        "apparent_power_before": quantity(s_old, "VA"),
        "apparent_power_after": quantity(s_new, "VA"),
        "line_current_before": quantity(i_old, "A"),
        "line_current_after": quantity(i_new, "A"),
        "line_current_reduction": quantity(1.0 - i_new / i_old, "1"),
    }


# --------------------------------------------------------------------------- #
# Per-unit system
# --------------------------------------------------------------------------- #
def per_unit(s_base=DEFAULT_S_BASE, v_base=DEFAULT_V_BASE) -> dict:
    """Derived three-phase per-unit bases from s_base (VA, three-phase) and v_base (V, line-to-line).

    Z_base = V_base**2 / S_base (Ohm); I_base = S_base / (sqrt(3) V_base) (A);
    V_phase_base = V_base / sqrt(3) (V); Y_base = 1 / Z_base (S).
    """
    s = _require_positive("s_base", s_base)
    v = _require_positive("v_base", v_base)
    z_base = v * v / s
    return {
        "model": "three-phase-per-unit-bases",
        "validation_status": "analytical-example",
        "assumptions": ["S_base is three-phase apparent power", "V_base is line-to-line voltage"],
        "limitations": ["bases only; no network is solved here"],
        "s_base": quantity(s, "VA"),
        "v_base": quantity(v, "V"),
        "v_phase_base": quantity(v / SQRT3, "V"),
        "i_base": quantity(s / (SQRT3 * v), "A"),
        "z_base": quantity(z_base, "Ohm"),
        "y_base": quantity(1.0 / z_base, "S"),
    }


def _same_kind(value, result: complex):
    """Return result as float when the input was real, otherwise as complex."""
    return result.real if isinstance(value, (int, float)) else result


def to_pu(value, base):
    """Convert an SI value (real or complex) to per-unit: value / base.  base: positive finite SI quantity."""
    b = _require_positive("base", base, maximum=math.inf)
    z = _require_complex("value", value)
    return _same_kind(value, _finite_result("to_pu", z / b))


def from_pu(value_pu, base):
    """Convert a per-unit value (real or complex) back to SI: value_pu * base."""
    b = _require_positive("base", base, maximum=math.inf)
    z = _require_complex("value_pu", value_pu)
    return _same_kind(value_pu, _finite_result("from_pu", z * b))


def change_base(z_pu, s_old, v_old, s_new, v_new):
    """Re-express a per-unit impedance on new bases: z_pu * (S_new / S_old) * (V_old / V_new)**2."""
    z = _require_complex("z_pu", z_pu)
    s_o = _require_positive("s_old", s_old)
    v_o = _require_positive("v_old", v_old)
    s_n = _require_positive("s_new", s_new)
    v_n = _require_positive("v_new", v_new)
    ratio = v_o / v_n
    return _same_kind(z_pu, _finite_result("change_base", z * (s_n / s_o) * (ratio * ratio)))


# --------------------------------------------------------------------------- #
# Combined teaching example
# --------------------------------------------------------------------------- #
def analyse(v_line_rms=DEFAULT_V_LINE, resistance=DEFAULT_Z_PHASE.real, reactance=DEFAULT_Z_PHASE.imag,
            frequency=DEFAULT_FREQUENCY, pf_target=DEFAULT_PF_TARGET, s_base=DEFAULT_S_BASE,
            v_base=DEFAULT_V_BASE, n_points=360) -> dict:
    """Run the whole lesson example and return one JSON-serialisable dictionary.

    Sections: wye load, delta load with the same impedance, delta-to-wye
    equivalent, sampled instantaneous power, power-factor correction to
    pf_target (when the load is lagging and below the target; otherwise a
    "not-applicable" record, not an error), per-unit bases and the load
    expressed in per-unit, and the balance self-check.  resistance must be
    non-negative (passive load).
    """
    r = _require_finite("resistance", resistance)
    if r < 0.0:
        raise ValueError(f"resistance must be non-negative for a passive load, got {resistance!r}")
    x = _require_finite("reactance", reactance)
    z = _require_passive_impedance("z_phase", complex(r, x))
    pf_t = _require_power_factor("pf_target", pf_target)
    wye = balanced_wye(v_line_rms, z, frequency)
    for label, value, unit in (("apparent power", wye["total"]["apparent_power"]["value"], "VA"),
                               ("line current", wye["line_current_rms"]["value"], "A")):
        if value > PLAUSIBLE_MAX:
            raise ValueError(
                f"the load's {label} {value:.4g} {unit} exceeds the numerical range of this model "
                f"({PLAUSIBLE_MAX:g} {unit}); reduce v_line_rms or increase the impedance"
            )
    delta = balanced_delta(v_line_rms, z, frequency)
    z_equivalent = delta_to_wye(z)
    wye_from_delta = balanced_wye(v_line_rms, z_equivalent, frequency)
    v_line = wye["line_voltage_rms"]["value"]
    f = wye["frequency"]["value"]
    p_total = wye["total"]["real_power"]["value"]
    pf_load = wye["power_factor"]["value"]
    pf_type = wye["power_factor_type"]
    phi_deg = math.degrees(cmath.phase(z))  # impedance angle = power-factor angle of a passive load
    i_line = wye["line_current_rms"]["value"]
    instantaneous = instantaneous_power(v_line, i_line, phi_deg, f, n_points=n_points)
    if pf_type != "lagging":
        reason = f"the load power factor is {pf_type} (Q <= 0); shunt capacitors only correct a lagging load"
    elif p_total <= 0.0:
        reason = "the load draws no real power, so the correction relation Q = P tan(phi) does not apply"
    elif pf_load >= pf_t:
        reason = f"the load power factor {pf_load:.4f} already meets or exceeds the target {pf_t:.4f}"
    else:
        reason = None
    if reason is None:
        correction = pf_correction_capacitance(p_total, pf_load, pf_t, v_line, f)
    else:
        correction = {
            "model": "shunt-capacitor-power-factor-correction",
            "validation_status": "analytical-example",
            "assumptions": ["shunt capacitors only raise a lagging power factor; the real power is unchanged by them"],
            "limitations": ["no capacitance is sized in this case; see reason"],
            "status": "not-applicable",
            "reason": reason,
            "pf_old": quantity(pf_load, "1"),
            "pf_new": quantity(pf_t, "1"),
        }
    primary = per_unit(s_base, v_base)
    load_side = per_unit(s_base, v_line)
    ratio = primary["v_base"]["value"] / v_line
    z_pu_load_side = to_pu(z, load_side["z_base"]["value"])
    z_referred = z * (ratio * ratio)
    z_pu_primary = to_pu(z_referred, primary["z_base"]["value"])
    s_total = complex(p_total, wye["total"]["reactive_power"]["value"])
    s_pu = to_pu(s_total, primary["s_base"]["value"])
    i_pu_load_side = to_pu(i_line, load_side["i_base"]["value"])
    i_pu_primary = to_pu(i_line / ratio, primary["i_base"]["value"])
    phase_voltages = balanced_phase_voltages(wye["phase_voltage_rms"]["value"])
    balance = check_balanced(list(phase_voltages.values()), unit="V")
    return {
        "model": "balanced-three-phase-teaching-model",
        "validation_status": "analytical-example",
        "assumptions": [
            "balanced sinusoidal steady state; ideal stiff source; no line impedance",
            "load sign convention S = V I*",
            "three-phase per-unit bases (S three-phase, V line-to-line)",
            "an ideal transformer of ratio v_base / v_line separates the per-unit primary and load-side bases",
        ],
        "limitations": [
            "analytical/numerical teaching model; nothing here is validated hardware performance",
            "the instantaneous-power section is a sampled numerical evaluation; all other sections are closed-form",
            "unbalanced loads are detected, not solved; symmetrical components belong to module ps.faults",
        ],
        "python_version": sys.version.split()[0],
        "inputs": {
            "v_line_rms": quantity(v_line, "V"),
            "frequency": quantity(f, "Hz"),
            "resistance_per_phase": quantity(r, "Ohm"),
            "reactance_per_phase": quantity(x, "Ohm"),
            "pf_target": quantity(pf_t, "1"),
            "s_base": quantity(primary["s_base"]["value"], "VA"),
            "v_base": quantity(primary["v_base"]["value"], "V"),
        },
        "wye_load": wye,
        "delta_load": delta,
        "delta_to_wye_equivalent": {
            "model": "delta-wye-equivalence",
            "validation_status": "analytical-example",
            "assumptions": ["balanced impedances"],
            "limitations": ["the equivalence holds for line quantities and total power; branch currents differ"],
            "z_delta": complex_dict(z, "Ohm"),
            "z_wye_equivalent": complex_dict(z_equivalent, "Ohm"),
            "line_current_delta": delta["line_current_rms"],
            "line_current_wye_equivalent": wye_from_delta["line_current_rms"],
            "total_real_power_delta": delta["total"]["real_power"],
            "total_real_power_wye_equivalent": wye_from_delta["total"]["real_power"],
            "delta_to_wye_power_ratio_same_impedance": quantity(
                delta["total"]["real_power"]["value"] / p_total if p_total > 0.0
                else delta["total"]["apparent_power"]["value"] / wye["total"]["apparent_power"]["value"], "1"),
        },
        "instantaneous_power": instantaneous,
        "power_factor_correction": correction,
        "per_unit": {
            "model": "three-phase-per-unit",
            "validation_status": "analytical-example",
            "assumptions": [
                "same S_base on both sides of an ideal transformer whose ratio is v_base / v_line",
            ],
            "limitations": ["ideal transformer only; transformer impedance is the subject of ps.transformers"],
            "primary_base": primary,
            "load_side_base": load_side,
            "ideal_transformer_ratio": quantity(ratio, "1"),
            "load_voltage_pu": quantity(1.0, "pu"),
            "load_impedance_pu_on_load_side_base": complex_dict(z_pu_load_side, "pu"),
            "load_impedance_referred_to_primary": complex_dict(z_referred, "Ohm"),
            "load_impedance_pu_on_primary_base": complex_dict(z_pu_primary, "pu"),
            "load_complex_power_pu": complex_dict(s_pu, "pu"),
            "load_line_current_pu_load_side": quantity(i_pu_load_side, "pu"),
            "load_line_current_pu_primary": quantity(i_pu_primary, "pu"),
        },
        "balance_check": balance,
    }


# --------------------------------------------------------------------------- #
# Command-line interface
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="three_phase.py",
        description=(
            "Balanced three-phase teaching calculations: wye and delta loads, complex power, "
            "instantaneous power, power-factor correction and per-unit bases. "
            "Analytical/numerical model only; not validated hardware performance."
        ),
        epilog=(
            "Default example: 400 V line-to-line, 50 Hz, 10 + j5 Ohm per phase (wye), "
            "correction target 0.95, per-unit base 100 kVA / 11 kV.  Exit code 2 on invalid input."
        ),
    )
    parser.add_argument("--v-line", type=float, default=DEFAULT_V_LINE,
                        help="line-to-line RMS voltage in V (default 400)")
    parser.add_argument("--resistance", type=float, default=DEFAULT_Z_PHASE.real,
                        help="load resistance per phase in Ohm (default 10)")
    parser.add_argument("--reactance", type=float, default=DEFAULT_Z_PHASE.imag,
                        help="load reactance per phase in Ohm; positive = inductive, negative = capacitive (default 5)")
    parser.add_argument("--frequency", type=float, default=DEFAULT_FREQUENCY,
                        help="supply frequency in Hz (default 50)")
    parser.add_argument("--pf-target", type=float, default=DEFAULT_PF_TARGET,
                        help="target power factor for shunt-capacitor correction, in (0, 1] (default 0.95)")
    parser.add_argument("--s-base", type=float, default=DEFAULT_S_BASE,
                        help="three-phase apparent-power base in VA (default 100000)")
    parser.add_argument("--v-base", type=float, default=DEFAULT_V_BASE,
                        help="line-to-line voltage base in V (default 11000)")
    parser.add_argument("--points", type=int, default=360,
                        help="samples per cycle for the instantaneous-power evaluation, 4 to 1000000 (default 360)")
    parser.add_argument("--json", action="store_true",
                        help="print compact single-line JSON (the default output is indented JSON)")
    parser.add_argument("--plot", action="store_true",
                        help="also plot instantaneous power and phasors (optional, needs matplotlib)")
    parser.add_argument("--out", default=None,
                        help="with --plot: save the figure to this file instead of opening a window")
    return parser


def plot(result: dict, out=None) -> int:
    """Optional matplotlib figure: instantaneous powers over one cycle and the phasor diagram."""
    try:
        import matplotlib
        if out:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; the JSON above is complete. Install it with "
              "'python -m pip install matplotlib' to use --plot.", file=sys.stderr)
        return 0
    wye = result["wye_load"]
    v_line = wye["line_voltage_rms"]["value"]
    i_line = wye["line_current_rms"]["value"]
    phi = wye["power_factor_angle"]["value"]
    f = wye["frequency"]["value"]
    series = instantaneous_power(v_line, i_line, phi, f, n_points=720, include_samples=True)["samples"]
    fig, (ax_p, ax_ph) = plt.subplots(1, 2, figsize=(11, 4.5))
    t_ms = [1000.0 * t for t in series["time"]]
    for key, label in (("p_a", "phase a"), ("p_b", "phase b"), ("p_c", "phase c")):
        ax_p.plot(t_ms, series[key], label=label, linewidth=1.0)
    ax_p.plot(t_ms, series["p_total"], label="three-phase total", linewidth=2.0, color="black")
    ax_p.set_xlabel("time (ms)")
    ax_p.set_ylabel("instantaneous power (W)")
    ax_p.set_title("Each phase pulsates; the total is constant")
    ax_p.grid(True, alpha=0.3)
    ax_p.legend(fontsize=8)
    ax_ph.set_aspect("equal")
    for name, item in wye["phasors"]["line_to_neutral_voltages"].items():
        z = phasor(item["magnitude"]["value"], item["angle"]["value"])
        ax_ph.annotate("", xy=(z.real, z.imag), xytext=(0, 0),
                       arrowprops={"arrowstyle": "->", "color": "tab:blue"})
        ax_ph.text(z.real * 1.08, z.imag * 1.08, f"V{name}n", color="tab:blue", fontsize=8)
    scale = wye["phase_voltage_rms"]["value"] / i_line
    for name, item in wye["phasors"]["line_currents"].items():
        z = phasor(item["magnitude"]["value"] * scale, item["angle"]["value"])
        ax_ph.annotate("", xy=(z.real, z.imag), xytext=(0, 0),
                       arrowprops={"arrowstyle": "->", "color": "tab:red"})
        ax_ph.text(z.real * 1.08, z.imag * 1.08, f"I{name}", color="tab:red", fontsize=8)
    limit = 1.3 * wye["phase_voltage_rms"]["value"]
    ax_ph.set_xlim(-limit, limit)
    ax_ph.set_ylim(-limit, limit)
    ax_ph.set_title(f"Phasors (currents scaled, lag {phi:.1f} deg)")
    ax_ph.set_xlabel("real (V)")
    ax_ph.set_ylabel("imaginary (V)")
    ax_ph.grid(True, alpha=0.3)
    fig.tight_layout()
    if out:
        try:
            fig.savefig(out, dpi=120)
        except OSError as exc:
            print(f"error: cannot write {out}: {exc}", file=sys.stderr)
            return 2
        print(f"plot written to {out}", file=sys.stderr)
    else:
        plt.show()
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = analyse(
            v_line_rms=args.v_line, resistance=args.resistance, reactance=args.reactance,
            frequency=args.frequency, pf_target=args.pf_target, s_base=args.s_base,
            v_base=args.v_base, n_points=args.points,
        )
        if args.json:
            text = json.dumps(result, separators=(",", ":"), allow_nan=False)
        else:
            text = json.dumps(result, indent=2, allow_nan=False)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(text)
    if args.plot:
        return plot(result, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
