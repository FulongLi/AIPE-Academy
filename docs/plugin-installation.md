# Installing AIPE Academy for Codex and Claude Code

AIPE Academy ships one agent capability, `aipe-academy`, for two platforms. Both
load the same skill text (`skills/aipe-academy/SKILL.md`), follow the same
tutor workflow (`prompts/tutor-guide.md`) and call the same companion command
(`skills/aipe-academy/scripts/academy.py`). Nothing is duplicated between the
two integrations.

Requirements for either platform:

- Python 3.10 or newer on `PATH` (the labs and the companion command use only
  the standard library; matplotlib is optional for `--plot`).
- Normal access to your chosen agent platform. No API subscription beyond that,
  no proprietary engineering software, no cloud database. Learning records
  stay on your machine (`learning/`, git-ignored).

## Claude Code

### Install from the repository marketplace

In a Claude Code session:

```text
/plugin install aipe-academy --marketplace FulongLi/AIPE-Academy
```

Claude Code adds the `aipe-academy` marketplace from the GitHub repository,
opens the plugin's details and asks for a scope (user, project or local). The
same from a shell:

```sh
claude plugin marketplace add FulongLi/AIPE-Academy
claude plugin install aipe-academy@aipe-academy
```

Confirm it loaded: type `/` and look for `/aipe-academy:learn`, or run
`claude plugin list` in your shell.

### Use it

| Say or run | What happens |
| --- | --- |
| `/aipe-academy:learn` or "Teach me electrical engineering from the beginning." | Onboarding: three short diagnostic questions, a first task, then the first lesson. |
| "I want to learn power electronics using AIPE Academy." | The seven-stage path with G1/G2/G3 gates, starting at your first unmet prerequisite. |
| `/aipe-academy:explain Buck converter` or "Explain the operation of a Buck converter." | Intuition → switch states → volt-second balance → ripple → CCM/DCM, then the lab. |
| `/aipe-academy:lab three-phase-fundamentals` or "Run a simple three-phase power calculation." | Runs `labs/power-systems/three_phase.py`, asks for your prediction first. |
| "Help me understand how solar panels generate electricity." | The Solar PV lesson and `labs/renewable-energy/pv_model.py`. |
| "Continue my previous learning session." | Resumes from `learning/progress.json`; says so honestly if there is none. |
| `/aipe-academy:references buck converter` | MIT OpenCourseWare scope references with official links and the non-affiliation statement. |

The skill itself is `/aipe-academy:aipe-academy`; the four commands are thin
shortcuts to it.

### Develop or test without installing

```sh
git clone https://github.com/FulongLi/AIPE-Academy
cd AIPE-Academy
claude plugin validate .
claude --plugin-dir . plugin list
claude --plugin-dir .
```

## Codex

### Repository skill (no installation)

```sh
git clone https://github.com/FulongLi/AIPE-Academy
cd AIPE-Academy
codex
```

Codex discovers repository skills from `.agents/skills/`; this repository
provides `.agents/skills/aipe-academy/SKILL.md`, which points at the shared
skill. Type `$aipe-academy` (or `/skills`) to invoke it explicitly, or simply
say "Guide me through AIPE Academy from the beginning." Codex may also choose
the skill implicitly when a request matches its description.

### Personal installation

To use the skill from any folder, copy or symlink `skills/aipe-academy/` into
`~/.agents/skills/aipe-academy/` (Codex's user-level skills directory), or ask
Codex's skill installer to fetch it: `$skill-installer` with the GitHub path
`FulongLi/AIPE-Academy/skills/aipe-academy`. The companion command then needs
to know where the curriculum is: run it with `--repo <checkout>` or set
`AIPE_ACADEMY_ROOT`; without a checkout it prints the clone command.

## Any other AI assistant

Share the repository link or the local folder and say "Guide me through AIPE
Academy from the beginning." `START-HERE.md`, `AGENTS.md` and
`prompts/tutor-guide.md` carry the same workflow in plain Markdown.

## What was tested (2026-10-20, Windows 11, Python 3.10.11)

| Check | Platform / version | Result |
| --- | --- | --- |
| `claude plugin validate .` | Claude Code 2.1.303 | `Validation passed` (marketplace and plugin manifests) |
| `claude --plugin-dir . plugin list` | Claude Code 2.1.303 | `aipe-academy@inline · Version: 0.2.0 · Status: ✔ loaded` |
| Skill discovery | Codex CLI 0.163.0, `codex debug prompt-input` run inside the checkout | The model-visible skills list contains `aipe-academy` with the skill's description and file path |
| Companion command | `tests/test_academy_cli.py` | onboarding, lesson selection, prerequisite checks, record lifecycle and continuation, lab execution and rejection, reference retrieval, missing-dependency reporting |
| Packaging | `tests/test_plugin_packaging.py` | Agent Skills frontmatter rules, stub ↔ shared skill consistency, manifest fields, marketplace entry, `claude plugin validate` |
| CI | `.github/workflows/validate.yml` | installs the Claude Code CLI and runs `claude plugin validate .` and `claude --plugin-dir . plugin list` on every push |

Not executed here: an end-to-end interactive tutoring conversation driven by a
model inside Codex or Claude Code (requires an interactive session with the
user's account), and installation through the GitHub marketplace against the
upstream repository before this change is merged. The marketplace install
command works once `.claude-plugin/marketplace.json` is on the default branch
of `FulongLi/AIPE-Academy`; until then install with `--plugin-dir` or from a
fork: `/plugin install aipe-academy --marketplace <owner>/AIPE-Academy`.

## Fallbacks and troubleshooting

- `status` fails with "No AIPE Academy checkout found": pass `--repo`, set
  `AIPE_ACADEMY_ROOT` or clone the repository.
- `generated/lessons.json` missing: run `python scripts/build_catalogue.py`
  in the checkout (the published repository already contains it).
- matplotlib not installed: labs print JSON without plots; `--plot` is optional.
- ngspice not installed: not required; the Python labs cover the core
  calculations, and `check-tools` says what ngspice would add.
- Claude Code says the plugin has no components: the plugin root is the
  repository root (the folder containing `.claude-plugin/`), not a subfolder.
- Codex does not list the skill: the working directory must be the repository
  (or a parent of it) for repository skills; restart Codex after cloning.

## Uninstall

Claude Code: `claude plugin uninstall aipe-academy@aipe-academy` (add `--scope`
if you installed at project or local scope); the marketplace can be removed
with `claude plugin marketplace remove aipe-academy`. Codex: delete the
`~/.agents/skills/aipe-academy/` copy. Your `learning/` records are ordinary
files; keep or delete them as you wish.
