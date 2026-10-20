"""DC circuit fundamentals: Ohm's law, power and energy, series and parallel
networks, the loaded voltage divider, a small nodal solver and conservation
checks.

Companion lab for the AIPE Academy lesson
curriculum/foundations/circuits/dc-circuit-fundamentals.md.  Python 3.10+
standard library only (math, json, argparse, numbers, sys); matplotlib is
imported lazily and only when --plot is requested.

Purpose
-------
Give a beginner a reproducible way to check hand calculations on ideal DC
resistive circuits, and to explore what changes when one parameter changes.

Inputs (SI units unless the parameter name says otherwise)
----------------------------------------------------------
v, v_in          voltage in volts (V); signed, finite
i                current in amperes (A); signed, finite
r, r_top, ...    resistance in ohms (written "Ohm"); finite and not negative;
                 zero is accepted only where no voltage is applied across it
hours            duration in hours (h): a convenience unit for energy, converted
                 to seconds internally (1 h = 3600 s)
branches         list of dicts {"type": "R" | "V" | "I", "nodes": [a, b],
                 "value": x, "name": optional} describing a network; see
                 solve_network() for the sign conventions
branch_currents  signed currents in A at one node, positive when leaving it
loop_voltages    signed voltages in V around one loop, drops positive

Model assumptions
-----------------
* Lumped, ideal elements: resistors obey V = I R exactly at constant
  temperature; voltage sources hold their voltage at any current; current
  sources drive their current at any voltage; wires have zero resistance.
* DC steady state: nothing varies with time, so there are no capacitors,
  inductors or switching waveforms.
* Passive sign convention for every branch: the branch voltage is
  V(a) - V(b) and the branch current flows from a to b inside the element, so
  power = voltage * current is positive when the element absorbs energy and
  negative when it supplies energy.

Outputs
-------
Every public function returns a dict.  Physical quantities are
{"value": <float>, "unit": "<SI symbol>"}.  Each result carries "model",
"validation_status" ("analytical-example" for closed-form results,
"numerical-simulation" for the Gaussian-elimination nodal solver),
"assumptions" and "limitations".  The CLI prints indented JSON.

Validation checks
-----------------
ValueError with a specific message for: non-numeric, NaN or infinite inputs;
negative resistance; zero resistance where a voltage is applied; a resistance
so small that its conductance 1/R is not a finite float; an under-determined
or inconsistent ohm() call; an empty resistor list; an unknown series/parallel
mode; a non-positive divider or load resistance; a negative duration; a
network with a floating node, a loop of ideal voltage sources, a branch whose
two terminals are the same node, a duplicate branch name or an unknown element
type; a conservation check with no values; and any input, result or
intermediate sum that overflows the floating-point range (reported as a
ValueError naming the inputs, never as a traceback).  No result ever contains
NaN or inf; the CLI serialises with json.dumps(..., allow_nan=False).

Limits of the model
-------------------
All results are analytical or numerical teaching values, not validated
hardware performance.  Real resistors have tolerance, temperature coefficients
and power ratings; real sources have internal resistance and current limits;
real wires have resistance; measured values carry instrument error.  The nodal
solver is written for small networks (at most 50 unknowns), DC only, with
independent sources and resistors; it has no controlled sources, no reactive
elements and no non-linear devices.  Two numerical limits apply to it.  When
resistances in series differ by more than about 1e8 (for example 1 Ohm next to
1e9 Ohm), the current through the small resistor is the difference of two
nearly equal node voltages and loses digits through cancellation: its absolute
error is about 1e-16 * V_max / R_small.  The conservation tolerances include
this rounding floor, so "passes" stays true for a correctly solved network,
but that one current is only accurate to that floor.  And a network that
contains a voltage source together with resistances above about 1e13 Ohm is
rejected as singular, because the pivot test compares conductances in siemens
with the source-constraint entries of 1.

How to reproduce (run from the repository root)
----------------------------------------------
    python labs/foundations/dc_circuits.py                 # default example, JSON
    python labs/foundations/dc_circuits.py --json          # same, explicit flag
    python labs/foundations/dc_circuits.py ohm --v 6 --r 300
    python labs/foundations/dc_circuits.py power --v 6 --i 0.02 --hours 0.5
    python labs/foundations/dc_circuits.py series 10000 10000
    python labs/foundations/dc_circuits.py parallel 10000 10000
    python labs/foundations/dc_circuits.py divider --v-in 12 --r-top 10000 --r-bottom 10000 --r-load 10000
    python labs/foundations/dc_circuits.py network --example two-source
    python labs/foundations/dc_circuits.py network --branch V,in,0,12 --branch R,in,out,10000 --branch R,out,0,10000
    python labs/foundations/dc_circuits.py check --currents -0.0008 0.0004 0.0004 --voltages -12 8 4
    python labs/foundations/dc_circuits.py --plot --out loading.png divider --v-in 12 --r-top 10000 --r-bottom 10000 --r-load 10000

Exit code 0 on success; stdout then carries exactly one JSON document, and any
notice (plot written, matplotlib missing, nothing to plot) goes to stderr.  On
invalid input the CLI prints "error: <message>" to stderr and exits with code
2.  The default run takes well under one second.
"""
from __future__ import annotations

import argparse
import json
import math
import numbers
import sys

__version__ = "0.3.0"

OHM = "Ohm"
MAX_UNKNOWNS = 50

COMMON_ASSUMPTIONS = [
    "lumped ideal elements: resistors obey V = I R exactly at constant temperature",
    "ideal sources: a voltage source holds its voltage at any current, a current source holds its current at any voltage",
    "ideal wires with zero resistance",
    "DC steady state: no time variation, no capacitors or inductors",
    "passive sign convention: branch voltage V(a) - V(b), branch current from a to b, positive power is absorbed",
]

COMMON_LIMITATIONS = [
    "analytical/numerical teaching model, not validated hardware performance",
    "no resistor tolerance, temperature coefficient, power rating or self-heating",
    "no source internal resistance, current limit or wiring resistance",
    "no measurement error model",
]

