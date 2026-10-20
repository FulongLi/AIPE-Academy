# Buck converter fundamentals: from switch states to ripple and conduction modes

> Module: `pe.buck` · Also covers: `pe.topologies` · Level: undergraduate · Status: available
> Suggested time: 120 minutes · Labs: `labs/power-electronics/buck_switching.py`, `labs/buck_open.py`

A 24 V supply has to feed a 12 V load without wasting half of the energy as heat. The buck converter does this by switching the input on and off very quickly and letting an inductor and a capacitor smooth the result. This lesson explains why that works, how far a few lines of algebra predict the output voltage, the ripple and the conduction mode, and how to check those predictions with a switching simulation you can run yourself.

## Learning Objectives

After this lesson the learner can:

- draw the two current paths of a buck converter and name the element carrying the current in each;
- derive the ideal conversion ratio from volt-second balance and explain its load independence in continuous conduction;
- calculate the inductor current ripple, its extremes and the capacitor voltage ripple for an operating point;
- decide the conduction mode from the boundary current or the dimensionless $$K$$, and predict the discontinuous-mode output;
- predict, and verify with the lab, the open-loop response to changes of input voltage, load, frequency, inductance and capacitance;
- list what the ideal model leaves out and which way each effect moves a real measurement.

## Prerequisites

- DC circuits: Ohm's law, Kirchhoff's laws, power and energy (module `f.dc-circuits`; the Foundations lesson [DC circuit fundamentals](../../foundations/circuits/dc-circuit-fundamentals.md), slug `dc-circuit-fundamentals`, or the Chinese-language [first lesson](../../01-foundations/first-lesson.zh-CN.md)).
- The storage laws $$v = L\,\mathrm{d}i/\mathrm{d}t$$ and $$i = C\,\mathrm{d}v/\mathrm{d}t$$, and the fact that inductor current and capacitor voltage cannot jump (module `f.dynamics`).
- Period, frequency, duty cycle (called the duty ratio $$D$$ in this lesson) and the average of a periodic waveform (module `f.ac`).
- The ideal switch and diode as circuit elements (module `f.electronics`; real devices belong to `pe.devices`).
- Running a Python script and changing a command-line argument (module `f.computation`).

Mathematics introduced here: integrating a constant, the area of a triangle and one quadratic equation.

## Physical Intuition

Imagine filling a bucket from a tap that is either fully open or fully closed: open for half of every second, it delivers half the flow on average. A buck converter does the same: a switch connects the output filter to the input for a fraction $$D$$ of every period and disconnects it for the rest, so a perfect averaging filter would deliver $$D$$ times the input.

The inductor makes the averaging possible without burning energy. Its current cannot change instantly, so when the switch opens it keeps flowing, through the diode instead, and feeds the load in both intervals, rising a little while the switch is on and falling a little while it is off. That rise and fall is the inductor current ripple, which the capacitor absorbs so that the load sees an almost constant voltage.

Two questions before the derivations: if the switching frequency doubles, so each on-interval is half as long, what happens to the ripple? And since the diode conducts in one direction only, what happens when the load is so light that the falling current reaches zero before the switch turns on again?

## Fundamental Principles

### The circuit and its two loops

```text
             S (ideal switch)            L (inductor)
    +-----------o/ o-----------+---------UUUUU---------+-----------+
    |                          |                       |           |
    |                         ---  D (ideal diode,     |           |
   Vg  (input source)        / \   cathode up)        === C        R  (load)   v (output)
    |                         ---                      |           |
    |                          |                       |           |
    +--------------------------+-----------------------+-----------+
                             (common return)

   Loop 1, switch on  (0 < t < D Ts):   Vg -> S -> L -> C in parallel with R -> back to Vg.  Diode blocks.
   Loop 2, switch off (D Ts < t < Ts):  L -> C in parallel with R -> return -> D -> back to L.  Switch open.
```

