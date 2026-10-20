# DC circuit fundamentals: voltage, current, power and the circuit laws

> Module: `f.dc-circuits` · Also covers: `f.quantities` · Level: beginner · Status: available
> Suggested time: 90 minutes · Labs: `labs/foundations/dc_circuits.py`

Connect a battery to a resistor and three questions follow: how much current
flows, how quickly is energy converted, and what changes when a second
component joins the circuit? This lesson answers them for ideal direct-current
(DC) circuits, the starting point of every later analysis in power engineering.

## Learning Objectives

After this lesson the learner can:

- define voltage, current, resistance, power and energy with SI units, and
  distinguish the watt from the watt-hour and the joule;
- calculate any one of voltage, current and resistance from the other two for
  an ideal resistor, stating the sign convention used;
- apply Kirchhoff's current and voltage laws to a node and a loop with
  consistent signs, and reduce series and parallel groups to an equivalent
  resistance;
- calculate a voltage divider's output with and without a load, explain why the
  loaded output is lower, and predict it from the Thevenin equivalent;
- write the current-law equation of a small network as a linear equation,
  check a two-source result by superposition, and verify the lab's numerical
  solution against a hand calculation.

## Prerequisites

- Decimal and fraction arithmetic, ratios, and rearranging a simple equation
  such as $$a = b/c$$. Unit prefixes and unit checking (`f.quantities`) are
  introduced below where first used; the Chinese outline
  [先修课程路线](../../01-foundations/prerequisite-path.zh-CN.md) covers the
  same ground.
- No calculus is needed; the one calculus idea used (energy as the area under
  a power-time graph) is explained in words.
- Optional: the Chinese introductory lesson
  [一个简单电路用了多少电？](../../01-foundations/first-lesson.zh-CN.md) covers
  the first third of this material with the same 6 V / 300 Ω example (this
  lesson is original English content, not a translation); `f.electromagnetism`
  gives the physics of charge, field and potential.

## Physical Intuition

Picture a bicycle chain. When the rider pushes the pedals, every link moves at
once, all the way round; the chain is not consumed at the rear wheel, it
delivers the rider's effort there and comes back for more. Charge in a closed
circuit behaves the same way: current is how fast the chain moves, voltage is
how hard the pedals push between two points, and a resistor is the stiff part
where effort turns into heat. What a resistor uses up is energy, not charge.

Three predictions before reading on:

1. A fixed 6 V source drives a 300 Ω resistor. Swap it for 600 Ω: does the
   current double, halve or stay the same, and what happens to the heat?
2. Two identical resistors are connected side by side across one source. Is the
   total current larger or smaller than with one resistor?
3. Two equal resistors in series across 12 V give 6 V at their junction. A third
   resistor is connected from the junction to the return wire. Does the junction
   stay at 6 V?

Most beginners miss the third: the new resistor opens a second path, more
current flows through the top resistor, its drop grows, and less voltage is
left at the output.

## Fundamental Principles

The lumped-element model underlies everything here: each component is a point
where exactly one thing happens (a fixed voltage, a fixed current, or
resistance), joined by wires that do nothing; exact for an idealised circuit
and excellent at the bench.

### Quantities and units

- **Charge** $$q$$ in coulombs (C) is conserved in a circuit.
- **Current** $$I$$ in amperes (A) is the rate at which charge passes a point,
  $$1\ \text{A} = 1\ \text{C/s}$$; it carries a sign relative to a chosen arrow.
- **Voltage** $$V$$ in volts (V) is energy per unit charge between two points,
  $$1\ \text{V} = 1\ \text{J/C}$$. "The voltage at a node" means the voltage
  between that node and the reference node (ground), defined as 0 V.
- **Resistance** $$R$$ in ohms (Ω) is the fixed ratio of voltage to current for
  a linear resistor; **conductance** $$G = 1/R$$ in siemens (S) suits parallel
  circuits.
- **Power** $$P$$ in watts (W) is the rate of energy conversion,
  $$1\ \text{W} = 1\ \text{J/s}$$.
