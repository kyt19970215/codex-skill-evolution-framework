# Rule Lifecycle

Use this reference to prevent rules from only accumulating. A rule should have a lifecycle: observe, adopt, promote, relax, downgrade, archive, or remove.

## Lifecycle States

- Candidate: possible rule, not yet durable.
- Observe: useful pattern, but needs more evidence.
- Active-soft: default preference or workflow habit.
- Active-hard: safety or external-side-effect boundary.
- Scoped: valid only for a project, tool, version, file type, or phase.
- Example-only: historical lesson, not a future constraint.
- Devolution-review: may be too narrow, stale, duplicated, or blocking progress.
- Archived: retained for history, not applied.
- Removed: deleted because it is harmful, obsolete, duplicated, or superseded.

## Promotion Rules

- One unclear failure: keep as Candidate or Example-only; do not make it Active-hard.
- One clear failure with known root cause: create a scoped soft rule or failure shield.
- Repeated across three similar contexts: eligible for Active-soft or broader scoped rule.
- Safety, privacy, destructive action, account, payment, credential, security, legal, or compliance boundaries may become Active-hard from one clear user boundary or verified high-risk failure.
- If a rule depends on public tools, versions, APIs, or exact errors, mark it verification-required instead of treating it as timeless.

## Devolution Triggers

Move a rule to Devolution-review when any of these happen:

- It blocks reasonable progress three times.
- It causes repeated unnecessary confirmation for low-risk work.
- It conflicts with the current large-project goal without a safety reason.
- It duplicates another rule in the same or broader skill.
- It grew from one unclear failure and later proves too narrow.
- It has not been useful for about 30 days and is not safety-critical.
- It depends on old versions, old tools, stale sources, or a resolved condition.
- It makes trigger descriptions broad enough to activate unrelated skills.

## Devolution Actions

- Relax: change "must/always/never" into "default/prefer unless...".
- Scope: move it to project skill, repo `AGENTS.md`, tool-specific reference, or version-specific note.
- Merge: replace several narrow rules with one broader principle.
- Downgrade: move it to Example-only, known issue, failure-learning note, or reference.
- Archive: keep for history but stop applying it.
- Remove: delete only when duplicated, harmful, obsolete, superseded, or clearly wrong.

## Retention Rules

- Hard safety rules do not expire automatically.
- Soft rules should justify their context cost.
- Example-only rules should not live in `SKILL.md` if a reference file can hold them.
- If the user explicitly says a preference still matters, keep it but scope it clearly.
- If deletion would lose useful history, archive or downgrade instead.

## Ledger Rules

Update `devolution-ledger.md` when:

- a rule is promoted from Candidate or Observe to Active-soft or Active-hard
- a rule enters Devolution-review
- a rule is relaxed, scoped, merged, downgraded, archived, or removed
- a rule blocks a large project

Use sanitized summaries. Do not store secrets, private logs, full transcripts, account details, or sensitive project content.