Symbols: $$V_g$$ input voltage (V); $$v$$ output voltage (V); $$i_L$$ inductor current (A); $$L$$ inductance (H); $$C$$ capacitance (F); $$R$$ load resistance (Ω); $$f_s$$ switching frequency (Hz); $$T_s = 1/f_s$$ switching period (s); $$D$$ duty ratio, the fraction of the period for which the switch conducts (dimensionless, $$0 < D < 1$$). Upper-case $$V$$ and $$I$$ denote steady-state averages, lower-case letters instantaneous values.

Switch on. The inductor's left end sits at $$V_g$$, its voltage is $$V_g - v$$, positive, and its current rises; the diode blocks with $$V_g$$ across it.

Switch off. The inductor current must continue, so it pulls the switch node down until the diode conducts and holds the left end at zero; the inductor voltage is $$-v$$, the current falls, and the diode carries all of it.

In both intervals the capacitor current is $$i_C = i_L - v/R$$: the ripple goes into the capacitor and the average into the load.

```text
  i_L (A)                                       v (V)
  2.7 |     /\        /\        /\              12.0025 |  __        __
      |    /  \      /  \      /  \                     | /  \      /  \
  2.5 |   /    \    /    \    /    \   <- I = 2.5 A     |/    \    /    \
      |  /      \  /      \  /      \           12.0000 |------\--/------\--/-----
  2.3 | /        \/        \/        \                  |       \/        \/
      +----|----|----|----|----|----|--> t      11.9975 +----|----|----|----|--> t
        on  off  on  off  on  off                         on  off  on  off
   (design point: 10 us period, 5 us on)        (minimum halfway through "on", maximum halfway through "off")
```

### State equations

The two energy-storage laws give, with the switch position selecting the inductor voltage,

$$
L\frac{\mathrm{d}i_L}{\mathrm{d}t} =
\begin{cases}
V_g - v & \text{switch on} \\
-v & \text{switch off, diode conducting} \\
0 & \text{switch off, diode blocking, } i_L = 0
\end{cases}
\qquad
C\frac{\mathrm{d}v}{\mathrm{d}t} = i_L - \frac{v}{R} .
$$

The third case is what the diode forces at light load.

### Idealisations

The analysis assumes an ideal switch (no resistance, instant transitions) at constant duty ratio without feedback, an ideal diode (no forward drop, no reverse current), a lossless inductor and capacitor, a resistive load, a constant input voltage and periodic steady state; the lab shares every idealisation but starts from zero and runs until it reaches that state. Small-ripple approximations are named where used. Everything here is an analytical and numerical teaching model: no hardware has been measured and no efficiency or temperature is predicted.

### What the ideal model leaves out

- Conduction losses in switch, diode and winding lower the output below $$D V_g$$ and the efficiency below 1; switching losses, including the ringing of parasitic capacitance and inductance at the switch node when the diode turns off in discontinuous conduction (DCM, defined below), grow with $$f_s$$ and cap the useful frequency.
- A diode forward drop $$V_F$$ of about 0.5 V removes roughly $$(1 - D) V_F$$, here 0.25 V or 2 %, from the output.
- The capacitor's equivalent series resistance (ESR) adds a triangular term $$\Delta i \times R_{\mathrm{ESR}}$$ in phase with the inductor ripple: 50 mΩ gives 20 mV, four times the capacitive ripple found below and, the two being in quadrature, essentially the total.
- Start-up without soft start overshoots, here by two thirds (damping ratio $$\zeta = \sqrt{L/C}/(2R) = 0.128$$, dimensionless), and briefly drives several times the load current through the inductor.
- In DCM the output rises above $$D V_g$$; a synchronous rectifier that allows reverse current would keep continuous conduction (CCM) at the cost of circulating current.

## Mathematical Derivations

### Volt-second balance and the conversion ratio

In periodic steady state the inductor current ends the period where it started, so integrating $$v_L = L\,\mathrm{d}i_L/\mathrm{d}t$$ over one period gives

$$
\int_0^{T_s} v_L\,\mathrm{d}t = L\,[\,i_L(T_s) - i_L(0)\,] = 0 .
$$

