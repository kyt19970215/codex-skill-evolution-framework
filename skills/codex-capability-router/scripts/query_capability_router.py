#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Query the local Codex capability registry for a task."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


CATEGORY_KEYWORDS = {
    "product_design": ["product design", "ux", "ui", "prototype", "figma", "canva", "screenshot", "url clone", "visual", "interface", "image generation", "mood board", "产品设计", "原型", "设计", "界面", "交互", "截图", "生图", "视觉"],
    "business_analysis": ["business analysis", "analytics", "metric", "kpi", "dashboard", "report", "variance", "商业分析", "指标", "看板", "报告", "数据分析"],
    "creative_production": ["creative", "campaign", "marketing", "ads", "ecommerce", "image set", "创意", "营销", "广告", "物料", "图片"],
    "sales": ["sales", "crm", "account", "meeting prep", "follow-up", "deal", "销售", "客户", "跟进", "商机"],
    "finance_investing": ["public equity", "earnings", "investment", "banking", "diligence", "pitch", "金融", "投资", "财报", "尽调", "路演"],
    "documents": ["docx", "word", "document", "google docs", "redline", "comments", "文档", "批注", "修订"],
    "spreadsheets": ["xlsx", "csv", "tsv", "spreadsheet", "sheet", "excel", "workbook", "表格"],
    "presentations": ["pptx", "slides", "deck", "powerpoint", "presentation", "幻灯片", "ppt", "演示"],
    "pdf": ["pdf"],
    "github": ["github", "pull request", " pr ", "issue", "ci", "actions", "review"],
    "web_browser": ["browser", "chrome", "website", "live url", "web test", "浏览器", "网页"],
    "desktop_control": ["desktop", "windows app", "computer use", "桌面", "windows 应用"],
    "sites": ["hosted", "deploy", "site", "hosting", "部署", "托管", "网站"],
    "latex": ["latex", "tex"],
    "nvidia": ["nvidia", "cuda", "omniverse", "gpu"],
    "openai_docs": ["openai", "codex", "gpt", "api", "model", "官方文档"],
    "coding_debug": ["debug", "build", "test", "script", "shell", "path", "encoding", "代码", "调试", "构建", "测试"],
    "research_verification": ["version", "dependency", "install", "upgrade", "compatibility", "public tool", "版本", "依赖", "安装", "兼容"],
    "skill_evolution": ["skill", "plugin", "evolution", "trigger observation", "passive trigger", "absorb skill", "absorb capability", "maintain rule", "prune rule", "remember", "route rule", "技能演化", "能力吸收", "规则维护", "插件", "技能", "规则"],
    "content_visuals": ["article illustration", "illustrate article", "cover image", "infographic", "visual summary", "为文章配图", "文章配图", "封面图", "信息图", "高密度信息大图"],
    "software_workflow": ["requirements", "brainstorming", "implementation plan", "tdd", "parallel agents", "code review", "verification", "需求梳理", "实施计划", "测试驱动", "并行开发", "代码审查", "完成前验证"],
    "product_strategy": ["founder", "ceo review", "product strategy", "engineering review", "design review", "创始人", "产品策略", "ceo 评审", "工程评审", "设计评审"],
    "browser_qa": ["browser qa", "website qa", "qa report", "report only", "regression test", "浏览器 qa", "网站 qa", "只读", "缺陷报告", "回归测试"],
    "skill_discovery": ["find skill", "skill search", "discover skill", "find a suitable skill", "查找 skill", "搜索 skill", "合适的 skill", "找合适的 skill", "skill 推荐", "找技能", "技能搜索", "技能推荐"],
}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_db() -> Path:
    return codex_home() / "skills" / "codex-capability-router" / "data" / "capabilities.sqlite"


def normalize(text: str) -> str:
    return f" {text.lower()} "


def score_category(task: str, category: str) -> int:
    text = normalize(task)
    score = 0
    for term in CATEGORY_KEYWORDS.get(category, []):
        needle = term.lower()
        if re.search(r"[\u4e00-\u9fff]", needle):
            if needle in text:
                score += max(2, len(needle))
        elif needle in text:
            score += max(1, len(needle.split()))
    return score


