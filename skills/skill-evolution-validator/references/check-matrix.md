# Check Matrix

## Fast Mode

- Compare the current file snapshot with the previous snapshot.
- Summarize local trigger events, labels, and recency-weighted route evidence.
- Check platform review age from the existing freshness record.
- Do not claim behavior regression passed when executable cases were not run.
- Do not replace a trusted snapshot after a failed full run or an explicit fast run with changed managed files.
- In `auto` mode, escalate to full validation when managed files changed or the previous run failed.

## Full Mode

- Run all fast checks.
- Validate every managed Skill's frontmatter, `SKILL.md`, and `agents/openai.yaml`.
- Check that core, router, and validator descriptions have distinct ownership.
- Execute every case in `regression-cases.json` against the installed passive probe.
- Compare changed files with the latest local evolution change-log entry.
- Check global guidance, `project-rules-router`, and the active repository `AGENTS.md` for blanket project overrides and missing hard-boundary authority rules.
- When a framework checkout is supplied, compare managed installed files with public source while excluding private ledgers, event logs, and local capability data.
- Report private event data as counts only; do not copy prompt text into reports.
- If the optional Hook is enabled, check the definition, wrapper, local trust record, and real conversation-event count separately.
- Preserve a timestamped snapshot whenever a trusted latest snapshot is updated.

## Hard Boundaries

- The validator is manual and report-first.
- Advisory Hook output never authorizes automatic actions.
- Missing labels are evidence gaps, not successful routes.
- Smoke tests are not real Hook observations.
- The validator stays report-only. An explicit repair request produces a handoff to `skill-evolution-core`; it does not make the validator a silent editor.
