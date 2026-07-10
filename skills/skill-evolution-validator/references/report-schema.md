# Report Schema

Every report contains:

- run id, selected mode, and mode basis
- overall status and findings by severity
- static structure results
- behavior-regression pass/fail counts or an explicit `not_run` state
- real Hook event count, smoke-test count, labels, and recency-weighted route summaries
- changed files and latest-ledger unmatched files
- platform freshness date, age, and official sources
- Markdown report, JSON report, and snapshot paths
- whether the trusted snapshot was updated and the path to the last-run status record

Generated reports are local artifacts and must not be committed to the public framework.
