#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a local Codex capability registry from installed skills and plugins."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any


SKIP_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv"}

ROUTE_ROWS = [
    ("product_design", "product design UX UI prototype screenshot URL clone visual direction interface image generation mood board 产品设计 原型 设计 界面 交互 生图 视觉", "installed-product-design-workflow", "installed-image-generation-workflow", "Ask before installing a missing design capability.", "Start with the installed workflow's context or brief gate, then use its specialized implementation route."),
    ("business_analysis", "business analysis metrics KPI dashboard report data exploration variance 商业分析 指标 看板 报告 数据分析", "spreadsheets", "presentations", "Ask before installing Data Analytics role plugin.", "Use installed artifact plugins first."),
    ("creative_production", "marketing creative campaign ads product photos ecommerce 创意 物料 广告 营销 图片", "imagegen", "product-design:index", "Ask before installing Creative Production role plugin.", "Use image generation only when bitmap assets are needed."),
    ("sales", "sales CRM meeting prep follow-up deal pipeline 销售 客户 跟进 商机 CRM", "installed-sales-workflow", "documents", "Ask before installing a sales capability or authorizing a connector.", "Installed connector availability may vary."),
    ("finance_investing", "public equities earnings comps pitch diligence investment thesis 金融 投资 财报 尽调 路演", "spreadsheets", "presentations", "Ask before installing finance role plugins.", "Use current data sources only after verification."),
    ("documents", "docx Word Google Docs document redline comments 文档 Word 批注 修订", "documents", "pdf", "No candidate install needed if Documents is installed.", "Use Documents plugin for editable document artifacts."),
    ("spreadsheets", "xlsx csv tsv sheets workbook formulas chart 表格 Excel CSV", "spreadsheets", "documents", "No candidate install needed if Spreadsheets is installed.", "Use Spreadsheets plugin for workbook artifacts."),
    ("presentations", "pptx slides deck PowerPoint Google Slides 幻灯片 PPT 演示", "presentations", "documents", "No candidate install needed if Presentations is installed.", "Use Presentations plugin for editable decks."),
    ("pdf", "pdf render extract form pages PDF 渲染 提取 表单", "pdf", "documents", "No candidate install needed if PDF is installed.", "Use PDF plugin when visual layout matters."),
    ("github", "GitHub repo pull request PR issue CI actions review commit branch", "installed-github-workflow", "git", "Install or authorize GitHub integration only if unavailable.", "Use the narrow installed route for comments, CI, or publishing."),
    ("web_browser", "browser Chrome website live URL web testing 浏览器 网页 测试", "browser", "chrome", "Ask before installing browser/chrome plugins.", "Use browser tools for live web verification."),
    ("desktop_control", "Windows app desktop UI automation computer use 桌面 Windows 应用", "computer-use", "computer-use:computer-use", "Ask before enabling desktop control.", "Use Computer Use only for OS/app UI work."),
    ("sites", "deploy hosted site web app share prototype hosting 网站 部署 托管", "sites", "product-design:share", "Ask before installing Sites.", "Use for hosted shareable web apps."),
    ("latex", "latex tex tectonic compile TeX 公式 排版", "latex", "pdf", "Ask before installing LaTeX plugin.", "Use LaTeX plugin for TeX compilation."),
    ("nvidia", "NVIDIA CUDA Omniverse AI-Q Dynamo cuOpt physical AI GPU", "nvidia", "research-verification", "Ask before installing NVIDIA plugin.", "Use NVIDIA specialized skills."),
    ("openai_docs", "OpenAI API Codex model docs official latest GPT", "openai-docs", "research-verification", "No candidate install needed if docs skill is installed.", "Use official OpenAI docs route."),
    ("coding_debug", "code shell build test dependency path encoding quoting script", "coding-debug-rules", "research-verification", "No candidate install needed.", "Use for local technical work."),
    ("research_verification", "public tool version API dependency compatibility error install upgrade", "research-verification", "coding-debug-rules", "No candidate install needed.", "Use for current public facts."),
    ("skill_evolution", "skill evolution create update split absorb plugin architecture rule remember 吞噬", "skill-evolution-core", "skill-evolution-router", "No candidate install needed.", "Use before editing skills or when the forced absorption shortcut is invoked."),
    ("content_visuals", "article illustration cover image infographic visual summary 为文章配图 封面 信息图 可视化", "installed-visual-workflow", "installed-image-generation-workflow", "Ask before installing a missing visual capability.", "Choose the narrow workflow for the requested visual artifact."),
    ("software_workflow", "requirements brainstorming implementation plan TDD parallel agents code review verification 需求 计划 测试驱动 并行 开发 审查 验证", "installed-development-workflow", "coding-debug-rules", "No candidate install needed when a matching workflow is installed.", "Use the narrow installed development workflow after project and environment routing."),
    ("product_strategy", "founder CEO product strategy engineering review design review product planning 创始人 产品策略 CEO 评审 工程评审 设计评审", "installed-product-strategy-workflow", "documents", "Ask before installing a missing strategy workflow.", "Keep remote writes separately authorized."),
    ("browser_qa", "browser QA report only regression test bugs website QA 浏览器 QA 只读测试 缺陷报告 回归测试", "installed-report-only-qa-workflow", "installed-browser-workflow", "Use a fixing route only when edits are authorized.", "Default to report-only QA."),
    ("skill_discovery", "find skill discover skill installable workflow skill search 查找 skill 搜索 skill 技能搜索", "find-skills", "codex-capability-router", "Discovery does not authorize installation.", "Use only when no installed capability clearly matches."),
]

