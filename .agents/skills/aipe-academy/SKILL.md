---
name: aipe-academy
description: Guided, AI-native learning of electrical power and energy engineering with AIPE Academy's open curriculum (Foundations, Power Electronics, Power Systems, Renewable Energy). Use when a learner wants to learn or review electrical engineering, circuits, power electronics, buck/boost converters, three-phase power, solar PV or energy storage from the beginning or from a chosen topic, asks for an explanation, a calculation or simulation lab, a knowledge check, academic references (MIT OpenCourseWare scope), or wants to continue a previous AIPE Academy session.
license: CC-BY-4.0. Teaching content is original AIPE Academy material; external academic references keep their own licences.
compatibility: Requires Python 3.10+ and this AIPE Academy repository checkout. No API key, cloud database or proprietary software.
metadata:
  capability: aipe-academy
  version: "0.2.0"
  entry: codex-repository-skill
---

# AIPE Academy tutor (Codex entry point)

This is the Codex discovery entry for the AIPE Academy capability inside its
own repository (`.agents/skills/`). The complete, shared instructions live once
at `../../../skills/aipe-academy/SKILL.md` (repository path
`skills/aipe-academy/SKILL.md`) so that Codex and Claude Code teach from the
same text.

1. Read `skills/aipe-academy/SKILL.md` and follow it.
2. The companion command is `python skills/aipe-academy/scripts/academy.py`
   run from the repository root (`status --json` first).
3. The shared tutor workflow is `prompts/tutor-guide.md`.

To use the skill outside this repository, install the `skills/aipe-academy`
folder into `~/.agents/skills/` (or ask the Codex skill installer to fetch it
from https://github.com/FulongLi/AIPE-Academy) and point the command at a
checkout with `--repo` or `AIPE_ACADEMY_ROOT`.
