---
name: skill-evolution-core
description: Overall workflow for evolving and absorbing Codex skills. Use when the user asks to create, update, refactor, split, merge, validate, improve, or absorb skills; convert repeated mistakes into durable failure shields; consolidate project rules; design a personal skill system; learn personal trigger words; decide where knowledge belongs; when the user types "进化" as a forced shortcut for total skill evolution; or when the user types "吞噬" to install and integrate a selected Skill, plugin, tool, app, file, or mature capability with global dependency closure, overlap removal, light-rule absorption, heavy-workflow routing, validation, and reporting.
---

# Skill Evolution Core

Use this skill as the high-level workflow for improving the user's Codex skill system. Keep it focused on how skills evolve; use `skill-evolution-router` to classify where each rule or lesson belongs.

## Forced Shortcuts

- When the user enters `进化` at the end of a conversation or after a task, run the total skill-evolution workflow. Review the preceding conversation for durable rules, repeated failures, semantic capture markers, and skill-routing updates before editing any skill.
- When the user enters `吞噬`, run the complete capability-absorption workflow in `references/capability-absorption.md`. Look back at the immediately preceding context to identify the target; if clear, do not ask the user to repeat it.

Run the trigger-learning pass in `references/trigger-learning.md` before promoting new trigger words. Record only sanitized evidence in `references/trigger-candidates.md`.

## Core Workflow

1. Identify the evolution request:
   - new skill
   - update existing skill
   - split or merge skills
   - promote a lesson from a task
   - reduce bloat or duplication
   - validate trigger behavior
   - forced `进化` shortcut from the end of a conversation
   - forced `吞噬` shortcut for capability ingestion
   - repeated personal usage pattern that may deserve a new trigger word

2. Collect the minimum evidence:
   - exact user rule or durable preference
   - failure symptom and verified root cause, if any
   - near-miss symptom or anomalous output that was dismissed as harmless
   - affected skill paths
   - whether the rule is global, type-specific, or project-specific
   - repeated trigger words, user phrasing, and chosen routing outcome
   - whether the rule is about capability discovery, installed plugin/skill routing, candidate plugin suggestions, or actual skill evolution
   - current `SKILL.md`, relevant references, and `agents/openai.yaml`

3. Route before editing:
   - Use `skill-evolution-router` for destination and scope.
   - Prefer the narrowest durable home.
   - Split general guardrails from project-specific examples.
   - When an upstream skill overlaps existing rules, use `references/capability-absorption.md` to choose absorption, delegation, or replacement before copying anything.

4. Edit with progressive disclosure:
   - Keep `SKILL.md` small and trigger-focused.
   - Put detailed matrices, examples, failure shields, source lists, and project maps in `references/`.
   - Put deterministic repeated code in `scripts/`.
   - Avoid README, changelog, installation guide, or other nonessential files inside skills.

5. Validate:
   - Run the skill validator after creating or structurally editing a skill.
   - Inspect generated `agents/openai.yaml` for stale display text.
   - Check for placeholder text, duplicated rules, mojibake, near-miss coverage, and trigger descriptions that are too broad.

6. Report succinctly:
   - Say which skill files changed.
   - State the classification decision.
   - Note verification and any residual uncertainty.

## Architecture Rules

- Use one small forced entry point when the user wants reliability, then route to narrower skills.
- Put reusable installed-plugin, installed-skill, app, MCP, and candidate-plugin selection logic in `codex-capability-router`; this skill should only manage how that routing skill evolves.
- Do not build a giant all-purpose `SKILL.md`; it will be fully loaded whenever selected.
- Use references to approximate "load only the needed part" within a skill.
- Use separate skills when trigger conditions differ meaningfully.
- Put always-on personal behavior in global guidance or AGENTS.md, not in a rarely triggered skill.
- Keep mature third-party workflows independently updateable. Absorb only compact, durable principles; route heavy execution through `codex-capability-router`.

## References

- `references/evolution-principles.md`: design rules for skill growth.
- `references/quality-gate.md`: checks before considering a skill update finished.
- `references/trigger-learning.md`: learn personal trigger words from repeated forced evolution runs.
- `references/trigger-candidates.md`: sanitized counter ledger for candidate trigger words.
- `references/capability-absorption.md`: deduplicate upstream skills and route mature heavy workflows.