OFFICIAL_ROLE_CANDIDATES = [
    {
        "id": "official-role:data-analytics",
        "kind": "plugin_candidate",
        "name": "data-analytics",
        "display_name": "Data Analytics",
        "category": "business_analysis",
        "status": "candidate",
        "description": "Role-specific plugin direction for exploring product and business data, explaining metric changes, and creating reports or dashboards.",
        "trigger_terms": "data analytics business analysis metrics dashboards reports Snowflake Databricks Hex Tableau",
        "source_url": "https://github.com/openai/role-specific-plugins",
        "trust_level": "official-candidate",
        "permissions": "May require workspace apps or data connectors.",
        "notes": "Refresh availability in the Codex plugin directory before install guidance.",
    },
    {
        "id": "official-role:creative-production",
        "kind": "plugin_candidate",
        "name": "creative-production",
        "display_name": "Creative Production",
        "category": "creative_production",
        "status": "candidate",
        "description": "Role-specific plugin direction for campaign boards, ad variations, product lifestyle shots, and ecommerce-ready image sets.",
        "trigger_terms": "creative production marketing campaign assets ads ecommerce images Canva Figma Shutterstock Picsart Fal",
        "source_url": "https://github.com/openai/role-specific-plugins",
        "trust_level": "official-candidate",
        "permissions": "May require connected creative apps.",
        "notes": "Suggest as candidate only unless installed.",
    },
    {
        "id": "official-role:sales",
        "kind": "plugin_candidate",
        "name": "sales",
        "display_name": "Sales",
        "category": "sales",
        "status": "candidate",
        "description": "Role-specific plugin direction for account signals, meeting preparation, follow-ups, CRM updates, close plans, and deal risk review.",
        "trigger_terms": "sales CRM Salesforce HubSpot Slack Outreach Clay account meeting follow-up deal",
        "source_url": "https://github.com/openai/role-specific-plugins",
        "trust_level": "official-candidate",
        "permissions": "May require CRM or sales app authorization.",
        "notes": "Suggest as candidate only unless installed.",
    },
    {
        "id": "official-role:public-equity-investing",
        "kind": "plugin_candidate",
        "name": "public-equity-investing",
        "display_name": "Public Equity Investing",
        "category": "finance_investing",
        "status": "candidate",
        "description": "Role-specific plugin direction for earnings review, company comparison, market signals, and investment thesis tracking.",
        "trigger_terms": "public equity investing earnings companies thesis FactSet LSEG PitchBook Hebbia",
        "source_url": "https://github.com/openai/role-specific-plugins",
        "trust_level": "official-candidate",
        "permissions": "May require market data connectors or subscriptions.",
        "notes": "Not financial advice; verify data freshness.",
    },
    {
        "id": "official-role:investment-banking",
        "kind": "plugin_candidate",
        "name": "investment-banking",
        "display_name": "Investment Banking",
        "category": "finance_investing",
        "status": "candidate",
        "description": "Role-specific plugin direction for pitch materials, comparable company and transaction analysis, diligence, and client-ready recommendations.",
        "trigger_terms": "investment banking pitch materials comps transactions diligence recommendations",
        "source_url": "https://github.com/openai/role-specific-plugins",
        "trust_level": "official-candidate",
        "permissions": "May require finance data or document connectors.",
        "notes": "Suggest as candidate only unless installed.",
    },
]

