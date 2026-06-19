# Project Skill Contract

Use this reference when creating or updating a per-project skill that should be routed by `project-rules-router`.

## Naming

Prefer one of these names:

- `<project>-project` for overall project rules.
- `<project>-rules` for process, standards, and workflow rules.
- `<project>-research` for source priorities and research habits.
- `<project>-debug` for recurring debugging workflows.

Use short lowercase hyphen-case names. Keep legacy names if the user already relies on them.

## Minimum Contents

Each project skill should include:

- A frontmatter description that names the project, aliases, domains, repos, and task types that should trigger the skill.
- A short evidence order: user request, local evidence, project notes, preferred sources, broader sources.
- Source priorities, if research is involved.
- A semantic rule-capture policy for clear user standards such as "以后", "每次", "默认", "必须", "优先", "先 X 后 Y", "规则", "标准", or "增加规则".
- Known local paths, logs, configs, or commands only when they are stable and non-sensitive.
- Common failure modes and the preferred troubleshooting order.
- A place for durable failure-learning entries when the project has recurring project-specific errors.
- A rule for when to verify against current local state or current public sources.

## Suggested References

Use references only when they keep `SKILL.md` lean:

- `references/sources.yaml`: preferred sites, forums, official docs, GitHub repos, search templates, and credibility notes.
- `references/local-map.md`: stable repo paths, config locations, logs, build outputs, and generated files.
- `references/known-issues.md`: recurring errors, symptoms, root causes, and verified fixes.
- `references/decisions.md`: durable project decisions and the evidence behind them.
- `references/failure-shields.md`: compact guardrails derived from repeated mistakes, if separate from known issues.
- `references/sources.md`: project-specific source order and search preferences, when research is part of the project.

## Quality Bar

- Prefer durable rules over session recaps.
- Mark stale, version-specific, or forum-derived information clearly.
- Do not present historical notes as current facts without verification.
- Do not overfit to one task; write rules that help future tasks.
- Do not add a rule from a single failure until the root cause is clear enough to distinguish environment/tooling from business logic.
- For strong semantic rule markers, preserve the user's intended order or priority, but still mark unverified technical claims as needing current evidence.
- Keep the project skill small enough that loading it is worth the context cost.
