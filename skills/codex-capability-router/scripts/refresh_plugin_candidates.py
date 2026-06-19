#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh public GitHub Codex plugin candidate leads.

This script records candidates only. It never installs or enables plugins.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_QUERIES = [
    "codex plugin",
    "codex-plugin",
    "awesome codex plugins",
    ".codex-plugin plugin.json",
]


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_db() -> Path:
    return codex_home() / "skills" / "codex-capability-router" / "data" / "capabilities.sqlite"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def http_json(url: str, timeout: int = 20) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "codex-capability-router",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def http_text(url: str, timeout: int = 20) -> str | None:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-capability-router"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None


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


def upsert(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
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
    conn.execute(
        f"INSERT OR REPLACE INTO capabilities ({', '.join(fields)}) VALUES ({', '.join('?' for _ in fields)})",
        [row.get(field, "") for field in fields],
    )


def export_json(conn: sqlite3.Connection, db_path: Path) -> None:
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute("SELECT * FROM capabilities ORDER BY status, kind, name")]
    routes = []
    try:
        routes = [dict(row) for row in conn.execute("SELECT * FROM routes ORDER BY category")]
    except sqlite3.OperationalError:
        routes = []
    payload = {
        "generated_at": now_iso(),
        "capabilities": rows,
        "routes": routes,
    }
    db_path.with_suffix(".json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def category_from_text(text: str) -> str:
    lower = text.lower()
    def has_term(term: str) -> bool:
        needle = term.lower()
        if re.search(r"[\u4e00-\u9fff]", needle):
            return needle in lower
        if " " in needle or "-" in needle:
            return needle in lower
        return re.search(rf"\b{re.escape(needle)}\b", lower) is not None

    for category, terms in {
        "product_design": ["product design", "figma", "prototype", "ux", "ui"],
        "business_analysis": ["data", "analytics", "dashboard", "business", "metrics"],
        "creative_production": ["creative", "marketing", "campaign", "image"],
        "sales": ["sales", "crm", "customer"],
        "finance_investing": ["finance", "investing", "equity", "banking"],
        "github": ["github", "review", "pull request"],
        "plugin_discovery": ["plugin", "codex"],
    }.items():
        if any(has_term(term) for term in terms):
            return category
    return "plugin_discovery"


def inspect_manifest(full_name: str, default_branch: str) -> dict[str, Any] | None:
    raw = f"https://raw.githubusercontent.com/{full_name}/{default_branch}/.codex-plugin/plugin.json"
    text = http_text(raw)
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    interface = data.get("interface") or {}
    name = data.get("name") or full_name.split("/")[-1]
    desc = data.get("description") or interface.get("longDescription") or interface.get("shortDescription") or ""
    return {
        "name": name,
        "display_name": interface.get("displayName") or name,
        "description": desc,
        "trigger_terms": " ".join([name, desc, " ".join(data.get("keywords") or [])]),
        "trust_level": "community-candidate",
        "notes": "Confirmed .codex-plugin/plugin.json at repository root.",
    }


def search_repos(query: str, limit: int) -> list[dict[str, Any]]:
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": query, "sort": "updated", "order": "desc", "per_page": str(limit)}
    )
    data = http_json(url)
    return list(data.get("items") or [])


def refresh(db_path: Path, query: str | None, limit: int) -> list[dict[str, Any]]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    ensure_schema(conn)
    queries = DEFAULT_QUERIES.copy()
    if query:
        queries.insert(0, query)
    inserted: list[dict[str, Any]] = []
    seen: set[str] = set()
    for q in queries:
        try:
            repos = search_repos(q, limit)
        except urllib.error.HTTPError as exc:
            inserted.append({"query": q, "error": f"HTTP {exc.code}: {exc.reason}"})
            continue
        except Exception as exc:
            inserted.append({"query": q, "error": str(exc)})
            continue
        for repo in repos:
            full_name = repo.get("full_name")
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)
            desc = repo.get("description") or ""
            manifest = inspect_manifest(full_name, repo.get("default_branch") or "main")
            trust = "community-candidate" if manifest else "unverified-lead"
            name = full_name.split("/")[-1]
            row = {
                "id": f"github:{full_name}",
                "kind": "github_candidate",
                "name": manifest.get("name") if manifest else name,
                "display_name": manifest.get("display_name") if manifest else name,
                "category": category_from_text(f"{full_name} {desc}"),
                "status": "candidate",
                "description": manifest.get("description") if manifest else desc,
                "trigger_terms": manifest.get("trigger_terms") if manifest else f"{full_name} {desc}",
                "source_path": "",
                "source_url": repo.get("html_url") or f"https://github.com/{full_name}",
                "trust_level": manifest.get("trust_level") if manifest else trust,
                "permissions": "Unknown until manifest, hooks, MCP, commands, and app connectors are inspected.",
                "last_verified": now_iso(),
                "notes": manifest.get("notes") if manifest else "Repository search lead; manifest not confirmed at repository root.",
            }
            upsert(conn, row)
            inserted.append(row)
    conn.commit()
    export_json(conn, db_path)
    conn.close()
    return inserted


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh GitHub Codex plugin candidate leads.")
    parser.add_argument("--query", default="")
    parser.add_argument("--db", default=str(default_db()))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    rows = refresh(Path(args.db).expanduser(), args.query or None, args.limit)
    if args.format == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for row in rows:
            if "error" in row:
                print(f"{row['query']}: {row['error']}")
            else:
                print(f"{row['display_name']} [{row['trust_level']}] - {row['source_url']}")
    print("Candidates only; do not install without user confirmation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
