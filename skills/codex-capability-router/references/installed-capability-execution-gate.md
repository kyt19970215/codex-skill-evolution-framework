# Installed Capability Execution Gate

Use this gate after an installed Skill, plugin, App, MCP tool, or specialist
workflow is selected. Its purpose is to prevent false capability use: naming or
reading a capability while the deliverable is still produced through a weaker
generic path.

## Trigger

The gate is mandatory when either condition is true:

1. The user explicitly names an installed capability.
2. The task's dominant artifact or specialist workflow directly matches an
   installed capability description and using it can materially improve
   quality, fidelity, correctness, or rework cost.

An adjacent or merely interesting capability does not trigger this gate.
Installation does not authorize login, payment, upload, remote writes,
publishing, deployment, commits, destructive actions, or access to private
account state.

## Source Ladder

Before substantial execution, read only the directly relevant layers:

1. The exact installed capability entrypoint for the current version.
2. References marked required, must, always, hard gate, or non-negotiable for
   the current task shape.
3. Installed-version official examples, templates, catalogs, components,
   assets, packages, or source modules that match the requested result.
4. Current official documentation, release notes, and source when behavior is
   version-sensitive or local evidence is incomplete.
5. Existing project integration patterns needed to connect the native path.

Do not read every reference or every installed capability. Reuse the inspected
source set throughout one coherent task unless the task or version changes.

## Native-Use Contract

For each material requirement, identify the capability owner, native mechanism,
integration point, and verification method. This mapping may remain in working
notes; do not create a document only to prove compliance.

A selected capability counts as used only when at least one applicable native
path enters the execution chain:

- its CLI, MCP tool, App action, API, or runtime is invoked;
- an official module, block, component, template, example, asset, or generated
  artifact is integrated; or
- for a guidance-only Skill, its required workflow gate, review, or validator
  materially shapes and checks the deliverable.

Reading a Skill and hand-writing an approximate substitute does not count.
Mentioning a plugin or borrowing its vocabulary does not count. Prefer the
native path when it satisfies the approved goal and constraints.

When several capabilities are genuinely needed, assign one owner to each phase
and pass a concrete artifact or contract between them. Each claimed participant
still needs its own use evidence.

## Execution Notice

At the first meaningful execution node, state briefly:

- the selected capability and its role;
- the exact entrypoint or native resource being used;
- what remains owned by the project or another capability; and
- any authorization, account, cost, compatibility, or runtime boundary.

This is a progress notice, not another approval gate when the approved result
and side-effect boundary are unchanged.

## Fallback

Fallback is allowed only when current evidence shows that the native path is
irrelevant, unavailable, incompatible, broken for the installed version,
blocked by an unapproved side effect, or unable to meet the approved result.

Before falling back:

1. Record the concrete failure or mismatch.
2. Check the smallest relevant official troubleshooting or alternative path.
3. Choose the nearest compatible fallback that preserves the intended quality.
4. Ask the user only when the fallback changes result, experience, cost, scope,
   authorization, or long-term direction.

## Completion Evidence

The final report should state compactly:

- the capability actually used;
- the official or native resource consumed;
- the concrete artifact, command, module, or integration produced;
- capability-specific validation performed; and
- any justified fallback or unverified boundary.

Never infer successful capability use from a compiled project alone. Verify the
selected capability's meaningful output, then apply the project's normal final
acceptance checks.
