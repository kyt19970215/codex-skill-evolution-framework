---
name: skill-evolution-validator
description: Audit an evolution skill system for structure, routing behavior, ledger alignment, privacy, and platform freshness. Use only for explicit health, cleanliness, regression, ledger, or release-readiness checks; do not use for routine edits or configured shortcuts.
---

# Skill Evolution Validator

Use this skill for manual, report-first checks of the installed evolution framework. It gathers evidence and reports risks; it does not edit other skills unless the user separately requests a repair.

When the same request explicitly asks to fix, repair, update, or resolve findings, complete the report first and emit a repair handoff owned by `skill-evolution-core` and `skill-evolution-router`. The validator still does not edit files. The owning workflow applies the authorized change, updates local ledgers, and returns for a full rerun without asking for duplicate approval.

## Trigger Boundary

Use this skill when the user explicitly asks for an evolution-system:

- self-check, health check, cleanliness check, or audit
- trigger or routing behavior regression
- local-ledger comparison
- platform freshness review
- release or GitHub readiness report
- global/project rule-authority review
- installed versus public-framework source comparison

Do not trigger it for routine skill edits, configured evolution shortcuts, configured absorption shortcuts, or ordinary rule-maintenance requests. Those belong to `skill-evolution-core` and `skill-evolution-router`.

## Modes

- `auto`: run `full` when no previous report or snapshot exists; otherwise run log-based `fast` mode.
- `full`: run structure, semantics, behavior regression, event evidence, ledger reconciliation, rule authority, framework-source comparison, and platform freshness.
- `fast`: compare current files with the previous snapshot and summarize existing event evidence. It must say that behavior regression was not run.

Run:

```text
python scripts/validate_evolution_skills.py --mode auto
```

Use `--mode full` before public release or after routing behavior changes.
Use `--project-root` for the active repository, `--framework-root` for a public checkout, and `--repair-authorized` only when the current request already authorizes remediation.

## Required Output

Every run writes Markdown, JSON, a latest snapshot, and timestamped snapshot history under the local report directory. The report must distinguish Hook definition/trust health, real observations, and smoke-test evidence; list unlabeled route outcomes; show files not represented by the latest local ledger entry; report authority conflicts and managed-source drift; and state whether the official platform review is stale.

## References

- `references/check-matrix.md`: mode-specific checks and boundaries.
- `references/report-schema.md`: report fields and wording requirements.
- `references/ledger-reconciliation.md`: local change-log format and matching rules.
- `references/devolution-self-check-boundary.md`: validator versus rule-maintenance ownership.
- `references/regression-cases.md`: human-readable behavior expectations.
- `references/regression-cases.json`: executable behavior cases.
- `references/severity-levels.md`: finding severity definitions.
- `references/platform-freshness.json`: official-source review timestamp.