The average inductor voltage is zero: inductor volt-second balance. In continuous conduction mode (CCM) the diode conducts for the whole off-interval, so $$v_L$$ is $$V_g - v$$ with the switch on and $$-v$$ with it off. Since $$\int_0^{T_s} v\,\mathrm{d}t = V\,T_s$$ by definition of the average,

$$
\int_0^{T_s} v_L\,\mathrm{d}t = V_g\,D\,T_s - \int_0^{T_s} v\,\mathrm{d}t = V_g\,D\,T_s - V\,T_s = 0
\quad\Longrightarrow\quad
V = D\,V_g ,
$$

exactly, whatever the ripple; the small-ripple approximation $$v \approx V$$ is needed only for the ripple formulas below and for the DCM analysis. The ideal conversion ratio $$M = V/V_g = D$$ contains neither $$R$$ nor $$L$$ nor $$f_s$$: in CCM the output depends on the duty ratio alone.

### Charge balance and the inductor current

The same argument for the capacitor gives $$\int_0^{T_s} i_C\,\mathrm{d}t = 0$$; with $$i_C = i_L - v/R$$ the average inductor current equals the load current, again exactly:

$$
I_L = \frac{V}{R} = I .
$$

### Inductor current ripple

During the on-interval the inductor voltage is constant, so the current rises linearly with slope $$(V_g - V)/L$$ for a time $$D T_s$$. The rise is the peak-to-peak ripple,

$$
\Delta i = \frac{(V_g - V)\,D}{L f_s} = \frac{V\,(1 - D)}{L f_s},
$$

where the second form uses $$V_g - V = V(1 - D)/D$$. The current is a triangle about its average, so $$i_{L,\min} = I - \Delta i/2$$ and $$i_{L,\max} = I + \Delta i/2$$; the ripple falls with $$L$$ and $$f_s$$ and, at fixed output voltage, is largest for small $$D$$.

### Output voltage ripple

The capacitor current is the triangular ripple $$i_L - I$$. It is positive for exactly half a period, from the middle of the on-interval to the middle of the off-interval, delivering the charge $$\Delta q$$ (C) under a triangle of base $$T_s/2$$ and height $$\Delta i/2$$:

$$
\Delta q = \frac{1}{2}\cdot\frac{T_s}{2}\cdot\frac{\Delta i}{2} = \frac{\Delta i\,T_s}{8},
\qquad
\Delta v = \frac{\Delta q}{C} = \frac{\Delta i}{8\,C f_s} .
$$

The voltage ripple is parabola-shaped, with its extremes where the capacitor current changes sign. The capacitor sees only $$\Delta i$$, never $$I$$.

### The conduction boundary

The diode carries only positive current, so the CCM analysis holds while $$i_{L,\min} > 0$$:

$$
I > \frac{\Delta i}{2} .
$$

Writing $$I = D V_g/R$$ and $$\Delta i = V_g D (1 - D)/(L f_s)$$ and cancelling $$D V_g$$, continuous conduction requires

$$
K > K_{\mathrm{crit}}, \qquad K = \frac{2L}{R\,T_s} = \frac{2 L f_s}{R}, \qquad K_{\mathrm{crit}} = 1 - D .
$$

The dimensionless $$K$$ compares $$2 L f_s$$, in ohms, with the load resistance: a light load means a large $$R$$, a small $$K$$ and discontinuous conduction. The boundary load resistance is $$R_{\mathrm{crit}} = 2 L f_s/(1 - D)$$.

### Discontinuous conduction

Below the boundary, in discontinuous conduction mode (DCM), each period has three intervals. The switch conducts for $$D T_s$$ and the current rises from zero to $$i_{pk} = (V_g - V) D T_s/L$$; the diode conducts for $$D_2 T_s$$ while the current falls to zero with slope $$-V/L$$, so also $$i_{pk} = V D_2 T_s/L$$; then both are off and the current stays at zero for $$(1 - D - D_2) T_s$$ while the capacitor alone feeds the load. Equating the two expressions for $$i_{pk}$$,

