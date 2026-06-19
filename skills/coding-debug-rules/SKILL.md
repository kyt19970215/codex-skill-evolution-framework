---
name: coding-debug-rules
description: Reusable coding, debugging, shell, environment, script, build, test, path, encoding, dependency, error-triage, and failure-learning workflow rules. Use when working on code changes, failing commands, Windows PowerShell issues, local scripts, build/test failures, dependency/tool version problems, generated files, CLI tools, automation scripts, error self-checks, or when the user asks to debug, fix, install, verify, run, inspect, remember, classify, or add a technical failure rule in any project.
---

# Coding Debug Rules

Use this skill for project-agnostic coding and tooling work. Combine it with project-specific skills when available.

## Core Workflow

1. Read the local project instructions first: nearest `AGENTS.md`, active user instructions, and relevant project skill.
2. Collect the smallest useful local fingerprint:
   - exact command or reproduction step
   - complete error text
   - OS/shell/runtime
   - tool/package/version
   - recently changed files
   - expected vs actual result
3. Classify the failure before editing:
   - environment or permission
   - path, quoting, escaping, encoding
   - version/API mismatch
   - dependency missing
   - test/data mismatch
   - actual business logic bug
4. Make the smallest scoped change that addresses the likely cause.
5. Re-run the targeted verification.
6. If the first local fix fails, or the root cause is still unclear after 10-15 minutes, use `research-verification` for external sources before continuing to modify code.
7. After a command, script, tool call, file generation, or verification failure, or after anomalous output such as mojibake, unexpected paths, empty files, duplicated work, or suspicious encoding, run the failure-learning pass in `references/failure-learning.md` before deciding whether to dismiss it or change business logic.

## Windows And PowerShell Guardrails

- Treat encoding, quoting, paths with spaces, drive letters, shell differences, and PowerShell version as first-class risks.
- Prefer `-LiteralPath` for filesystem paths.
- Avoid chaining noisy commands with separators when parallel reads would be clearer.
- Do not pass file lists from PowerShell into another shell for destructive operations.
- Before recursive delete or move, verify resolved absolute target paths.
- For file edits, prefer the repo's normal editor/patch flow; avoid ad hoc shell write tricks when a structured edit is safer.
- For modifying, copying, backing up, or versioning existing user artifacts, first decide whether a direct `Copy-Item -LiteralPath ...` followed by targeted edit is safer and cheaper than rebuilding from source.
- Use explicit encodings when reading/writing user-facing text.
- If Chinese text appears as mojibake, verify the file encoding before changing content.
- If generated metadata, JSON, manifests, or logs contain mojibake in paths or filenames, do not assume it is only console display; verify with an explicit UTF-8 read and, when possible, a structured parser plus file existence check.

## Secrets And API Keys

- If the user actively pastes an API key, token, password, cookie, or private credential and asks to use it, permission covers current-task use only. Do not repeat it, store it in memory, write it into skills, commit it to a repo, or include it in logs/search queries.
- For CLI or tool setup that needs a credential, prefer local environment variables, local auth files, or secret stores with placeholders in instructions. If current-task use is necessary, keep it scoped to that task and avoid echoing it. Treat any credential pasted into chat as exposed for risk reporting, while still respecting the user's explicit instruction that it may be used now.

## Code Change Rules

- Prefer existing project patterns and helper APIs.
- Keep changes tightly scoped to the requested behavior.
- Do not refactor unrelated code while fixing a bug unless needed for safety.
- Do not revert user changes unless explicitly asked.
- Add tests proportional to risk and blast radius.
- When working with generated output, know whether the source of truth is the generator or the generated file.

## Verification Rules

- Run the narrowest meaningful test first.
- If no automated test exists, run the relevant script/CLI and inspect generated output.
- For UI/image/report work, inspect the generated preview where possible.
- In the final answer, say what was verified and what was not.
- Do not claim a fix is complete if only the script compiled but behavior was not checked.

## References

- `references/windows-shell.md`: Windows/PowerShell pitfalls.
- `references/debug-checklist.md`: unclear-root-cause checklist.
- `references/failure-learning.md`: classify failed technical actions and promote concise guardrails into the right skill when asked.
