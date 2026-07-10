---
name: skill-evolution-core
description: Evolve, absorb, relax, split, merge, or maintain Codex skills and durable failure shields. Use for explicit skill-system changes or configured shortcuts. Route health, regression, ledger, freshness, and release audits to skill-evolution-validator.
---

# Skill Evolution Core

Use this skill as the high-level workflow for improving the user's Codex skill system. Keep it focused on how skills evolve; use `skill-evolution-router` to classify where each rule or lesson belongs.

## Configured Shortcuts

- When the local entry routes the configured evolution shortcut at the end of a conversation or after a task, classify the evolution load level using `references/evolution-load-levels.md`. Default to a light pass for one clear failure shield or one target-skill patch; escalate only when routing, ownership, multi-skill impact, absorption, devolution, or architecture changes require it.
- When the local entry routes the configured absorption shortcut, run the complete capability-absorption workflow in `references/capability-absorption.md`. Look back at the immediately preceding context to identify the target; if clear, do not ask the user to repeat it.
- When the user asks to relax, prune, merge, downgrade, archive, or remove bloated or over-narrow rules, run the devolution workflow in `references/devolution.md`.
- When the user asks to audit evolution-system health, cleanliness, behavior regression, local-ledger alignment, freshness, or release readiness, route to `skill-evolution-validator`. Do not run that audit for every routine evolution or absorption request.

Run the trigger-learning pass in `references/trigger-learning.md` before promoting new trigger words. Record only sanitized evidence in `references/trigger-candidates.md`.

For passive semantic trigger observation, use `references/passive-trigger-observation.md`, `scripts/passive_trigger_probe.py`, and `scripts/trigger_event_tools.py`. The optional `UserPromptSubmit` Hook may record anonymous local evidence and add one advisory route hint. It must not automatically run skills, change files, or execute workflows.

## Core Workflow

1. Identify the evolution request:
   - new skill
   - update existing skill
   - split or merge skills
   - promote a lesson from a task
   - reduce bloat or duplication
   - validate trigger behavior
   - explicit manual evolution-system audit, which belongs to `skill-evolution-validator`
   - configured evolution shortcut from the end of a conversation
   - configured absorption shortcut for capability ingestion
   - devolution or rule-maintenance request
   - passive semantic trigger observation or trigger-event counting
   - evolution load level: light, standard, or full
   - repeated personal usage pattern that may deserve a new trigger word

2. Collect the minimum evidence:
   - exact user rule or durable preference
   - failure symptom and verified root cause, if any
   - near-miss symptom or anomalous output that was dismissed as harmless
   - affected skill paths
   - whether the rule is global, type-specific, or project-specific
   - whether the rule is hard safety, soft preference, scoped guidance, or only a historical example
   - current lifecycle state when relaxing, promoting, or degrading a rule
   - repeated trigger words, user phrasing, and chosen routing outcome
   - whether the rule is about capability discovery, installed plugin/skill routing, candidate plugin suggestions, or actual skill evolution
   - current `SKILL.md`, relevant references, and `agents/openai.yaml`

3. Route before editing:
   - Use `skill-evolution-router` for destination and scope.
   - Use `references/evolution-load-levels.md` to keep the current evolution run proportional.
   - Prefer the narrowest durable home.
   - Split general guardrails from project-specific examples.
   - If a new lesson overlaps existing guidance, update the existing owner text instead of appending a parallel section.
   - When an upstream skill overlaps existing rules, use `references/capability-absorption.md` to choose absorption, delegation, or replacement before copying anything.
   - Before adding narrow hard constraints, run the anti-narrowing check in `references/devolution.md`.
   - For lifecycle thresholds, use `references/rule-lifecycle.md`.

