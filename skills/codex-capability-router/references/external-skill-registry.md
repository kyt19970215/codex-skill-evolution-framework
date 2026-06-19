# External Skill Registry

Use this file as a local configuration template. It intentionally ships without a real user's installed-skill inventory.

## Ownership Table

Record only the minimum routing information needed to prevent duplicated workflows.

| Capability | Preferred route | Use when | Boundary |
| --- | --- | --- | --- |
| example-capability | example-skill | The task clearly matches this capability | State whether the route is read-only, may edit local files, or needs separate authorization for external effects |

## Precedence Rules

1. Prefer the narrowest installed capability that fully covers the task.
2. Keep mature third-party workflows independently updateable; do not copy their complete instructions into the evolution framework.
3. Store only trigger routing, precedence, compatibility notes, and external-effect boundaries here.
4. Route durable rule mutation through `skill-evolution-core` and `skill-evolution-router`.
5. Require explicit authorization for login, cookie import, commit, push, merge, publish, deploy, paid purchases, or other remote writes.
6. Never store tokens, account names, private project details, or generated capability inventories in this file.

## Local Customization

Replace the example row after installation. This file is expected to diverge locally and should be reviewed before any customized copy is published.
