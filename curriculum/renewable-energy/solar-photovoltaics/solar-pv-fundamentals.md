# Solar PV fundamentals: from photons to the maximum power point

> Module: `re.pv` · Also covers: `re.mppt` (introductory) · Level: undergraduate · Status: available
> Suggested time: 120 minutes · Labs: `labs/renewable-energy/pv_model.py`

A photovoltaic module has no moving parts, yet in the same sunlight it can
deliver its full rated power or less than a quarter of it, depending on how it
is loaded. This lesson explains where a solar cell's current comes from, why
its current–voltage curve has its shape, why one best operating voltage exists
and moves with sunlight and temperature, and how a converter can follow it.
Every number comes from a reproducible Python model of a synthetic 60-cell
module.

## Learning Objectives

After this lesson the learner can:

- explain how photons above the band gap create a photocurrent in a p-n
  junction, and why a cell behaves as a current source in parallel with a diode;
- define $$I_{sc}$$, $$V_{oc}$$, the maximum power point and the fill factor
  with SI units, and derive the single-diode equation with $$R_s$$ and
  $$R_{sh}$$ from Kirchhoff's current law;
- predict how $$I_{sc}$$, $$V_{oc}$$ and $$P_{mp}$$ change with irradiance and
  temperature, and reproduce the lesson's numbers with the lab;
- explain why a converter is needed, describe perturb-and-observe tracking and
  its oscillation versus speed trade-off, and state the model's limits,
  separating analytical, numerical and (absent) hardware results.

## Prerequisites

- DC circuits: Kirchhoff's laws, $$P = VI$$, series and parallel networks, the
  load line (module `f.dc-circuits`; lesson
  [DC circuit fundamentals](../../foundations/circuits/dc-circuit-fundamentals.md),
  slug `dc-circuit-fundamentals`; Chinese bridge in
  [the prerequisite path](../../01-foundations/prerequisite-path.zh-CN.md)).
- The diode's exponential law and thermal voltage (module `f.electronics`,
  introductory level); no further semiconductor physics is needed.
- Running a Python script and changing one argument at a time (module
  `f.computation`).
- Mathematics used: logarithm and exponential, one derivative for a maximum,
  one logarithmic derivative (signposted where it appears) and one fixed-point
  iteration; Newton's method and golden-section search run inside the lab.
- Helpful: the buck converter's input resistance (module `pe.buck`; lesson
  [Buck converter fundamentals](../../power-electronics/dc-dc-conversion/buck-converter-fundamentals.md),
  slug `buck-converter-fundamentals`; legacy
  [buck lesson](../../03-converters/buck-converter.md) and
  [open lab](../../03-converters/buck-open-lab.md)).

## Physical Intuition

### Photons and the band gap

Sunlight arrives as photons whose energy is set by colour: about 1.8 eV for
red, 2.8 eV for blue. In silicon an electron must be lifted across the band gap
of 1.12 eV before it can carry current. A photon below the gap passes through
unused; a photon above it frees one electron and one hole, and its surplus
becomes heat within picoseconds. These two losses are the main reason a silicon
cell converts only about a fifth of the sunlight.

### The junction separates the charges

Where n-type silicon meets p-type silicon, a thin region with a built-in
electric field forms. Pairs generated nearby are pulled apart before they can
recombine: electrons to the n-side, holes to the p-side. This flow is the
photocurrent, proportional to the irradiance (light power per square metre) and
almost independent of the terminal voltage.

### A current source in parallel with a diode

In the dark the junction is an ordinary diode. Under light the photocurrent
flows out of the p-terminal into the circuit, against the diode's forward
direction, so the terminal current is the photocurrent minus what the diode
takes back:

```text
   +----------+-------------+-----------+---/\/\/\---o  +
   |          |             |           |     R_s
  (I_ph)     ---  diode    | | R_sh    |
   |  light   \ /  (p-n     | | leakage |             V
   |  current  V   junction)| |         |
   +----------+-------------+-----------+--------------o  -
```

Short the terminals and the diode has almost no voltage, so the whole
photocurrent flows out: the short-circuit current. Open them and the
photocurrent is forced through the diode, whose voltage rises until it carries
it all: the open-circuit voltage, which grows only logarithmically with light
because the diode current grows exponentially. Two parasitic resistances
complete the picture: the series resistance $$R_s$$ (Ω) of fingers, contacts
and wiring costs voltage in proportion to current; the shunt resistance
$$R_{sh}$$ (Ω) of leakage paths steals current in proportion to voltage and
hurts most in weak light.

Predict before any formula: if irradiance halves, what happens to the
short-circuit current and to the open-circuit voltage? If the cell heats up and
the diode conducts more at the same voltage, what happens to the open-circuit
voltage?

