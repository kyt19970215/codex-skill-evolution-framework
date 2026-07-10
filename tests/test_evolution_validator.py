from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "skill-evolution-validator" / "scripts" / "validate_evolution_skills.py"


def load_module():
    spec = importlib.util.spec_from_file_location("public_evolution_validator", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvolutionValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_module()

    def test_auto_mode_runs_full_first_then_log_based_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            manifest = temp / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "triggers": {
                            "evolution": "review-growth",
                            "absorption": "absorb-capability",
                        },
                    }
                ),
                encoding="utf-8",
            )
            output = temp / "reports"
            now = dt.datetime(2026, 7, 10, tzinfo=dt.timezone.utc)

            first = self.validator.run_validation(
                skills_root=ROOT / "skills",
                output_dir=output,
                manifest_path=manifest,
                mode="auto",
                now=now,
            )
            second = self.validator.run_validation(
                skills_root=ROOT / "skills",
                output_dir=output,
                manifest_path=manifest,
                mode="auto",
                now=now,
            )

        self.assertEqual(first["mode"], "full")
        self.assertEqual(first["behavior_regression"]["status"], "passed")
        self.assertGreater(first["behavior_regression"]["passed"], 0)
        self.assertEqual(second["mode"], "fast")
        self.assertEqual(second["behavior_regression"]["status"], "not_run")
        self.assertIn("existing", second["mode_basis"])

    def test_full_mode_writes_readable_report_and_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            manifest = temp / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "triggers": {
                            "evolution": "review-growth",
                            "absorption": "absorb-capability",
                        },
                    }
                ),
                encoding="utf-8",
            )
            report = self.validator.run_validation(
                skills_root=ROOT / "skills",
                output_dir=temp / "reports",
                manifest_path=manifest,
                mode="full",
                now=dt.datetime(2026, 7, 10, tzinfo=dt.timezone.utc),
            )

            self.assertTrue(Path(report["report_path"]).is_file())
            self.assertTrue(Path(report["json_path"]).is_file())
            self.assertTrue(Path(report["snapshot_path"]).is_file())
            rendered = Path(report["report_path"]).read_text(encoding="utf-8")

        self.assertIn("Evolution Skill Validation Report", rendered)
        self.assertIn("Behavior regression", rendered)
        self.assertIn("Platform freshness", rendered)

    def test_failed_full_run_keeps_auto_mode_on_full_until_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            skills_root = temp / "skills"
            shutil.copytree(ROOT / "skills", skills_root)
            manifest = temp / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "triggers": {
                            "evolution": "review-growth",
                            "absorption": "absorb-capability",
                        },
                    }
                ),
                encoding="utf-8",
            )
            output = temp / "reports"
            now = dt.datetime(2026, 7, 10, tzinfo=dt.timezone.utc)
            good = self.validator.run_validation(
                skills_root=skills_root,
                output_dir=output,
                manifest_path=manifest,
                mode="full",
                now=now,
            )
            snapshot_before = Path(good["snapshot_path"]).read_text(encoding="utf-8")

            cases_path = (
                skills_root
                / "skill-evolution-validator"
                / "references"
                / "regression-cases.json"
            )
            cases = json.loads(cases_path.read_text(encoding="utf-8"))
            cases[0]["expected_route"] = "wrong-route"
            cases_path.write_text(json.dumps(cases), encoding="utf-8")

            failed = self.validator.run_validation(
                skills_root=skills_root,
                output_dir=output,
                manifest_path=manifest,
                mode="full",
                now=now + dt.timedelta(minutes=1),
            )
            retry = self.validator.run_validation(
                skills_root=skills_root,
                output_dir=output,
                manifest_path=manifest,
                mode="auto",
                now=now + dt.timedelta(minutes=2),
            )

            snapshot_after = Path(good["snapshot_path"]).read_text(encoding="utf-8")

        self.assertEqual(failed["status"], "failed")
        self.assertFalse(failed["snapshot_updated"])
        self.assertEqual(snapshot_after, snapshot_before)
        self.assertEqual(retry["mode"], "full")
        self.assertEqual(retry["behavior_regression"]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
