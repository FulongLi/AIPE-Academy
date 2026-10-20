"""Time-domain switching simulation of an ideal buck converter.

Purpose
-------
Teaching lab for the AIPE Academy lesson "Buck converter fundamentals: from
switch states to ripple and conduction modes". The script integrates the two
state equations of a buck converter one switching interval at a time, with an
ideal switch and an ideal diode that blocks reverse current, so that the
inductor current ripple, the output voltage ripple, the start-up transient and
the change from continuous (CCM) to discontinuous conduction (DCM) all emerge
from the circuit laws instead of being assumed. The analytical steady-state
formulas of labs/buck_open.py are evaluated alongside the simulation and the
relative differences are reported. Standard library only; matplotlib is used
only behind the optional --plot flag.

Inputs (SI units)
-----------------
v_in             input voltage Vg                                            V
v_out_target     wanted output voltage; sets the duty ratio D = v_out_target/v_in
                 (default 12 V unless duty is given)                         V
duty             alternative to v_out_target: duty ratio D, 0 < D < 1        1
power            load power at the target voltage; sets R = v_out_target^2/power
                 (default 30 W unless load_resistance is given)              W
load_resistance  alternative to power: load resistance R                     Ohm
frequency        switching frequency fs                                      Hz
inductance       filter inductance L                                         H
capacitance      output capacitance C                                        F
cycles           maximum number of switching periods to simulate             1
steps_per_cycle  integration steps per switching period (nominal step Ts/N)  1
tolerance        settling criterion on successive cycle averages             1

The default values are the synthetic AIPE design point used by labs/buck_open.py:
24 V -> 12 V, 30 W (R = 4.8 Ohm), 100 kHz, 150 uH, 100 uF.

Model assumptions
-----------------
* ideal switch: zero on-resistance, instant transitions, constant duty ratio
  (open loop, no feedback, no soft start);
* ideal diode: zero forward drop and no reverse current, so the inductor
  current can fall to zero and stay there (this is what creates DCM);
* lossless inductor and capacitor with no ESR or ESL, a purely resistive
  load and a constant input voltage;
* the simulation starts from zero inductor current and zero output voltage
  (a cold start), so the start-up transient is part of the run.

Numerical method
----------------
Fixed-step, explicit, first-order semi-implicit (symplectic) Euler. In every
step the inductor current is advanced with the capacitor voltage at the start
of the step, then the capacitor voltage is advanced with the inductor current
at the end of the step. The nominal step is Ts/steps_per_cycle; the on and off
intervals are divided into round(D*N) and N - round(D*N) equal steps so the
switching instants fall exactly on step boundaries. When the inductor current
would cross zero inside an off-state step, the crossing time is located by
linear interpolation and the capacitor receives exactly the triangular charge
delivered up to that instant. In periodic steady state the discrete scheme
satisfies inductor volt-second balance and capacitor charge balance exactly,
so the period means are exact; the remaining numerical error is in the
transient (damping and resonant frequency, first order in the step), in
extrema sampled between steps, and in a first-order error of about h/(R C) in
the output voltage ripple (1e-4 at 200 steps per period at the design point).
Use step counts for which D*N is even, so that the switching instants and
both ripple extrema fall on step boundaries: 50 steps at D = 0.5 is less
accurate than 20. Compare --steps-per-cycle 200 with 2000 to measure it.

Stability: the explicit scheme is stable only while the step is below
min(2 sqrt(L C), 2 R C). simulate() refuses a step above STABILITY_MARGIN
(0.5) times that limit with a ValueError that names a step count that works,
and raises ValueError if the state ever becomes non-finite or exceeds
DIVERGENCE_FACTOR (10) times the input voltage, instead of writing NaN or
infinity. The design point's 50 ns step is about 1/5000 of the limit.

Settling: the time averages of the output voltage and inductor current are
computed for every switching period. When both change by less than
`tolerance` (relative to v_in and to v_in/R) for five successive periods, the
run stops and the last period is reported as the periodic steady state. If
`cycles` periods pass first, the result carries settled = false and a warning.
The default tolerance of 1e-8 leaves a residual start-up drift of about 2e-5
of the output voltage ripple (tolerance 1e-9 brings it below 1e-5 at the cost
of about 200 more periods); a looser 1e-6 stops about 460 periods earlier at
the design point but biases the reported ripple by roughly 0.2 %, which is
the largest numerical error in this lab and is worth measuring yourself. When
only one period is simulated no change can be computed and the two
last_cycle_change values are reported as null.

Outputs (dict, printed as JSON)
-------------------------------
inputs, numerical_method, settling, steady_state (mean output voltage, mean
inductor current, inductor current min/max and peak-to-peak ripple, output
voltage min/max and ripple, conduction mode CCM/DCM, zero-current fraction,
mean input current, input and output power), startup (peak values during the
transient), analytical_ccm (the labs/buck_open.py formulas plus the capacitor
ripple), conduction_boundary (K = 2 L fs / R against K_crit = 1 - D),
analytical_dcm (when the boundary predicts DCM) and comparison (relative
differences between the simulation and the applicable analytical model).
Physical quantities are {"value": <float>, "unit": "<SI symbol>"}.

Validation checks
-----------------
Every input must be a finite real number; voltages, powers, resistances,
frequency, inductance, capacitance and tolerance must be positive; the duty
ratio must lie strictly between 0 and 1; v_out_target must be below v_in;
cycles must be a positive integer and steps_per_cycle an integer of at least
4; v_out_target and duty are mutually exclusive, as are power and
load_resistance; the integration step must be within the stability limit
described above and the state must stay finite and bounded during the run.
Violations raise ValueError with a specific message; the CLI prints
"error: <message>" to stderr and exits with code 2 (JSON serialisation runs
inside the same guard). No NaN or infinity is ever written (json.dumps uses
allow_nan=False).

Limits of the model
-------------------
No conduction or switching losses, so efficiency is exactly 1; no diode
forward drop or switch resistance, so the real output is slightly lower than
D*Vg; no capacitor ESR, so the real output ripple is larger and partly
resistive; no parasitic capacitance, so the switch node does not ring in DCM;
no feedback, so the output follows the input voltage and, in DCM, the load;
cold start without soft start, so the start-up overshoot is that of the
lightly damped LC filter. If the inductor current is negative at a switch-off
instant (possible only during start-up at high duty ratios, when the output
briefly exceeds the input), it is clamped to zero and a warning is recorded.
Nothing here is a measurement: it is an analytical and numerical teaching
model, not validated hardware performance.

How to reproduce
----------------
    python labs/power-electronics/buck_switching.py
    python labs/power-electronics/buck_switching.py --frequency 200000
    python labs/power-electronics/buck_switching.py --v-in 20 --duty 0.5 --load 4.8
    python labs/power-electronics/buck_switching.py --load 120
    python labs/power-electronics/buck_switching.py --steps-per-cycle 2000
    python labs/power-electronics/buck_switching.py --tolerance 1e-6
    python labs/power-electronics/buck_switching.py --plot --out buck.png
    python -m unittest tests.test_lab_buck_switching

Negative values written with an exponent, such as -1e-6 or -inf, must be
attached with "=" (--capacitance=-1e-6, which the validation then rejects as
not positive), because argparse reads a bare -1e-6 as an option name; plain
negatives such as --v-in -24 reach the validation directly.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

DESIGN_POINT = {
    "v_in": 24.0,
    "v_out_target": 12.0,
    "power": 30.0,
    "frequency": 100000.0,
    "inductance": 0.00015,
    "capacitance": 0.0001,
}
DEFAULT_CYCLES = 20000
DEFAULT_STEPS_PER_CYCLE = 200
DEFAULT_TOLERANCE = 1e-8
SETTLE_CYCLES = 5
MIN_STEPS_PER_CYCLE = 4
STABILITY_MARGIN = 0.5  # largest allowed integration step as a fraction of min(2 sqrt(LC), 2RC)
DIVERGENCE_FACTOR = 10.0  # |v| above this multiple of v_in means the integration has diverged

MODEL = "ideal-buck-switching-simulation"
ASSUMPTIONS = [
    "ideal switch with instant transitions and constant open-loop duty ratio",
    "ideal diode with zero forward drop that blocks reverse current",
    "lossless inductor and capacitor without ESR or ESL",
    "resistive load and constant input voltage",
    "cold start from zero inductor current and zero output voltage",
    "fixed-step first-order explicit integration (semi-implicit Euler)",
]
LIMITATIONS = [
    "no conduction or switching losses, so efficiency is exactly 1",
    "no diode drop or switch resistance, so a real output sits below D*Vg",
    "no capacitor ESR, so a real output ripple is larger and partly resistive",
    "no parasitic capacitance, so the switch node does not ring in DCM",
    "no feedback or soft start: line, load and start-up behaviour are open loop",
    "numerical teaching model, not validated hardware performance",
]

EXAMPLES = """examples:
  python labs/power-electronics/buck_switching.py
  python labs/power-electronics/buck_switching.py --frequency 200000
  python labs/power-electronics/buck_switching.py --v-in 20 --duty 0.5 --load 4.8
  python labs/power-electronics/buck_switching.py --load 120
  python labs/power-electronics/buck_switching.py --steps-per-cycle 2000 --json
  python labs/power-electronics/buck_switching.py --tolerance 1e-6
  python labs/power-electronics/buck_switching.py --plot --out buck.png