## Fundamental Principles

### Quantities and units

- Irradiance $$G$$ (W/m²), light power per unit area in the module plane;
  standard test conditions (STC): 1000 W/m², 25 °C cell temperature, standard
  spectrum.
- Cell temperature $$T$$ (K) or $$T_c$$ (°C), $$T = T_c + 273.15$$.
- Terminal voltage $$V$$ (V) and current $$I$$ (A) in the generator convention;
  delivered power $$P = VI$$ (W).
- Short-circuit current $$I_{sc}$$ (A) at $$V = 0$$; open-circuit voltage
  $$V_{oc}$$ (V) at $$I = 0$$; maximum power point (MPP) $$(V_{mp}, I_{mp})$$
  where $$P$$ is largest, $$P_{mp} = V_{mp} I_{mp}$$ (W).
- Fill factor $$FF = P_{mp} / (V_{oc} I_{sc})$$ (dimensionless), the fraction of
  the $$V_{oc} \times I_{sc}$$ rectangle the curve fills.
- Photocurrent $$I_{ph}$$ (A), diode current $$I_D$$ (A), saturation current
  $$I_0$$ (A), ideality factor $$n$$ (1 to 2 for silicon), $$R_s$$ and
  $$R_{sh}$$ (Ω), series cells $$N_s$$, band-gap energy $$E_g$$ (eV;
  1 eV $$= 1.602 \times 10^{-19}$$ J).
- Thermal voltage $$V_t = k_B T / q$$ (V), with $$k_B = 1.380649 \times 10^{-23}$$ J/K
  and $$q = 1.602176634 \times 10^{-19}$$ C: 25.69 mV at 25 °C; for $$N_s$$
  cells of ideality $$n$$ the module thermal voltage is $$a = n N_s V_t$$ (V).
- Relative temperature coefficients $$\alpha$$, $$\beta$$, $$\gamma$$ of
  $$I_{sc}$$, $$V_{oc}$$ and $$P_{mp}$$ (%/K on datasheets, 1/K in equations):
  $$\alpha$$ is a model input, $$\beta$$ and $$\gamma$$ are outputs.

### Model assumptions

1. Superposition: terminal current equals photocurrent minus diode current minus
   shunt leakage; the photocurrent is independent of voltage.
2. $$I_{ph} \propto G$$; spectral changes are ignored.
3. Diode law $$I_D = I_0 (e^{V_d / a} - 1)$$ with constant $$n$$; $$V_d$$ (V)
   is the junction voltage, not the terminal voltage.
4. Temperature: $$I_{ph}$$ rises linearly through $$\alpha$$ (the datasheet's
   +0.05 %/K); $$I_0$$ rises steeply through $$E_g$$; $$a \propto T$$.
5. Identical, equally lit cells at one temperature (one lumped diode with
   $$N_s$$ times the voltage); partial shading, bypass diodes and reverse
   breakdown are outside the model.
6. Constant $$R_s$$, $$R_{sh}$$, $$n$$ and $$E_g$$; cell temperature is an
   input (no thermal model from ambient temperature, irradiance and wind).
7. Steady state; in the MPPT demonstration a lossless converter imposes each
   commanded voltage exactly and the power is measured without noise.

The lab implements exactly these statements; its outputs are numerical
simulations labelled `validation_status: numerical-simulation`, not
measurements or validated hardware performance.

### The synthetic module

An original 60-cell module, similar in scale to a residential crystalline-silicon
module but not a copy of any product: $$I_{sc} = 9.0$$ A and $$V_{oc} = 37.5$$ V
at STC, $$n = 1.3$$, $$R_s = 0.3$$ Ω, $$R_{sh} = 300$$ Ω, $$\alpha = +0.05$$ %/K,
$$E_g = 1.12$$ eV, $$N_s = 60$$.

## Mathematical Derivations

### The single-diode equation

Kirchhoff's current law at the node joining the current source, the diode and
the shunt resistor gives the current flowing towards the terminal:

$$
I = I_{ph} - I_0 \left( e^{V_d / a} - 1 \right) - \frac{V_d}{R_{sh}}
$$

With $$V_d = V + I R_s$$ this becomes the module equation used throughout:

$$
I = I_{ph} - I_0 \left[ \exp\!\left( \frac{V + I R_s}{a} \right) - 1 \right]
- \frac{V + I R_s}{R_{sh}}, \qquad a = \frac{n N_s k_B T}{q}
$$

$$I$$ appears on both sides, inside an exponential: the equation is implicit,
but it has exactly one solution for each $$V$$ (the right-hand side falls as
$$I$$ rises while the left-hand side rises), so a numerical root-finder is safe.

