# Quality Gate

Before finishing a skill update, check:

- Does the `description` clearly say when the skill should trigger?
- Is `SKILL.md` small enough that loading it is worth the context cost?
- Are detailed examples, matrices, and source lists in `references/`?
- Are deterministic repeated commands in `scripts/` when useful?
- Are secrets, tokens, private account data, and noisy logs excluded?
- Did the edit avoid duplicating the same rule in several places?
- Did the edit avoid turning one failure into an over-narrow hard rule?
- If a rule may block future work, was it scoped, softened, or routed through `references/devolution.md` instead of becoming always-on?
- For an upstream skill, were compact principles absorbed while heavy workflows stayed independently updateable and routed?
- Are upstream learn/skillify commands prevented from bypassing the evolution ownership boundary?
- If the update came from a near-miss instead of a hard failure, did the new shield say what observable symptom should trigger it?
- If the update adds a learned trigger word, does `trigger-candidates.md` show enough sanitized evidence and a clear routing outcome?
- Could the learned trigger make a skill trigger too broadly or on ordinary conversation?
- If the update relaxed, scoped, downgraded, archived, or removed a rule, was `references/rule-lifecycle.md` applied and `references/devolution-ledger.md` updated?
- Were Chinese or other non-ASCII rules read/written with explicit UTF-8?
- Did the validator pass after structural changes?
- Did the final answer name changed files and verification?
