"""Verify MIT OpenCourseWare candidate courses against the live site.

This is the network-dependent half of the academic reference pipeline. It is
run deliberately, never by the offline test suite:

  python scripts/verify_academic_sources.py              # write the report
  python scripts/verify_academic_sources.py --update     # also refresh verified
                                                         # fields in the catalogue

For every record in references/mit-ocw-catalogue.json it fetches the official
course page and the course's machine-readable ``data.json`` that MIT OCW
publishes next to it, records the HTTP outcome, the canonical URL after
redirects, the title, course number, term, level, instructors and public
learning-resource types that MIT itself states, and the sub-pages (syllabus,
lecture notes, videos, problem sets ...) that the course page links to.

Facts observed on the live site are written to
references/mit-ocw-verification.json together with the check date. With
``--update`` the same facts replace the ``verified`` block of each catalogue
record; the curated fields (priority, topics, mapped modules, notes) are never
touched by this script. An unreachable or changed course is reported, not
silently treated as valid.

Only metadata is stored. No lecture notes, videos, assignments or other MIT
course content is downloaded or copied; those remain on MIT OpenCourseWare
under its own licence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "references/mit-ocw-catalogue.json"
REPORT = ROOT / "references/mit-ocw-verification.json"
USER_AGENT = "AIPE-Academy-source-verifier/0.2 (+https://github.com/FulongLi/AIPE-Academy)"
TIMEOUT = 40

# Sub-page kinds recognised on an OCW course home page. The label is what the
# report records; the pattern matches the path segment after the course slug.
SUBPAGE_KINDS = (
    ("syllabus", r"pages/syllabus/?$"),
    ("calendar", r"pages/calendar/?$"),
    ("readings", r"pages/readings/?$"),
    ("lecture_notes", r"(pages|lists)/[^/]*lecture-notes[^/]*/?$"),
    ("lecture_videos", r"video_galleries/[^/]+/?$"),
    ("recitations", r"(pages|lists)/[^/]*recitation[^/]*/?$"),
    ("problem_sets", r"(pages|lists)/[^/]*(problem-sets?|assignments?|homework)[^/]*/?$"),
    ("exams", r"(pages|lists)/[^/]*(exams?|quizzes|assessments)[^/]*/?$"),
    ("projects", r"(pages|lists)/[^/]*(project|design)[^/]*/?$"),
    ("labs", r"(pages|lists)/[^/]*lab[^/]*/?$"),
    ("tools", r"(pages|lists)/[^/]*(tools|software|simulations?)[^/]*/?$"),
    ("study_materials", r"(pages|lists)/[^/]*(study-materials|related-resources|resources)[^/]*/?$"),
    ("instructor_insights", r"pages/instructor-insights/?$"),
    ("download", r"download/?$"),
)


def fetch(url: str) -> tuple[int | None, str | None, bytes, str | None]:
    """Return (status, final_url, body, error) following redirects."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.geturl(), response.read(), None
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl(), b"", f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, None, b"", f"{type(exc).__name__}: {exc}"


def course_slug(url: str) -> str:
    path = urllib.parse.urlsplit(url).path.strip("/")
    parts = path.split("/")
    return parts[1] if len(parts) >= 2 and parts[0] == "courses" else path


def subpages(page: str, slug: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for href in re.findall(r'href="(/courses/' + re.escape(slug) + r'/[^"#?]*)"', page):
        rest = href.split(f"/courses/{slug}/", 1)[1]
        for kind, pattern in SUBPAGE_KINDS:
            if re.fullmatch(pattern, rest):
                url = "https://ocw.mit.edu" + href
                if url not in found.setdefault(kind, []):
                    found[kind].append(url)
                break
    return {kind: sorted(urls) for kind, urls in sorted(found.items())}


def text_of(page: str) -> str:
    page = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page)))