EXAMPLE_NETWORKS = {
    "single-resistor": [
        {"name": "V1", "type": "V", "nodes": ["a", "0"], "value": 6.0},
        {"name": "R1", "type": "R", "nodes": ["a", "0"], "value": 300.0},
    ],
    "loaded-divider": [
        {"name": "V1", "type": "V", "nodes": ["in", "0"], "value": 12.0},
        {"name": "Rtop", "type": "R", "nodes": ["in", "out"], "value": 10000.0},
        {"name": "Rbottom", "type": "R", "nodes": ["out", "0"], "value": 10000.0},
        {"name": "Rload", "type": "R", "nodes": ["out", "0"], "value": 10000.0},
    ],
    "two-source": [
        {"name": "V1", "type": "V", "nodes": ["n1", "0"], "value": 12.0},
        {"name": "R1", "type": "R", "nodes": ["n1", "n2"], "value": 2000.0},
        {"name": "R2", "type": "R", "nodes": ["n2", "0"], "value": 4000.0},
        {"name": "I1", "type": "I", "nodes": ["0", "n2"], "value": 0.0015},
    ],
}

_ELEMENT_TYPES = {
    "r": "R", "res": "R", "resistor": "R", "resistance": "R",
    "v": "V", "vs": "V", "voltage": "V", "voltage_source": "V", "voltage-source": "V",
    "i": "I", "is": "I", "current": "I", "current_source": "I", "current-source": "I",
}

_UNIT_OF_TYPE = {"R": OHM, "V": "V", "I": "A"}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _quantity(value, unit):
    """Wrap a finite float as {"value": ..., "unit": ...}.

    Inputs are validated as finite, so a non-finite result can only come from
    arithmetic overflow; it is reported as an input-magnitude problem.
    """
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(
            f"the result in {unit} overflowed the floating-point range (inf or nan); "
            "check the magnitudes of the inputs"
        )
    return {"value": value, "unit": unit}


