# Evolution Principles

## Scope Ladder

Prefer the narrowest durable scope:

1. Current prompt only: one-off constraint.
2. Repo `AGENTS.md`: repository commands, conventions, and verification.
3. Project skill: domain terms, source priorities, local maps, and project-specific failure shields.
4. Global reusable skill: project-agnostic workflows such as debugging, research, documents, or skill maintenance.
5. Global guidance: always-on personal preferences and broad response rules.

The discovery location does not fix the final scope. Audit project rules for a project-agnostic core before leaving them project-local; promote that core to the matching global type skill and retain project facts or exceptions locally.

## Keep Skills Lean

- Frontmatter `description` is for trigger scope; include the key use cases there.
- `SKILL.md` is for the core workflow and navigation.
- `references/` is for details loaded only when needed.
- `scripts/` is for deterministic repeated operations.
- Do not duplicate the same rule across multiple skills unless one entry is only a pointer.

## Split Or Merge

Split skills when:

- Trigger conditions are different.
- The details are large and unrelated.
- Loading one topic every time another topic is used would waste context.
- One area needs its own validation or failure shields.

Merge or keep together when:

- The same trigger always needs the same rules.
- The body is small and cohesive.
- Separation would add routing overhead without saving context.

## Evidence Standard

- Store verified durable rules, not raw transcripts.
- Mark stale, version-specific, forum-derived, or unverified claims.
- For one failure, add a shield only after the root cause is clear.
- For a near-miss, add a shield when the symptom is clear enough to prevent premature dismissal, even if the underlying tool behavior still needs a small local verification step.
- Preserve the user's intended preference, but do not turn uncertain technical claims into facts.

## Near-Miss Capture

- Treat anomalous output, mojibake, truncated text, unexpected path changes, or repeated manual work as capture candidates even when the command exits successfully.
- If a broad existing rule did not trigger, record why: wrong skill selected, trigger text too narrow, failure-learning only covered nonzero exits, or the anomaly was treated as cosmetic.
- Add the smallest executable guardrail to the task-type skill, and keep the skill-evolution entry focused on improving capture behavior.

## Trigger Learning

- Treat repeated forced skill use as evidence that the user's natural language may need a new trigger.
- Count normalized trigger candidates across forced `进化` runs, not raw full prompts.
- Three similar occurrences are enough to propose promotion; automatic promotion is allowed only for low-risk, narrow-scope trigger rules.
- Ask before promoting triggers that affect destructive actions, safety, account risk, external publishing, broad always-on behavior, or unclear project scope.
- Prefer specific trigger patterns over broad keywords that would make skills fire too often.
