---
name: skill-evolution-router
description: Classification and routing workflow for reusable Codex rules, lessons, failure shields, source priorities, trigger-word learning, and project knowledge. Use when the user asks to save, remember, add, classify, split, promote, or organize a rule; when they mention skill evolution, "进化", global vs project rules, reusable lessons, failure learning, semantic rule capture, personal trigger words, or where a piece of knowledge should live; or before editing skills from a newly discovered durable lesson.
---

# Skill Evolution Router

Use this skill to decide where durable knowledge belongs before editing any skill. It classifies; `skill-evolution-core` manages the overall update workflow.

## Routing Workflow

1. Extract the candidate rule:
   - user preference
   - project convention
   - source priority
   - debugging guardrail
   - failure lesson
   - personal trigger candidate
   - skill architecture decision

2. Determine scope:
   - one-off task
   - current repo
   - named project or domain
   - global reusable workflow
   - always-on personal preference

   Treat the rule's origin as evidence, not as its destination. A rule first learned in one project may still belong in a global type skill when its reusable core is project-agnostic.

3. Choose the destination using `references/routing-matrix.md`.

4. If the user used a strong capture marker, use `references/semantic-rule-capture.md`.

5. If the rule comes from repeated forced `进化` usage, use `skill-evolution-core/references/trigger-learning.md` before promotion.

6. Edit only the narrowest durable home:
   - global type skill for reusable process
   - project skill for project facts and project-specific habits
   - project `AGENTS.md` for repo commands and repo conventions
   - global guidance only for always-on behavior

7. Keep the entry compact:
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
