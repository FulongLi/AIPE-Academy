# Three-phase system fundamentals: balanced operation, power and the per-unit system

> Module: `ps.three-phase` · Also covers: `ps.per-unit` · Level: undergraduate · Status: available
> Suggested time: 120 minutes · Labs: `labs/power-systems/three_phase.py`

Almost every grid above a few kilowatts is a three-phase system. This lesson explains why three displaced voltages deliver smoother power with less copper than one, how phase and line quantities, wye and delta connections, real, reactive and apparent power and power-factor correction fit together, and how the per-unit system puts a 400 V supply and an 11 kV feeder on the same footing, checking every number with a reproducible Python lab.

## Learning Objectives

After this lesson the learner can:

- explain why a balanced three-phase system delivers constant instantaneous power although each phase pulsates, and why it needs fewer conductors than three single-phase circuits;
- convert between phase and line quantities for wye and delta connections, with the $$\sqrt{3}$$ factors and 30° shifts, and replace a balanced delta by its wye equivalent;
- calculate the real, reactive and apparent power and the power factor of a balanced load, label it lagging or leading, and size wye-connected shunt capacitors that raise it to a target;
- choose a three-phase per-unit base, derive the impedance and current bases that follow from it, convert impedances and powers to per-unit, and explain why per-unit values do not change across an ideal transformer;
- predict the effect of a parameter change before running the lab, and tell an analytical result from a sampled numerical one.

## Prerequisites

- DC circuit analysis: Ohm's law, Kirchhoff's laws, series and parallel combinations (module `f.dc-circuits`, lesson `dc-circuit-fundamentals`).
- AC basics: sinusoids, RMS values, complex numbers, phasors and impedance (module `f.ac`); phasors and impedance are recapped at the start of Fundamental Principles.
- Trigonometry: cosine, tangent, their inverses and one product-to-sum identity.
- Running a Python script and reading JSON (module `f.computation`).

## Physical Intuition

**Power that breathes.** The power absorbed by a single-phase heater peaks and falls to zero twice every cycle, 100 times a second at 50 Hz. A motor fed this way receives a pulsating torque. Feed three identical heaters from three voltages a third of a cycle apart and, when one is at its dip, the other two are near their peaks: the sum is flat, like three pistons on a crankshaft with throws 120° apart.

**Copper.** Three single-phase circuits need six wires. Join the three return wires and their currents share one conductor. Prediction question: if the three currents have equal magnitude and are 120° apart, what flows in that shared return? The answer, zero, is derived below: three conductors do the work of six.

