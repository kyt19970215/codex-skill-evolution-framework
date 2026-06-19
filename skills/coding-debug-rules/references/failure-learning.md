# Failure Learning

Use this reference after a failed command, temporary script, file generation, tool call, build, test, or local verification step. Also use it for near-misses where a command succeeds but produces anomalous output, mojibake, unexpected paths, empty artifacts, suspicious file mutations, or avoidable repeated work.

## Self-Check

Before changing business logic, identify:

1. The exact failed or anomalous action and complete error/output text.
2. The execution context: OS, shell, working directory, runtime, tool versions, encoding, and relevant paths.
3. The failure class: shell syntax, quoting/escaping, path, encoding, permissions, missing dependency, version/API mismatch, generated-file source of truth, test/data mismatch, or business logic.
4. The smallest local check that confirms or rejects the suspected class.
5. The verified fix or the next missing evidence.

## Promotion Rules

- Promote only durable rules that would prevent a future repeat.
- Do not promote a rule when the root cause is still speculative.
- Keep one-off task details, private paths, secrets, tokens, and noisy logs out of skills.
- If the user explicitly asks to save, remember, classify, or add the lesson, edit the appropriate skill reference directly.
- If the user did not ask for a durable update, report a candidate rule instead of silently changing skills.

## Routing

- Add project-agnostic shell, encoding, path, quoting, script, local tool, dependency, build, test, or generated-file guardrails here or in `windows-shell.md` / `debug-checklist.md`.
- Add public-source, API, version compatibility, dependency release, browser/driver, install/upgrade, stale-doc, or exact-public-error guardrails to `research-verification`.
- Add repo paths, project commands, domain-specific traps, local artifact rules, and architecture exceptions to the narrow project skill.
- For mixed lessons, store the reusable guardrail in the global type skill and the project-specific example in the project skill.

## Durable Failure Shields

## Mojibake In Generated Metadata Is Not Automatically Cosmetic

- Symptom: A generated JSON, manifest, log, or command output shows Chinese paths or filenames as mojibake, while the main artifact appears to exist.
- Root cause: The issue may be console decoding, file encoding mismatch, serialized metadata damage, or an upstream generator/path bug; a successful exit code does not distinguish these.
- Guardrail: Before dismissing it as harmless, re-read the file with explicit UTF-8, parse structured data with the native parser, and verify referenced paths with `Test-Path -LiteralPath` or equivalent.
- Verification: Confirm whether the mojibake exists in the parsed value, only in console rendering, or only in a secondary manifest; state which layer was affected.

## Prefer Copy-And-Targeted-Edit For Existing Artifacts

- Symptom: A task asks to revise, version, back up, or slightly extend an existing file, but the workflow rebuilds a new artifact from scratch and repeats earlier generation work.
- Root cause: The previous generated file was not treated as a reusable source of truth, or the workflow did not first classify the task as copy/edit versus rebuild.
- Guardrail: Before rebuilding, check whether the existing artifact can be copied with `Copy-Item -LiteralPath` and edited through a structured tool while preserving formatting and reducing work.
- Verification: Compare the expected edit scope, source availability, and editing reliability; use rebuild only when the old artifact is not a trustworthy editable source, the narrative/layout must substantially change, or targeted editing would be riskier than regeneration.

## Shell Syntax Before Business Logic

- Symptom: A quick inline script fails before the target code runs, often with parser errors such as missing redirection targets or unexpected tokens.
- Root cause: The command uses syntax from a different shell, such as Bash heredoc syntax inside PowerShell.
- Guardrail: Identify the active shell first and translate multiline commands into that shell's native form before debugging application logic.
- Verification: Run a minimal one-line or two-line probe in the active shell before executing the full script.

## Encoding And Raw Transcript Rendering

- Symptom: Chinese text becomes mojibake, a generated script reports an unterminated string, or copied Markdown/code fences break parsing.
- Root cause: Windows PowerShell 5.1 encoding defaults, here-string terminators embedded in content, or backtick escaping inside double-quoted strings.
- Guardrail: Use explicit UTF-8 reads/writes, prefer UTF-8 with BOM for Windows PowerShell 5.1 scripts containing Chinese, and store long arbitrary text in external UTF-8 data files instead of raw here-strings.
- Verification: Inspect the exact failing line with `Get-Content -Encoding UTF8`, then re-run a small parser check before regenerating the artifact.

## Dependency Presence Is Not Dependency Usability

- Symptom: A package folder exists but importing or requiring it fails because a transitive dependency is missing.
- Root cause: Filesystem presence was treated as proof that the runtime dependency works.
- Guardrail: Verify the actual import/require path with a tiny command before choosing an implementation path.
- Verification: Record the runtime executable, module search path, package version when available, and the import/require result.

## Do Not Parallelize Dependent Verification

- Symptom: A generated artifact is reported missing or incomplete immediately after a generation command.
- Root cause: Existence/size/preview checks ran in parallel with the generator instead of after it completed.
- Guardrail: Use parallel calls only for independent reads; run dependent verification sequentially after the producer finishes.
- Verification: Re-check file existence, size, dimensions, and preview after the generator command exits successfully.

## Prefer Native Config Profiles Before Switch Scripts

- Symptom: A tool/provider switch creates ad hoc scripts that copy active config or auth files before checking whether the tool has native profile or override support.
- Root cause: The setup is treated as a generic file-copy problem instead of first checking the tool's official configuration protocol.
- Guardrail: For Codex model/provider/API switching, check the current Codex manual plus local CLI help before writing scripts. Prefer `$CODEX_HOME/<name>.config.toml`, `--profile <name>`, provider `env_key`, and documented app deep links/settings over copying `config.toml` or `auth.json`.
- Verification: Confirm which commands or app surfaces actually accept profiles or overrides, and remove temporary switch scripts when a native mechanism covers the workflow.

## Entry Format

Use this compact shape when adding a durable failure shield:

```markdown
## Short Title

- Symptom:
- Root cause:
- Guardrail:
- Verification:
```
