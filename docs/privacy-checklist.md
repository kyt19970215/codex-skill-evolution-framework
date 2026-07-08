# Privacy Checklist

Run this checklist before publishing or pushing a customized copy.

## Exclude

- Private project names, repository names, local maps, and absolute paths.
- Credentials, tokens, account names, email addresses, cookies, headers, and API keys.
- Raw logs, screenshots, traces, conversation transcripts, generated reports, and memory files.
- Generated capability databases and local plugin inventories.
- Real trigger-learning evidence that reveals user behavior or private work.
- Filled personal `AGENTS.md` files; publish only templates with placeholders.
- Filled rule-maintenance ledgers such as `devolution-ledger.md`.
- Passive trigger event logs, even when sanitized.
- Project-specific source lists and unverified claims presented as facts.

## Sanitize

- Replace project names with `example-project`.
- Replace paths with environment-relative examples.
- Replace source lists with source categories.
- Replace real trigger ledgers and external-skill registries with empty templates.
- Replace personal shortcut words in shareable guidance with placeholders such as `<EVOLUTION_SHORTCUT>`.
- Replace passive trigger examples with synthetic phrases and keep JSONL event logs out of Git.
- Keep public skills focused on reusable process.

## Verify

1. Run `python scripts/validate_framework.py`.
2. Search for private keywords known only to your installation.
3. Inspect the complete staged diff before committing.
4. Confirm every referenced file exists and every `agents/openai.yaml` still matches its skill.
5. Confirm global guidance templates do not contain private projects, local paths, account names, or fixed personal shortcut words.
6. Read representative files again from the remote repository after pushing.
