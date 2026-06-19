# Plugin Discovery Policy

Use discovery to inform the user, not to silently modify their Codex setup.

## Source Priority

1. Current session tools and skills already exposed to Codex.
2. Local plugin cache under `~/.codex/plugins/cache`.
3. Official OpenAI Codex docs, plugin directory, release notes, and OpenAI-maintained repositories.
4. GitHub repositories with a visible `.codex-plugin/plugin.json` or marketplace file.
5. Community indexes or forum posts, treated as leads until manifest and source are inspected.

## Trust Levels

- `installed`: available in the current Codex environment or local plugin cache.
- `official-candidate`: official OpenAI source but not installed or not exposed in the current session.
- `community-candidate`: public community project with a plausible Codex plugin structure.
- `unverified-lead`: public mention without a confirmed manifest.

## Install Boundary

Never auto-install or auto-enable a candidate plugin. When a candidate is relevant:

1. Name the plugin or source.
2. State the project function in plain language.
3. State the trust level and why.
4. Ask the user whether to inspect, install, or ignore it.

Do not auto-trust plugin hooks, MCP servers, app connectors, or commands. If a candidate requires credentials, private workspace data, or external app authorization, say that before install.

## Current Known Public Directions

OpenAI has described role-specific plugin directions including Product Design, Data Analytics, Creative Production, Sales, Public Equity Investing, and Investment Banking. Treat availability as current-state data that must be refreshed before making install claims.

Community discovery sources currently worth checking include OpenAI plugin examples and community curated lists such as awesome Codex plugin repositories. Treat them as candidate sources, not installed capability.

Image generation is not only a fallback for missing design tools. When a design task benefits from visual directions, realistic references, product imagery, or mood boards, treat OpenAI image generation as a normal design option alongside Product Design workflows.
