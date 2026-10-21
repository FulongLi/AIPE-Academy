# AIPE — Academy

**English** | [简体中文](README.zh-CN.md)

AIPE Academy is the open, AI-native learning platform of **AI for Power Engineering**: Foundations,
Power Electronics, Power Systems and Renewable Energy. One knowledge base, maintained here, is served
through three interfaces - GitHub, the [AIPE website](https://aipel.co.uk/academy/) and AI coding agents
(a Codex skill and a Claude Code plugin) - so that a learner with a computer, curiosity and an AI
assistant can move from zero background to genuine engineering capability through guided study,
reproducible calculations and simulations.

## Features

- Four-domain knowledge architecture (Domain → Track → Module → Lesson → Lab; 57 modules) with
  cross-domain prerequisites and learning paths, including the seven-stage power-electronics path with
  G1/G2/G3 gates
- One complete thirteen-section reference lesson with a Python lab per domain; the catalogue says which
  other modules are outlines or planned
- Reproducible standard-library Python labs: JSON output with units, stated assumptions, invalid inputs
  rejected
- Verified MIT OpenCourseWare baseline (22 courses) mapped to modules; metadata and links only
- AI tutor workflow shared by the Codex skill and the Claude Code plugin, with a deterministic companion
  command and local, uncommitted learning records
- Deterministic generated catalogue (`generated/`) feeding the website

## Installation

Claude Code: `/plugin install aipe-academy --marketplace FulongLi/AIPE-Academy`. Codex: clone and open
the repository (`$aipe-academy`). Other assistants: share the repository link and say "Guide me through
AIPE Academy from the beginning". Labs and the companion command need only Python 3.10 or newer; the
validation tools need:

```sh
python -m pip install -r requirements-dev.txt
```

## Usage

```sh
python labs/power-electronics/buck_switching.py          # time-domain buck simulation, CCM/DCM detection
python skills/aipe-academy/scripts/academy.py status     # companion command used by both agent integrations
python scripts/build_catalogue.py --check                # taxonomy, catalogue, references, generated outputs
python -m unittest discover -s tests -v
```

The tutor finds your starting point with short diagnostic tasks, teaches intuition before equations, runs
the labs with you and keeps progress in a local, never-committed `learning/` folder.

## Project Information

- Version: 0.2.0 (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`)
- Status: Prototype (`aipe.yaml`: `active` / `prototype`); four complete reference lessons, most modules
  outlined or planned
- Developer: Fulong Li
- Organisation: Spirit Connect / AIPE Labs
- License: CC BY 4.0 ([LICENSE.md](LICENSE.md)) for the content, code and metadata here. External academic
  references, including MIT OpenCourseWare, keep their own licences and are linked, not copied; AIPE
  Academy is not affiliated with or endorsed by MIT

## Documentation

- [Start here](START-HERE.md) · [Curriculum](curriculum/README.md) ·
  [Curriculum overview and learning paths](docs/learning-paths.md)
- [Plugin installation for Codex and Claude Code, and what was tested](docs/plugin-installation.md)
- [Architecture](docs/architecture.md) · [Curriculum guide for contributors](docs/curriculum-guide.md) ·
  [Development, validation and repository structure](docs/development.md)
- [MIT OpenCourseWare baseline](references/mit-ocw-baseline.md) ·
  [Academic coverage map](references/academic-coverage-map.md) ·
  [Academic source guidelines](references/academic-source-guidelines.md)
- [Website integration](docs/website-integration.md) ·
  [v0.2 implementation report](docs/v0.2-implementation-report.md) ·
  [v0.1 ecosystem notes](docs/ecosystem-v0.1.md)
- [Tutor workflow](prompts/tutor-guide.md) · [Capability manifest](aipe.yaml) · [AGENTS.md](AGENTS.md)
