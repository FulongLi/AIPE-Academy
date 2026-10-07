"""Ideal CCM buck calculation. Synthetic teaching case; no device model or hardware."""
import argparse
import json
import math


def calculate(v_in=24.0, v_out=12.0, power=30.0, frequency=100000.0, inductance=0.00015):
    values = (v_in, v_out, power, frequency, inductance)
    if any(isinstance(v, bool) or not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError("All inputs must be finite positive SI values")
    if v_out >= v_in:
        raise ValueError("This buck model requires 0 < output voltage < input voltage")
    duty = v_out / v_in
    current = power / v_out
    ripple = (v_in - v_out) * duty / (inductance * frequency)
    if current <= ripple / 2:
        raise ValueError("CCM assumption fails: choose a CCM point or use a DCM model")
    return {
        "model": "ideal-ccm-buck", "validation_status": "analytical-example",
        "assumptions": ["ideal switches", "periodic steady state", "small output voltage ripple", "resistive load", "continuous conduction"],
        "duty_ratio": {"value": duty, "unit": "1"},
        "output_current": {"value": current, "unit": "A"},
        "inductor_ripple_pp": {"value": ripple, "unit": "A"},
        "inductor_current_min": {"value": current - ripple / 2, "unit": "A"},
        "load_resistance": {"value": v_out * v_out / power, "unit": "Ohm"},
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name, default in (("v-in",24.0),("v-out",12.0),("power",30.0),("frequency",100000.0),("inductance",0.00015)):
        p.add_argument("--"+name, type=float, default=default)
    args = vars(p.parse_args())
    print(json.dumps(calculate(**args), indent=2, allow_nan=False))