def categories_for_task(task: str) -> list[tuple[str, int]]:
    scores = [(cat, score_category(task, cat)) for cat in CATEGORY_KEYWORDS]
    scores = [(cat, score) for cat, score in scores if score > 0]
    if not scores:
        return [("general", 0)]
    return sorted(scores, key=lambda item: item[1], reverse=True)[:4]


def rows(conn: sqlite3.Connection, query: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(query, params)]


def capability_matches(conn: sqlite3.Connection, category: str, status: str, limit: int) -> list[dict[str, Any]]:
    return rows(
        conn,
        """
        SELECT * FROM capabilities
        WHERE category = ? AND status = ?
        ORDER BY
          CASE kind
            WHEN 'plugin' THEN 0
            WHEN 'plugin_skill' THEN 1
            WHEN 'skill' THEN 2
            WHEN 'plugin_candidate' THEN 3
            ELSE 4
          END,
          name
        LIMIT ?
        """,
        (category, status, limit),
    )


def capability_named(conn: sqlite3.Connection, token: str, status: str, limit: int) -> list[dict[str, Any]]:
    name = token.split(":")[-1].strip().lower()
    if not name:
        return []
    return rows(
        conn,
        """
        SELECT * FROM capabilities
        WHERE status = ?
          AND (
            lower(name) = ?
            OR lower(display_name) = ?
            OR lower(name) LIKE ?
          )
        ORDER BY
          CASE kind
            WHEN 'plugin' THEN 0
            WHEN 'plugin_skill' THEN 1
            WHEN 'skill' THEN 2
            ELSE 3
          END,
          name
        LIMIT ?
        """,
        (status, name, name, f"%{name}%", limit),
    )


def explicit_capability_matches(
    conn: sqlite3.Connection,
    task: str,
    status: str,
    limit: int,
) -> list[dict[str, Any]]:
    task_text = task.lower()
    matches: list[tuple[int, int, str, dict[str, Any]]] = []
    kind_order = {"plugin": 0, "plugin_skill": 1, "skill": 2}

    for item in rows(conn, "SELECT * FROM capabilities WHERE status = ?", (status,)):
        aliases: set[str] = set()
        for value in (item.get("name"), item.get("display_name")):
            alias = str(value or "").strip().lower()
            if not alias:
                continue
            aliases.add(alias)
            aliases.add(alias.replace("-", " "))
            if ":" in alias:
                aliases.add(alias.split(":")[-1].strip())

        best = 0
        for alias in aliases:
            if len(alias) < 3:
                continue
            if re.search(r"[\u4e00-\u9fff]", alias):
                matched = alias in task_text
            else:
                matched = (
                    re.search(
                        rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])",
                        task_text,
                    )
                    is not None
                )
            if matched:
                best = max(best, len(alias))
        if best:
            matches.append(
                (
                    best,
                    kind_order.get(str(item.get("kind")), 3),
                    str(item.get("name")),
                    item,
                )
            )

    matches.sort(key=lambda value: (-value[0], value[1], value[2]))
    return [item for _, _, _, item in matches[:limit]]


TEXT_SEARCH_STOP_WORDS = {
    "and",
    "for",
    "from",
    "into",
    "make",
    "the",
    "this",
    "use",
    "using",
    "with",
}


def task_search_terms(task: str) -> list[str]:
    terms = re.findall(r"[a-z0-9][a-z0-9+._:-]*|[\u4e00-\u9fff]{2,}", task.lower())
    return [
        term
        for term in terms
        if len(term) >= 3 and term not in TEXT_SEARCH_STOP_WORDS
    ][:16]


def text_search(conn: sqlite3.Connection, task: str, status: str, limit: int) -> list[dict[str, Any]]:
    terms = task_search_terms(task)
    if not terms:
        return []
    kind_order = {"plugin": 0, "plugin_skill": 1, "skill": 2}
    matches: list[tuple[int, int, str, dict[str, Any]]] = []
    for item in rows(conn, "SELECT * FROM capabilities WHERE status = ?", (status,)):
        haystack = str(item.get("trigger_terms") or "").lower()
        score = sum(max(1, len(term.split())) for term in terms if term in haystack)
        if score:
            matches.append(
                (
                    score,
                    kind_order.get(str(item.get("kind")), 3),
                    str(item.get("name")),
                    item,
                )
            )
    matches.sort(key=lambda value: (-value[0], value[1], value[2]))
    return [item for _, _, _, item in matches[:limit]]