def _real(name, value):
    """Return value as a float after checking that it is a finite real number."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"{name} must be a real number, got {value!r}")
    try:
        value = float(value)
    except OverflowError:
        raise ValueError(
            f"{name} is too large for a floating-point number (the limit is about 1.8e308)"
        ) from None
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return value


def _resistance(name, value, allow_zero=False):
    """Validate a resistance in Ohm: finite, not negative, zero only if allowed,
    and large enough that its conductance 1/R is still a finite float."""
    r = _real(name, value)
    if r < 0:
        raise ValueError(f"{name} must not be negative: a passive resistor has R >= 0 Ohm, got {r} Ohm")
    if r == 0 and not allow_zero:
        raise ValueError(
            f"{name} must be greater than 0 Ohm: a 0 Ohm element is an ideal wire, and a voltage "
            "applied across it would drive unbounded current"
        )
    if r > 0 and not math.isfinite(1.0 / r):
        raise ValueError(
            f"{name} = {r} Ohm is too small to represent: its conductance 1/R overflows the "
            "floating-point range (use 0 Ohm for a wire where that is allowed)"
        )
    return r


def _sequence(name, values, unit):
    """Validate a non-empty sequence of finite real numbers; return a list of floats."""
    if isinstance(values, (str, bytes, dict)) or not hasattr(values, "__iter__"):
        raise ValueError(f"{name} must be a list of numbers in {unit}")
    items = list(values)
    if not items:
        raise ValueError(f"{name} is empty: at least one value in {unit} is needed")
    return [_real(f"{name}[{k}]", v) for k, v in enumerate(items)]


def _fsum(values):
    """math.fsum that reports a float-range overflow as a ValueError, not a traceback."""
    try:
        return math.fsum(values)
    except OverflowError:
        raise ValueError(
            "the values overflow the floating-point range when summed; check the magnitudes of the inputs"
        ) from None


# ---------------------------------------------------------------------------
# Ohm's law, power and energy
# ---------------------------------------------------------------------------

def ohm(v=None, i=None, r=None):
    """Solve V = I R for the missing quantity of an ideal resistor.

    Parameters: v voltage (V), i current (A), r resistance (Ohm).  Give any two
    and the third is solved; give all three and the call checks that they are
    consistent.  Rejects an under-determined call (fewer than two values), a
    non-finite input, a negative resistance, a zero resistance with a voltage
    applied (no finite current), zero current when solving for r (open
    circuit, no finite resistance), opposite signs of v and i (negative
    resistance) and an inconsistent triple.

    Returns a dict with "solved_for", voltage (V), current (A), resistance
    (Ohm) and the power absorbed by the resistor (W).
    """
    given = [name for name, value in (("v", v), ("i", i), ("r", r)) if value is not None]
    if len(given) < 2:
        raise ValueError(
            "ohm() is under-determined: give two of v (V), i (A) and r (Ohm) to solve for the third; got "
            + (", ".join(given) if given else "nothing")
        )
    if v is not None:
        v = _real("v", v)
    if i is not None:
        i = _real("i", i)
    if r is not None:
        r = _resistance("r", r, allow_zero=True)

    if r is None:
        if i == 0.0:
            raise ValueError(
                "cannot solve r = v / i with i = 0 A: the resistance is undefined "
                "(an open circuit if v is not 0 V, anything at all if v = 0 V)"
            )
        r = v / i
        if r < 0:
            raise ValueError(
                "v and i have opposite signs, which would give a negative resistance; with the passive "
                "sign convention (current enters the + terminal) a resistor has v and i of the same sign"
            )
        solved_for = "r"
    elif v is None:
        v = i * r
        solved_for = "v"
    elif i is None:
        if r == 0.0:
            raise ValueError(
                "cannot solve i = v / r with r = 0 Ohm: an ideal voltage source across an ideal wire "
                "(a short circuit) has no finite current"
            )
        i = v / r
        solved_for = "i"
    else:
        expected = i * r
        if not math.isclose(v, expected, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError(
                f"inconsistent inputs: v = {v} V but i * r = {i} A * {r} Ohm = {expected} V; "
                "change one value or give only two of them"
            )
        solved_for = "none (consistency check passed)"

    return {
        "model": "ideal-resistor-ohm-law",
        "validation_status": "analytical-example",
        "lab_version": __version__,
        "assumptions": list(COMMON_ASSUMPTIONS),
        "limitations": list(COMMON_LIMITATIONS),
        "solved_for": solved_for,
        "voltage": _quantity(v, "V"),
        "current": _quantity(i, "A"),
        "resistance": _quantity(r, OHM),
        "power": _quantity(v * i, "W"),
    }


def power_energy(v, i, hours):
    """Power and energy of one element from its voltage, current and duration.

    v: voltage (V); i: current (A); hours: duration in hours (h), a convenience
    unit converted to seconds (1 h = 3600 s).  Power is assumed constant over
    the duration.  Returns power in W, energy in J and in Wh, and the duration
    in s.  Positive power means the element absorbs energy (passive sign
    convention); a source supplying energy shows negative values.
    """
    v = _real("v", v)
    i = _real("i", i)
    h = _real("hours", hours)
    if h < 0:
        raise ValueError(f"hours must not be negative, got {h} h: a duration cannot be negative")
    power = v * i
    seconds = h * 3600.0
    return {
        "model": "constant-power-energy",
        "validation_status": "analytical-example",
        "lab_version": __version__,
        "assumptions": list(COMMON_ASSUMPTIONS) + ["power is constant over the whole duration, so energy = power * time"],
        "limitations": list(COMMON_LIMITATIONS),
        "voltage": _quantity(v, "V"),
        "current": _quantity(i, "A"),
        "power": _quantity(power, "W"),
        "duration": _quantity(seconds, "s"),
        "duration_hours": _quantity(h, "h"),
        "energy": _quantity(power * seconds, "J"),
        "energy_watt_hours": _quantity(power * h, "Wh"),
    }


# ---------------------------------------------------------------------------
# Series, parallel and the voltage divider
# ---------------------------------------------------------------------------

def series_parallel(resistances, mode):
    """Equivalent resistance of a group of resistors.

    resistances: non-empty list of resistances in Ohm (finite, not negative).
    mode: "series" (same current, resistances add) or "parallel" (same
    voltage, conductances add).  A 0 Ohm resistor is accepted in series (it is
    a wire) but rejected in parallel, where it would short-circuit the group.

    Returns the equivalent resistance (Ohm), the equivalent conductance (S)
    when it is finite, and a sanity check: a series group is at least as large
    as its largest member, a parallel group no larger than its smallest.
    """
    if isinstance(resistances, (str, bytes, dict)) or not hasattr(resistances, "__iter__"):
        raise ValueError("resistances must be a list of resistances in Ohm")
    values = list(resistances)
    if not values:
        raise ValueError("resistances is empty: at least one resistor is needed to form an equivalent resistance")
    mode_key = str(mode).strip().lower()
    if mode_key not in ("series", "parallel"):
        raise ValueError(f"mode must be 'series' or 'parallel', got {mode!r}")
    rs = []
    for k, value in enumerate(values):
        r = _resistance(f"resistances[{k}]", value, allow_zero=True)
        if r == 0.0 and mode_key == "parallel":
            raise ValueError(
                f"resistances[{k}] is 0 Ohm: a 0 Ohm branch in parallel short-circuits the whole group "
                "(equivalent 0 Ohm) and any applied voltage would drive unbounded current; remove it or model it as a wire"
            )
        rs.append(r)

    if mode_key == "series":
        equivalent = _fsum(rs)
        rule = "series: R_eq >= largest resistor"
        passes = equivalent >= max(rs) * (1 - 1e-12)
    else:
        equivalent = 1.0 / _fsum(1.0 / r for r in rs)
        rule = "parallel: R_eq <= smallest resistor"
        passes = equivalent <= min(rs) * (1 + 1e-12)

    result = {
        "model": f"ideal-resistors-{mode_key}",
        "validation_status": "analytical-example",
        "lab_version": __version__,
        "assumptions": list(COMMON_ASSUMPTIONS),
        "limitations": list(COMMON_LIMITATIONS),
        "mode": mode_key,
        "count": len(rs),
        "resistances": [_quantity(r, OHM) for r in rs],
        "equivalent_resistance": _quantity(equivalent, OHM),
        "sanity_check": {"rule": rule, "passes": bool(passes)},
    }
    if equivalent > 0:
        result["equivalent_conductance"] = _quantity(1.0 / equivalent, "S")
    return result


def voltage_divider(v_in, r_top, r_bottom, r_load=None):
    """Two-resistor voltage divider, unloaded and loaded.

    v_in: source voltage (V) across the series pair.  r_top: resistor from the
    source to the output node (Ohm, > 0).  r_bottom: resistor from the output
    node to the return (Ohm, > 0).  r_load: optional load across r_bottom
    (Ohm, > 0); None means no load.

    Returns the unloaded output V_out = V_in * R_bottom / (R_top + R_bottom),
    the loaded output with R_bottom replaced by R_bottom || R_load, the loading
    error (loaded minus unloaded, in V, as a fraction and in percent), the
    Thevenin equivalent seen by the load (V_th = unloaded output,
    R_th = R_top || R_bottom), the divider currents and the power drawn from
    the source.  The relative loading error is -R_th / (R_th + R_load) and does
    not depend on V_in.
    """
    v_in = _real("v_in", v_in)
    r_top = _resistance("r_top", r_top)
    r_bottom = _resistance("r_bottom", r_bottom)
    r_series = r_top + r_bottom
    v_unloaded = v_in * r_bottom / r_series
    r_th = r_top * r_bottom / r_series
    i_unloaded = v_in / r_series

    if r_load is None:
        r_bottom_eff = r_bottom
        v_loaded = v_unloaded
        i_load = 0.0
        error_rel = 0.0
        load_quantity = None
    else:
        r_load = _resistance("r_load", r_load)
        r_bottom_eff = r_bottom * r_load / (r_bottom + r_load)
        v_loaded = v_in * r_bottom_eff / (r_top + r_bottom_eff)
        i_load = v_loaded / r_load
        error_rel = -r_th / (r_th + r_load)
        load_quantity = _quantity(r_load, OHM)
    i_in_loaded = v_in / (r_top + r_bottom_eff)

    return {
        "model": "ideal-two-resistor-voltage-divider",
        "validation_status": "analytical-example",
        "lab_version": __version__,
        "assumptions": list(COMMON_ASSUMPTIONS) + ["the load is a pure resistance across r_bottom"],
        "limitations": list(COMMON_LIMITATIONS),
        "input_voltage": _quantity(v_in, "V"),
        "r_top": _quantity(r_top, OHM),
        "r_bottom": _quantity(r_bottom, OHM),
        "load_resistance": load_quantity,
        "output_unloaded": _quantity(v_unloaded, "V"),
        "output_loaded": _quantity(v_loaded, "V"),
        "loading_error": _quantity(v_loaded - v_unloaded, "V"),
        "loading_error_relative": _quantity(error_rel, "1"),
        "loading_error_percent": _quantity(100.0 * error_rel, "%"),
        "thevenin_voltage": _quantity(v_unloaded, "V"),
        "thevenin_resistance": _quantity(r_th, OHM),
        "r_bottom_parallel_load": _quantity(r_bottom_eff, OHM),
        "input_current_unloaded": _quantity(i_unloaded, "A"),
        "input_current_loaded": _quantity(i_in_loaded, "A"),
        "load_current": _quantity(i_load, "A"),
        "source_power_unloaded": _quantity(v_in * i_unloaded, "W"),
        "source_power_loaded": _quantity(v_in * i_in_loaded, "W"),
    }


# ---------------------------------------------------------------------------
# Nodal analysis
# ---------------------------------------------------------------------------

def _normalise_branch(index, branch):
    """Validate one branch dict and return {"name", "type", "a", "b", "value"}."""
    if not isinstance(branch, dict):
        raise ValueError(f"branch {index} must be a dict with keys 'type', 'nodes' and 'value'")
    raw_type = branch.get("type")
    etype = _ELEMENT_TYPES.get(str(raw_type).strip().lower()) if raw_type is not None else None
    if etype is None:
        raise ValueError(
            f"branch {index}: unknown element type {raw_type!r}; use 'R' (resistor), "
            "'V' (voltage source) or 'I' (current source)"
        )
    nodes = branch.get("nodes")
    if not isinstance(nodes, (list, tuple)) or len(nodes) != 2:
        raise ValueError(f"branch {index}: 'nodes' must be a pair [a, b] of node labels")
    a, b = (str(n) for n in nodes)
    if a == b:
        raise ValueError(f"branch {index}: both terminals connect to node {a!r}; a branch must join two different nodes")
    name = str(branch.get("name") or f"{etype}{index + 1}")
    if "value" not in branch:
        raise ValueError(f"branch {name}: missing 'value' in {_UNIT_OF_TYPE[etype]}")
    if etype == "R":
        value = _resistance(f"branch {name} resistance", branch["value"], allow_zero=True)
        if value == 0.0:
            raise ValueError(
                f"branch {name}: a 0 Ohm resistor is an ideal wire; give both ends the same node label "
                "instead of adding a resistor"
            )
    else:
        value = _real(f"branch {name} value", branch["value"])
    return {"name": name, "type": etype, "a": a, "b": b, "value": value}


def _find(parent, x):
    """Union-find root lookup with path halving."""
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def gaussian_elimination(matrix, rhs):
    """Solve matrix * x = rhs by Gaussian elimination with partial pivoting.

    matrix: square list of lists of floats; rhs: list of floats.  Pure Python,
    O(n^3), intended for a few dozen unknowns at most.  Raises ValueError when
    a pivot is smaller than 1e-13 times the largest matrix entry, which signals
    a singular (or numerically singular) system.  The threshold is relative to
    the largest entry of the whole matrix, which is 1 whenever an MNA matrix
    holds a voltage source, so networks whose conductances are all below about
    1e-13 S (resistances above about 1e13 Ohm) are rejected as singular.
    """
    n = len(rhs)
    if n == 0 or any(len(row) != n for row in matrix) or len(matrix) != n:
        raise ValueError("gaussian_elimination needs a square matrix and a right-hand side of matching length")
    aug = [[float(x) for x in matrix[k]] + [float(rhs[k])] for k in range(n)]
    scale = max(abs(aug[r][c]) for r in range(n) for c in range(n))
    if scale == 0.0:
        raise ValueError("singular system: the coefficient matrix is all zeros")
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        pivot = aug[pivot_row][col]
        if abs(pivot) <= 1e-13 * scale:
            raise ValueError(
                "singular system: the network has no unique solution "
                "(check for floating nodes or loops of ideal voltage sources)"
            )
        if pivot_row != col:
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pivot_values = aug[col]
        for r in range(col + 1, n):
            factor = aug[r][col] / pivot
            if factor != 0.0:
                row = aug[r]
                for c in range(col, n + 1):
                    row[c] -= factor * pivot_values[c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        total = aug[r][n] - _fsum(aug[r][c] * x[c] for c in range(r + 1, n))
        x[r] = total / aug[r][r]
    if any(not math.isfinite(value) for value in x):
        raise ValueError("singular or ill-conditioned system: the solution is not finite")
    return x


def solve_network(branches, ground="0"):
    """Solve a small DC resistive network by modified nodal analysis (MNA).

    branches: list of dicts {"type": "R" | "V" | "I", "nodes": [a, b],
    "value": x, "name": optional}.  Node labels are converted to str.
      R: resistance in Ohm (> 0) between a and b.
      V: ideal voltage source with V(a) - V(b) = value in V (a is the + terminal).
      I: ideal current source driving `value` amperes from a through the source
         to b, so it injects current into node b (the SPICE convention).
    ground: label of the reference node (0 V), default "0".

    Method: one KCL equation per non-ground node plus one constraint row per
    voltage source (its current is an extra unknown), solved with pure-Python
    Gaussian elimination and partial pivoting.  Before solving, the network is
    checked structurally: every node needs a resistor or voltage-source path to
    ground (a current source alone does not fix a voltage) and ideal voltage
    sources must not form a loop.

    Returns node voltages (V), each branch's voltage (V), current (A, flowing
    from a to b inside the element) and power (W, positive when absorbed), the
    signed current sum at every node (KCL residual), the resistor dissipation,
    the source supply and their difference (power balance residual).  The
    "checks" entry also reports the tolerances behind "passes": a relative part
    (1e-9 of the largest current or power) plus the floating-point rounding
    floor of the node voltages, about 64 * eps * V_max, converted to a current
    through the largest conductance and to a power through V_max again.

    Limits: at most MAX_UNKNOWNS (50) unknowns, independent sources only, no
    controlled sources, no capacitors, inductors or non-linear devices.  When
    series resistances differ by more than about 1e8 the small resistor's
    current is found by subtracting nearly equal node voltages and keeps only
    the digits above the rounding floor (see the module docstring).  The
    result is a numerical solution of an idealised model, not a measurement.
    """
    if isinstance(branches, (str, bytes, dict)) or not hasattr(branches, "__iter__"):
        raise ValueError("branches must be a list of branch dicts")
    items = [_normalise_branch(k, b) for k, b in enumerate(list(branches))]
    if not items:
        raise ValueError("branches is empty: a network needs at least one branch")
    names = [item["name"] for item in items]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(f"branch names must be unique; duplicated: {', '.join(duplicates)}")
    ground = str(ground)
    nodes = []
    for item in items:
        for node in (item["a"], item["b"]):
            if node not in nodes:
                nodes.append(node)
    if ground not in nodes:
        raise ValueError(f"ground node {ground!r} does not appear in any branch; nodes present: {', '.join(nodes)}")

    adjacency = {node: set() for node in nodes}
    for item in items:
        if item["type"] in ("R", "V"):
            adjacency[item["a"]].add(item["b"])
            adjacency[item["b"]].add(item["a"])
    reached = {ground}
    frontier = [ground]
    while frontier:
        node = frontier.pop()
        for nxt in adjacency[node]:
            if nxt not in reached:
                reached.add(nxt)
                frontier.append(nxt)
    floating = [node for node in nodes if node not in reached]
    if floating:
        raise ValueError(
            "floating node(s) " + ", ".join(repr(n) for n in floating)
            + ": no resistor or voltage-source path to ground, so the node voltage is undefined "
            "(a current source alone does not fix a voltage)"
        )
    parent = {node: node for node in nodes}
    for item in items:
        if item["type"] == "V":
            root_a, root_b = _find(parent, item["a"]), _find(parent, item["b"])
            if root_a == root_b:
                raise ValueError(
                    f"voltage source {item['name']} closes a loop of ideal voltage sources; "
                    "parallel or looped ideal voltage sources are either contradictory or redundant"
                )
            parent[root_a] = root_b

    unknown_nodes = [node for node in nodes if node != ground]
    index = {node: k for k, node in enumerate(unknown_nodes)}
    vsources = [item for item in items if item["type"] == "V"]
    n_nodes = len(unknown_nodes)
    size = n_nodes + len(vsources)
    if size > MAX_UNKNOWNS:
        raise ValueError(
            f"network has {size} unknowns; this teaching solver is limited to {MAX_UNKNOWNS} "
            "(use a circuit simulator for larger networks)"
        )

    matrix = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for item in items:
        ia, ib = index.get(item["a"]), index.get(item["b"])
        if item["type"] == "R":
            g = 1.0 / item["value"]
            if ia is not None:
                matrix[ia][ia] += g
            if ib is not None:
                matrix[ib][ib] += g
            if ia is not None and ib is not None:
                matrix[ia][ib] -= g
                matrix[ib][ia] -= g
        elif item["type"] == "I":
            if ia is not None:
                rhs[ia] -= item["value"]
            if ib is not None:
                rhs[ib] += item["value"]
    for k, source in enumerate(vsources):
        row = n_nodes + k
        ia, ib = index.get(source["a"]), index.get(source["b"])
        if ia is not None:
            matrix[ia][row] += 1.0
            matrix[row][ia] += 1.0
        if ib is not None:
            matrix[ib][row] -= 1.0
            matrix[row][ib] -= 1.0
        rhs[row] = source["value"]

    solution = gaussian_elimination(matrix, rhs)
    voltages = {ground: 0.0}
    for node, k in index.items():
        voltages[node] = solution[k]
    source_currents = {source["name"]: solution[n_nodes + k] for k, source in enumerate(vsources)}

    branch_results = []
    leaving = {node: [] for node in nodes}
    dissipated = []
    supplied = []
    for item in items:
        v = voltages[item["a"]] - voltages[item["b"]]
        if item["type"] == "R":
            i = v / item["value"]
        elif item["type"] == "V":
            i = source_currents[item["name"]]
        else:
            i = item["value"]
        p = v * i
        (dissipated if item["type"] == "R" else supplied).append(p if item["type"] == "R" else -p)
        leaving[item["a"]].append(i)
        leaving[item["b"]].append(-i)
        branch_results.append({
            "name": item["name"],
            "type": item["type"],
            "nodes": [item["a"], item["b"]],
            "value": _quantity(item["value"], _UNIT_OF_TYPE[item["type"]]),
            "voltage": _quantity(v, "V"),
            "current": _quantity(i, "A"),
            "power": _quantity(p, "W"),
        })

    node_sums = {node: _fsum(currents) for node, currents in leaving.items()}
    max_kcl = max(abs(value) for value in node_sums.values())
    current_scale = max(abs(b["current"]["value"]) for b in branch_results)
    p_dissipated = _fsum(dissipated)
    p_supplied = _fsum(supplied)
    power_residual = p_dissipated - p_supplied
    power_scale = max(abs(p_dissipated), abs(p_supplied))
    # Tolerances: a relative part for the arithmetic plus the rounding floor of
    # the node voltages (about eps * V_max), which becomes a current through
    # the largest conductance and a power when multiplied by V_max again.
    eps = sys.float_info.epsilon
    v_max = max(abs(value) for value in voltages.values())
    g_max = max((1.0 / item["value"] for item in items if item["type"] == "R"), default=0.0)
    kcl_tolerance = 1e-9 * current_scale + 64.0 * eps * v_max * g_max + 1e-15
    power_tolerance = 1e-9 * power_scale + 64.0 * eps * v_max * v_max * g_max + 1e-15
    passes = max_kcl <= kcl_tolerance and abs(power_residual) <= power_tolerance

    return {
        "model": "dc-nodal-analysis-mna-gaussian-elimination",
        "validation_status": "numerical-simulation",
        "lab_version": __version__,
        "assumptions": list(COMMON_ASSUMPTIONS) + [
            "independent sources only; node voltages found by solving the KCL equations with Gaussian elimination and partial pivoting",
        ],
        "limitations": list(COMMON_LIMITATIONS) + [
            f"small networks only (at most {MAX_UNKNOWNS} unknowns); no controlled sources, capacitors, inductors or non-linear devices",
            "floating nodes and loops of ideal voltage sources are rejected rather than approximated",
            "series resistances that differ by more than about 1e8 leave the small resistor's current with only the digits "
            "above the rounding floor (absolute error about 1e-16 * V_max / R_small); the check tolerances allow for this floor",
        ],
        "ground": ground,
        "unknowns": size,
        "node_voltages": {node: _quantity(voltages[node], "V") for node in nodes},
        "branches": branch_results,
        "node_current_sums": {node: _quantity(node_sums[node], "A") for node in nodes},
        "checks": {
            "max_kcl_residual": _quantity(max_kcl, "A"),
            "kcl_tolerance": _quantity(kcl_tolerance, "A"),
            "power_dissipated_by_resistors": _quantity(p_dissipated, "W"),
            "power_supplied_by_sources": _quantity(p_supplied, "W"),
            "power_balance_residual": _quantity(power_residual, "W"),
            "power_tolerance": _quantity(power_tolerance, "W"),
            "passes": bool(passes),
        },
    }


def example_network(name="loaded-divider"):
    """Return a fresh copy of one of the built-in example branch lists.

    Names: "single-resistor" (6 V across 300 Ohm), "loaded-divider" (12 V,
    10 kOhm / 10 kOhm, 10 kOhm load) and "two-source" (12 V source, 2 kOhm,
    4 kOhm and a 1.5 mA current source meeting at one node).
    """
    try:
        template = EXAMPLE_NETWORKS[name]
    except KeyError:
        raise ValueError(f"unknown example {name!r}; choose from {', '.join(sorted(EXAMPLE_NETWORKS))}") from None
    return [dict(branch, nodes=list(branch["nodes"])) for branch in template]


def node_currents(network_result, node):
    """Signed currents (A) leaving `node` in a solve_network() result.

    Positive values leave the node, negative values enter it; the list is
    ready for kcl_kvl_check(branch_currents=...).
    """
    node = str(node)
    currents = []
    for branch in network_result["branches"]:
        a, b = branch["nodes"]
        i = branch["current"]["value"]
        if a == node:
            currents.append(i)
        if b == node:
            currents.append(-i)
    if not currents:
        raise ValueError(f"node {node!r} is not in the network result")
    return currents


# ---------------------------------------------------------------------------
# Conservation checks
# ---------------------------------------------------------------------------

def _conservation(label, values, unit, rel_tol, abs_tol):
    """Sum `values` (in `unit`, A for KCL or V for KVL) and compare |sum| with
    max(abs_tol, rel_tol * largest magnitude); returns the per-law dict used by
    kcl_kvl_check()."""
    items = _sequence(label, values, unit)
    total = _fsum(items)
    scale = max(abs(value) for value in items)
    tolerance = max(abs_tol, rel_tol * scale)
    return {
        "count": len(items),
        "values": [_quantity(value, unit) for value in items],
        "sum": _quantity(total, unit),
        "largest_magnitude": _quantity(scale, unit),
        "tolerance": _quantity(tolerance, unit),
        "passes": bool(abs(total) <= tolerance),
    }


def kcl_kvl_check(branch_currents=None, loop_voltages=None, rel_tol=1e-9, abs_tol=1e-12):
    """Verify Kirchhoff's laws on supplied numbers to a tolerance.

    branch_currents: currents in A meeting at one node, positive when leaving
    the node (KCL: they must sum to zero).  loop_voltages: voltages in V around
    one closed loop in the direction of travel, drops positive and rises
    negative (KVL: they must sum to zero).  Give one or both lists.
    rel_tol: tolerance relative to the largest magnitude in a list; abs_tol: an
    absolute floor in A or V.  Hand calculations rounded to three significant
    figures typically need rel_tol around 1e-3.

    The function does not raise when a sum fails; it reports "passes": False
    for that law and overall.  It raises ValueError for missing, empty or
    non-finite inputs and for negative tolerances.
    """
    if branch_currents is None and loop_voltages is None:
        raise ValueError(
            "give branch_currents (A, signed, positive leaving the node) and/or loop_voltages "
            "(V, signed drops around one loop)"
        )
    rel_tol = _real("rel_tol", rel_tol)
    abs_tol = _real("abs_tol", abs_tol)
    if rel_tol < 0 or abs_tol < 0:
        raise ValueError("tolerances must not be negative")
    result = {
        "model": "kirchhoff-conservation-check",
        "validation_status": "analytical-example",
        "lab_version": __version__,
        "assumptions": [
            "KCL: the signed currents meeting at one node sum to zero (charge is conserved, no storage in the node)",
            "KVL: the signed voltage drops around one closed loop sum to zero (potential is single valued)",
        ],
        "limitations": list(COMMON_LIMITATIONS) + ["checks the numbers you supply; it cannot detect a sign convention applied inconsistently"],
        "rel_tol": _quantity(rel_tol, "1"),
    }
    flags = []
    if branch_currents is not None:
        result["kcl"] = _conservation("branch_currents", branch_currents, "A", rel_tol, abs_tol)
        flags.append(result["kcl"]["passes"])
    if loop_voltages is not None:
        result["kvl"] = _conservation("loop_voltages", loop_voltages, "V", rel_tol, abs_tol)
        flags.append(result["kvl"]["passes"])
    result["passes"] = all(flags)
    return result


# ---------------------------------------------------------------------------
# Default example and plotting
# ---------------------------------------------------------------------------

def default_example():
    """The lesson's default numbers in one dict.

    6 V across 300 Ohm for 0.5 h; two 10 kOhm resistors in series and in
    parallel; a 12 V divider of 10 kOhm / 10 kOhm loaded by 10 kOhm, solved
    analytically and again by nodal analysis; and a KCL/KVL check on the nodal
    result (currents at the output node, voltages around the source loop).
    """
    ohm_result = ohm(v=6.0, r=300.0)
    energy = power_energy(6.0, ohm_result["current"]["value"], 0.5)
    series = series_parallel([10000.0, 10000.0], "series")
    parallel = series_parallel([10000.0, 10000.0], "parallel")
    divider = voltage_divider(12.0, 10000.0, 10000.0, 10000.0)
    network = solve_network(example_network("loaded-divider"))
    by_name = {branch["name"]: branch for branch in network["branches"]}
    loop = [
        -by_name["V1"]["voltage"]["value"],      # travelling up through the source: a rise
        by_name["Rtop"]["voltage"]["value"],     # drop across the top resistor
        by_name["Rbottom"]["voltage"]["value"],  # drop across the bottom resistor back to ground
    ]
    check = kcl_kvl_check(branch_currents=node_currents(network, "out"), loop_voltages=loop)
    analytical = divider["output_loaded"]["value"]
    numerical = network["node_voltages"]["out"]["value"]
    return {
        "model": "dc-circuit-fundamentals-default-example",
        "validation_status": "analytical-example",
        "assumptions": list(COMMON_ASSUMPTIONS),
        "limitations": list(COMMON_LIMITATIONS),
        "lab_version": __version__,
        "ohm": ohm_result,
        "power_energy": energy,
        "series": series,
        "parallel": parallel,
        "voltage_divider": divider,
        "network": network,
        "kcl_kvl_check": check,
        "cross_check": {
            "divider_output_analytical": _quantity(analytical, "V"),
            "divider_output_nodal": _quantity(numerical, "V"),
            "difference": _quantity(numerical - analytical, "V"),
        },
    }


def plot_loading_curve(v_in, r_top, r_bottom, r_load=None, out=None):
    """Draw the loaded divider output against load resistance on a log axis.

    Needs matplotlib; when it is missing a notice is written to stderr and
    False is returned without error.  With `out` the figure is written to that
    file (notice on stderr, so stdout stays a single JSON document), otherwise
    a window is opened.  The figure is closed afterwards.  Returns True when a
    figure was produced.
    """
    try:
        import matplotlib
        if out:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "matplotlib is not installed, so no plot was produced; the JSON results are complete. "
            "Install it with: python -m pip install matplotlib",
            file=sys.stderr,
        )
        return False
    base = voltage_divider(v_in, r_top, r_bottom)
    r_th = base["thevenin_resistance"]["value"]
    v_open = base["output_unloaded"]["value"]
    loads = [r_th * 10 ** (k / 8) for k in range(-16, 25)]  # 0.01 to 1000 times R_th
    outputs = [voltage_divider(v_in, r_top, r_bottom, r)["output_loaded"]["value"] for r in loads]

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.grid(True, which="major", color="#e6e5e1", linewidth=1)
    ax.set_axisbelow(True)
    ax.axhline(v_open, color="#b9b8b3", linewidth=1)
    ax.text(loads[0], v_open, f"unloaded output {v_open:g} V", color="#52514e", va="bottom", fontsize=9)
    ax.semilogx(loads, outputs, color="#2a78d6", linewidth=2, solid_joinstyle="round", solid_capstyle="round")
    ax.text(loads[-1], outputs[-1], " loaded output", color="#0b0b0b", va="center", fontsize=9)
    if r_load is not None:
        point = voltage_divider(v_in, r_top, r_bottom, r_load)["output_loaded"]["value"]
        ax.plot([r_load], [point], marker="o", markersize=8, color="#2a78d6",
                markeredgecolor="#fcfcfb", markeredgewidth=2)
        ax.annotate(f"{point:.3g} V at {r_load:g} Ohm", (r_load, point), textcoords="offset points",
                    xytext=(8, -14), color="#0b0b0b", fontsize=9)
    ax.set_xlabel("load resistance (Ohm)", color="#52514e")
    ax.set_ylabel("output voltage (V)", color="#52514e")
    ax.set_title(f"Loaded divider: V_in = {v_in:g} V, R_top = {r_top:g} Ohm, R_bottom = {r_bottom:g} Ohm",
                 fontsize=10, color="#0b0b0b")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#b9b8b3")
    ax.tick_params(colors="#52514e")
    fig.tight_layout()
    if out:
        fig.savefig(out, dpi=150)
        print(f"plot written to {out}", file=sys.stderr)
    else:
        plt.show()
    plt.close(fig)
    return True


# ---------------------------------------------------------------------------
# Command line interface
# ---------------------------------------------------------------------------

def _parse_branch(text):
    """Parse a CLI --branch string TYPE,NODE_A,NODE_B,VALUE[,NAME] into a branch
    dict; VALUE is in Ohm for R, V for V and A for I.  Raises ValueError on a
    malformed string."""
    parts = [p.strip() for p in str(text).split(",")]
    if len(parts) not in (4, 5):
        raise ValueError(f"--branch expects TYPE,NODE_A,NODE_B,VALUE[,NAME], got {text!r}")
    etype, a, b, raw_value = parts[:4]
    try:
        value = float(raw_value)
    except ValueError:
        raise ValueError(f"--branch {text!r}: VALUE must be a number") from None
    branch = {"type": etype, "nodes": [a, b], "value": value}
    if len(parts) == 5 and parts[4]:
        branch["name"] = parts[4]
    return branch


def build_parser():
    """Build the argparse parser (exposed for documentation and tests)."""
    parser = argparse.ArgumentParser(
        prog="dc_circuits.py",
        description=(
            "AIPE Academy DC circuit fundamentals lab: Ohm's law, power and energy, series/parallel "
            "groups, the loaded voltage divider, a small nodal solver and KCL/KVL checks. Without a "
            "subcommand it prints the lesson's default example (6 V across 300 Ohm; a 12 V divider of "
            "10 kOhm / 10 kOhm loaded by 10 kOhm) as JSON. All inputs are SI (V, A, Ohm) except "
            "--hours. Teaching model only: not validated hardware performance."
        ),
        epilog="Examples:\n  dc_circuits.py ohm --v 6 --r 300\n  dc_circuits.py divider --v-in 12 --r-top 10000 --r-bottom 10000 --r-load 10000\n  dc_circuits.py network --example two-source",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="print JSON (always the case; accepted for consistency with other labs)")
    parser.add_argument("--plot", action="store_true", help="also draw the divider loading curve (matplotlib; skipped with a message if it is missing)")
    parser.add_argument("--out", metavar="FILE", help="with --plot, write the figure to FILE instead of opening a window (notice on stderr; stdout stays JSON)")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p_ohm = sub.add_parser("ohm", help="solve V = I R for the missing quantity (give two of --v, --i, --r)")
    p_ohm.add_argument("--v", type=float, help="voltage in V")
    p_ohm.add_argument("--i", type=float, help="current in A")
    p_ohm.add_argument("--r", type=float, help="resistance in Ohm")

    p_power = sub.add_parser("power", help="power in W and energy in J and Wh from voltage, current and duration")
    p_power.add_argument("--v", type=float, required=True, help="voltage in V")
    p_power.add_argument("--i", type=float, required=True, help="current in A")
    p_power.add_argument("--hours", type=float, required=True, help="duration in hours (h)")

    for mode in ("series", "parallel"):
        p_mode = sub.add_parser(mode, help=f"equivalent resistance of resistors in {mode}")
        p_mode.add_argument("resistances", type=float, nargs="+", metavar="OHM", help="resistances in Ohm")

    p_div = sub.add_parser("divider", help="two-resistor voltage divider, optionally loaded")
    p_div.add_argument("--v-in", type=float, default=12.0, help="input voltage in V (default 12)")
    p_div.add_argument("--r-top", type=float, default=10000.0, help="top resistor in Ohm (default 10000)")
    p_div.add_argument("--r-bottom", type=float, default=10000.0, help="bottom resistor in Ohm (default 10000)")
    p_div.add_argument("--r-load", type=float, default=None, help="load resistor in Ohm across the bottom resistor (default: none)")

    p_net = sub.add_parser("network", help="solve a small DC resistive network by nodal analysis")
    p_net.add_argument("--branch", action="append", default=[], metavar="TYPE,A,B,VALUE[,NAME]",
                       help="repeatable; TYPE is R (Ohm), V (V, A is the + terminal) or I (A, flowing A->B through the source)")
    p_net.add_argument("--example", choices=sorted(EXAMPLE_NETWORKS), help="use a built-in example network")
    p_net.add_argument("--ground", default="0", help="label of the reference node (default 0)")

    p_check = sub.add_parser("check", help="verify KCL (signed currents at a node) and/or KVL (signed drops around a loop)")
    p_check.add_argument("--currents", type=float, nargs="+", metavar="A", help="signed currents in A at one node, positive leaving")
    p_check.add_argument("--voltages", type=float, nargs="+", metavar="V", help="signed voltage drops in V around one loop")
    p_check.add_argument("--rel-tol", type=float, default=1e-9, help="relative tolerance (default 1e-9; use 1e-3 for rounded hand values)")
    p_check.add_argument("--abs-tol", type=float, default=1e-12, help="absolute tolerance floor in A or V (default 1e-12)")
    return parser


def run(argv=None):
    """Entry point: returns the process exit code.

    0: success, stdout holds exactly one JSON document and notices go to
    stderr.  2: invalid input (ValueError or float overflow), "error: <message>"
    on stderr.  1: the console could not encode a notice (an output problem,
    not an input problem).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    plot_args = None
    try:
        if args.command is None:
            result = default_example()
            plot_args = (12.0, 10000.0, 10000.0, 10000.0)
        elif args.command == "ohm":
            result = ohm(v=args.v, i=args.i, r=args.r)
        elif args.command == "power":
            result = power_energy(args.v, args.i, args.hours)
        elif args.command in ("series", "parallel"):
            result = series_parallel(args.resistances, args.command)
        elif args.command == "divider":
            result = voltage_divider(args.v_in, args.r_top, args.r_bottom, args.r_load)
            plot_args = (args.v_in, args.r_top, args.r_bottom, args.r_load)
        elif args.command == "network":
            if args.example and args.branch:
                raise ValueError("give either --example or --branch, not both")
            if args.example:
                branches = example_network(args.example)
            else:
                branches = [_parse_branch(text) for text in args.branch]
            if not branches:
                raise ValueError("network needs --example NAME or at least one --branch TYPE,A,B,VALUE")
            result = solve_network(branches, ground=args.ground)
        else:
            result = kcl_kvl_check(args.currents, args.voltages, args.rel_tol, args.abs_tol)
        print(json.dumps(result, indent=2, allow_nan=False))
        if args.out and not args.plot:
            print("--out has no effect without --plot; no file was written", file=sys.stderr)
        if args.plot:
            if plot_args is None:
                print("--plot applies to the default example and the divider command; nothing to plot", file=sys.stderr)
            else:
                plot_loading_curve(*plot_args, out=args.out)
    except UnicodeEncodeError as exc:
        # A subclass of ValueError, so it must be caught first: the inputs were
        # fine, the console could not encode a notice (JSON itself is ASCII).
        print(f"output encoding error (not an input error): {exc}; set PYTHONIOENCODING=utf-8", file=sys.stderr)
        return 1
    except (ValueError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(run())
