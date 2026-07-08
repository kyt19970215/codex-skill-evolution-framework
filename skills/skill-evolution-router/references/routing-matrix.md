# Routing Matrix

## Destinations

- Current prompt only: one-off instructions, temporary output preferences, or task-local constraints.
- Repo `AGENTS.md`: build/test commands, repository conventions, review rules, local verification steps, and path rules for that repo.
- `project-rules-router`: project work entry and project-skill discovery only; avoid putting detailed domain rules here.
- `codex-capability-router`: reusable routing from task intent to installed Codex skills, plugins, apps, MCP tools, and safe candidate plugin suggestions.
- `skill-evolution-core`: how to create, update, split, merge, validate, relax, prune, degrade, and keep skills lean.
- `skill-evolution-router`: where rules, lessons, source priorities, trigger candidates, passive trigger candidates, devolution candidates, and failure shields should live.
- `coding-debug-rules`: shell, encoding, quoting, paths, local scripts, generated files, dependencies, build/test failures, and debugging guardrails that apply across projects.
- `research-verification`: public source quality, current-version checks, APIs, dependencies, install/upgrade behavior, stale docs, exact public errors, and forum/source reliability.
- Project skill such as `example-project`: project terms, source priorities, project paths, local commands, architecture choices, domain-specific known issues, and project-specific examples.
- Global guidance: always-on answer style, caution level, language preference, and broad personal working defaults.
- Installed upstream skill: source of truth for a mature heavy workflow; keep local trigger, precedence, and safety adapters in `codex-capability-router` instead of copying its body.
- `skill-evolution-core`: also owns the capability-absorption workflow reached through the locally configured absorption shortcut; it installs and integrates a selected capability, closes global dependencies, audits overlap, absorbs light rules, and routes heavy workflows.
- `skill-evolution-core`: also owns devolution for bloated, duplicated, stale, over-narrow, or progress-blocking rules.

## Decision Order

1. If the rule is one-off, do not persist it.
2. Determine scope from what the rule depends on, not only where it was discovered.
3. If it is repo-specific, prefer repo `AGENTS.md`.
4. If it names a project/domain but contains a project-agnostic guardrail, promote the guardrail to the relevant global type skill and retain only project facts or exceptions locally.
5. If it applies across projects but only to a task type, prefer the relevant global type skill.
6. If it is about selecting, discovering, recommending, or safely suggesting Codex plugins/skills/apps/MCP capabilities, prefer `codex-capability-router`.
7. If it is about skills themselves, use `skill-evolution-core` or `skill-evolution-router`.
   - If it is about weakening, pruning, relaxing, merging, downgrading, archiving, or removing rules, run the devolution workflow in `skill-evolution-core/references/devolution.md`.
8. If it should affect every conversation, consider global guidance.
9. If it is a global runtime/dependency-closure authorization or external-action boundary, keep the authoritative rule in global guidance and only point to it from specialized skills.

## Project-To-Global Promotion Check

Promote when all applicable checks pass:

- The rule still makes sense after removing the project name, path, local command, and domain example.
- The destination global skill has a matching task trigger and ownership boundary.
- The rule is evidence-backed or is an explicit user preference, not an unsupported inference.
- Promotion reduces duplication without losing a project-specific exception.

Keep local when any essential condition is project-only. Split the rule when only part is reusable.

## Trigger Candidate Handling

- If a phrase appears during a run invoked by the configured evolution shortcut, record it as a trigger candidate only when the intended destination is clear.
- Three matching occurrences can promote the phrase to a trigger rule.
- Count only same-intent and same-destination occurrences; do not count identical words used for different tasks.
- Promote narrow triggers before broad ones.

## Passive Trigger Handling

- Passive trigger candidates start at observation levels L0-L2.
- Use `skill-evolution-core/references/passive-trigger-observation.md` before promoting any passive candidate.
- Scripts may suggest routes and count evidence, but AI remains the decision-maker until an L3 promotion is explicitly approved.
- Never let passive triggers automatically edit files, install tools, commit, push, publish, or perform account actions.

## Devolution Candidate Handling

- Treat rule-maintenance requests as explicit requests to reduce bloat or over-narrowing, not as ordinary memory saving.
- Use `skill-evolution-core/references/rule-lifecycle.md` to decide whether a rule is Candidate, Observe, Active-soft, Active-hard, Scoped, Example-only, Devolution-review, Archived, or Removed.
- Update `skill-evolution-core/references/devolution-ledger.md` when a rule is promoted, enters devolution review, blocks progress, is relaxed, scoped, merged, downgraded, archived, or removed.
- Prefer relaxing, scoping, merging, or downgrading before deleting.
- Never silently weaken hard safety rules for destructive actions, external publishing, accounts, payments, credentials, security, legal/compliance, or private data.

## Verification Flags

Require current verification when the rule involves:

- public tools, APIs, dependencies, versions, browser/driver behavior, or OS behavior
- exact error messages
- install or upgrade behavior
- security, anti-cheat, account risk, or compliance
- forum-derived, old, or memory-derived claims
