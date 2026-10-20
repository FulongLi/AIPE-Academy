"""Knowledge architecture tests: four domains, tracks, modules, cross-domain edges, cycles and learning paths."""
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

DOMAINS = ["foundations", "power-electronics", "power-systems", "renewable-energy"]


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ("schemas", "curriculum", "references", "labs"):
            shutil.copytree(ROOT / path, self.root / path)
        self.path = self.root / "curriculum/taxonomy.json"

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, fn):
        taxonomy = json.loads(self.path.read_text(encoding="utf-8"))
        fn(taxonomy)
        self.path.write_text(json.dumps(taxonomy), encoding="utf-8")

    def test_four_canonical_domains_in_order(self):
        taxonomy = catalogue.load_taxonomy(ROOT)
        self.assertEqual([d["id"] for d in sorted(taxonomy["domains"], key=lambda d: d["order"])], DOMAINS)
        for domain in taxonomy["domains"]:
            self.assertTrue(any(t["domain"] == domain["id"] for t in taxonomy["tracks"]), domain["id"])
            self.assertTrue(any(m["domain"] == domain["id"] for m in taxonomy["modules"]), domain["id"])

    def test_foundation_modules_f00_to_f09_are_preserved(self):
        taxonomy = catalogue.load_taxonomy(ROOT)
        codes = {m.get("legacy", {}).get("foundation_module") for m in taxonomy["modules"] if m["domain"] == "foundations"}
        self.assertEqual(codes - {None}, {f"F0{i}" for i in range(10)})

    def test_seven_stage_path_is_preserved(self):
        taxonomy = catalogue.load_taxonomy(ROOT)
        path = next(p for p in taxonomy["learning_paths"] if p["id"] == "power-electronics-core")
        self.assertEqual([s["id"] for s in path["stages"]], [
            "00-orientation", "01-foundations", "02-components", "03-converters",
            "04-modeling-and-control", "05-practical-design", "06-systems-and-applications",
        ])
        self.assertEqual(set(path["gates"]), {"G1", "G2", "G3"})

    def test_cross_domain_dependencies_exist(self):
        taxonomy = catalogue.load_taxonomy(ROOT)
        modules = {m["id"]: m for m in taxonomy["modules"]}
        self.assertIn("pe.topologies", modules["re.mppt"]["requires"] + modules["re.storage"]["requires"])
        self.assertIn("pe.control", modules["ps.grid-converters"]["requires"])
        self.assertIn("f.ac", modules["ps.three-phase"]["requires"])
        cross = [m for m in modules.values() if any(modules[r]["domain"] != m["domain"] for r in m["requires"])]
        self.assertGreaterEqual(len(cross), 10)

    def test_bilingual_labels(self):
        taxonomy = catalogue.load_taxonomy(ROOT)
        for group in ("domains", "tracks", "modules"):
            for item in taxonomy[group]:
                for field in ("title", "summary"):
                    self.assertEqual(set(item[field]), {"en", "zh"}, f"{group} {item['id']} {field}")

    def test_generated_graph_matches_catalogue(self):
        outputs = catalogue.build(ROOT)
        graph = outputs[catalogue.GRAPH_OUT]
        lessons = {row["slug"]: row for row in outputs[catalogue.LESSONS_OUT]["lessons"]}
        self.assertEqual([d["id"] for d in graph["domains"]], DOMAINS)
        for module in graph["modules"]:
            for slug in module["lessons"]:
                row = lessons[slug]
                self.assertIn(module["id"], [row["module"]] + row["covers"])
            if module["lessons"]:
                self.assertIn(module["status"], {"outline", "draft", "available"})
            else:
                self.assertEqual(module["status"], "planned")
        available = {m["domain"] for m in graph["modules"] if m["status"] == "available"}
        self.assertEqual(available, set(DOMAINS))

    def test_module_prerequisite_cycle_rejected(self):
        self.mutate(lambda t: next(m for m in t["modules"] if m["id"] == "f.quantities")["requires"].append("pe.control"))
        with self.assertRaisesRegex(ValueError, "cycle"):
            catalogue.build(self.root)

    def test_track_outside_domain_rejected(self):
        self.mutate(lambda t: next(m for m in t["modules"] if m["id"] == "pe.buck").update(track="circuits"))
        with self.assertRaisesRegex(ValueError, "outside its domain"):
            catalogue.build(self.root)

    def test_unknown_requires_rejected(self):
        self.mutate(lambda t: next(m for m in t["modules"] if m["id"] == "pe.buck")["requires"].append("pe.unicorn"))
        with self.assertRaisesRegex(ValueError, "unknown"):
            catalogue.build(self.root)

    def test_duplicate_module_rejected(self):
        self.mutate(lambda t: t["modules"].append(dict(t["modules"][0])))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            catalogue.build(self.root)

    def test_gate_must_be_defined(self):
        self.mutate(lambda t: t["learning_paths"][0]["stages"][2].update(gate="G9"))
        with self.assertRaisesRegex(ValueError, "undefined gate"):
            catalogue.build(self.root)


if __name__ == "__main__":
    unittest.main()
