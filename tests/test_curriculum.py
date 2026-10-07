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


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in ("schemas", "curriculum", "references"):
            shutil.copytree(ROOT / path, self.root / path)

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, fn):
        path = self.root / "curriculum/catalogue.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        fn(rows)
        path.write_text(json.dumps(rows), encoding="utf-8")

    def test_deterministic_and_current(self):
        expected = (ROOT / "generated/lessons.json").read_text(encoding="utf-8")
        self.assertEqual(catalogue.render(catalogue.build()), expected)
        self.assertEqual(catalogue.render(catalogue.build()), expected)

    def test_duplicate(self):
        self.mutate(lambda r: r.append(copy.deepcopy(r[0])))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            catalogue.build(self.root)

    def test_missing_prerequisite(self):
        self.mutate(lambda r: r[0].update(prerequisites=["missing"]))
        with self.assertRaisesRegex(ValueError, "Invalid"):
            catalogue.build(self.root)

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
        self.mutate(lambda r: r[0].update(tools=[{"id":"matlab", "licence_class":"commercial", "optional":False}]))
        with self.assertRaisesRegex(ValueError, "proprietary"):
            catalogue.build(self.root)


class BuckTests(unittest.TestCase):
    def test_balance_and_ripple(self):
        result = lab.calculate()
        self.assertAlmostEqual(result["duty_ratio"]["value"], 0.5)
        self.assertAlmostEqual(result["inductor_ripple_pp"]["value"], 0.4)
        self.assertAlmostEqual(result["output_current"]["value"], 2.5)
        self.assertAlmostEqual(result["load_resistance"]["value"], 4.8)

    def test_domain_and_ccm(self):
        for kwargs in ({"frequency":0},{"v_out":30},{"power":0.01},{"v_in":float("nan")},{"power":float("inf")}):
            with self.assertRaises(ValueError):
                lab.calculate(**kwargs)


if __name__ == "__main__":
    unittest.main()
