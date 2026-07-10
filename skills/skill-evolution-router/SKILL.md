---
name: skill-evolution-router
description: Classify durable rules, reusable lessons, failure shields, trigger candidates, and project-to-global promotions before editing. Use for rule-placement and scope decisions; do not own configured shortcut execution or evolution-system audits.
---

# Skill Evolution Router

Use this skill to decide where durable knowledge belongs before editing any skill. It classifies; `skill-evolution-core` manages the overall update workflow.

If the request is about the evolution system's health, cleanliness, behavior regression, local ledger, freshness, or release readiness rather than rule placement, route it to `skill-evolution-validator` instead.

## Routing Workflow

1. Extract the candidate rule:
   - user preference
   - project convention
   - source priority
   - debugging guardrail
   - failure lesson
   - personal trigger candidate
   - passive trigger observation candidate
   - skill architecture decision
   - devolution candidate: a rule that may need pruning, relaxation, merging, scoping, or downgrading

2. Determine scope:
   - one-off task
   - current repo
   - named project or domain
   - global reusable workflow
   - always-on personal preference

   Treat the rule's origin as evidence, not as its destination. A rule first learned in one project may still belong in a global type skill when its reusable core is project-agnostic.

3. Choose the destination using `references/routing-matrix.md`.

4. If the user used a strong capture marker, use `references/semantic-rule-capture.md`.

5. If the rule comes from repeated use of the configured evolution shortcut, use `skill-evolution-core/references/trigger-learning.md` before promotion.

6. If the rule may be over-narrow, bloated, stale, duplicated, or blocking progress, use `skill-evolution-core/references/devolution.md` before editing.

7. If the candidate is a passive trigger, keep it at observation level unless `skill-evolution-core/references/passive-trigger-observation.md` promotion gates are satisfied.

8. Edit only the narrowest durable home:
   - global type skill for reusable process
   - project skill for project facts and project-specific habits
   - project `AGENTS.md` for repo commands and repo conventions
   - global guidance only for always-on behavior

9. Keep the entry compact:
   - rule
   - scope
   - evidence or rationale
   - verification requirement when the rule depends on current tools, APIs, versions, or environment

## Split Mixed Lessons

When a lesson contains both reusable process and project facts, split it:

- Put the general guardrail in the relevant global skill.
- Put the project example, path, source, or exception in the project skill.
- Link by wording only when necessary; avoid duplicating long explanations.

## Promote Project Rules

Audit a project rule for global promotion when its behavior could recur across unrelated projects.

- Promote the reusable core when it does not depend on project paths, commands, domain facts, private data, or project-only architecture.
- Keep project examples, paths, source priorities, exceptions, and local verification steps in the project skill or repo `AGENTS.md`.
- Replace duplicated project wording with a short project-specific exception or pointer after promotion.
- Repeated occurrence across projects increases confidence but is not mandatory when the rule is intrinsically project-agnostic and supported by clear evidence.
- If broader wording would change meaning, create false triggers, or rely on uncertain technical claims, leave it project-local and record it as a promotion candidate.

## References

- `references/routing-matrix.md`: destination map.
- `references/semantic-rule-capture.md`: strong user markers and capture rules.