def route_task(db_path: Path, task: str, limit: int) -> dict[str, Any]:
    if not db_path.exists():
        return {
            "error": f"Registry not found: {db_path}",
            "next_step": "Run build_capability_registry.py first.",
        }
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    categories = categories_for_task(task)
    recommendations = explicit_capability_matches(conn, task, "installed", limit)
    candidates = explicit_capability_matches(conn, task, "candidate", limit)
    route_rows = []
    general_only = categories == [("general", 0)]
    if general_only:
        recommendations.extend(text_search(conn, task, "installed", limit))
        candidates.extend(text_search(conn, task, "candidate", limit))
    else:
        for category, score in categories:
            route_rows.extend(
                rows(conn, "SELECT * FROM routes WHERE category = ?", (category,))
            )
        for route in route_rows:
            for key in ("primary_capability", "fallback_capability"):
                recommendations.extend(
                    capability_named(conn, route.get(key, ""), "installed", limit)
                )
                candidates.extend(
                    capability_named(conn, route.get(key, ""), "candidate", limit)
                )
        for category, score in categories:
            recommendations.extend(
                capability_matches(conn, category, "installed", limit)
            )
            candidates.extend(
                capability_matches(conn, category, "candidate", limit)
            )
    if not general_only:
        recommendations.extend(text_search(conn, task, "installed", limit))
        candidates.extend(text_search(conn, task, "candidate", limit))
    conn.close()
    return {
        "task": task,
        "categories": [{"category": cat, "score": score} for cat, score in categories],
        "installed_recommendations": dedupe(recommendations)[:limit],
        "candidate_plugins_or_sources": dedupe(candidates)[:limit],
        "route_notes": route_rows[:limit],
        "use_contract": (
            "Select only direct task owners. Treat each selected installed capability "
            "as an execution route, not a label: read its exact entrypoint and required "
            "official references, prefer its native tools, modules, templates, examples, "
            "or assets, and report concrete use evidence or a justified fallback."
        ),
        "install_boundary": "Do not install candidates automatically. Tell the user the project function and ask before installing.",
    }


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for item in items:
        key = (
            item.get("kind"),
            str(item.get("name") or "").lower(),
            str(item.get("display_name") or "").lower(),
            item.get("category"),
            item.get("status"),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def as_text(payload: dict[str, Any]) -> str:
    if "error" in payload:
        return f"{payload['error']}\nNext: {payload.get('next_step', '')}"
    lines = []
    cats = ", ".join(f"{item['category']}({item['score']})" for item in payload["categories"])
    lines.append(f"Detected categories: {cats}")
    lines.append("")
    lines.append("Installed capability candidates, exact and direct matches first:")
    if payload["installed_recommendations"]:
        for item in payload["installed_recommendations"]:
            lines.append(f"- {item.get('display_name') or item.get('name')} [{item.get('kind')}] - {short(item.get('description'))}")
    else:
        lines.append("- None matched in the local registry.")
    lines.append("")
    lines.append("Candidate plugins or sources to mention only after asking:")
    if payload["candidate_plugins_or_sources"]:
        for item in payload["candidate_plugins_or_sources"]:
            lines.append(f"- {item.get('display_name') or item.get('name')} [{item.get('trust_level')}] - {short(item.get('description'))}")
    else:
        lines.append("- None matched.")
    lines.append("")
    lines.append(payload["use_contract"])
    lines.append("")
    lines.append(payload["install_boundary"])
    return "\n".join(lines)


def short(text: Any, length: int = 180) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= length:
        return value
    return value[: length - 3] + "..."


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Route a task to Codex capabilities.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--db", default=str(default_db()))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    payload = route_task(Path(args.db).expanduser(), args.task, args.limit)
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(as_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
