# Ledger Reconciliation

The local change log lives at `skill-evolution-core/references/evolution-change-log.md`. Framework updates preserve the installed copy.

Each new durable change should include a `Files` list with paths relative to the installed skills root. The validator compares paths changed since the previous snapshot with the latest entry and reports unmatched files.

Do not invent missing historical links or copy full prompts into the ledger. Use a sanitized recovery locator when a direct source reference is unavailable.
