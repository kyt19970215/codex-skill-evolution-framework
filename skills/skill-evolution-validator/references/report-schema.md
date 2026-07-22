# Report Schema

Every report contains:

- run id, selected mode, and mode basis
- overall status and findings by severity
- static structure results
- behavior-regression pass/fail counts or an explicit `not_run` state
- real Hook event count, smoke-test count, labels, and recency-weighted route summaries
- Hook enabled state, definition/wrapper health, and local trust evidence
- changed files and latest-ledger unmatched files
- rule-authority status, checked global/project files, conflict details, and the effective global-guidance byte budget
- installed/public framework drift with private local files excluded
- repair authorization, handoff owner, and confirmation that the validator did not edit files
- platform freshness date, age, and official sources
- Markdown report, JSON report, latest snapshot, and timestamped snapshot-history paths
- whether the trusted snapshot was updated and the path to the last-run status record

Generated reports are local artifacts and must not be committed to the public framework.
