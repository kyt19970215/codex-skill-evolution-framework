# Quality Gate

Before finishing a skill update, check:

- Does the `description` clearly say when the skill should trigger?
- Is `SKILL.md` small enough that loading it is worth the context cost?
- Are detailed examples, matrices, and source lists in `references/`?
- Are deterministic repeated commands in `scripts/` when useful?
- Are secrets, tokens, private account data, and noisy logs excluded?
- Did the edit avoid duplicating the same rule in several places?
- When a new lesson overlapped existing guidance, was it merged into the existing owner text instead of appended as a parallel section?
- Did the edit remove or reconcile superseded duplicates so the rule surface is cleaner than before?
- Did the edit avoid turning one failure into an over-narrow hard rule?
- If this update was triggered by the configured evolution shortcut, was the load level classified with `references/evolution-load-levels.md` and kept to the smallest sufficient scope?
- If this update was capability absorption, did post-install discovery run before editing durable routing or skill behavior, and did the final routing reflect verified installed identifiers, versions, paths, warnings, missing dependencies, and minimal invocation results?
- If this update was capability absorption, did it include a lightweight devolution/reconciliation pass for overlap, conflict, obsolete local wording, and semantic preservation?
- If a rule may block future work, was it scoped, softened, or routed through `references/devolution.md` instead of becoming always-on?
- For an upstream skill, were compact principles absorbed while heavy workflows stayed independently updateable and routed?
- Are upstream learn/skillify commands prevented from bypassing the evolution ownership boundary?
- If the update came from a near-miss instead of a hard failure, did the new shield say what observable symptom should trigger it?
- If the update adds a learned trigger word, does `trigger-candidates.md` show enough sanitized evidence and a clear routing outcome?
- Could the learned trigger make a skill trigger too broadly or on ordinary conversation?
- If this update adds passive semantic triggering, is it kept in observation mode L0-L2 unless a validation report and user approval support L3 promotion?
- Does the Hook return only advisory context, avoid blocking by default, and preserve all approval and safety boundaries?
- Are prompt text, session identifiers, working directories, and transcripts absent from default event records except as short hashes?
- Were representative positive, negative, discussion-only, audit, coding-failure, and continuation cases executed rather than checked only by keyword presence?
- Are real Hook events separated from smoke tests, with `actual_route` and `was_correct` left unknown until reviewed?
- Does route weighting decay old evidence without automatically promoting or executing a route?
- Did any repeated trigger counting use `scripts/passive_trigger_probe.py` or another compact script-readable ledger instead of forcing AI to reread long conversation history?
- If the update relaxed, scoped, downgraded, archived, or removed a rule, was `references/rule-lifecycle.md` applied and `references/devolution-ledger.md` updated?
- If this update relaxed, downgraded, split trigger levels, or made a check conditional, did tests and user confirmation cover the changed semantics or execution effect?
- If the claimed change is only cleanup, did representative trigger checks show equivalent behavior after the edit?
- Were Chinese or other non-ASCII rules read/written with explicit UTF-8?
- Did the validator pass after structural changes?
- For a manual validator run, did `fast` clearly remain log-based while `full` executed behavior cases and ledger reconciliation?
- Did the final answer name changed files and verification?
