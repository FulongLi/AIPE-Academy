# Power Electronics Learning Track

This track is the first domain inside AIPE Academy.

For a guided first session, use [Start here](../START-HERE.md). Before the domain stages, diagnose the learner's needs using the [foundation prerequisite path](01-foundations/prerequisite-path.zh-CN.md). Its F-series modules are submodules of Foundations, not additional academy phases.

These seven stages form the Education phase. A later Research phase will build on demonstrated design skills through literature study, reproduction, and original investigation. See the [foundation review and proposed progression](../references/erickson-foundation-review.zh-CN.md); the research curriculum remains a discussion draft.

The goal is to make power electronics learnable by anyone with curiosity, a computer, and an AI mentor. It is designed for beginners, but it should also remain useful for engineers who want a structured review path.

The curriculum is inspired by the learning philosophy behind Robert W. Erickson and Dragan Maksimovic's *Fundamentals of Power Electronics*: start from first principles, build converter intuition, connect steady-state operation to modeling and control, and then move toward real engineering constraints.

This repository does not copy textbook content. It uses public educational structure, original explanations, simulations, projects, and AI-native study workflows.

## Seven Stages

1. Orientation: understand what power electronics is and why it matters.
2. Foundations: build the electrical, mathematical, and measurement intuition needed for the field.
3. Components: learn the real parts that make power converters possible.
4. Converters: study the core switching topologies and their steady-state behavior.
5. Modeling and Control: learn how converters behave dynamically and how to regulate them.
6. Practical Design: connect theory to engineering constraints such as magnetics, layout, EMI, thermal design, protection, and safety.
7. Systems and Applications: understand how converters become products and infrastructure.

## Learning Loop

Every topic should follow the same learner-centered loop:

1. Start with a plain-language explanation.
2. Build a mental model.
3. Do the minimum math.
4. Run a calculation or simulation.
5. Interpret waveforms and tradeoffs.
6. Ask an AI tutor to challenge your understanding.
7. Document what changed in your thinking.
8. Move to a slightly harder project.

## Track Outcomes

A learner who completes this track should be able to:

- explain what power electronics does in modern energy and electronic systems
- analyze basic DC-DC converter operation in steady state
- estimate duty cycle, ripple, power loss, efficiency, and thermal limits
- read basic component datasheets and identify practical constraints
- simulate converters and interpret voltage/current waveforms
- understand why feedback control is needed and what stability means
- recognize engineering risks in layout, isolation, EMI, thermal design, and high-voltage work
- complete small project briefs and communicate design decisions clearly

## Suggested Repository Flow

Use the stage folders in order. Each stage can contain topic files, simulations, project briefs, diagrams, and self-check questions.

For a new topic, copy the structure from `templates/topic-template.md`.

For AI-guided study, start with `prompts/ai-tutor-prompts.md`.
