#!/usr/bin/env python3
"""Validate an installed evolution framework and write local reports."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any


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
        "## Ledger reconciliation",
        "",
        f"- Changed files: {len(report['file_changes']['all'])}",
        f"- Unmatched files: {len(ledger['unmatched_changed_files'])}",
        "",
        "## Platform freshness",
        "",
        f"- Last reviewed: `{freshness['last_reviewed'] or 'unknown'}`",
        f"- Age days: {freshness['age_days'] if freshness['age_days'] is not None else 'unknown'}",
        f"- Stale: `{freshness['stale']}`",
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
    else:
        structure = {"status": "not_run", "checked": 0, "missing": []}
        behavior = {"status": "not_run", "passed": 0, "failed": 0, "cases": []}

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

    blocking = any(item["severity"] in {"P0", "P1"} for item in findings)
    snapshot_updated = not blocking and not (
        selected_mode == "fast" and bool(changes["all"])
    )
    run_id = current_time.strftime("%Y%m%dT%H%M%SZ") + f"-{selected_mode}"
    report_path = output_dir / f"{run_id}-evolution-validation.md"
    json_path = output_dir / f"{run_id}-evolution-validation.json"
    report: dict[str, Any] = {
        "run_id": run_id,
        "mode": selected_mode,
        "mode_basis": mode_basis,
        "status": "failed" if blocking else "passed_with_notes" if findings else "passed",
        "structure": structure,
        "behavior_regression": behavior,
        "event_summary": events,
        "file_changes": changes,
        "ledger_reconciliation": ledger,
        "platform_freshness": freshness,
        "findings": findings,
        "report_path": str(report_path),
        "json_path": str(json_path),
        "snapshot_path": str(snapshot_path),
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
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = run_validation(
        skills_root=args.skills_root,
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        mode=args.mode,
    )
    print(f"status={report['status']}")
    print(f"mode={report['mode']}")
    print(f"report={report['report_path']}")
    print(f"json={report['json_path']}")
    print(f"snapshot={report['snapshot_path']}")
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