DISCOVERY_SOURCES = [
    {
        "id": "source:openai-plugins",
        "kind": "plugin_source",
        "name": "openai/plugins",
        "display_name": "OpenAI plugin examples",
        "category": "plugin_discovery",
        "status": "candidate",
        "description": "OpenAI-maintained examples of Codex plugin structure and installable plugin layouts.",
        "trigger_terms": "codex plugin examples official openai",
        "source_url": "https://github.com/openai/plugins",
        "trust_level": "official-candidate",
        "permissions": "Inspect before installing examples.",
        "notes": "Use as a source of candidate plugin examples.",
    },
    {
        "id": "source:awesome-codex-plugins",
        "kind": "plugin_source",
        "name": "awesome-codex-plugins",
        "display_name": "Awesome Codex Plugins",
        "category": "plugin_discovery",
        "status": "candidate",
        "description": "Community curated list and marketplace source for Codex plugins.",
        "trigger_terms": "awesome codex plugins community marketplace",
        "source_url": "https://github.com/hashgraph-online/awesome-codex-plugins",
        "trust_level": "community-candidate",
        "permissions": "Inspect manifest, hooks, MCP, and commands before installing.",
        "notes": "Treat as a candidate index, not a trusted install source.",
    },
    {
        "id": "source:role-specific-plugins",
        "kind": "plugin_source",
        "name": "role-specific-plugins",
        "display_name": "Role-specific plugin templates",
        "category": "plugin_discovery",
        "status": "candidate",
        "description": "OpenAI role-specific plugin templates for roles such as sales, data analytics, product design, and financial markets.",
        "trigger_terms": "role-specific plugins sales data analytics product design finance",
        "source_url": "https://github.com/openai/role-specific-plugins",
        "trust_level": "official-candidate",
        "permissions": "Inspect templates before adapting or installing.",
        "notes": "Availability and contents should be refreshed before use.",
    },
]

NAME_CATEGORY = {
    "product-design": "product_design",
    "browser": "web_browser",
    "chrome": "web_browser",
    "computer-use": "desktop_control",
    "documents": "documents",
    "spreadsheets": "spreadsheets",
    "presentations": "presentations",
    "pdf": "pdf",
    "github": "github",
    "sites": "sites",
    "latex": "latex",
    "nvidia": "nvidia",
    "imagegen": "creative_production",
    "openai-docs": "openai_docs",
    "coding-debug-rules": "coding_debug",
    "research-verification": "research_verification",
    "skill-evolution-core": "skill_evolution",
    "skill-evolution-router": "skill_evolution",
    "skill-creator": "skill_evolution",
    "skill-installer": "skill_evolution",
    "plugin-creator": "skill_evolution",
    "codex-capability-router": "plugin_discovery",
    "find-skills": "skill_discovery",
}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp936", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    match = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line[:1].isspace() or ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            block: list[str] = []
            index += 1
            while index < len(lines) and (lines[index][:1].isspace() or not lines[index].strip()):
                block.append(lines[index].strip())
                index += 1
            separator = "\n" if value.startswith("|") else " "
            data[key] = separator.join(part for part in block if part).strip()
            continue
        data[key] = value.strip("\"'")
        index += 1
    return data