note: attach negative exponent-form values with "=", e.g. --capacitance=-1e-6,
      because argparse reads a bare -1e-6 as an option name
"""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def _real(name: str, value) -> float:
    """Return value as a finite float or raise ValueError naming the input."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a real number, got {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return float(value)


def _positive(name: str, value) -> float:
    number = _real(name, value)
    if number <= 0.0:
        raise ValueError(f"{name} must be positive, got {value!r}")
    return number


def _integer(name: str, value, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, got {value!r}")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value}")
    return value


def _duty(name: str, value) -> float:
    number = _real(name, value)
    if not 0.0 < number < 1.0:
        raise ValueError(f"{name} must lie strictly between 0 and 1, got {value!r}")
    return number


def quantity(value: float, unit: str) -> dict:
    """Wrap a physical quantity as {"value": float, "unit": SI symbol}."""
    return {"value": float(value), "unit": unit}


def _optional_quantity(value, unit: str) -> dict:
    """Like quantity(), but a value that could not be computed (None) is reported as null, not as 0.0."""
    return {"value": None if value is None else float(value), "unit": unit}


def _relative(simulated: float, reference: float, scale: float = 1.0) -> float:
    """Relative difference (simulated - reference) / reference.

    When the reference is exactly zero (the analytical minimum inductor current
    at the CCM/DCM boundary) the difference is normalised by `scale` instead,
    which callers set to the mean value of the same quantity.
    """
    denominator = reference if reference != 0.0 else scale
    return (simulated - reference) / denominator


