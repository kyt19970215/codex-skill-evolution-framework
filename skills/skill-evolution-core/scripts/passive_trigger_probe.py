#!/usr/bin/env python3
"""Observation-only passive trigger probe for the public evolution framework."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any


CODING_TERMS = [
    "code",
    "bug",
    "debug",
    "error",
    "traceback",
    "exception",
    "build",
    "test",
    "script",
    "shell",
    "powershell",
    "cmd",
    "path",
    "encoding",
    "quote",
    "dependency",
    "import",
    "compile",
    "lint",
    "typescript",
    "javascript",
    "python",
    "react",
    "rust",
    "function",
    "class",
    "api",
    "sdk",
    "cli",
    "crash",
    "代码",
    "编程",
    "报错",
    "调试",
    "构建",
    "测试",
    "脚本",
    "命令",
    "路径",
    "编码",
    "引号",
    "转义",
    "依赖",
    "类型错误",
    "类型不匹配",
    "无法运行",
    "编译失败",
    "构建失败",
    "测试失败",
    "崩溃",
    "异常",
    "函数",
    "接口",
]

EVOLUTION_TERMS = [
    "skill",
    "trigger",
    "validator",
    "ledger",
    "evolution",
    "devolution",
    "absorption",
    "route",
    "rule",
    "shield",
    "self-check",
    "触发",
    "盾牌",
    "规则",
    "校验",
    "自检",
    "台账",
]

HIGH_IMPACT_TERMS = [
    "delete",
    "remove",
    "commit",
    "push",
    "publish",
    "deploy",
    "install",
    "login",
    "cookie",
    "password",
    "token",
    "credential",
    "删除",
    "提交",
    "推送",
    "发布",
    "部署",
    "安装",
    "登录",
    "密码",
    "令牌",
    "账号",
]

EVOLUTION_CONTEXT_TERMS = (
    "evolution skill",
    "skill evolution",
    "evolution system",
    "skill system",
    "trigger system",
    "validator",
    "自检器",
)

SELF_CHECK_TERMS = (
    "self-check",
    "self check",
    "validation",
    "validate",
    "audit",
    "health",
    "freshness",
    "cleanliness",
    "behavior regression",
    "ledger comparison",
    "自检",
    "校验",
    "干净度",
    "健康检查",
    "行为回归",
    "缺点",
    "新鲜度",
    "台账对照",
)

DISCUSSION_ONLY_TERMS = (
    "discuss only",
    "discussion only",
    "do not run",
    "don't run",
    "do not execute",
    "don't execute",
    "do not modify",
    "don't modify",
    "question only",
    "只是讨论",
    "只讨论",
    "不要执行",
    "不执行",
    "不要修改",
    "不修改",
    "只是询问",
    "仅询问",
)

RULE_CAPTURE_TERMS = (
    "save this as a durable rule",
    "add this rule",
    "add a rule",
    "write this into a skill",
    "write into skill",
    "for future tasks",
    "from now on",
    "以后遇到",
    "以后都",
    "增加规则",
    "添加规则",
    "沉淀规则",
    "写进 skill",
    "加入 skill",
)

CONTINUATION_TERMS = (
    "continue",
    "next step",
    "previous task",
    "previous message",
    "carry on",
    "继续",
    "下一步",
    "上一条",
    "上一个",
    "接着",
)

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key|token|password|cookie)\s*[:=]\s*\S+"),
    re.compile(r"\b[A-Za-z0-9_-]{32,}\b"),
]


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_ledger() -> Path:
    return (
        codex_home()
        / "skills"
        / "skill-evolution-core"
        / "references"
        / "evolution-trigger-events.jsonl"
    )


def default_manifest() -> Path:
    return codex_home() / ".skill-evolution-framework.json"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sanitize(text: str, limit: int = 160) -> str:
    value = " ".join(text.split())
    for pattern in SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    if len(value) > limit:
        value = value[: limit - 3] + "..."
    return value


def hits(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    found: list[str] = []
    for term in terms:
        needle = term.lower()
        if re.search(r"[\u4e00-\u9fff]", needle):
            matched = needle in text
        else:
            matched = re.search(rf"\b{re.escape(needle)}\b", lower) is not None
        if matched:
            found.append(term)
    return found


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lower = text.casefold()
    return any(term.casefold() in lower for term in terms)


def normalize_shortcut_text(text: str) -> str:
    return text.strip().strip(".!?。！？ ").casefold()


def shortcut_matches(text: str, shortcuts: list[str]) -> tuple[bool, bool]:
    normalized = normalize_shortcut_text(text)
    exact = any(normalized == normalize_shortcut_text(value) for value in shortcuts)
    contained = any(value.casefold() in text.casefold() for value in shortcuts)
    return exact, contained


def load_manifest_triggers(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    triggers = payload.get("triggers")
    if not isinstance(triggers, dict):
        return {}
    return {key: value for key, value in triggers.items() if isinstance(value, str) and value}


def configured_shortcuts(args: argparse.Namespace) -> list[str]:
    triggers = load_manifest_triggers(Path(args.manifest).expanduser())
    values = [
        args.evolution_shortcut or triggers.get("evolution", ""),
        args.absorption_shortcut or triggers.get("absorption", ""),
        args.rule_maintenance_shortcut or triggers.get("rule_maintenance", ""),
    ]
    return [value.strip() for value in values if value and value.strip()]


def classify(
    text: str,
    shortcuts: list[str],
    context_route: str = "",
) -> dict[str, Any]:
    coding = hits(text, CODING_TERMS)
    evolution = hits(text, EVOLUTION_TERMS)
    high_impact = hits(text, HIGH_IMPACT_TERMS)

    exact_shortcut, contained_shortcut = shortcut_matches(text, shortcuts)
    discussion_only = contains_any(text, DISCUSSION_ONLY_TERMS)
    evolution_context = bool(evolution) or contains_any(text, EVOLUTION_CONTEXT_TERMS)
    explicit_self_check = evolution_context and contains_any(text, SELF_CHECK_TERMS)
    rule_capture = contains_any(text, RULE_CAPTURE_TERMS)
    continuation = bool(context_route) and contains_any(text, CONTINUATION_TERMS)

    shield_hints: list[str] = []
    lower = text.lower()
    if any(term in lower or term in text for term in ("encoding", "utf-8", "mojibake", "乱码", "编码")):
        shield_hints.append("encoding")
    if any(term in lower or term in text for term in ("path", "路径", "literalpath", "file not found", "文件不存在")):
        shield_hints.append("path")
    if any(term in lower or term in text for term in ("quote", "escape", "引号", "转义", "powershell")):
        shield_hints.append("quoting")
    if any(term in lower or term in text for term in ("dependency", "import", "module", "依赖", "导入")):
        shield_hints.append("dependency")
    if not shield_hints and coding:
        shield_hints = ["environment", "path", "encoding", "quoting"]

    if exact_shortcut:
        suggested_route = "skill-evolution-core"
        trigger_level = "L4"
        trigger_type = "configured_shortcut"
        confidence = "high"
    elif explicit_self_check:
        suggested_route = "skill-evolution-validator"
        trigger_level = "L4"
        trigger_type = "explicit_self_check"
        confidence = "high"
    elif discussion_only:
        suggested_route = ""
        trigger_level = "L0"
        trigger_type = "discussion_only"
        confidence = "high"
    elif contained_shortcut:
        suggested_route = "skill-evolution-core"
        trigger_level = "L4"
        trigger_type = "configured_shortcut_in_request"
        confidence = "high"
    elif rule_capture:
        suggested_route = "skill-evolution-router"
        trigger_level = "L1"
        trigger_type = "passive_rule_capture_candidate"
        confidence = "high"
    elif coding:
        suggested_route = "coding-debug-rules"
        trigger_level = "L1"
        trigger_type = "passive_coding_shield_candidate"
        confidence = "medium" if len(coding) < 3 else "high"
    elif continuation:
        suggested_route = context_route
        trigger_level = "L1"
        trigger_type = "passive_context_continuation"
        confidence = "medium"
    elif evolution:
        suggested_route = "skill-evolution-router"
        trigger_level = "L1"
        trigger_type = "passive_evolution_candidate"
        confidence = "medium"
    else:
        suggested_route = ""
        trigger_level = "L0"
        trigger_type = "no_clear_trigger"
        confidence = "low"

    return {
        "trigger_level": trigger_level,
        "trigger_type": trigger_type,
        "suggested_route": suggested_route,
        "confidence": confidence,
        "matched_terms": {
            "coding": coding[:12],
            "evolution": evolution[:12],
            "high_impact": high_impact[:12],
        },
        "shield_hints": shield_hints,
        "need_ai_review": bool(high_impact or confidence == "low"),
        "auto_action_allowed": False,
        "observation_phase": True,
        "reason_codes": {
            "discussion_only": discussion_only,
            "explicit_self_check": explicit_self_check,
            "rule_capture": rule_capture,
            "continuation": continuation,
        },
    }


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Observe passive trigger signals without automatic action."
    )
    parser.add_argument("--text", default="", help="User message or sanitized task text to inspect.")
    parser.add_argument("--context", default="", help="Optional short task context.")
    parser.add_argument("--record", action="store_true", help="Append an event to the trigger ledger.")
    parser.add_argument("--ledger", default=str(default_ledger()))
    parser.add_argument("--manifest", default=str(default_manifest()))
    parser.add_argument("--evolution-shortcut", default="")
    parser.add_argument("--absorption-shortcut", default="")
    parser.add_argument("--rule-maintenance-shortcut", default="")
    parser.add_argument("--actual-route", default="")
    parser.add_argument("--changed-rules", action="store_true")
    parser.add_argument("--was-correct", choices=["true", "false", "unknown"], default="unknown")
    parser.add_argument("--notes", default="observation only")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    inspected_text = " ".join(part for part in (args.context, args.text) if part).strip()
    result = classify(inspected_text, configured_shortcuts(args))
    if args.was_correct == "true":
        was_correct: bool | None = True
    elif args.was_correct == "false":
        was_correct = False
    else:
        was_correct = None

    event = {
        "time": now_iso(),
        "trigger_level": result["trigger_level"],
        "trigger_type": result["trigger_type"],
        "source_signal": sanitize(inspected_text),
        "suggested_route": result["suggested_route"],
        "actual_route": args.actual_route,
        "confidence": result["confidence"],
        "changed_rules": bool(args.changed_rules),
        "was_correct": was_correct,
        "auto_action_allowed": False,
        "notes": sanitize(args.notes, limit=200),
        "matched_terms": result["matched_terms"],
        "shield_hints": result["shield_hints"],
        "need_ai_review": result["need_ai_review"],
        "observation_phase": True,
    }

    if args.record:
        append_event(Path(args.ledger).expanduser(), event)

    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
