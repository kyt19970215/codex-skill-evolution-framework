---
name: codex-capability-router
description: Route Codex work to the best installed skills, plugins, apps, MCP tools, or safe candidate plugins. Use when the task mentions plugin discovery, installable Codex plugins, role-specific plugins, Product Design, business analysis, data analytics, creative production, sales workflows, finance workflows, documents/slides/sheets/PDFs, GitHub work, browser/computer use, or when starting a non-trivial project task where an installed Codex capability may help even if the user did not name it.
---

# Codex Capability Router

Use this skill to choose capabilities before doing substantial work. It is a routing layer, not a replacement for the selected skill or plugin.

## Workflow

1. Identify task signals:
   - user intent, domain, requested artifact, current workspace, file types, and explicit tools mentioned
   - installed skills in the current session and plugin skills already exposed by Codex
   - local plugin cache and registry data when the answer depends on installed or candidate plugin inventory

2. Prefer installed capability:
   - If a bundled or installed skill/plugin clearly matches, use it directly and tell the user briefly which one is being used.
   - For Product Design work, start with the Product Design index or get-context skill, then route to ideate, image-to-code, audit, prototype, research, share, or URL-to-code as needed.
   - For design work, treat OpenAI image generation as a normal design option for visual directions, realistic product/interface references, mood boards, campaign visuals, and asset exploration; do not default only to wireframes or line-art sketches.
   - For files and artifacts, prefer the installed document, spreadsheet, presentation, PDF, GitHub, browser, computer-use, or sites plugin skill instead of hand-rolling the workflow.
   - When a local external-skill registry is configured, apply `references/external-skill-registry.md` so overlapping skills have one owner and heavy workflows are loaded only when needed.

3. Use the local registry when routing is unclear:
   - Build or refresh installed capability data:

```powershell
python "$env:USERPROFILE\.codex\skills\codex-capability-router\scripts\build_capability_registry.py"
```

   - Query a task:

```powershell
python "$env:USERPROFILE\.codex\skills\codex-capability-router\scripts\query_capability_router.py" --task "product design prototype from a screenshot"
```

4. Discover candidate plugins only as suggestions:
   - Use `scripts/refresh_plugin_candidates.py` or public-source research to find official or community candidates.
   - Never auto-install, auto-enable, or auto-trust candidate plugins, MCP servers, apps, or hooks.
   - When suggesting a candidate, state the project function in plain language and ask the user whether to install or investigate it.

5. Continue with the selected workflow:
   - Load the matched skill/plugin instructions.
   - If no installed capability fits, proceed with normal local evidence and general best practices.

## References

- `references/routing-categories.md`: task signals and preferred installed capabilities.
- `references/plugin-discovery-policy.md`: discovery sources, trust levels, and install boundary.
- `references/external-skill-registry.md`: selected external skill routes, precedence, and side-effect boundaries.