4. Edit with progressive disclosure:
   - Keep `SKILL.md` small and trigger-focused.
   - Put detailed matrices, examples, failure shields, source lists, and project maps in `references/`.
   - Put deterministic repeated code in `scripts/`.
   - Avoid README, changelog, installation guide, or other nonessential files inside skills.
   - Preserve specification neatness: merge duplicate or overlapping rules into their original owner text, remove superseded duplicates, and create a new heading only when the rule has a distinct trigger, owner, or lifecycle.
   - For devolution, prefer relaxing, scoping, merging, or downgrading a rule before deleting it outright.
   - Record devolution decisions in `references/devolution-ledger.md` when a rule is promoted, relaxed, scoped, downgraded, archived, or removed.
   - Append durable local skill changes to `references/evolution-change-log.md`. Keep prompts, private paths, account data, and project secrets out of the log.

5. Validate:
   - Run structural validation after creating or structurally editing a skill.
   - Use `skill-evolution-validator` only when the user asks for a manual audit, behavior regression, ledger comparison, freshness review, or release-readiness report.
   - Inspect generated `agents/openai.yaml` for stale display text.
   - Check for placeholder text, duplicated rules, conflicting guidance, mojibake, near-miss coverage, and trigger descriptions that are too broad.
   - If a rule was relaxed, downgraded, scoped, split into trigger levels, or made conditional, verify that the final semantics and execution effect are unchanged unless the user explicitly approved the behavior change.
   - When a validator report contains an authorized repair handoff, route the finding through `skill-evolution-router`, apply the smallest durable fix, update local ledgers, and rerun full validation. The validator remains report-only and does not own file edits.

6. Report succinctly:
   - Say which skill files changed.
   - State the classification decision.
   - Note verification and any residual uncertainty.

## Architecture Rules

- Use one small local entry point for configured shortcuts, then route to narrower skills.
- Put reusable installed-plugin, installed-skill, app, MCP, and candidate-plugin selection logic in `codex-capability-router`; this skill should only manage how that routing skill evolves.
- Do not build a giant all-purpose `SKILL.md`; it will be fully loaded whenever selected.
- Use references to approximate "load only the needed part" within a skill.
- Use separate skills when trigger conditions differ meaningfully.
- Put always-on personal behavior in global guidance or AGENTS.md, not in a rarely triggered skill.
- Keep mature third-party workflows independently updateable. Absorb only compact, durable principles; route heavy execution through `codex-capability-router`.
- Treat absorption as adding and reconciling, not just appending: every absorption pass includes a proportional devolution check for overlap, conflict, and obsolete local wording, but this check must stay lightweight unless the user asked for full rule maintenance.
- Treat devolution as maintenance, not failure: it keeps skills useful by reducing bloat and turning over-specific patches back into scoped guidance.
- Distinguish runtime cost from AI/context cost. Prefer deterministic scripts for passive trigger counting, keyword or semantic-signal matching, recency checks, and compact reports. AI should steer, review exceptions, and approve promotion or devolution; it should not reread long ledgers or deep skill references on every ordinary message.
- Do not promote passive triggers to automatic execution early. Until enough accuracy evidence exists, passive triggers stay in observation levels L0-L2: log, suggest, or request AI review.
- Keep observation AI-led and script-assisted. Recency weights and route suggestions are evidence, not authority.

## References

- `references/evolution-principles.md`: design rules for skill growth.
- `references/quality-gate.md`: checks before considering a skill update finished.
- `references/trigger-learning.md`: learn personal trigger words from repeated forced evolution runs.
- `references/trigger-candidates.md`: sanitized counter ledger for candidate trigger words.
- `references/passive-trigger-observation.md`: observation-first passive semantic trigger levels, accuracy gates, and event-log rules.
- `scripts/trigger_event_tools.py`: label actual route outcomes and build recency-weighted local summaries.
- `references/evolution-load-levels.md`: classify evolution runs into light, standard, or full passes.
- `references/capability-absorption.md`: deduplicate upstream skills and route mature heavy workflows.
- `references/devolution.md`: relax, prune, merge, downgrade, archive, or remove bloated and over-narrow rules.
- `references/rule-lifecycle.md`: lifecycle states and thresholds for promotion, devolution review, downgrade, archive, and removal.
- `references/devolution-ledger.md`: sanitized local ledger for rule lifecycle and devolution decisions.
- `references/evolution-change-log.md`: protected local template for durable skill-system changes.
- `skill-evolution-validator`: separate manual audit and release-readiness workflow.