**Two ways to connect.** A load is connected in **wye** (star, Y), one end of each impedance joined at a neutral point, or in **delta** (Δ), the three impedances forming a triangle between the lines (British and IEC usage is star; this lesson says wye to match the lab's keys). Second prediction question: the same impedances are reconnected from wye to delta; does the load draw more or less power? The lab shows a factor of exactly three.

```text
Wye (star)                            Delta (mesh)

 a o----[ Z ]----+                    a o--------+----------+
                 |                             [ Z ]      [ Z ]
 b o----[ Z ]----+ n (neutral)                   |          |
                 |                    b o--------+--[ Z ]---+--o c
 c o----[ Z ]----+
 V across each Z = V_line / sqrt(3)   V across each Z = V_line
 I in each Z     = I_line             I in each Z     = I_line / sqrt(3)
```

**Reactive power.** An inductor stores energy in its magnetic field for part of each cycle and returns it in the next: the energy sloshes between source and load, averages to zero and does no work, yet the current carrying it heats every conductor on the way; reactive power $$Q$$ measures the exchange. A capacitor stores energy with the opposite timing, so a capacitor beside an inductive load exchanges the energy locally: power-factor correction. Per-unit is simpler still: divide every quantity by a base chosen for its voltage level, and a transformer whose bases follow its turns ratio disappears from the circuit.

## Fundamental Principles

**Phasor recap.** A steady sinusoid $$v(t) = \sqrt{2}\,V\cos(\omega t + \theta)$$ with RMS value $$V$$ (V), angular frequency $$\omega = 2\pi f$$ (rad/s) at supply frequency $$f$$ (Hz) and angle $$\theta$$ (degrees here) is represented by the phasor $$\mathbf{V} = V\angle\theta$$. An impedance $$\mathbf{Z} = R + jX$$ (Ω), with resistance $$R$$ (Ω) and reactance $$X$$ (Ω), gives $$\mathbf{I} = \mathbf{V}/\mathbf{Z}$$: the magnitude is divided by $$|\mathbf{Z}| = \sqrt{R^2 + X^2}$$ and the impedance angle $$\varphi = \operatorname{atan2}(X, R)$$, equal to $$\arctan(X/R)$$ for $$R > 0$$ and to $$\pm 90^\circ$$ for $$R = 0$$, is subtracted. The lab does this algebra with Python's `cmath` and accepts only $$R \geq 0$$, a passive load.

**Balanced source.** Three line-to-neutral voltages of equal RMS magnitude $$V_\mathrm{ph}$$ (V), displaced by 120°:

$$
\mathbf{V}_{an} = V_\mathrm{ph}\angle 0^\circ, \qquad
\mathbf{V}_{bn} = V_\mathrm{ph}\angle{-120^\circ}, \qquad
\mathbf{V}_{cn} = V_\mathrm{ph}\angle{+120^\circ}.
$$

The order in which the phases peak, a then b then c, is the positive (abc) sequence; swapping two phases gives the negative (acb) sequence, which reverses a three-phase motor.

**Phase and line quantities.** A *phase* quantity belongs to one element of the source or load; a *line* quantity belongs to the conductors joining them: the line-to-line voltage $$V_L$$ (V) and the line current $$I_L$$ (A). With phase current $$I_\mathrm{ph}$$ (A): in a wye, $$V_L = \sqrt{3}\,V_\mathrm{ph}$$ and $$I_L = I_\mathrm{ph}$$; in a delta, $$V_L = V_\mathrm{ph}$$ and $$I_L = \sqrt{3}\,I_\mathrm{ph}$$. The line quantity is shifted 30° from the related phase quantity.

**Complex power.** For a load element with RMS phasors $$\mathbf{V}$$ and $$\mathbf{I}$$,

$$
\mathbf{S} = \mathbf{V}\,\mathbf{I}^{*} = P + jQ,
$$

where $$\mathbf{I}^{*}$$ is the complex conjugate. $$P$$ (W) is the real power, the average rate of energy conversion; $$Q$$ (var, volt-ampere reactive) is the reactive power; the apparent power $$S = |\mathbf{S}| = VI$$ (VA) sizes conductors and transformers. The power factor is $$\mathrm{pf} = P/S = \cos\varphi$$, with $$\varphi$$ the angle between voltage and current. In this load convention $$Q > 0$$ means an inductive load whose current lags the voltage, a *lagging* power factor; $$Q < 0$$ means a capacitive load and a *leading* power factor.

**Three-phase power.** Each phase of a balanced system carries the same complex power, so

$$
S_{3\phi} = 3\,V_\mathrm{ph} I_\mathrm{ph} = \sqrt{3}\,V_L I_L
$$

for wye and delta alike. The instantaneous power $$p(t) = v(t)\,i(t)$$ (W) of one phase pulsates; the sum over three balanced phases is constant and equal to $$P_{3\phi}$$.

**Per-unit system.** A per-unit value is an actual value divided by a base of the same kind, $$x_\mathrm{pu} = x/x_\mathrm{base}$$. Two bases are chosen freely, the three-phase apparent-power base $$S_\mathrm{base}$$ (VA) and the line-to-line voltage base $$V_\mathrm{base}$$ (V); the impedance base $$Z_\mathrm{base}$$ (Ω), current base $$I_\mathrm{base}$$ (A) and phase-voltage base $$V_\mathrm{ph,base}$$ (V) follow:

$$
Z_\mathrm{base} = \frac{V_\mathrm{base}^2}{S_\mathrm{base}}, \qquad
I_\mathrm{base} = \frac{S_\mathrm{base}}{\sqrt{3}\,V_\mathrm{base}}, \qquad
V_\mathrm{ph,base} = \frac{V_\mathrm{base}}{\sqrt{3}}.
$$

Because the phase-voltage base carries the same $$\sqrt{3}$$ as the phase voltage, line-to-line and line-to-neutral voltages share one per-unit value and $$\mathbf{S}_\mathrm{pu} = \mathbf{V}_\mathrm{pu}\mathbf{I}_\mathrm{pu}^{*}$$ with no factor of three.

**What is idealised.** Sinusoidal steady state at one frequency; an ideal source with zero internal and line impedance; three identical, linear impedances at constant temperature; lossless correction capacitors; an ideal transformer in the per-unit example. Line and transformer impedance, the many-bus network and unbalance belong to later modules (Further Learning).

## Mathematical Derivations

### Line voltage of a wye source

With $$\mathbf{V}_{bn} = V_\mathrm{ph}\left(-\tfrac{1}{2} - j\tfrac{\sqrt{3}}{2}\right)$$,

$$
\mathbf{V}_{ab} = \mathbf{V}_{an} - \mathbf{V}_{bn}
= V_\mathrm{ph}\left(\tfrac{3}{2} + j\tfrac{\sqrt{3}}{2}\right)
= \sqrt{3}\,V_\mathrm{ph}\angle 30^\circ .
$$

The magnitude is $$\sqrt{(3/2)^2 + (\sqrt{3}/2)^2} = \sqrt{3}$$ times the phase voltage and the line voltage leads $$\mathbf{V}_{an}$$ by 30°; by symmetry $$\mathbf{V}_{bc} = \sqrt{3}\,V_\mathrm{ph}\angle{-90^\circ}$$ and $$\mathbf{V}_{ca} = \sqrt{3}\,V_\mathrm{ph}\angle 150^\circ$$.

### The neutral carries no current

For a balanced wye load of $$\mathbf{Z}$$ per phase, $$\mathbf{I}_k = \mathbf{V}_{kn}/\mathbf{Z}$$ and

$$
\mathbf{I}_a + \mathbf{I}_b + \mathbf{I}_c
= \frac{V_\mathrm{ph}}{\mathbf{Z}}\left(1 + 1\angle{-120^\circ} + 1\angle{120^\circ}\right) = 0,
$$

because the three unit phasors form an equilateral triangle centred on the origin: the neutral can be omitted, and three conductors replace six.

### Line current of a delta load

With branch currents $$\mathbf{I}_{ab} = \mathbf{V}_{ab}/\mathbf{Z}$$ and so on, Kirchhoff's current law at the corner joined to line a gives

$$
\mathbf{I}_a = \mathbf{I}_{ab} - \mathbf{I}_{ca}
= \mathbf{I}_{ab}\left(1 - 1\angle 120^\circ\right)
= \sqrt{3}\,\mathbf{I}_{ab}\angle{-30^\circ},
$$

using $$\mathbf{I}_{ca} = \mathbf{I}_{ab}\angle 120^\circ$$ for a balanced set: the line current is $$\sqrt{3}$$ times the branch current and lags it by 30°.

### Delta to wye equivalence

For a delta of $$\mathbf{Z}_\Delta$$ (Ω) per branch, substituting the branch voltages gives $$\mathbf{I}_a = (\mathbf{V}_{ab} - \mathbf{V}_{ca})/\mathbf{Z}_\Delta$$, and $$\mathbf{V}_{ab} - \mathbf{V}_{ca} = 2\mathbf{V}_{an} - \mathbf{V}_{bn} - \mathbf{V}_{cn} = 3\mathbf{V}_{an}$$ because the phase voltages sum to zero. Hence

$$
\mathbf{I}_a = \frac{3\,\mathbf{V}_{an}}{\mathbf{Z}_\Delta} = \frac{\mathbf{V}_{an}}{\mathbf{Z}_\Delta / 3}.
$$

The supply cannot distinguish a delta of $$\mathbf{Z}_\Delta$$ per branch from a wye of $$\mathbf{Z}_Y = \mathbf{Z}_\Delta/3$$ (Ω) per phase: line currents and total power are identical, so the same impedance in delta draws three times its wye power.

### Real, reactive and apparent power of an impedance

With $$\mathbf{I} = \mathbf{V}/\mathbf{Z}$$ the per-phase complex power is

$$
\mathbf{S} = \mathbf{V}\left(\frac{\mathbf{V}}{\mathbf{Z}}\right)^{*} = \frac{V^2}{\mathbf{Z}^{*}} = \frac{V^2 (R + jX)}{R^2 + X^2},
\qquad P = I^2 R, \quad Q = I^2 X .
$$

$$P$$, $$Q$$ and $$S$$ form the power triangle, $$S^2 = P^2 + Q^2$$, with $$\cos\varphi = P/S$$ and $$\tan\varphi = Q/P$$; $$\varphi$$ equals the impedance angle, so a passive load with positive reactance always has a lagging power factor.

### Instantaneous power

For phase a, $$v_a(t) = \sqrt{2}\,V\cos\omega t$$ and $$i_a(t) = \sqrt{2}\,I\cos(\omega t - \varphi)$$ with per-phase RMS values $$V$$ and $$I$$. The identity $$\cos A\cos B = \tfrac{1}{2}[\cos(A-B) + \cos(A+B)]$$ gives

$$
p_a(t) = VI\cos\varphi + VI\cos(2\omega t - \varphi).
$$

The first term is the average power; the second pulsates at twice the supply frequency between $$-VI$$ and $$+VI$$, so $$p_a(t)$$ swings between $$VI(\cos\varphi - 1)$$ and $$VI(\cos\varphi + 1)$$ and is negative for part of each cycle whenever $$\varphi \neq 0$$: energy flowing back to the source. Phases b and c have the same form with $$2\omega t$$ replaced by $$2\omega t \mp 240^\circ$$; the three pulsating terms are a balanced set at frequency $$2\omega$$ and cancel at every instant:

$$
p_a + p_b + p_c = 3\,VI\cos\varphi = P_{3\phi}.
$$

### Power-factor correction with shunt capacitors

A load drawing $$P$$ at power factor $$\cos\varphi_1$$ absorbs $$Q_1 = P\tan\varphi_1$$. Parallel capacitors leave $$P$$ unchanged and supply $$Q_C$$, so the supply sees $$Q_2 = Q_1 - Q_C$$. To reach a target $$\cos\varphi_2$$,

$$
Q_C = P\left(\tan\varphi_1 - \tan\varphi_2\right).
$$

A capacitor $$C$$ (F) across RMS voltage $$V_C$$ (V) supplies $$\omega C V_C^2$$ var. Three wye-connected capacitors each see $$V_L/\sqrt{3}$$ and each supplies $$Q_C/3$$, so

$$
C_Y = \frac{Q_C/3}{\omega (V_L/\sqrt{3})^2} = \frac{Q_C}{\omega V_L^2},
\qquad
C_\Delta = \frac{Q_C/3}{\omega V_L^2} = \frac{C_Y}{3}.
$$

The delta connection needs one third of the capacitance, but each capacitor must withstand the full line voltage.

### Per-unit bases and the transformer

Dividing the phase-voltage base by the current base recovers $$Z_\mathrm{base} = (V_\mathrm{base}/\sqrt{3})(\sqrt{3}\,V_\mathrm{base}/S_\mathrm{base}) = V_\mathrm{base}^2/S_\mathrm{base}$$. An impedance quoted on one base moves to another with

$$
Z_\mathrm{pu,new} = Z_\mathrm{pu,old}\,\frac{S_\mathrm{base,new}}{S_\mathrm{base,old}}\left(\frac{V_\mathrm{base,old}}{V_\mathrm{base,new}}\right)^2 .
$$

For an ideal transformer of ratio $$a = V_1/V_2$$, an impedance $$\mathbf{Z}_2$$ on the low-voltage side appears from side 1 as $$a^2\mathbf{Z}_2$$. With the same $$S_\mathrm{base}$$ on both sides and $$V_\mathrm{base,1}/V_\mathrm{base,2} = a$$, $$Z_\mathrm{base,1} = a^2 Z_\mathrm{base,2}$$ and

$$
\frac{a^2 \mathbf{Z}_2}{Z_\mathrm{base,1}} = \frac{a^2 \mathbf{Z}_2}{a^2 Z_\mathrm{base,2}} = \frac{\mathbf{Z}_2}{Z_\mathrm{base,2}} .
$$

The per-unit impedance is the same from either side: the ideal transformer becomes a plain connection in the per-unit diagram.

## Worked Examples

All numbers are the lab's default output, rounded for reading: analytical results of the idealised model, not measurements.

### Example 1: a balanced wye load

A 400 V (line-to-line), 50 Hz supply feeds a wye load of $$\mathbf{Z} = 10 + j5\ \Omega$$ per phase.

1. Phase voltage: $$V_\mathrm{ph} = 400/\sqrt{3} = 230.94\ \mathrm{V}$$.
2. Impedance: $$|\mathbf{Z}| = \sqrt{10^2 + 5^2} = 11.180\ \Omega$$, $$\varphi = \arctan(5/10) = 26.565^\circ$$.
3. Current: $$I_\mathrm{ph} = I_L = 230.94/11.180 = 20.656\ \mathrm{A}$$, lagging by 26.565°; $$\mathbf{I}_b$$ and $$\mathbf{I}_c$$ follow 120° behind and ahead, and $$\mathbf{V}_{ab} = 400\angle 30^\circ$$ V.
4. Per phase: $$P = I^2 R = 20.656^2\times 10 = 4266.67\ \mathrm{W}$$, $$Q = I^2 X = 2133.33\ \mathrm{var}$$, $$S = 4770.28\ \mathrm{VA}$$.
5. Totals: $$P_{3\phi} = 12\,800\ \mathrm{W}$$, $$Q_{3\phi} = 6400\ \mathrm{var}$$, $$S_{3\phi} = 14\,310.84\ \mathrm{VA}$$; power factor $$12\,800/14\,310.84 = 0.8944$$ lagging.

Sanity checks: $$\sqrt{3}\times 400\times 20.656 = 14\,310.8\ \mathrm{VA}$$ agrees with $$3V_\mathrm{ph}I_\mathrm{ph}$$, and $$P_{3\phi} = 3V_\mathrm{ph}^2 R/|\mathbf{Z}|^2 = 3\times 53\,333\times 10/125 = 12\,800\ \mathrm{W}$$ exactly.

### Example 2: the same impedance in delta, and its wye equivalent

In delta each branch sees 400 V, so $$I_\mathrm{ph} = 400/11.180 = 35.777\ \mathrm{A}$$ and $$I_L = \sqrt{3}\times 35.777 = 61.968\ \mathrm{A}$$. The lab gives $$\mathbf{I}_{ab} = 35.777\angle 3.435^\circ$$ A and $$\mathbf{I}_a = 61.968\angle{-26.565^\circ}$$ A, 30° behind the branch current. Totals: $$P_{3\phi} = 3\times 400^2\times 10/125 = 38\,400\ \mathrm{W}$$ and $$Q_{3\phi} = 19\,200\ \mathrm{var}$$, three times the wye values. The wye equivalent $$\mathbf{Z}_Y = \mathbf{Z}_\Delta/3 = 3.3333 + j1.6667\ \Omega$$ gives $$I_L = 230.94/3.7268 = 61.968\ \mathrm{A}$$ and $$P_{3\phi} = 38\,400\ \mathrm{W}$$, identical to the delta.

### Example 3: pulsating phases, constant total

With $$VI = 230.94\times 20.656 = 4770.28\ \mathrm{VA}$$ and $$\varphi = 26.565^\circ$$, phase a pulsates at 100 Hz between $$4770.28\times(0.8944 - 1) = -503.61\ \mathrm{W}$$ and $$4770.28\times 1.8944 = 9036.95\ \mathrm{W}$$, while the total is $$3\times 4770.28\times 0.8944 = 12\,800\ \mathrm{W}$$ at every instant. Sampling one cycle at 360 points, the lab reports a total between 12 799.999999999993 W and 12 800.000000000013 W, a spread of order $$10^{-11}$$ W, about $$10^{-15}$$ of the apparent power: floating-point rounding, not physics. The last digits are the residue of the platform's cosine routine and summation order, repeatable only on one platform and Python build, and do not shrink with more samples. The sampled phase-a extremes, −503.38 W and 9036.71 W, lie just inside the analytical ones because no sample falls exactly on a peak; they converge as `--points` grows.

### Example 4: correcting the power factor to 0.95

The load draws $$P = 12\,800\ \mathrm{W}$$ at 0.8944 lagging, so $$Q_1 = 6400\ \mathrm{var}$$. At the target, $$\tan(\arccos 0.95) = 0.3287$$ and $$Q_2 = 12\,800\times 0.3287 = 4207.16\ \mathrm{var}$$, so $$Q_C = 6400 - 4207.16 = 2192.84\ \mathrm{var}$$, or 730.95 var per phase. With $$\omega = 2\pi\times 50 = 314.16\ \mathrm{rad/s}$$:

$$
C_Y = \frac{2192.84}{314.16\times 400^2} = 43.6\ \mu\mathrm{F} \ \text{per phase at 230.94 V},
\qquad
C_\Delta = \frac{C_Y}{3} = 14.5\ \mu\mathrm{F} \ \text{per phase at 400 V}.
$$

Each wye capacitor carries $$730.95/230.94 = 3.165\ \mathrm{A}$$. The apparent power falls from 14 310.84 VA to $$12\,800/0.95 = 13\,473.68\ \mathrm{VA}$$ and the line current from 20.656 A to 19.448 A, a 5.85 % reduction, while $$P$$ is unchanged.

### Example 5: per-unit on a 100 kVA, 11 kV base

With $$S_\mathrm{base} = 100\ \mathrm{kVA}$$ and $$V_\mathrm{base} = 11\ \mathrm{kV}$$: $$Z_\mathrm{base} = 11\,000^2/100\,000 = 1210\ \Omega$$, $$I_\mathrm{base} = 100\,000/(\sqrt{3}\times 11\,000) = 5.249\ \mathrm{A}$$, $$V_\mathrm{ph,base} = 6350.85\ \mathrm{V}$$.
Now place the load of Example 1 on the 400 V side of an ideal 11 kV/400 V transformer (ratio 27.5). On the 400 V base ($$Z_\mathrm{base} = 400^2/100\,000 = 1.6\ \Omega$$), $$\mathbf{Z}_\mathrm{pu} = (10 + j5)/1.6 = 6.25 + j3.125$$ pu. Referred to the 11 kV side the ohmic impedance is $$27.5^2\times(10 + j5) = 7562.5 + j3781.25\ \Omega$$, which on the 1210 Ω base is again $$6.25 + j3.125$$ pu. The load's complex power is $$(12\,800 + j6400)/100\,000 = 0.128 + j0.064$$ pu and its current $$20.656/144.34 = 0.1431$$ pu on the 400 V side ($$I_\mathrm{base} = 144.34\ \mathrm{A}$$) and $$0.7511/5.249 = 0.1431$$ pu on the 11 kV side. Check: at 1.0 pu voltage, $$\mathbf{S}_\mathrm{pu} = 1/\mathbf{Z}_\mathrm{pu}^{*} = 1/(6.25 - j3.125) = 0.128 + j0.064$$ pu and $$|\mathbf{I}_\mathrm{pu}| = |\mathbf{S}_\mathrm{pu}| = 0.1431$$, with no $$\sqrt{3}$$ anywhere.

## Numerical or Simulation Lab

- Lab script: [`labs/power-systems/three_phase.py`](../../../labs/power-systems/three_phase.py), Python 3.10+, standard library only; matplotlib is optional (`--plot`) and its absence is reported on standard error, not fatal.
- Inputs (SI units, listed by `--help`): line-to-line voltage in V, resistance (non-negative) and reactance per phase in Ω (negative reactance is capacitive), frequency in Hz, power-factor target in (0, 1], the $$S$$ and $$V$$ bases in VA and V, and samples per cycle; the defaults are the lesson example.
- Assumptions: those of Fundamental Principles, with $$\mathbf{V}_{an}$$ as angle reference and an ideal transformer between the primary and load-side per-unit bases.
- Outputs: one JSON document with the sections `inputs`, `wye_load`, `delta_load`, `delta_to_wye_equivalent`, `instantaneous_power`, `power_factor_correction`, `per_unit` and `balance_check`; physical quantities are `{"value": ..., "unit": ...}`; every result section except `inputs` carries `model`, `validation_status`, `assumptions` and `limitations`, and a not-applicable correction record adds `status` and `reason`.

Commands (repository root):

```text
python labs/power-systems/three_phase.py
python labs/power-systems/three_phase.py --json
python labs/power-systems/three_phase.py --v-line 400 --resistance 10 --reactance 5 --frequency 50 --pf-target 0.95 --s-base 100000 --v-base 11000
python labs/power-systems/three_phase.py --plot --out three_phase.png
python -m unittest tests.test_lab_three_phase -v
```

Expected values for the default case, as key paths into the JSON:

```text
wye_load.phase_voltage_rms.value                              230.94010767585033      V
wye_load.line_current_rms.value                                20.655911179772893      A
wye_load.phasors.line_currents.a.angle.value                  -26.565051177            deg
wye_load.total.real_power.value                             12800.000000000004        W
wye_load.total.reactive_power.value                          6400.000000000002        var
wye_load.total.apparent_power.value                         14310.835055998657        VA
wye_load.power_factor.value                                     0.894427190999916      1   (power_factor_type "lagging")
delta_load.line_current_rms.value                              61.967733539318665      A
delta_load.total.real_power.value                           38400.0                   W
delta_to_wye_equivalent.z_wye_equivalent (real, imag)           3.3333, 1.6667         Ohm
instantaneous_power.total.sampled_min.value                 12799.999999999993        W   (rounding residue; last digits vary by platform)
instantaneous_power.total.sampled_max.value                 12800.000000000013        W   (as above)
power_factor_correction.capacitor_reactive_power_total.value 2192.8434537105486       var
power_factor_correction.capacitance_per_phase_wye.value         4.3625234385592196e-05 F
power_factor_correction.line_current_after.value               19.447588014808453      A
per_unit.primary_base.z_base.value                           1210.0                   Ohm
per_unit.primary_base.i_base.value                              5.2486388108147795     A
per_unit.load_impedance_pu_on_primary_base (real, imag)         6.25, 3.125            pu
per_unit.load_complex_power_pu (real, imag)                     0.128, 0.064           pu
balance_check.balanced / phase_sequence                      true / "abc (positive sequence)"
```

Validation: the script raises `ValueError` (exit code 2, `error: ...` on standard error) for a non-finite or non-positive voltage, frequency or base, a negative resistance, a zero impedance, inputs outside the model's numerical range (above $$10^{12}$$ in SI units or so small that the power underflows to zero), a power-factor target outside (0, 1] and a sample count outside 4 to $$10^{6}$$. A target below the load's existing power factor is not an error: `power_factor_correction` reports `"status": "not-applicable"` with the reason (likewise for a unity or leading load); only `pf_correction_capacitance`, called directly with a lower target, raises `ValueError`. `check_balanced` accepts only three finite phasors and reports an unbalanced set, with its phase sequence and error size, rather than averaging it; `complex_power_from_phasors` then refuses the balanced-set shortcut. No output contains NaN or infinity.

Validation status: every section except `instantaneous_power` is an analytical example; that section is a numerical simulation whose extremes depend on the sample count. Nothing here is hardware-validated: the lab is an analytical/numerical teaching model, not validated hardware performance. For reproducibility record the command, inputs, Python version (`python_version` in the JSON) and output; the calculation is deterministic (no randomness, no clock), and across platforms only the last digits of the sampled instantaneous-power extremes may differ.

## Parameter Exploration

Change one input at a time; write your prediction down before running the command.

1. **Remove the reactance** (`--reactance 0`). Predict the power factor, $$Q$$, the current and whether the phase power ever goes negative. Result: pf = 1 (unity), $$Q = 0$$, $$I = 23.094\ \mathrm{A}$$, $$P = 16\,000\ \mathrm{W}$$, phase-a minimum 0 W, correction `not-applicable`. The current rises because $$|\mathbf{Z}|$$ fell from 11.18 Ω to 10 Ω.
2. **Make the load capacitive** (`--reactance -5`). Predict the sign of $$Q$$ and the current angle. Result: $$Q = -6400\ \mathrm{var}$$, leading, $$\mathbf{I}_a$$ at +26.565°, the same magnitudes as the default; correction not applicable because capacitors would make a leading load worse.
3. **Double the voltage** (`--v-line 800`). Predict how $$P$$, $$I$$, $$Q_C$$ and $$C_Y$$ change. Result: $$P = 51\,200\ \mathrm{W}$$ (four times), $$I = 41.312\ \mathrm{A}$$ (twice), $$Q_C = 8771.37\ \mathrm{var}$$ (four times), but $$C_Y = 43.6\ \mu\mathrm{F}$$ unchanged: the reactive power to be supplied and the reactive power a fixed capacitor supplies both grow with $$V^2$$.
4. **Change the frequency** (`--frequency 60`). Result: $$P$$, $$Q$$ and the currents are unchanged and $$C_Y$$ falls to 36.35 µF, the ratio 50/60. A model limit: the lab takes the reactance as given, whereas a real coil of inductance $$L$$ (H) has $$X = \omega L$$, which would rise by 20 % at 60 Hz.
5. **Aim higher** (`--pf-target 1.0`, then `0.98`, then `0.9`). Predict whether the capacitance grows in proportion to the target. Result: $$C_Y = 127.3$$, 75.6 and 4.0 µF; the line current falls to 18.475, 18.852 and 20.528 A (10.6 %, 8.7 % and 0.6 % reductions). The last hundredths cost far more capacitance per ampere saved, hence practical targets near 0.95.

## Common Misconceptions

- **"The line voltage of a wye is three times the phase voltage because there are three phases."** The factor is $$\sqrt{3}$$: the line voltage is the vector difference of two phase voltages 120° apart. Check: $$2\times 230.94\times\cos 30^\circ = 400\ \mathrm{V}$$.
- **"Phase power and line power are different kinds of power."** They are one total in different variables; $$3V_\mathrm{ph}I_\mathrm{ph}$$ and $$\sqrt{3}V_L I_L$$ are equal for wye and delta alike. Check: in the default JSON, `wye_load.total.apparent_power` (14 310.84 VA) equals both $$3\times 230.94\times 20.656$$ and $$\sqrt{3}\times 400\times 20.656$$.
- **"Reactive power is wasted energy, and capacitors cut the energy I pay for."** Reactive power is exchanged, not consumed; the energy meter registers $$P$$, which capacitors do not change. They only remove the extra $$I^2R$$ heating of the larger current. Check: Example 4 changes $$Q$$ and $$I$$ but leaves $$P$$ at 12 800 W.
- **"A leading power factor is better than a lagging one."** Both mean reactive current the supply must carry; the sign only says which way it flows. Check: `--reactance -5` gives the same apparent power and line current as the inductive case.
- **"A per-unit impedance of 0.04 is 0.04 ohms."** It is 0.04 of $$Z_\mathrm{base}$$: 48.4 Ω on an 11 kV, 100 kVA base and 0.064 Ω on a 400 V, 100 kVA base. Check: with `--s-base 50000` the same load becomes $$3.125 + j1.5625$$ pu on a 2420 Ω base.
- **"The three-phase formulas work for any three voltages."** They assume balance. Check: give `check_balanced` a set with one magnitude 10 % low and it reports `balanced: false`, and `complex_power_from_phasors` refuses the balanced shortcut.

## AI Tutor Exercises

Give these prompts to an AI tutor; each makes the tutor ask before it tells (`prompts/tutor-guide.md`).

1. **Diagnostic.** "Before explaining anything, ask me to sketch the three phase-voltage phasors of a balanced wye source and to draw $$\mathbf{V}_{ab}$$ as a difference of two of them. Ask me to predict its magnitude and angle relative to $$\mathbf{V}_{an}$$ before showing the derivation. If my factor is 3 instead of $$\sqrt{3}$$, ask what the two phasors would have to look like for 3 to be right."
2. **Explain-back.** "I will explain, in my own words and without equations, why the total instantaneous power of a balanced three-phase load is constant although each phase pulsates. Then ask me one question that tests whether I understand why the three pulsating terms cancel; do not correct me until I have answered it."
3. **Change one condition.** "Using the lab's default example, ask me to predict, before running anything, what happens to the per-phase capacitance needed for 0.95 power factor if the supply voltage doubles. After I commit, have me run `--v-line 800`; if I was wrong, ask which quantity I assumed stayed fixed."
4. **Debug my work.** "I calculated the delta line current of Example 2 as 35.777 A and the total power as 12 800 W. Do not give me the right numbers; ask me which voltage I applied across each branch and which current I called the line current, until I find both errors myself."

## Knowledge Assessment

Questions 1 and 2 are conceptual; 3 to 6 are numerical. To record this module as `demonstrated`, a learner must solve questions 3, 4 and 6 independently, with fresh numbers if the answers below have been seen; assisted answers do not count as demonstrated.

1. Give two reasons why three-phase systems are preferred to single-phase systems for delivering power, with one sentence of explanation each.
2. A wye-connected load and a delta-connected load draw the same line current from the same supply. How are their per-phase impedances related, and which load's elements carry the larger current?
3. A balanced wye load of $$8 + j6\ \Omega$$ per phase is connected to a 400 V, 50 Hz supply. Find the line current, the total $$P$$, $$Q$$ and $$S$$, and the power factor with its lagging/leading label.
4. The load of question 3 is to be corrected to 0.95 lagging with wye-connected capacitors. Find $$Q_C$$, the capacitance per phase and the line current after correction.
5. A delta-connected load of $$30 + j15\ \Omega$$ per branch is fed from the same 400 V supply as the default example. Without solving the delta directly, find its line current and total real power.
6. A 200 kVA, 11 kV/400 V transformer has a per-unit impedance of 0.05 on its own rating. Find its impedance in ohms seen from each side and its per-unit impedance on a 100 kVA system base.

<details><summary>Answers</summary>

1. Constant total instantaneous power (smooth torque, no 100 Hz pulsation) and conductor economy (three conductors replace six because the balanced line currents sum to zero).
2. For equal line currents $$\mathbf{Z}_\Delta = 3\mathbf{Z}_Y$$. The delta elements each carry $$I_L/\sqrt{3}$$ while the wye elements carry $$I_L$$, so the wye elements carry the larger current and see the smaller voltage.
3. $$|\mathbf{Z}| = 10\ \Omega$$, $$\varphi = 36.87^\circ$$, $$V_\mathrm{ph} = 230.94\ \mathrm{V}$$, $$I_L = 23.094\ \mathrm{A}$$; $$P = 3\times 23.094^2\times 8 = 12\,800\ \mathrm{W}$$, $$Q = 9600\ \mathrm{var}$$, $$S = 16\,000\ \mathrm{VA}$$; pf = 0.80 lagging. Check with `--resistance 8 --reactance 6`.
4. $$Q_1 = 9600\ \mathrm{var}$$; $$Q_2 = 12\,800\times\tan(\arccos 0.95) = 4207.16\ \mathrm{var}$$; $$Q_C = 5392.84\ \mathrm{var}$$; $$C_Y = 5392.84/(314.16\times 400^2) = 107.3\ \mu\mathrm{F}$$ per phase; line current after correction $$13\,473.68/(\sqrt{3}\times 400) = 19.448\ \mathrm{A}$$, down from 23.094 A.
5. Wye equivalent $$\mathbf{Z}_Y = 10 + j5\ \Omega$$, the default example: $$I_L = 20.656\ \mathrm{A}$$ and $$P = 12\,800\ \mathrm{W}$$.
6. Own bases $$Z_\mathrm{base,HV} = 11\,000^2/200\,000 = 605\ \Omega$$ and $$Z_\mathrm{base,LV} = 400^2/200\,000 = 0.8\ \Omega$$, so $$30.25\ \Omega$$ from the 11 kV side and $$0.04\ \Omega$$ from the 400 V side (ratio $$27.5^2 = 756.25$$, as it must be). On a 100 kVA system base: $$0.05\times 100/200 = 0.025$$ pu.

</details>

## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 6.061 — Introduction to Electric Power Systems (Spring 2011)
- https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/
- Syllabus: https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/syllabus/
- Readings: https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/pages/readings/

AC circuit prerequisites (phasors, impedance):

- MIT 6.002 — Circuits and Electronics (Spring 2007)
- https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/
- Syllabus: https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/syllabus/
- Lecture notes: https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/lecture-notes/

Relevant subjects:

- Balanced three-phase circuits, phase and line quantities, wye and delta connections
- Complex, real and reactive power and the power factor
- Per-unit normalisation of power-system quantities
- Sinusoidal steady-state analysis with phasors and impedance (6.002)

This lesson has been independently developed by AIPE Academy with reference to the academic scope of the above courses. MIT OpenCourseWare is an external educational resource released under its own licence (generally CC BY-NC-SA 4.0). AIPE Academy is not affiliated with or endorsed by MIT.

### Other references

- IEC 60038:2009, *IEC standard voltages*, IEC, edition 7 (consolidated with Amendment 1 in 2021): the standard whose Table 1 lists 230/400 V at 50 Hz, the nominal low-voltage three-phase system behind this lesson's numbers. Publisher record: https://webstore.iec.ch/en/publication/153 (no content reproduced).
- The verified course metadata used above is recorded in [`references/mit-ocw-catalogue.json`](../../../references/mit-ocw-catalogue.json).

## Further Learning

- Next available lesson (the catalogue's `next`): [Solar PV fundamentals](../../renewable-energy/solar-photovoltaics/solar-pv-fundamentals.md) (slug `solar-pv-fundamentals`, module `re.pv`); its planned follow-on on PV systems, inverters and grid interfaces will reuse this lesson's phase and line quantities.
- Power-systems track: transformers and network components (`ps.transformers`, `ps.components`), power flow (`ps.power-flow`), which solves the per-unit network of many buses, faults and symmetrical components (`ps.faults`), which extend this lab's balance check, and protection (`ps.protection`). All are planned modules without a lesson yet, taught from their summaries as tutor-generated material.
- Cross-domain links: three-phase rectifiers and inverters (`pe.rectifiers`, `pe.inverters`, outlined so far only in the converters stage) and grid-connected converters (`ps.grid-converters`, planned) use this lesson's phase and line quantities; the open buck lab [`buck-open-lab.md`](../../03-converters/buck-open-lab.md) applies the same predict-then-run method to a DC-DC converter.
- Validation: these results are analytical, with one sampled numerical check; a follow-on lab in `ps.components` can compare them with a time-domain simulation including source and line impedance.
