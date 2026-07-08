# Passive Trigger Observation

Use this reference when designing or reviewing semantic triggers based on a user's language habits.

## Goal

Build a lightweight observation layer, not an automatic workflow runner.

The intended split is:

- runtime cost is acceptable when it improves correctness
- AI/context cost should stay low
- scripts should do repeatable counting, matching, recency checks, redaction, and compact reporting
- AI should steer, review ambiguity, approve promotion, and handle exceptions

During the suggestion stage, judgment stays AI-led and script-assisted. Scripts may propose likely routes, shields, and confidence summaries, but the AI decides whether to use the hint in the current conversation. Self-triggering is deferred until the candidate has enough organized evidence, validation, and explicit user approval.

## Observation First

During the early phase, passive triggers must not automatically run skills or workflows.

Allowed:

- L0 record: append a sanitized event row
- L1 suggest: return a short hint to the AI; AI remains the decision-maker
- L2 soft activate: AI may choose a skill or shield based on the hint; script output is still advisory

Not allowed yet:

- L3 automatic light trigger
- automatic edits
- automatic installs
- automatic commits, publishing, account actions, or other high-impact operations

## Trigger Levels

| Level | Name | Behavior |
| --- | --- | --- |
| L0 | record | Log the candidate trigger only. |
| L1 | suggest | Suggest a likely route or shield in one compact summary; AI judges whether to use it. |
| L2 | soft activate | AI may choose to apply the short hint; no long context load by default, and no script-owned routing. |
| L3 | automatic light trigger | Future state only after accuracy evidence and user approval. |
| L4 | configured forced trigger | Explicit configured shortcuts or explicit self-check requests. |

## Promotion Gate

Promote a passive trigger to L3 only when all are true:

- at least 10 observed events, unless the user approves a smaller sample
- recent accuracy is 80% or higher
- no high-impact false positive
- one clear destination skill or shield family
- validation lists the candidate and its evidence
- user approves the promotion

If a trigger is broad, private, safety-sensitive, account-related, destructive, project-sensitive, or publish-related, keep it below L3 unless the user explicitly approves the narrower behavior.

## Event Ledger

`scripts/passive_trigger_probe.py` can append JSONL rows to a local event ledger. The default ledger is created in the user's installed Codex home, not in the public repository.

Each row should be one JSON object:

```json
{
  "time": "2026-01-01T00:00:00+00:00",
  "trigger_level": "L1",
  "trigger_type": "passive_semantic_candidate",
  "source_signal": "sanitized short phrase",
  "suggested_route": "coding-debug-rules",
  "actual_route": "",
  "confidence": "medium",
  "changed_rules": false,
  "was_correct": null,
  "auto_action_allowed": false,
  "notes": "observation only"
}
```

Do not store raw full prompts, secrets, private account data, long logs, screenshots, or sensitive project details.

## Coding Shield Example

For a coding-like task, the probe may return:

```json
{
  "trigger_level": "L1",
  "suggested_route": "coding-debug-rules",
  "shield_hints": ["encoding", "path", "quoting", "dependency"],
  "confidence": "medium",
  "auto_action_allowed": false
}
```

This is a hint, not automatic workflow execution.
