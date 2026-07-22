from __future__ import annotations

import importlib.util
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "codex-capability-router"
    / "scripts"
    / "query_capability_router.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("public_capability_router", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CapabilityRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.router = load_module()

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "capabilities.sqlite"
        connection = sqlite3.connect(self.db_path)
        connection.executescript(
            """
            CREATE TABLE capabilities (
              id TEXT,
              kind TEXT,
              name TEXT,
              display_name TEXT,
              category TEXT,
              status TEXT,
              description TEXT,
              trigger_terms TEXT,
              source_path TEXT,
              source_url TEXT,
              trust_level TEXT,
              permissions TEXT,
              last_verified TEXT,
              notes TEXT
            );
            CREATE TABLE routes (
              category TEXT,
              primary_capability TEXT,
              fallback_capability TEXT,
              notes TEXT
            );
            """
        )
        connection.executemany(
            """
            INSERT INTO capabilities (
              id, kind, name, display_name, category, status,
              description, trigger_terms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "plugin_skill:motion-studio",
                    "plugin_skill",
                    "motion-studio",
                    "Motion Studio",
                    "general",
                    "installed",
                    "Create video compositions and motion graphics.",
                    "video animation motion graphics",
                ),
                (
                    "plugin:product-design",
                    "plugin",
                    "product-design",
                    "Product Design",
                    "product_design",
                    "installed",
                    "Explore and validate product designs.",
                    "product design ux ui prototype",
                ),
                (
                    "plugin:mail",
                    "plugin",
                    "mail",
                    "Mail",
                    "general",
                    "installed",
                    "Work with email. Tool support: \U0001f6e0\ufe0f",
                    "mail email inbox",
                ),
            ],
        )
        connection.commit()
        connection.close()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_explicit_capability_name_is_ranked_first(self) -> None:
        result = self.router.route_task(
            self.db_path,
            "Use Motion Studio to create a video with motion graphics",
            8,
        )

        self.assertEqual(
            "motion-studio",
            result["installed_recommendations"][0]["name"],
        )
        self.assertIn("native", result["use_contract"].lower())

    def test_task_text_supplements_a_broad_category_route(self) -> None:
        result = self.router.route_task(
            self.db_path,
            "Create a video with motion graphics",
            8,
        )

        names = [item["name"] for item in result["installed_recommendations"]]
        self.assertIn("motion-studio", names)
        self.assertNotIn("mail", names)

    def test_explicit_display_name_is_ranked_first(self) -> None:
        result = self.router.route_task(
            self.db_path,
            "Use Product Design before implementing this prototype",
            8,
        )

        self.assertEqual(
            "product-design",
            result["installed_recommendations"][0]["name"],
        )

    def test_cli_writes_utf8_when_the_inherited_console_encoding_is_legacy(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "cp936"

        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--db",
                str(self.db_path),
                "--task",
                "Use Mail",
            ],
            capture_output=True,
            check=False,
            env=environment,
        )

        self.assertEqual(0, completed.returncode, completed.stderr.decode("utf-8", "replace"))
        self.assertIn("Tool support", completed.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