### Short circuit and open circuit

At $$V = 0$$ the junction voltage is $$I_{sc} R_s = 2.70$$ V, so the diode term
$$I_0 (e^{I_{sc} R_s / a} - 1) = 1.9 \times 10^{-7}$$ A is about 0.2 µA and
the shunt term a fraction $$R_s / R_{sh}$$ of the current:

$$
I_{sc} \approx I_{ph} \left( 1 - \frac{R_s}{R_{sh}} \right) \approx I_{ph}
$$

The model identifies $$I_{ph}$$ at STC with the nominal 9.0 A, so its own
$$I_{sc}$$ is 0.1 % lower, 8.991 A.

At $$I = 0$$ no current flows in $$R_s$$, so the series resistance drops out:

$$
0 = I_{ph} - I_0 \left( e^{V_{oc} / a} - 1 \right) - \frac{V_{oc}}{R_{sh}}
\quad \Rightarrow \quad
V_{oc} \approx a \ln\!\left( \frac{I_{ph}}{I_0} + 1 \right) \approx a \ln \frac{I_{ph}}{I_0}
$$

Hence $$V_{oc}$$ rises by $$a \ln 2 = 1.39$$ V per doubling of irradiance while
$$I_{sc}$$ doubles, and $$V_{oc}$$ is independent of $$R_s$$: poor series
resistance bends the knee and shows only in the fill factor.

### Saturation current from the datasheet

Solving the open-circuit condition at STC for the unquoted $$I_0$$,

$$
I_0^{STC} = \frac{I_{ph}^{STC} - V_{oc}^{STC} / R_{sh}}
{\exp\!\left( V_{oc}^{STC} / a_{STC} \right) - 1}
$$

The only approximation is $$I_{ph}^{STC} = I_{sc}^{STC}$$; the model then
reproduces $$V_{oc}$$ at STC exactly, by construction.

### Temperature

In the usual single-diode array models,

$$
I_0(T) = I_0^{STC} \left( \frac{T}{T_{STC}} \right)^{3}
\exp\!\left[ \frac{E_g}{n k_B} \left( \frac{1}{T_{STC}} - \frac{1}{T} \right) \right]
$$

with temperatures in kelvin, $$T_{STC} = 298.15$$ K and $$E_g$$ in joules
(1.12 eV = $$1.794 \times 10^{-19}$$ J), so that
$$E_g / (n k_B) = 9.998 \times 10^{3}$$ K for $$n = 1.3$$; the lab stores the
gap in electronvolts and writes the same factor as $$q E_g / (n k_B)$$. The
ideality factor sits in the exponent because the dominant recombination current
scales as $$\exp(-E_g / n k_B T)$$. At fixed irradiance
$$I_{ph}(T) = I_{ph}^{STC} [1 + \alpha (T - T_{STC})]$$.

One new piece of mathematics: a product of powers and exponentials is easiest
to differentiate through its logarithm, since
$$\mathrm{d}(\ln y)/\mathrm{d}T = (\mathrm{d}y/\mathrm{d}T)/y$$ turns products
into sums. Applied to $$V_{oc} \approx a \ln (I_{ph} / I_0)$$ with
$$a \propto T$$, $$\mathrm{d}(\ln I_{ph})/\mathrm{d}T = \alpha$$ and
$$\mathrm{d}(\ln I_0)/\mathrm{d}T = 3/T + E_g / (n k_B T^2)$$:

$$
\frac{\mathrm{d} V_{oc}}{\mathrm{d} T} = \frac{V_{oc} - 3a - N_s E_g / q}{T} + a \alpha
$$

Every term is nearly constant, so $$V_{oc}$$ falls almost linearly, and since
$$N_s E_g / q = 67.2$$ V exceeds $$V_{oc} = 37.5$$ V the slope is negative:
$$(37.5 - 6.01 - 67.2)/298.15 + 2.004 \times 0.0005 = -0.1188$$ V/K, or
$$-0.317$$ %/K, within the $$-0.25$$ to $$-0.35$$ %/K of crystalline-silicon
datasheets. The lab's numerical value, with the shunt term, is $$-0.316$$ %/K:
an output of the model, not an input.

### The maximum power point

$$P(V) = V I(V)$$ vanishes at both ends of the curve, so its maximum satisfies

$$
\frac{\mathrm{d} P}{\mathrm{d} V} = I + V \frac{\mathrm{d} I}{\mathrm{d} V} = 0
\quad \Longleftrightarrow \quad
\frac{\mathrm{d} I}{\mathrm{d} V} = - \frac{I}{V}
$$

the incremental conductance equals minus the static conductance. For the
idealised module ($$R_s \to 0$$, $$R_{sh} \to \infty$$) this rearranges to

