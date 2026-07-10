# Codex Skill Evolution Framework

[简体中文](README.zh-CN.md)

A reusable, privacy-clean framework for growing a Codex skill system without turning it into one giant prompt.

It keeps seven concerns separate:

1. `skill-evolution-core` — create, update, split, merge, absorb, and maintain skills.
2. `skill-evolution-router` — decide where durable rules and lessons belong.
3. `project-rules-router` — select project-specific guidance before non-trivial work.
4. `coding-debug-rules` — triage local environment, shell, encoding, path, dependency, build, and test failures.
5. `research-verification` — verify public tools, APIs, versions, and error behavior against current sources.
6. `codex-capability-router` — select installed skills, plugins, apps, MCP tools, or safe discovery candidates.
7. `skill-evolution-validator` — run manual structure, behavior, ledger, privacy, and platform-freshness audits.

Shortcut aliases are local configuration. On first installation, each user chooses one shortcut for a full evolution pass and another for capability absorption. The public framework does not impose personal trigger words.

The framework also includes an optional global guidance template at `templates/global-agents-template/AGENTS.md`. It is a privacy-clean starting point for response style, smallest-sufficient execution, source and decision gates, confirmation rhythm, rule layering, verification habits, file safety, and evolution routing. It is not installed automatically because a filled global `AGENTS.md` is personal configuration.

Skill evolution now supports proportional load levels, executable routing regression cases, outcome labels, recency-weighted evidence, and observation-first passive trigger probes. The optional Hook can add one advisory route hint, but it does not execute workflows, edit files, install tools, commit, push, publish, or perform account actions.

## Privacy Model

This repository contains no real trigger evidence, generated capability inventory, local absolute paths, account data, private project names, logs, screenshots, conversation transcripts, or project-specific source lists.

`skills/codex-capability-router/data/` is generated locally and ignored by Git. `trigger-candidates.md`, `devolution-ledger.md`, and `evolution-change-log.md` are empty local ledger templates. Passive trigger event logs, Hook state, and validator reports are local artifacts that remain outside the public repository. `external-skill-registry.md` is a neutral configuration template.

The advisory Hook records prompt, session, turn, and working-directory hashes rather than raw values by default. Raw prompt text is recorded only when the user explicitly sets `CODEX_PASSIVE_TRIGGER_RECORD_TEXT=1` in the local environment.

## Install Or Update

Clone or download the repository, then run from its root:

```text
python scripts/install_or_update.py
```

On first installation, the script asks for two distinct shortcut aliases and installs all seven routed skills. For unattended first installation, supply both choices explicitly:

```text
python scripts/install_or_update.py --non-interactive --evolution-trigger "YOUR_EVOLUTION_SHORTCUT" --absorption-trigger "YOUR_ABSORPTION_SHORTCUT"
```

Run the same script after pulling a newer repository version. Saved shortcuts and local personal evolution are preserved by default. Unchanged framework files update automatically; locally modified files remain in place, while incoming copies are written under `~/.codex/.skill-evolution-updates/` for review.

Installations created before the manifest existed are handled conservatively: existing files are preserved and incoming versions are staged for review. The installer uses Python 3 and otherwise only the standard library.

### Optional Advisory Hook

The passive `UserPromptSubmit` Hook is opt-in:

```text
python scripts/install_or_update.py --enable-passive-hook
```

On an unattended first installation, combine that flag with both shortcut arguments. The installer preserves unrelated entries in `~/.codex/hooks.json`, keeps one backup under `~/.codex/.skill-evolution-backups/` when that file already exists, and installs a non-blocking advisory Hook. Use `/hooks` in Codex to review and trust the exact Hook definition after installation or an update.

See [Passive Hook](docs/passive-hook.md) for privacy and behavior boundaries.

## Validate

From the repository root:

```text
python scripts/validate_framework.py
```

The validator checks skill metadata, folder names, referenced files, script syntax, forbidden generated artifacts, and common privacy leaks.

After installation, run the manual evolution-system validator when you need a health, behavior, ledger, freshness, or release-readiness report:

```text
python ~/.codex/skills/skill-evolution-validator/scripts/validate_evolution_skills.py --mode full
```

`auto` runs a full first pass and uses a log-based fast pass after a snapshot exists. Fast mode explicitly does not claim that executable behavior regression ran.

## Build The Local Capability Registry

After installation:

```text
python ~/.codex/skills/codex-capability-router/scripts/build_capability_registry.py
python ~/.codex/skills/codex-capability-router/scripts/query_capability_router.py --task "create and review a slide deck"
```

The optional candidate refresh script queries public GitHub metadata. It does not upload local files:

```text
python ~/.codex/skills/codex-capability-router/scripts/refresh_plugin_candidates.py
```

## Customize Safely

- Put always-on personal preferences in global guidance rather than publishing them inside a skill.
- Use `templates/global-agents-template/AGENTS.md` as a starting point for private global guidance, then replace placeholders locally.
- Put repository commands and conventions in the repository's `AGENTS.md`.
- Copy `templates/project-skill-template/` for private project knowledge.
- Keep `skill-evolution-entry/`, `trigger-candidates.md`, `devolution-ledger.md`, `evolution-change-log.md`, and `external-skill-registry.md` local; the updater never overwrites them.
- Keep passive trigger event logs local; they may contain behavior signals even when sanitized.
- Keep real trigger evidence and local capability inventories private.
- Run the validator and [privacy checklist](docs/privacy-checklist.md) before publishing a customized fork.

## License

MIT. See [LICENSE](LICENSE).
