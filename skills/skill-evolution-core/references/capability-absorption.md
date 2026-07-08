# Capability Absorption

Use this process when a mature external skill overlaps the user's existing skill system.

## Configured Trigger

- Treat the configured absorption shortcut as explicit authorization to install and locally integrate the target identified in the immediately preceding context, including its ordinary required global dependencies.
- If the target is clear, proceed without asking the user to repeat it. If no target can be identified, ask one concise question naming the missing target.
- The shortcut does not authorize login, cookie import, remote publishing, commit, push, merge, deployment, paid purchases, or other materially separate external effects.

## Decide Before Copying

Classify each overlapping part:

- **Absorb:** a short, durable principle that improves routing, validation, or failure prevention across skills.
- **Delegate:** a mature, substantial workflow with its own scripts, templates, release cycle, or specialist role. Keep it independent and route to it.
- **Replace:** a local rule is clearly obsolete, narrower, or contradicted by verified current behavior. Remove or rewrite it only after evidence and validation.
- **Ignore:** branding, examples, duplicated prose, tool-specific ceremony, or behavior that conflicts with user safety boundaries.

Do not paste a complete upstream workflow into an evolution skill. The upstream package remains the source of truth; the local system owns only trigger routing, precedence, safety boundaries, and concise reusable lessons.

Absorption must include a lightweight devolution/reconciliation pass:

- Merge useful overlap into the existing owner paragraph or bullet instead of appending a parallel section.
- Remove or rewrite a superseded duplicate only after confirming the original intent is still preserved.
- Treat replacement, downgrade, or trigger-strength reduction as a behavior change unless tests and the user confirm it should change.
- Escalate to the full devolution workflow only when overlap, conflict, bloat, or progress blockage is real; do not turn every absorption into a heavy cleanup.

## Post-Install Discovery Rule

After installing, enabling, or updating the selected capability, rerun discovery from the actual installed state before editing durable routing or skill behavior. This is part of the same absorption run; do not ask the user to trigger absorption again.

Capture only the evidence needed for correct routing:

- actual executable, skill, plugin, MCP, app, or hook identifiers
- version, path, PATH or registry visibility, and clean-shell discovery
- help output, schema, manifest, metadata, commands, supported formats, and required environment variables
- first-run warnings, missing optional dependencies, permission prompts, or unavailable subfeatures
- minimal real invocation or load result, using nonsensitive sample data when possible

If installed behavior differs from the pre-install assumption, prefer verified installed behavior. Do not write or keep routing that points to an unusable command, stale capability name, missing app, unavailable plugin, or unverified cloud/remote feature. Record unresolved subfeatures as residual risk instead of presenting the capability as fully absorbed.

## Integration Workflow

1. Resolve the target's canonical name, official source, current version or revision, license, trust level, supported hosts, permissions, external effects, update method, and required runtime chain.
2. Verify public capabilities against official documentation, releases, repository files, and current local evidence. Treat videos and community summaries as discovery leads.
3. Install the selected target and its complete ordinary global dependency closure under the rule below.
4. Rerun post-install discovery from the actual installed state before writing durable routing or skill behavior.
5. Compare the verified installed capability with `AGENTS.md`, project rules, global reusable skills, and the capability registry; classify each overlap as absorb, delegate, replace, or ignore.
6. Run the lightweight reconciliation pass: merge absorbed principles into the current owner text, identify obsolete duplicates, and preserve final semantics unless the user approved a behavior change.
7. Extract only principles that remain useful after removing the upstream name. Keep mature scripts, templates, role workflows, and large instructions independently updateable.
8. Add task-to-skill routing, precedence, compatibility adapters, and external-effect boundaries to `codex-capability-router`.
9. Keep lasting personal rule edits under `skill-evolution-core` and `skill-evolution-router`; upstream learn or skillify functions may produce proposals only.
10. Validate changed local skills, UI metadata, clean-shell dependency discovery, imports or loads, a minimal real invocation, representative routing queries, and any semantic/effect-preservation claim. Report installed, post-install discovered, absorbed, delegated, replaced, ignored, routed, verified, and unresolved parts.

## Current Ownership Boundaries

- `skill-evolution-core` and `skill-evolution-router` exclusively own durable rule capture and skill mutation; the local entry owns the chosen shortcut aliases and routes both workflows to `skill-evolution-core`.
- `codex-capability-router` owns automatic selection of installed mature skills.
- `coding-debug-rules` owns first-pass local environment and failure triage; specialist debugging skills may take over after that evidence pass.
- Product Design `get-context` owns the design brief gate; visual-style skills refine the selected direction afterward.
- Artifact plugins for documents, spreadsheets, presentations, and PDFs remain preferred over overlapping general-purpose generators.
- Upstream learn/skillify/writing-skills commands may propose lessons, but they do not directly write the user's durable skill system; route proposals through evolution.

## Global Dependency-Closure Rule

When the user explicitly asks to install a file, tool, plugin, skill, application, or capability, that authorization also covers all runtime environments and supporting libraries required for it to work. Node.js, npm, npx, and Bun are examples only, not a closed list. The dependency closure may include package managers, language runtimes, SDKs, compilers, browser engines, command-line tools, native libraries, and required system components.

- Install required dependencies globally for the user account rather than leaving project-local packages as the only working environment. Use machine-wide installation only when the dependency requires it or the user explicitly requests it.
- Determine the required dependency chain from official manifests or documentation. Do not treat unrelated optional integrations as required dependencies.
- Do not ask for separate confirmation for ordinary required dependencies after the main installation has been authorized.
- Prefer official sources, verify checksums or signatures when available, and test versions, PATH or library discovery, imports/loads, and a minimal real invocation from a clean shell.
- Stop and report when a dependency introduces a distinct license purchase, account authorization, security-sensitive driver, unavoidable reboot, destructive replacement, or incompatible global version. Those are new boundaries, not ordinary dependency closure.

This reference records the evolution classification; `~/.codex/AGENTS.md` is the always-on source of truth.
