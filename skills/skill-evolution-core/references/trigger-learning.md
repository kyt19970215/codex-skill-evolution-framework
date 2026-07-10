# Trigger Learning

Use this reference when the user invokes the configured evolution shortcut and the preceding conversation suggests a personal trigger word or phrase should be learned.

## Goal

Learn the user's natural trigger words without turning every repeated phrase into a permanent rule.

Think of this like a small habit counter: it records "the user used this kind of wording, and the correct handling was this route" until the pattern is stable enough to become a trigger.

## Counter Rule

Use `references/trigger-candidates.md` as the ledger.

For each forced evolution run:

1. Identify the user's key phrase or pattern before the configured evolution shortcut.
2. Normalize it into a short trigger candidate.
3. Record the routing outcome, such as `coding-debug-rules`, `research-verification`, `project skill`, or `global guidance`.
4. Increment the count only when the new case has the same intent and same destination as earlier cases.
5. At count 3, mark the candidate as `promote-candidate`.
6. Use `scripts/trigger_event_tools.py` to prefer recent labeled outcomes over old unlabeled observations; do not treat recency weight as automatic approval.

## Promotion Rule

At count 3:

- Auto-promote only if the trigger is low-risk, narrow, and clearly maps to one skill or reference.
- Ask the user before promotion if the trigger is broad, ambiguous, project-sensitive, private, safety-sensitive, account-related, destructive, or affects publishing.
- Prefer adding the trigger to `skill-evolution-router/references/semantic-rule-capture.md` or the relevant skill frontmatter description.
- Do not store raw conversation transcripts. Store only sanitized short evidence.
- Keep `actual_route` and correctness unknown until a person or the acting AI reviews the outcome.

## Better Than A Plain Counter

A plain counter can learn the wrong thing. Use these safeguards:

- Count intent plus destination, not just words.
- Keep one short sanitized example per occurrence.
- Do not count sarcasm, rejected suggestions, brainstorming, or one-off wording.
- Merge synonyms only when the handling is identical.
- If a promoted trigger causes over-triggering, remove it or narrow the wording.

## Entry Format

```markdown
## Candidate: <short trigger>

- Count: 1
- Destination:
- Status: watch | promote-candidate | promoted | rejected
- Evidence:
  - YYYY-MM-DD: <sanitized phrase> -> <routing outcome>
- Promotion note:
```