$$
D_2 = D\,\frac{V_g - V}{V} .
$$

The average inductor current, the triangle's area over the period, is $$I_L = \tfrac{1}{2} i_{pk} (D + D_2)$$ and must equal $$V/R$$. Write $$M = V/V_g$$. From the expression for $$D_2$$, $$D + D_2 = D V_g/V = D/M$$, and $$i_{pk} = (1 - M) D V_g T_s/L$$, so $$I_L = D^2 T_s V_g (1 - M)/(2 L M)$$. Setting this equal to $$V/R = M V_g/R$$ and using $$K = 2L/(R T_s)$$ gives $$D^2 (1 - M) = K M^2$$, the quadratic $$K M^2 + D^2 M - D^2 = 0$$, whose positive root is

$$
M_{\mathrm{DCM}} = \frac{2}{1 + \sqrt{1 + 4K/D^2}} .
$$

At $$K = 1 - D$$ this equals $$D$$, so the two modes join continuously; for $$K < 1 - D$$ it exceeds $$D$$: at light load the open-loop output rises above $$D V_g$$ and depends on the load as well as on the input, as the lab confirms. Real converters close a feedback loop around $$D$$ to remove both dependencies, the subject of the follow-on tutorial.

## Worked Examples

Both examples use the AIPE Academy synthetic design point: $$V_g = 24$$ V, $$V = 12$$ V, $$P = 30$$ W, $$f_s = 100$$ kHz, $$L = 150$$ µH, $$C = 100$$ µF. It is a teaching example, not a reviewed design.

### Example 1: the CCM operating point with `labs/buck_open.py`

$$D = 12/24 = 0.5$$; $$I = 30/12 = 2.5$$ A; $$R = 144/30 = 4.8$$ Ω; $$\Delta i = (24 - 12) \times 0.5 / (150 \times 10^{-6} \times 10^5) = 6/15 = 0.4$$ A; $$i_{L,\min} = 2.3$$ A and $$i_{L,\max} = 2.7$$ A; $$\Delta v = 0.4 / (8 \times 10^{-4} \times 10^5) = 5$$ mV, 0.04 % of the output, which justifies the small-ripple approximation. Sanity checks: the minimum current is positive, so CCM is consistent, and the input current $$D I = 1.25$$ A gives $$24 \times 1.25 = 30$$ W, matching the output power.

Run the analytical lab from the repository root:

```text
python labs/buck_open.py
```

It prints `duty_ratio` 0.5, `output_current` 2.5 A, `inductor_ripple_pp` 0.4 A, `inductor_current_min` 2.3 A and `load_resistance` 4.8 Ohm, with `validation_status` `analytical-example`. With `--power 0.01` the run is rejected with exit code 2 (`error: CCM assumption fails: choose a CCM point or use a DCM model`): at 10 mW the 0.83 mA average current is far below half the ripple, so the formulas no longer apply.

### Example 2: boundary and discontinuous conduction

$$K_{\mathrm{crit}} = 1 - D = 0.5$$ and at full load $$K = 2 \times 150 \times 10^{-6} \times 10^5 / 4.8 = 30/4.8 = 6.25$$: deep in CCM. The boundary load is $$R_{\mathrm{crit}} = 30/0.5 = 60$$ Ω, that is 0.2 A or 2.4 W, 8 % of rated power.

At $$R = 120$$ Ω, $$K = 0.25 < 0.5$$, so the converter is discontinuous: $$4K/D^2 = 4$$, $$M = 2/(1 + \sqrt{5}) = 0.618$$ and $$V = 14.83$$ V instead of 12 V. Then $$I = 14.83/120 = 0.1236$$ A, $$i_{pk} = (24 - 14.83) \times 0.5 \times 10^{-5} / (150 \times 10^{-6}) = 0.3056$$ A, $$D_2 = 0.5 \times 9.17/14.83 = 0.309$$, and the current is zero for $$1 - 0.5 - 0.309 = 0.191$$ of each period. Check: $$\tfrac{1}{2} \times 0.3056 \times 0.809 = 0.1236$$ A, equal to $$V/R$$.

