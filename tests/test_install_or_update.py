from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.install_or_update import MANAGED_SKILLS, install_or_update


class InstallOrUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source"
        self.codex_home = self.root / "codex-home"
        self._write_source("v1")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_source(self, version: str) -> None:
        for skill_name in MANAGED_SKILLS:
            skill_dir = self.source / "skills" / skill_name
            (skill_dir / "agents").mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ndescription: Test skill.\n---\n\n{version}\n",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                f'interface:\n  display_name: "{skill_name}"\n'
                '  short_description: "Test skill"\n'
                f'  default_prompt: "Use ${skill_name}."\n',
                encoding="utf-8",
            )

        trigger_candidates = (
            self.source
            / "skills"
            / "skill-evolution-core"
            / "references"
            / "trigger-candidates.md"
        )
        trigger_candidates.parent.mkdir(parents=True, exist_ok=True)
        trigger_candidates.write_text(f"upstream trigger template {version}\n", encoding="utf-8")

        devolution_ledger = (
            self.source
            / "skills"
            / "skill-evolution-core"
            / "references"
            / "devolution-ledger.md"
        )
        devolution_ledger.write_text(f"upstream devolution ledger {version}\n", encoding="utf-8")

        registry = (
            self.source
            / "skills"
            / "codex-capability-router"
            / "references"
            / "external-skill-registry.md"
        )
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text(f"upstream registry template {version}\n", encoding="utf-8")

    def _first_install(self):
        return install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            evolution_trigger="复盘成长",
            absorption_trigger="吸收能力",
            non_interactive=True,
        )

    def test_first_install_generates_entry_with_selected_triggers(self) -> None:
        result = self._first_install()

        entry = self.codex_home / "skills" / "skill-evolution-entry" / "SKILL.md"
        entry_text = entry.read_text(encoding="utf-8")
        self.assertTrue(result.first_install)
        self.assertIn("复盘成长", entry_text)
        self.assertIn("吸收能力", entry_text)
        self.assertTrue(
            (self.codex_home / "skills" / "skill-evolution-core" / "SKILL.md").is_file()
        )

        manifest = json.loads(
            (self.codex_home / ".skill-evolution-framework.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["triggers"]["evolution"], "复盘成长")
        self.assertEqual(manifest["triggers"]["absorption"], "吸收能力")

    def test_interactive_first_install_asks_for_both_triggers(self) -> None:
        with patch("builtins.input", side_effect=["整理经验", "引入能力"]) as prompt:
            install_or_update(source_root=self.source, codex_home=self.codex_home)

        entry = self.codex_home / "skills" / "skill-evolution-entry" / "SKILL.md"
        entry_text = entry.read_text(encoding="utf-8")
        self.assertEqual(prompt.call_count, 2)
        self.assertIn("整理经验", entry_text)
        self.assertIn("引入能力", entry_text)

    def test_first_install_rejects_missing_or_duplicate_triggers(self) -> None:
        with self.assertRaisesRegex(ValueError, "required"):
            install_or_update(
                source_root=self.source,
                codex_home=self.codex_home,
                non_interactive=True,
            )

        with self.assertRaisesRegex(ValueError, "different"):
            install_or_update(
                source_root=self.source,
                codex_home=self.codex_home,
                evolution_trigger="同一个词",
                absorption_trigger="同一个词",
                non_interactive=True,
            )

    def test_update_preserves_generated_entry_and_saved_triggers(self) -> None:
        self._first_install()
        entry = self.codex_home / "skills" / "skill-evolution-entry" / "SKILL.md"
        original_entry = entry.read_text(encoding="utf-8") + "\nMy personal route.\n"
        entry.write_text(original_entry, encoding="utf-8")
        self._write_source("v2")

        result = install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            non_interactive=True,
        )

        self.assertFalse(result.first_install)
        self.assertEqual(entry.read_text(encoding="utf-8"), original_entry)
        updated_skill = self.codex_home / "skills" / "coding-debug-rules" / "SKILL.md"
        self.assertIn("v2", updated_skill.read_text(encoding="utf-8"))

    def test_update_replaces_unchanged_managed_file(self) -> None:
        self._first_install()
        self._write_source("v2")

        result = install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            non_interactive=True,
        )

        target = self.codex_home / "skills" / "project-rules-router" / "SKILL.md"
        self.assertIn("v2", target.read_text(encoding="utf-8"))
        self.assertIn("skills/project-rules-router/SKILL.md", result.updated)

    def test_update_preserves_modified_managed_file_and_stages_upstream_copy(self) -> None:
        self._first_install()
        target = self.codex_home / "skills" / "research-verification" / "SKILL.md"
        target.write_text("my local evolution\n", encoding="utf-8")
        self._write_source("v2")

        result = install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            non_interactive=True,
        )

        relative = "skills/research-verification/SKILL.md"
        pending = self.codex_home / ".skill-evolution-updates" / relative
        self.assertEqual(target.read_text(encoding="utf-8"), "my local evolution\n")
        self.assertIn("v2", pending.read_text(encoding="utf-8"))
        self.assertIn(relative, result.preserved)

        self._write_source("v3")
        second_result = install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            non_interactive=True,
        )
        self.assertEqual(target.read_text(encoding="utf-8"), "my local evolution\n")
        self.assertIn("v3", pending.read_text(encoding="utf-8"))
        self.assertIn(relative, second_result.preserved)

    def test_update_never_overwrites_personal_data_files(self) -> None:
        self._first_install()
        trigger_candidates = (
            self.codex_home
            / "skills"
            / "skill-evolution-core"
            / "references"
            / "trigger-candidates.md"
        )
        registry = (
            self.codex_home
            / "skills"
            / "codex-capability-router"
            / "references"
            / "external-skill-registry.md"
        )
        devolution_ledger = (
            self.codex_home
            / "skills"
            / "skill-evolution-core"
            / "references"
            / "devolution-ledger.md"
        )
        trigger_candidates.write_text("my trigger history\n", encoding="utf-8")
        registry.write_text("my installed capabilities\n", encoding="utf-8")
        devolution_ledger.write_text("my devolution decisions\n", encoding="utf-8")
        self._write_source("v2")

        result = install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            non_interactive=True,
        )

        self.assertEqual(trigger_candidates.read_text(encoding="utf-8"), "my trigger history\n")
        self.assertEqual(registry.read_text(encoding="utf-8"), "my installed capabilities\n")
        self.assertEqual(
            devolution_ledger.read_text(encoding="utf-8"), "my devolution decisions\n"
        )
        self.assertIn(
            "skills/skill-evolution-core/references/trigger-candidates.md",
            result.preserved,
        )
        self.assertIn(
            "skills/skill-evolution-core/references/devolution-ledger.md",
            result.preserved,
        )
        self.assertIn(
            "skills/codex-capability-router/references/external-skill-registry.md",
            result.preserved,
        )

    def test_update_leaves_unmanaged_local_skill_untouched(self) -> None:
        self._first_install()
        personal_skill = self.codex_home / "skills" / "my-private-project" / "SKILL.md"
        personal_skill.parent.mkdir(parents=True, exist_ok=True)
        personal_skill.write_text("private project knowledge\n", encoding="utf-8")
        self._write_source("v2")

        install_or_update(
            source_root=self.source,
            codex_home=self.codex_home,
            non_interactive=True,
        )

        self.assertEqual(
            personal_skill.read_text(encoding="utf-8"), "private project knowledge\n"
        )

    def test_public_managed_skills_do_not_define_fixed_chinese_shortcuts(self) -> None:
        repository_skills = Path(__file__).resolve().parents[1] / "skills"
        for skill_name in MANAGED_SKILLS:
            for path in (repository_skills / skill_name).rglob("*"):
                if path.is_file() and path.suffix in {".md", ".py", ".yaml", ".yml"}:
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("进化", text, path)
                    self.assertNotIn("吞噬", text, path)
                    self.assertNotIn("退化", text, path)

    def test_global_agents_template_uses_placeholders_not_private_details(self) -> None:
        template = (
            Path(__file__).resolve().parents[1]
            / "templates"
            / "global-agents-template"
            / "AGENTS.md"
        )
        text = template.read_text(encoding="utf-8")
        self.assertIn("<EVOLUTION_SHORTCUT>", text)
        self.assertIn("<ABSORPTION_SHORTCUT>", text)
        self.assertIn("<RULE_MAINTENANCE_SHORTCUT>", text)
        forbidden = [
            "C:" + "\\Users" + "\\",
            "G:" + "\\",
            "D" + "NF",
            "293" + "297533",
            "kyt" + "19970215",
            "进化",
            "吞噬",
            "退化",
        ]
        for value in forbidden:
            self.assertNotIn(value, text)

    def test_legacy_install_without_manifest_preserves_existing_files(self) -> None:
        existing = self.codex_home / "skills" / "coding-debug-rules" / "SKILL.md"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("legacy personal rules\n", encoding="utf-8")

        result = self._first_install()

        pending = (
            self.codex_home
            / ".skill-evolution-updates"
            / "skills"
            / "coding-debug-rules"
            / "SKILL.md"
        )
        self.assertEqual(existing.read_text(encoding="utf-8"), "legacy personal rules\n")
        self.assertTrue(pending.is_file())
        self.assertIn("skills/coding-debug-rules/SKILL.md", result.preserved)


if __name__ == "__main__":
    unittest.main()