def _continuous(k: float, k_critical: float) -> bool:
    """True when K >= K_crit within a relative rounding margin, so an exact boundary counts as CCM."""
    return k >= k_critical * (1.0 - 1e-9)


# ---------------------------------------------------------------------------
# Operating point and analytical models
# ---------------------------------------------------------------------------
def resolve_operating_point(v_in=DESIGN_POINT["v_in"], v_out_target=None, duty=None,
                            power=None, load_resistance=None):
    """Turn either (v_out_target, power) or (duty, load_resistance) into the simulation inputs.

    Returns (v_in [V], duty [1], v_out_target [V], load_resistance [Ohm]). The target
    voltage is the ideal CCM prediction D*Vg; the simulation shows what the output
    actually does. Missing values fall back to the design point (12 V, 30 W).
    """
    v_in = _positive("v_in", v_in)
    if duty is not None and v_out_target is not None:
        raise ValueError("Specify either v_out_target or duty, not both")
    if duty is None:
        if v_out_target is None:
            v_out_target = DESIGN_POINT["v_out_target"]
        v_out_target = _positive("v_out_target", v_out_target)
        if v_out_target >= v_in:
            raise ValueError(
                f"v_out_target ({v_out_target} V) must be below v_in ({v_in} V): a buck converter only steps down")
        duty = v_out_target / v_in
    else:
        duty = _duty("duty", duty)
        v_out_target = duty * v_in
    if power is not None and load_resistance is not None:
        raise ValueError("Specify either power or load_resistance, not both")
    if load_resistance is None:
        if power is None:
            power = DESIGN_POINT["power"]
        power = _positive("power", power)
        load_resistance = v_out_target * v_out_target / power
    else:
        load_resistance = _positive("load_resistance", load_resistance)
    return v_in, duty, v_out_target, load_resistance


def ccm_steady_state(v_in: float, duty: float, load_resistance: float, frequency: float,
                     inductance: float, capacitance: float) -> dict:
    """Ideal CCM steady state: the formulas of labs/buck_open.py plus the capacitor ripple.

    Units: v_in V, duty 1, load_resistance Ohm, frequency Hz, inductance H, capacitance F.
    V = D*Vg; I_L = V/R; delta_i = (Vg - V) D / (L fs); delta_v = delta_i / (8 C fs).
    """
    v_in = _positive("v_in", v_in)
    duty = _duty("duty", duty)
    load_resistance = _positive("load_resistance", load_resistance)
    frequency = _positive("frequency", frequency)
    inductance = _positive("inductance", inductance)
    capacitance = _positive("capacitance", capacitance)
    v_out = duty * v_in
    current = v_out / load_resistance
    ripple = (v_in - v_out) * duty / (inductance * frequency)
    return {
        "model": "ideal-ccm-buck",
        "validation_status": "analytical-example",
        "duty_ratio": quantity(duty, "1"),
        "output_voltage": quantity(v_out, "V"),
        "inductor_current_mean": quantity(current, "A"),
        "inductor_ripple_pp": quantity(ripple, "A"),
        "inductor_current_min": quantity(current - ripple / 2.0, "A"),
        "inductor_current_max": quantity(current + ripple / 2.0, "A"),
        "output_voltage_ripple_pp": quantity(ripple / (8.0 * capacitance * frequency), "V"),
        "load_resistance": quantity(load_resistance, "Ohm"),
    }


