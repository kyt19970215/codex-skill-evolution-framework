from __future__ import annotations

import importlib.util
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "user_prompt_passive_trigger.py"
PROBE = ROOT / "skills" / "skill-evolution-core" / "scripts" / "passive_trigger_probe.py"


def load_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PassiveHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hook = load_path("public_passive_hook", HOOK)
        cls.probe = load_path("public_passive_probe_for_hook", PROBE)

    def test_hook_parses_official_user_prompt_submit_fields(self) -> None:
        payload = self.hook.parse_hook_payload(
            json.dumps(
                {
                    "prompt": "Audit the evolution skill health.",
                    "session_id": "private-session-id",
                    "turn_id": "private-turn-id",
                    "cwd": "/private/workspace",
                }
            )
        )
        self.assertEqual(payload["prompt"], "Audit the evolution skill health.")
        self.assertEqual(payload["session_id"], "private-session-id")

    def test_event_is_anonymous_by_default_and_hint_is_advisory(self) -> None:
        metadata = {
            "prompt": "Audit the evolution skill health.",
            "session_id": "private-session-id",
            "turn_id": "private-turn-id",
            "cwd": "/private/workspace",
            "transcript_path": "/private/transcript.jsonl",
        }
        with patch.object(self.hook, "load_probe", return_value=self.probe):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CODEX_PASSIVE_TRIGGER_RECORD_TEXT", None)
                event = self.hook.build_event(
                    metadata["prompt"],
                    metadata,
                    shortcuts=["review-growth", "absorb-capability"],
                )

        self.assertEqual(event["source_signal"], "[redacted]")
        self.assertNotIn("private-session-id", json.dumps(event))
        self.assertNotIn("/private/workspace", json.dumps(event))
        self.assertEqual(event["suggested_route"], "skill-evolution-validator")
        self.assertFalse(event["auto_action_allowed"])

        output = self.hook.hook_output(event)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertTrue(output["continue"])
        self.assertIn("advisory only", context)
        self.assertIn("skill-evolution-validator", context)


if __name__ == "__main__":
    unittest.main()
