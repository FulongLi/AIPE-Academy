# Working in AIPE Academy

Determine the user's intent before acting:

- For repository development, research, editing or review, carry out the requested work. Do not start a tutoring interview with the maintainer.
- For a request to learn with this repository, follow `skills/aipe-academy/SKILL.md` (the shared Codex/Claude Code skill) and `prompts/tutor-guide.md`. They define the learning workflow; the learner does not need to write a detailed prompt. The companion command `python skills/aipe-academy/scripts/academy.py` answers curriculum questions deterministically.
- If a link is shared without a clear request, briefly explain that this is a guided learning repository and ask whether the user wants to start learning or inspect the project.

## Development rules

- The hand-maintained sources are `curriculum/taxonomy.json`, `curriculum/catalogue.json` and `references/mit-ocw-catalogue.json`; `generated/*` and `references/mit-ocw-baseline.md` / `references/academic-coverage-map.md` are generated. After editing sources run `python scripts/build_catalogue.py`, `python scripts/build_reference_docs.py` and `python -m unittest discover -s tests`.
- Keep lesson URLs (`/academy/<domain>/<slug>/`) and module ids stable; the website and the agents depend on them.
- New lessons follow `templates/lesson-template.md` and `docs/curriculum-guide.md`; labs follow the standard-library contract of `labs/buck_open.py`.
- Keep university course facts separate from AIPE Academy's proposed adaptations. Record source URLs, course edition/term, access limitations and verification dates. Do not describe a course outline as a completed lesson or claim to have read unavailable attachments. Network verification (`scripts/verify_academic_sources.py`) is deliberate, never part of the offline tests.
- Use original exercises and explanations. External materials retain their own licences (MIT OpenCourseWare is generally CC BY-NC-SA 4.0); never copy or closely paraphrase them, and never imply MIT affiliation or endorsement. See `references/academic-source-guidelines.md`.
- Save personal learning records locally (`learning/`, git-ignored); do not publish or commit them as part of routine curriculum work.
