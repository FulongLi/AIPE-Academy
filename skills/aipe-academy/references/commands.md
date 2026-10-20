# academy.py command reference

`python <skill-dir>/scripts/academy.py [--repo PATH] [--json] [--language en|zh] [--record PATH] <command> ...`

The repository root is discovered from `--repo`, `AIPE_ACADEMY_ROOT`, the
script location (the plugin root) or the current directory and its parents.
Exit codes: 0 success, 1 curriculum or record error (message on stderr),
2 a lab rejected its input.

| Command | Purpose | Example |
| --- | --- | --- |
| `status` | Checkout summary: domains, lesson counts by status, modules, learning paths, record location, Python version | `status --json` |
| `domains` | The four canonical domains with module coverage and entry lessons | `domains --language zh` |
| `tracks [--domain D]` | Tracks (Domain → Track → Module) | `tracks --domain power-systems` |
| `modules [--domain D] [--track T] [--status S]` | Knowledge modules with status `available`, `draft`, `outline` or `planned` | `modules --domain renewable-energy --status planned` |
| `module <id>` | One module: summary, prerequisites, related modules, lessons, academic references | `module pe.buck` |
| `lessons [--domain D] [--module M] [--lang en|zh-CN] [--status S] [--type T]` | Lesson records | `lessons --domain foundations --lang zh-CN` |
| `lesson <slug> [--content]` | Lesson metadata, prerequisite and next lessons, labs, references, translations; `--content` adds the Markdown | `lesson buck-converter-fundamentals --content` |
| `paths` / `path <id>` | Learning paths; `path` shows stages, gates and which gate modules the record marks demonstrated | `path power-electronics-core` |
| `onboarding [--goal TEXT] [--lang L]` | Diagnostic questions, first diagnostic task and entry lessons for the learner's goal | `onboarding --goal "learn solar"` |
| `prerequisites <slug>` | Prerequisite lessons (transitively) and module requirements, marked against the record | `prerequisites solar-pv-fundamentals` |
| `resume` | Current module, next task and recent history from the record; fails clearly when there is none | `resume --json` |
| `record init [--goal] [--lang] [--time] [--force]` | Create `learning/progress.json` | `record init --goal "power electronics" --lang en --time "3 h/week"` |
| `record show` | Print the record | |
| `record set [--module M] [--lesson S] [--next-task TEXT]` | Update the current position | `record set --lesson dc-circuit-fundamentals --next-task "loaded divider exercise"` |
| `record log --task T --mode independent|assisted --evidence E --status learning|needs_review|demonstrated [--lesson S] [--module M] [--help-given H]` | Append an attempt; `demonstrated` is refused for assisted work | |
| `lab <slug|labs/path> [--timeout S] -- [args]` | Run a lab script and relay its JSON; for a lesson with several labs the first listed runs and `other_labs` names the rest | `lab buck-converter-fundamentals -- --frequency 200000`; `lab labs/power-electronics/buck_switching.py` |
| `lab --list` | Lessons with labs | |
| `references [--domain D] [--module M] [--lesson S]` | Academic reference baseline (MIT OpenCourseWare) | `references --lesson three-phase-fundamentals` |
| `reference <id>` | One reference with verified facts, mapped modules and citing lessons | `reference mit-6-622-2023` |
| `search <text>` | Lessons, modules and references matching a word | `search "power factor"` |
| `check-tools` | Python version, matplotlib, numpy, ngspice, git, with fallbacks | |

## Lab flags

Each lab prints `--help`. Defaults reproduce the lesson's worked example.

- `labs/buck_open.py` — `--v-in --v-out --power --frequency --inductance` (ideal CCM buck; rejects CCM violations)
- `labs/power-electronics/buck_switching.py` — time-domain switching simulation; `--duty --load --frequency --inductance --capacitance --cycles --steps-per-cycle [--plot]`
- `labs/foundations/dc_circuits.py` — Ohm's law, power/energy, series/parallel, loaded divider, small nodal solver
- `labs/power-systems/three_phase.py` — balanced wye/delta quantities, P/Q/S, power factor correction, per-unit
- `labs/renewable-energy/pv_model.py` — single-diode PV module, I-V/P-V curve, MPP, irradiance/temperature sweeps, `--mppt` perturb-and-observe

Run `lab <slug> -- --help` for the authoritative flag list of each script.
