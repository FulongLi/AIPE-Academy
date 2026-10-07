# Buck converter: from principles to design

> Canonical teaching source: AIPE Academy. Adapted from Dr. Fulong Li's AIPE Labs
> article under CC BY 4.0; migration details are in `references/website-migration.json`.
> Start with the [open Python lab](buck-open-lab.md). MATLAB/PLECS and LTspice
> sections below are optional historical variants requiring their own licences;
> the core calculation lab needs only open-source Python. This tutorial remains a draft.

A supply rail gives you 24 V, but your load needs 12 V. A linear regulator would simply burn the difference as heat. How can a circuit step the voltage down efficiently, choose its components, hold the output steady, and become a board that works on the bench?

This tutorial follows one **24 V to 12 V, 30 W buck converter** through that process. Start with the energy flow, build and test a model, design feedback, then move towards a physical prototype. The same example connects the circuit theory of an undergraduate course to control modelling and practical engineering.

> **First draft — design example, not a validated reference board.** The numerical values below are analytical starting points. The accompanying MATLAB script and LTspice netlist are teaching resources; native simulator execution, completed PLECS/Simulink projects, a KiCad board and hardware measurements are not yet included. No efficiency or transient specification is claimed as a measured result.

**Reading route:** [principles](#principles) → [design](#design) → [open loop](#open-loop) → [models](#models) → [feedback](#feedback) → [implementation](#implementation) → [simulation](#simulation) → [PCB](#pcb) → [bench](#bench) → [product](#product).

This article is the step-down companion to [Boost Converter: From Zero to Everything](https://aipel.co.uk/resources/blog/boost-converter-from-zero-to-everything/). The two converters are deliberately mirror images: same 30 W, same 100 kHz, same 150 µH, and the same 0.5 nominal duty. Reading them side by side is the fastest way to see which properties belong to *switching conversion in general* and which belong to *one particular topology*. The sharpest difference — the boost's right-half-plane zero, absent here — appears in [Section 4](#models).

## 1. What is a buck converter? {#principles}

A buck converter is a switching DC–DC converter that lowers an input voltage to a lower output voltage. The basic circuit uses a controlled switch, a diode (or a second switch), an inductor and an output capacitor. It is non-isolated: input and output share a ground connection. In this topology, there is no transformer.

![Buck converter power schematic](../../assets/migrated/buck/circuit-buck.svg)

*Q1 is the high-side switch; D1 freewheels from the common return to the switch node. L1 feeds C2 and R1 in both intervals. C1 is the local input capacitor.*

Here Q is normally a high-side MOSFET. The diode cathode faces the switching node; its anode faces ground, so it conducts only when the switching node is pulled below ground. The inductor connects the switching node to the output; C and the load are connected in parallel. The inductor and capacitor together form a low-pass LC filter — remembering that will explain most of the buck's behaviour later.

A lower voltage does not make the losses disappear. With efficiency defined as output power divided by input power,

$$
\eta=\frac{P_{\mathrm{out}}}{P_{\mathrm{in}}},\qquad
I_{\mathrm{in}}=\frac{V_{\mathrm{out}}I_{\mathrm{out}}}{\eta V_{\mathrm{in}}}.
\tag{1}
$$

Delivering 30 W from 24 V draws 1.25 A at ideal efficiency, or about 1.39 A if efficiency is provisionally assumed to be 90%. That 90% is a sizing assumption, not a prediction. Note that unlike a linear regulator, the average input current is *lower* than the output current: the converter trades voltage for current rather than dissipating the surplus.

The basic diode buck regulates below its input. In normal operation, turning the high-side switch off interrupts the input path while inductor current freewheels through the diode. This does not provide galvanic isolation or protection against a shorted switch, stored output energy or every external backfeed path; those faults need separate protection.

### Analysis conventions

Unless stated otherwise, the first calculations assume ideal components, continuous conduction, a resistive load and small switching ripple. Lowercase quantities denote time-varying values; uppercase quantities denote steady-state values; a hat denotes a small perturbation. The input voltage is $$v_g$$, output voltage is $$v_o$$ and inductor current is $$i_L$$. L, C and R denote inductance, output capacitance and load resistance.

### Watch one switching cycle

Let the switching period be $$T_s=1/f_s$$. Duty ratio $$d$$ is the fraction of each period for which Q conducts; its steady-state value is $$D$$.

**Q on, diode off:** the input is connected to the inductor through the switch, so the switching node sits at $$v_g$$. The voltage across the inductor is $$v_g-v_o$$, which is positive, so its current rises while it delivers energy to the output and capacitor. For ideal components,

$$
L\frac{di_L}{dt}=v_g-v_o,\qquad C\frac{dv_o}{dt}=i_L-\frac{v_o}{R}.
\tag{2}
$$

**Q off, diode on:** the inductor current cannot stop instantly, so it pulls the switching node below ground until the diode conducts and provides a return path. The switching node sits near zero, the inductor sees $$-v_o$$, and its current falls. For ideal components,

$$
L\frac{di_L}{dt}=-v_o,\qquad
C\frac{dv_o}{dt}=i_L-\frac{v_o}{R}.
\tag{3}
$$

Notice that in **both** intervals the inductor stays connected to the output, so the inductor current is continuous and the capacitor only has to absorb its ripple. This is the structural reason a buck output is quiet — and, as we will see, the reason its *input* current is the choppy one.

An inductor obeys $$v_L=L\,di_L/dt$$, so its current cannot change instantaneously under a finite voltage. This continuity is what lets it keep delivering current when the switch opens. Its stored energy is $$E_L=Li_L^2/2$$.

![Gate, inductor voltage and current, and capacitor current over two cycles](../../assets/migrated/buck/buck-waveforms.svg)

*Read down one dashed switching boundary: the gate changes the inductor voltage, which changes the current slope. The current itself stays continuous. The plotted values use the nominal example.*

[Open the interactive switching explorer](https://aipel.co.uk/resources/blog/buck-converter-from-zero-to-everything/#principles).

### Derive the conversion ratio

In periodic steady state, the energy-storage states repeat after each switching period. Integrating the inductor and capacitor laws gives **inductor volt-second balance** and **capacitor charge balance**:

$$
\int_0^{T_s}v_L(t)\,dt=0,\qquad
\int_0^{T_s}i_C(t)\,dt=0.
\tag{4}
$$

With small ripple in continuous conduction mode, applying the volt-second balance to the two inductor voltages gives

$$
D(V_g-V)+(1-D)(-V)=0,
\tag{5}
$$

which simplifies to

$$
\boxed{V=D V_g},\qquad
\boxed{D=\frac{V}{V_g}}.
\tag{6}
$$

The average capacitor current is zero, and because the inductor feeds the output in both intervals,

$$
I_L=\frac{V}{R}=I_o.
\tag{7}
$$

At 24 V input and 12 V output, the ideal duty is 0.5, and the inductor carries the full 2.5 A load current. These relations describe the ideal CCM steady state; parasitic losses and discontinuous conduction change the result. Unlike the boost ratio $$V_g/(1-D)$$, the buck ratio $$DV_g$$ is linear and bounded — the output cannot exceed the input, and there is no runaway as duty approaches one.

### CCM and DCM

In **continuous conduction mode (CCM)** the inductor current stays above zero. In **discontinuous conduction mode (DCM)** it falls to zero and remains there for part of the switching period, because the diode blocks reverse current. DCM introduces a third interval in which both the switch and diode are off.

The CCM equations below cannot simply be extended into DCM. At light load, observe the inductor current and change the model if the operating mode changes. (A synchronous buck, with a second switch replacing the diode, can instead allow reverse current and stay in CCM down to no load — a design choice with its own trade-offs.)

## 2. Turn a requirement into component values {#design}

Before selecting parts, write down the operating envelope. Here is the provisional specification for our teaching example.

| Quantity | Starting value or objective |
|---|---|
| Input voltage | 24 V nominal; 20–28 V design range |
| Output voltage | 12 V |
| Maximum output power | 30 W |
| Rated output current | 2.5 A |
| Nominal resistive load | 4.8 Ω |
| Switching frequency | 100 kHz |
| Inductor | 150 µH starting value |
| Output capacitance | 100 µF effective starting value |
| Steady switching-ripple objective | Below 60 mV peak-to-peak; to be verified |
| Topology | Single-phase, diode-rectified (asynchronous) buck |

The effective capacitance means the value available in operation, including tolerance and any voltage dependence. Transient voltage excursion is a separate requirement from switching ripple; we will establish it when choosing the control bandwidth and load-step specification.

### Size the inductor

During the on interval the inductor sees $$v_g-v_o$$, giving the approximate peak-to-peak ripple

$$
\Delta i_{L,\mathrm{pp}}=\frac{(V_g-V)D}{Lf_s}=\frac{V(1-D)}{Lf_s}.
\tag{8}
$$

At the nominal operating point, choosing 150 µH gives

$$
\Delta i_{L,\mathrm{pp}}=
\frac{12\times0.5}{150\times10^{-6}\times100\times10^3}
=0.40\ \mathrm{A}.
\tag{9}
$$

The average inductor current equals the load current, 2.5 A, so

$$
I_{L,\mathrm{pk}}\approx I_L+\frac{\Delta i_{L,\mathrm{pp}}}{2}=2.70\ \mathrm{A},
\tag{10}
$$

$$
I_{L,\mathrm{rms}}\approx\sqrt{I_L^2+\frac{\Delta i_{L,\mathrm{pp}}^2}{12}}\approx2.50\ \mathrm{A}.
\tag{11}
$$

Now check the input range — and notice the direction is the opposite of a boost. Writing $$\Delta i_{L,\mathrm{pp}}=V(1-V/V_g)/(Lf_s)$$ shows the ripple *grows* with input voltage. The worst case is therefore at the maximum 28 V input, where $$D=0.429$$ and the ripple is about 0.457 A, giving a 2.73 A peak. Size the inductor and choose the current limit for that condition, not the nominal one.

Choose saturation and thermal current ratings with allowance for tolerance, temperature, startup and the intended current limit. A part rated only for the nominal 2.70 A peak leaves too little information to make that decision.

The ideal CCM boundary occurs at $$I_L=\Delta i_{L,\mathrm{pp}}/2$$. At the nominal point,

$$
I_{o,\mathrm{boundary}}\approx\frac{\Delta i_{L,\mathrm{pp}}}{2}=0.20\ \mathrm{A}.
\tag{12}
$$

This is about 2.4 W at 12 V. The nominal CCM model therefore needs reconsideration near that light-load region, unless a synchronous stage keeps the current continuous.

### Size the capacitor

Here the buck differs sharply from the boost. Because the inductor current flows into the output node continuously, the capacitor only sees the *triangular ripple* current, not the full load current. Integrating that triangle over a half period gives

$$
\Delta v_{o,\mathrm{pp}}\approx\frac{\Delta i_{L,\mathrm{pp}}}{8Cf_s}.
\tag{13}
$$

For 100 µF at the nominal point, this is approximately 5 mV. This is the capacitive switching-ripple component only. In a real board the output-capacitor ESR and ESL usually dominate the measured ripple, so a low-ESR capacitor matters more than raw capacitance here.

The capacitor RMS current is correspondingly small:

$$
I_{C,\mathrm{rms}}\approx\frac{\Delta i_{L,\mathrm{pp}}}{\sqrt{12}}\approx0.12\ \mathrm{A}.
\tag{14}
$$

Contrast this with a boost, where the output capacitor must carry a pulsed current of over 1 A RMS for the same power. **In a buck the demanding capacitor is on the input side.** The switch draws a chopped current from the input, so the input capacitor must supply the difference between that pulsed draw and the smooth source current. A first estimate of its RMS current is

$$
I_{C_{\mathrm{in}},\mathrm{rms}}\approx I_o\sqrt{D(1-D)}\approx1.25\ \mathrm{A}
\tag{15}
$$

at the nominal point. Provide adequate input decoupling and check its ripple-current rating; skipping it is a common cause of input-rail noise and EMI.

For a sudden increase in load, the output capacitor initially supplies the current deficit until the inductor current can slew:

$$
\Delta v_o(t)\approx-\frac{1}{C}\int_0^t\Delta i_{\mathrm{deficit}}(\tau)\,d\tau.
\tag{16}
$$

This explains why a small calculated switching ripple does not guarantee a small load-transient dip. The inductor limits how fast current can change, so transient capacitance is often chosen by the load-step requirement, not by the ripple formula.

### Select devices and estimate losses

In the ideal circuit, the MOSFET off-state voltage and the diode reverse voltage are approximately the input voltage. Real devices must also tolerate switching overshoot and operating extremes. Check MOSFET conduction and switching losses, gate-drive requirements, diode forward loss and recovery, and inductor copper and core losses.

Useful first estimates are

$$
P_{Q,\mathrm{cond}}\approx D\left(I_L^2+\frac{\Delta i_L^2}{12}\right)R_{\mathrm{DS(on)}},
\qquad P_D\approx (1-D)V_F I_o,
\tag{17}
$$

$$
P_{Q,\mathrm{sw}}\approx\frac12 V_{\mathrm{in}}I_{\mathrm{sw}}(t_r+t_f)f_s,
\qquad P_{L,\mathrm{Cu}}=I_{L,\mathrm{rms}}^2r_L.
\tag{18}
$$

The diode conducts for the *off* fraction $$(1-D)$$, so its loss is often the largest single term in an asynchronous buck; replacing it with a second MOSFET (a synchronous buck) is the usual efficiency upgrade. The switching-loss expression is a rough overlap estimate, not a substitute for device waveforms or characterised switching energy. Temperature changes the parameters, and core loss requires a suitable magnetic model. [TI's power-stage calculation note](https://www.ti.com/lit/an/slva477b/slva477b.pdf) provides a useful independent buck component-sizing reference.

## 3. Build an open-loop simulation first {#open-loop}

Connect the source, switch, diode, inductor, capacitor and resistor. Set a 100 kHz PWM signal with duty 0.5. Plot inductor current, switch-node voltage and output voltage.

After startup, an ideal CCM circuit should approach 12 V with about 2.5 A average inductor current and 0.40 A ripple. A model containing voltage drops and resistance will differ. Record the cause rather than forcing every model to match the ideal calculation.

Next change input voltage while keeping duty fixed. The ideal gain predicts 10 V output at 20 V input and 14 V at 28 V input. That is the first reason to add feedback.

Then vary load. In an ideal CCM model the DC voltage gain $$D$$ is independent of R, although the transient and current change. In a real converter, losses cause a small load-dependent output error; at sufficiently light load, DCM also changes the gain. Distinguishing these effects is a useful modelling exercise.

Do not mistake a steady-state model for a startup model. Starting the capacitor at zero involves a large initial inductor-voltage and inrush that the two-interval CCM average model does not capture correctly. Use a switching model for startup and protection behaviour, and expect soft-start to be a real requirement.

## 4. Choose the right mathematical model {#models}

Each model answers a different question.

| Model | What it retains | What to use it for |
|---|---|---|
| Switching model | Individual on/off intervals | Ripple, device stress, startup and switching events |
| Nonlinear averaged model | Cycle-averaged energy flow | Slower trajectories while its conduction assumptions remain valid |
| Linear small-signal model | First-order changes around one operating point | Transfer functions, Bode plots and local feedback design |
| Sampled/discrete control model | Sampling, update timing and delay | Digital implementation and its additional stability limits |

For the ideal CCM converter with a resistive load, the averaged equations are

$$
L\frac{di_L}{dt}=d\,v_g-v_o,
\qquad
C\frac{dv_o}{dt}=i_L-\frac{v_o}{R}.
\tag{19}
$$

Here the variables represent cycle averages. The equations are still nonlinear because duty multiplies the input voltage. Averaging and linearisation are two different operations.

Write each variable as its operating point plus a small perturbation, such as $$d=D+\hat d$$ and $$v_o=V+\hat v_o$$. Removing the equilibrium terms and neglecting products of perturbations yields

$$
L\frac{d\hat i_L}{dt}=D\hat v_g+V_g\hat d-\hat v_o,
\tag{20}
$$

$$
C\frac{d\hat v_o}{dt}=\hat i_L-\frac{\hat v_o}{R}.
\tag{21}
$$

Holding input voltage fixed, the duty-to-output transfer function is

$$
\boxed{G_{vd}(s)=\frac{\hat v_o(s)}{\hat d(s)}
=\frac{V_g}{LCs^2+(L/R)s+1}}.
\tag{22}
$$

### Why the buck has no right-half-plane zero

This is the single most important control difference between the two converters. The buck's duty-to-output numerator is a **constant**, $$V_g$$ — there is no $$s$$ term, so there is no zero at all. Compare the boost, whose numerator $$(1-D)V-LI_Ls$$ produces a [right-half-plane zero](https://aipel.co.uk/resources/blog/boost-converter-from-zero-to-everything/#models) that adds phase lag and caps the achievable bandwidth.

The physical reason is structural. In a buck the inductor feeds the output in *every* interval, so raising the duty immediately raises the output — the response has the same sign as the command. In a boost, raising the duty first *disconnects* the output from the inductor for longer, so the output initially dips before it rises. The buck has no such inverse response, and that is precisely what a right-half-plane zero encodes.

The plant is a clean second-order low-pass filter. Its natural frequency and quality factor are

$$
\omega_0=\frac{1}{\sqrt{LC}},\qquad
Q=R\sqrt{\frac{C}{L}}.
\tag{23}
$$

For this example, $$f_0\approx1.30\ \mathrm{kHz}$$ and $$Q\approx3.92$$. Frequencies in hertz are angular frequencies divided by $$2\pi$$. The DC duty-to-output gain is simply $$V_g=24$$ V per unit duty, and with this light damping the response peaks near $$V_gQ\approx94$$ (about 39 dB) at $$f_0$$. That tall, lightly damped resonance — not a right-half-plane zero — is the obstacle the compensator must handle.

The line-to-output response $$G_{vg}=D/(LCs^2+(L/R)s+1)$$ and the output impedance $$Z_o=Ls/(LCs^2+(L/R)s+1)$$ share the same denominator. The general method for introducing perturbations and discarding the right terms is worked step by step in [Small-Signal Modelling from First Principles: A Boost Converter Walkthrough](https://aipel.co.uk/resources/blog/small-signal-modelling-boost-converter/); the algebra transfers directly, and the buck is the easier case because the numerator collapses to a constant.

![Negative feedback from measured output through controller and PWM](../../assets/migrated/buck/feedback-loop.svg)

*Start with the sign of the error: a low measured output should command the correction required by this plant. Include sensor and PWM gains before calculating the loop gain.*

## 5. Close the feedback loop deliberately {#feedback}

Start with voltage-mode control: measure output voltage, compare it with a reference, and use a compensator to adjust duty. The small-signal loop gain is

$$
T(s)=G_c(s)G_{\mathrm{PWM}}(s)G_{vd}(s)H(s),
\tag{24}
$$

where $$H$$ is the sensing path and $$G_{\mathrm{PWM}}$$ converts the controller output to duty. For an analogue ramp of peak-to-peak amplitude $$V_{\mathrm{ramp}}$$, its low-frequency gain is approximately $$1/V_{\mathrm{ramp}}$$. For a controller expressed directly in duty units, it is one before adding timing effects.

With negative feedback, the reference-to-output response is

$$
\frac{\hat v_o}{\hat v_{\mathrm{ref}}}
=\frac{G_cG_{\mathrm{PWM}}G_{vd}}{1+T}.
\tag{25}
$$

This reference is expressed in the same units as the sensed feedback. Rescaling the measurement changes the controller gains.

### A reproducible, intentionally slow first controller

For a teaching baseline, let the software reconstruct output voltage in volts, so $$H=1$$, and let the controller produce duty directly. Choose a PI controller:

$$
G_c(s)=K_p+\frac{K_i}{s},\qquad
K_p=8.0\times10^{-3}\ \mathrm{V}^{-1},\quad
K_i=8.0\ \mathrm{V}^{-1}\mathrm{s}^{-1}.
\tag{26}
$$

Its nominal crossover is about 31 Hz with a large phase margin. This is deliberately slow, and for a specific reason: the LC resonance near 1.30 kHz peaks at roughly 39 dB, so any proportional gain large enough to push crossover towards that peak makes the peak itself cross unity and creates extra gain crossings. A pure PI therefore cannot be both simple and fast on this plant. This controller demonstrates regulation; it is not offered as a production transient-performance design.

The [MATLAB analysis script](../../assets/migrated/buck/buck_ccm_analysis.m) builds the plant and controller, lists all stability margins and plots the small-signal responses. It requires MATLAB with Control System Toolbox. The supplied values and continuous-time stability have been independently checked numerically; the script has not yet been run in MATLAB.

### Move from the baseline to a useful design

1. Evaluate the plant over the input range, load range and component tolerances, keeping track of CCM/DCM boundaries. Remember the DC gain $$V_g$$ moves with input voltage.
2. Set transient-response objectives, then choose a candidate crossover well below the switching frequency. A common target is $$f_c\approx f_s/10$$; here that is 10 kHz, comfortably achievable *because there is no right-half-plane zero to limit it*.
3. To cross above the LC resonance you generally need Type III compensation: two zeros near $$f_0$$ to cancel the resonant phase drop, and two higher poles to attenuate switching noise. A PI alone cannot do this.
4. Include sensing filters, PWM gain, delay and parasitics. Inspect every gain crossing and the closed-loop poles, not only one displayed phase margin.
5. Aim initially for at least 60° phase margin and 10 dB gain margin across the specified CCM operating points; treat these as design objectives to be verified.
6. Check line steps, load steps, startup, duty saturation and recovery in the switching model. Establish a separate light-load strategy when DCM is involved.

A generic Type III form is

$$
G_c(s)=K\frac{(1+s/\omega_{z1})(1+s/\omega_{z2})}
{s(1+s/\omega_{p1})(1+s/\omega_{p2})}.
\tag{27}
$$

Do not place its poles and zeros by copying another converter's component values. They must work with this converter's measured or modelled plant.

Current-mode control adds an inner current loop. On a buck it is especially attractive: it effectively removes one pole from the voltage-loop plant, tames the resonant peak, and gives inherent cycle-by-cycle current limiting. Peak current-mode implementations still need slope compensation for duty above 0.5 and a sampled-current analysis where appropriate; the duty-to-voltage model above alone does not certify their stability.

## 6. Implement the controller: analogue or digital {#implementation}

These are two implementation routes built on the same power stage and feedback principles.

### Analogue route

A reference, output divider, error amplifier, compensation network, PWM comparator and gate driver form a basic voltage-mode implementation. A controller IC can integrate several of these blocks, and many buck controllers add a high-side gate driver with a bootstrap supply, which the diode version still needs for the single high-side switch.

For a divider,

$$
V_{\mathrm{fb}}=V_o\frac{R_{\mathrm{bottom}}}{R_{\mathrm{top}}+R_{\mathrm{bottom}}}.
\tag{28}
$$

A 1.2 V reference at 12 V output requires a nominal 0.1 sensing gain. Include this gain and the PWM ramp amplitude when translating a compensator into actual resistors and capacitors. The direct-duty PI numbers above cannot be pasted into an error-amplifier circuit without that scaling.

Use LTspice first with behavioural blocks, then with a suitable amplifier or controller model. Add output swing limits, supply rails and the gate driver. A linear compensator that asks its amplifier for an impossible voltage will not behave as the algebra predicts.

### Digital route

A microcontroller or DSP samples voltage with an ADC, computes a control action and updates a PWM peripheral. Set the sampling period to $$T_a$$, which is distinct from the switching period even if both are 10 µs in the first example.

For the PI above, Tustin discretisation uses

$$
\frac1s\approx\frac{T_a}{2}\frac{1+z^{-1}}{1-z^{-1}}.
\tag{29}
$$

The unsaturated incremental controller becomes

$$
u[k]=u[k-1]+\left(K_p+\frac{K_iT_a}{2}\right)e[k]
+\left(-K_p+\frac{K_iT_a}{2}\right)e[k-1].
\tag{30}
$$

Here $$u$$ is the duty correction, and $$e$$ is output-voltage error in volts. At $$T_a=10\ \mu\mathrm{s}$$, the two error coefficients are 0.00804 and −0.00796.

Add an operating duty bias or feedforward term and enforce bounds:

$$
d[k]=\operatorname{clip}\bigl(D_{\mathrm{ff}}[k]+u[k],d_{\min},d_{\max}\bigr),
\qquad D_{\mathrm{ff}}\approx\frac{V_{\mathrm{target}}}{v_g}.
\tag{31}
$$

Because the buck ratio is linear, this feedforward is exact in the ideal CCM case, and input-voltage feedforward makes the loop reject line changes almost immediately. Choose duty limits from the actual hardware. Add anti-windup so the integrator does not keep accumulating error while duty is limited; a separate integrator state with conditional integration or back-calculation makes this explicit. The incremental equation by itself has no anti-windup.

Account for ADC scaling, quantisation, PWM resolution, sample timing, computation time and when a new duty actually takes effect. An effective delay contributes approximately

$$
G_{\mathrm{delay}}(s)=e^{-sT_d},\qquad
\phi_{\mathrm{delay}}(\omega)=-\omega T_d.
\tag{32}
$$

Use a sampled-data model for the final digital stability check. Firmware must also define startup, shutdown, soft-start, fault handling and recovery. Fast overcurrent protection should not depend only on a slow voltage-regulation loop.

## 7. Keep the simulations comparable {#simulation}

Use the same parameter names, operating points and test events across tools.

| Environment | Suggested exercise | Current draft resource |
|---|---|---|
| PLECS | Ideal switched stage, averaged stage, then continuous and sampled control | Construction recipe below; native project pending |
| MATLAB/Simulink | Transfer functions, sampled PI, closed-loop system simulation | MATLAB analysis script supplied; native Simulink model pending |
| LTspice | Switching waveforms, then analogue compensation and device models | Open-loop starter netlist supplied; native execution pending |

[LTspice is available free from Analog Devices](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html), making it a useful accessible route for the circuit-level exercises. Access to PLECS and MATLAB/Simulink depends on the reader's licences.

### Construct the PLECS or Simulink models

For the switched model, use a DC source, high-side switch, diode, 150 µH inductor, 100 µF capacitor and 4.8 Ω resistor. Drive the switch with a 100 kHz pulse generator and observe the three waveforms listed earlier. Use switching-capable solver settings and repeat with a smaller step or tighter tolerance to check convergence.

For the averaged model, implement the two averaged derivatives with two integrators. Initialise them at 2.5 A and 12 V for local perturbation experiments. Close the loop with the PI, a duty limiter and an explicit anti-windup implementation. For digital control, add a zero-order-held measurement, a discrete controller and the intended PWM-update delay.

Do not use the averaged model to claim switching ripple: averaging has deliberately removed it.

### Open the LTspice starter

Download [buck_open_loop.cir](../../assets/migrated/buck/buck_open_loop.cir) and open it in LTspice. It uses a voltage-controlled switch, a simple diode and illustrative winding resistance, so the output will not be exactly the ideal 12 V. These are generic parts, not a selected production BOM.

Run its transient analysis and plot `V(out)`, `V(sw)` and `I(L1)`. Compare the last few switching periods with the earlier calculations. The switch is off at the start, so the output ramps up from zero when PWM begins; this is a PWM-enable transient, not a characterised startup. Increase the simulation duration if the waveform has not settled.

### Use a shared test sheet

At minimum, compare nominal operation, 20 V and 28 V input, half and full load, a half-to-full-load step, startup, duty limiting and light load near the CCM boundary. Separate small perturbations used for model validation from large events used to test nonlinear behaviour.

Record the simulator/version, component-model assumptions, timestep settings, steady output, ripple, peak current and transient recovery. Leave efficiency blank in an ideal model, or label its ideal result explicitly; useful loss estimates require lossy component models.

## 8. Move into KiCad and PCB design {#pcb}

The circuit diagram is only part of the hardware design. Before layout, add the gate driver and its bootstrap supply, local input decoupling, voltage and current sensing, protection, connector ratings and test points. Select real parts and check their footprints against manufacturer drawings.

A practical KiCad workflow is:

1. Capture the complete schematic and annotate component values and ratings.
2. Assign verified footprints and run electrical rules checks.
3. Place the input capacitor, high-side switch and diode to keep the high-frequency commutation loop short. **In a buck the hot loop is the input-capacitor → switch → diode → input-capacitor path**, because that is where the current is chopped — the opposite side from a boost. Put the input ceramic capacitor as close to the switch and diode as the layout allows.
4. Keep the switching node compact but small in copper area to limit radiated noise, route the gate-drive return closely, and keep sensitive feedback away from switching edges. Use Kelvin sensing where needed and plan return-current paths.
5. Size copper for current and temperature rise, then check clearances, thermal paths and manufacturability. The diode (or synchronous MOSFET) is often the dominant heat source.
6. Run design rules checks and inspect the board before generating Gerbers, drill files, BOM and assembly data.

Automation can help generate repetitive schematic content and organise layout. Electrical and design rules checks do not prove low EMI, correct loop compensation or adequate cooling. Those require engineering review and measurements.

A future downloadable KiCad project should identify its board revision and match the tested BOM. This draft does not yet include a routed or tested PCB.

## 9. Bring up the prototype and compare it with the model {#bench}

Begin with visual inspection, polarity and continuity checks. Verify auxiliary rails, controller operation, the bootstrap supply and PWM timing before sustained power conversion. Use a current-limited source and a defined load for staged power-up; choose the current limit and ramp procedure from the component limits.

Remember the direct input-to-output path when the switch is on: a stuck-on high-side switch places the full input on the load. Check probe grounding and voltage ratings before measuring the switching node, and discharge stored energy before handling the board.

Record:

- Output regulation over input and load range.
- Switching ripple with a documented probe connection and measurement bandwidth; expect ESR to dominate over the calculated capacitive ripple.
- Inductor current and switch-node stress, including startup and load changes.
- Input/output power at defined electrical boundaries, with instrument uncertainty.
- Temperatures after reaching an identified thermal condition, with attention to the diode.
- Line/load transients, limiting behaviour and recovery from intended fault tests.

Measured efficiency is

$$
\eta=\frac{\langle v_o(t)i_o(t)\rangle}{\langle v_g(t)i_g(t)\rangle}.
\tag{33}
$$

For sufficiently steady DC rails, products of DC readings may approximate these average powers. Include auxiliary supplies consistently and state what is included.

If the measurement disagrees with simulation, investigate the assumptions: effective capacitance and ESR, inductor DCR and saturation, diode drop, switching loss, sensor filtering, timing and layout parasitics. Update the model and repeat the test. That feedback is part of the converter's development process.

## 10. A working prototype is a milestone towards a product {#product}

A board that regulates at one operating point is a useful achievement. Turning it into a dependable product adds repeatability across component tolerances, temperature, production units, supply conditions and load behaviour.

The next work includes thermal design, EMI and EMC evaluation, protection coordination, reliability, sourcing, assembly and production testing. Applicable requirements depend on the end application; this teaching example does not establish product compliance.

Once the basic converter is understood, extensions include synchronous rectification (replacing the diode with a second switch for higher efficiency and controlled light-load behaviour), interleaving, current-mode control, better magnetics and application-specific optimisation. Each introduces new trade-offs and, often, new models.

The central habit remains the same: write down the requirement, explain the energy flow, calculate, simulate, build, measure and revise. A model is valuable because it helps you make and test a design decision.

**Read the step-up counterpart:** [Boost Converter: From Zero to Everything](https://aipel.co.uk/resources/blog/boost-converter-from-zero-to-everything/), and the derivation it builds on, [Small-Signal Modelling from First Principles](https://aipel.co.uk/resources/blog/small-signal-modelling-boost-converter/).

## Further study

Robert W. Erickson and Dragan Maksimović, [*Fundamentals of Power Electronics*, third edition, Springer, 2020](https://link.springer.com/book/10.1007/978-3-030-43881-4). Relevant chapters cover steady-state converter analysis, AC equivalent circuit modelling, converter transfer functions and controller design. The derivations and numerical example on this page are presented independently; this article is not a reproduction of the textbook.
