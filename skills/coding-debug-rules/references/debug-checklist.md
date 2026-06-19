# Debug Checklist

## Before Editing

- What changed recently?
- Is the failure reproducible?
- Is the error from the target code, shell, dependency, permissions, or data?
- Is there a smaller command or sample that reproduces it?
- Are there generated files that should not be manually edited?

## During Editing

- Keep the edit small.
- Preserve user changes.
- Avoid changing formatting across unrelated files.
- Prefer structured APIs/parsers over brittle string manipulation when available.
- Add comments only for non-obvious logic.

## After Editing

- Run targeted verification.
- Inspect output artifacts if behavior is visual, data, or report based.
- Summarize changed files, verification, and residual risk.
- If a fix remains uncertain, name the uncertainty and the next evidence needed.