$$
V_{mp} = V_{oc} - a \ln\!\left( 1 + \frac{V_{mp}}{a} \right), \qquad
I_{mp} = I_{ph} \, \frac{V_{mp} / a}{1 + V_{mp} / a}
$$

solvable by a few substitutions; with the resistances there is no shortcut and
the lab finds the maximum numerically.

### Why a converter is needed

A resistor $$R$$ draws $$I = V / R$$, a straight load line through the origin,
and operates where that line crosses the module curve. Only
$$R_{mp} = V_{mp} / I_{mp}$$ crosses at the MPP, which moves with irradiance and
temperature while the resistor does not. A lossless buck converter in
continuous conduction with duty ratio $$D$$ (dimensionless) feeding a load
$$R_L$$ (Ω) presents an input resistance $$R_{in} = R_L / D^2$$ (Ω) to the
module. Since $$D \le 1$$, $$R_{in} \ge R_L$$: a buck can only raise the
apparent resistance and reaches the MPP when $$R_L \le R_{mp}$$ (3.575 Ω at
STC); a boost or buck-boost covers the other case. Maximum power point tracking
(MPPT) is the control loop that chooses $$D$$; it is not a converter efficiency.

### Perturb and observe

Each control period the tracker moves the voltage by a fixed step $$\Delta V$$
(V), measures the power, keeps the direction if the power rose and reverses it
if it fell. It inevitably steps over the summit and back, so in steady state it
cycles through $$V_{mp} - \Delta V$$, about $$V_{mp}$$ and $$V_{mp} + \Delta V$$
in four steps, averaging slightly below $$P_{mp}$$: a small step gives a small
oscillation loss but a slow climb, a large step the reverse. Incremental
conductance uses the derivative test $$\mathrm{d}I/\mathrm{d}V > -I/V$$ (left of
the MPP, so raise the voltage) instead; in principle it stops at the MPP, but
with measurement noise and a finite step it behaves much like perturb and
observe.

## Worked Examples

Numbers come from the lab's default run, rounded for display.

### Example 1: from datasheet to the current at 30 V

Thermal voltage: $$V_t = k_B \times 298.15 / q = 0.025693$$ V, so
$$a = 1.3 \times 60 \times 0.025693 = 2.0040$$ V.

Saturation current: $$V_{oc}/a = 37.5/2.0040 = 18.712$$,
$$e^{18.712} = 1.3387 \times 10^{8}$$; the shunt takes $$37.5/300 = 0.125$$ A,
leaving 8.875 A for the diode, so
$$I_0 = 8.875 / (1.3387 \times 10^{8}) = 6.630 \times 10^{-8}$$ A (66.3 nA);
$$I_{ph}/I_0 \sim 10^{8}$$ is typical of silicon.

Current at 30 V by fixed-point iteration from $$I = 8.3$$ A:
$$V_d = 30 + 8.3 \times 0.3 = 32.49$$ V, $$V_d/a = 16.212$$,
$$e^{16.212} = 1.099 \times 10^{7}$$,
$$I_D = 6.630 \times 10^{-8} \times 1.099 \times 10^{7} = 0.729$$ A, shunt
current $$32.49/300 = 0.108$$ A, so $$I = 9.000 - 0.729 - 0.108 = 8.163$$ A.
The next passes give 8.178, 8.1765 and 8.1766 A, the lab's value. It converges
because an error of one ampere in $$I$$ changes $$I_D$$ by only
$$I_D R_s / a \approx 0.72 \times 0.3 / 2.0 = 0.11$$ A; that slope,
$$I_D R_s / a + R_s / R_{sh}$$, exceeds 1 above about 36.3 V
($$I_D > a / R_s = 6.7$$ A; 1.33 at $$V_{oc}$$), where fixed-point iteration
diverges, so the lab uses Newton's method with a bisection fallback. The power
at 30 V is $$30 \times 8.1766 = 245.30$$ W.

### Example 2: maximum power point and fill factor

The lab finds $$V_{mp} = 29.632$$ V, $$I_{mp} = 8.288$$ A and
$$P_{mp} = 245.58$$ W, so

$$
FF = \frac{245.58}{37.500 \times 8.991} = \frac{245.58}{337.16} = 0.7284
$$

Per cell: $$V_{oc} = 0.625$$ V, $$V_{mp} = 0.494$$ V, $$P_{mp} = 4.09$$ W; the
MPP sits at 79 % of $$V_{oc}$$ and 92 % of $$I_{sc}$$, and the matched load is
$$R_{mp} = 29.632/8.288 = 3.575$$ Ω.