- **Energy** $$E$$ in joules (J); battery labels use the watt-hour, the energy
  converted at 1 W for one hour, $$1\ \text{Wh} = 3600\ \text{J}$$. A watt says
  how fast; a joule or watt-hour says how much.

Prefixes scale any unit by a power of ten: $$1\ \text{k}\Omega = 1000\ \Omega$$,
$$1\ \text{mA} = 0.001\ \text{A}$$, $$1\ \text{mW} = 0.001\ \text{W}$$. Carry
units through every calculation as a check:
$$0.02\ \text{A} \times 300\ \Omega = 6\ \text{V}$$; a rearranged formula that
yields anything but volts is wrong.

### Ideal elements

- **Ideal resistor**: $$V = IR$$ at every current, with $$R$$ constant. Real
  resistors have tolerance, drift with temperature and carry a power rating.
- **Ideal voltage source**: holds its voltage whatever current flows; a real
  battery has internal resistance and sags under load.
- **Ideal current source**: forces its current whatever voltage appears across
  it.
- **Ideal wire**: zero resistance, so two points joined by a wire are one node.

```text
            I -->
     +---------------------+
     |                     |
    +|                    +-+
   ( )  V = 6 V           | |  R = 300 Ohm
    -|                    +-+
     |                     |
     +---------------------+
```

### The passive sign convention

Every branch (one element between two nodes) gets an end $$a$$ and an end
$$b$$. Its voltage is $$v = V_a - V_b$$ and its current $$i$$ flows from $$a$$
to $$b$$ through the element, so $$p = v\,i$$ is positive when the element
absorbs energy and negative when it supplies it. A resistor always absorbs; a
source delivering energy shows negative power, which is not an error. The lab,
like SPICE circuit simulators, uses this convention.

### Kirchhoff's laws

