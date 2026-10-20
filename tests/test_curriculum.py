"""Offline curriculum tests: schema, references, cycles, URLs, languages and the open buck lab."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalogue = load("catalogue", "scripts/build_catalogue.py")
lab = load("lab", "labs/buck_open.py")

# Public URLs published before v0.2. Changing one requires an explicit redirect
# in the website repository and a deliberate edit of this list.
LEGACY_URLS = {
    "/academy/foundations/orientation/",
    "/academy/foundations/foundations/",
    "/academy/foundations/prerequisite-path-zh/",
    "/academy/foundations/first-circuit-zh/",
    "/academy/power-electronics/components/",
    "/academy/power-electronics/converters/",
    "/academy/power-electronics/buck-converter/",
    "/academy/power-electronics/buck-open-lab/",
    "/academy/power-electronics/dynamics-and-control/",
    "/academy/power-electronics/practical-design/",
    "/academy/power-electronics/systems-applications/",
}


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ("schemas", "curriculum", "references", "labs"):
            shutil.copytree(ROOT / path, self.root / path)

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, fn):
        path = self.root / "curriculum/catalogue.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        fn(rows)
        path.write_text(json.dumps(rows), encoding="utf-8")

    def row(self, rows, slug):
        return next(r for r in rows if r["slug"] == slug)

    def test_deterministic_and_current(self):
        outputs = catalogue.build()
        for relative, payload in outputs.items():
            expected = (ROOT / relative).read_text(encoding="utf-8")
            self.assertEqual(catalogue.render(payload), expected, relative)
        self.assertEqual(catalogue.render(outputs), catalogue.render(catalogue.build()))

    def test_legacy_urls_preserved(self):
        urls = {row["url"] for row in catalogue.build()[catalogue.LESSONS_OUT]["lessons"]}
        self.assertTrue(LEGACY_URLS.issubset(urls), LEGACY_URLS - urls)

    def test_four_domains_each_have_an_available_lesson(self):
        lessons = catalogue.build()[catalogue.LESSONS_OUT]["lessons"]
        available = {row["domain"] for row in lessons if row["status"] == "available"}
        self.assertEqual(available, {"foundations", "power-electronics", "power-systems", "renewable-energy"})

    def test_standard_format_lessons_carry_labs_and_references(self):
        lessons = catalogue.build()[catalogue.LESSONS_OUT]["lessons"]
        standard = [row for row in lessons if row["format"] == "aipe-lesson-v2"]
        self.assertGreaterEqual(len(standard), 4)
        for row in standard:
            self.assertTrue(row["labs"], row["slug"])
            self.assertTrue(row["academic_references"], row["slug"])
            self.assertEqual(row["status"], "available", row["slug"])

    def test_language_mapping(self):
        lessons = {row["slug"]: row for row in catalogue.build()[catalogue.LESSONS_OUT]["lessons"]}
        self.assertEqual(lessons["first-circuit-zh"]["translations"], {"en": None, "zh-CN": "first-circuit-zh"})
        self.assertEqual(lessons["orientation"]["translations"]["en"], "orientation")
        for row in lessons.values():
            self.assertIn(row["translation_status"], {"original", "reviewed-translation", "machine-translation"})

    def test_duplicate(self):
        self.mutate(lambda r: r.append(copy.deepcopy(r[0])))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            catalogue.build(self.root)

    def test_duplicate_language_for_concept(self):
        def change(rows):
            clone = copy.deepcopy(rows[0])
            clone["slug"] = "orientation-copy"
            rows.append(clone)
        self.mutate(change)
        with self.assertRaisesRegex(ValueError, "Concept"):
            catalogue.build(self.root)

    def test_missing_prerequisite(self):
        self.mutate(lambda r: r[0].update(prerequisites=["missing"]))
        with self.assertRaisesRegex(ValueError, "Invalid"):
            catalogue.build(self.root)

    def test_cross_domain_prerequisite_is_allowed(self):
        self.mutate(lambda r: self.row(r, "components").update(prerequisites=["foundations", "first-circuit-zh"]))
        lessons = {row["slug"]: row for row in catalogue.build(self.root)[catalogue.LESSONS_OUT]["lessons"]}
        self.assertIn("first-circuit-zh", lessons["components"]["prerequisites"])

    def test_missing_reference(self):
        self.mutate(lambda r: r[0].update(references=["missing.json"]))
        with self.assertRaisesRegex(ValueError, "reference"):
            catalogue.build(self.root)

    def test_prerequisite_cycle(self):
        def cycle(rows):
            rows[0]["prerequisites"] = [rows[1]["slug"]]
            rows[1]["prerequisites"] = [rows[0]["slug"]]
        self.mutate(cycle)
        with self.assertRaisesRegex(ValueError, "cycle"):
            catalogue.build(self.root)

    def test_traversal(self):
        self.mutate(lambda r: r[0].update(source="../outside.md"))
        with self.assertRaises(ValueError):
            catalogue.build(self.root)

    def test_proprietary_required(self):
        self.mutate(lambda r: r[0].update(tools=[{"id": "matlab", "licence_class": "commercial", "optional": False}]))
        with self.assertRaisesRegex(ValueError, "proprietary"):
            catalogue.build(self.root)

    def test_module_must_belong_to_domain(self):
        self.mutate(lambda r: self.row(r, "components").update(module="f.dc-circuits"))
        with self.assertRaisesRegex(ValueError, "outside its domain"):
            catalogue.build(self.root)

    def test_track_must_match_module(self):
        self.mutate(lambda r: self.row(r, "components").update(track="dc-dc-conversion"))
        with self.assertRaisesRegex(ValueError, "differs from the module"):
            catalogue.build(self.root)

    def test_lesson_type_requires_module(self):
        self.mutate(lambda r: self.row(r, "first-circuit-zh").update(module=None))
        with self.assertRaisesRegex(ValueError, "must name a module"):
            catalogue.build(self.root)

    def test_unknown_academic_reference(self):
        self.mutate(lambda r: self.row(r, "buck-open-lab").update(academic_references=["mit-0-000-1999"]))
        with self.assertRaisesRegex(ValueError, "unknown academic reference"):
            catalogue.build(self.root)

    def test_academic_reference_must_be_linked_in_lesson(self):
        self.mutate(lambda r: self.row(r, "buck-open-lab").update(academic_references=["mit-6-622-2023", "mit-18-06sc-2011"]))
        with self.assertRaisesRegex(ValueError, "does not link its official URL"):
            catalogue.build(self.root)

    def test_missing_lab_script(self):
        self.mutate(lambda r: self.row(r, "buck-open-lab").update(labs=["labs/does_not_exist.py"]))
        with self.assertRaisesRegex(ValueError, "missing lab script"):
            catalogue.build(self.root)

    def test_standard_format_sections_are_enforced(self):
        self.mutate(lambda r: self.row(r, "buck-open-lab").update(format="aipe-lesson-v2"))
        with self.assertRaisesRegex(ValueError, "standard lesson sections"):
            catalogue.build(self.root)

    def test_front_matter_rejected(self):
        source = self.root / "curriculum/03-converters/buck-open-lab.md"
        source.write_text("---\nlayout: x\n---\n" + source.read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "front matter"):
            catalogue.build(self.root)

    def test_unknown_learning_path_lesson(self):
        path = self.root / "curriculum/taxonomy.json"
        taxonomy = json.loads(path.read_text(encoding="utf-8"))
        taxonomy["learning_paths"][0]["stages"][0]["lessons"].append("not-a-lesson")
        path.write_text(json.dumps(taxonomy), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unknown lesson"):
            catalogue.build(self.root)


class BuckTests(unittest.TestCase):
    def test_balance_and_ripple(self):
        result = lab.calculate()
        self.assertAlmostEqual(result["duty_ratio"]["value"], 0.5)
        self.assertAlmostEqual(result["inductor_ripple_pp"]["value"], 0.4)
        self.assertAlmostEqual(result["output_current"]["value"], 2.5)
        self.assertAlmostEqual(result["load_resistance"]["value"], 4.8)

    def test_domain_and_ccm(self):
        for kwargs in ({"frequency": 0}, {"v_out": 30}, {"power": 0.01}, {"v_in": float("nan")}, {"power": float("inf")}):
            with self.assertRaises(ValueError):
                lab.calculate(**kwargs)


if __name__ == "__main__":
    unittest.main()