def ccm_boundary(v_in: float, duty: float, load_resistance: float, frequency: float,
                 inductance: float) -> dict:
    """Where continuous conduction ends.

    K = 2 L fs / R is compared with K_crit = 1 - D. CCM holds when the average
    output current D*Vg/R is at least half the peak-to-peak ripple, which is
    the same statement as K >= K_crit. The boundary load resistance is
    R_crit = 2 L fs / (1 - D). Units: V, 1, Ohm, Hz, H.
    """
    v_in = _positive("v_in", v_in)
    duty = _duty("duty", duty)
    load_resistance = _positive("load_resistance", load_resistance)
    frequency = _positive("frequency", frequency)
    inductance = _positive("inductance", inductance)
    k = 2.0 * inductance * frequency / load_resistance
    k_critical = 1.0 - duty
    v_out = duty * v_in
    ripple = (v_in - v_out) * duty / (inductance * frequency)
    r_critical = 2.0 * inductance * frequency / (1.0 - duty)
    return {
        "k": quantity(k, "1"),
        "k_critical": quantity(k_critical, "1"),
        "predicted_mode": "CCM" if _continuous(k, k_critical) else "DCM",
        "output_current_ccm": quantity(v_out / load_resistance, "A"),
        "boundary_output_current": quantity(ripple / 2.0, "A"),
        "boundary_load_resistance": quantity(r_critical, "Ohm"),
        "boundary_power": quantity(v_out * v_out / r_critical, "W"),
    }


def dcm_conversion_ratio(duty: float, k: float) -> float:
    """DCM conversion ratio M = V/Vg = 2 / (1 + sqrt(1 + 4K/D^2)) of the ideal buck.

    duty is D (1), k is K = 2 L fs / R (1). The formula applies for K < 1 - D;
    at K = 1 - D it returns D, so it joins the CCM ratio continuously.
    """
    duty = _duty("duty", duty)
    k = _positive("k", k)
    return 2.0 / (1.0 + math.sqrt(1.0 + 4.0 * k / (duty * duty)))


def dcm_steady_state(v_in: float, duty: float, load_resistance: float, frequency: float,
                     inductance: float) -> dict:
    """Ideal DCM steady state for K < 1 - D (raises ValueError otherwise).

    Units: V, 1, Ohm, Hz, H. The output is M*Vg, the inductor current is a
    triangle of peak (Vg - V) D / (L fs) that returns to zero after a diode
    interval D2 = D (Vg - V) / V, then stays at zero for 1 - D - D2 of the period.
    """
    v_in = _positive("v_in", v_in)
    duty = _duty("duty", duty)
    load_resistance = _positive("load_resistance", load_resistance)
    frequency = _positive("frequency", frequency)
    inductance = _positive("inductance", inductance)
    k = 2.0 * inductance * frequency / load_resistance
    if _continuous(k, 1.0 - duty):
        raise ValueError(
            f"K = {k:.4g} is not below 1 - D = {1.0 - duty:.4g}: the converter is in CCM and the DCM formulas do not apply")
    ratio = dcm_conversion_ratio(duty, k)
    v_out = ratio * v_in
    peak = (v_in - v_out) * duty / (inductance * frequency)
    d2 = duty * (v_in - v_out) / v_out
    return {
        "model": "ideal-dcm-buck",
        "validation_status": "analytical-example",
        "k": quantity(k, "1"),
        "conversion_ratio": quantity(ratio, "1"),
        "output_voltage": quantity(v_out, "V"),
        "inductor_current_mean": quantity(v_out / load_resistance, "A"),
        "inductor_current_max": quantity(peak, "A"),
        "diode_duty_ratio": quantity(d2, "1"),
        "zero_current_fraction": quantity(1.0 - duty - d2, "1"),
    }


