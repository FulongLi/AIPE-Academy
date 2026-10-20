# Predict and check an ideal buck converter

This original software-only lab links steady-state reasoning to a reproducible
calculation. It does not require a commercial licence, an API key or hardware.
Python 3.10+ and its standard library are sufficient.

Before starting, explain voltage, current, power, duty ratio, inductor continuity
and volt-second balance. Ask your tutor to return to the prerequisite bridge if
any of those are unfamiliar. Knowing a formula alone is not evidence of readiness.

Use a synthetic 24 V to 12 V, 30 W ideal converter, switching at 100000 Hz with
0.00015 H inductance. Assume continuous conduction, periodic steady state and
small output voltage ripple. Do not interpret these as a production design.

1. Predict the duty ratio using average inductor voltage of zero.
2. Calculate average output current from power and voltage.
3. Calculate on-time current rise: `(Vin - Vout) * duty / (L * frequency)`.
4. Run `python labs/buck_open.py` from the Academy checkout.
5. Compare your results with the JSON quantities: duty 0.5, current 2.5 A and
   peak-to-peak ripple 0.4 A. Explain why minimum current is positive.
6. Double frequency with `--frequency 200000`. Predict the ripple before running.
7. Try `--power 0.01`. The script rejects the continuous-conduction assumption.
   Explain why a positive voltage ratio alone does not justify the CCM model.

Record inputs, assumptions, software version, command, output and discrepancies.
No efficiency, losses, measured temperature or device suitability is predicted.
The next experiment is a switched-circuit simulation with ngspice; compare step
size and steady-state windows before interpreting solver waveforms. The AIPE
Simulation Skills repository provides that workflow. MATLAB/PLECS variants are
optional extensions with separate licences and model-validation requirements.

To pass, derive the voltage balance and explain an assumption failure without
copying the answer. A tutor should record assisted and independent performance
separately in the learner's local record, never the public repository.

## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 6.622 — Power Electronics (Spring 2023)
  https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/

Relevant subjects:

- Steady-state analysis of the buck converter
- Inductor volt-second balance and current ripple
- Continuous and discontinuous conduction modes

This lab has been independently developed by AIPE Academy with reference to the
academic scope of the above course. MIT OpenCourseWare is an external
educational resource released under its own licence (generally CC BY-NC-SA 4.0).
AIPE Academy is not affiliated with or endorsed by MIT.