## Numerical or Simulation Lab

- Lab script: [`labs/power-electronics/buck_switching.py`](../../../labs/power-electronics/buck_switching.py) (Python 3.10+, standard library; optional plotting with matplotlib). Tests: [`tests/test_lab_buck_switching.py`](../../../tests/test_lab_buck_switching.py).
- Model: the three-case state equations above with an ideal switch and a diode that blocks reverse current, so DCM appears by itself; a cold start from zero current and zero voltage without soft start. A numerical teaching model, not validated hardware performance.
- Inputs (SI units): `--v-in` (V); `--v-out` target (V, sets $$D = V_{\mathrm{target}}/V_g$$) or `--duty`; `--power` (W, sets $$R = V_{\mathrm{target}}^2/P$$) or `--load` (Ω); `--frequency` (Hz); `--inductance` (H); `--capacitance` (F); `--cycles`, `--steps-per-cycle` and `--tolerance`. Defaults: the design point, 20000 periods, 200 steps, $$10^{-8}$$.
- Method: fixed-step explicit first-order integration (semi-implicit Euler), 200 steps of 50 ns per period, switching instants exactly on step boundaries, diode turn-off inside a step located by linear interpolation. The run stops when the period averages of output voltage and inductor current change by less than the tolerance, relative to $$V_g$$ and $$V_g/R$$, for five successive periods, and reports the last period.
- Outputs: `steady_state` (means, ripples, extremes, conduction mode, zero-current fraction, input current and power balance), `startup` peaks, `analytical_ccm` (the `buck_open.py` formulas plus the capacitor ripple), `conduction_boundary`, `analytical_dcm` when predicted and `comparison` with relative differences, all `{"value", "unit"}` pairs with `validation_status` `numerical-simulation`.

Run the default case from the repository root:

```text
python labs/power-electronics/buck_switching.py
```

Expected values (deterministic on every platform):

```text
settling.settled                        true
settling.cycles_simulated               1427         (14.27 ms of converter time)
steady_state.conduction_mode            "CCM"
steady_state.output_voltage_mean        12.0000 V    analytical 12.0 V
steady_state.output_voltage_ripple_pp   5.0014 mV    analytical 5.0 mV
steady_state.inductor_current_mean      2.50000 A    analytical 2.5 A
steady_state.inductor_current_min       2.29997 A    analytical 2.3 A
steady_state.inductor_current_max       2.70003 A    analytical 2.7 A
steady_state.inductor_ripple_pp         0.40006 A    analytical 0.4 A
steady_state.input_current_mean         1.25000 A
steady_state.power_balance_error        6.4e-7
startup.peak_output_voltage             20.014 V
startup.peak_inductor_current           10.575 A
```

Every relative difference in `comparison.relative_difference` is below $$3 \times 10^{-4}$$. The largest, $$+2.8 \times 10^{-4}$$ on the voltage ripple, is only partly numerical: the exact ripple waveform gives 5.0008 mV ($$+1.7 \times 10^{-4}$$, second-order effects the formula ignores) and the remaining $$+1.1 \times 10^{-4}$$ is first-order step error, falling to $$+0.2 \times 10^{-4}$$ with `--steps-per-cycle 2000`. The $$+1.4 \times 10^{-4}$$ on the current ripple is not numerical: it is the second-order effect of the 5 mV voltage ripple on the current slopes, which the small-ripple formula ignores, and it is identical at 200 and 2000 steps. The mean output agrees to $$10^{-8}$$ because $$V = D V_g$$ is exact in CCM and the discrete scheme, too, satisfies volt-second balance exactly.