# ---------------------------------------------------------------------------
# Switching simulation
# ---------------------------------------------------------------------------
def simulate(v_in=DESIGN_POINT["v_in"], v_out_target=None, duty=None, power=None, load_resistance=None,
             frequency=DESIGN_POINT["frequency"], inductance=DESIGN_POINT["inductance"],
             capacitance=DESIGN_POINT["capacitance"], cycles=DEFAULT_CYCLES,
             steps_per_cycle=DEFAULT_STEPS_PER_CYCLE, tolerance=DEFAULT_TOLERANCE,
             waveform=False) -> dict:
    """Simulate the ideal buck converter switch by switch and compare with analysis.

    Give either v_out_target (V) or duty (1), and either power (W) or
    load_resistance (Ohm); frequency in Hz, inductance in H, capacitance in F.
    cycles is the maximum number of switching periods, steps_per_cycle the
    number of integration steps per period and tolerance the settling
    criterion (see the module docstring). With waveform=True the result also
    carries the samples of the last period and the per-period averages.
    Returns a dict of quantities {"value", "unit"}; raises ValueError for
    invalid input, for a step above the stability limit of the explicit scheme
    and if the state diverges during the run.
    """
    v_in, duty, v_target, resistance = resolve_operating_point(v_in, v_out_target, duty, power, load_resistance)
    frequency = _positive("frequency", frequency)
    inductance = _positive("inductance", inductance)
    capacitance = _positive("capacitance", capacitance)
    cycles = _integer("cycles", cycles, 1)
    steps = _integer("steps_per_cycle", steps_per_cycle, MIN_STEPS_PER_CYCLE)
    tolerance = _positive("tolerance", tolerance)

    period = 1.0 / frequency
    n_on = min(steps - 1, max(1, round(duty * steps)))
    n_off = steps - n_on
    h_on = duty * period / n_on
    h_off = (1.0 - duty) * period / n_off
    current_scale = v_in / resistance
    h_max = max(h_on, h_off)
    h_limit = min(2.0 * math.sqrt(inductance * capacitance), 2.0 * resistance * capacitance)
    if h_max > STABILITY_MARGIN * h_limit:
        needed = 2 * math.ceil(0.55 * steps * h_max / (STABILITY_MARGIN * h_limit))
        raise ValueError(
            f"steps_per_cycle = {steps} gives an integration step of {h_max:.3g} s, above {STABILITY_MARGIN:g} x the "
            f"stability limit {h_limit:.3g} s of the explicit scheme (min(2 sqrt(LC), 2 R C) for L = {inductance:g} H, "
            f"C = {capacitance:g} F, R = {resistance:.4g} Ohm); use --steps-per-cycle >= {needed} or change L, C, R or fs")
    warnings: list[str] = []

    i = 0.0  # inductor current, A
    v = 0.0  # output (capacitor) voltage, V
    prev_v_mean = prev_i_mean = None
    change_v = change_i = None
    quiet = 0
    settled = False
    cycles_run = 0
    peak_v = 0.0
    peak_i = 0.0
    clamps = 0
    mean_v_history: list[float] = []
    mean_i_history: list[float] = []
    t_list: list[float] = []
    i_list: list[float] = []
    v_list: list[float] = []

    for cycle in range(cycles):
        sum_v = sum_i = sum_in = sum_p = 0.0
        zero_time = 0.0
        i_min = i_max = i
        v_min = v_max = v
        if waveform:
            t = 0.0
            t_list = [0.0]
            i_list = [i]
            v_list = [v]
        # Switch on: the inductor sees Vg - v and its current rises.
        for _ in range(n_on):
            i_new = i + h_on * (v_in - v) / inductance
            sum_in += 0.5 * (i + i_new) * h_on
            v += h_on * (i_new - v / resistance) / capacitance
            i = i_new
            sum_v += v * h_on
            sum_i += i * h_on
            sum_p += v * v / resistance * h_on
            if i < i_min:
                i_min = i
            elif i > i_max:
                i_max = i
            if v < v_min:
                v_min = v
            elif v > v_max:
                v_max = v
            if waveform:
                t += h_on
                t_list.append(t)
                i_list.append(i)
                v_list.append(v)
        # Switch off: the diode carries the current while it is positive.
        if i < 0.0:
            clamps += 1
            i = 0.0
        for _ in range(n_off):
            if i > 0.0:
                di = -h_off * v / inductance
                if i + di > 0.0:
                    i_new = i + di
                    v += h_off * (i_new - v / resistance) / capacitance
                    i = i_new
                else:
                    # The current reaches zero inside this step; the diode then blocks.
                    conduction = h_off * (i / -di)
                    zero_time += h_off - conduction
                    charge = 0.5 * i * conduction
                    v += (charge - h_off * v / resistance) / capacitance
                    i = 0.0
            else:
                zero_time += h_off
                v -= h_off * v / (resistance * capacitance)
            sum_v += v * h_off
            sum_i += i * h_off
            sum_p += v * v / resistance * h_off
            if i < i_min:
                i_min = i
            elif i > i_max:
                i_max = i
            if v < v_min:
                v_min = v
            elif v > v_max:
                v_max = v
            if waveform:
                t += h_off
                t_list.append(t)
                i_list.append(i)
                v_list.append(v)
        cycles_run = cycle + 1
        v_mean = sum_v / period
        i_mean = sum_i / period
        v_extreme = max(abs(v_min), abs(v_max))
        if not (math.isfinite(v_mean) and math.isfinite(i_mean)) or v_extreme > DIVERGENCE_FACTOR * v_in:
            raise ValueError(
                f"the simulation diverged in period {cycles_run} (|v| reached {v_extreme:.3g} V, |i| reached "
                f"{max(abs(i_min), abs(i_max)):.3g} A): the explicit scheme is unstable for these parameters; "
                "increase --steps-per-cycle")
        mean_v_history.append(v_mean)
        mean_i_history.append(i_mean)
        if v_max > peak_v:
            peak_v = v_max
        if i_max > peak_i:
            peak_i = i_max
        if prev_v_mean is not None:
            change_v = abs(v_mean - prev_v_mean) / v_in
            change_i = abs(i_mean - prev_i_mean) / current_scale
            quiet = quiet + 1 if (change_v < tolerance and change_i < tolerance) else 0
        prev_v_mean, prev_i_mean = v_mean, i_mean
        if quiet >= SETTLE_CYCLES:
            settled = True
            break

    if not settled:
        time_constant = 2.0 * resistance * capacitance  # decay time of the start-up envelope, 1 / (zeta omega_0)
        warnings.append(
            f"cycle averages had not settled to tolerance {tolerance:g} after {cycles_run} periods "
            f"({cycles_run * period:.3g} s simulated); in continuous conduction the start-up envelope decays with time "
            f"constant 2RC = {time_constant:.3g} s, so about {math.ceil(20.0 * time_constant / period)} periods (20 time "
            "constants) should suffice, fewer in discontinuous conduction; increase --cycles or loosen --tolerance")
    if clamps:
        warnings.append(
            f"inductor current was negative at {clamps} switch-off instant(s) during start-up and was clamped to zero; "
            "the ideal switch and diode cannot carry it (output briefly above input)")

    ripple_i = i_max - i_min
    ripple_v = v_max - v_min
    mode = "DCM" if zero_time > 0.0 else "CCM"
    zero_fraction = zero_time / period
    diode_fraction = (1.0 - duty) - zero_fraction
    input_current = sum_in / period
    p_in = v_in * input_current
    p_out = sum_p / period

    analytical = ccm_steady_state(v_in, duty, resistance, frequency, inductance, capacitance)
    boundary = ccm_boundary(v_in, duty, resistance, frequency, inductance)
    dcm = dcm_steady_state(v_in, duty, resistance, frequency, inductance) if boundary["predicted_mode"] == "DCM" else None

    if dcm is None:
        reference_model = "analytical-ccm"
        current_mean = analytical["inductor_current_mean"]["value"]
        differences = {
            "output_voltage": _relative(v_mean, analytical["output_voltage"]["value"]),
            "inductor_current_mean": _relative(i_mean, current_mean),
            "inductor_ripple_pp": _relative(ripple_i, analytical["inductor_ripple_pp"]["value"]),
            "inductor_current_min": _relative(i_min, analytical["inductor_current_min"]["value"], current_mean),
            "inductor_current_max": _relative(i_max, analytical["inductor_current_max"]["value"], current_mean),
            "output_voltage_ripple_pp": _relative(ripple_v, analytical["output_voltage_ripple_pp"]["value"]),
        }
    else:
        reference_model = "analytical-dcm"
        differences = {
            "output_voltage": _relative(v_mean, dcm["output_voltage"]["value"]),
            "inductor_current_mean": _relative(i_mean, dcm["inductor_current_mean"]["value"]),
            "inductor_current_max": _relative(i_max, dcm["inductor_current_max"]["value"]),
            "diode_conduction_fraction": _relative(diode_fraction, dcm["diode_duty_ratio"]["value"]),
        }

    result = {
        "model": MODEL,
        "validation_status": "numerical-simulation",
        "assumptions": list(ASSUMPTIONS),
        "limitations": list(LIMITATIONS),
        "inputs": {
            "input_voltage": quantity(v_in, "V"),
            "duty_ratio": quantity(duty, "1"),
            "target_output_voltage": quantity(v_target, "V"),
            "load_resistance": quantity(resistance, "Ohm"),
            "switching_frequency": quantity(frequency, "Hz"),
            "inductance": quantity(inductance, "H"),
            "capacitance": quantity(capacitance, "F"),
            "cycles_max": cycles,
            "steps_per_cycle": steps,
            "tolerance": quantity(tolerance, "1"),
        },
        "numerical_method": {
            "scheme": "semi-implicit Euler, explicit, first order, fixed step",
            "switching_period": quantity(period, "s"),
            "nominal_step": quantity(period / steps, "s"),
            "step_on": quantity(h_on, "s"),
            "step_off": quantity(h_off, "s"),
            "steps_on": n_on,
            "steps_off": n_off,
            "diode_turn_off": "zero crossing located inside the step by linear interpolation",
        },
        "settling": {
            "settled": settled,
            "cycles_simulated": cycles_run,
            "simulated_time": quantity(cycles_run * period, "s"),
            "consecutive_quiet_cycles_required": SETTLE_CYCLES,
            "last_cycle_change_output_voltage": _optional_quantity(change_v, "1"),
            "last_cycle_change_inductor_current": _optional_quantity(change_i, "1"),
        },
        "steady_state": {
            "conduction_mode": mode,
            "output_voltage_mean": quantity(v_mean, "V"),
            "output_voltage_min": quantity(v_min, "V"),
            "output_voltage_max": quantity(v_max, "V"),
            "output_voltage_ripple_pp": quantity(ripple_v, "V"),
            "inductor_current_mean": quantity(i_mean, "A"),
            "inductor_current_min": quantity(i_min, "A"),
            "inductor_current_max": quantity(i_max, "A"),
            "inductor_ripple_pp": quantity(ripple_i, "A"),
            "diode_conduction_fraction": quantity(diode_fraction, "1"),
            "zero_current_fraction": quantity(zero_fraction, "1"),
            "input_current_mean": quantity(input_current, "A"),
            "input_power": quantity(p_in, "W"),
            "output_power": quantity(p_out, "W"),
            "power_balance_error": quantity(_relative(p_in, p_out), "1"),
        },
        "startup": {
            "peak_output_voltage": quantity(peak_v, "V"),
            "peak_inductor_current": quantity(peak_i, "A"),
            "overshoot_ratio": quantity(peak_v / v_mean if v_mean > 0.0 else 0.0, "1"),
        },
        "analytical_ccm": analytical,
        "conduction_boundary": boundary,
        "analytical_dcm": dcm,
        "comparison": {
            "reference_model": reference_model,
            "mode_agrees": boundary["predicted_mode"] == mode,
            "relative_difference": {name: quantity(value, "1") for name, value in differences.items()},
        },
        "warnings": warnings,
    }
    if waveform:
        result["waveform"] = {
            "description": "samples of the last simulated period (time from the start of the period) and per-period averages",
            "time": {"values": t_list, "unit": "s"},
            "inductor_current": {"values": i_list, "unit": "A"},
            "output_voltage": {"values": v_list, "unit": "V"},
            "cycle_mean_output_voltage": {"values": mean_v_history, "unit": "V"},
            "cycle_mean_inductor_current": {"values": mean_i_history, "unit": "A"},
        }
    return result


