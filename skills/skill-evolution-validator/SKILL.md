---
name: skill-evolution-validator
description: Audit an evolution skill system for structure, routing behavior, ledger alignment, privacy, and platform freshness. Use only for explicit health, cleanliness, regression, ledger, or release-readiness checks; do not use for routine edits or configured shortcuts.
---

# Skill Evolution Validator

Use this skill for manual, report-first checks of the installed evolution framework. It gathers evidence and reports risks; it does not edit other skills unless the user separately requests a repair.

## Trigger Boundary

Use this skill when the user explicitly asks for an evolution-system:

- self-check, health check, cleanliness check, or audit
- trigger or routing behavior regression
- local-ledger comparison
- platform freshness review
- release or GitHub readiness report

Do not trigger it for routine skill edits, configured evolution shortcuts, configured absorption shortcuts, or ordinary rule-maintenance requests. Those belong to `skill-evolution-core` and `skill-evolution-router`.

## Modes

- `auto`: run `full` when no previous report or snapshot exists; otherwise run log-based `fast` mode.
- `full`: run structure, semantics, behavior regression, event evidence, ledger reconciliation, and platform freshness.
- `fast`: compare current files with the previous snapshot and summarize existing event evidence. It must say that behavior regression was not run.

Run:

```text
python scripts/validate_evolution_skills.py --mode auto
```

Use `--mode full` before public release or after routing behavior changes.

## Required Output

Every run writes Markdown, JSON, and a reusable snapshot under the local report directory. The report must distinguish real Hook observations from smoke-test evidence, list unlabeled route outcomes, show files not represented by the latest local ledger entry, and state whether the official platform review is stale.

## References

- `references/check-matrix.md`: mode-specific checks and boundaries.
- `references/report-schema.md`: report fields and wording requirements.
- `references/ledger-reconciliation.md`: local change-log format and matching rules.
- `references/devolution-self-check-boundary.md`: validator versus rule-maintenance ownership.
- `references/regression-cases.md`: human-readable behavior expectations.
- `references/regression-cases.json`: executable behavior cases.
- `references/severity-levels.md`: finding severity definitions.
- `references/platform-freshness.json`: official-source review timestamp.
