# Codex Skill Evolution Framework

[简体中文](README.zh-CN.md)

A reusable, privacy-clean framework for growing a Codex skill system without turning it into one giant prompt.

It keeps six concerns separate:

1. `skill-evolution-core` — create, update, split, merge, validate, and absorb skills.
2. `skill-evolution-router` — decide where durable rules and lessons belong.
3. `project-rules-router` — select project-specific guidance before non-trivial work.
4. `coding-debug-rules` — triage local environment, shell, encoding, path, dependency, build, and test failures.
5. `research-verification` — verify public tools, APIs, versions, and error behavior against current sources.
6. `codex-capability-router` — select installed skills, plugins, apps, MCP tools, or safe discovery candidates.

The default shortcut aliases are `进化` for a full evolution pass and `吞噬` for capability absorption. They can be renamed or removed after installation.

## Privacy Model

This repository contains no real trigger evidence, generated capability inventory, local absolute paths, account data, private project names, logs, screenshots, conversation transcripts, or project-specific source lists.

`skills/codex-capability-router/data/` is generated locally and ignored by Git. `trigger-candidates.md` is an empty ledger template. `external-skill-registry.md` is a neutral configuration template.

## Install

Copy the desired folders from `skills/` into your Codex skills directory:

```text
~/.codex/skills/
  skill-evolution-core/
  skill-evolution-router/
  project-rules-router/
  coding-debug-rules/
  research-verification/
  codex-capability-router/
```

Install all six for the complete routed system. The skills use Markdown and YAML; the capability-registry and validation scripts require Python 3 and otherwise use the standard library.

## Validate

From the repository root:

```text
python scripts/validate_framework.py
```

The validator checks skill metadata, folder names, referenced files, script syntax, forbidden generated artifacts, and common privacy leaks.

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
- Put repository commands and conventions in the repository's `AGENTS.md`.
- Copy `templates/project-skill-template/` for private project knowledge.
- Keep real trigger evidence and local capability inventories private.
- Run the validator and [privacy checklist](docs/privacy-checklist.md) before publishing a customized fork.

## License

MIT. See [LICENSE](LICENSE).
