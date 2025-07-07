# 🔋 Double Pulse Test (DPT) Platform

This repository provides documentation, scripts, and guidelines for conducting **Double Pulse Testing (DPT)** on power semiconductor devices such as **IGBTs**, **SiC MOSFETs**, and **GaN HEMTs**. DPT is a widely adopted method to evaluate **switching behavior**, **losses**, and **dynamic performance** of power devices under realistic operating conditions.

---

## 📘 Principle of Double Pulse Test

The Double Pulse Test applies two sequential gate pulses to the Device Under Test (DUT) in a half-bridge configuration:

1. The **first pulse** builds up current in the inductor.
2. The **second pulse** initiates the switching event, allowing measurement of the device’s dynamic behavior at a known current level.

This enables accurate characterization of:

- **Turn-on and turn-off switching transients**
- **Switching losses (E<sub>on</sub>, E<sub>off</sub>)**
- **Voltage/current overshoots**
- **Parasitic effects** such as ringing and crosstalk

---

## 🧰 Test Setup

A typical DPT setup includes the following components:

- **Half-bridge test board** with low-inductance layout
- **Gate driver** with isolated power supplies and adjustable gate resistance
- **Load inductor** to set the desired test current
- **DC-link capacitor** (low ESL film or ceramic types)
- **Current sensing**: Rogowski coil, current transformer (CT), or shunt resistor
- **Voltage sensing**: High-bandwidth differential voltage probe
- **Oscilloscope**: ≥ 500 MHz bandwidth and ≥ 1 GS/s sampling rate

You may also require a digital delay generator and external logic isolators for precise timing.

---

## ⚡ Testing Tips by Device Type

| Device Type   | Gate Drive Recommendation       | Measurement Notes                            | Safety & Notes                              |
|---------------|----------------------------------|-----------------------------------------------|----------------------------------------------|
| **IGBT**      | +15V/-5V, soft turn-off R<sub>g</sub> | Moderate switching speed, V<sub>CE</sub> overshoot | Tail current must be captured accurately     |
| **SiC MOSFET**| +18V/-5V or -4V, low R<sub>g</sub>   | Fast dV/dt and dI/dt; high voltage overshoot   | Layout parasitics critical to performance     |
| **GaN HEMT**  | 0/6V or 0/5V, very low R<sub>g</sub> | Ultra-fast switching; potential for ringing    | Use coaxial probing, precise dead-time control|

---

## 🎛️ Measurement & Waveform Capture

- **Voltage probe**: Use a high-voltage differential probe rated above V<sub>ds</sub>/V<sub>ce</sub> of DUT
- **Current probe**: Prefer Rogowski coils or CTs with high bandwidth; shunt resistors may distort fast edges
- **Oscilloscope settings**:
  - ≥ 1 GS/s sampling rate
  - Disable bandwidth limit
  - Use **single-shot trigger mode**
- **Triggering**:
  - Trigger on gate signal or inductor current step
  - Ensure horizontal delay is adjusted to observe both pre- and post-switching events

---

## 🧮 Post-Processing of Waveforms

Use MATLAB or Python (NumPy, SciPy, matplotlib) for waveform processing and loss calculation.

### ⚙️ Switching Loss Calculations

\[
E_{on} = \int_{t_{on\_start}}^{t_{on\_end}} V_{ds}(t) \cdot I_d(t) \, dt
\]
\[
E_{off} = \int_{t_{off\_start}}^{t_{off\_end}} V_{ds}(t) \cdot I_d(t) \, dt
\]

### 📊 Additional Metrics

- **Voltage/current overshoot**
- **Ringing frequency**
- **dV/dt and dI/dt estimation**
- **Thermal energy estimation over multiple switching cycles**

Example scripts will be included in the `/scripts` directory for automated waveform processing.

---

