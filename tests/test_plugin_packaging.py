"""Packaging tests for the Codex skill and the Claude Code plugin.

Static checks run everywhere. `claude plugin validate` is executed when the
Claude Code CLI is installed and reported as skipped otherwise, so a passing run
never implies that the functional validation happened.
"""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/aipe-academy/SKILL.md"
STUB = ROOT / ".agents/skills/aipe-academy/SKILL.md"
PLUGIN = ROOT / ".claude-plugin/plugin.json"
MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} has no front matter")
    block = text.split("---\n", 2)[1]
    fields = {}
    for line in block.splitlines():
        if line and not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


class SkillTests(unittest.TestCase):
    def check_agent_skills_spec(self, path: Path):
        fields = front_matter(path)
        self.assertEqual(fields["name"], path.parent.name)
        self.assertTrue(NAME_PATTERN.match(fields["name"]))
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertTrue(1 <= len(fields["description"]) <= 1024, len(fields["description"]))
        self.assertLessEqual(len(fields.get("compatibility", "")), 500)
        allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
        self.assertTrue(set(fields) <= allowed, set(fields) - allowed)
        return fields

    def test_shared_skill_follows_agent_skills_spec(self):
        fields = self.check_agent_skills_spec(SKILL)
        self.assertEqual(fields["name"], "aipe-academy")
        for word in ("power electronics", "three-phase", "solar", "continue"):
            self.assertIn(word, fields["description"].lower())
        body = SKILL.read_text(encoding="utf-8")
        self.assertLess(body.count("\n"), 500)
        for command in ("onboarding", "prerequisites", "resume", "record", "lab", "references", "search", "check-tools"):
            self.assertIn(command, body)
        self.assertIn("prompts/tutor-guide.md", body)
        self.assertIn("not affiliated", body)

    def test_codex_stub_points_to_shared_skill(self):
        fields = self.check_agent_skills_spec(STUB)
        self.assertEqual(fields["name"], "aipe-academy")
        self.assertEqual(fields["description"], front_matter(SKILL)["description"], "stub and shared skill must advertise the same triggers")
        body = STUB.read_text(encoding="utf-8")
        self.assertIn("skills/aipe-academy/SKILL.md", body)
        self.assertTrue((STUB.parent / "../../../skills/aipe-academy/SKILL.md").resolve().is_file())

    def test_supporting_files_exist(self):
        self.assertTrue((SKILL.parent / "scripts/academy.py").is_file())
        self.assertTrue((SKILL.parent / "references/commands.md").is_file())
        openai = (SKILL.parent / "agents/openai.yaml").read_text(encoding="utf-8")
        for key in ("interface:", "display_name:", "short_description:", "default_prompt:", "policy:", "allow_implicit_invocation:"):
            self.assertIn(key, openai)


class PluginManifestTests(unittest.TestCase):
    def test_manifest_fields(self):
        manifest = json.loads(PLUGIN.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "aipe-academy")
        self.assertTrue(NAME_PATTERN.match(manifest["name"]))
        self.assertFalse(manifest["name"].startswith(("claude-", "anthropic-", "cc-plugin-")))
        for field in ("version", "description", "author", "homepage", "repository", "license", "keywords"):
            self.assertIn(field, manifest)
        self.assertEqual(manifest["author"]["name"], "AIPE Academy contributors")
        self.assertEqual(manifest["license"], "CC-BY-4.0")
        for name, command in manifest["commands"].items():
            self.assertTrue(NAME_PATTERN.match(name))
            self.assertEqual(sum(key in command for key in ("source", "content")), 1, name)
            self.assertIn("aipe-academy skill", command["content"])
        self.assertTrue((ROOT / "skills/aipe-academy/SKILL.md").is_file(), "default skills/ scan must find the shared skill")
        self.assertFalse((ROOT / ".claude-plugin/skills").exists(), "components must not live inside .claude-plugin/")

    def test_marketplace_lists_the_repository_root_plugin(self):
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        manifest = json.loads(PLUGIN.read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "aipe-academy")
        self.assertTrue(marketplace["owner"]["name"])
        self.assertTrue(marketplace.get("description"))
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], manifest["name"])
        self.assertEqual(entry["source"], "./")
        self.assertNotIn("version", entry, "plugin.json owns the version")

    def test_versions_agree(self):
        manifest = json.loads(PLUGIN.read_text(encoding="utf-8"))
        aipe = json.loads((ROOT / "aipe.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], aipe.get("version", manifest["version"]))
        self.assertIn(manifest["version"], front_matter(SKILL).get("metadata", "") + SKILL.read_text(encoding="utf-8"))


class ClaudeCliValidationTests(unittest.TestCase):
    def test_claude_plugin_validate(self):
        claude = shutil.which("claude")
        if claude is None:
            self.skipTest("Claude Code CLI not installed; functional plugin validation not executed here")
        # The Windows launcher is a shell script, so run through the shell there.
        completed = subprocess.run(f'"{claude}" plugin validate "{ROOT}"', shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        output = (completed.stdout or "") + (completed.stderr or "")
        self.assertEqual(completed.returncode, 0, output)
        self.assertIn("Validation passed", output)


if __name__ == "__main__":
    unittest.main()