- **KCL (Kirchhoff's current law)**: at any node the signed currents sum to
  zero. In the lumped model a junction stores no charge, so what flows in must
  flow out at every instant; capacitors, met in `f.dynamics`, store charge
  inside a branch, and KCL still holds at their terminals.
- **KVL (Kirchhoff's voltage law)**: around any closed loop the signed voltage
  drops sum to zero, as a walk round a hill returns to the same height. It
  holds whenever no changing magnetic flux from outside the elements threads
  the loop; a lumped inductor keeps its flux inside and appears as an ordinary
  branch voltage in `f.dynamics`.

Elements are **in series** when the same current must pass through each and
**in parallel** when they connect between the same pair of nodes and share a
voltage.

## Mathematical Derivations

### 1. Ohm's law, power and energy

$$
V = IR, \qquad I = \frac{V}{R}, \qquad R = \frac{V}{I}.
$$

Substituting into $$P = VI$$ gives two further forms:

$$
P = VI = I^2 R = \frac{V^2}{R}.
$$

The last form shows why halving the voltage across a fixed resistor quarters
the power. At constant power for a time $$t$$,

$$
E = P\,t,
$$

in joules when $$t$$ is in seconds and in watt-hours when $$t$$ is in hours.
When power varies, energy is the area under the power-time graph (the only idea
borrowed from calculus); constant power makes that area a rectangle.

### 2. Series resistors and the voltage divider

Series resistors carry the same current $$I$$, and by KVL the drops add:
$$V = IR_1 + IR_2 = I(R_1 + R_2)$$, so $$R_{\text{eq}} = R_1 + R_2 + \dots + R_n$$.
The voltage across the lower resistor of a pair is $$IR_2$$, which gives

$$
V_{\text{out}} = V_{\text{in}}\,\frac{R_{\text{bottom}}}{R_{\text{top}} + R_{\text{bottom}}}.
$$

### 3. Parallel resistors and the current divider

Parallel resistors share a voltage $$V$$, and by KCL the branch currents add:
$$I = V/R_1 + V/R_2 = V(G_1 + G_2)$$, so conductances add and

$$
\frac{1}{R_{\text{eq}}} = \frac{1}{R_1} + \frac{1}{R_2} + \dots + \frac{1}{R_n}.
$$

For two resistors $$R_{\text{eq}} = R_1 R_2/(R_1 + R_2)$$; for $$n$$ equal
resistors it is $$R/n$$. The equivalent is always below the smallest member.
The share of the total current taken by $$R_1$$ is

$$
I_1 = I\,\frac{R_2}{R_1 + R_2},
$$

the current divider: the larger share flows through the smaller resistor.

### 4. The Thevenin equivalent, introductory level

Seen from any two terminals, a network of resistors and independent sources
behaves like one ideal voltage source $$V_{\text{th}}$$ in series with one
resistor $$R_{\text{th}}$$: $$V_{\text{th}}$$ is the open-circuit voltage and
$$R_{\text{th}}$$ the resistance seen looking in with
every source switched off (a voltage source becomes a wire, a current source a
gap; the proof is deferred to a later lesson). For a divider seen from its
output, the source becomes a wire and the two resistors appear in parallel:

$$
V_{\text{th}} = V_{\text{in}}\,\frac{R_{\text{bottom}}}{R_{\text{top}} + R_{\text{bottom}}},
\qquad
R_{\text{th}} = \frac{R_{\text{top}} R_{\text{bottom}}}{R_{\text{top}} + R_{\text{bottom}}}.
$$

### 5. The loaded divider and its loading error

A load $$R_L$$ across $$R_{\text{bottom}}$$ is in parallel with it, so one route
replaces $$R_{\text{bottom}}$$ by $$R_{\text{bottom}} \parallel R_L$$ in the
divider formula. The Thevenin route is quicker: the load sees $$V_{\text{th}}$$
through $$R_{\text{th}}$$, itself a divider,

$$
V_{\text{loaded}} = V_{\text{th}}\,\frac{R_L}{R_{\text{th}} + R_L},
\qquad
\frac{V_{\text{loaded}} - V_{\text{th}}}{V_{\text{th}}} = -\frac{R_{\text{th}}}{R_{\text{th}} + R_L}.
$$

The relative error depends only on $$R_L/R_{\text{th}}$$, not on
$$V_{\text{in}}$$; keeping its magnitude at or below 1 % needs
$$R_L \geq 99\,R_{\text{th}}$$ (strictly below 1 % needs $$R_L > 99\,R_{\text{th}}$$).

### 6. Nodal analysis: KCL as a linear equation

Take a 12 V source from node n1 to ground, $$R_1 = 2\ \text{k}\Omega$$ from n1
to n2, $$R_2 = 4\ \text{k}\Omega$$ from n2 to ground, and a 1.5 mA current
source pushing current from ground into n2. The source fixes
$$V_1 = 12\ \text{V}$$, so the only unknown is $$V_2$$. KCL at n2, counting
currents leaving the node as positive, gives

$$
\frac{V_2 - 12}{2000} + \frac{V_2}{4000} - 0.0015 = 0
\quad\Rightarrow\quad
2(V_2 - 12) + V_2 - 6 = 0
\quad\Rightarrow\quad
V_2 = 10\ \text{V}.
$$

The recipe scales: one KCL equation per non-reference node, plus one extra
unknown (the source current) and one equation per ideal voltage source. This is
modified nodal analysis; the lab solves it by Gaussian elimination (theory in
`f.linear-algebra`) and agrees with hand calculation to floating-point rounding,
which is why its residuals are near $$10^{-19}$$ A rather than exactly zero.

Because these equations are linear, the **superposition principle** holds: the
response to several independent sources is the sum of the responses to each
source acting alone, the others switched off as in Derivation 4. It fails for
non-linear elements such as diodes.

## Worked Examples

Examples 1 and 2 use the lab's default outputs; Example 3 uses its built-in
`two-source` network.

### Example 1: one resistor across an ideal source

An ideal 6 V source drives 300 Ω for 30 minutes.

$$
I = \frac{6\ \text{V}}{300\ \Omega} = 0.02\ \text{A} = 20\ \text{mA}, \qquad
P = VI = 6 \times 0.02 = 0.12\ \text{W} = I^2 R = 0.02^2 \times 300.
$$

Thirty minutes is 0.5 h or 1800 s, so

$$
E = 0.12 \times 0.5 = 0.06\ \text{Wh} = 0.12 \times 1800 = 216\ \text{J},
$$

and the two agree because $$0.06 \times 3600 = 216$$. Sanity check: 0.12 W is
indicator-lamp scale, far below a phone charger's 5 W to 20 W. The lab prints
exactly these values. Now try one before reading on: a 4 V source and a 200 Ω
resistor for 2 hours (Knowledge Assessment question 2).

### Example 2: the loaded voltage divider

A 12 V source feeds two 10 kΩ resistors in series; the junction is the output.

```text
  in (12 V) o----[ R_top 10 kOhm ]----o out
                                      |
                              +-------+--------+
                        [ R_bottom ]       [ R_load ]
                          10 kOhm            10 kOhm
                              |                |
   0 (ground) o---------------+----------------+
```

Unloaded: $$V_{\text{out}} = 12 \times 10\,000/20\,000 = 6\ \text{V}$$. With a
10 kΩ load,
$$R_{\text{bottom}} \parallel R_L = 5000\ \Omega$$ and

$$
V_{\text{loaded}} = 12 \times \frac{5000}{10\,000 + 5000} = 4\ \text{V},
$$

a loading error of $$-2\ \text{V}$$ or $$-33.3\ \%$$. The Thevenin route agrees
in one line: $$V_{\text{th}} = 6\ \text{V}$$, $$R_{\text{th}} = 5000\ \Omega$$,
$$V_{\text{loaded}} = 6 \times 10\,000/15\,000 = 4\ \text{V}$$.

KCL at the output: $$(12 - 4)/10\,000 = 0.8\ \text{mA}$$ arrives through the top
resistor and $$4/10\,000 = 0.4\ \text{mA}$$ leaves through each of the bottom
resistor and the load. Power: the source supplies
$$12 \times 0.8\ \text{mA} = 9.6\ \text{mW}$$ and the resistors dissipate
$$6.4 + 1.6 + 1.6 = 9.6\ \text{mW}$$. The lab reports `output_loaded` 4.0 V,
`loading_error_percent` -33.33 % and `thevenin_resistance` 5000 Ω.

### Example 3: a node with three branches, by hand and by the solver

```text
  n1 (12 V) o----[ R1 2 kOhm ]----o n2
     |                             |
   (V1 12 V)                 [ R2 4 kOhm ]    (I1 1.5 mA, driven from 0 into n2)
     |                             |                  |
   0 o-----------------------------+------------------+
```

Derivation 6 gave $$V_2 = 10\ \text{V}$$. Then $$I_{R1} = (12 - 10)/2000 = 1\ \text{mA}$$
into n2 and $$I_{R2} = 10/4000 = 2.5\ \text{mA}$$ out, and KCL balances:
$$1 + 1.5 = 2.5$$ mA. The resistors dissipate $$0.001^2 \times 2000 = 2\ \text{mW}$$
and $$0.0025 \times 10 = 25\ \text{mW}$$, 27 mW in all; the voltage source
supplies $$12 \times 1\ \text{mA} = 12\ \text{mW}$$ and the current source
$$10 \times 1.5\ \text{mA} = 15\ \text{mW}$$, also 27 mW.

`network --example two-source` reproduces this: n2 at 10.0 V, R1 current
0.001 A, R2 current 0.0025 A, dissipation and supply both 0.027 W to rounding,
`passes` true. The source powers are -0.012 W and -0.015 W to rounding:
supplied power is negative in the passive convention.

## Numerical or Simulation Lab

- Lab script: [`labs/foundations/dc_circuits.py`](../../../labs/foundations/dc_circuits.py)
  (Python 3.10+, standard library only; matplotlib optional, behind `--plot`).
- Everything it computes is an analytical or numerical teaching model of ideal
  elements, not validated hardware performance: no tolerance, temperature,
  source resistance or measurement error is modelled, and no measurements exist
  for this lesson. Closed-form results carry
  `"validation_status": "analytical-example"`, the Gaussian-elimination solver
  `"numerical-simulation"`.

### Functions, inputs and outputs

| Function | Inputs (SI unless stated) | Output |
| --- | --- | --- |
| `ohm(v, i, r)` | any two of voltage (V), current (A), resistance (Ω) | the third quantity and the power (W) |
| `power_energy(v, i, hours)` | voltage (V), current (A), duration in hours (h) | power (W), energy (J and Wh), duration (s) |
| `series_parallel(resistances, mode)` | resistances (Ω), `"series"` or `"parallel"` | equivalent resistance (Ω) and conductance (S) |
| `voltage_divider(v_in, r_top, r_bottom, r_load)` | source (V), resistances (Ω), optional load (Ω) | unloaded and loaded output, loading error, Thevenin values |
| `solve_network(branches, ground)` | `R`, `V`, `I` branches between named nodes | node voltages, branch currents and powers, conservation residuals and tolerances |
| `kcl_kvl_check(branch_currents, loop_voltages)` | signed currents at a node (A), signed drops round a loop (V) | sums, tolerance and pass flags |

### Commands and expected values

Run from the repository root; the default run prints the lesson example as
indented JSON.

```sh
python labs/foundations/dc_circuits.py
python labs/foundations/dc_circuits.py ohm --v 6 --r 300
python labs/foundations/dc_circuits.py power --v 6 --i 0.02 --hours 0.5
python labs/foundations/dc_circuits.py parallel 10000 10000
python labs/foundations/dc_circuits.py divider --v-in 12 --r-top 10000 --r-bottom 10000 --r-load 10000
python labs/foundations/dc_circuits.py network --example two-source
python labs/foundations/dc_circuits.py check --currents -0.0008 0.0004 0.0004 --voltages -12 8 4
```

The `check` currents follow the lab's sign convention, positive when leaving
the node. Default output, abbreviated (each quantity is a
`{"value": ..., "unit": ...}` pair, printed to full floating-point precision,
so 9.6 mW appears as 0.009600000000000001 W; the ohm is written `Ohm` for plain
ASCII):

```json
{
  "lab_version": "0.3.0",
  "ohm": {"current": {"value": 0.02, "unit": "A"}, "power": {"value": 0.12, "unit": "W"}},
  "power_energy": {"energy": {"value": 216.0, "unit": "J"}, "energy_watt_hours": {"value": 0.06, "unit": "Wh"}},
  "series": {"equivalent_resistance": {"value": 20000.0, "unit": "Ohm"}},
  "parallel": {"equivalent_resistance": {"value": 5000.0, "unit": "Ohm"}},
  "voltage_divider": {
    "output_unloaded": {"value": 6.0, "unit": "V"},
    "output_loaded": {"value": 4.0, "unit": "V"},
    "loading_error": {"value": -2.0, "unit": "V"},
    "loading_error_percent": {"value": -33.33333333333333, "unit": "%"},
    "thevenin_resistance": {"value": 5000.0, "unit": "Ohm"}
  },
  "network": {
    "validation_status": "numerical-simulation",
    "node_voltages": {"in": {"value": 12.0, "unit": "V"}, "0": {"value": 0.0, "unit": "V"}, "out": {"value": 4.0, "unit": "V"}},
    "checks": {"power_dissipated_by_resistors": {"value": 0.009600000000000001, "unit": "W"}, "passes": true}
  },
  "kcl_kvl_check": {"passes": true},
  "cross_check": {"difference": {"value": 0.0, "unit": "V"}}
}
```

### Validation checks

Each function raises `ValueError` with a specific message; the command line
prints `error:` and the message to stderr and exits with code 2. Try
`ohm --v 6` (under-determined), `ohm --v 6 --r 0` (an ideal source across an
ideal wire has no finite current), `ohm --v 6 --r -300` (negative resistance),
`ohm --v 6 --i 0.02 --r 400` (inconsistent), `parallel 100 0` (a 0 Ω branch
short-circuits the group), `divider --r-load 0`, and
`network --branch V,a,0,6 --branch V,a,0,5` (a loop of ideal voltage sources);
`nan`, `inf`, values beyond the floating-point range and floating nodes are
rejected too. No result ever contains `NaN` or infinity (`allow_nan=False`),
and the solver's `checks` report the tolerances behind `passes`.

### Reproducibility

Record the command, the Python version, the `lab_version` printed in every
result (0.3.0) and the output. The script uses no randomness and no clock, so
results are identical on any operating system; keep records locally in
`learning/`, not in the shared repository.

## Parameter Exploration

Each experiment changes one thing: predict first, run, then explain any
difference.

1. **Double the resistance.** Prediction: with 6 V fixed, current and power
   both halve. `ohm --v 6 --r 600` gives 0.01 A and 0.06 W. This relies on the
   fixed voltage; a battery that sags under load would not give exactly half.
2. **Sweep the load on the divider.** Prediction: the error magnitude is
   $$R_{\text{th}}/(R_{\text{th}} + R_L)$$ with $$R_{\text{th}} = 5\ \text{k}\Omega$$,
   so 1 kΩ, 10 kΩ, 100 kΩ and 1 MΩ loads give about -83 %, -33 %, -4.8 %
   and -0.5 %. `divider --v-in 12 --r-top 10000 --r-bottom 10000 --r-load R`
   reports 1.0 V, 4.0 V, 5.714 V and 5.970 V with errors -83.33 %, -33.33 %,
   -4.76 % and -0.50 %, approaching but never reaching 6 V. Adding
   `--plot --out loading.png` before `divider` draws this curve (optional
   matplotlib).
3. **Make the divider stiffer.** Keep the 10 kΩ load but use 1 kΩ and 1 kΩ.
   Prediction: $$R_{\text{th}}$$ falls to 500 Ω, so the error falls to
   $$-500/10\,500 = -4.76\ \%$$, while the divider's own current rises tenfold.
   `divider --v-in 12 --r-top 1000 --r-bottom 1000 --r-load 10000` gives
   5.714 V and `source_power_loaded` 0.0754 W against 0.0096 W for the 10 kΩ
   pair: accuracy traded for standing loss.
4. **Switch one source off in the network.** Prediction from superposition:
   8 V with the current source at zero (a plain 2 kΩ / 4 kΩ divider), 2 V with
   the voltage source at zero (1.5 mA into $$2000 \parallel 4000 = 1333.3\ \Omega$$).
   Run `network --branch V,n1,0,12 --branch R,n1,n2,2000 --branch R,n2,0,4000 --branch I,0,n2,0`,
   then the same command with `V,n1,0,0` and `I,0,n2,0.0015`. The two results
   add to the 10 V of the full circuit, as superposition requires.

## Common Misconceptions

- **"The resistor uses up the current."** The same current enters and leaves;
  energy is what is converted. Check: the lab's `node_current_sums` are zero to
  floating-point rounding (about $$10^{-19}$$ A) at every node.
- **"Watts and watt-hours are the same kind of thing."** A watt is a rate, a
  watt-hour an amount. Check: `power --v 6 --i 0.02 --hours 0.5` prints 0.12 W,
  0.06 Wh and 216 J together.
- **"A divider's output is fixed by its resistor ratio."** Only with nothing
  connected. Check: run `divider` with and without `--r-load 10000` and watch
  6 V become 4 V.
- **"Adding a resistor always increases resistance."** In parallel it opens a
  new path and lowers it. Check: `parallel 10000 10000` gives 5000 Ω.
- **"A negative current or power means a mistake."** A sign reports direction
  relative to the reference arrow, or supply rather than absorption. Check: in
  the default network the source shows -0.0096 W (to rounding) while the
  resistors' positive powers sum to 9.6 mW.
- **"Ohm's law applies to every component."** It describes linear resistors;
  diodes, lamps and transistors have no constant $$V/I$$ ratio. Check: the
  lab's `assumptions` list states when its numbers hold.

## AI Tutor Exercises

Give these prompts to the tutor; each asks it to hear your reasoning first.

1. **Diagnostic.** "Ask me to predict and justify what happens to current and
   power when the resistor across a fixed 6 V source changes from 300 Ω to
   600 Ω, before explaining anything or showing the lab's `ohm` output."
2. **Explain back.** "Ask me to explain without formulas why a divider's output
   falls when a load is connected, and which resistor carries the extra current.
   Correct me only after I have tried."
3. **Change one condition.** "Ask me to predict the 12 V, 10 kΩ / 10 kΩ
   divider's output with a 100 kΩ load before I run `divider --r-load 100000`,
   then what change would bring the error below 1 % and what it costs."
4. **Debug my work.** "I will paste my KCL equation for node n2 of the
   two-source network. Ask which sign convention I used for each branch before
   saying whether it is right, and withhold the corrected equation until I have
   attempted a fix."

## Knowledge Assessment

Questions 3, 5, 6 and 8 must be solved independently, without the answers or
the lab, before `f.dc-circuits` counts as `demonstrated`; if an answer was
shown, the tutor sets a fresh variant. The other questions may be worked with
help.

1. (Conceptual) A battery drives 20 mA through a resistor. Is the current
   leaving smaller than the current entering? What is used up, and where does
   it go?
2. (Numerical) A 4 V source feeds 200 Ω for 2 hours. Find the current in mA,
   the power in W and the energy in Wh.
3. (Numerical, transfer) An 8 V source feeds 400 Ω for 15 minutes. Find the
   current, the power and the energy in Wh and J; then halve the voltage with
   the same resistor and state how current and power change.
4. (Numerical) Find the equivalent resistance of three 10 kΩ resistors in
   parallel, and of 3 kΩ in parallel with 6 kΩ.
5. (Numerical) For the 12 V, 10 kΩ / 10 kΩ divider, what is the smallest load
   that keeps the loading error magnitude at or below 1 %?
6. (Numerical) In the two-source network the 1.5 mA source is reversed so that
   it pulls current out of n2 towards ground. Find the node voltage by KCL and
   confirm it by superposition.
7. (Conceptual) One learner writes the KVL sum of the loaded divider's source
   loop as $$+12 - 8 - 4 = 0$$, another as $$-12 + 8 + 4 = 0$$. Can both be
   right?
8. (Numerical) A divider has a 9 V source, 3 kΩ on top and 6 kΩ below. Find
   $$V_{\text{th}}$$ and $$R_{\text{th}}$$, then the output with a 6 kΩ load
   by both the Thevenin and the parallel-combination route.

<details><summary>Answers</summary>

1. No; current in equals current out. Energy is converted: electrical potential
   energy carried by the charge becomes heat in the resistor.
2. $$I = 4/200 = 20\ \text{mA}$$; $$P = 4 \times 0.02 = 0.08\ \text{W}$$;
   $$E = 0.08 \times 2 = 0.16\ \text{Wh}$$.
3. $$I = 8/400 = 20\ \text{mA}$$; $$P = 0.16\ \text{W}$$; 15 minutes is 0.25 h
   or 900 s, so $$E = 0.04\ \text{Wh} = 144\ \text{J}$$. At 4 V the current halves
   to 10 mA and the power quarters to 0.04 W, because $$P = V^2/R$$.
4. $$10\,000/3 = 3333.3\ \Omega$$; $$3000 \times 6000/9000 = 2000\ \Omega$$.
5. $$R_{\text{th}} = 5\ \text{k}\Omega$$ and $$R_{\text{th}}/(R_{\text{th}} + R_L) \leq 0.01$$
   gives $$R_L \geq 99 \times 5000 = 495\ \text{k}\Omega$$.
6. KCL with 1.5 mA now leaving the node:
   $$(V_2 - 12)/2000 + V_2/4000 + 0.0015 = 0$$, so $$3V_2 = 18$$ and
   $$V_2 = 6\ \text{V}$$; superposition gives $$8 - 2 = 6\ \text{V}$$. The lab's
   `network` command with `--branch I,n2,0,0.0015` prints 6.000000000000001 V,
   which is 6 V to rounding.
7. Yes. They walked the loop in opposite directions, or one counted drops and
   the other rises as positive; KVL needs only one consistent choice.
8. $$V_{\text{th}} = 9 \times 6000/9000 = 6\ \text{V}$$,
   $$R_{\text{th}} = 3000 \times 6000/9000 = 2\ \text{k}\Omega$$;
   Thevenin: $$6 \times 6000/8000 = 4.5\ \text{V}$$; parallel:
   $$6000 \parallel 6000 = 3\ \text{k}\Omega$$ and $$9 \times 3000/6000 = 4.5\ \text{V}$$.

</details>

## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 6.002 — Circuits and Electronics (Spring 2007)
- https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/
  - Syllabus: https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/syllabus/
  - Lecture notes: https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/lecture-notes/

Supporting physics reference:

- MIT 8.02 — Physics II: Electricity and Magnetism (Spring 2007)
- https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/
  - Syllabus: https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/syllabus/
  - Readings: https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/readings/

Optional mathematics reference (slope and area ideas only):

- MIT 18.01SC — Single Variable Calculus (Fall 2010)
- https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/
  - Syllabus: https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/syllabus/

Relevant subjects:

- The lumped circuit abstraction, resistors, independent sources, Kirchhoff's
  laws, series and parallel reduction, dividers, Thevenin equivalents and the
  node method (6.002)
- Charge, electric potential, current and resistance as physical quantities
  (8.02)
- The derivative as a rate and the integral as an accumulated area, used here
  only to relate power to energy (18.01SC)

This lesson has been independently developed by AIPE Academy with reference to
the academic scope of the above courses. MIT OpenCourseWare is an external
educational resource released under its own licence (generally CC BY-NC-SA 4.0).
AIPE Academy is not affiliated with or endorsed by MIT.

### Other references

- Alexander and Sadiku, *Fundamentals of Electric Circuits*, McGraw Hill
  publisher record: https://www.mheducation.com/highered/product/Fundamentals-of-Electric-Circuits-Alexander.html
  (scope only; no content reproduced).

## Further Learning

- Next in the circuits track: energy storage dynamics, module `f.dynamics`
  (capacitors, inductors, RC and RL responses), then waveforms and AC, module
  `f.ac`; both are outlines at present. `f.computation` scripts such parameter
  sweeps; `f.linear-algebra` covers the solver's theory.
- Across domains, this lesson is a prerequisite of
  [Buck converter fundamentals](../../power-electronics/dc-dc-conversion/buck-converter-fundamentals.md)
  (module `pe.buck`), which reuses $$P = VI$$ and $$R = V^2/P$$, of
  [Three-phase system fundamentals](../../power-systems/ac-power-networks/three-phase-fundamentals.md)
  (module `ps.three-phase`), where KCL and KVL return with phasors, and of
  [Solar PV fundamentals](../../renewable-energy/solar-photovoltaics/solar-pv-fundamentals.md)
  (module `re.pv`). The lab
  [Predict and check an ideal buck converter](../../03-converters/buck-open-lab.md)
  starts from the same formulas.
- Validation status: no lesson here yet compares this model with a switching
  simulation or a measurement; the ngspice workflow referenced from the buck
  lab is the planned simulation check, and `f.magnetism` will examine the gap
  between ideal numbers and a multimeter reading. Hands-on competence needs a
  separate assessment.
