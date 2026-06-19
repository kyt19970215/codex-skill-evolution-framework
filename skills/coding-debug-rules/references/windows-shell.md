# Windows Shell Notes

## Common Failure Sources

- PowerShell parsing of quoted executable paths requires call operator `&`.
- Bash heredoc syntax such as `python - <<'PY'` does not work in PowerShell; use a PowerShell here-string piped to the command, a temporary script, or the shell's native multiline form.
- Windows PowerShell and PowerShell 7 can differ in default encoding and command behavior.
- `Get-Content` without explicit encoding may display UTF-8 Chinese text as mojibake in older Windows PowerShell.
- Mojibake inside generated JSON/manifests/logs can be console decoding, serialized content damage, or an upstream generator/path issue; verify before dismissing it.
- Windows PowerShell 5.1 may need UTF-8 with BOM for `.ps1` files containing Chinese text; when in doubt, rewrite with explicit UTF-8 read/write and verify the text around the failing line.
- PowerShell here-strings are fragile for arbitrary copied content because a line containing only `'@` or `"@` ends the string; use JSON/base64/external UTF-8 data files for long raw transcripts.
- PowerShell backtick is an escape character inside double-quoted strings; use single quotes for literal Markdown fences such as `'```'`.
- Paths with spaces require careful quoting; prefer `-LiteralPath` for file cmdlets.
- A command that works in `cmd.exe` may not work unchanged in PowerShell.
- Running a target app as administrator can require the test or recorder process to run as administrator to observe input.

## Safe Defaults

- Use `rg` or `rg --files` for searching when available.
- Use `Get-Content -Encoding UTF8` when reading known UTF-8 Markdown.
- For JSON or manifests containing Chinese paths, prefer a structured UTF-8 parse such as `Get-Content -Encoding UTF8 -Raw | ConvertFrom-Json`, then verify referenced paths with `Test-Path -LiteralPath`; do not rely on the console-rendered text alone.
- Before relying on a Node/Python package, run a tiny `require(...)` or `import ...` check; a visible package directory can still miss transitive dependencies.
- Use `Select-String` for quick local text search.
- Use `Format-Table | Out-String -Width N` only for inspection, not as machine-readable output.
- Keep scripts deterministic and parameterized.
- Before recreating an existing artifact, ask whether the task is a targeted edit/backup/versioning operation; if yes, prefer `Copy-Item -LiteralPath $src -Destination $dst` and then edit the copied artifact with the appropriate structured tool.
- Prefer ASCII in scripts unless Chinese text is required; use Unicode codepoint helpers if older PowerShell encoding is fragile.

## Troubleshooting Order

1. Re-run the exact command and capture the exact error.
2. Check shell, working directory, and path existence.
3. Check encoding and quoting.
4. Check dependency/tool availability and version.
5. If generating an artifact, complete generation before checking existence, size, dimensions, or preview; do not parallelize dependent verification with the generator.
6. Check whether the command needs elevated privileges.
7. Only then modify business logic.
