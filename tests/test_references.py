"""Academic reference tests (offline): record structure, unique ids and URLs, mapping targets, lesson citations.

Network verification of the live MIT OpenCourseWare pages is a separate,
deliberately run step: python scripts/verify_academic_sources.py.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("catalogue", ROOT / "scripts/build_catalogue.py")
catalogue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogue)

CANDIDATES = {
    "18.01SC", "18.02SC", "18.03SC", "18.06SC", "8.02", "6.002", "6.003", "6.013",
    "6.622", "6.334", "6.012", "6.302",
    "6.061", "6.691", "6.685",
    "2.627", "EC.S07", "22.081J", "8.21", "10.626", "2.60J", "15.031J",
}


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ("schemas", "curriculum", "references", "labs"):
            shutil.copytree(ROOT / path, self.root / path)
        self.path = self.root / "references/mit-ocw-catalogue.json"

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, fn):
        data = json.loads(self.path.read_text(encoding="utf-8"))
        fn(data)
        self.path.write_text(json.dumps(data), encoding="utf-8")

    def test_all_22_candidates_reviewed(self):
        data = json.loads((ROOT / "references/mit-ocw-catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual({c["course_number"] for c in data["courses"]}, CANDIDATES)
        for course in data["courses"]:
            self.assertNotEqual(course["resource_status"], "pending-review", course["id"])
            self.assertIsNotNone(course["verified_on"], course["id"])
            self.assertTrue(course["url"].startswith("https://ocw.mit.edu/courses/"), course["id"])
            if course["resource_status"] == "verified":
                self.assertEqual(course["verified"]["expectation_mismatches"], [], course["id"])
                self.assertTrue(course["verified"]["official_title"], course["id"])

    def test_every_course_maps_to_at_least_one_module(self):
        data = json.loads((ROOT / "references/mit-ocw-catalogue.json").read_text(encoding="utf-8"))
        for course in data["courses"]:
            self.assertTrue(course["mapped_modules"], f"{course['id']} has no module mapping")
            self.assertTrue(course["topics"], f"{course['id']} has no topic tags")
            for mapped in course["mapped_modules"]:
                self.assertTrue(mapped.get("evidence_url", "").startswith("https://ocw.mit.edu/"), f"{course['id']} {mapped['module']}")

    def test_primary_benchmark_is_6_622(self):
        data = json.loads((ROOT / "references/mit-ocw-catalogue.json").read_text(encoding="utf-8"))
        by_number = {c["course_number"]: c for c in data["courses"]}
        self.assertEqual(by_number["6.622"]["priority"], "core")
        self.assertEqual(by_number["6.334"]["priority"], "historical")
        self.assertEqual(by_number["6.622"]["primary_domain"], "power-electronics")

    def test_generated_projection_lists_citing_lessons(self):
        outputs = catalogue.build(ROOT)
        projection = {c["id"]: c for c in outputs[catalogue.REFERENCES_OUT]["courses"]}
        lessons = outputs[catalogue.LESSONS_OUT]["lessons"]
        for row in lessons:
            for ref in row["academic_references"]:
                self.assertIn(row["slug"], projection[ref]["lessons"])
        self.assertIn("buck-open-lab", projection["mit-6-622-2023"]["lessons"])
        for course in projection.values():
            self.assertNotIn("verified", course)  # curation noise and raw sub-page lists stay in the source catalogue

    def test_duplicate_id_rejected(self):
        self.mutate(lambda d: d["courses"].append(dict(d["courses"][0])))
        with self.assertRaisesRegex(ValueError, "Duplicate reference id"):
            catalogue.build(self.root)

    def test_duplicate_canonical_url_rejected(self):
        def change(data):
            clone = dict(data["courses"][0])
            clone["id"] = "mit-duplicate-url"
            data["courses"].append(clone)
        self.mutate(change)
        with self.assertRaisesRegex(ValueError, "canonical URL"):
            catalogue.build(self.root)

    def test_unknown_module_mapping_rejected(self):
        self.mutate(lambda d: d["courses"][0]["mapped_modules"].append({"module": "pe.unicorn", "coverage": "core"}))
        with self.assertRaisesRegex(ValueError, "unknown module"):
            catalogue.build(self.root)

    def test_unknown_domain_rejected(self):
        self.mutate(lambda d: d["courses"][0].update(primary_domain="quantum"))
        with self.assertRaisesRegex(ValueError, "unknown domain"):
            catalogue.build(self.root)

    def test_verified_status_requires_verified_block(self):
        def change(data):
            course = data["courses"][0]
            course.pop("verified")
        self.mutate(change)
        with self.assertRaisesRegex(ValueError, "without a matching verified block"):
            catalogue.build(self.root)

    def test_empty_url_rejected_by_schema(self):
        self.mutate(lambda d: d["courses"][0].update(url=""))
        with self.assertRaises(Exception):
            catalogue.build(self.root)


if __name__ == "__main__":
    unittest.main()
