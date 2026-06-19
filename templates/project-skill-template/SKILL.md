---
name: example-project
description: Template project skill for a named project or repo. Rename this folder and frontmatter before use. Use for project-specific source priorities, local paths, commands, domain terms, decisions, known issues, semantic rule capture, and failure-learning entries that should not live in global skills.
---

# Example Project

Use this skill as the project rule layer for a named project. Replace placeholders before using it for real work.

## First Steps

1. Treat the current user request and current local files as the source of truth.
2. Read `references/project-rules.md` before making non-trivial project decisions.
3. Read `references/local-map.md` when you need paths, script names, generated outputs, or stable local commands.
4. Read `references/sources.md` before broad public research.
5. Read `references/known-issues.md` when a failure looks project-specific or when the user asks to save a project lesson.
6. When the user gives a clear project-scoped durable rule marker, capture the rule into the narrowest project reference instead of requiring the user to say "add this to skill" every time.

## Collaboration Rules

- Use the user's preferred language unless project policy says otherwise.
- Lead with conclusion, then evidence, risk, and next step.
- Avoid presenting inference as fact.
- For new scripts, reports, previews, or output artifacts, include local links in the final answer when appropriate.

## Project Rule Capture

- Put project website/source/search-order preferences in `references/sources.md`.
- Put project workflow, communication, safety, architecture, and verification standards in `references/project-rules.md`.
- Put stable local commands, paths, generated outputs, and repo map details in `references/local-map.md`.
- Put recurring project-specific failures in `references/known-issues.md`.
- Put durable architecture decisions in `references/decisions.md`.
- If the user says only "add a rule" after a project instruction, look back at the immediately preceding user message and extract the durable project rule.

## References

- `references/project-rules.md`: durable project requirements and workflow rules.
- `references/local-map.md`: stable paths, commands, outputs, and local structure.
- `references/sources.md`: project-specific source priority and research rules.
- `references/known-issues.md`: recurring project-specific symptoms, root causes, guardrails, and verified fixes.
- `references/decisions.md`: durable project decisions and evidence.