Numerical error. Even 20 steps per period keep the ripple within 0.13 %; the error is first order in the step but not monotonic (50 steps, an odd on-interval count, is worse than 20 at 0.20 %), so keep $$D N$$ even. Stopping too early matters more: `--tolerance 1e-6` stops after 962 periods with the voltage ripple 0.23 % high from residual start-up drift, `--tolerance 1e-5` after 767 periods with it 1.5 % low. The exception is `--power 0.01`: the diode conducts for 41 ns, under one step, and the current quantities come out about 1 % low.

Validation. A non-finite or non-positive input, a duty ratio outside $$(0, 1)$$, a target output at or above the input, fewer than four steps per period, a step above half the stability limit $$\min(2\sqrt{LC},\, 2RC)$$ of the explicit scheme (the message names a step count that works), a diverging state or an inconsistent pair (`--v-out` with `--duty`, `--power` with `--load`) raises `ValueError`; the command line prints `error:` with the reason and exits with code 2, and results never contain NaN or infinity. For reproducibility record the command, `python --version`, the JSON output and the result of `python -m unittest tests.test_lab_buck_switching`. `--plot --out buck.png` draws the last period and the start-up if matplotlib is installed and otherwise prints a message and exits 0.

## Parameter Exploration

Each experiment changes one parameter. Write your prediction down before running.

1. Frequency. Predict the ripple at 200 kHz, then run `python labs/power-electronics/buck_switching.py --frequency 200000`: $$\Delta i = 0.20001$$ A, $$i_{L,\min} = 2.4000$$ A, $$\Delta v = 1.2502$$ mV, output still 12.0000 V. The current ripple halves because the on-time halves at the same slope; the voltage ripple quarters because the ripple current and its duration both halve. Settling takes 2694 periods: the filter's response lasts a fixed time, so a faster clock fits more periods into it.

2. Input voltage at fixed duty. Run `--v-in 20 --duty 0.5 --load 4.8` and `--v-in 28 --duty 0.5 --load 4.8`: 10.0000 V with $$\Delta i = 0.33338$$ A and $$\Delta v = 4.168$$ mV, then 14.0000 V with 0.46673 A and 5.835 mV. The open-loop output is proportional to the input, exactly as $$V = D V_g$$ says.

3. Load. `--load 9.6` gives 12.0000 V, 1.2500 A and the same ripples, 0.40006 A and 5.001 mV, in CCM. `--load 60` gives a mean current of 0.2000 A, a minimum of 0.0000 A and a DCM label with a zero-current fraction of $$6 \times 10^{-5}$$, half a nanosecond per period ($$5 \times 10^{-5}$$ at 2000 steps), while the analytical block predicts the exact boundary $$K = 0.5$$ from the small-ripple formula: the real ripple is 0.014 % larger, the current dips a few tens of microamperes below zero and the converter is marginally discontinuous, so `mode_agrees` is false. `--load 120` gives DCM after 4342 periods: 14.834 V against the analytical 14.833 V, a 0.3056 A peak, zero current for 19.1 % of the period and diode conduction for 30.9 %, so the output is 24 % above $$D V_g$$ and depends on the load.

4. Capacitance. Predict, then run `--capacitance 1e-5` (10 µF): $$\Delta v = 50.09$$ mV, tenfold, while $$\Delta i = 0.4006$$ A and the output are unchanged. The start-up peak drops from 20.0 V to 15.0 V and settling takes 161 periods, because the damping ratio $$\zeta$$ rises from 0.128 to 0.40.

5. Inductance. `--inductance 75e-6` gives $$\Delta i = 0.8002$$ A, $$i_{L,\min} = 2.0999$$ A, $$\Delta v = 10.004$$ mV, $$K = 3.125$$ and $$R_{\mathrm{crit}} = 30$$ Ω: halving $$L$$ doubles both ripples and halves the load range with continuous conduction.

## Common Misconceptions

