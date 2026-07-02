# Spirit Connect Academy

Spirit Connect Academy is an open-source learning framework for power electronics education in the AI era.

The goal is simple: a learner with only a computer, curiosity, and an AI coding assistant should be able to move from zero background to practical power electronics capability through a structured, project-based path.

This repository is the public front door for that vision. It will host the learning map, teaching materials, project briefs, simulation tasks, lab-style exercises, and AI interaction prompts that help students learn power electronics step by step.

## Why This Exists

Traditional engineering education is powerful, but it is often expensive, slow, and hard to personalize. AI changes the learning interface.

Spirit Connect Academy treats AI as a one-on-one mentor that can:

- explain concepts at the learner's level
- turn theory into simulations and small experiments
- review calculations, code, and design choices
- guide students through a curriculum without requiring a formal university setting

The long-term vision is to make power electronics education open, practical, and accessible to junior high students, high school students, self-taught engineers, and industry beginners.

## Learning Path

The curriculum is designed as a progressive syllabus rather than a collection of disconnected notes.

The first domain track is power electronics. Its technical direction is inspired by the learning philosophy behind Robert W. Erickson and Dragan Maksimovic's *Fundamentals of Power Electronics*: build from first principles, understand steady-state converter behavior, move into modeling and control, and then connect theory to practical engineering constraints.

This project does not copy textbook content. It uses original explanations, learning maps, simulations, projects, and AI tutor prompts.

1. Orientation
   - what power electronics is and why it matters
   - DC-DC, AC-DC, DC-AC, and AC-AC conversion
   - applications in chargers, EVs, solar, batteries, motor drives, servers, and the grid

2. Foundations
   - voltage, current, power, energy, KCL, KVL, and equivalent circuits
   - capacitors, inductors, transients, waveforms, average value, and RMS
   - the minimum math and measurement thinking used in power electronics

3. Components
   - resistors, capacitors, inductors, transformers, diodes, MOSFETs, IGBTs, SiC, and GaN
   - ideal behavior versus real-world parasitics
   - datasheet reading, component selection, thermal limits, and packaging

4. Converters
   - buck, boost, buck-boost, flyback, forward, half-bridge, full-bridge, and resonant converter awareness
   - PWM, duty cycle, ripple, efficiency, and loss
   - continuous and discontinuous conduction modes

5. Modeling and Control
   - averaged models, small-signal thinking, transfer functions, and Bode plots
   - feedback loops, compensation, stability, and transient response
   - voltage-mode control, current-mode control, and digital control awareness

6. Practical Design
   - magnetics, gate driving, isolation, protection, PCB layout, EMI, and thermal design
   - measurement artifacts, safe lab habits, first-power-up checklists, and design reviews
   - engineering tradeoffs between efficiency, cost, density, reliability, and safety

7. Systems and Applications
   - motor drives, EV power systems, solar inverters, chargers, UPS, storage, server power, and grid converters
   - requirements, reliability, manufacturability, standards awareness, and product tradeoffs
   - project documentation and specialization paths

## AI-Native Study Loop

Each topic should eventually include:

- a plain-language explanation
- a concept map
- example calculations
- simulation tasks
- hands-on or lab-style exercises
- common mistakes
- AI tutor prompts
- self-check questions
- extension challenges

The intended workflow is:

1. Read the topic brief.
2. Ask an AI mentor to explain it at your level.
3. Run a simulation or calculation.
4. Compare the result with the expected behavior.
5. Ask the AI to challenge your understanding.
6. Record what you learned.
7. Move to the next project.

## Repository Structure

Current structure:

```text
.
+-- index.html
+-- styles.css
+-- assets/
|   +-- hero-power-electronics-ai.png
+-- curriculum/
|   +-- README.md
|   +-- 00-orientation/
|   +-- 01-foundations/
|   +-- 02-components/
|   +-- 03-converters/
|   +-- 04-modeling-and-control/
|   +-- 05-practical-design/
|   +-- 06-systems-and-applications/
+-- prompts/
|   +-- ai-tutor-prompts.md
+-- references/
|   +-- power-electronics-reading-map.md
+-- templates/
|   +-- topic-template.md
+-- README.md
+-- LICENSE.md
```

Planned expansion:

```text
labs/
  spice/
  python/
  hardware/

projects/
  beginner/
  intermediate/
  advanced/

diagrams/
  concept-maps/
  converter-current-paths/
  system-block-diagrams/
```

## Website

Open `index.html` in a browser to view the current static showcase page.

No build step is required.

## Contributing Direction

Good contributions should help learners move from confusion to capability.

Useful contribution types include:

- beginner-friendly explanations
- diagrams and concept maps
- converter design walkthroughs
- simulation files
- Python analysis notebooks
- datasheet reading guides
- safety notes
- AI prompt templates
- project briefs with expected learning outcomes

## License

The repository currently includes a Creative Commons Attribution 4.0 International license in `LICENSE.md`, suitable for open educational content.

