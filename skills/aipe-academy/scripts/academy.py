#!/usr/bin/env python3
"""AIPE Academy companion CLI for AI tutors (Codex skill and Claude Code plugin).

Standard library only. It reads the generated, versioned curriculum metadata of
an AIPE Academy checkout and gives a tutor deterministic answers to the
questions that recur in every learning session:

  status                 what this checkout contains and which tools are available
  domains / tracks / modules / module <id>
  lessons [filters] / lesson <slug> [--content]
  paths / path <id>      recommended learning progressions and their gates
  onboarding [--goal]    entry points and the first diagnostic questions
  prerequisites <slug>   prerequisite lessons and which ones the record shows as demonstrated
  resume                 what the local learning record says to do next
  record ...             create and update the learner's local progress record
  lab <slug|path> [...]  run a reproducible lab script and relay its JSON
  references [filters] / reference <id>
  search <text>
  check-tools            optional dependencies (matplotlib, ngspice, git)

Every command accepts --json for machine-readable output. The repository root is
found from --repo, the AIPE_ACADEMY_ROOT environment variable, the location of
this script (skills/aipe-academy/scripts/academy.py inside the repository) or by
walking up from the current directory. Personal learning records are written to
learning/progress.json (git-ignored) unless --record or AIPE_ACADEMY_RECORD
points elsewhere; nothing is sent anywhere.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = "0.2.0"
STATUSES = ("not_started", "learning", "needs_review", "demonstrated")
LANGUAGE_NAMES = {"en": "English", "zh-CN": "简体中文"}
CLONE_URL = "https://github.com/FulongLi/AIPE-Academy.git"


class AcademyError(Exception):
    pass


# ----------------------------------------------------------------------------
# Repository discovery and data access
# ----------------------------------------------------------------------------

def is_repo(path: Path) -> bool:
    return (path / "curriculum/catalogue.json").is_file() and (path / "generated/lessons.json").is_file()


def find_repo(explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("AIPE_ACADEMY_ROOT"):
        candidates.append(Path(os.environ["AIPE_ACADEMY_ROOT"]))
    here = Path(__file__).resolve()
    if len(here.parents) >= 4:
        candidates.append(here.parents[3])
    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])
    for candidate in candidates:
        try:
            if is_repo(candidate):
                return candidate.resolve()
        except OSError:
            continue
    raise AcademyError(
        "No AIPE Academy checkout found. Pass --repo <path>, set AIPE_ACADEMY_ROOT, or clone it:\n"
        f"  git clone {CLONE_URL}\n"
        "Then run the command again from inside that folder."
    )


class Academy:
    def __init__(self, root: Path):
        self.root = root
        self.lessons_doc = self._read("generated/lessons.json")
        self.graph = self._read("generated/knowledge-graph.json")
        self.references_doc = self._read("generated/academic-references.json")
        self.lessons = {row["slug"]: row for row in self.lessons_doc["lessons"]}
        self.domains = {d["id"]: d for d in self.graph["domains"]}
        self.tracks = {t["id"]: t for t in self.graph["tracks"]}
        self.modules = {m["id"]: m for m in self.graph["modules"]}
        self.paths = {p["id"]: p for p in self.graph["learning_paths"]}
        self.references = {c["id"]: c for c in self.references_doc["courses"]}

    def _read(self, relative: str):
        path = self.root / relative
        if not path.is_file():
            raise AcademyError(f"Missing {relative}; run python scripts/build_catalogue.py in the checkout")
        return json.loads(path.read_text(encoding="utf-8"))

    def label(self, item: dict, lang: str) -> str:
        title = item.get("title")
        if isinstance(title, dict):
            return title.get("zh" if lang.startswith("zh") else "en") or title.get("en", "")
        return str(title)

    def lesson(self, slug: str) -> dict:
        if slug not in self.lessons:
            close = [s for s in self.lessons if slug in s or s in slug]
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            raise AcademyError(f"Unknown lesson slug '{slug}'.{hint}")
        return self.lessons[slug]

    def lesson_modules(self, row: dict) -> list[str]:
        return ([row["module"]] if row.get("module") else []) + list(row.get("covers", []))


# ----------------------------------------------------------------------------
# Learning record (local, never committed)
# ----------------------------------------------------------------------------

class Record:
    def __init__(self, path: Path):
        self.path = path
        self.data = None
        if path.is_file():
            self.data = json.loads(path.read_text(encoding="utf-8"))

    @property
    def exists(self) -> bool:
        return self.data is not None

    def require(self) -> dict:
        if not self.exists:
            raise AcademyError(
                f"No learning record at {self.path}. There is no stored progress to resume; "
                "start with `onboarding`, or create a record with `record init`."
            )
        return self.data

    def init(self, goal: str | None, language: str | None, study_time: str | None, force: bool) -> dict:
        if self.exists and not force:
            raise AcademyError(f"A learning record already exists at {self.path}; use --force to replace it")
        self.data = {
            "schema_version": SCHEMA_VERSION,
            "created": today(),
            "updated": today(),
            "learner": {"goal": goal, "preferred_language": language, "available_study_time": study_time},
            "current": {"module": None, "lesson": None, "next_task": None},
            "module_status": {},
            "history": [],
        }
        self.save()
        return self.data

    def set_current(self, module: str | None, lesson: str | None, next_task: str | None) -> dict:
        data = self.require()
        for key, value in (("module", module), ("lesson", lesson), ("next_task", next_task)):
            if value is not None:
                data["current"][key] = value
        self.save()
        return data

    def log(self, lesson: str | None, module: str | None, task: str, mode: str, evidence: str, status: str, help_given: str | None) -> dict:
        data = self.require()
        if status == "demonstrated" and mode != "independent":
            raise AcademyError("Only independent work can be recorded as demonstrated; record assisted work as learning or needs_review and repeat with a fresh task")
        entry = {"date": today(), "lesson": lesson, "module": module, "task": task, "mode": mode, "evidence": evidence, "status": status, "help_given": help_given}
        data["history"].append(entry)
        if module:
            previous = data["module_status"].get(module, "not_started")
            data["module_status"][module] = status if STATUSES.index(status) >= STATUSES.index(previous) or status == "needs_review" else previous
        self.save()
        return data

    def demonstrated_modules(self) -> set[str]:
        if not self.exists:
            return set()
        return {m for m, s in self.data["module_status"].items() if s == "demonstrated"}

    def save(self) -> None:
        self.data["updated"] = today()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.render_markdown()

    def render_markdown(self) -> None:
        data = self.data
        lines = [
            "# My AIPE Academy learning record",
            "",
            f"- Updated: {data['updated']}",
            f"- Goal: {data['learner'].get('goal') or ''}",
            f"- Preferred language: {data['learner'].get('preferred_language') or ''}",
            f"- Available study time: {data['learner'].get('available_study_time') or ''}",
            f"- Current module: {data['current'].get('module') or ''}",
            f"- Current lesson: {data['current'].get('lesson') or ''}",
            f"- Next small task: {data['current'].get('next_task') or ''}",
            "",
            "## Module status",
            "",
            "| Module | Status |",
            "|---|---|",
        ]
        for module, status in sorted(data["module_status"].items()):
            lines.append(f"| {module} | {status} |")
        lines += ["", "## Module history", "", "| Date | Lesson | Module | Task | Independent or assisted | Evidence | Status |", "|---|---|---|---|---|---|---|"]
        for item in data["history"]:
            lines.append(f"| {item['date']} | {item.get('lesson') or ''} | {item.get('module') or ''} | {item['task']} | {item['mode']} | {item['evidence']} | {item['status']} |")
        lines += ["", "Statuses: not_started, learning, needs_review, demonstrated. `demonstrated` is recorded only for independent work. This file is generated from progress.json and is excluded from Git."]
        (self.path.parent / "progress.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def today() -> str:
    return dt.date.today().isoformat()


# ----------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------

def cmd_status(academy: Academy, args) -> dict:
    counts = {}
    for row in academy.lessons.values():
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    record = Record(record_path(academy, args))
    return {
        "repository": str(academy.root),
        "catalogue_schema": academy.lessons_doc["schema_version"],
        "domains": list(academy.domains),
        "lessons": len(academy.lessons),
        "lessons_by_status": dict(sorted(counts.items())),
        "modules": len(academy.modules),
        "modules_with_lessons": sum(1 for m in academy.modules.values() if m["lessons"]),
        "learning_paths": list(academy.paths),
        "academic_references": len(academy.references),
        "learning_record": str(record.path) if record.exists else None,
        "python": sys.version.split()[0],
    }


def cmd_domains(academy: Academy, args) -> list[dict]:
    rows = []
    for domain in sorted(academy.domains.values(), key=lambda d: d["order"]):
        modules = [m for m in academy.modules.values() if m["domain"] == domain["id"]]
        lessons = [row for row in academy.lessons.values() if row["domain"] == domain["id"]]
        rows.append({
            "id": domain["id"],
            "title": academy.label(domain, args.language),
            "summary": (domain["summary"].get("zh") if args.language.startswith("zh") else domain["summary"]["en"]),
            "tracks": domain["tracks"],
            "modules": len(modules),
            "modules_with_lessons": sum(1 for m in modules if m["lessons"]),
            "lessons": {s: sum(1 for row in lessons if row["status"] == s) for s in ("available", "draft", "outline")},
            "entry_lessons": [row["slug"] for row in lessons if row["status"] == "available" and row["type"] in ("lesson", "tutorial", "lab")],
        })
    return rows


def cmd_tracks(academy: Academy, args) -> list[dict]:
    rows = []
    for track in sorted(academy.tracks.values(), key=lambda t: (academy.domains[t["domain"]]["order"], t["order"])):
        if args.domain and track["domain"] != args.domain:
            continue
        rows.append({"id": track["id"], "domain": track["domain"], "title": academy.label(track, args.language), "modules": track["modules"]})
    return rows


def module_view(academy: Academy, module: dict, lang: str) -> dict:
    return {
        "id": module["id"],
        "domain": module["domain"],
        "track": module["track"],
        "parent": module.get("parent"),
        "title": academy.label(module, lang),
        "summary": module["summary"].get("zh" if lang.startswith("zh") else "en"),
        "status": module["status"],
        "requires": module["requires"],
        "related": module["related"],
        "lessons": [{"slug": s, "title": academy.lessons[s]["title"], "status": academy.lessons[s]["status"], "language": academy.lessons[s]["language"]} for s in module["lessons"]],
        "academic_references": [{**ref, "title": academy.references[ref["id"]]["title"], "course_number": academy.references[ref["id"]]["course_number"], "url": academy.references[ref["id"]]["url"]} for ref in module["academic_references"]],
        "legacy": module.get("legacy", {}),
    }


def cmd_modules(academy: Academy, args) -> list[dict]:
    rows = []
    for module in academy.modules.values():
        if args.domain and module["domain"] != args.domain:
            continue
        if args.track and module["track"] != args.track:
            continue
        if args.status and module["status"] != args.status:
            continue
        rows.append({"id": module["id"], "title": academy.label(module, args.language), "track": module["track"], "status": module["status"], "lessons": module["lessons"]})
    return rows


def cmd_module(academy: Academy, args) -> dict:
    if args.id not in academy.modules:
        raise AcademyError(f"Unknown module id '{args.id}'; list them with `modules`")
    return module_view(academy, academy.modules[args.id], args.language)


def lesson_summary(academy: Academy, row: dict) -> dict:
    return {"slug": row["slug"], "title": row["title"], "domain": row["domain"], "module": row["module"], "type": row["type"], "status": row["status"], "language": row["language"], "estimated_time": row["estimated_time"], "url": row["url"]}


def cmd_lessons(academy: Academy, args) -> list[dict]:
    rows = []
    for row in academy.lessons.values():
        if args.domain and row["domain"] != args.domain:
            continue
        if args.module and args.module not in academy.lesson_modules(row):
            continue
        if args.lang and row["language"] != args.lang:
            continue
        if args.status and row["status"] != args.status:
            continue
        if args.type and row["type"] != args.type:
            continue
        rows.append(lesson_summary(academy, row))
    return rows


def lesson_view(academy: Academy, row: dict, include_content: bool) -> dict:
    view = dict(row)
    view["source_path"] = str(academy.root / row["source"])
    view["prerequisite_lessons"] = [lesson_summary(academy, academy.lessons[s]) for s in row["prerequisites"]]
    view["next_lessons"] = [lesson_summary(academy, academy.lessons[s]) for s in row["next"]]
    view["module_titles"] = {m: academy.label(academy.modules[m], "en") for m in academy.lesson_modules(row)}
    view["academic_reference_details"] = [
        {"id": r, "course_number": academy.references[r]["course_number"], "title": academy.references[r]["title"], "term": academy.references[r]["term"], "url": academy.references[r]["url"]}
        for r in row["academic_references"]
    ]
    view["lab_paths"] = [str(academy.root / lab) for lab in row["labs"]]
    view["translations_available"] = {lang: slug for lang, slug in row["translations"].items() if slug}
    if include_content:
        view["content"] = (academy.root / row["source"]).read_text(encoding="utf-8")
    return view


def cmd_lesson(academy: Academy, args) -> dict:
    return lesson_view(academy, academy.lesson(args.slug), args.content)


def cmd_paths(academy: Academy, args) -> list[dict]:
    return [{"id": p["id"], "domain": p["domain"], "title": academy.label(p, args.language), "stages": [s["id"] for s in p["stages"]], "gates": list(p["gates"])} for p in academy.paths.values()]


def cmd_path(academy: Academy, args) -> dict:
    if args.id not in academy.paths:
        raise AcademyError(f"Unknown learning path '{args.id}'; list them with `paths`")
    path = academy.paths[args.id]
    record = Record(record_path(academy, args))
    demonstrated = record.demonstrated_modules()
    stages = []
    for stage in path["stages"]:
        stages.append({
            "id": stage["id"],
            "title": academy.label(stage, args.language),
            "gate": stage.get("gate"),
            "modules": [{"id": m, "title": academy.label(academy.modules[m], args.language), "status": academy.modules[m]["status"], "demonstrated": m in demonstrated} for m in stage["modules"]],
            "lessons": [{"slug": s, "title": academy.lessons[s]["title"], "status": academy.lessons[s]["status"], "language": academy.lessons[s]["language"]} for s in stage["lessons"]],
        })
    gates = {}
    for gate_id, gate in path["gates"].items():
        gates[gate_id] = {
            "title": academy.label(gate, args.language),
            "demonstrate": gate["demonstrate"],
            "missing": [m for m in gate["demonstrate"] if m not in demonstrated],
            "criteria": gate["criteria"].get("zh" if args.language.startswith("zh") else "en"),
        }
    return {"id": path["id"], "title": academy.label(path, args.language), "summary": path["summary"].get("zh" if args.language.startswith("zh") else "en"), "stages": stages, "gates": gates, "record_used": str(record.path) if record.exists else None}


GOAL_KEYWORDS = {
    "foundations": ["beginning", "basics", "zero", "scratch", "circuit", "electrical engineering", "foundation", "math", "从零", "基础", "电路", "入门"],
    "power-electronics": ["power electronics", "converter", "buck", "boost", "inverter", "switch", "电力电子", "变换器"],
    "power-systems": ["power system", "grid", "three-phase", "three phase", "transformer", "power flow", "电力系统", "电网", "三相"],
    "renewable-energy": ["solar", "pv", "photovoltaic", "wind", "battery", "storage", "renewable", "光伏", "太阳能", "风", "储能", "可再生"],
}
# Words that mean "start from the beginning"; only these keep Foundations in the match
# when a specialised domain also matches ("solar panels ... electricity" is renewable energy).
BEGINNER_WORDS = ["beginning", "basics", "zero", "scratch", "foundation", "从零", "基础", "入门"]


def cmd_onboarding(academy: Academy, args) -> dict:
    goal = (args.goal or "").lower()
    matched = [d for d, words in GOAL_KEYWORDS.items() if any(w in goal for w in words)]
    if len(matched) > 1 and "foundations" in matched and not any(w in goal for w in BEGINNER_WORDS):
        matched.remove("foundations")
    if goal and not matched:
        matched = ["foundations"]
    entries = []
    for domain_id in matched or list(academy.domains):
        path = next((p for p in academy.paths.values() if p["domain"] == domain_id), None)
        first_lesson = None
        if path:
            for stage in path["stages"]:
                for slug in stage["lessons"]:
                    row = academy.lessons[slug]
                    if row["status"] == "available" and (not args.lang or row["language"] == args.lang):
                        first_lesson = lesson_summary(academy, row)
                        break
                if first_lesson:
                    break
        entries.append({"domain": domain_id, "title": academy.label(academy.domains[domain_id], args.language), "learning_path": path["id"] if path else None, "first_available_lesson": first_lesson})
    return {
        "principle": "Find the learner's objective, prior knowledge and entry point with short diagnostic tasks, one question at a time; self-reported background alone is not evidence.",
        "diagnostic_questions": [
            "What would you like to be able to do or understand? (an everyday answer is fine)",
            "How comfortable are you with algebra and with the words voltage and current? ('I don't know' is a valid answer)",
            "How much time can you give per week?",
        ],
        "first_diagnostic_task": "Ask the learner to predict what happens to the current in a 6 V, 300 Ω circuit when the resistance doubles, then explain in their own words. The answer places them before or after f.dc-circuits.",
        "matched_domains": matched,
        "entry_points": entries,
        "advanced_learners": "A learner who names a specific topic may start there: run `prerequisites <slug>` and only the missing prerequisites are proposed.",
        "record_hint": "With a writable workspace create the local record (`record init`), otherwise return a copyable progress summary and say that nothing is stored.",
    }


def cmd_prerequisites(academy: Academy, args) -> dict:
    row = academy.lesson(args.slug)
    record = Record(record_path(academy, args))
    demonstrated = record.demonstrated_modules()
    seen: dict[str, dict] = {}

    def walk(slug: str, depth: int) -> None:
        for pre in academy.lessons[slug]["prerequisites"]:
            if pre in seen:
                continue
            pre_row = academy.lessons[pre]
            modules = academy.lesson_modules(pre_row)
            seen[pre] = {
                "slug": pre,
                "title": pre_row["title"],
                "status": pre_row["status"],
                "language": pre_row["language"],
                "modules": modules,
                "depth": depth,
                "demonstrated": bool(modules) and all(m in demonstrated for m in modules),
            }
            walk(pre, depth + 1)

    walk(row["slug"], 1)
    module_requirements = []
    for module_id in academy.lesson_modules(row):
        for required in academy.modules[module_id]["requires"]:
            module_requirements.append({"module": required, "title": academy.label(academy.modules[required], args.language), "demonstrated": required in demonstrated, "status": academy.modules[required]["status"]})
    unmet = [p for p in seen.values() if not p["demonstrated"]]
    return {
        "lesson": lesson_summary(academy, row),
        "prerequisite_lessons": sorted(seen.values(), key=lambda p: (p["depth"], p["slug"])),
        "module_requirements": module_requirements,
        "unmet_prerequisites": [p["slug"] for p in unmet],
        "record_used": str(record.path) if record.exists else None,
        "note": "Without a learning record nothing counts as demonstrated; use a short diagnostic task instead of assuming.",
    }


def cmd_resume(academy: Academy, args) -> dict:
    record = Record(record_path(academy, args))
    data = record.require()
    current = data["current"]
    suggestion = None
    if current.get("lesson") and current["lesson"] in academy.lessons:
        suggestion = lesson_summary(academy, academy.lessons[current["lesson"]])
    recent = data["history"][-3:]
    needs_review = [m for m, s in data["module_status"].items() if s == "needs_review"]
    return {
        "record": str(record.path),
        "updated": data["updated"],
        "learner": data["learner"],
        "current": current,
        "current_lesson": suggestion,
        "recent_history": recent,
        "needs_review": needs_review,
        "demonstrated_modules": sorted(record.demonstrated_modules()),
        "advice": "Check one earlier concept briefly before continuing; keep assisted and independent work separate; this record is the only memory the tutor has.",
    }


def cmd_record(academy: Academy, args) -> dict:
    record = Record(record_path(academy, args))
    if args.record_command == "init":
        return record.init(args.goal, args.lang, args.time, args.force)
    if args.record_command == "show":
        return record.require()
    if args.record_command == "set":
        if args.lesson and args.lesson not in academy.lessons:
            raise AcademyError(f"Unknown lesson slug '{args.lesson}'")
        if args.module and args.module not in academy.modules:
            raise AcademyError(f"Unknown module id '{args.module}'")
        return record.set_current(args.module, args.lesson, args.next_task)
    if args.record_command == "log":
        if args.lesson and args.lesson not in academy.lessons:
            raise AcademyError(f"Unknown lesson slug '{args.lesson}'")
        if args.module and args.module not in academy.modules:
            raise AcademyError(f"Unknown module id '{args.module}'")
        return record.log(args.lesson, args.module, args.task, args.mode, args.evidence, args.status, args.help_given)
    raise AcademyError("Unknown record command")


def resolve_lab(academy: Academy, target: str) -> tuple[Path, list[str]]:
    """Return the lab script for a lesson slug or a labs/ path, plus any further labs the lesson lists."""
    other_labs: list[str] = []
    if target in academy.lessons:
        labs = academy.lessons[target]["labs"]
        if not labs:
            raise AcademyError(f"Lesson '{target}' has no lab script")
        # A lesson lists its labs in teaching order; the first is the default, the others are reported.
        target, other_labs = labs[0], labs[1:]
    path = (academy.root / target).resolve()
    labs_root = (academy.root / "labs").resolve()
    if not path.is_relative_to(labs_root) or path.suffix != ".py" or not path.is_file():
        raise AcademyError(f"'{target}' is not a lab script inside {labs_root}")
    return path, other_labs


def cmd_lab(academy: Academy, args) -> dict:
    if args.list:
        return [{"lesson": row["slug"], "labs": row["labs"]} for row in academy.lessons.values() if row["labs"]]
    if not args.target:
        raise AcademyError("Name a lesson slug or a lab path, or use --list")
    path, other_labs = resolve_lab(academy, args.target)
    command = [sys.executable, str(path), *args.lab_args]
    try:
        completed = subprocess.run(command, cwd=str(academy.root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        raise AcademyError(f"Lab timed out after {args.timeout} s: {' '.join(command)}")
    output = None
    if completed.returncode == 0:
        try:
            output = json.loads(completed.stdout)
        except json.JSONDecodeError:
            output = None
    return {
        "command": command,
        "exit_code": completed.returncode,
        "result": output,
        "stdout": completed.stdout if output is None else None,
        "stderr": completed.stderr.strip() or None,
        "other_labs": other_labs,
        "interpretation": "exit code 0: calculation completed; 2: the lab rejected an input or assumption (read stderr and discuss it with the learner); other: unexpected error. other_labs lists further scripts of the same lesson; run one by its labs/ path.",
    }


def cmd_references(academy: Academy, args) -> list[dict]:
    wanted = None
    if args.lesson:
        wanted = set(academy.lesson(args.lesson)["academic_references"])
    elif args.module:
        if args.module not in academy.modules:
            raise AcademyError(f"Unknown module id '{args.module}'")
        wanted = {r["id"] for r in academy.modules[args.module]["academic_references"]}
    rows = []
    for course in academy.references.values():
        if wanted is not None and course["id"] not in wanted:
            continue
        if args.domain and args.domain not in [course["primary_domain"], *course["secondary_domains"]]:
            continue
        rows.append({k: course[k] for k in ("id", "course_number", "title", "term", "url", "primary_domain", "academic_level", "priority", "resource_status", "verified_on", "lessons")})
    return rows


def cmd_reference(academy: Academy, args) -> dict:
    if args.id not in academy.references:
        raise AcademyError(f"Unknown reference id '{args.id}'; list them with `references`")
    course = dict(academy.references[args.id])
    course["note"] = academy.references_doc["relationship"]
    course["license_note"] = academy.references_doc["license_note"]
    return course


def cmd_search(academy: Academy, args) -> dict:
    needle = args.text.lower()
    lessons = [lesson_summary(academy, row) for row in academy.lessons.values() if needle in row["title"].lower() or needle in row["slug"] or any(needle in o.lower() for o in row["learning_objectives"])]
    modules = [{"id": m["id"], "title": m["title"], "status": m["status"]} for m in academy.modules.values() if needle in m["id"] or any(needle in str(v).lower() for v in m["title"].values()) or any(needle in str(v).lower() for v in m["summary"].values())]
    references = [{"id": c["id"], "course_number": c["course_number"], "title": c["title"]} for c in academy.references.values() if needle in c["title"].lower() or needle in c["course_number"].lower() or any(needle in t for t in c["topics"])]
    return {"query": args.text, "lessons": lessons, "modules": modules, "references": references}


def cmd_check_tools(academy: Academy, args) -> dict:
    def importable(name: str) -> bool:
        try:
            __import__(name)
            return True
        except Exception:
            return False
    return {
        "python": sys.version.split()[0],
        "python_ok": sys.version_info >= (3, 10),
        "matplotlib": importable("matplotlib"),
        "numpy": importable("numpy"),
        "ngspice": shutil.which("ngspice") is not None,
        "git": shutil.which("git") is not None,
        "fallbacks": {
            "matplotlib": "labs print JSON without plots; --plot is optional",
            "numpy": "not required; all labs use the standard library",
            "ngspice": "switching-simulation extensions are optional; the Python labs cover the core calculations",
        },
    }


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

def record_path(academy: Academy, args) -> Path:
    explicit = getattr(args, "record", None) or os.environ.get("AIPE_ACADEMY_RECORD")
    return Path(explicit).resolve() if explicit else academy.root / "learning/progress.json"


def human(result, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(result, dict):
        lines = []
        for key, value in result.items():
            if isinstance(value, (dict, list)) and value:
                lines.append(f"{pad}{key}:")
                lines.append(human(value, indent + 1))
            else:
                lines.append(f"{pad}{key}: {value if value not in ({}, []) else '-'}")
        return "\n".join(lines)
    if isinstance(result, list):
        lines = []
        for item in result:
            if isinstance(item, dict):
                head = item.get("slug") or item.get("id") or item.get("module") or item.get("lesson") or ""
                title = item.get("title")
                title = title.get("en") if isinstance(title, dict) else title
                status = item.get("status")
                lines.append(f"{pad}- {head}{': ' + str(title) if title else ''}{' [' + status + ']' if status else ''}")
                rest = {k: v for k, v in item.items() if k not in ("slug", "id", "title", "status")}
                if rest and indent < 2:
                    lines.append(human(rest, indent + 2))
            else:
                lines.append(f"{pad}- {item}")
        return "\n".join(lines)
    return f"{pad}{result}"


def add_global_options(parser: argparse.ArgumentParser, suppress: bool) -> None:
    """Global options; also attached to every subcommand so `status --json` and `--json status` both work."""
    default = {"default": argparse.SUPPRESS} if suppress else {}
    parser.add_argument("--repo", help="AIPE Academy checkout (default: discovered)", **default)
    parser.add_argument("--json", action="store_true", help="machine-readable output", **default)
    parser.add_argument("--language", help="label language for titles: en or zh", **({"default": argparse.SUPPRESS} if suppress else {"default": "en"}))
    parser.add_argument("--record", help="learning record path (default: <repo>/learning/progress.json)", **default)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="academy", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_global_options(parser, suppress=False)
    common = argparse.ArgumentParser(add_help=False)
    add_global_options(common, suppress=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", parents=[common])
    sub.add_parser("domains", parents=[common])
    p = sub.add_parser("tracks", parents=[common]); p.add_argument("--domain")
    p = sub.add_parser("modules", parents=[common]); p.add_argument("--domain"); p.add_argument("--track"); p.add_argument("--status")
    p = sub.add_parser("module", parents=[common]); p.add_argument("id")
    p = sub.add_parser("lessons", parents=[common]); p.add_argument("--domain"); p.add_argument("--module"); p.add_argument("--lang", choices=list(LANGUAGE_NAMES)); p.add_argument("--status"); p.add_argument("--type")
    p = sub.add_parser("lesson", parents=[common]); p.add_argument("slug"); p.add_argument("--content", action="store_true", help="include the lesson Markdown")
    sub.add_parser("paths", parents=[common])
    p = sub.add_parser("path", parents=[common]); p.add_argument("id")
    p = sub.add_parser("onboarding", parents=[common]); p.add_argument("--goal"); p.add_argument("--lang", choices=list(LANGUAGE_NAMES))
    p = sub.add_parser("prerequisites", parents=[common]); p.add_argument("slug")
    sub.add_parser("resume", parents=[common])
    p = sub.add_parser("record", parents=[common]); rs = p.add_subparsers(dest="record_command", required=True)
    r = rs.add_parser("init", parents=[common]); r.add_argument("--goal"); r.add_argument("--lang", choices=list(LANGUAGE_NAMES)); r.add_argument("--time"); r.add_argument("--force", action="store_true")
    rs.add_parser("show", parents=[common])
    r = rs.add_parser("set", parents=[common]); r.add_argument("--module"); r.add_argument("--lesson"); r.add_argument("--next-task", dest="next_task")
    r = rs.add_parser("log", parents=[common]); r.add_argument("--lesson"); r.add_argument("--module"); r.add_argument("--task", required=True); r.add_argument("--mode", choices=["independent", "assisted"], required=True); r.add_argument("--evidence", required=True); r.add_argument("--status", choices=STATUSES[1:], required=True); r.add_argument("--help-given", dest="help_given")
    p = sub.add_parser("lab", parents=[common]); p.add_argument("target", nargs="?"); p.add_argument("--list", action="store_true"); p.add_argument("--timeout", type=float, default=120.0); p.add_argument("lab_args", nargs=argparse.REMAINDER, help="arguments passed to the lab script after --")
    p = sub.add_parser("references", parents=[common]); p.add_argument("--domain"); p.add_argument("--module"); p.add_argument("--lesson")
    p = sub.add_parser("reference", parents=[common]); p.add_argument("id")
    p = sub.add_parser("search", parents=[common]); p.add_argument("text")
    sub.add_parser("check-tools", parents=[common])
    return parser


COMMANDS = {
    "status": cmd_status, "domains": cmd_domains, "tracks": cmd_tracks, "modules": cmd_modules, "module": cmd_module,
    "lessons": cmd_lessons, "lesson": cmd_lesson, "paths": cmd_paths, "path": cmd_path, "onboarding": cmd_onboarding,
    "prerequisites": cmd_prerequisites, "resume": cmd_resume, "record": cmd_record, "lab": cmd_lab,
    "references": cmd_references, "reference": cmd_reference, "search": cmd_search, "check-tools": cmd_check_tools,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "lab_args") and args.lab_args[:1] == ["--"]:
        args.lab_args = args.lab_args[1:]
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        academy = Academy(find_repo(args.repo))
        result = COMMANDS[args.command](academy, args)
    except AcademyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(human(result))
    if args.command == "lab" and isinstance(result, dict) and result.get("exit_code", 0) != 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
