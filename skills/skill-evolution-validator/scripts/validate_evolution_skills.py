#!/usr/bin/env python3
"""Validate an installed evolution framework and write local reports."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 fallback; the framework has no dependencies.
    tomllib = None  # type: ignore[assignment]


EXPECTED_SKILLS = {
    "skill-evolution-core",
    "skill-evolution-router",
    "project-rules-router",
    "coding-debug-rules",
    "research-verification",
    "codex-capability-router",
    "skill-evolution-validator",
}
SNAPSHOT_EXCLUDES = {"evolution-trigger-events.jsonl"}
FRAMEWORK_SYNC_EXCLUDES = {
    "skill-evolution-core/references/trigger-candidates.md",
    "skill-evolution-core/references/devolution-ledger.md",
    "skill-evolution-core/references/evolution-change-log.md",
    "skill-evolution-core/references/evolution-trigger-events.jsonl",
    "codex-capability-router/references/external-skill-registry.md",
}
AUTHORITY_HEADINGS = (
    "rule authority and conflict resolution",
    "规则权威与冲突处理",
)
BLANKET_OVERRIDE_PATTERNS = (
    re.compile(r"\b(?:ignore|override)\s+(?:all\s+)?global\b", re.I),
    re.compile(r"\bproject rules?\s+(?:always|unconditionally)\s+(?:win|override)", re.I),
    re.compile(r"忽略(?:所有|全部)?全局"),
    re.compile(r"(?:项目规则|更靠近当前项目的规则).*(?:无条件|始终|一律).*(?:优先|覆盖|为准)"),
    re.compile(r"项目规则无条件覆盖"),
)
NEGATED_OVERRIDE_MARKERS = (
    "do not", "must not", "never", "not blanket", "cannot",
    "不得", "不要", "禁止", "不代表", "不能", "并非",
)
DEFAULT_PROJECT_DOC_MAX_BYTES = 32 * 1024


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_skills_root() -> Path:
    return codex_home() / "skills"


def default_output_dir() -> Path:
    return codex_home() / "skill-evolution-reports"


def default_manifest() -> Path:
    return codex_home() / ".skill-evolution-framework.json"


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return default


def project_doc_max_bytes(config_path: Path) -> tuple[int, str]:
    try:
        text = config_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return DEFAULT_PROJECT_DOC_MAX_BYTES, "default"
    if tomllib is None:
        match = re.search(
            r"(?m)^\s*project_doc_max_bytes\s*=\s*([1-9][0-9]*)\s*(?:#.*)?$",
            text,
        )
        if match:
            return int(match.group(1)), "configured"
        return DEFAULT_PROJECT_DOC_MAX_BYTES, "default"
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return DEFAULT_PROJECT_DOC_MAX_BYTES, "default"
    value = payload.get("project_doc_max_bytes")
    if isinstance(value, int) and value > 0:
        return value, "configured"
    return DEFAULT_PROJECT_DOC_MAX_BYTES, "default"


def check_agents_doc_budget(
    agents_path: Path,
    config_path: Path,
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    limit, source = project_doc_max_bytes(config_path)
    if not agents_path.is_file():
        return {
            "status": "not_configured",
            "path": str(agents_path),
            "size_bytes": 0,
            "limit_bytes": limit,
            "limit_source": source,
            "headroom_bytes": limit,
        }

    size = agents_path.stat().st_size
    headroom = limit - size
    status = "passed"
    if size > limit:
        status = "truncated"
        add_finding(
            findings,
            "P1",
            "Global guidance exceeds the configured loading limit",
            (
                f"{agents_path} is {size} bytes while the {source} "
                f"project_doc_max_bytes limit is {limit}; trailing rules may not load."
            ),
        )
    elif size >= int(limit * 0.9):
        status = "near_limit"
        add_finding(
            findings,
            "P2",
            "Global guidance is close to the configured loading limit",
            (
                f"{agents_path} is {size} bytes with {headroom} bytes remaining "
                "before nested project guidance risks truncation."
            ),
        )
    return {
        "status": status,
        "path": str(agents_path),
        "size_bytes": size,
        "limit_bytes": limit,
        "limit_source": source,
        "headroom_bytes": headroom,
    }


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_snapshot(skills_root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(skills_root.rglob("*")):
        if (
            not path.is_file()
            or "__pycache__" in path.parts
            or path.name in SNAPSHOT_EXCLUDES
            or path.suffix.lower() in {".pyc", ".sqlite", ".sqlite3", ".db"}
        ):
            continue
        snapshot[path.relative_to(skills_root).as_posix()] = hash_file(path)
    return snapshot


def compare_snapshots(
    previous: dict[str, str] | None,
    current: dict[str, str],
) -> dict[str, list[str]]:
    if previous is None:
        return {"added": [], "modified": [], "removed": [], "all": []}
    added = sorted(set(current) - set(previous))
    removed = sorted(set(previous) - set(current))
    modified = sorted(
        path for path in set(current) & set(previous) if current[path] != previous[path]
    )
    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "all": sorted(set(added + modified + removed)),
    }


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}
    values: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def add_finding(
    findings: list[dict[str, str]],
    severity: str,
    title: str,
    detail: str,
) -> None:
    findings.append({"severity": severity, "title": title, "detail": detail})


def _has_authority_heading(text: str) -> bool:
    lowered = text.casefold()
    return any(heading in lowered for heading in AUTHORITY_HEADINGS)


def discover_project_agents(
    project_root: Path | None,
    current_dir: Path | None = None,
) -> list[Path]:
    if project_root is None:
        return []
    root = Path(project_root).resolve()
    current = Path(current_dir).resolve() if current_dir is not None else root
    try:
        relative = current.relative_to(root)
    except ValueError:
        relative = Path()
    directories = [root]
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        directories.append(cursor)
    found: list[Path] = []
    for directory in directories:
        for name in ("AGENTS.override.md", "AGENTS.md"):
            candidate = directory / name
            if candidate.is_file():
                found.append(candidate)
                break
    return found


def _blanket_override_lines(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    conflicts: list[str] = []
    for line in lines:
        stripped = line.strip()
        lowered = stripped.casefold()
        if any(marker in lowered for marker in NEGATED_OVERRIDE_MARKERS):
            continue
        if any(pattern.search(stripped) for pattern in BLANKET_OVERRIDE_PATTERNS):
            conflicts.append(stripped[:240])
    return conflicts


def validate_rule_authority(
    skills_root: Path,
    global_agents: Path | None,
    project_root: Path | None,
    findings: list[dict[str, str]],
    current_dir: Path | None = None,
    config_path: Path | None = None,
) -> dict[str, Any]:
    conflicts: list[dict[str, str]] = []
    checked_files: list[str] = []
    instruction_budget = {
        "status": "not_configured",
        "path": "",
        "size_bytes": 0,
        "limit_bytes": DEFAULT_PROJECT_DOC_MAX_BYTES,
        "limit_source": "default",
        "headroom_bytes": DEFAULT_PROJECT_DOC_MAX_BYTES,
    }
    if global_agents is not None:
        global_path = Path(global_agents).expanduser().resolve()
        budget_config = (
            Path(config_path).expanduser().resolve()
            if config_path is not None
            else global_path.parent / "config.toml"
        )
        instruction_budget = check_agents_doc_budget(
            global_path,
            budget_config,
            findings,
        )
        if global_path.is_file():
            checked_files.append(str(global_path))
            text = global_path.read_text(encoding="utf-8")
            if not _has_authority_heading(text):
                conflicts.append(
                    {
                        "file": str(global_path),
                        "type": "missing_authority_model",
                        "detail": "The guidance does not separate loading/routing order from rule authority.",
                    }
                )
            for line in _blanket_override_lines(global_path):
                conflicts.append(
                    {
                        "file": str(global_path),
                        "type": "blanket_project_precedence",
                        "detail": line,
                    }
                )

    project_router = Path(skills_root) / "project-rules-router" / "SKILL.md"
    if project_router.is_file():
        checked_files.append(str(project_router.resolve()))
        if not _has_authority_heading(project_router.read_text(encoding="utf-8")):
            conflicts.append(
                {
                    "file": str(project_router.resolve()),
                    "type": "router_missing_conflict_branch",
                    "detail": "The project router does not classify policy conflicts separately from stale technical facts.",
                }
            )

    project_agents = discover_project_agents(project_root, current_dir=current_dir)
    for path in project_agents:
        checked_files.append(str(path.resolve()))
        for line in _blanket_override_lines(path):
            conflicts.append(
                {
                    "file": str(path.resolve()),
                    "type": "project_waives_global_boundary",
                    "detail": line,
                }
            )

    if conflicts:
        add_finding(
            findings,
            "P1",
            "Rule authority conflict",
            f"{len(conflicts)} authority or blanket-override issue(s) require evolution review.",
        )
    status = (
        "failed"
        if conflicts or instruction_budget["status"] == "truncated"
        else "passed"
    )
    if not checked_files:
        status = "not_configured"
    return {
        "status": status,
        "checked_files": checked_files,
        "project_agents": [str(path.resolve()) for path in project_agents],
        "conflicts": conflicts,
        "instruction_budget": instruction_budget,
    }


def _framework_file_map(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    if not root.is_dir():
        return files
    for skill_name in sorted(EXPECTED_SKILLS):
        skill_root = root / skill_name
        if not skill_root.is_dir():
            continue
        for path in sorted(skill_root.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or "data" in path.parts:
                continue
            if path.suffix.lower() in {".pyc", ".sqlite", ".sqlite3", ".db", ".jsonl"}:
                continue
            relative = path.relative_to(root).as_posix()
            if relative in FRAMEWORK_SYNC_EXCLUDES:
                continue
            files[relative] = hash_file(path)
    return files


def compare_framework_source(
    skills_root: Path,
    framework_root: Path | None,
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    if framework_root is None:
        return {
            "status": "not_configured",
            "framework_root": "",
            "different_files": [],
            "installed_only": [],
            "source_only": [],
            "excluded_files": sorted(FRAMEWORK_SYNC_EXCLUDES),
        }
    source_root = Path(framework_root).expanduser().resolve()
    if (source_root / "skills").is_dir():
        source_root = source_root / "skills"
    installed_root = Path(skills_root).expanduser().resolve()
    installed = _framework_file_map(installed_root)
    source = _framework_file_map(source_root)
    if not source:
        add_finding(
            findings,
            "P2",
            "Framework source comparison is unavailable",
            f"No managed framework skills were found under {source_root}.",
        )
        return {
            "status": "unavailable",
            "framework_root": str(source_root),
            "different_files": [],
            "installed_only": [],
            "source_only": [],
            "excluded_files": sorted(FRAMEWORK_SYNC_EXCLUDES),
        }
    shared = set(installed) & set(source)
    different = sorted(path for path in shared if installed[path] != source[path])
    installed_only = sorted(set(installed) - set(source))
    source_only = sorted(set(source) - set(installed))
    status = "drift" if different or installed_only or source_only else "aligned"
    if status == "drift":
        add_finding(
            findings,
            "P2",
            "Installed and public framework sources differ",
            (
                f"Review {len(different)} changed, {len(installed_only)} installed-only, "
                f"and {len(source_only)} source-only managed file(s) before publishing."
            ),
        )
    return {
        "status": status,
        "framework_root": str(source_root),
        "different_files": different,
        "installed_only": installed_only,
        "source_only": source_only,
        "excluded_files": sorted(FRAMEWORK_SYNC_EXCLUDES),
    }


def build_repair_handoff(
    findings: list[dict[str, str]],
    authorized: bool,
) -> dict[str, Any]:
    review_only_markers = (
        "no real conversation evidence",
        "sources differ",
        "route outcomes remain unlabeled",
        "trust is not recorded",
    )
    repair_candidates = [
        item for item in findings if item.get("severity") in {"P0", "P1", "P2"}
    ]
    review_only = [
        item
        for item in repair_candidates
        if any(
            marker in str(item.get("title", "")).casefold()
            for marker in review_only_markers
        )
    ]
    actionable = [item for item in repair_candidates if item not in review_only]
    if not authorized:
        status = "not_authorized"
    elif actionable:
        status = "ready"
    else:
        status = "not_needed"
    return {
        "authorized": authorized,
        "status": status,
        "owner": "skill-evolution-core",
        "validator_edits_files": False,
        "actionable_findings": actionable,
        "review_only_findings": review_only,
        "next_step": (
            "Route findings through skill-evolution-core and skill-evolution-router, update the local ledger, then rerun full validation."
            if status == "ready"
            else "Keep the validator report-only until repair is explicitly authorized."
        ),
    }


def validate_structure(
    skills_root: Path,
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    found = {path.name for path in skills_root.iterdir() if path.is_dir()}
    missing = sorted(EXPECTED_SKILLS - found)
    for name in missing:
        add_finding(findings, "P1", "Missing managed skill", name)

    checked = 0
    for name in sorted(EXPECTED_SKILLS & found):
        root = skills_root / name
        skill_path = root / "SKILL.md"
        agent_path = root / "agents" / "openai.yaml"
        if not skill_path.is_file():
            add_finding(findings, "P1", "Missing SKILL.md", name)
            continue
        if not agent_path.is_file():
            add_finding(findings, "P1", "Missing openai.yaml", name)
        metadata = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
        if metadata.get("name") != name:
            add_finding(findings, "P1", "Invalid skill name", name)
        if not metadata.get("description"):
            add_finding(findings, "P1", "Missing skill description", name)
        checked += 1

    core = skills_root / "skill-evolution-core" / "SKILL.md"
    router = skills_root / "skill-evolution-router" / "SKILL.md"
    validator = skills_root / "skill-evolution-validator" / "SKILL.md"
    if core.is_file() and "skill-evolution-validator" not in core.read_text(encoding="utf-8"):
        add_finding(
            findings,
            "P1",
            "Core lacks validator route",
            "Explicit health and release-readiness checks need a separate owner.",
        )
    if router.is_file() and "classif" not in router.read_text(encoding="utf-8").casefold():
        add_finding(findings, "P2", "Router ownership is unclear", router.name)
    if validator.is_file():
        description = parse_frontmatter(validator.read_text(encoding="utf-8")).get(
            "description", ""
        )
        if "do not" not in description.casefold():
            add_finding(
                findings,
                "P2",
                "Validator lacks a negative trigger boundary",
                "Its description should exclude routine skill edits.",
            )
    return {"status": "passed" if not missing else "failed", "checked": checked, "missing": missing}


def load_shortcuts(manifest_path: Path) -> dict[str, str]:
    payload = load_json(manifest_path, {})
    triggers = payload.get("triggers", {}) if isinstance(payload, dict) else {}
    if not isinstance(triggers, dict):
        return {}
    return {
        key: value.strip()
        for key, value in triggers.items()
        if isinstance(value, str) and value.strip()
    }


def run_behavior_regression(
    skills_root: Path,
    manifest_path: Path,
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    validator_root = skills_root / "skill-evolution-validator"
    cases = load_json(validator_root / "references" / "regression-cases.json", [])
    shortcuts = load_shortcuts(manifest_path)
    if not isinstance(cases, list) or not shortcuts.get("evolution") or not shortcuts.get("absorption"):
        add_finding(
            findings,
            "P1",
            "Behavior regression cannot run",
            "A valid case file and installed shortcut manifest are required.",
        )
        return {"status": "failed", "passed": 0, "failed": 0, "cases": []}

    probe = load_module(
        "validator_passive_trigger_probe",
        skills_root
        / "skill-evolution-core"
        / "scripts"
        / "passive_trigger_probe.py",
    )
    shortcut_values = list(shortcuts.values())
    results: list[dict[str, Any]] = []
    passed = 0
    for raw_case in cases:
        if not isinstance(raw_case, dict):
            continue
        text = str(raw_case.get("text", ""))
        text = text.replace("{{evolution}}", shortcuts["evolution"])
        text = text.replace("{{absorption}}", shortcuts["absorption"])
        actual = probe.classify(
            text,
            shortcut_values,
            context_route=str(raw_case.get("context_route", "")),
        )
        ok = (
            actual.get("suggested_route") == raw_case.get("expected_route")
            and actual.get("trigger_level") == raw_case.get("expected_level")
        )
        results.append(
            {
                "id": str(raw_case.get("id", "unnamed")),
                "passed": ok,
                "actual_route": actual.get("suggested_route", ""),
                "actual_level": actual.get("trigger_level", ""),
            }
        )
        passed += int(ok)
    failed = len(results) - passed
    if failed:
        add_finding(
            findings,
            "P1",
            "Behavior regression failed",
            f"{failed} of {len(results)} routing cases failed.",
        )
    return {
        "status": "passed" if failed == 0 else "failed",
        "passed": passed,
        "failed": failed,
        "cases": results,
    }


def parse_latest_ledger_files(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    entries: list[list[str]] = []
    current: list[str] | None = None
    in_files = False
    in_code_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        if stripped.startswith("## "):
            if current is not None:
                entries.append(current)
            current = [] if "entry template" not in stripped.casefold() else None
            in_files = False
            continue
        if current is None:
            continue
        if stripped.casefold() == "- files:":
            in_files = True
            continue
        if in_files and stripped.startswith("- "):
            current.append(stripped[2:].strip().replace("\\", "/"))
        elif in_files and stripped:
            in_files = False
    if current is not None:
        entries.append(current)
    return entries[-1] if entries else []


def reconcile_ledger(
    skills_root: Path,
    changed_files: list[str],
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    ledger = (
        skills_root
        / "skill-evolution-core"
        / "references"
        / "evolution-change-log.md"
    )
    latest_files = parse_latest_ledger_files(ledger)
    unmatched = sorted(set(changed_files) - set(latest_files)) if changed_files else []
    if unmatched:
        add_finding(
            findings,
            "P2",
            "Changed files lack latest ledger mapping",
            f"{len(unmatched)} file(s) are not listed in the latest local entry.",
        )
    return {
        "ledger_present": ledger.is_file(),
        "latest_entry_files": latest_files,
        "unmatched_changed_files": unmatched,
    }


def platform_freshness(
    skills_root: Path,
    now: dt.datetime,
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    path = (
        skills_root
        / "skill-evolution-validator"
        / "references"
        / "platform-freshness.json"
    )
    payload = load_json(path, {})
    try:
        reviewed = dt.date.fromisoformat(str(payload.get("last_reviewed", "")))
    except ValueError:
        reviewed = None
    limit = int(payload.get("freshness_days", 30)) if isinstance(payload, dict) else 30
    age = (now.date() - reviewed).days if reviewed else None
    stale = age is None or age > limit
    if stale:
        add_finding(
            findings,
            "P2",
            "Official platform review is stale",
            "Refresh the Skills and Hooks source review before release decisions.",
        )
    return {
        "last_reviewed": reviewed.isoformat() if reviewed else "",
        "age_days": age,
        "freshness_days": limit,
        "stale": stale,
        "sources": payload.get("sources", []) if isinstance(payload, dict) else [],
    }


def event_summary(skills_root: Path, now: dt.datetime) -> dict[str, Any]:
    script = (
        skills_root
        / "skill-evolution-core"
        / "scripts"
        / "trigger_event_tools.py"
    )
    ledger = (
        skills_root
        / "skill-evolution-core"
        / "references"
        / "evolution-trigger-events.jsonl"
    )
    tools = load_module("validator_trigger_event_tools", script)
    return tools.build_summary(tools.load_events(ledger), now=now)


def inspect_hook_health(
    codex_home_path: Path,
    hook_enabled: bool,
    event_summary: dict[str, Any],
    findings: list[dict[str, str]],
) -> dict[str, Any]:
    home = Path(codex_home_path).expanduser().resolve()
    if not hook_enabled:
        return {
            "status": "disabled",
            "enabled": False,
            "definition_ok": False,
            "wrapper_present": False,
            "trust_present": False,
            "real_hook_events": int(event_summary.get("real_hook_events", 0)),
        }
    hooks_path = home / "hooks.json"
    wrapper = home / "hooks" / "user_prompt_passive_trigger.py"
    config = home / "config.toml"
    hooks = load_json(hooks_path, {})
    rendered = json.dumps(hooks, ensure_ascii=False) if isinstance(hooks, dict) else ""
    definition_ok = "UserPromptSubmit" in rendered and "user_prompt_passive_trigger.py" in rendered
    wrapper_present = wrapper.is_file()
    config_text = ""
    try:
        config_text = config.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        pass
    trust_present = "user_prompt_submit" in config_text.casefold() and "trusted_hash" in config_text.casefold()
    real_events = int(event_summary.get("real_hook_events", 0))
    if not definition_ok or not wrapper_present:
        add_finding(
            findings,
            "P1",
            "Enabled Hook is incomplete",
            "The manifest enables the advisory Hook, but its definition or wrapper is missing.",
        )
    if not trust_present:
        add_finding(
            findings,
            "P2",
            "Hook trust is not recorded",
            "Review and trust the exact UserPromptSubmit definition before relying on it.",
        )
    if real_events == 0:
        add_finding(
            findings,
            "P2",
            "Hook has no real conversation evidence",
            "Definition and smoke tests do not prove that UserPromptSubmit ran in a real task.",
        )
    status = "healthy" if definition_ok and wrapper_present and trust_present and real_events else "configured_no_events" if definition_ok and wrapper_present and trust_present else "incomplete"
    return {
        "status": status,
        "enabled": True,
        "definition_ok": definition_ok,
        "wrapper_present": wrapper_present,
        "trust_present": trust_present,
        "real_hook_events": real_events,
    }


def write_snapshot(path: Path, snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def render_markdown(report: dict[str, Any]) -> str:
    behavior = report["behavior_regression"]
    freshness = report["platform_freshness"]
    events = report["event_summary"]
    ledger = report["ledger_reconciliation"]
    authority = report["rule_authority"]
    budget = authority["instruction_budget"]
    framework = report["framework_sync"]
    repair = report["repair_handoff"]
    hook = report["hook_health"]
    findings = report["findings"]
    lines = [
        "# Evolution Skill Validation Report",
        "",
        f"- Run: `{report['run_id']}`",
        f"- Mode: `{report['mode']}` ({report['mode_basis']})",
        f"- Status: `{report['status']}`",
        f"- Trusted snapshot updated: `{report['snapshot_updated']}`",
        "",
        "## Behavior regression",
        "",
        f"- Status: `{behavior['status']}`",
        f"- Passed: {behavior['passed']}",
        f"- Failed: {behavior['failed']}",
        "",
        "## Event evidence",
        "",
        f"- Real Hook events: {events['real_hook_events']}",
        f"- Smoke-test events: {events['smoke_test_events']}",
        f"- Unlabeled events: {events['unlabeled']}",
        "",
        "## Hook health",
        "",
        f"- Status: `{hook['status']}`",
        f"- Enabled: `{hook['enabled']}`",
        f"- Definition valid: `{hook['definition_ok']}`",
        f"- Trust recorded: `{hook['trust_present']}`",
        "",
        "## Ledger reconciliation",
        "",
        f"- Changed files: {len(report['file_changes']['all'])}",
        f"- Unmatched files: {len(ledger['unmatched_changed_files'])}",
        "",
        "## Rule authority and conflict resolution",
        "",
        f"- Status: `{authority['status']}`",
        f"- Checked files: {len(authority['checked_files'])}",
        f"- Conflicts: {len(authority['conflicts'])}",
        f"- Instruction loading budget: `{budget['status']}`",
        f"- Global guidance bytes: {budget['size_bytes']} / {budget['limit_bytes']}",
        "",
        "## Installed versus public framework",
        "",
        f"- Status: `{framework['status']}`",
        f"- Different files: {len(framework['different_files'])}",
        f"- Installed-only files: {len(framework['installed_only'])}",
        f"- Source-only files: {len(framework['source_only'])}",
        "",
        "## Platform freshness",
        "",
        f"- Last reviewed: `{freshness['last_reviewed'] or 'unknown'}`",
        f"- Age days: {freshness['age_days'] if freshness['age_days'] is not None else 'unknown'}",
        f"- Stale: `{freshness['stale']}`",
        "",
        "## Repair handoff",
        "",
        f"- Authorized: `{repair['authorized']}`",
        f"- Status: `{repair['status']}`",
        f"- Owner: `{repair['owner']}`",
        f"- Validator edits files: `{repair['validator_edits_files']}`",
        f"- Actionable findings: {len(repair['actionable_findings'])}",
        f"- Review-only findings: {len(repair['review_only_findings'])}",
        "",
        "## Findings",
        "",
    ]
    if findings:
        for finding in findings:
            lines.append(
                f"- `{finding['severity']}` {finding['title']}: {finding['detail']}"
            )
    else:
        lines.append("- No findings.")
    lines.extend(
        [
            "",
            "Generated locally. Event prompt text is not copied into this report.",
            "",
        ]
    )
    return "\n".join(lines)


def run_validation(
    skills_root: Path,
    output_dir: Path,
    manifest_path: Path,
    mode: str = "auto",
    now: dt.datetime | None = None,
    global_agents: Path | None = None,
    project_root: Path | None = None,
    framework_root: Path | None = None,
    repair_authorized: bool = False,
    codex_home_path: Path | None = None,
    project_cwd: Path | None = None,
) -> dict[str, Any]:
    skills_root = Path(skills_root).resolve()
    output_dir = Path(output_dir).resolve()
    manifest_path = Path(manifest_path).resolve()
    current_time = now or dt.datetime.now(dt.timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=dt.timezone.utc)
    else:
        current_time = current_time.astimezone(dt.timezone.utc)

    state_dir = output_dir / "state"
    snapshot_path = state_dir / "evolution-file-snapshot.json"
    last_run_path = state_dir / "last-run.json"
    previous_snapshot = load_json(snapshot_path, None)
    if not isinstance(previous_snapshot, dict):
        previous_snapshot = None
    previous_run = load_json(last_run_path, {})
    if not isinstance(previous_run, dict):
        previous_run = {}
    snapshot = current_snapshot(skills_root)
    changes = compare_snapshots(previous_snapshot, snapshot)
    selected_mode = mode
    if mode == "auto":
        if previous_snapshot is None:
            selected_mode = "full"
            mode_basis = "first run without a trusted snapshot"
        elif previous_run.get("status") == "failed":
            selected_mode = "full"
            mode_basis = "previous full validation still failed"
        elif changes["all"]:
            selected_mode = "full"
            mode_basis = "managed skill files changed since the trusted snapshot"
        else:
            selected_mode = "fast"
            mode_basis = "existing logs and unchanged trusted snapshot"
    elif mode == "fast":
        mode_basis = "explicit log-based fast validation"
    else:
        mode_basis = "explicit full validation"
    if selected_mode not in {"fast", "full"}:
        raise ValueError(f"Unsupported validation mode: {mode}")

    findings: list[dict[str, str]] = []
    if selected_mode == "fast" and changes["all"]:
        add_finding(
            findings,
            "P2",
            "Fast mode skipped changed skill files",
            "Run full mode before accepting a new trusted snapshot.",
        )
    if selected_mode == "full":
        structure = validate_structure(skills_root, findings)
        behavior = run_behavior_regression(skills_root, manifest_path, findings)
        authority = validate_rule_authority(
            skills_root=skills_root,
            global_agents=global_agents,
            project_root=project_root,
            findings=findings,
            current_dir=project_cwd,
            config_path=(codex_home_path or skills_root.parent) / "config.toml",
        )
        framework = compare_framework_source(
            skills_root=skills_root,
            framework_root=framework_root,
            findings=findings,
        )
    else:
        structure = {"status": "not_run", "checked": 0, "missing": []}
        behavior = {"status": "not_run", "passed": 0, "failed": 0, "cases": []}
        authority = {
            "status": "not_run",
            "checked_files": [],
            "project_agents": [],
            "conflicts": [],
            "instruction_budget": {
                "status": "not_run",
                "path": "",
                "size_bytes": 0,
                "limit_bytes": DEFAULT_PROJECT_DOC_MAX_BYTES,
                "limit_source": "default",
                "headroom_bytes": DEFAULT_PROJECT_DOC_MAX_BYTES,
            },
        }
        framework = {
            "status": "not_run",
            "framework_root": "",
            "different_files": [],
            "installed_only": [],
            "source_only": [],
            "excluded_files": sorted(FRAMEWORK_SYNC_EXCLUDES),
        }

    ledger = reconcile_ledger(skills_root, changes["all"], findings)
    freshness = platform_freshness(skills_root, current_time, findings)
    events = event_summary(skills_root, current_time)
    if events["unlabeled"]:
        add_finding(
            findings,
            "P2",
            "Route outcomes remain unlabeled",
            f"{events['unlabeled']} local event(s) need actual-route review.",
        )

    manifest_payload = load_json(manifest_path, {})
    passive_hook = manifest_payload.get("passive_hook", {}) if isinstance(manifest_payload, dict) else {}
    hook_enabled = isinstance(passive_hook, dict) and passive_hook.get("enabled") is True
    hook = inspect_hook_health(
        codex_home_path=codex_home_path or skills_root.parent,
        hook_enabled=hook_enabled,
        event_summary=events,
        findings=findings,
    )

    repair_handoff = build_repair_handoff(findings, repair_authorized)

    blocking = any(item["severity"] in {"P0", "P1"} for item in findings)
    snapshot_updated = not blocking and not (
        selected_mode == "fast" and bool(changes["all"])
    )
    run_id = current_time.strftime("%Y%m%dT%H%M%SZ") + f"-{selected_mode}"
    report_path = output_dir / f"{run_id}-evolution-validation.md"
    json_path = output_dir / f"{run_id}-evolution-validation.json"
    snapshot_archive_path = state_dir / "snapshots" / f"{run_id}.json"
    report: dict[str, Any] = {
        "run_id": run_id,
        "mode": selected_mode,
        "mode_basis": mode_basis,
        "status": "failed" if blocking else "passed_with_notes" if findings else "passed",
        "structure": structure,
        "behavior_regression": behavior,
        "event_summary": events,
        "hook_health": hook,
        "file_changes": changes,
        "ledger_reconciliation": ledger,
        "rule_authority": authority,
        "framework_sync": framework,
        "repair_handoff": repair_handoff,
        "platform_freshness": freshness,
        "findings": findings,
        "report_path": str(report_path),
        "json_path": str(json_path),
        "snapshot_path": str(snapshot_path),
        "snapshot_archive_path": str(snapshot_archive_path),
        "snapshot_updated": snapshot_updated,
        "last_run_path": str(last_run_path),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if snapshot_updated:
        write_snapshot(snapshot_path, snapshot)
        write_snapshot(snapshot_archive_path, snapshot)
    write_snapshot(
        last_run_path,
        {
            "run_id": report["run_id"],
            "mode": report["mode"],
            "status": report["status"],
            "snapshot_updated": snapshot_updated,
        },
    )
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the evolution skill system.")
    parser.add_argument("--mode", choices=("auto", "fast", "full"), default="auto")
    parser.add_argument("--skills-root", type=Path, default=default_skills_root())
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    parser.add_argument("--manifest", type=Path, default=default_manifest())
    parser.add_argument(
        "--global-agents",
        type=Path,
        default=codex_home() / "AGENTS.md",
        help="Global guidance file to include in rule-authority checks.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Current repository root whose active AGENTS.md should be checked.",
    )
    parser.add_argument(
        "--framework-root",
        type=Path,
        help="Optional public framework checkout used for installed/source drift reporting.",
    )
    parser.add_argument(
        "--repair-authorized",
        action="store_true",
        help="Emit a repair handoff to skill-evolution-core; the validator still does not edit files.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = run_validation(
        skills_root=args.skills_root,
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        mode=args.mode,
        global_agents=args.global_agents,
        project_root=args.project_root,
        framework_root=args.framework_root,
        repair_authorized=args.repair_authorized,
        codex_home_path=codex_home(),
        project_cwd=Path.cwd(),
    )
    print(f"status={report['status']}")
    print(f"mode={report['mode']}")
    print(f"report={report['report_path']}")
    print(f"json={report['json_path']}")
    print(f"snapshot={report['snapshot_path']}")
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
