# Development, validation and repository structure

## AI-native tutoring

The shared tutor workflow ([prompts/tutor-guide.md](../prompts/tutor-guide.md)) defines seven workflows: start learning, explain a topic, learn by simulation, check understanding, continue learning, explore advanced topics, and learning records. The Codex skill and the Claude Code plugin load the same skill text ([skills/aipe-academy/SKILL.md](../skills/aipe-academy/SKILL.md)) and call the same companion command, which answers curriculum questions deterministically from the generated catalogue:

```sh
python skills/aipe-academy/scripts/academy.py status
python skills/aipe-academy/scripts/academy.py onboarding --goal "solar"
python skills/aipe-academy/scripts/academy.py prerequisites buck-converter-fundamentals
python skills/aipe-academy/scripts/academy.py lab three-phase-fundamentals -- --help
python skills/aipe-academy/scripts/academy.py references --lesson solar-pv-fundamentals
```

Learning records live in `learning/progress.json` (git-ignored); `demonstrated` is recorded only for independent work. The tutor never claims to remember progress that is not in the record. Installation details for Codex and Claude Code and what has been tested: [plugin-installation.md](plugin-installation.md).

## Website

<https://aipel.co.uk/academy/> is generated from this repository at a pinned revision: lessons, the knowledge graph topics, prerequisites and the academic references all come from `generated/`. Each website lesson links its canonical Markdown source here, its lab scripts and its external academic references. See [website-integration.md](website-integration.md).

## Repository structure

```text
.
├── README.md · README.zh-CN.md · START-HERE.md · AGENTS.md · aipe.yaml
├── curriculum/
│   ├── taxonomy.json            Domain → Track → Module, learning paths, G1/G2/G3 gates
│   ├── catalogue.json           one record per lesson, lab, tutorial, guide or stage outline
│   ├── 00-orientation … 06-systems-and-applications/   v0.1 stage outlines and lessons (preserved)
│   ├── foundations/ · power-electronics/ · power-systems/ · renewable-energy/   v0.2 lessons
├── labs/                        standard-library Python labs (buck_open.py and labs/<domain>/)
├── references/                  MIT OCW catalogue, verification, coverage, baseline, guidelines; v0.1 reviews
├── schemas/                     lesson, taxonomy and academic-reference JSON Schemas
├── scripts/                     build_catalogue.py · build_reference_docs.py · verify_academic_sources.py
├── generated/                   lessons.json · knowledge-graph.json · academic-references.json
├── prompts/ · templates/        tutor workflow, lesson and learning-record templates
├── skills/aipe-academy/         shared Codex / Claude Code skill and companion command
├── .agents/skills/aipe-academy/ Codex repository-discovery entry
├── .claude-plugin/              Claude Code plugin and marketplace manifests
├── tests/ · .github/workflows/  offline tests, lab runs, plugin validation
└── docs/                        architecture, curriculum guide, plugin installation, website integration
```

## Development and validation

```sh
python -m pip install -r requirements-dev.txt
python scripts/build_catalogue.py --check        # taxonomy, catalogue, references, generated outputs
python scripts/build_reference_docs.py --check   # Markdown references rendered from JSON
python -m unittest discover -s tests -v          # curriculum, taxonomy, references, labs, CLI, packaging
claude plugin validate .                         # Claude Code plugin manifest (optional, needs the CLI)
python scripts/verify_academic_sources.py        # network re-verification of the MIT OCW pages (on demand)
```

CI (`.github/workflows/validate.yml`) runs the offline checks, every lab with its default inputs, the companion command and the Claude Code plugin validation on every push; the network verification of the MIT OpenCourseWare pages runs on demand only.

Architecture and contribution details: [architecture.md](architecture.md), [curriculum-guide.md](curriculum-guide.md).

## Contributing direction

Good contributions help learners move from confusion to capability: beginner-friendly explanations, standard-format lessons for planned modules, reproducible labs and tests, translations with reviewed status, datasheet reading guides, safety notes, and tutor exercises. Follow the curriculum guide and the academic source guidelines; never copy external course material.

## Ecosystem

AIPE Academy is the education capability of the AIPE ecosystem (`aipe.yaml`). The v0.1 integration notes remain in [ecosystem-v0.1.md](ecosystem-v0.1.md).
