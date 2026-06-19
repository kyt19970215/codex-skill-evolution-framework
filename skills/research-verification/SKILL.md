---
name: research-verification
description: Reusable external research and verification workflow for public tools, plugins, dependencies, APIs, OS behavior, browser/driver issues, version compatibility, security/anti-cheat claims, install/upgrade problems, exact error messages, stale claims, and research failure-learning rules. Use when the user asks to search, verify, compare current options, investigate a public project, remember or classify a public-source failure, or when local debugging hits an unclear environment/dependency/tooling issue.
---

# Research Verification

Use this skill when a claim or technical behavior may have changed, depends on public tooling, or needs external precedent.

## Research Workflow

1. Collect minimal local evidence first:
   - exact error or claim
   - tool/package/project name
   - version and OS/runtime
   - command or reproduction step
   - relevant local config/file names
2. Form a narrow search query from public, non-sensitive details.
3. Search 1-3 high-relevance sources first.
4. Prefer sources in this order:
   - official docs
   - official changelog/release notes
   - GitHub repo, issue, discussion, maintainer comment
   - standards/specification
   - Stack Overflow or high-signal forum
   - blog/video/forum as hypothesis only
5. Return to the local environment and verify the selected hypothesis.
6. Report the source-backed conclusion, local verification result, and remaining uncertainty.

## Search Budget

- Start narrow; do not browse broadly unless the user asks for deeper research.
- For recommendations that could cost significant time or money, verify current options.
- For legal, medical, financial, anti-cheat/security, or account-risk topics, browse by default and phrase cautiously.

## Privacy And Safety

- Do not put private code, account names, tokens, full logs, local paths with sensitive names, or proprietary details into search queries.
- Search generic error fragments and public component names.
- Treat forum claims as leads, not facts.
- Never claim "no risk" for anti-cheat, account, security, or compliance topics.

## Output Pattern

Use this shape when helpful:

- Conclusion
- Local evidence
- External evidence
- What was verified locally
- Risk / uncertainty
- Next step

## Combine With Other Skills

- Combine with `coding-debug-rules` when researching a coding/tooling failure.
- Combine with `project-rules-router` when a project-specific source priority exists.
- Combine with the relevant project skill before broad research if the project has preferred sources or terminology.

## Failure Learning

- When a public-source, version, API, dependency, browser/driver, install/upgrade, or stale-doc issue causes a failed attempt, capture the exact claim, source used, local version/context, corrected source, and verified outcome.
- Promote only reusable source-selection or verification guardrails, not long search transcripts.
- If the user asks to save the lesson, add it to `references/failure-learning.md`.

## References

- `references/source-quality.md`: source strength and verification notes.
- `references/failure-learning.md`: durable research and version-verification failure shields.
