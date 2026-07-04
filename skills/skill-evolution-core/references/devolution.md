# Devolution Workflow

Devolution is controlled rule maintenance: prune, relax, merge, downgrade, archive, or remove rules that became too narrow, too numerous, contradictory, stale, or blocking.

Use `rule-lifecycle.md` for promotion and devolution thresholds. Use `devolution-ledger.md` to record concise sanitized outcomes when rule behavior changes.

## When To Run

Run this workflow when:

- the user asks to relax, prune, degrade, downgrade, archive, merge, or remove rules
- a project is stalling because too many small rules are being applied
- rules keep narrowing after each failure
- a skill is bloated, repetitive, or hard to route
- old project-specific guidance is being treated like a global rule
- a rule prevents reasonable progress without a safety reason

## Safety Boundary

Do not automatically weaken hard safety boundaries:

- deletion, overwrite, reset, publish, deploy, commit, push, or merge
- payment, account, login, cookie, credential, or private data
- security, legal, compliance, or other high-impact external effects

For these areas, devolution may clarify scope or reduce duplicate wording, but it must not weaken the protection without explicit user direction.

## Rule Classes

Classify each candidate rule before editing:

- Hard rule: safety, external side effect, privacy, or destructive action. Keep strict unless the user explicitly changes the boundary.
- Soft rule: preference, workflow habit, style, or usual order. May be relaxed by current goal or project phase.
- Scoped rule: valid only for a project, tool, version, file type, or situation. Move to the narrowest home.
- Example rule: useful history but not a future constraint. Move to examples, known issues, or archived wording.
- Stale rule: depended on old versions, old tools, or a resolved condition. Mark stale or remove after verification.

## Devolution Pass

1. Identify the target:
   - explicitly named skill or rule
   - latest rules added by recent evolution work
   - the skill blocking the current project
   - if unclear, inspect the most likely skill and report uncertainty

2. Check lifecycle state:
   - Read `rule-lifecycle.md`.
   - Classify the target as Candidate, Observe, Active-soft, Active-hard, Scoped, Example-only, Devolution-review, Archived, or Removed.
   - If the rule is safety-critical, keep it hard unless the user explicitly changes the boundary.

3. Find narrowing symptoms:
   - repeated "must", "always", or "never" wording from one-off failures
   - project-specific details inside global skills
   - duplicate rules in several files
   - rules that require confirmation for ordinary low-risk work
   - examples written as universal commands
   - long `SKILL.md` bodies that should be references
   - trigger descriptions broad enough to fire on unrelated tasks

4. Apply lifecycle thresholds:
   - One unclear failure: keep as Candidate or Example-only; do not make it a hard rule.
   - Three similar useful occurrences: eligible for Active-soft promotion.
   - Three progress blocks: move to Devolution-review.
   - About 30 days unused: consider downgrade if not safety-critical.
   - About 90 days stale or superseded: consider archive or removal after verification.

5. Decide an action for each rule:
   - Keep: still broad, useful, and not blocking.
   - Relax: convert "must/always" to "default/prefer unless...".
   - Scope: move global wording to project skill or repo `AGENTS.md`.
   - Merge: replace several similar rules with one broader principle.
   - Downgrade: move from hard workflow to reference, example, or known issue.
   - Archive/remove: delete only when obsolete, duplicated, or harmful and not safety-critical.

6. Preserve intent:
   - Keep the original problem the rule was trying to prevent.
   - Replace brittle special cases with the smallest broad guardrail.
   - If removing a rule would reintroduce a real failure, keep a narrower safety note.

7. Update the ledger:
   - Add or update a short entry in `devolution-ledger.md`.
   - Include date, rule/file, current state, signal, impact, decision, and next review.
   - Keep entries sanitized; do not store private logs, secrets, account details, or long transcripts.

8. Validate:
   - Run skill validation after structural edits.
   - Check that trigger descriptions are not overbroad.
   - Check that no private project details were moved into public skills.
   - State what became stricter, looser, merged, moved, archived, or removed.

## Anti-Narrowing Check Before Adding Rules

Before adding a new durable rule, ask:

- Did this happen once, or repeat across contexts?
- Is the root cause known, or only suspected?
- Can the rule be phrased as a broad principle instead of a patch?
- What valid future task would this rule accidentally block?
- Should it be a soft preference, scoped project rule, example, or hard rule?
- Does it belong in a reference file instead of `SKILL.md`?

If the answer is unclear, record it as a candidate or example instead of a hard rule.

## Large Project Progress Override

For long-running projects, do not let minor soft rules override the main objective. Apply this order:

1. Preserve safety and user boundaries.
2. Preserve the current project goal.
3. Use current local evidence.
4. Apply project-specific rules.
5. Apply soft global preferences.
6. Treat stale or example-only rules as references, not blockers.

When a soft rule conflicts with progress, mention the conflict briefly, choose the path that serves the project goal, and record a devolution candidate if the same conflict repeats.