- "The output is $$D V_g$$ whatever the load." Only in CCM. Below the boundary the diode blocks, volt-second balance gains a third interval and the output rises towards $$V_g$$: 24 V in and 10 mW out gives 23.8 V (`--power 0.01`).
- "A bigger capacitor reduces the inductor current ripple." The current ripple is set by $$V$$, $$D$$, $$L$$ and $$f_s$$; the capacitor only turns it into a voltage ripple. Experiment 4 leaves $$\Delta i$$ unchanged while $$\Delta v$$ grows tenfold.
- "Doubling the frequency halves the output voltage ripple." It quarters it, because $$\Delta v = \Delta i/(8 C f_s)$$ and $$\Delta i$$ itself halves: experiment 1 goes from 5.00 mV to 1.25 mV.
- "A smaller time step always means a more accurate simulation." The step changed the ripple by 0.01 % here; stopping too early changed it by 1.5 %. Check convergence for every setting that matters, including reaching periodic steady state.

## AI Tutor Exercises

Give these prompts to an AI tutor; they make the tutor ask before it tells.

1. Diagnostic: "Before explaining anything, ask me to sketch the inductor current of a buck converter over two periods, mark where the switch is on, and say which element carries the current when it is off. Correct me only after I have answered."
2. Explain-back: "I will derive $$V = D V_g$$ from volt-second balance out loud. Interrupt only if I use an assumption I have not named, and at the end ask me which assumption fails first at light load."
3. Change one condition: "Ask me to predict, in numbers, what `--inductance 300e-6` will do to the ripple, the minimum current and the boundary load resistance before I run the lab, then make me explain any difference from the JSON."
4. Debug my work: "I believe the output ripple should be 10 mV at 100 kHz with 100 µF and 0.4 A of ripple current. Do not give me the value; question me about the shape of the capacitor current until I find my wrong factor."
5. Discontinuous conduction: "Ask me why the output of an open-loop buck rises at light load and what $$K$$ equals for `--load 120`, then have me check the DCM ratio formula against the simulation and explain why they agree to 0.01 % although the formula ignores the output ripple."

## Knowledge Assessment

1. (Numerical) A buck converter steps 48 V down to 12 V at 200 kHz with $$L = 47$$ µH. Find $$D$$, the inductor current ripple and the minimum load current for continuous conduction.
2. (Conceptual) Explain without equations why the output of an ideal buck in continuous conduction is independent of the load, and why that fails in discontinuous conduction.
3. (Numerical) For the design point of this lesson (24 V to 12 V, 100 kHz, 150 µH) the load is reduced to $$R = 240$$ Ω. Compute $$K$$, decide the conduction mode and find the output voltage.
4. (Numerical) With $$\Delta i = 0.4$$ A and $$f_s = 100$$ kHz, what capacitance limits the output voltage ripple to 1 mV? What happens to the start-up damping ratio when you install it?
5. (Conceptual) The simulation reports a current ripple of 0.40006 A against the analytical 0.4 A at both 200 and 2000 steps per period. Is the 0.014 % difference numerical error? Justify your answer.
6. (Conceptual and numerical) The default run peaks at 20.0 V and 10.6 A during start-up. Name two model assumptions that make this peak larger than in a well-designed real converter, and estimate it from the damping ratio $$\zeta$$.

Questions 1, 3 and 5 must be solved independently, without the tutor showing the method, before `pe.buck` is recorded as `demonstrated`; assisted answers count as `learning`, not as demonstrated.

<details><summary>Answers</summary>

