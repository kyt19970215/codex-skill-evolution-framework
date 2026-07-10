#!/usr/bin/env python3
"""Non-blocking UserPromptSubmit hook for advisory route observation."""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


TEXT_KEYS = {
    "prompt",
    "user_prompt",
    "userPrompt",
    "input",
    "text",
    "message",
    "content",
    "query",
}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def load_probe() -> Any:
    path = (
        codex_home()
        / "skills"
        / "skill-evolution-core"
        / "scripts"
        / "passive_trigger_probe.py"
    )
    spec = importlib.util.spec_from_file_location("passive_trigger_probe", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load passive trigger probe: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_stdin_text() -> str:
    raw = sys.stdin.buffer.read()
    if not raw:
        return ""
    for encoding in ("utf-8-sig", "utf-8", "mbcs"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def collect_strings(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        if value.strip():
            found.append(value.strip())
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_strings(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in TEXT_KEYS or key in {"messages", "items", "parts"}:
                found.extend(collect_strings(item))
    return found


def parse_hook_payload(raw_text: str) -> dict[str, str]:
    metadata = {
        "prompt": "",
        "session_id": "",
        "turn_id": "",
        "cwd": "",
        "transcript_path": "",
    }
    stripped = raw_text.strip()
    if not stripped:
        return metadata
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        metadata["prompt"] = stripped
        return metadata
    if not isinstance(payload, dict):
        return metadata
    for key in metadata:
        value = payload.get(key)
        if isinstance(value, str):
            metadata[key] = value.strip()
    if not metadata["prompt"]:
        metadata["prompt"] = max(collect_strings(payload), key=len, default="")
    return metadata


def short_hash(value: str, length: int = 16) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def state_key(session_id: str) -> str:
    return short_hash(session_id, 20)


def load_shortcuts(probe: Any) -> list[str]:
    manifest = probe.load_manifest_triggers(probe.default_manifest())
    return [
        value.strip()
        for value in manifest.values()
        if isinstance(value, str) and value.strip()
    ]


def state_path() -> Path:
    return codex_home() / "hooks" / "state" / "passive-trigger-route-state.json"


def load_route_state(path: Path) -> dict[str, dict[str, str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(value, dict):
        return {}
    return {
        str(key): item
        for key, item in value.items()
        if isinstance(item, dict)
    }


def save_route_state(path: Path, session_id: str, route: str) -> None:
    key = state_key(session_id)
    if not key or not route:
        return
    state = load_route_state(path)
    state[key] = {
        "route": route,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    ordered = sorted(
        state.items(),
        key=lambda item: item[1].get("updated_at", ""),
        reverse=True,
    )[:200]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(ordered), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def build_event(
    text: str,
    metadata: dict[str, str],
    shortcuts: list[str] | None = None,
    context_route: str = "",
) -> dict[str, Any]:
    probe = load_probe()
    result = probe.classify(
        text,
        shortcuts if shortcuts is not None else load_shortcuts(probe),
        context_route=context_route,
    )
    prompt_hash = short_hash(text, 20)
    identity = ":".join(
        [
            short_hash(metadata.get("session_id", ""), 20),
            short_hash(metadata.get("turn_id", ""), 20),
            prompt_hash,
        ]
    )
    event_id = short_hash(identity, 20)
    source_signal = (
        probe.sanitize(text)
        if os.environ.get("CODEX_PASSIVE_TRIGGER_RECORD_TEXT") == "1"
        else "[redacted]"
    )
    return {
        "event_id": event_id,
        "time": probe.now_iso(),
        "session_hash": short_hash(metadata.get("session_id", ""), 20),
        "turn_hash": short_hash(metadata.get("turn_id", ""), 20),
        "cwd_hash": short_hash(metadata.get("cwd", ""), 12),
        "trigger_level": result["trigger_level"],
        "trigger_type": result["trigger_type"],
        "source_signal": source_signal,
        "prompt_hash": prompt_hash,
        "suggested_route": result["suggested_route"],
        "actual_route": "",
        "confidence": result["confidence"],
        "changed_rules": False,
        "was_correct": None,
        "hint_delivered": bool(result["suggested_route"]),
        "auto_action_allowed": False,
        "notes": "advisory observation only",
        "matched_terms": result["matched_terms"],
        "shield_hints": result["shield_hints"],
        "need_ai_review": result["need_ai_review"],
        "observation_phase": True,
        "hook_event": "UserPromptSubmit",
    }


def hook_output(event: dict[str, Any]) -> dict[str, Any]:
    route = str(event.get("suggested_route") or "")
    if not route:
        return {}
    hints = ", ".join(str(value) for value in event.get("shield_hints") or [])
    suffix = f"; shield hints: {hints}" if hints else ""
    context = (
        f"Passive route hint (advisory only, not automatic execution): "
        f"consider ${route}{suffix}. AI remains responsible for routing and all "
        "approval, privacy, and safety boundaries still apply."
    )
    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context[:400],
        },
    }


def record_error(error: Exception) -> None:
    try:
        path = codex_home() / "hooks" / "state" / "passive-trigger-errors.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        message = " ".join(str(error).split())[:300]
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{timestamp} {type(error).__name__}: {message}\n")
    except Exception:
        pass


def main() -> int:
    try:
        probe = load_probe()
        metadata = parse_hook_payload(read_stdin_text())
        text = metadata["prompt"]
        if not text:
            return 0
        state = load_route_state(state_path())
        context_route = str(
            state.get(state_key(metadata.get("session_id", "")), {}).get("route", "")
        )
        event = build_event(
            text,
            metadata,
            shortcuts=load_shortcuts(probe),
            context_route=context_route,
        )
        probe.append_event(probe.default_ledger(), event)
        route = str(event.get("suggested_route") or "")
        if route:
            save_route_state(state_path(), metadata.get("session_id", ""), route)
            print(json.dumps(hook_output(event), ensure_ascii=False, separators=(",", ":")))
    except Exception as error:
        record_error(error)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