def safe_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(read_text(path))
    except Exception:
        return None


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def category_from_text(text: str) -> str:
    lowered = text.lower()
    def has_term(term: str) -> bool:
        needle = term.lower()
        if re.search(r"[\u4e00-\u9fff]", needle):
            return needle in lowered
        if " " in needle or "-" in needle:
            return needle in lowered
        return re.search(rf"\b{re.escape(needle)}\b", lowered) is not None

    checks = [
        ("content_visuals", ["article illustration", "cover image", "infographic", "visual summary", "为文章配图", "封面图", "信息图"]),
        ("browser_qa", ["browser qa", "qa report", "report-only qa", "regression test", "只读测试", "缺陷报告", "回归测试"]),
        ("product_strategy", ["founder", "ceo review", "product strategy", "engineering review", "产品策略", "创始人", "工程评审"]),
        ("skill_discovery", ["find skill", "skill search", "discover skill", "查找 skill", "搜索 skill", "技能搜索"]),
        ("product_design", ["product design", "design-qa", "prototype", "figma", "ux", "ui", "screenshot", "interface", "视觉", "原型", "设计"]),
        ("business_analysis", ["analytics", "business", "metric", "dashboard", "spreadsheet", "kpi", "数据", "指标", "商业"]),
        ("creative_production", ["creative", "campaign", "marketing", "image", "广告", "创意", "营销"]),
        ("sales", ["sales", "crm", "account", "deal", "销售", "客户"]),
        ("finance_investing", ["finance", "invest", "equity", "banking", "earnings", "金融", "投资"]),
        ("documents", ["docx", "word", "document", "docs", "文档"]),
        ("spreadsheets", ["xlsx", "spreadsheet", "csv", "sheet", "excel", "表格"]),
        ("presentations", ["ppt", "slides", "deck", "presentation", "幻灯片", "演示"]),
        ("pdf", ["pdf"]),
        ("github", ["github", "pull request", "issue", "ci", "pr"]),
        ("web_browser", ["browser", "chrome", "website", "url", "网页", "浏览器"]),
        ("desktop_control", ["computer use", "desktop", "windows app", "桌面"]),
        ("sites", ["sites", "hosting", "deploy", "website", "部署"]),
        ("latex", ["latex", "tex"]),
        ("nvidia", ["nvidia", "cuda", "omniverse", "gpu"]),
        ("openai_docs", ["openai", "codex", "gpt", "api"]),
        ("coding_debug", ["debug", "build", "test", "shell", "script", "code", "调试", "代码"]),
        ("research_verification", ["version", "dependency", "install", "api", "兼容", "版本"]),
        ("skill_evolution", ["skill", "plugin", "evolution", "remember", "进化", "插件"]),
    ]
    for category, needles in checks:
        if any(has_term(needle) for needle in needles):
            return category
    return "general"


def category_for(name: str, path: Path | None, text: str) -> str:
    lower_name = name.lower()
    if lower_name in NAME_CATEGORY:
        return NAME_CATEGORY[lower_name]
    if path:
        for part in (piece.lower() for piece in path.parts):
            if part in NAME_CATEGORY:
                return NAME_CATEGORY[part]
    return category_from_text(text)


def normalize_terms(values: Any) -> str:
    if isinstance(values, list):
        return " ".join(str(item) for item in values)
    if values is None:
        return ""
    return str(values)


def capability_id(kind: str, name: str, path: Path | None = None) -> str:
    if path:
        text = str(path).replace("\\", "/").lower()
        if "/plugins/cache/" in text:
            return f"{kind}:{name}:{abs(hash(text))}"
    return f"{kind}:{name}"


def scan_skill_file(path: Path, home: Path) -> dict[str, Any] | None:
    if should_skip(path):
        return None
    text = read_text(path)
    meta = parse_frontmatter(text)
    name = meta.get("name") or path.parent.name
    description = meta.get("description") or ""
    kind = "skill"
    status = "installed"
    trust = "installed"
    category = category_for(name, path, f"{name} {description} {path}")
    if home.joinpath("plugins", "cache") in path.parents:
        kind = "plugin_skill"
    return {
        "id": capability_id(kind, name, path),
        "kind": kind,
        "name": name,
        "display_name": name,
        "category": category,
        "status": status,
        "description": description,
        "trigger_terms": f"{name} {description}",
        "source_path": str(path),
        "source_url": "",
        "trust_level": trust,
        "permissions": "",
        "last_verified": now_iso(),
        "notes": "Discovered from SKILL.md.",
    }