1. $$D = 12/48 = 0.25$$; $$\Delta i = (48 - 12) \times 0.25 / (47 \times 10^{-6} \times 2 \times 10^5) = 9/9.4 = 0.957$$ A; the boundary load current is $$\Delta i/2 = 0.479$$ A, about 5.7 W at 12 V.
2. In CCM the inductor sees $$V_g - V$$ and $$-V$$ for fixed fractions of the period, so volt-second balance fixes $$V/V_g = D$$ however much current flows. In DCM the inductor voltage is zero while the diode blocks, and the fraction $$D_2$$ spent at $$-V$$ depends on the load current, so $$V$$ depends on $$R$$.
3. $$K = 2 \times 150 \times 10^{-6} \times 10^5 / 240 = 0.125 < 0.5$$: DCM. $$4K/D^2 = 2$$, $$M = 2/(1 + \sqrt{3}) = 0.732$$, $$V = 17.6$$ V; the lab gives 17.570 V with `--load 240`.
4. $$C = \Delta i/(8 f_s \Delta v) = 0.4 / (8 \times 10^5 \times 10^{-3}) = 500$$ µF. $$\zeta$$ falls from 0.128 to 0.057, so the open-loop start-up rings longer and overshoots more, about 84 % instead of 67 %.
5. No: a numerical error would shrink when the step is refined tenfold, and this one does not. The output is below its mean during the on-interval and above it during the off-interval, so both current slopes are slightly steeper than the small-ripple formula assumes.
6. No soft start (the full duty ratio is applied from the first period) and no losses (nothing damps the LC filter). With $$\zeta = 0.128$$ the overshoot is $$\exp(-\pi \zeta / \sqrt{1 - \zeta^2}) = 0.667$$, so the peak is $$12 \times 1.667 = 20.0$$ V, as simulated.

</details>

## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 6.622 — Power Electronics (Spring 2023)
- https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/
- Syllabus: https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/pages/syllabus/
- Lecture notes: https://ocw.mit.edu/courses/6-622-power-electronics-spring-2023/pages/lecture-notes/

Supplementary references:

- MIT 6.334 — Power Electronics (Spring 2007)
- https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/
- Syllabus: https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/syllabus/
- Lecture notes: https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/pages/lecture-notes/

Circuit prerequisites:

- MIT 6.002 — Circuits and Electronics (Spring 2007)
- https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/
- Syllabus: https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/syllabus/
- Lecture notes: https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/lecture-notes/

Relevant subjects:

- Steady-state analysis of switching converters: volt-second and charge balance, conversion ratios (6.622, 6.334).
- Inductor current ripple, output filter behaviour and continuous versus discontinuous conduction (6.622, 6.334).
- Circuit prerequisites: Kirchhoff's laws, first-order energy-storage elements, ideal switch and diode models (6.002).

This lesson has been independently developed by AIPE Academy with reference to the academic scope of the above courses. MIT OpenCourseWare is an external educational resource released under its own licence (generally CC BY-NC-SA 4.0). AIPE Academy is not affiliated with or endorsed by MIT.

### Other references

- R. W. Erickson and D. Maksimović, *Fundamentals of Power Electronics*, 3rd edition, Springer, 2020. Publisher record: https://link.springer.com/book/10.1007/978-3-030-43881-4 (no content reproduced).

## Further Learning

- Next in this track: [Buck converter: from principles to design](../../03-converters/buck-converter.md) (slug `buck-converter`), the advanced follow-on for `pe.buck` (component sizing, averaged models, feedback, layout, bench measurement); then the stage [Dynamics, transfer functions and control](../../04-modeling-and-control/README.md) (slug `dynamics-and-control`) for `pe.modelling` and `pe.control`.
- Companion lab: [Predict and check an ideal buck converter](../../03-converters/buck-open-lab.md) (slug `buck-open-lab`), the analytical exercise this lesson started from, in the [converters stage](../../03-converters/README.md).
- Cross-domain follow-on: [Solar PV fundamentals: from photons to the maximum power point](../../renewable-energy/solar-photovoltaics/solar-pv-fundamentals.md) (slug `solar-pv-fundamentals`, module `re.mppt`, Maximum power point tracking) uses a buck converter as the tracking stage: its CCM input resistance $$R/D^2$$ moves a panel's operating point.
- Related modules: `pe.boost` (Boost and buck-boost converters), `pe.losses` (Switching losses and efficiency), `pe.passives` (Passive and magnetic components), `pe.devices` (Power semiconductor devices) and `pe.simulation` (Simulation: checking a result against circuit simulators such as ngspice).
- Validation status: the lab is an analytical and numerical teaching model not yet compared with hardware by any AIPE Academy lesson; the follow-on tutorial's bench section describes the intended comparison and `pe.simulation` covers solver settings and steady-state windows.
