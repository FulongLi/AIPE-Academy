# Curriculum guide: writing and registering AIPE Academy content

This guide is for contributors adding or revising lessons, labs and metadata.
It describes the v0.2 standard lesson format, the catalogue record, the lab
contract, the academic reference rules and the review checklist.

## 1. Teaching philosophy in one paragraph

Accessible to a beginner, correct for an engineer. Physical intuition before
mathematics; mathematics introduced only when the step needs it; every symbol
defined with its SI unit; analytical results, numerical simulations and
physical validation clearly distinguished; original explanations, numbers,
exercises and code; external references used for scope, never copied. The
tutor asks for a prediction before revealing a result, and a module counts as
demonstrated only after independent work.

## 2. The standard lesson format (`format: aipe-lesson-v2`)

Copy `templates/lesson-template.md`. A standard lesson is a Markdown file with:

1. a single `# Title` first line (no YAML front matter; metadata lives in the
   catalogue);
2. the `> Module … / > Suggested time …` block and an opening paragraph;
3. exactly these thirteen `##` sections, in order:
   Learning Objectives · Prerequisites · Physical Intuition · Fundamental
   Principles · Mathematical Derivations · Worked Examples · Numerical or
   Simulation Lab · Parameter Exploration · Common Misconceptions · AI Tutor
   Exercises · Knowledge Assessment · Academic References · Further Learning.

Conventions:

- British English; 2,000–3,500 words of prose plus equations and code.
- Mathematics in kramdown/MathJax form: `$$ … $$` for display and inline.
- No images, Liquid tags or mermaid inside lessons (the website renders them
  with kramdown); text diagrams go in fenced code blocks.
- Relative repository links: labs as `../../../labs/<domain>/<file>.py`,
  other lessons by repository path. The website rewrites lesson links to site
  URLs and other repository links to GitHub.
- Worked-example numbers equal the lab's default output.
- Knowledge Assessment: at least six questions, answers in a
  `<details><summary>Answers</summary>…</details>` block, and a sentence saying
  which questions must be solved independently.
- Academic References: each course as `MIT <number> — <official title> (<Term
  Year>)` and its official URL, taken from the `verified` block of
  `references/mit-ocw-catalogue.json`, then the fixed non-affiliation
  paragraph. The build fails if a cited course's URL is missing from the text.

Existing v0.1 material (stage outlines, the Chinese first lesson, the migrated
buck tutorial) keeps `format: legacy`; improve it in place or write a new
standard lesson next to it rather than deleting it.

## 3. The catalogue record

Add one object to `curriculum/catalogue.json` (schema: `schemas/lesson.schema.json`).

| Field | Meaning |
| --- | --- |
| `slug` | stable id and URL segment; never change it once published |
| `domain`, `track`, `module` | taxonomy ids; the module must belong to the track and the track to the domain; `module` may be `null` only for `stage` and `guide` overviews |
| `covers` | further modules taught at introductory depth |
| `concept` | language-independent key shared by translations; one record per language per concept |
| `language` | `en` or `zh-CN`; `translation_status` is `original`, `reviewed-translation` or `machine-translation` |
| `type` | `lesson`, `tutorial`, `lab`, `guide` or `stage` |
| `status` | `outline` (planned coverage), `draft` (complete enough to study with care), `available` (ready) |
| `format` | `aipe-lesson-v2` or `legacy` |
| `prerequisites`, `next` | lesson slugs, cross-domain allowed, acyclic |
| `labs` | lab scripts the lesson uses (`labs/**/*.py`, must exist) |
| `academic_references` | ids from `references/mit-ocw-catalogue.json` |
| `tools` | open-source tools are the core path; proprietary tools must be `optional: true` |
| `references` | repository reference files or https URLs |

Then run `python scripts/build_catalogue.py` and the tests. Also add the lesson
to the right learning path stage in `curriculum/taxonomy.json` if it belongs to
one.

## 4. The lab contract

Labs are the reproducible half of a lesson. Mirror `labs/buck_open.py`:

- Python 3.10+, standard library only for calculations; matplotlib only behind
  an optional `--plot` flag with a lazy import and a graceful message.
- Module docstring: purpose, inputs with SI units, assumptions, outputs,
  validation checks, limits of the model, reproduction commands.
- Results are dicts; physical quantities are `{"value": x, "unit": "A"}`; include
  `model`, `validation_status` (`analytical-example` or `numerical-simulation`),
  `assumptions` and `limitations`.
- Validation: `ValueError` with a specific message for non-finite, non-positive
  or inconsistent inputs; never emit NaN or infinity; the CLI prints
  `error: …` to stderr and exits with code 2.
- Deterministic, SI units, default run under 3 seconds, JSON output.
- Tests in `tests/test_lab_<name>.py` (unittest): default values, trends,
  limiting cases, invalid inputs, a CLI smoke test and a CLI failure case.
- A passing lab is a model result. Say so in the lesson; it is not hardware
  validation.

## 5. Translations

Write the translation as a separate record with the same `concept`, its own
slug (the v0.1 convention appends `-zh`), its own source file and
`translation_status`. Never mix languages inside one lesson. The website shows
"also available in …" only for recorded pairs.

## 6. Status discipline

- `available` requires: standard format or a complete legacy lesson, a working
  lab or equivalent practical calculation, a self-assessment, and reviewed
  numbers.
- `draft` is complete enough to study with care; say what is missing in the
  text.
- `outline` is planned coverage; the website shows it as an outline and the
  tutor labels its own practice as tutor-generated.
- Modules with no lesson are `planned`; do not create empty lessons to change
  that.

## 7. Review checklist

- [ ] Thirteen sections, in order, exact headings; title line; no front matter.
- [ ] Every symbol defined with units; intuition before equations.
- [ ] Worked examples recomputed independently and equal to the lab output.
- [ ] Lab runs with defaults, rejects invalid inputs, tests pass on Windows and Linux.
- [ ] Analytical / numerical / hardware validation clearly distinguished.
- [ ] Misconceptions (≥4), tutor exercises that ask first, assessment (≥6) with
      withheld answers and an independence statement.
- [ ] Academic References from verified data with the non-affiliation paragraph;
      no copied external text, figures or problems.
- [ ] Catalogue record complete; `python scripts/build_catalogue.py --check` and
      `python -m unittest discover -s tests` pass.