Sanity check against an ideal module ($$R_s \to 0$$, $$R_{sh} \to \infty$$)
with the same $$I_{sc}$$ and $$V_{oc}$$: iterating
$$V_{mp} = 37.5 - 2.004 \ln(1 + V_{mp}/2.004)$$ from 30 V gives 31.95, 31.83,
31.84 V, then $$I_{mp} = 9.0 \times 15.89/16.89 = 8.467$$ A, $$P_{mp} = 269.6$$ W
and $$FF = 0.799$$ (lab: `--r-s 1e-9 --r-sh inf`, 269.55 W; keeping the real
module's $$I_0$$ instead would give $$V_{oc} = 37.53$$ V). The resistances cost
about 24 W: $$R_s$$ alone moves the MPP from 31.84 V to 29.62 V, about 2.2 V
(first-order estimate $$I_{mp} R_s = 2.5$$ V), and the lab confirms the split
(248.3 W without the shunt, 245.6 W with both).

### Example 3: a hot, hazy afternoon

At $$G = 600$$ W/m² and $$T_c = 50$$ °C the photocurrent is
$$9.0 \times 0.6 \times (1 + 0.0005 \times 25) = 5.4675$$ A and the model's
$$I_{sc}$$ is 5.462 A. The linear coefficient gives
$$V_{oc} = 37.5 (1 - 0.00316 \times 25) = 34.5$$ V at full sun and 50 °C, and
the irradiance term removes $$a(T) \ln(1/0.6) = 2.172 \times 0.511 = 1.11$$ V,
about 33.4 V; the lab gives 33.388 V. The MPP moves to 26.396 V, 4.950 A,
130.67 W, $$FF = 0.7165$$. The 3.575 Ω resistor that was perfect at STC now
sits at 19.2 V and extracts 103.5 W (79 %); holding 29.632 V extracts 111.6 W
(85 %); a tracker that finds 26.4 V extracts all 130.67 W. At 200 W/m² and
25 °C the resistor manages 11.3 W of a possible 45.0 W.

## Numerical or Simulation Lab

- Script: [`labs/renewable-energy/pv_model.py`](../../../labs/renewable-energy/pv_model.py),
  Python 3.10+, standard library only; `matplotlib` optional, behind `--plot`.
- Inputs: irradiance in W/m² (0 to 2000), cell temperature in °C (−40 to 100),
  module parameter overrides (`--cells`, `--i-sc`, `--v-oc`, `--ideality`,
  `--r-s`, `--r-sh`, `--alpha-isc`, `--band-gap`), `--points` (default 201)
  and the P&O settings `--step-v` (0.5 V), `--iterations` (40) and
  `--start-v` (default 0.4 $$V_{oc}$$ = 15 V).
- Model: the single-diode equation, solved by safeguarded Newton iteration to a
  current residual below $$10^{-9}$$ A; the MPP is bracketed on a 401-point grid
  and refined by golden-section search to $$10^{-6}$$ V. Precision of
  $$P_{mp}$$: about $$10^{-12}$$ W from the voltage bracket; the current
  tolerance could add up to $$3 \times 10^{-8}$$ W, but Newton's quadratic
  convergence leaves residuals near $$10^{-15}$$ A (measured error at STC
  $$10^{-13}$$ W). A teaching model, not validated against any measured module.
- Outputs: indented JSON (`model`, `validation_status`, `assumptions`,
  `limitations`, parameters, key points, eleven I-V samples, sweeps,
  temperature coefficients), every quantity a `{"value", "unit"}` pair.

```text
python labs/renewable-energy/pv_model.py                       # default STC example
python labs/renewable-energy/pv_model.py --mppt                # add the P&O trajectory
python labs/renewable-energy/pv_model.py --irradiance 600 --temperature 50
python labs/renewable-energy/pv_model.py --json                # full 201-point I-V arrays
python labs/renewable-energy/pv_model.py --plot --out pv.png   # optional figure
python -m unittest tests.test_lab_pv_model                     # unit tests of the model
```

Expected default values, abbreviated from the JSON:

```text
derived_parameters.thermal_voltage_module_a    2.0040 V
derived_parameters.saturation_current_stc      6.6296e-08 A
key_points.short_circuit_current               8.9910 A
key_points.open_circuit_voltage                37.500 V
key_points.v_mp / i_mp / p_mp                  29.632 V / 8.2878 A / 245.58 W
key_points.fill_factor                         0.7284
sensitivity.temperature_coefficients_at_stc    alpha +0.0500 %/K, beta -0.3165 %/K, gamma -0.4103 %/K
```

With `--mppt` (step 0.5 V, 40 iterations, start 15 V) the tracker reaches the
band within one step of $$V_{mp}$$ at iteration 29, then cycles through 29.0,
29.5 and 30.0 V (244.85, 245.55 and 245.30 W); the mean over the last eight
iterations is 245.31 W, a tracking efficiency of 0.9989.

Validation: `ValueError` for non-finite, boolean or out-of-range inputs,
voltages below 0 V (reverse bias is outside the model) or above twice
$$V_{oc}$$, inconsistent parameter sets ($$V_{oc}/R_{sh} \ge I_{sc}$$,
$$R_s I_{sc} \ge V_{oc}$$ or $$V_{oc}/a > 100$$) and invalid sample counts or
P&O settings (checked even without `--mppt`); the command line prints `error:`
and the message to standard error and exits with code 2. Zero irradiance gives
an all-zero curve with the fill factor `null`, never NaN. Equal inputs give
identical JSON; record the command, `reproducibility.python_version` and the
key points.

## Parameter Exploration

Change one input at a time and write the prediction first.

1. Irradiance 200 to 1000 W/m² at 25 °C (`sensitivity.irradiance_sweep`).
   Predict $$I_{sc} \propto G$$, $$V_{oc}$$ up about 1.4 V per doubling,
   $$P_{mp}$$ nearly proportional. Result: $$I_{sc}$$ 1.798, 3.596, 5.395, 7.193,
   8.991 A; $$V_{oc}$$ 34.17, 35.62, 36.46, 37.05, 37.50 V (1.42 V per doubling
   against $$a \ln 2 = 1.39$$ V); $$P_{mp}$$ 45.0, 95.5, 146.1, 196.3, 245.6 W.
   The fill factor peaks near 400 to 600 W/m² (0.745), between series loss at
   high current and shunt loss in weak light.
2. Temperature 0 to 75 °C at 1000 W/m² (`sensitivity.temperature_sweep`).
   Predict each sign. Result: $$I_{sc}$$ 8.879 to 9.216 A; $$V_{oc}$$ 40.45,
   37.50, 34.51, 31.49 V, almost exactly 3.0 V per 25 K; $$P_{mp}$$ 270.5,
   245.6, 220.2, 194.5 W ($$-0.41$$ %/K); $$V_{mp}$$ 32.7 to 23.6 V. A module
   30 K above STC loses over 12 % of its power and 3.6 V of MPP voltage: a
   tracker must follow temperature as well as light.
3. Resistances. `--r-s 0.15` and `--r-s 0.6`: $$V_{oc}$$ stays 37.500 V,
   $$I_{sc}$$ moves about 0.1 %, $$P_{mp}$$ 255.9, 245.6, 225.2 W, $$FF$$ 0.759,
   0.728, 0.669, a pure fill-factor loss. `--r-sh 50` costs 5.5 % of $$P_{mp}$$
   at full sun (232.2 W) but 28 % at 200 W/m² (32.4 W, $$FF$$ 0.54), because
   the leakage barely changes while the photocurrent falls with the light.
4. P&O step `--mppt --iterations 200` with `--step-v 0.1`, `0.5`, `1.0`,
   `2.0`. Predict climb time and power ripple. Result: iterations to the MPP
   band 146, 29, 14, 7; power band 0.03, 0.70, 4.15, 9.21 W; tracking
   efficiency 0.99995, 0.9989, 0.9942, 0.9839. The oscillation loss grows
   roughly as the square of the step (parabolic P-V top, modulated by where the
   step lattice falls around $$V_{mp}$$) while the climb time falls only
   linearly, hence small or adaptive steps in practice.
5. Series connection `--cells 120 --v-oc 75 --r-s 0.6 --r-sh 600` (two identical
   modules). Predict $$V_{mp}$$, $$I_{mp}$$, $$FF$$. Result: 59.264 V (double),
   8.288 A (unchanged), 491.16 W, $$FF = 0.7284$$ (unchanged): series connection
   adds voltages and leaves current alone, exactly so only for identical,
   equally lit cells.

## Common Misconceptions

- "A 245 W module delivers 245 W whenever the sun shines." Only at STC and only
  at 29.6 V. At 600 W/m² and 50 °C the best is 131 W, and a resistor matched at
  STC extracts 104 W of that. Check: Example 3.
- "A hotter module produces more power." Photocurrent rises 0.05 %/K, $$V_{oc}$$
  falls about 0.32 %/K, power falls about 0.41 %/K. Check: the temperature
  sweep and the $$V_{oc}$$ derivative.
- "$$V_{oc}$$ scales with irradiance like the current." It scales
  logarithmically: a tenfold drop in light removes about $$a \ln 10 = 4.6$$ V
  plus a small shunt contribution. Check: `--irradiance 100` gives
  $$V_{oc} = 32.66$$ V, 4.8 V (13 %) below STC, while $$I_{sc}$$ falls by 90 %.
- "MPPT efficiency is the converter's efficiency." Tracking efficiency compares
  the power drawn with the power available at the MPP; converter losses
  multiply it. Check: the lab's 0.9989 assumes a lossless converter.
- "A smaller P&O step is always better." Below some size the oscillation loss is
  negligible, but the tracker then needs many periods to follow a passing cloud.
  Check: Exploration 4.

## AI Tutor Exercises

Prompts written so that the tutor asks before it tells.

1. Diagnostic: "Before explaining anything, ask me to sketch a module's I-V
   curve, mark $$I_{sc}$$, $$V_{oc}$$ and the MPP, and say what happens to each
   when irradiance halves and when the module heats by 25 K. Only then compare
   my predictions with `labs/renewable-energy/pv_model.py`."
2. Explain-back: "Ask me to explain, without equations, why a solar cell is
   modelled as a current source in parallel with a diode, and probe with two
   follow-ups such as what the diode does at short and at open circuit. Do not
   give the explanation first."
3. Change one condition: "Before I run the lab with `--r-s 0.6`, ask me which of
   $$I_{sc}$$, $$V_{oc}$$, $$FF$$ and $$P_{mp}$$ will change and by roughly how
   much; afterwards ask me to explain any wrong prediction with the open-circuit
   derivation."
4. Numerical reasoning: "Give me $$V_{oc}$$, $$a$$ and $$R_{sh}$$ and ask me to
   compute $$I_0$$ by hand, checking each step instead of giving the answer;
   then ask what an ideality factor of 1.0 instead of 1.3 does to $$I_0$$ and
   $$P_{mp}$$."
5. Debug my work: "I will paste my own perturb-and-observe code or my reading of
   the lab's trajectory. Ask what steady-state pattern I expect, then help me
   find the discrepancy by asking questions, not by rewriting my code, and
   finish by asking which model assumption a shaded cell would break."

## Knowledge Assessment

Questions 2, 4 and 6 must be solved independently (no hints, no copied answers)
before `re.pv` is marked `demonstrated`; assisted answers count as `learning`.
An independent Q6 records `re.mppt` as introductory `learning` only, since
`demonstrated` for `re.mppt` needs the converter-in-the-loop lab planned in
Further Learning.

1. Conceptual. Why does a photon below the band gap produce no current, and
   where does the surplus energy of a photon well above the gap go?
2. Numerical. Another synthetic module has $$N_s = 72$$, $$V_{oc} = 45.0$$ V,
   $$I_{sc} = 10.2$$ A, $$n = 1.2$$ and $$R_{sh} = 400$$ Ω at STC. Compute
   $$a$$ and $$I_0$$ with steps and units, then check with
   `--cells 72 --v-oc 45 --i-sc 10.2 --ideality 1.2 --r-sh 400`.
3. Conceptual. A module's $$V_{oc}$$ and $$I_{sc}$$ are normal but its fill
   factor has dropped from 0.73 to 0.65. Which model parameter has most likely
   changed, and what fault could cause it?
4. Numerical. Using $$-0.316$$ %/K for $$V_{oc}$$ and $$-0.410$$ %/K for
   $$P_{mp}$$, estimate both at 1000 W/m² and 60 °C and give one reason the
   exact model values differ slightly.
5. Conceptual. With the load-line picture, explain why a resistor matched at
   STC extracts only a quarter of the available power at 200 W/m², and what a
   converter changes.
6. Numerical and conceptual. At 600 W/m² and 50 °C (MPP 26.40 V, 130.67 W) a
   P&O tracker with a 1.0 V step starts at 20 V. Which voltages does it visit
   in steady state, what are its mean power and tracking efficiency, and what
   does halving the step change? Check with
   `--mppt --step-v 1 --start-v 20 --irradiance 600 --temperature 50`.
7. Model limits. Name two lab assumptions that fail for a module with one shaded
   cell and what the lab would then predict wrongly.

<details><summary>Answers</summary>

1. A sub-gap photon cannot free an electron and is not absorbed; the surplus of
   an above-gap photon becomes lattice heat within picoseconds.
2. $$a = 1.2 \times 72 \times 0.025693 = 2.2198$$ V; $$V_{oc}/a = 20.272$$,
   $$e^{20.272} = 6.37 \times 10^{8}$$; the shunt takes $$45/400 = 0.1125$$ A,
   leaving 10.0875 A for the diode, so
   $$I_0 = 10.0875/(6.37 \times 10^{8} - 1) = 1.58 \times 10^{-8}$$ A
   (15.8 nA); the lab gives $$1.5844 \times 10^{-8}$$ A.
3. $$R_s$$: it leaves $$V_{oc}$$ unchanged and barely changes $$I_{sc}$$ but
   rounds the knee; causes include corroded ribbons, degraded solder joints or a
   poor connector.
4. $$V_{oc} \approx 37.5 (1 - 0.00316 \times 35) = 33.4$$ V,
   $$P_{mp} \approx 245.6 (1 - 0.00410 \times 35) = 210$$ W; the lab gives
   33.311 V and 209.92 W because the dependence is only approximately linear.
5. The load line $$I = V/R$$ is fixed; at 200 W/m² it crosses the shrunken curve
   near 6.4 V, giving 11 W instead of the 45 W available near 28.2 V
   ($$R_{mp} = 17.7$$ Ω). A converter changes the effective resistance: a buck
   with $$D = 0.45$$ presents $$3.575/0.45^2 = 17.7$$ Ω and moves the crossing
   to the MPP.
6. It reaches the band at iteration 6 and cycles through 25, 26 and 27 V
   (128.74, 130.49 and 130.20 W); the mean over the last eight iterations is
   129.98 W, a tracking efficiency of 0.9947. A 0.5 V step cycles through 26.0,
   26.5 and 27.0 V with 130.50 W and 0.9987 but needs 12 iterations to reach
   the band: smaller ripple, slower climb.
7. Identical, equally lit cells and one lumped diode: a shaded cell has a much
   smaller photocurrent and is driven into reverse bias or bypassed, so the
   real curve has several local maxima (which can trap a P&O tracker) and less
   power than the lab's smooth single-peak prediction.

</details>

## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 2.627 — Fundamentals of Photovoltaics (Fall 2013)
  https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/
  Syllabus: https://ocw.mit.edu/courses/2-627-fundamentals-of-photovoltaics-fall-2013/pages/syllabus/

Supporting academic references:

- MIT EC.S07 — Photovoltaic Solar Energy Systems (Fall 2004)
  https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/
  Lecture notes: https://ocw.mit.edu/courses/ec-s07-photovoltaic-solar-energy-systems-fall-2004/pages/lecture-notes/
- MIT 6.012 — Microelectronic Devices and Circuits (Fall 2005)
  https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/
  Lecture notes: https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/pages/lecture-notes/

Relevant subjects:

- Photon absorption, band gap and charge separation at a p-n junction
  (2.627, 6.012)
- Solar cell current–voltage characteristics, equivalent circuit and losses
  (2.627)
- Module behaviour under varying irradiance and temperature, load matching and
  power conditioning (EC.S07)
- The p-n junction diode equation and its temperature dependence (6.012)

This lesson has been independently developed by AIPE Academy with reference to
the academic scope of the above courses. MIT OpenCourseWare is an external
educational resource released under its own licence (generally CC BY-NC-SA 4.0).
AIPE Academy is not affiliated with or endorsed by MIT.

### Other references

- M. G. Villalva, J. R. Gazoli and E. Ruppert Filho, "Comprehensive Approach to
  Modeling and Simulation of Photovoltaic Arrays", IEEE Transactions on Power
  Electronics, vol. 24, no. 5, 2009. Publisher record:
  https://doi.org/10.1109/TPEL.2009.2013862 (single-diode parameter approach
  and $$I_0(T)$$ law; no content reproduced).
