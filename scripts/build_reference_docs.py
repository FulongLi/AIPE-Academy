"""Render the human-readable academic reference documents from the JSON sources.

    python scripts/build_reference_docs.py          # write the two Markdown files
    python scripts/build_reference_docs.py --check  # fail if they are stale

Inputs:
  references/mit-ocw-catalogue.json   verified facts + AIPE mapping per course
  references/mit-ocw-coverage.json    topic outlines, gaps and recommendations per course
  generated/knowledge-graph.json      modules with attached lessons and their status
  generated/lessons.json              lesson titles and statuses

Outputs:
  references/mit-ocw-baseline.md      academic reference index by domain
  references/academic-coverage-map.md MIT course -> MIT topic -> AIPE module -> AIPE lesson / lab,
                                      with academic coverage separated from content completion

Rendering from the JSON keeps the Markdown and the machine-readable records
identical; edit the JSON (or the preamble text below), never the Markdown.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "references/mit-ocw-baseline.md"
COVERAGE = "references/academic-coverage-map.md"
DOMAIN_ORDER = ["foundations", "power-electronics", "power-systems", "renewable-energy"]
MODERN_GAPS_REQUIRED = [
    "Inverter-dominated grids",
    "Grid-forming converters",
    "Converter interaction and stability",
    "DC distribution and DC grids",
    "High-renewable-penetration power systems",
]


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def cell(text, limit: int = 0) -> str:
    text = str(text).replace("|", "\\|").replace("\n", " ").strip()
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def join(items, sep: str = "; ", limit: int = 0, cap: int = 0) -> str:
    items = list(items)
    if not items:
        return "—"
    shown = items[:cap] if cap else items
    text = sep.join(cell(i, limit) for i in shown)
    if cap and len(items) > cap:
        text += f"{sep}(+{len(items) - cap} more in the JSON source)"
    return text


def course_heading(course: dict) -> str:
    verified = course.get("verified") or {}
    title = verified.get("official_title") or course["title"]
    term = verified.get("term") or course["term"]
    return f"MIT {course['course_number']} — {title} ({term})"


def render_baseline(catalogue: dict, coverage: dict, graph: dict, lessons: dict) -> str:
    domains = {d["id"]: d for d in graph["domains"]}
    modules = {m["id"]: m for m in graph["modules"]}
    by_course_coverage = {c["id"]: c for c in coverage["courses"]}
    checked = sorted({c["verified_on"] for c in catalogue["courses"] if c.get("verified_on")})
    statuses = defaultdict(int)
    for course in catalogue["courses"]:
        statuses[course["resource_status"]] += 1
    out = [
        "# MIT OpenCourseWare academic baseline",
        "",
        "Generated from `references/mit-ocw-catalogue.json` and `references/mit-ocw-coverage.json` by",
        "`scripts/build_reference_docs.py`; edit the JSON, not this file.",
        "",
        catalogue["purpose"],
        "",
        f"**Relationship.** {catalogue['relationship']}",
        "",
        f"**Licence.** {catalogue['license_note']}",
        "",
        "## Verification summary",
        "",
        f"- Candidate courses reviewed: {len(catalogue['courses'])} (the 22 initial candidates of v0.2).",
        f"- Verification date(s): {', '.join(checked) if checked else 'none'}; method: {coverage.get('method', 'official course page and data.json read by scripts/verify_academic_sources.py')}.",
        "- Status counts: " + ", ".join(f"`{status}` {count}" for status, count in sorted(statuses.items())) + ".",
        "- Facts under *Verified* were read from the official MIT OCW page and its `data.json`; *Topic coverage* titles were read from the public syllabus, calendar and resource listing pages (URLs in the coverage file); *AIPE mapping* is AIPE Academy's own judgement.",
        "- Re-run: `python scripts/verify_academic_sources.py --update` (network), then `python scripts/build_reference_docs.py`.",
        "",
        "| Status | Meaning |",
        "| --- | --- |",
    ]
    for status, meaning in catalogue["status_vocabulary"].items():
        out.append(f"| `{status}` | {cell(meaning)} |")
    out.append("")
    for domain_id in DOMAIN_ORDER:
        domain = domains[domain_id]
        courses = [c for c in catalogue["courses"] if c["primary_domain"] == domain_id]
        out += [f"## {domain['title']['en']}", "", domain["summary"]["en"], ""]
        secondary = [c for c in catalogue["courses"] if domain_id in c.get("secondary_domains", [])]
        if secondary:
            out.append("Also relevant (primary domain elsewhere): " + ", ".join(f"MIT {c['course_number']}" for c in secondary) + ".")
            out.append("")
        for course in sorted(courses, key=lambda c: (["core", "foundation", "supplementary", "historical"].index(c["priority"]), c["course_number"])):
            verified = course.get("verified") or {}
            cov = by_course_coverage.get(course["id"], {})
            out += [f"### {course_heading(course)}", ""]
            rows = [
                ("Official URL", f"<{course['url']}>"),
                ("Course number(s)", join(verified.get("course_numbers") or [course["course_number"]], ", ")),
                ("Teaching term", verified.get("term") or course["term"]),
                ("Level (MIT)", join(verified.get("level") or [], ", ")),
                ("Instructor(s) as listed", join(verified.get("instructors") or [], ", ")),
                ("AIPE priority", course["priority"]),
                ("AIPE reference area", course.get("reference_area", "—")),
                ("Available public resources", join(verified.get("learning_resource_types") or [], ", ")),
                ("Main knowledge areas (AIPE tags)", join(course["topics"], ", ")),
                ("Relevant AIPE modules", join([f"`{m['module']}` ({m['coverage']})" for m in course["mapped_modules"]], ", ")),
                ("Lessons citing this course", join([f"`{slug}`" for slug in sorted(lessons_citing(lessons, course["id"]))], ", ")),
                ("Access limitations", join(course.get("access_limitations") or ["none recorded"], "; ", limit=220, cap=3)),
                ("Verification", f"{course['resource_status']} on {course['verified_on']} (HTTP {verified.get('homepage_status')}; syllabus HTTP {verified.get('syllabus_status')})"),
            ]
            out += ["| Field | Value |", "| --- | --- |"]
            out += [f"| {k} | {cell(v)} |" for k, v in rows]
            out.append("")
            key_resources = course.get("key_resources") or []
            if key_resources:
                out.append("Official resource pages (summaries in `references/mit-ocw-coverage.json`):")
                out.append("")
                out += [f"- [{cell(r['label'])}]({r['url']})" for r in key_resources]
                out.append("")
            if course.get("coverage_notes"):
                out += ["Scope (AIPE summary in its own words):", "", cell(course["coverage_notes"], 900), ""]
    return "\n".join(out).rstrip("\n") + "\n"


def lessons_citing(lessons: dict, course_id: str) -> list[str]:
    return [slug for slug, row in lessons.items() if course_id in row.get("academic_references", [])]


def render_coverage(catalogue: dict, coverage: dict, graph: dict, lessons: dict) -> str:
    domains = {d["id"]: d for d in graph["domains"]}
    tracks = {t["id"]: t for t in graph["tracks"]}
    modules = {m["id"]: m for m in graph["modules"]}
    courses = {c["id"]: c for c in catalogue["courses"]}
    cov_by_id = {c["id"]: c for c in coverage["courses"]}
    covering: dict[str, list[tuple[str, str, list[str]]]] = defaultdict(list)
    for course in catalogue["courses"]:
        for mapped in course["mapped_modules"]:
            covering[mapped["module"]].append((course["id"], mapped["coverage"], mapped.get("mit_topics", [])))
    out = [
        "# Academic coverage map",
        "",
        "Generated by `scripts/build_reference_docs.py` from the reference catalogue, the topic coverage records and the",
        "generated knowledge graph; edit the JSON sources, not this file.",
        "",
        "This map connects **MIT course → MIT topic → AIPE knowledge module → AIPE lesson / lab**. It separates two",
        "different facts: *academic coverage* (a verified MIT course teaches the topic) and *content completion* (an",
        "AIPE lesson with that status exists). A topic covered by MIT and marked `planned` here has no AIPE lesson yet.",
        "",
        "Coverage labels: `core` the course's central subject matter; `partial` substantial but not central; `introductory`",
        "brief treatment; `background` assumed or tangential. Lesson statuses: `available`, `draft`, `outline`, or `planned`",
        "(no lesson). MIT OpenCourseWare is an external resource; AIPE Academy is not affiliated with or endorsed by MIT.",
        "",
        "## 1. Module coverage by domain",
        "",
    ]
    for domain_id in DOMAIN_ORDER:
        domain = domains[domain_id]
        out += [f"### {domain['title']['en']}", ""]
        out += ["| Track | Module | AIPE status | AIPE lessons | MIT courses covering it | Prerequisite modules |", "| --- | --- | --- | --- | --- | --- |"]
        for track_id in domain["tracks"]:
            for module_id in tracks[track_id]["modules"]:
                module = modules[module_id]
                lesson_cells = [f"`{slug}` ({lessons[slug]['status']})" for slug in module["lessons"]]
                courses_cells = [f"MIT {courses[cid]['course_number']} ({cov})" for cid, cov, _ in sorted(covering.get(module_id, []), key=lambda x: (["core", "partial", "introductory", "background"].index(x[1]), x[0]))]
                out.append(f"| {tracks[track_id]['title']['en']} | `{module_id}` {cell(module['title']['en'])} | {module['status']} | {join(lesson_cells, '; ')} | {join(courses_cells, '; ')} | {join([f'`{r}`' for r in module['requires']], ', ')} |")
        out.append("")
    out += ["## 2. MIT course → MIT topic → AIPE module", ""]
    out.append("Topic titles are short public listing titles (at most twelve words), grouped by the official page they were read from; nothing else from the courses is reproduced. Mapping rationales, background-level mappings and per-page resource summaries are in `references/mit-ocw-coverage.json`.")
    out.append("")
    for domain_id in DOMAIN_ORDER:
        for course in [c for c in catalogue["courses"] if c["primary_domain"] == domain_id]:
            cov = cov_by_id.get(course["id"])
            out += [f"### {course_heading(course)}", ""]
            if not cov:
                out += ["No topic coverage record.", ""]
                continue
            out += [cell(cov["course_facts"]["scope_summary"], 900), ""]
            if cov["course_facts"].get("stated_prerequisites"):
                out += ["Stated prerequisites (paraphrased): " + join(cov["course_facts"]["stated_prerequisites"], "; ", limit=160, cap=6), ""]
            out += ["| AIPE module | Coverage | MIT topics (listing titles) | Evidence |", "| --- | --- | --- | --- |"]
            for mapped in course["mapped_modules"]:
                out.append(f"| `{mapped['module']}` {cell(modules[mapped['module']]['title']['en'])} | {mapped['coverage']} | {join(mapped.get('mit_topics', []), '; ', limit=90, cap=5)} | {('<' + mapped['evidence_url'] + '>') if mapped.get('evidence_url') else '—'} |")
            out.append("")
            outline = cov["course_facts"].get("topic_outline") or []
            if outline:
                out.append("<details><summary>Topic outline as listed by MIT (" + str(len(outline)) + " items)</summary>")
                out.append("")
                current_source = None
                for item in outline:
                    if item["source_url"] != current_source:
                        current_source = item["source_url"]
                        out.append(f"From <{current_source}>:")
                        out.append("")
                    prefix = f"{item['index']}. " if item.get("index") else ""
                    out.append(f"- {prefix}{cell(item['title'], 120)}")
                out += ["", "</details>", ""]
    out += ["## 3. Gaps", ""]
    out += ["### 3.1 Concepts the MIT baseline covers that AIPE has no lesson for yet", ""]
    missing = defaultdict(list)
    for cov in coverage["courses"]:
        for concept in cov["aipe_mapping"].get("concepts_missing_in_aipe", []):
            missing[cell(concept, 200)].append(courses[cov["id"]]["course_number"])
    for concept, numbers in sorted(missing.items()):
        out.append(f"- {concept} (MIT {', '.join(sorted(set(numbers)))})")
    out.append("")
    out += ["### 3.2 Modern topics AIPE needs that the MIT baseline does not cover", ""]
    out.append("Required by v0.2 and confirmed absent from the listed course pages (do not attribute them to the older courses):")
    out.append("")
    for gap in MODERN_GAPS_REQUIRED:
        out.append(f"- {gap}")
    out.append("")
    out.append("Additional gaps recorded per course:")
    out.append("")
    extra = defaultdict(list)
    for cov in coverage["courses"]:
        for gap in cov["aipe_mapping"].get("modern_gaps_not_covered_by_mit", []):
            extra[cell(gap, 200)].append(courses[cov["id"]]["course_number"])
    for gap, numbers in sorted(extra.items()):
        out.append(f"- {gap} (noted for MIT {', '.join(sorted(set(numbers)))})")
    out.append("")
    out += ["### 3.3 Modules without any MIT coverage in the baseline", ""]
    uncovered = [m for m in graph["modules"] if m["id"] not in covering]
    out += [f"- `{m['id']}` {cell(m['title']['en'])} ({m['domain']})" for m in uncovered] or ["- none"]
    out.append("")
    out += ["## 4. Recommended lessons and simulations", ""]
    out.append("Proposals recorded per course during the mapping review (full text in the JSON source); each is an AIPE suggestion, not an MIT recommendation.")
    out.append("")
    for domain_id in DOMAIN_ORDER:
        recs_l, recs_s = [], []
        for cov in coverage["courses"]:
            if courses[cov["id"]]["primary_domain"] != domain_id:
                continue
            recs_l += [f"{cell(r, 220)} (MIT {courses[cov['id']]['course_number']})" for r in cov["aipe_mapping"].get("recommended_lessons", [])]
            recs_s += [f"{cell(r, 220)} (MIT {courses[cov['id']]['course_number']})" for r in cov["aipe_mapping"].get("recommended_simulations", [])]
        out += [f"### {domains[domain_id]['title']['en']}", "", "Lessons:", ""]
        out += [f"- {r}" for r in recs_l] or ["- none recorded"]
        out += ["", "Simulations and labs (open tools):", ""]
        out += [f"- {r}" for r in recs_s] or ["- none recorded"]
        out.append("")
    out += ["## 5. Prerequisite relationships implied by the courses", ""]
    out.append("Relationships the course structures imply, stated against the taxonomy's module ids; where a course suggests a dependency the taxonomy does not yet record, the note says so.")
    out.append("")
    for cov in coverage["courses"]:
        for rel in cov["aipe_mapping"].get("prerequisite_relationships", []):
            out.append(f"- {cell(rel, 220)} (MIT {courses[cov['id']]['course_number']})")
    out.append("")
    out += ["## 6. Content completion versus academic coverage", ""]
    total = len(graph["modules"])
    status_counts = defaultdict(int)
    for module in graph["modules"]:
        status_counts[module["status"]] += 1
    out.append("| AIPE module status | Modules |")
    out.append("| --- | --- |")
    for status in ("available", "draft", "outline", "planned"):
        out.append(f"| {status} | {status_counts.get(status, 0)} |")
    out += ["", f"{len(covering)} of {total} modules have at least one MIT course mapped to them; {status_counts.get('available', 0)} have an available AIPE lesson. Academic coverage does not imply content completion.", ""]
    return "\n".join(out).rstrip("\n") + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalogue = read_json("references/mit-ocw-catalogue.json")
    coverage = read_json("references/mit-ocw-coverage.json")
    graph = read_json("generated/knowledge-graph.json")
    lessons = {row["slug"]: row for row in read_json("generated/lessons.json")["lessons"]}
    outputs = {BASELINE: render_baseline(catalogue, coverage, graph, lessons), COVERAGE: render_coverage(catalogue, coverage, graph, lessons)}
    stale = []
    for relative, text in outputs.items():
        target = ROOT / relative
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                stale.append(relative)
        else:
            target.write_text(text, encoding="utf-8", newline="\n")
    if stale:
        parser.error(f"Stale reference documents: {', '.join(stale)}; run python scripts/build_reference_docs.py")
    print(f"Rendered {len(outputs)} reference documents for {len(catalogue['courses'])} courses")


if __name__ == "__main__":
    main()
