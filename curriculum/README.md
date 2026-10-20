# Curriculum

AIPE Academy organises knowledge in four domains, each a tree of tracks and
modules ([taxonomy.json](taxonomy.json)), and attaches lessons, labs,
tutorials, guides and stage outlines to modules through
[catalogue.json](catalogue.json). Learning paths are a separate dimension: a
recommended order through the modules, with readiness gates.

For a guided first session, use [Start here](../START-HERE.md); AI tutors
follow the [shared skill](../skills/aipe-academy/SKILL.md) and the
[tutor workflow](../prompts/tutor-guide.md).

## Four domains

| Domain | Folder(s) | Complete reference lesson |
| --- | --- | --- |
| Foundations | `00-orientation/`, `01-foundations/` (v0.1), `foundations/` (v0.2) | [DC circuit fundamentals](foundations/circuits/dc-circuit-fundamentals.md); Chinese first lesson and prerequisite path in `01-foundations/` |
| Power Electronics | `02-components/` … `06-systems-and-applications/` (v0.1 stages), `power-electronics/` (v0.2) | [Buck converter fundamentals](power-electronics/dc-dc-conversion/buck-converter-fundamentals.md), then the [open Buck lab](03-converters/buck-open-lab.md) and the [Buck design tutorial](03-converters/buck-converter.md) |
| Power Systems | `power-systems/` | [Three-phase system fundamentals](power-systems/ac-power-networks/three-phase-fundamentals.md) |
| Renewable Energy | `renewable-energy/` | [Solar PV fundamentals](renewable-energy/solar-photovoltaics/solar-pv-fundamentals.md) |

Lesson URLs on the website are `/academy/<domain>/<slug>/` and never depend on
these folders, so v0.1 files stay where they are. New lessons go into
`<domain>/<track>/` and follow [templates/lesson-template.md](../templates/lesson-template.md)
(see [docs/curriculum-guide.md](../docs/curriculum-guide.md)).

## The power-electronics learning path (seven stages, preserved)

This track was the first domain inside AIPE Academy and remains its most
developed learning path (`power-electronics-core` in taxonomy.json):

1. [Orientation](00-orientation/README.md): understand what power electronics is and why it matters.
2. [Foundations](01-foundations/README.md): build the electrical, mathematical and measurement intuition needed for the field (F00–F09), introduced as tasks require them.
3. [Components](02-components/README.md): learn the real parts that make power converters possible.
4. [Converters](03-converters/README.md): study the core switching topologies and their steady-state behaviour (readiness check G1).
5. [Modeling and Control](04-modeling-and-control/README.md): learn how converters behave dynamically and how to regulate them (G2).
6. [Practical Design](05-practical-design/README.md): connect theory to magnetics, layout, EMI, thermal design, protection and safety.
7. [Systems and Applications](06-systems-and-applications/README.md): understand how converters become products and infrastructure (G3).

A later Research phase will build on demonstrated design skills through
literature study, reproduction and original investigation; it remains a
planned progression. The curriculum is inspired by the learning philosophy
behind Robert W. Erickson and Dragan Maksimović's *Fundamentals of Power
Electronics* and benchmarked against MIT 6.622 (see
[references/](../references/mit-ocw-baseline.md)); it copies neither.

## Learning loop

Every topic follows the same learner-centred loop:

1. Start with a plain-language explanation and a prediction question.
2. Build a mental model, then do the minimum mathematics.
3. Run a reproducible calculation or simulation and compare it with the prediction.
4. Interpret waveforms, numbers and trade-offs; change one parameter at a time.
5. Ask the AI tutor to challenge your understanding with a fresh task.
6. Record what changed in your thinking (locally, in `learning/`).
7. Move to the next module along your path.

## Status vocabulary

`available` lessons are complete; `draft` lessons are complete enough to study
with care; `outline` records describe planned coverage; modules without any
lesson are `planned`. The generated catalogue
([generated/lessons.json](../generated/lessons.json),
[generated/knowledge-graph.json](../generated/knowledge-graph.json)) is the
authoritative list.
