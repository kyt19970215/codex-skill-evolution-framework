from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "skill-evolution-core" / "scripts" / "passive_trigger_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("public_passive_trigger_probe", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PassiveTriggerProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.probe = load_module()
        cls.shortcuts = ["review-growth", "absorb-capability"]

    def assert_route(self, text: str, route: str, level: str, context_route: str = "") -> None:
        result = self.probe.classify(text, self.shortcuts, context_route=context_route)
        self.assertEqual(result["suggested_route"], route)
        self.assertEqual(result["trigger_level"], level)
        self.assertFalse(result["auto_action_allowed"])

    def test_exact_configured_shortcut_routes_to_core(self) -> None:
        self.assert_route("review-growth", "skill-evolution-core", "L4")

    def test_discussion_only_phrase_does_not_force_shortcut(self) -> None:
        self.assert_route(
            "Do not run review-growth; discuss the idea only.",
            "",
            "L0",
        )

    def test_discussion_only_evolution_wording_stays_unrouted(self) -> None:
        self.assert_route(
            "Discuss product evolution, but do not modify any skill.",
            "",
            "L0",
        )

    def test_health_and_freshness_question_routes_to_validator(self) -> None:
        self.assert_route(
            "Audit the evolution skill health, behavior regression, and freshness.",
            "skill-evolution-validator",
            "L4",
        )

    def test_read_only_health_audit_still_routes_to_validator(self) -> None:
        self.assert_route(
            "Audit the evolution skill health, but do not modify files.",
            "skill-evolution-validator",
            "L4",
        )

    def test_durable_rule_capture_routes_to_router(self) -> None:
        self.assert_route(
            "Save this as a durable rule for future tasks.",
            "skill-evolution-router",
            "L1",
        )

    def test_coding_failure_routes_to_debug_skill(self) -> None:
        self.assert_route(
            "The TypeScript build failed with a path encoding error.",
            "coding-debug-rules",
            "L1",
        )

    def test_continuation_uses_prior_advisory_route(self) -> None:
        self.assert_route(
            "Continue with the previous task.",
            "skill-evolution-router",
            "L1",
            context_route="skill-evolution-router",
        )


if __name__ == "__main__":
    unittest.main()