# ---------------------------------------------------------------------------
# Optional plot and command line
# ---------------------------------------------------------------------------
def plot(result: dict, out: str | None = None) -> int:
    """Draw the last period and the start-up with matplotlib; exit 0 with a message if it is missing."""
    try:
        import matplotlib
        if out:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed, so no figure was drawn; the JSON above is complete. "
              "Install it with 'python -m pip install matplotlib' to use --plot.", file=sys.stderr)
        return 0
    wave = result["waveform"]
    t_us = [1e6 * t for t in wave["time"]["values"]]
    steady = result["steady_state"]
    analytical = result["analytical_dcm"] or result["analytical_ccm"]
    fig, axes = plt.subplots(3, 1, figsize=(8, 9), constrained_layout=True)
    axes[0].plot(t_us, wave["inductor_current"]["values"], color="#2a78d6", linewidth=1.5)
    axes[0].set_ylabel("inductor current (A)")
    axes[0].set_title(f"last period: {steady['conduction_mode']}, mean {steady['inductor_current_mean']['value']:.3f} A")
    axes[1].plot(t_us, wave["output_voltage"]["values"], color="#1baf7a", linewidth=1.5)
    axes[1].set_ylabel("output voltage (V)")
    axes[1].set_title(
        f"last period: mean {steady['output_voltage_mean']['value']:.4f} V, "
        f"ripple {1e3 * steady['output_voltage_ripple_pp']['value']:.2f} mV")
    axes[1].set_xlabel("time within the period (µs)")
    axes[1].ticklabel_format(axis="y", useOffset=False, style="plain")
    means = wave["cycle_mean_output_voltage"]["values"]
    axes[2].plot(range(1, len(means) + 1), means, color="#2a78d6", linewidth=1.5)
    axes[2].axhline(analytical["output_voltage"]["value"], color="#52514e", linewidth=1.0, linestyle="--")
    axes[2].annotate(f"analytical {analytical['output_voltage']['value']:.3f} V",
                     xy=(len(means), analytical["output_voltage"]["value"]),
                     xytext=(-6, 6), textcoords="offset points", ha="right", color="#52514e", fontsize=9)
    axes[2].set_ylabel("period-average output (V)")
    axes[2].set_xlabel("switching period")
    axes[2].set_title("start-up from zero: period averages until settling")
    for axis in axes:
        axis.grid(True, color="#dddcd7", linewidth=0.6)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    if out:
        fig.savefig(out, dpi=150)
        print(f"figure saved to {out}", file=sys.stderr)
    else:
        plt.show()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Command-line parser; all options take SI units (V, W, Ohm, Hz, H, F) except the dimensionless duty ratio and counts."""
    parser = argparse.ArgumentParser(
        description="Time-domain switching simulation of an ideal buck converter (AIPE Academy teaching lab). "
                    "Defaults reproduce the lesson's design point: 24 V -> 12 V, 30 W, 100 kHz, 150 uH, 100 uF.",
        epilog=EXAMPLES, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--v-in", type=float, default=DESIGN_POINT["v_in"], help="input voltage in V (default 24)")
    parser.add_argument("--v-out", type=float, default=None,
                        help="target output voltage in V, sets the duty ratio D = V_out/V_in (default 12 unless --duty is given)")
    parser.add_argument("--duty", type=float, default=None, help="duty ratio, 0 < D < 1 (alternative to --v-out)")
    parser.add_argument("--power", type=float, default=None,
                        help="load power in W at the target voltage (default 30 unless --load is given)")
    parser.add_argument("--load", type=float, default=None, help="load resistance in Ohm (alternative to --power)")
    parser.add_argument("--frequency", type=float, default=DESIGN_POINT["frequency"],
                        help="switching frequency in Hz (default 100000)")
    parser.add_argument("--inductance", type=float, default=DESIGN_POINT["inductance"],
                        help="inductance in H (default 0.00015)")
    parser.add_argument("--capacitance", type=float, default=DESIGN_POINT["capacitance"],
                        help="output capacitance in F (default 0.0001)")
    parser.add_argument("--cycles", type=int, default=DEFAULT_CYCLES,
                        help=f"maximum switching periods; the run stops early once settled (default {DEFAULT_CYCLES})")
    parser.add_argument("--steps-per-cycle", type=int, default=DEFAULT_STEPS_PER_CYCLE,
                        help=f"integration steps per period (default {DEFAULT_STEPS_PER_CYCLE})")
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                        help=f"settling tolerance on successive period averages (default {DEFAULT_TOLERANCE:g})")
    parser.add_argument("--json", action="store_true", help="print compact single-line JSON instead of indented JSON")
    parser.add_argument("--plot", action="store_true",
                        help="draw the last period and the start-up with matplotlib, if installed")
    parser.add_argument("--out", default=None, help="with --plot: save the figure to this file instead of opening a window")
    return parser


def main(argv=None) -> int:
    """Run the simulation from the command line: JSON on stdout and exit 0, or "error: ..." on stderr and exit 2."""
    args = build_parser().parse_args(argv)
    try:
        result = simulate(v_in=args.v_in, v_out_target=args.v_out, duty=args.duty, power=args.power,
                          load_resistance=args.load, frequency=args.frequency, inductance=args.inductance,
                          capacitance=args.capacitance, cycles=args.cycles, steps_per_cycle=args.steps_per_cycle,
                          tolerance=args.tolerance, waveform=args.plot)
        waveform = result.pop("waveform", None)
        if args.json:
            text = json.dumps(result, separators=(",", ":"), allow_nan=False)
        else:
            text = json.dumps(result, indent=2, allow_nan=False)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(text)
    if args.plot:
        result["waveform"] = waveform
        return plot(result, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
