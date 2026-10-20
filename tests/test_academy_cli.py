"""Functional tests of the shared Academy companion command used by the Codex skill and the Claude Code plugin.

They exercise onboarding, lesson selection, prerequisite checks, learning
continuation, lab execution, missing-dependency reporting and academic
reference retrieval against the real repository checkout.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills/aipe-academy/scripts/academy.py"


def run(*args, record=None, cwd=ROOT, expect=0):
    command = [sys.executable, str(CLI), "--repo", str(ROOT), "--json"]
    if record is not None:
        command += ["--record", str(record)]
    command += list(args)
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", cwd=str(cwd), timeout=120)
    if completed.returncode != expect:
        raise AssertionError(f"{' '.join(args)} exited {completed.returncode}, expected {expect}\n{completed.stdout}\n{completed.stderr}")
    return json.loads(completed.stdout) if completed.stdout.strip().startswith(("{", "[")) else completed.stdout, completed.stderr


class DiscoveryTests(unittest.TestCase):
    def test_status_describes_the_checkout(self):
        status, _ = run("status")
        self.assertEqual(status["domains"], ["foundations", "power-electronics", "power-systems", "renewable-energy"])
        self.assertGreaterEqual(status["lessons_by_status"]["available"], 5)
        self.assertEqual(status["academic_references"], 22)

    def test_domains_and_entry_lessons(self):
        domains, _ = run("domains")
        self.assertEqual([d["id"] for d in domains], ["foundations", "power-electronics", "power-systems", "renewable-energy"])
        for domain in domains:
            self.assertTrue(domain["entry_lessons"], domain["id"])
        zh, _ = run("--language", "zh", "domains")
        self.assertEqual(zh[3]["title"], "可再生能源")

    def test_lesson_selection_and_filters(self):
        lessons, _ = run("lessons", "--domain", "foundations", "--lang", "zh-CN")
        self.assertTrue(all(l["language"] == "zh-CN" and l["domain"] == "foundations" for l in lessons))
        lesson, _ = run("lesson", "buck-converter-fundamentals")
        self.assertEqual(lesson["module"], "pe.buck")
        self.assertTrue(lesson["lab_paths"])
        self.assertTrue(any(r["id"] == "mit-6-622-2023" for r in lesson["academic_reference_details"]))
        with_content, _ = run("lesson", "buck-converter-fundamentals", "--content")
        self.assertIn("## Learning Objectives", with_content["content"])
        _, stderr = run("lesson", "no-such-lesson", expect=1)
        self.assertIn("Unknown lesson slug", stderr)

    def test_search_finds_lessons_modules_and_references(self):
        found, _ = run("search", "three-phase")
        self.assertIn("three-phase-fundamentals", [l["slug"] for l in found["lessons"]])
        self.assertIn("ps.three-phase", [m["id"] for m in found["modules"]])

    def test_academic_references_for_a_lesson(self):
        refs, _ = run("references", "--lesson", "solar-pv-fundamentals")
        self.assertIn("mit-2-627-2013", [r["id"] for r in refs])
        one, _ = run("reference", "mit-6-622-2023")
        self.assertEqual(one["course_number"], "6.622")
        self.assertIn("not affiliated", one["note"])
        self.assertIn("buck-open-lab", one["lessons"])


class OnboardingAndPrerequisiteTests(unittest.TestCase):
    def test_onboarding_matches_goal(self):
        onboarding, _ = run("onboarding", "--goal", "Help me understand how solar panels generate electricity")
        self.assertEqual(onboarding["matched_domains"], ["renewable-energy"])
        self.assertEqual(onboarding["entry_points"][0]["first_available_lesson"]["slug"], "solar-pv-fundamentals")
        self.assertEqual(len(onboarding["diagnostic_questions"]), 3)
        beginner, _ = run("onboarding", "--goal", "Teach me electrical engineering from the beginning")
        self.assertIn("foundations", beginner["matched_domains"])

    def test_prerequisites_without_record_are_all_unmet(self):
        result, _ = run("prerequisites", "solar-pv-fundamentals")
        slugs = {p["slug"] for p in result["prerequisite_lessons"]}
        self.assertIn("dc-circuit-fundamentals", slugs)
        self.assertIn("buck-converter-fundamentals", slugs)
        self.assertEqual(set(result["unmet_prerequisites"]), slugs)
        self.assertIsNone(result["record_used"])

    def test_learning_path_with_gates(self):
        path, _ = run("path", "power-electronics-core")
        self.assertEqual(len(path["stages"]), 7)
        self.assertEqual(path["stages"][3]["gate"], "G1")
        self.assertIn("f.dc-circuits", path["gates"]["G1"]["missing"])


class RecordAndContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.record = Path(self.temp.name) / "learning/progress.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_resume_without_record_is_honest(self):
        _, stderr = run("resume", record=self.record, expect=1)
        self.assertIn("No learning record", stderr)

    def test_record_lifecycle_and_independence_rule(self):
        created, _ = run("record", "init", "--goal", "power electronics", "--lang", "en", "--time", "3 h/week", record=self.record)
        self.assertEqual(created["learner"]["goal"], "power electronics")
        self.assertTrue(self.record.is_file())
        self.assertTrue((self.record.parent / "progress.md").is_file())
        run("record", "set", "--lesson", "dc-circuit-fundamentals", "--module", "f.dc-circuits", "--next-task", "loaded divider", record=self.record)
        _, stderr = run("record", "log", "--module", "f.dc-circuits", "--task", "divider", "--mode", "assisted", "--evidence", "needed the formula", "--status", "demonstrated", record=self.record, expect=1)
        self.assertIn("Only independent work", stderr)
        logged, _ = run("record", "log", "--lesson", "dc-circuit-fundamentals", "--module", "f.dc-circuits", "--task", "loaded divider with new numbers", "--mode", "independent", "--evidence", "correct 20 mA and explained halving", "--status", "demonstrated", record=self.record)
        self.assertEqual(logged["module_status"]["f.dc-circuits"], "demonstrated")
        resumed, _ = run("resume", record=self.record)
        self.assertEqual(resumed["current"]["lesson"], "dc-circuit-fundamentals")
        self.assertIn("f.dc-circuits", resumed["demonstrated_modules"])
        prereq, _ = run("prerequisites", "buck-converter-fundamentals", record=self.record)
        demonstrated = {p["slug"]: p["demonstrated"] for p in prereq["prerequisite_lessons"]}
        self.assertFalse(demonstrated["dc-circuit-fundamentals"], "f.quantities is also covered by the lesson and is not yet demonstrated")
        run("record", "log", "--module", "f.quantities", "--task", "unit conversion", "--mode", "independent", "--evidence", "W vs Wh explained", "--status", "demonstrated", record=self.record)
        prereq, _ = run("prerequisites", "buck-converter-fundamentals", record=self.record)
        demonstrated = {p["slug"]: p["demonstrated"] for p in prereq["prerequisite_lessons"]}
        self.assertTrue(demonstrated["dc-circuit-fundamentals"])
        self.assertIn("converters", prereq["unmet_prerequisites"])

    def test_record_rejects_unknown_ids(self):
        run("record", "init", record=self.record)
        _, stderr = run("record", "set", "--lesson", "nope", record=self.record, expect=1)
        self.assertIn("Unknown lesson slug", stderr)


class LabExecutionTests(unittest.TestCase):
    def test_lab_runs_and_relays_json(self):
        result, _ = run("lab", "buck-open-lab")
        self.assertEqual(result["exit_code"], 0)
        self.assertAlmostEqual(result["result"]["duty_ratio"]["value"], 0.5)

    def test_lab_rejection_is_reported_not_hidden(self):
        result, _ = run("lab", "buck-open-lab", "--", "--power", "0.01", expect=2)
        self.assertEqual(result["exit_code"], 2, "labs exit with code 2 when they reject an input or assumption")
        self.assertIsNone(result["result"])
        self.assertIn("CCM assumption fails", result["stderr"])

    def test_lab_lists_and_refuses_paths_outside_labs(self):
        listing, _ = run("lab", "--list")
        self.assertIn("buck-open-lab", [l["lesson"] for l in listing])
        _, stderr = run("lab", "scripts/build_catalogue.py", expect=1)
        self.assertIn("not a lab script", stderr)
        _, stderr = run("lab", "orientation", expect=1)
        self.assertIn("has no lab script", stderr)

    def test_lesson_with_several_labs_runs_the_first_and_reports_the_rest(self):
        result, _ = run("lab", "buck-converter-fundamentals")
        self.assertEqual(result["exit_code"], 0)
        self.assertTrue(result["command"][1].replace("\\", "/").endswith("labs/buck_open.py"))
        self.assertEqual(result["other_labs"], ["labs/power-electronics/buck_switching.py"])
        switching, _ = run("lab", "labs/power-electronics/buck_switching.py")
        self.assertEqual(switching["exit_code"], 0)
        self.assertEqual(switching["result"]["steady_state"]["conduction_mode"]["value"] if isinstance(switching["result"]["steady_state"]["conduction_mode"], dict) else switching["result"]["steady_state"]["conduction_mode"], "CCM")

    def test_global_options_accepted_after_the_subcommand(self):
        command = [sys.executable, str(CLI), "status", "--json", "--repo", str(ROOT)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT), timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["academic_references"], 22)
        command = [sys.executable, str(CLI), "domains", "--language", "zh", "--json", "--repo", str(ROOT)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT), timeout=120)
        self.assertEqual(json.loads(completed.stdout)[0]["title"], "基础")

    def test_new_labs_run_through_the_cli(self):
        for slug in ("dc-circuit-fundamentals", "three-phase-fundamentals", "solar-pv-fundamentals"):
            result, _ = run("lab", slug)
            self.assertEqual(result["exit_code"], 0, slug)
            self.assertIsInstance(result["result"], dict, slug)

    def test_check_tools_reports_fallbacks(self):
        tools, _ = run("check-tools")
        self.assertTrue(tools["python_ok"])
        for key in ("matplotlib", "numpy", "ngspice", "git"):
            self.assertIn(key, tools)
            self.assertIsInstance(tools[key], bool)
        self.assertIn("ngspice", tools["fallbacks"])


if __name__ == "__main__":
    unittest.main()
