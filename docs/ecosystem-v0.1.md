# AIPE Academy v0.1 integration

AIPE means **AI for Power Engineering**. Power electronics is the primary v0.1
curriculum. Existing seven stages, the Chinese prerequisite bridge, first lesson,
tutor prompts, foundation reviews and original assets are retained. Future power
systems, machines, microgrids and energy topics can add `domain` and `track`
metadata without reorganising the present curriculum. No empty courses are implied.

## Academic coverage and readiness

This is AIPE's adaptation, not a university syllabus or endorsement. Erickson and
Maksimović's *Fundamentals of Power Electronics*, third edition (Springer, 2020),
is the academic reference and coverage benchmark. The publisher's public record
and teaching overview were checked on 2026-10-07; paid book contents and exercises
were not accessed or reproduced. Prior source investigations remain unchanged.

| Knowledge progression | Existing canonical location | v0.1 coverage |
| --- | --- | --- |
| Motivation and learning method | `00-orientation` | Stage outline |
| Quantities, physics, DC circuits, RLC, waveforms, switches, simulation | `01-foundations` | F00-F09 bridge and one original first lesson |
| Switch models, device limits, losses | `02-components` | Stage outline |
| Steady state, conduction modes, converter families | `03-converters` | Outline, migrated buck draft and runnable open lab |
| Dynamics, transfer functions, feedback | `04-modeling-and-control` | Stage outline; buck draft introduces an example |
| Magnetics, inductor/transformer design, thermal and layout | `05-practical-design` | Stage outline |
| Advanced modelling, control and system projects | `06-systems-and-applications` | Stage outline; detailed units deferred |
| Reproduction and original research | Existing reference/tutor documents | Proposed progression, no completed research course |

The beginner route starts with plain-language goals and diagnostic questions,
then units/algebra, basic physics, voltage/current/power/energy, DC circuits,
RLC dynamics, signals, switching, electronics and simulation literacy. Existing
G1/G2/G3 checks establish readiness from demonstrated skills, not reading counts.
The tutor identifies gaps and chooses original exercises. Learner records stay
local; they are not published by catalogue generation.

## Metadata and build

`curriculum/catalogue.json` is the sidecar metadata source. Keeping metadata in a
sidecar preserves existing source files and distinguishes stage outlines from
lessons. Each record has title, slug, domain, track, level, type, prerequisites,
learning objectives, next lessons, estimated minutes, tools, status and references.
References are slug IDs. Slugs are globally unique, with `-zh` for Chinese pages.
Every content edit changes its SHA-256 in the deterministic published catalogue.
Text hashes use UTF-8 with LF newlines so Windows and Linux checkouts agree.

```sh
python -m pip install -r requirements-dev.txt
python scripts/build_catalogue.py
python scripts/build_catalogue.py --check
python -m unittest discover -s tests -v
python labs/buck_open.py
```

The build rejects unresolved prerequisite/next IDs, cycles, duplicate slugs,
unsafe/missing source paths and mandatory proprietary tools. `estimated_time`
describes suggested study time, not tested completion time. Document status is
independent from schema validation or physical validation.

Website synchronization consumes `generated/lessons.json` plus pinned source
files and renders `/academy/<domain>/<slug>/`; URLs do not depend on folders.
Public readers use the website without a GitHub account. The Registry advertises
this capability through `aipe.yaml`. Engineering examples can map their SI inputs,
assumptions and computed evidence into Core; this release does not equate learner
progress records with a validated Engineering State.

## Open practice and migration

The complete first open lab uses only Python's standard library. It checks ideal
buck steady-state balance, ripple, units and CCM applicability. It does not claim
switching losses or real-world suitability. Jupyter/NumPy/SciPy and ngspice can
extend numerical and switching analysis; FreeCAD, KiCad and suitable open FEA
solvers support later design work. Tool choice must follow the physical problem.
Commercial variants remain optional and must identify licence requirements.

One English buck tutorial is migrated from the website under CC BY 4.0, retaining
author, original revision/hash, figures and download attribution in
`references/website-migration.json`. Liquid includes are converted to portable
Markdown. Its old URL remains available through the website's synchronization
mapping. Chinese posts and other educational articles stay at their original URLs
pending separate reviewed migrations. RESEARCH, BUILD and NEWS stay editorial.

Sources: [publisher record](https://link.springer.com/book/10.1007/978-3-030-43881-4),
[Erickson teaching overview](https://www.colorado.edu/faculty/erickson/teaching).
Original source materials retain their licences; this repository does not license
external textbooks or linked third-party software.
