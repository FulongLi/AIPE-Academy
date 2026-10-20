# Lesson title (one line, no front matter)

> Module: `<domain>.<module-id>` · Level: beginner | undergraduate | graduate · Status: outline | draft | available
> Suggested time: NN minutes · Labs: `labs/<domain>/<script>.py`

One or two sentences stating the engineering question this lesson answers and
why a learner should care. Keep the first paragraph free of equations.

## Learning Objectives

After this lesson the learner can:

- objective 1 (observable: explain, calculate, predict, compare ...)
- objective 2
- objective 3

## Prerequisites

- What the learner must already be able to do, each item linked to the lesson
  or module that teaches it. Use module ids from `curriculum/taxonomy.json`.
- Mathematics is introduced only where this lesson needs it; say which parts.

## Physical Intuition

Plain-language picture of the phenomenon before any mathematics. Use an
everyday analogy, a thought experiment or a prediction question the tutor can
ask ("if we double R, what happens to I?").

## Fundamental Principles

Definitions, physical laws and the model assumptions, each symbol defined with
its SI unit. State clearly what is idealised (ideal source, lossless switch,
constant temperature ...).

## Mathematical Derivations

Step-by-step derivations with kramdown/MathJax display mathematics:

$$
I = \frac{V}{R}
$$

Introduce advanced mathematics only when the derivation needs it, and say so.

## Worked Examples

At least two fully worked numerical examples with SI units, intermediate steps
and a sanity check (order of magnitude, limiting case). Use the same numbers as
the lab's default inputs so learners can verify them by running the script.

## Numerical or Simulation Lab

- Lab script: `labs/<domain>/<script>.py` (Python 3.10+, standard library;
  optional plotting with matplotlib).
- Input specifications, model assumptions, SI units, expected outputs.
- Exact commands to run, and the expected JSON values for the default case.
- Validation checks the script performs and the errors it raises for invalid
  input.
- Reproducibility: record inputs, command, software version and output.

## Parameter Exploration

Three or more experiments where one parameter changes at a time, each with a
prediction to make before running and the physical interpretation afterwards.

## Common Misconceptions

Misconception → why it is wrong → how to check it yourself. At least four.

## AI Tutor Exercises

Prompts a learner can give an AI tutor, written so the tutor asks before it
tells: diagnostic question, explain-back, change-one-condition, debug-my-work.
Do not reveal solutions here.

## Knowledge Assessment

Five or more questions with a mix of conceptual and numerical items. Put the
answers in a separate `<details>` block (or a clearly marked answer list at the
end of the section) so a tutor can withhold them. Mark which questions must be
solved independently before the module counts as `demonstrated`.

## Academic References

### MIT OpenCourseWare

Primary academic reference:

- MIT 6.XXX — Course Title (Term Year)
- https://ocw.mit.edu/courses/<slug>/

Relevant subjects:

- subject 1
- subject 2

This lesson has been independently developed by AIPE Academy with reference to
the academic scope of the above course. MIT OpenCourseWare is an external
educational resource released under its own licence (generally CC BY-NC-SA 4.0).
AIPE Academy is not affiliated with or endorsed by MIT.

### Other references

- Textbook or standard, publisher record URL only; no copied content.

## Further Learning

- Next lesson(s) in this track and the module ids they teach.
- Related lessons in other domains (cross-domain prerequisites and follow-ons).
- Which later lesson or lab validates this model against a switching
  simulation or measurement.
