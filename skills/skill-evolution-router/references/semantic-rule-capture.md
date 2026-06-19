# Semantic Rule Capture

Use this reference when the user gives a durable standard without explicitly saying "edit the skill file."

## Strong Capture Markers

Treat these as likely durable-rule intent when scope is clear:

- "以后", "以后都", "下次", "每次", "总是", "默认"
- "必须", "不要", "禁止", "优先", "先 X 后 Y", "只要 X 就 Y"
- "规则", "标准", "流程", "原则", "习惯", "记住", "保存", "沉淀"
- "增加规则", "写进 skill", "加入 skill", "加到项目规则"
- "进化" when it appears at the end of a conversation or after a task

When the user only says "增加规则" or similar, inspect the immediately preceding user request and the latest relevant failure/self-check. Extract the durable semantic rule from that context.

When the user only says "进化" after a task, run `skill-evolution-core` first, then use this router to decide which durable lessons should be promoted.

## Capture Decision

Add the rule directly when all are true:

1. The user used a strong capture marker.
2. The scope is clear: global coding/debug, research/verification, skill evolution, or a named/current project.
3. The rule is a reusable preference, order, source priority, guardrail, or known pit.
4. The rule does not store secrets, account details, private tokens, or unsafe instructions.

Ask or present a candidate instead when:

- The scope is ambiguous.
- The rule is based on an unverified technical claim.
- The rule could increase safety, security, anti-cheat, account, destructive-edit, or compliance risk.
- The wording looks like a one-off task instruction rather than a durable standard.

## Entry Shape

Write compact rules. Prefer this shape:

```markdown
- When <scope/trigger>, <preferred behavior>. Rationale: <short evidence or user preference>.
```

For source priority rules:

```markdown
- For <topic>, check <source/order> before broader search. Verify against current local evidence before concluding.
```
