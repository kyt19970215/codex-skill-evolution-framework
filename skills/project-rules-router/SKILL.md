---
name: project-rules-router
description: Global router for project-specific Codex rules and capability selection. Use when starting or continuing non-trivial work in a repo, workspace, named project, game, product, plugin, dependency, or research domain; when the user asks to apply project-specific preferences, source priorities, debugging habits, AGENTS.md rules, memories, local notes, reusable project skills, plugin/skill routing, Codex capability selection, error self-checks, or failure-learning rules; or when a task should be routed to a project skill such as example-project, example-research, or another per-project rule package.
---

# Project Rules Router

Use this skill as a first-pass router for project work. It does not replace local evidence, user instructions, or external verification; it decides which project-specific rules should be consulted and how strongly to trust them.

## Routing Workflow

1. Identify project signals before acting:
   - Explicit project names, domains, games, products, plugins, repositories, or paths in the user request.
   - Current workspace name, repo files, package names, config files, logs, `AGENTS.md`, and nearby docs.
   - Available project skills under the user's Codex skills directory.

2. Select the most relevant project skill:
   - Prefer a skill explicitly named by the user.
   - Prefer exact or narrow matches before broad ones.
   - Look for names such as `<project>-project`, `<project>-rules`, `<project>-research`, `<project>-debug`, or a project-specific legacy name.
   - If several skills match, read only the most relevant `SKILL.md` files and choose the narrowest applicable one.
   - Do not load unrelated project skills just because they exist.

3. Add reusable global skills only when the task shape calls for them:
   - Use `codex-capability-router` when an installed Codex plugin, plugin-provided skill, app, MCP tool, or candidate plugin may materially improve the task, especially for design, business analysis, documents, spreadsheets, presentations, PDFs, GitHub, browser/computer use, sites, role-specific workflows, or plugin discovery.
   - Use `coding-debug-rules` for code edits, failing commands, shell/encoding/path issues, build/test failures, local scripts, and unclear technical bugs.
   - Use `research-verification` for public tools, APIs, dependencies, install/upgrade behavior, version compatibility, exact public error messages, security/anti-cheat claims, or stale/current claims.
   - Use `skill-evolution-router` when the user asks to save, remember, classify, add, split, or route a reusable rule or lesson.
   - Use `skill-evolution-core` when actually creating, updating, splitting, merging, or validating skills.
   - Project skills stay responsible for project-specific facts; global skills provide reusable process.

4. Route failure-learning requests before editing any skill:
   - Use `skill-evolution-router` to classify the lesson's destination before editing.
   - Put project-agnostic shell, encoding, path, quoting, script, local tool, dependency, build, test, or generated-file lessons in `coding-debug-rules`.
   - Put public-source, API, version compatibility, dependency release, browser/driver, install/upgrade, stale-doc, or exact-public-error lessons in `research-verification`.
   - Put repo paths, project commands, domain terms, architecture decisions, project-specific known issues, and local artifact rules in the narrow project skill.
   - If a lesson is mixed, store the general guardrail in the global type skill and only the project-specific example or exception in the project skill.

5. Route semantic rule-capture requests:
   - Use `skill-evolution-router` when the user gives durable-rule markers such as future/default/must/prefer/remember/save/add-rule wording.
   - Treat "add a rule" style requests as permission to look back at the immediate prior user instruction and extract the durable rule, even if the user does not restate it.
   - Route the extracted rule to the narrowest global type skill or project skill.

6. Apply evidence in this order:
   - Current user request and active system/developer/project instructions.
   - Current local evidence: files, configs, logs, exact errors, versions, and reproduction steps.
   - The selected project skill and its references.
   - The selected capability router result, when plugin/skill/app routing is relevant.
   - Reusable global skill workflow, if applicable.
   - Project-preferred public sources.
   - Broader public sources such as official docs, release notes, GitHub issues, maintainer replies, forums, and search results.

7. Treat project skills as priority guides, not hard boundaries:
   - A preferred source list means "check these first", not "only use these".
   - A historical project note is a hypothesis until current local evidence or current public sources confirm it.
   - Version, API, dependency, plugin, operating system, and error-behavior claims must be rechecked against the current environment.

8. If no project skill exists:
   - Continue from current local evidence and active instructions.
   - Use general best practices for the task.
   - Mention that no project-specific skill was found only when it affects confidence or when the user is intentionally building the project rule system.

## Maintenance Rules

- Do not create or update a project skill unless the user asks.
- When a task reveals durable, reusable project knowledge, suggest promoting it into that project's skill after finishing the immediate work.
- When an existing project rule contains a project-agnostic workflow or guardrail, use `skill-evolution-router` to promote the reusable core into the matching global type skill while keeping project facts and exceptions local.
- When the user asks to save, remember, classify, or add a failure lesson, use `skill-evolution-router` first, then edit the selected skill directly and keep the entry concise.
- When the user gives a clear durable rule marker and the scope is clear, treat it as an implicit request to update the relevant skill.
- When the user did not ask for a durable update, present a candidate failure rule instead of silently changing skills.
- Before adding any failure or semantic rule, write a one-paragraph self-check that separates symptom/request, root cause or durable intent, scope, evidence, and verification.
- Keep global rules small. Put project-specific details in project skills.
- Keep reusable plugin/skill/app routing rules in `codex-capability-router`; keep only project-specific capability preferences in the project skill.
- Keep secrets, credentials, private tokens, and sensitive account data out of skills.
- Prefer concise, evidence-backed project notes over broad summaries.

## Project Skill Contract

When creating or updating a project skill that should work with this router, follow `references/project-skill-contract.md`. For implicit rule capture, use `skill-evolution-router`.