def scan_plugin_manifest(path: Path) -> dict[str, Any] | None:
    data = safe_json(path)
    if not data:
        return None
    interface = data.get("interface") or {}
    author = data.get("author") or {}
    name = str(data.get("name") or path.parent.parent.name)
    display = str(interface.get("displayName") or name)
    description = str(data.get("description") or interface.get("longDescription") or interface.get("shortDescription") or "")
    keywords = normalize_terms(data.get("keywords"))
    capabilities = normalize_terms(interface.get("capabilities"))
    source_url = str(data.get("repository") or data.get("homepage") or "")
    developer = str(interface.get("developerName") or author.get("name") or "")
    trust = "installed"
    category = category_for(name, path, f"{name} {display} {description} {keywords}")
    return {
        "id": capability_id("plugin", name, path),
        "kind": "plugin",
        "name": name,
        "display_name": display,
        "category": category,
        "status": "installed",
        "description": description,
        "trigger_terms": f"{name} {display} {keywords} {description}",
        "source_path": str(path),
        "source_url": source_url,
        "trust_level": trust,
        "permissions": capabilities,
        "last_verified": now_iso(),
        "notes": f"Developer: {developer}" if developer else "Discovered from plugin.json.",
    }


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS capabilities (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            name TEXT NOT NULL,
            display_name TEXT,
            category TEXT,
            status TEXT,
            description TEXT,
            trigger_terms TEXT,
            source_path TEXT,
            source_url TEXT,
            trust_level TEXT,
            permissions TEXT,
            last_verified TEXT,
            notes TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS routes (
            category TEXT,
            task_signal TEXT,
            primary_capability TEXT,
            fallback_capability TEXT,
            ask_user_when TEXT,
            notes TEXT,
            PRIMARY KEY (category, primary_capability, fallback_capability)
        )
        """
    )


def upsert_capability(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    fields = [
        "id",
        "kind",
        "name",
        "display_name",
        "category",
        "status",
        "description",
        "trigger_terms",
        "source_path",
        "source_url",
        "trust_level",
        "permissions",
        "last_verified",
        "notes",
    ]
    values = [row.get(field, "") for field in fields]
    conn.execute(
        f"""
        INSERT OR REPLACE INTO capabilities ({", ".join(fields)})
        VALUES ({", ".join("?" for _ in fields)})
        """,
        values,
    )


def seed_routes(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT OR REPLACE INTO routes
        (category, task_signal, primary_capability, fallback_capability, ask_user_when, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ROUTE_ROWS,
    )


def export_json(conn: sqlite3.Connection, path: Path) -> None:
    rows = [dict(row) for row in conn.execute("SELECT * FROM capabilities ORDER BY status, kind, name")]
    routes = [dict(row) for row in conn.execute("SELECT * FROM routes ORDER BY category")]
    payload = {
        "generated_at": now_iso(),
        "capabilities": rows,
        "routes": routes,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def build_registry(home: Path, db_path: Path, json_path: Path) -> tuple[int, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    conn.execute("DELETE FROM capabilities WHERE status = 'installed' OR kind IN ('plugin_candidate', 'plugin_source')")
    conn.execute("DELETE FROM routes")

    count = 0
    skill_root = home / "skills"
    if skill_root.exists():
        for skill_file in skill_root.rglob("SKILL.md"):
            row = scan_skill_file(skill_file, home)
            if row:
                upsert_capability(conn, row)
                count += 1

    plugin_root = home / "plugins" / "cache"
    if plugin_root.exists():
        for manifest in plugin_root.rglob("plugin.json"):
            if manifest.parent.name != ".codex-plugin":
                continue
            row = scan_plugin_manifest(manifest)
            if row:
                upsert_capability(conn, row)
                count += 1
        for skill_file in plugin_root.rglob("SKILL.md"):
            row = scan_skill_file(skill_file, home)
            if row:
                upsert_capability(conn, row)
                count += 1

    for row in OFFICIAL_ROLE_CANDIDATES + DISCOVERY_SOURCES:
        seeded = dict(row)
        seeded.setdefault("source_path", "")
        seeded.setdefault("last_verified", now_iso())
        upsert_capability(conn, seeded)

    seed_routes(conn)
    conn.commit()
    export_json(conn, json_path)
    route_count = conn.execute("SELECT COUNT(*) FROM routes").fetchone()[0]
    conn.close()
    return count, route_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Codex capability registry.")
    parser.add_argument("--codex-home", default=str(codex_home()))
    parser.add_argument("--db", default="")
    parser.add_argument("--json", default="")
    args = parser.parse_args()

    home = Path(args.codex_home).expanduser()
    data_dir = home / "skills" / "codex-capability-router" / "data"
    db_path = Path(args.db).expanduser() if args.db else data_dir / "capabilities.sqlite"
    json_path = Path(args.json).expanduser() if args.json else data_dir / "capabilities.json"

    installed_count, route_count = build_registry(home, db_path, json_path)
    print(f"Built registry: {installed_count} installed/local capabilities, {route_count} routes")
    print(f"SQLite: {db_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
