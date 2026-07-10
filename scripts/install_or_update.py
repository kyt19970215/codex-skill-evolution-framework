#!/usr/bin/env python3
"""Install or safely update the public skill evolution framework."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


MANAGED_SKILLS = (
    "skill-evolution-core",
    "skill-evolution-router",
    "project-rules-router",
    "coding-debug-rules",
    "research-verification",
    "codex-capability-router",
    "skill-evolution-validator",
)
MANIFEST_NAME = ".skill-evolution-framework.json"
PENDING_DIRECTORY = ".skill-evolution-updates"
PROTECTED_FILES = frozenset(
    {
        "skills/skill-evolution-core/references/trigger-candidates.md",
        "skills/skill-evolution-core/references/devolution-ledger.md",
        "skills/skill-evolution-core/references/evolution-change-log.md",
        "skills/codex-capability-router/references/external-skill-registry.md",
    }
)
IGNORED_PARTS = {".git", "__pycache__", "data"}
IGNORED_SUFFIXES = {".pyc", ".sqlite", ".sqlite3", ".db"}


@dataclass
class UpdateResult:
    first_install: bool
    hook_configured: bool = False
    installed: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    preserved: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_trigger(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} trigger is required for first installation")
    cleaned = value.strip()
    if any(ord(character) < 32 for character in cleaned):
        raise ValueError(f"{label} trigger cannot contain control characters")
    if len(cleaned) > 100:
        raise ValueError(f"{label} trigger must be 100 characters or fewer")
    return cleaned


def _collect_first_install_triggers(
    evolution_trigger: str | None,
    absorption_trigger: str | None,
    non_interactive: bool,
) -> tuple[str, str]:
    if not non_interactive:
        if evolution_trigger is None:
            evolution_trigger = input("Choose the evolution shortcut: ")
        if absorption_trigger is None:
            absorption_trigger = input("Choose the absorption shortcut: ")
    evolution = _validate_trigger(evolution_trigger, "Evolution")
    absorption = _validate_trigger(absorption_trigger, "Absorption")
    if evolution.casefold() == absorption.casefold():
        raise ValueError("Evolution and absorption triggers must be different")
    return evolution, absorption


def _load_manifest(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read installation manifest: {path}") from exc
    if payload.get("schema_version") != 1:
        raise ValueError(f"Unsupported installation manifest schema: {path}")
    if not isinstance(payload.get("files"), dict):
        raise ValueError(f"Invalid installation manifest: {path}")
    return payload


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _is_installable(path: Path, skill_root: Path) -> bool:
    relative = path.relative_to(skill_root)
    return (
        path.is_file()
        and not any(part in IGNORED_PARTS for part in relative.parts)
        and path.suffix.lower() not in IGNORED_SUFFIXES
    )


def _iter_source_files(source_root: Path, include_passive_hook: bool = False):
    skills_root = source_root / "skills"
    for skill_name in MANAGED_SKILLS:
        skill_root = skills_root / skill_name
        if not skill_root.is_dir():
            raise FileNotFoundError(f"Managed skill is missing: {skill_root}")
        for source in sorted(skill_root.rglob("*")):
            if _is_installable(source, skill_root):
                relative = Path("skills") / skill_name / source.relative_to(skill_root)
                yield source, relative
    if include_passive_hook:
        hook = source_root / "hooks" / "user_prompt_passive_trigger.py"
        if not hook.is_file():
            raise FileNotFoundError(f"Passive hook is missing: {hook}")
        yield hook, Path("hooks") / hook.name


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _stage_pending(source: Path, codex_home: Path, relative: Path) -> None:
    _copy_file(source, codex_home / PENDING_DIRECTORY / relative)


def _clear_pending(codex_home: Path, relative: Path) -> None:
    pending = codex_home / PENDING_DIRECTORY / relative
    if pending.is_file():
        pending.unlink()


def _markdown_code(value: str) -> str:
    return value.replace("`", "\\`")


def _entry_skill_text(evolution: str, absorption: str) -> str:
    evolution_code = _markdown_code(evolution)
    absorption_code = _markdown_code(absorption)
    description = (
        f"Local shortcut entry for skill evolution. Use when the user enters "
        f"{evolution!r} for evolution or {absorption!r} for capability absorption."
    )
    return (
        "---\n"
        "name: skill-evolution-entry\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---\n\n"
        "# Local Skill Evolution Entry\n\n"
        "This file belongs to the local installation and is never overwritten by framework updates.\n\n"
        "## Shortcuts\n\n"
        f"- When the user enters `{evolution_code}`, invoke `$skill-evolution-core` and run the total skill-evolution workflow.\n"
        f"- When the user enters `{absorption_code}`, invoke `$skill-evolution-core` and run the capability-absorption workflow.\n"
        "- Use the immediately preceding conversation to resolve context before asking the user to repeat it.\n"
    )


def _entry_agent_text(evolution: str, absorption: str) -> str:
    display_name = "Local Skill Evolution Entry"
    short_description = f"Shortcuts: {evolution} / {absorption}"
    default_prompt = (
        "Use $skill-evolution-entry to route the configured local shortcut to "
        "$skill-evolution-core."
    )
    return (
        "interface:\n"
        f"  display_name: {json.dumps(display_name, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short_description, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(default_prompt, ensure_ascii=False)}\n"
    )


def _create_local_entry(codex_home: Path, evolution: str, absorption: str) -> bool:
    entry_root = codex_home / "skills" / "skill-evolution-entry"
    skill_path = entry_root / "SKILL.md"
    agent_path = entry_root / "agents" / "openai.yaml"
    if skill_path.exists() or agent_path.exists():
        return False
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(_entry_skill_text(evolution, absorption), encoding="utf-8")
    agent_path.write_text(_entry_agent_text(evolution, absorption), encoding="utf-8")
    return True


def _hook_command(python_executable: str, hook_path: Path) -> str:
    escaped_python = python_executable.replace('"', '\\"')
    escaped_hook = str(hook_path).replace('"', '\\"')
    return f'"{escaped_python}" "{escaped_hook}"'


def _without_passive_handler(block: object) -> object | None:
    if not isinstance(block, dict):
        return block
    handlers = block.get("hooks")
    if not isinstance(handlers, list):
        return block
    retained = [
        handler
        for handler in handlers
        if not (
            isinstance(handler, dict)
            and "user_prompt_passive_trigger.py" in str(handler.get("command", ""))
        )
    ]
    if not retained:
        return None
    updated = dict(block)
    updated["hooks"] = retained
    return updated


def _load_hook_configuration(codex_home: Path) -> dict[str, object]:
    config_path = codex_home / "hooks.json"
    if config_path.is_file():
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot safely update hook configuration: {config_path}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Hook configuration must be a JSON object: {config_path}")
    else:
        payload = {}
    hooks = payload.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"Invalid hooks table: {config_path}")
    existing = hooks.get("UserPromptSubmit", [])
    if not isinstance(existing, list):
        raise ValueError(f"Invalid UserPromptSubmit hook list: {config_path}")
    return payload


def _configure_passive_hook(
    codex_home: Path,
    python_executable: str,
) -> bool:
    config_path = codex_home / "hooks.json"
    payload = _load_hook_configuration(codex_home)
    hooks = payload["hooks"]
    if not isinstance(hooks, dict):
        raise ValueError(f"Invalid hooks table: {config_path}")
    existing = hooks.get("UserPromptSubmit", [])
    if not isinstance(existing, list):
        raise ValueError(f"Invalid UserPromptSubmit hook list: {config_path}")

    retained = []
    for block in existing:
        updated = _without_passive_handler(block)
        if updated is not None:
            retained.append(updated)
    retained.append(
        {
            "hooks": [
                {
                    "type": "command",
                    "command": _hook_command(
                        python_executable,
                        codex_home / "hooks" / "user_prompt_passive_trigger.py",
                    ),
                    "timeout": 5,
                }
            ]
        }
    )
    hooks["UserPromptSubmit"] = retained

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if config_path.is_file() and config_path.read_text(encoding="utf-8") == rendered:
        return True
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.is_file():
        backup = codex_home / ".skill-evolution-backups" / "hooks.json"
        if not backup.exists():
            _copy_file(config_path, backup)
    temporary = config_path.with_suffix(config_path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(config_path)
    return True


def _reject_inline_hook_configuration(codex_home: Path) -> None:
    config_path = codex_home / "config.toml"
    if not config_path.is_file():
        return
    try:
        text = config_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Cannot inspect Codex configuration: {config_path}") from exc
    if re.search(r"(?m)^\s*\[\[?hooks(?:[.\]])", text):
        raise ValueError(
            "An inline Hook configuration already exists in config.toml; "
            "install the advisory Hook manually in that representation instead of "
            "mixing it with hooks.json"
        )


def install_or_update(
    source_root: Path,
    codex_home: Path,
    evolution_trigger: str | None = None,
    absorption_trigger: str | None = None,
    non_interactive: bool = False,
    enable_passive_hook: bool = False,
    python_executable: str | None = None,
) -> UpdateResult:
    source_root = Path(source_root).resolve()
    codex_home = Path(codex_home).expanduser().resolve()
    manifest_path = codex_home / MANIFEST_NAME
    previous_manifest = _load_manifest(manifest_path)
    first_install = previous_manifest is None

    if first_install:
        evolution, absorption = _collect_first_install_triggers(
            evolution_trigger, absorption_trigger, non_interactive
        )
    else:
        triggers = previous_manifest.get("triggers")
        if not isinstance(triggers, dict):
            raise ValueError(f"Invalid installation manifest: {manifest_path}")
        evolution = _validate_trigger(triggers.get("evolution"), "Evolution")
        absorption = _validate_trigger(triggers.get("absorption"), "Absorption")
        requested = (evolution_trigger, absorption_trigger)
        saved = (evolution, absorption)
        for requested_value, saved_value in zip(requested, saved):
            if requested_value is not None and requested_value.strip() != saved_value:
                raise ValueError(
                    "Triggers are local configuration and are preserved during updates"
                )

    previous_files = previous_manifest.get("files", {}) if previous_manifest else {}
    previous_hook = previous_manifest.get("passive_hook", {}) if previous_manifest else {}
    previous_hook_enabled = (
        isinstance(previous_hook, dict) and previous_hook.get("enabled") is True
    )
    passive_hook_enabled = bool(enable_passive_hook or previous_hook_enabled)
    if passive_hook_enabled:
        _reject_inline_hook_configuration(codex_home)
        _load_hook_configuration(codex_home)
    result = UpdateResult(first_install=first_install)
    next_files: dict[str, dict[str, str | None]] = {}

    for source, relative_path in _iter_source_files(
        source_root, include_passive_hook=passive_hook_enabled
    ):
        relative = relative_path.as_posix()
        destination = codex_home / relative_path
        upstream_hash = _hash_file(source)
        previous_record = previous_files.get(relative)
        installed_hash = None
        if isinstance(previous_record, dict):
            candidate_hash = previous_record.get("installed_hash")
            if isinstance(candidate_hash, str):
                installed_hash = candidate_hash

        if not destination.exists():
            _copy_file(source, destination)
            installed_hash = upstream_hash
            result.installed.append(relative)
            _clear_pending(codex_home, relative_path)
        else:
            current_hash = _hash_file(destination)
            if relative in PROTECTED_FILES:
                if current_hash != upstream_hash:
                    _stage_pending(source, codex_home, relative_path)
                    result.preserved.append(relative)
                else:
                    installed_hash = upstream_hash
                    result.unchanged.append(relative)
                    _clear_pending(codex_home, relative_path)
            elif current_hash == upstream_hash:
                installed_hash = upstream_hash
                result.unchanged.append(relative)
                _clear_pending(codex_home, relative_path)
            elif installed_hash is not None and current_hash == installed_hash:
                _copy_file(source, destination)
                installed_hash = upstream_hash
                result.updated.append(relative)
                _clear_pending(codex_home, relative_path)
            else:
                _stage_pending(source, codex_home, relative_path)
                result.preserved.append(relative)

        next_files[relative] = {
            "installed_hash": installed_hash,
            "upstream_hash": upstream_hash,
        }

    _create_local_entry(codex_home, evolution, absorption)
    hook_relative = "hooks/user_prompt_passive_trigger.py"
    first_enable_conflict = (
        passive_hook_enabled
        and not previous_hook_enabled
        and hook_relative in result.preserved
    )
    effective_hook_enabled = passive_hook_enabled and not first_enable_conflict
    if effective_hook_enabled:
        result.hook_configured = _configure_passive_hook(
            codex_home,
            python_executable or sys.executable,
        )
    manifest = {
        "schema_version": 1,
        "triggers": {"evolution": evolution, "absorption": absorption},
        "managed_skills": list(MANAGED_SKILLS),
        "passive_hook": {"enabled": effective_hook_enabled},
        "files": next_files,
    }
    _write_manifest(manifest_path, manifest)
    return result


def _default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Install the framework with user-selected shortcuts, or safely update an "
            "existing installation without overwriting local evolution."
        )
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Framework repository root (defaults to this checkout).",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=_default_codex_home(),
        help="Codex home directory (defaults to CODEX_HOME or ~/.codex).",
    )
    parser.add_argument("--evolution-trigger", help="Shortcut chosen on first install.")
    parser.add_argument("--absorption-trigger", help="Shortcut chosen on first install.")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Do not prompt. Both shortcuts are required on first install.",
    )
    parser.add_argument(
        "--enable-passive-hook",
        action="store_true",
        help=(
            "Install and configure the optional advisory UserPromptSubmit hook. "
            "Review and trust it with /hooks after installation."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = install_or_update(
            source_root=args.source_root,
            codex_home=args.codex_home,
            evolution_trigger=args.evolution_trigger,
            absorption_trigger=args.absorption_trigger,
            non_interactive=args.non_interactive,
            enable_passive_hook=args.enable_passive_hook,
        )
    except (FileNotFoundError, ValueError, OSError) as exc:
        parser.error(str(exc))

    action = "First installation complete" if result.first_install else "Update complete"
    print(action)
    print(f"Installed: {len(result.installed)}")
    print(f"Updated: {len(result.updated)}")
    print(f"Preserved local files: {len(result.preserved)}")
    print(f"Passive advisory hook configured: {result.hook_configured}")
    if result.preserved:
        print(f"Review incoming copies under: {args.codex_home / PENDING_DIRECTORY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
