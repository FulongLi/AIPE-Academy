"""Validate canonical lesson metadata and build a deterministic public catalogue."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def build(root: Path = ROOT) -> dict:
    schema = json.loads((root / "schemas/lesson.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    rows = json.loads((root / "curriculum/catalogue.json").read_text(encoding="utf-8"))
    seen = {}
    for row in rows:
        validator.validate(row)
        slug = row["slug"]
        if slug in seen:
            raise ValueError(f"Duplicate lesson slug: {slug}")
        source = (root / row["source"]).resolve()
        if not source.is_relative_to(root.resolve()) or not source.is_file():
            raise ValueError(f"Missing or unsafe source: {row['source']}")
        if source.suffix != ".md":
            raise ValueError("Lesson sources must be Markdown")
        for ref in row["references"]:
            if ref.startswith("https://"):
                continue
            reference = (root / ref).resolve()
            if not reference.is_relative_to(root.resolve()) or not reference.is_file():
                raise ValueError(f"Missing or unsafe reference: {ref}")
        if any(not t["optional"] and t["licence_class"] != "open_source" for t in row["tools"]):
            raise ValueError(f"Core learning path requires proprietary software: {slug}")
        row = dict(row)
        row["url"] = f"/academy/{row['domain']}/{slug}/"
        # Git checkouts can use CRLF. Hash canonical UTF-8/LF source content.
        row["sha256"] = hashlib.sha256(source.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        seen[slug] = row
    for slug, row in seen.items():
        for key in ("prerequisites", "next"):
            for ref in row[key]:
                if ref not in seen or ref == slug:
                    raise ValueError(f"Invalid {key} reference: {slug} -> {ref}")
    visiting, visited = set(), set()

    def walk(slug):
        if slug in visiting:
            raise ValueError(f"Prerequisite cycle at {slug}")
        if slug in visited:
            return
        visiting.add(slug)
        for ref in seen[slug]["prerequisites"]:
            walk(ref)
        visiting.remove(slug)
        visited.add(slug)

    for slug in seen:
        walk(slug)
    return {"schema_version": "0.1.0", "lessons": sorted(seen.values(), key=lambda r: r["slug"])}


def render(payload):
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated catalogue is stale")
    args = parser.parse_args()
    result = render(build())
    target = ROOT / "generated/lessons.json"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != result:
            parser.error("Stale catalogue; run python scripts/build_catalogue.py")
    else:
        target.parent.mkdir(exist_ok=True)
        target.write_text(result, encoding="utf-8", newline="\n")
    print(f"Validated {len(build()['lessons'])} lesson records")


if __name__ == "__main__":
    main()
