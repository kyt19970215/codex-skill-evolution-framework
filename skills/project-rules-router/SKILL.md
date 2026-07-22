---
name: project-rules-router
description: Global router for project-specific Codex rules and capability selection. Use when starting or continuing non-trivial work in a repo, workspace, named project, game, product, plugin, dependency, or research domain; when the user asks to apply project-specific preferences, source priorities, debugging habits, AGENTS.md rules, memories, local notes, reusable project skills, plugin/skill routing, Codex capability selection, error self-checks, or failure-learning rules; or when a task should be routed to a project skill such as example-project, example-research, or another per-project rule package.
---

# Project Rules Router

After active system, developer, user, and global authorization/privacy/safety
constraints have been applied, use this skill as the first project-specific
routing pass. It does not replace local evidence, user instructions, or external
verification; it decides which project-specific rules should be consulted and
how strongly to trust them.

## Rule Authority And Conflict Resolution

- Apply higher-level instructions and global personal hard boundaries before selecting project guidance.
- Use this router to select the narrowest relevant project skill. The selected project skill and repository `AGENTS.md` may then specialize paths, commands, terminology, implementation details, project facts, verification, and soft workflow defaults.
- Treat global/project layering as routing and default specificity, not blanket permission for project guidance to override every global rule. Project guidance concretizes an already constrained task; it does not redefine the higher-level authority boundary.
- They must not silently weaken explicit global authorization, privacy, safety, destructive-action, account/payment/publishing, or user-locked personal boundaries.
- For current technical facts, prefer current files, configuration, versions, logs, tests, and explicit user decisions, then mark stale rules for evolution review.
- A genuine project exception to a personal global boundary requires explicit current-user approval plus scope, rationale, one-off or durable status, and review or expiry. Higher system/developer boundaries remain unchanged.

## Routing Workflow

1. Identify project signals before acting:
   - Explicit project names, domains, games, products, plugins, repositories, or paths in the user request.
   - Current workspace name, repo files, package names, config files, logs, `AGENTS.md`, and nearby docs.
   - Available project skills under the user's Codex skills directory.
   - Treat incidentally discovered processes, windows, installed apps, recent files, unrelated diagnostic paths, and historical-memory matches as environment evidence only. They are not project signals unless the user request, workspace, target file, or task object directly links them to the project.

2. Select the most relevant project skill:
   - Prefer a skill explicitly named by the user.
   - Prefer exact or narrow matches before broad ones.
   - Look for names such as `<project>-project`, `<project>-rules`, `<project>-research`, `<project>-debug`, or a project-specific legacy name.
   - If several skills match, read only the most relevant `SKILL.md` files and choose the narrowest applicable one.
   - Do not load unrelated project skills just because they exist.
   - Do not carry project-only authorization boundaries or report language into an unrelated task merely because that project appeared during diagnostics.

3. Add reusable global skills only when the task shape calls for them:
   - Use `codex-capability-router` when the user names an installed capability or the project's dominant artifact/specialist workflow directly matches one. Apply its native-execution gate: exact entrypoint, required references, native tools/modules/templates, justified fallback, and concrete use evidence.
   - Use `coding-debug-rules` for code edits and bug fixes, including root-cause and direct impact-chain review, as well as failing commands, shell/encoding/path issues, build/test failures, local scripts, and unclear technical bugs.
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

6. Keep rule authority separate from technical evidence:
   - Rule application order is active system/developer/user instructions, global personal hard boundaries, the selected project skill, then the nearest repository `AGENTS.md` for concrete repo behavior.
   - Project guidance may specialize only after the global boundary is known. It cannot silently weaken or reverse that boundary.
   - For current technical facts, prefer current local files, configs, logs, exact errors, versions, and reproduction steps; then project-approved references; then current official sources and broader public evidence.
   - Apply capability-router results and reusable global workflows when the task shape requires them without changing the authority order.

   Classify an apparent conflict as `hard boundary`, `specializable default`, or `current technical fact`. Evidence can replace stale facts; it cannot silently waive policy or authorization.

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
