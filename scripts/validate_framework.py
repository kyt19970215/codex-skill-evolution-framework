#!/usr/bin/env python3
"""Validate the public skill framework without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".json", ".txt"}
FORBIDDEN_SUFFIXES = {".sqlite", ".sqlite3", ".db", ".pyc", ".zip"}
IGNORED_DIRECTORIES = {".git", ".worktrees", "__pycache__", ".venv", ".pytest_cache", ".mypy_cache"}
NAME_RE = re.compile(r"^[a-z0-9-]{1,63}$")
REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_/-])((?:references|scripts|assets)/[A-Za-z0-9._/-]+\.(?:md|py|yaml|yml|json))"
)
PRIVACY_PATTERNS = {
    "Windows absolute path": re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/]") ,
    "user home path": re.compile(
        r"(?i)(?:/"
        + "Users"
        + r"/[^/\s]+|/"
        + "home"
        + r"/[^/\s]+|\\"
        + "Users"
        + r"\\[^\\\s]+)"
    ),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail(errors, f"Non-UTF-8 text: {path.relative_to(ROOT)}")
        return ""


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail(errors, f"Missing YAML frontmatter: {path.relative_to(ROOT)}")
        return {}
    try:
        block = text.split("---\n", 2)[1]
    except IndexError:
        fail(errors, f"Unclosed YAML frontmatter: {path.relative_to(ROOT)}")
        return {}
    values: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(errors, f"Malformed frontmatter line in {path.relative_to(ROOT)}: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def validate_skill_bundle(
    skill_dir: Path, errors: list[str], expected_name: str | None = None
) -> None:
    skill_file = skill_dir / "SKILL.md"
    agent_file = skill_dir / "agents" / "openai.yaml"
    if not skill_file.is_file():
        fail(errors, f"Missing SKILL.md: {skill_dir.relative_to(ROOT)}")
        return
    if not agent_file.is_file():
        fail(errors, f"Missing agents/openai.yaml: {skill_dir.relative_to(ROOT)}")
    text = read_text(skill_file, errors)
    frontmatter = parse_frontmatter(skill_file, text, errors)
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    wanted_name = expected_name or skill_dir.name
    if name != wanted_name:
        fail(errors, f"Skill name does not match expected name: {skill_dir.relative_to(ROOT)}")
    if not NAME_RE.fullmatch(name):
        fail(errors, f"Invalid skill name: {name!r}")
    if not description:
        fail(errors, f"Missing description: {skill_file.relative_to(ROOT)}")
    unexpected = set(frontmatter) - {"name", "description"}
    if unexpected:
        fail(errors, f"Unexpected frontmatter keys in {skill_file.relative_to(ROOT)}: {sorted(unexpected)}")
    if agent_file.is_file():
        agent_text = read_text(agent_file, errors)
        for key in ("display_name:", "short_description:", "default_prompt:"):
            if key not in agent_text:
                fail(errors, f"Missing {key} in {agent_file.relative_to(ROOT)}")
        if f"${name}" not in agent_text:
            fail(errors, f"Default prompt does not reference ${name}: {agent_file.relative_to(ROOT)}")
    for match in REFERENCE_RE.finditer(text):
        relative = Path(match.group(1))
        if not (skill_dir / relative).exists():
            fail(errors, f"Missing referenced file from {skill_file.relative_to(ROOT)}: {relative}")


def validate_skills(errors: list[str]) -> tuple[int, int]:
    count = 0
    for skill_dir in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        count += 1
        validate_skill_bundle(skill_dir, errors)
    template_dir = ROOT / "templates" / "project-skill-template"
    template_count = 0
    if template_dir.is_dir():
        template_count = 1
        validate_skill_bundle(template_dir, errors, expected_name="example-project")
    else:
        fail(errors, "Missing project skill template")
    return count, template_count


def validate_files(errors: list[str]) -> tuple[int, int]:
    text_count = 0
    script_count = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(errors, f"Forbidden generated artifact: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text_count += 1
        text = read_text(path, errors)
        for label, pattern in PRIVACY_PATTERNS.items():
            if pattern.search(text):
                fail(errors, f"Possible {label}: {relative}")
        if path.suffix.lower() == ".py":
            script_count += 1
            try:
                compile(text, str(relative), "exec")
            except SyntaxError as exc:
                fail(errors, f"Python syntax error in {relative}:{exc.lineno}: {exc.msg}")
    return text_count, script_count


def main() -> int:
    errors: list[str] = []
    if not SKILLS.is_dir():
        print("ERROR: skills directory is missing", file=sys.stderr)
        return 1
    skill_count, template_count = validate_skills(errors)
    text_count, script_count = validate_files(errors)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Validation passed: {skill_count} skills, {template_count} template, "
        f"{text_count} text files, {script_count} Python scripts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
