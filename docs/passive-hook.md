# Passive Advisory Hook

The optional `UserPromptSubmit` Hook observes routing signals and may add one compact `additionalContext` hint for Codex. It is advisory only.

## Install

```text
python scripts/install_or_update.py --enable-passive-hook
```

The installer:

- copies `hooks/user_prompt_passive_trigger.py` into the local Codex Hook directory
- preserves unrelated Hook entries
- keeps one pre-change backup when `hooks.json` already exists
- adds one non-blocking `UserPromptSubmit` command with a five-second timeout
- remembers that the Hook is enabled so later framework updates can update an unchanged Hook file

If the user-level `config.toml` already contains inline Hook tables, the installer stops instead of creating a second representation in `hooks.json`. Add the advisory command to the existing inline configuration manually in that case.

If an unmanaged file already occupies the target Hook path, the installer preserves it, stages the public Hook under `.skill-evolution-updates/`, and leaves the Hook disabled until the conflict is reviewed.

After installation or any Hook update, use `/hooks` in Codex to inspect and trust the exact definition. Codex hashes non-managed Hook definitions, so changed commands require review again.

## Privacy

Default event records contain:

- event and prompt hashes
- hashed session, turn, and working-directory identifiers
- matched signal categories
- suggested route and confidence
- empty `actual_route` and unknown correctness until reviewed

Prompt text, transcript paths, and raw identifiers are excluded by default. Setting `CODEX_PASSIVE_TRIGGER_RECORD_TEXT=1` opts into storing a short redacted prompt locally. Event logs, Hook state, and error logs must remain outside public commits.

## Behavior

The Hook may return a short route hint through `hookSpecificOutput.additionalContext`. It never authorizes automatic edits, installs, commits, publishing, account actions, or other high-impact operations.

Use the event tool to review outcomes:

```text
python ~/.codex/skills/skill-evolution-core/scripts/trigger_event_tools.py summary --ledger ~/.codex/skills/skill-evolution-core/references/evolution-trigger-events.jsonl
```

Recent labeled events receive more weight than old events, with a 30-day half-life by default. Weighting remains evidence for AI review; it cannot promote a trigger or run a Skill automatically.
