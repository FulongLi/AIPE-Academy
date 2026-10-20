"""Validate canonical curriculum metadata and build deterministic public outputs.

Inputs (hand-maintained, reviewed in pull requests):
  curriculum/taxonomy.json            Domain -> Track -> Module hierarchy and learning paths
  curriculum/catalogue.json           one record per lesson, lab, tutorial, guide or stage outline
  references/mit-ocw-catalogue.json   academic reference baseline (verified facts + AIPE mapping)
  schemas/*.schema.json               JSON Schemas for the three files above

Outputs (deterministic; committed under generated/ and checked in CI):
  generated/lessons.json              lesson catalogue with stable URLs, content hashes and translations
  generated/knowledge-graph.json      taxonomy with lesson attachments, coverage status, module-level
                                      academic references and learning paths
  generated/academic-references.json  public projection of the reference catalogue with the lessons
                                      that cite each course

    python scripts/build_catalogue.py          # rebuild generated/*
    python scripts/build_catalogue.py --check  # fail if generated/* is stale

The build fails on unresolved ids, cycles, unsafe or missing paths, duplicate
slugs or concepts per language, mandatory proprietary tools, missing lab
scripts, lessons that cite a reference without linking its official URL, and
standard-format lessons that do not carry the thirteen required sections.
Text hashes use UTF-8 with LF newlines so Windows and Linux checkouts agree.
Lesson URLs are /academy/<domain>/<slug>/ and never depend on folder layout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LESSONS_OUT = "generated/lessons.json"
GRAPH_OUT = "generated/knowledge-graph.json"
REFERENCES_OUT = "generated/academic-references.json"
SCHEMA_VERSION = "0.2.0"

# The thirteen sections of templates/lesson-template.md, in order. A lesson
# whose catalogue record says format "aipe-lesson-v2" must contain exactly
# these level-two headings in this order.
STANDARD_SECTIONS = (
    "Learning Objectives",
    "Prerequisites",
    "Physical Intuition",
    "Fundamental Principles",
    "Mathematical Derivations",
    "Worked Examples",
    "Numerical or Simulation Lab",
    "Parameter Exploration",
    "Common Misconceptions",
    "AI Tutor Exercises",
    "Knowledge Assessment",
    "Academic References",
    "Further Learning",
)
STATUS_RANK = {"available": 3, "draft": 2, "outline": 1}
MODULE_LESS_TYPES = {"stage", "guide"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validator(root: Path, name: str) -> Draft202012Validator:
    return Draft202012Validator(read_json(root / "schemas" / name))


def confined(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError(f"Path escapes repository: {relative}")
    return path


def check_acyclic(edges: dict[str, list[str]], what: str) -> None:
    state: dict[str, str] = {}

    def visit(node: str, trail: list[str]) -> None:
        if state.get(node) == "done":
            return
        if state.get(node) == "active":
            raise ValueError(f"{what} cycle at {' -> '.join(trail + [node])}")
        state[node] = "active"
        for target in edges.get(node, []):
            visit(target, trail + [node])
        state[node] = "done"

    for node in edges:
        visit(node, [])


def load_taxonomy(root: Path) -> dict:
    taxonomy = read_json(root / "curriculum/taxonomy.json")
    validator(root, "taxonomy.schema.json").validate(taxonomy)
    domains = {d["id"]: d for d in taxonomy["domains"]}
    tracks = {t["id"]: t for t in taxonomy["tracks"]}
    modules = {m["id"]: m for m in taxonomy["modules"]}
    for name, items, table in (("domain", taxonomy["domains"], domains), ("track", taxonomy["tracks"], tracks), ("module", taxonomy["modules"], modules)):
        if len(items) != len(table):
            raise ValueError(f"Duplicate {name} id in taxonomy")
    for track in tracks.values():
        if track["domain"] not in domains:
            raise ValueError(f"Track {track['id']} names unknown domain {track['domain']}")
    for module in modules.values():
        where = f"Module {module['id']}"
        if module["domain"] not in domains:
            raise ValueError(f"{where} names unknown domain {module['domain']}")
        track = tracks.get(module["track"])
        if track is None or track["domain"] != module["domain"]:
            raise ValueError(f"{where} names a track outside its domain: {module['track']}")
        parent = module.get("parent")
        if parent is not None and (parent not in modules or parent == module["id"] or modules[parent]["domain"] != module["domain"]):
            raise ValueError(f"{where} has an invalid parent {parent}")
        for field in ("requires", "related"):
            for ref in module[field]:
                if ref not in modules or ref == module["id"]:
                    raise ValueError(f"{where} {field} unknown or self module {ref}")
    check_acyclic({m: modules[m]["requires"] for m in modules}, "Module prerequisite")
    paths = {p["id"]: p for p in taxonomy["learning_paths"]}
    if len(paths) != len(taxonomy["learning_paths"]):
        raise ValueError("Duplicate learning path id")
    for path in paths.values():
        if path["domain"] not in domains:
            raise ValueError(f"Learning path {path['id']} names unknown domain {path['domain']}")
        stage_ids = [s["id"] for s in path["stages"]]
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError(f"Learning path {path['id']} repeats a stage id")
        for stage in path["stages"]:
            for module in stage["modules"]:
                if module not in modules:
                    raise ValueError(f"Learning path {path['id']} stage {stage['id']} names unknown module {module}")
            gate = stage.get("gate")
            if gate is not None and gate not in path["gates"]:
                raise ValueError(f"Learning path {path['id']} stage {stage['id']} names undefined gate {gate}")
        for gate_id, gate in path["gates"].items():
            for module in gate["demonstrate"]:
                if module not in modules:
                    raise ValueError(f"Learning path {path['id']} gate {gate_id} names unknown module {module}")
    return taxonomy


def load_references(root: Path, taxonomy: dict) -> dict:
    catalogue = read_json(root / "references/mit-ocw-catalogue.json")
    validator(root, "academic-reference.schema.json").validate(catalogue)
    domains = {d["id"] for d in taxonomy["domains"]}
    modules = {m["id"] for m in taxonomy["modules"]}
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for course in catalogue["courses"]:
        where = f"Reference {course['id']}"
        if course["id"] in seen_ids:
            raise ValueError(f"Duplicate reference id {course['id']}")
        seen_ids.add(course["id"])
        url = course["url"].rstrip("/")
        if not url:
            raise ValueError(f"{where} has an empty official URL")
        if url in seen_urls:
            raise ValueError(f"{where} duplicates the canonical URL of another record")
        seen_urls.add(url)
        if course["primary_domain"] not in domains:
            raise ValueError(f"{where} names unknown domain {course['primary_domain']}")
        for domain in course.get("secondary_domains", []):
            if domain not in domains or domain == course["primary_domain"]:
                raise ValueError(f"{where} has an invalid secondary domain {domain}")
        mapped = [m["module"] for m in course["mapped_modules"]]
        if len(mapped) != len(set(mapped)):
            raise ValueError(f"{where} maps the same module twice")
        for module in mapped:
            if module not in modules:
                raise ValueError(f"{where} maps unknown module {module}")
        verified = course.get("verified")
        if course["resource_status"] in {"verified", "verified-with-differences", "page-only"}:
            if verified is None or course["verified_on"] is None or verified["verified_on"] != course["verified_on"]:
                raise ValueError(f"{where} claims verification without a matching verified block")
            if course["resource_status"] == "verified" and verified["expectation_mismatches"]:
                raise ValueError(f"{where} is marked verified but records mismatches")
            if verified["canonical_url"].rstrip("/") != url and course["resource_status"] == "verified":
                raise ValueError(f"{where} canonical URL differs from the recorded URL; record the redirect")
        elif course["resource_status"] == "pending-review" and course["verified_on"] is not None:
            raise ValueError(f"{where} is pending review but carries a verification date")
    return catalogue


def section_headings(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^## (.+?)\s*$", text, flags=re.M)]


def build(root: Path = ROOT) -> dict:
    root = root.resolve()
    taxonomy = load_taxonomy(root)
    references = load_references(root, taxonomy)
    domains = {d["id"]: d for d in taxonomy["domains"]}
    tracks = {t["id"]: t for t in taxonomy["tracks"]}
    modules = {m["id"]: m for m in taxonomy["modules"]}
    courses = {c["id"]: c for c in references["courses"]}
    lesson_validator = validator(root, "lesson.schema.json")
    rows = read_json(root / "curriculum/catalogue.json")
    seen: dict[str, dict] = {}
    concepts: dict[str, dict[str, str]] = {}
    for row in rows:
        lesson_validator.validate(row)
        slug = row["slug"]
        where = f"Lesson {slug}"
        if slug in seen:
            raise ValueError(f"Duplicate lesson slug: {slug}")
        source = confined(root, row["source"])
        if not source.is_file():
            raise ValueError(f"Missing or unsafe source: {row['source']}")
        if source.suffix != ".md":
            raise ValueError("Lesson sources must be Markdown")
        text = read_text(source)
        if text.startswith("---"):
            raise ValueError(f"{where} source must not carry YAML front matter; metadata lives in the catalogue")
        if "{%" in text or "{{" in text:
            raise ValueError(f"{where} source contains template syntax")
        for ref in row["references"]:
            if ref.startswith("https://"):
                continue
            reference = confined(root, ref)
            if not reference.is_file():
                raise ValueError(f"Missing or unsafe reference: {ref}")
        if any(not t["optional"] and t["licence_class"] != "open_source" for t in row["tools"]):
            raise ValueError(f"Core learning path requires proprietary software: {slug}")
        if row["domain"] not in domains:
            raise ValueError(f"{where} names unknown domain {row['domain']}")
        track = tracks.get(row["track"])
        if track is None or track["domain"] != row["domain"]:
            raise ValueError(f"{where} names a track outside its domain: {row['track']}")
        module_id = row["module"]
        if module_id is None:
            if row["type"] not in MODULE_LESS_TYPES:
                raise ValueError(f"{where} of type {row['type']} must name a module")
        else:
            module = modules.get(module_id)
            if module is None or module["domain"] != row["domain"]:
                raise ValueError(f"{where} names a module outside its domain: {module_id}")
            if module["track"] != row["track"]:
                raise ValueError(f"{where} track {row['track']} differs from the module's track {module['track']}")
        for covered in row.get("covers", []):
            if covered not in modules or covered == module_id:
                raise ValueError(f"{where} covers unknown or primary module {covered}")
        for lab in row.get("labs", []):
            lab_path = confined(root, lab)
            if not lab_path.is_file():
                raise ValueError(f"{where} names a missing lab script {lab}")
        for ref_id in row.get("academic_references", []):
            course = courses.get(ref_id)
            if course is None:
                raise ValueError(f"{where} cites unknown academic reference {ref_id}")
            if course["url"] not in text:
                raise ValueError(f"{where} cites {ref_id} but does not link its official URL {course['url']}")
        if row.get("format") == "aipe-lesson-v2":
            headings = section_headings(text)
            if tuple(headings) != STANDARD_SECTIONS:
                raise ValueError(f"{where} does not follow the standard lesson sections; found {headings}")
            if not text.startswith("# "):
                raise ValueError(f"{where} must start with a level-one title")
        concept_languages = concepts.setdefault(row["concept"], {})
        if row["language"] in concept_languages:
            raise ValueError(f"Concept {row['concept']} has two {row['language']} records: {concept_languages[row['language']]} and {slug}")
        concept_languages[row["language"]] = slug
        record = dict(row)
        record.setdefault("covers", [])
        record.setdefault("labs", [])
        record.setdefault("academic_references", [])
        record.setdefault("translation_status", "original")
        record.setdefault("format", "legacy")
        record["url"] = f"/academy/{row['domain']}/{slug}/"
        # Git checkouts can use CRLF. Hash canonical UTF-8/LF source content.
        record["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        seen[slug] = record
    for slug, record in seen.items():
        for key in ("prerequisites", "next"):
            for ref in record[key]:
                if ref not in seen or ref == slug:
                    raise ValueError(f"Invalid {key} reference: {slug} -> {ref}")
        record["translations"] = {language: concepts[record["concept"]].get(language) for language in ("en", "zh-CN")}
    check_acyclic({slug: record["prerequisites"] for slug, record in seen.items()}, "Prerequisite")
    for path in taxonomy["learning_paths"]:
        for stage in path["stages"]:
            for lesson in stage["lessons"]:
                if lesson not in seen:
                    raise ValueError(f"Learning path {path['id']} stage {stage['id']} names unknown lesson {lesson}")
    lessons = sorted(seen.values(), key=lambda r: r["slug"])

    # Knowledge graph: attach lessons and references to modules; derive status.
    module_lessons: dict[str, list[str]] = {m: [] for m in modules}
    for record in lessons:
        for module_id in ([record["module"]] if record["module"] else []) + record["covers"]:
            module_lessons[module_id].append(record["slug"])
    module_refs: dict[str, list[dict]] = {m: [] for m in modules}
    for course in references["courses"]:
        for mapped in course["mapped_modules"]:
            module_refs[mapped["module"]].append({"id": course["id"], "coverage": mapped["coverage"]})
    graph_modules = []
    for module in taxonomy["modules"]:
        attached = sorted(module_lessons[module["id"]])
        statuses = [seen[slug]["status"] for slug in attached]
        status = max(statuses, key=lambda s: STATUS_RANK[s]) if statuses else "planned"
        graph_modules.append({
            **module,
            "lessons": attached,
            "status": status,
            "academic_references": sorted(module_refs[module["id"]], key=lambda r: (r["id"], r["coverage"])),
        })
    graph_paths = []
    for path in taxonomy["learning_paths"]:
        stages = []
        for stage in path["stages"]:
            stage_record = dict(stage)
            stage_record["lesson_status"] = {slug: seen[slug]["status"] for slug in stage["lessons"]}
            stages.append(stage_record)
        graph_paths.append({**path, "stages": stages})
    graph = {
        "schema_version": SCHEMA_VERSION,
        "domains": [{**d, "tracks": [t["id"] for t in taxonomy["tracks"] if t["domain"] == d["id"]]} for d in taxonomy["domains"]],
        "tracks": [{**t, "modules": [m["id"] for m in taxonomy["modules"] if m["track"] == t["id"]]} for t in taxonomy["tracks"]],
        "modules": graph_modules,
        "learning_paths": graph_paths,
        "lesson_count": len(lessons),
    }

    # Public projection of the academic reference catalogue.
    cited_by: dict[str, list[str]] = {c: [] for c in courses}
    for record in lessons:
        for ref_id in record["academic_references"]:
            cited_by[ref_id].append(record["slug"])
    projected = []
    for course in references["courses"]:
        verified = course.get("verified") or {}
        projected.append({
            "id": course["id"],
            "institution": course["institution"],
            "platform": course["platform"],
            "course_number": course["course_number"],
            "title": course["title"],
            "term": course["term"],
            "url": course["url"],
            "primary_domain": course["primary_domain"],
            "secondary_domains": course.get("secondary_domains", []),
            "reference_area": course.get("reference_area", ""),
            "academic_level": course["academic_level"],
            "priority": course["priority"],
            "resource_status": course["resource_status"],
            "verified_on": course["verified_on"],
            "instructors": verified.get("instructors") or [],
            "level": verified.get("level") or [],
            "learning_resource_types": verified.get("learning_resource_types") or [],
            "key_resources": course.get("key_resources", []),
            "topics": course["topics"],
            "mapped_modules": course["mapped_modules"],
            "coverage_notes": course.get("coverage_notes", ""),
            "gaps": course.get("gaps", []),
            "access_limitations": course.get("access_limitations", []),
            "lessons": sorted(cited_by[course["id"]]),
        })
    references_out = {
        "schema_version": SCHEMA_VERSION,
        "relationship": references["relationship"],
        "license_note": references["license_note"],
        "courses": sorted(projected, key=lambda c: c["id"]),
    }
    return {
        LESSONS_OUT: {"schema_version": SCHEMA_VERSION, "lessons": lessons},
        GRAPH_OUT: graph,
        REFERENCES_OUT: references_out,
    }


def render(payload) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Fail if any generated file is stale")
    args = parser.parse_args()
    outputs = build()
    stale = []
    for relative, payload in outputs.items():
        target = ROOT / relative
        text = render(payload)
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                stale.append(relative)
        else:
            target.parent.mkdir(exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")
    if stale:
        parser.error(f"Stale generated files: {', '.join(stale)}; run python scripts/build_catalogue.py")
    lessons = outputs[LESSONS_OUT]["lessons"]
    graph = outputs[GRAPH_OUT]
    print(f"Validated {len(lessons)} lesson records, {len(graph['modules'])} modules in {len(graph['domains'])} domains, {len(outputs[REFERENCES_OUT]['courses'])} academic references")


if __name__ == "__main__":
    main()
