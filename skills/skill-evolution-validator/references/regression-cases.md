# Behavior Regression Cases

The executable case set verifies these boundaries:

- Each user-selected shortcut routes to `skill-evolution-core` only when it is an action request.
- Discussion-only or negated shortcut wording does not force execution.
- Evolution-system health, freshness, cleanliness, and behavior-audit requests route to `skill-evolution-validator`.
- A read-only health audit still routes to the report-first validator while preserving the no-edit constraint.
- Durable rule-capture requests route to `skill-evolution-router`.
- Coding failures route to `coding-debug-rules`.
- A lightweight continuation may reuse the prior advisory route without executing it automatically.
