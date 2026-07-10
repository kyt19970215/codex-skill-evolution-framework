#!/usr/bin/env python3
"""Label and summarize local passive-trigger events."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any


def parse_time(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Event at line {line_number} is not an object: {path}")
        events.append(value)
    return events


def write_events(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    content = "".join(
        json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
        for event in events
    )
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def label_event(
    path: Path,
    event_id: str,
    actual_route: str,
    was_correct: bool,
    changed_rules: bool,
) -> bool:
    events = load_events(path)
    changed = False
    for event in events:
        if event.get("event_id") != event_id:
            continue
        event["actual_route"] = actual_route
        event["was_correct"] = was_correct
        event["changed_rules"] = changed_rules
        changed = True
        break
    if changed:
        write_events(path, events)
    return changed


def recency_weight(
    event_time: dt.datetime | None,
    now: dt.datetime,
    half_life_days: int,
) -> float:
    if event_time is None:
        return 0.0
    age_days = max(0.0, (now - event_time).total_seconds() / 86400.0)
    return math.pow(0.5, age_days / max(1, half_life_days))


def build_summary(
    events: list[dict[str, Any]],
    now: dt.datetime | None = None,
    half_life_days: int = 30,
) -> dict[str, Any]:
    current = now or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    else:
        current = current.astimezone(dt.timezone.utc)

    summary: dict[str, Any] = {
        "total": len(events),
        "real_hook_events": 0,
        "smoke_test_events": 0,
        "labeled": 0,
        "unlabeled": 0,
        "routes": {},
        "half_life_days": half_life_days,
    }
    for event in events:
        evidence_kind = event.get("evidence_kind")
        if evidence_kind == "smoke_test":
            summary["smoke_test_events"] += 1
        elif event.get("hook_event") == "UserPromptSubmit":
            summary["real_hook_events"] += 1

        route = str(event.get("suggested_route") or "[no-route]")
        route_stats = summary["routes"].setdefault(
            route,
            {
                "count": 0,
                "weighted_score": 0.0,
                "correct": 0,
                "incorrect": 0,
                "unlabeled": 0,
            },
        )
        route_stats["count"] += 1
        route_stats["weighted_score"] += recency_weight(
            parse_time(event.get("time")), current, half_life_days
        )

        correctness = event.get("was_correct")
        if correctness is True:
            route_stats["correct"] += 1
            summary["labeled"] += 1
        elif correctness is False:
            route_stats["incorrect"] += 1
            summary["labeled"] += 1
        else:
            route_stats["unlabeled"] += 1
            summary["unlabeled"] += 1

    for stats in summary["routes"].values():
        stats["weighted_score"] = round(stats["weighted_score"], 6)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local trigger-event evidence.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="Print a recency-weighted summary.")
    summary.add_argument("--ledger", required=True)
    summary.add_argument("--half-life-days", type=int, default=30)

    label = subparsers.add_parser("label", help="Attach an observed route outcome.")
    label.add_argument("--ledger", required=True)
    label.add_argument("--event-id", required=True)
    label.add_argument("--actual-route", required=True)
    label.add_argument("--was-correct", choices=("true", "false"), required=True)
    label.add_argument("--changed-rules", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ledger = Path(args.ledger).expanduser()
    if args.command == "summary":
        print(
            json.dumps(
                build_summary(
                    load_events(ledger), half_life_days=max(1, args.half_life_days)
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    changed = label_event(
        ledger,
        event_id=args.event_id,
        actual_route=args.actual_route,
        was_correct=args.was_correct == "true",
        changed_rules=bool(args.changed_rules),
    )
    print(json.dumps({"updated": changed, "event_id": args.event_id}))
    return 0 if changed else 1


if __name__ == "__main__":
    raise SystemExit(main())
