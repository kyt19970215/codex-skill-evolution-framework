from __future__ import annotations

import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "skill-evolution-core" / "scripts" / "trigger_event_tools.py"


def load_module():
    spec = importlib.util.spec_from_file_location("public_trigger_event_tools", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TriggerEventToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tools = load_module()

    def test_summary_applies_recency_weight_and_separates_hook_evidence(self) -> None:
        now = dt.datetime(2026, 7, 10, tzinfo=dt.timezone.utc)
        events = [
            {
                "time": "2026-07-10T00:00:00+00:00",
                "suggested_route": "coding-debug-rules",
                "was_correct": True,
                "hook_event": "UserPromptSubmit",
            },
            {
                "time": "2026-06-10T00:00:00+00:00",
                "suggested_route": "coding-debug-rules",
                "was_correct": None,
                "hook_event": "UserPromptSubmit",
            },
            {
                "time": "2026-07-10T00:00:00+00:00",
                "suggested_route": "skill-evolution-router",
                "was_correct": False,
                "evidence_kind": "smoke_test",
            },
        ]

        summary = self.tools.build_summary(events, now=now, half_life_days=30)

        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["real_hook_events"], 2)
        self.assertEqual(summary["smoke_test_events"], 1)
        self.assertAlmostEqual(
            summary["routes"]["coding-debug-rules"]["weighted_score"],
            1.5,
            places=5,
        )
        self.assertEqual(summary["routes"]["coding-debug-rules"]["unlabeled"], 1)

    def test_label_event_updates_only_the_selected_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = Path(temp_dir) / "events.jsonl"
            ledger.write_text(
                "\n".join(
                    [
                        json.dumps({"event_id": "one", "actual_route": "", "was_correct": None}),
                        json.dumps({"event_id": "two", "actual_route": "", "was_correct": None}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            changed = self.tools.label_event(
                ledger,
                event_id="two",
                actual_route="skill-evolution-validator",
                was_correct=True,
                changed_rules=False,
            )
            events = self.tools.load_events(ledger)

        self.assertTrue(changed)
        self.assertEqual(events[0]["actual_route"], "")
        self.assertEqual(events[1]["actual_route"], "skill-evolution-validator")
        self.assertTrue(events[1]["was_correct"])


if __name__ == "__main__":
    unittest.main()
