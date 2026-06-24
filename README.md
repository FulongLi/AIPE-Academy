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

1. Foundations
   - electricity, voltage, current, power, and energy
   - basic circuit laws and measurement thinking
   - math tools used in power electronics

2. Electronic Components
   - resistors, capacitors, inductors, diodes, MOSFETs, IGBTs, SiC, and GaN
   - ideal behavior versus real-world parasitics
   - datasheet reading and component selection

3. Conversion Principles
   - buck, boost, buck-boost, flyback, forward, half-bridge, and full-bridge converters
   - PWM, duty cycle, ripple, efficiency, and loss
   - continuous and discontinuous conduction modes

4. Control and Simulation
   - feedback loops, compensation, stability, and transient response
   - SPICE, Python, MATLAB-style analysis, and digital control basics
   - AI-assisted simulation workflows

5. Power Devices and Gate Driving
   - MOSFET, IGBT, SiC MOSFET, and GaN HEMT behavior
   - gate drivers, dead time, isolation, protection, and layout influence
   - switching loss, ringing, EMI, and thermal constraints

6. Systems and Applications
   - motor drives, EV power systems, solar inverters, chargers, UPS, and grid converters
   - reliability, safety, standards awareness, and design tradeoffs
   - project reviews and design documentation

7. From Learner to Contributor
   - build small converter projects
   - document learning notes and experiments
   - contribute tutorials, simulations, diagrams, and AI prompts back to the community

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

Current starter structure:

```text
.
├── index.html
├── styles.css
├── assets/
│   └── hero-power-electronics-ai.png
├── README.md
└── LICENSE.md
```

Planned structure:

```text
curriculum/
  00-orientation/
  01-foundations/
  02-components/
  03-converters/
  04-control-and-simulation/
  05-devices-and-gate-driving/
  06-systems/
  07-projects/

prompts/
  ai-tutor-prompts.md
  project-review-prompts.md
  simulation-helper-prompts.md

labs/
  spice/
  python/
  hardware/
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