def verify_record(record: dict, today: str) -> dict:
    url = record["url"]
    status, final_url, body, error = fetch(url)
    result: dict = {
        "id": record["id"],
        "requested_url": url,
        "checked_on": today,
        "homepage_status": status,
        "final_url": final_url,
        "redirected": bool(final_url) and final_url.rstrip("/") != url.rstrip("/"),
        "error": error,
    }
    if status != 200 or not body:
        result["resource_status"] = "unavailable"
        return result
    page = body.decode("utf-8", errors="replace")
    slug = course_slug(final_url or url)
    title = re.search(r"<title>(.*?)</title>", page, re.S)
    result["html_title"] = html.unescape(title.group(1).strip()) if title else None
    result["subpages"] = subpages(page, slug)

    data_status, _, data_body, data_error = fetch(f"https://ocw.mit.edu/courses/{slug}/data.json")
    result["data_json_status"] = data_status
    if data_status == 200 and data_body:
        try:
            data = json.loads(data_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            result["error"] = f"data.json: {exc}"
            data = {}
        result["observed"] = {
            "course_title": data.get("course_title"),
            "primary_course_number": data.get("primary_course_number"),
            "extra_course_numbers": data.get("extra_course_numbers"),
            "term": data.get("term"),
            "year": data.get("year"),
            "level": data.get("level"),
            "instructors": [i.get("title") for i in data.get("instructors", []) if isinstance(i, dict)],
            "department_numbers": data.get("department_numbers"),
            "topics": data.get("topics"),
            "learning_resource_types": data.get("learning_resource_types"),
            "description": (data.get("course_description") or "")[:600],
        }
    else:
        result["observed"] = None
        result["error"] = result["error"] or f"data.json: {data_error}"

    # A syllabus is the public teaching-scope document; confirm it is reachable.
    syllabus = (result["subpages"].get("syllabus") or [None])[0]
    if syllabus:
        syllabus_status, _, _, _ = fetch(syllabus)
        result["syllabus_status"] = syllabus_status
    else:
        result["syllabus_status"] = None

    expectations = []
    observed = result.get("observed") or {}
    if observed:
        number = observed.get("primary_course_number")
        extra = observed.get("extra_course_numbers") or ""
        numbers = {number} | {n.strip() for n in str(extra).split(",") if n.strip()}
        if record["course_number"] not in numbers:
            expectations.append(f"course number {record['course_number']} not in {sorted(n for n in numbers if n)}")
        if observed.get("course_title") and record["title"].lower() != observed["course_title"].lower():
            expectations.append(f"title differs: catalogue '{record['title']}' vs MIT '{observed['course_title']}'")
        term = f"{observed.get('term') or ''} {observed.get('year') or ''}".strip()
        if term and record["term"].lower() != term.lower():
            expectations.append(f"term differs: catalogue '{record['term']}' vs MIT '{term}'")
    result["expectation_mismatches"] = expectations
    if observed and not expectations:
        result["resource_status"] = "verified"
    elif observed:
        result["resource_status"] = "verified-with-differences"
    else:
        result["resource_status"] = "page-only"
    return result


def apply_update(record: dict, result: dict) -> None:
    observed = result.get("observed") or {}
    term = f"{observed.get('term') or ''} {observed.get('year') or ''}".strip() or None
    record["verified"] = {
        "verified_on": result["checked_on"],
        "homepage_status": result.get("homepage_status"),
        "canonical_url": result.get("final_url") or record["url"],
        "official_title": observed.get("course_title"),
        "course_numbers": sorted({n for n in [observed.get("primary_course_number")] + [s.strip() for s in str(observed.get("extra_course_numbers") or "").split(",")] if n}),
        "term": term,
        "level": observed.get("level"),
        "instructors": observed.get("instructors"),
        "learning_resource_types": observed.get("learning_resource_types"),
        "mit_topics": observed.get("topics"),
        "subpages": result.get("subpages", {}),
        "syllabus_status": result.get("syllabus_status"),
        "expectation_mismatches": result.get("expectation_mismatches", []),
    }
    record["resource_status"] = result["resource_status"]
    record["verified_on"] = result["checked_on"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--update", action="store_true", help="refresh the verified block of each catalogue record")
    parser.add_argument("--only", help="comma-separated record ids to check")
    parser.add_argument("--date", help="override the check date (YYYY-MM-DD); defaults to today in UTC")
    args = parser.parse_args()
    today = args.date or dt.datetime.now(dt.timezone.utc).date().isoformat()
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    wanted = set(args.only.split(",")) if args.only else None
    results = []
    failures = 0
    for record in catalogue["courses"]:
        if wanted and record["id"] not in wanted:
            continue
        result = verify_record(record, today)
        results.append(result)
        flag = result["resource_status"]
        if flag in {"unavailable", "page-only"} or result["expectation_mismatches"]:
            failures += 1
        print(f"{record['id']:<24} {flag:<26} {result.get('homepage_status')} {result.get('final_url') or result.get('error')}", file=sys.stderr)
        for note in result["expectation_mismatches"]:
            print(f"    ! {note}", file=sys.stderr)
        if args.update and result["resource_status"] != "unavailable":
            apply_update(record, result)
        elif args.update:
            record["resource_status"] = "unavailable"
            record["verified_on"] = today
    report = {
        "schema_version": "0.2.0",
        "checked_on": today,
        "method": "HTTP GET of the official course page and its data.json; metadata only, no course content stored",
        "results": results,
    }
    if not wanted:
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"Wrote {REPORT.relative_to(ROOT)}", file=sys.stderr)
    if args.update:
        CATALOGUE.write_text(json.dumps(catalogue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"Updated verified fields in {CATALOGUE.relative_to(ROOT)}", file=sys.stderr)
    print(f"{len(results)} courses checked, {failures} need attention", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