- W. De Soto, S. A. Klein and W. A. Beckman, "Improvement and validation of a
  model for photovoltaic array performance", Solar Energy, vol. 80, no. 1,
  2006. Publisher record: https://doi.org/10.1016/j.solener.2005.06.010.
- R. W. Erickson and D. Maksimović, Fundamentals of Power Electronics, 3rd
  edition, Springer, 2020. Publisher record:
  https://link.springer.com/book/10.1007/978-3-030-43881-4 (converter
  input-resistance relations).

## Further Learning

- Next in this track: a planned lesson on PV systems, inverters and grid
  interfaces (module `re.pv-systems`, with `pe.inverters` and
  `ps.grid-converters`).
- Deeper MPPT (`re.mppt`): drive the buck model of
  [the open buck lab](../../03-converters/buck-open-lab.md) from this module
  model, so that duty ratio replaces voltage as the control variable and the
  input capacitor and sampling period enter the loop (`pe.buck`, `pe.control`).
- Related reading: the diode law and thermal voltage behind $$I_0$$ and $$n$$
  in `f.electronics` (power diodes as switches in `pe.devices`); within the
  same domain, energy and efficiency bookkeeping in `re.conversion`.
- Validation: no lesson yet compares this model with a switching simulation or
  a measurement; a planned follow-on lab would check it against an ngspice
  model of a buck-based tracker and, where equipment exists, a measured I-V
  trace. Until then every number here is a model output.
