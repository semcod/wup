#!/usr/bin/env python3
"""Create a deduplicated local Planfile ticket for a canonical refactoring plan.

The command is intentionally dry-run by default.  It never uses ``--sync``:
refactoring work starts as local triage and may be published only through the
repository's reviewed Planfile lifecycle.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


DOCUMENT_SCHEMA = "wellmanifest.docs/document/v1"
PLAN_KIND = "refactoring-plan"
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)


def canonical_plan_path(identifier: str) -> Path:
    """Return the only supported repository-relative refactoring-plan path."""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
        raise ValueError("identifier must be a lowercase slug")
    return Path("docs") / "refactoring" / f"{identifier}.md"


def read_plan(root: Path, identifier: str) -> tuple[Path, dict[str, Any]]:
    """Load and validate the minimum canonical-document contract."""
    relative = canonical_plan_path(identifier)
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"canonical refactoring plan is missing: {relative}")
    match = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"canonical refactoring plan has no JSON metadata: {relative}")
    try:
        metadata = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError(f"canonical refactoring plan has invalid JSON metadata: {relative}") from exc
    if metadata.get("schema") != DOCUMENT_SCHEMA:
        raise ValueError(f"canonical refactoring plan has wrong schema: {relative}")
    if metadata.get("kind") != PLAN_KIND or metadata.get("id") != identifier:
        raise ValueError(f"canonical refactoring plan has wrong kind or id: {relative}")
    return relative, metadata


def ticket_contains_path(ticket: dict[str, Any], relative: Path) -> bool:
    """Return whether a Planfile ticket already owns this canonical plan."""
    needle = relative.as_posix()
    if needle in str(ticket.get("description", "")):
        return True
    outputs = ticket.get("outputs", {})
    notes = outputs.get("notes", []) if isinstance(outputs, dict) else []
    return any(needle in str(note) for note in notes)


def find_existing_ticket(tickets: Iterable[dict[str, Any]], relative: Path) -> str | None:
    """Find the open ticket already linked to a canonical plan."""
    for ticket in tickets:
        if isinstance(ticket, dict) and ticket_contains_path(ticket, relative):
            ticket_id = str(ticket.get("id", "")).strip()
            if ticket_id:
                return ticket_id
    return None


def build_create_command(
    planfile_command: str,
    title: str,
    summary: str,
    relative: Path,
    priority: str,
    files: Iterable[str],
) -> list[str]:
    """Build the local-triage command without a GitHub integration or sync."""
    description = f"Canonical refactoring plan: {relative.as_posix()}\n\n{summary.strip()}"
    command = [
        planfile_command,
        "ticket",
        "create",
        f"Refactor: {title.strip()}",
        "--priority",
        priority,
        "--source",
        "refactoring-planner",
        "--label",
        "refactoring",
        "--label",
        "triage",
        "--description",
        description,
    ]
    for file_name in files:
        command.extend(["--files", file_name])
    return command


def load_open_tickets(root: Path, planfile_command: str) -> list[dict[str, Any]]:
    """Read open tickets from Planfile, failing closed on an unreadable store."""
    result = subprocess.run(
        [planfile_command, "ticket", "list", "--status", "open", "--format", "json"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise RuntimeError(f"cannot read open Planfile tickets: {detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Planfile returned invalid ticket JSON") from exc
    if not isinstance(payload, list):
        raise RuntimeError("Planfile ticket list must be a JSON array")
    return [ticket for ticket in payload if isinstance(ticket, dict)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="Canonical docs/refactoring slug")
    parser.add_argument("--title", required=True, help="Short ticket title")
    parser.add_argument("--summary", required=True, help="Bounded intent and acceptance summary")
    parser.add_argument("--priority", choices=("critical", "high", "normal", "low"), default="normal")
    parser.add_argument("--file", action="append", default=[], help="Repository-relative file in scope")
    parser.add_argument("--planfile-command", default="planfile")
    parser.add_argument("--apply", action="store_true", help="Create the local triage ticket")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd().resolve()
    try:
        relative, _metadata = read_plan(root, args.id)
        existing = find_existing_ticket(load_open_tickets(root, args.planfile_command), relative)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}")
        return 2

    if existing:
        print(json.dumps({"action": "existing", "ticket_id": existing, "plan": relative.as_posix()}))
        return 0

    command = build_create_command(
        args.planfile_command, args.title, args.summary, relative, args.priority, args.file
    )
    if not args.apply:
        print(json.dumps({"action": "create", "plan": relative.as_posix(), "command": command}))
        return 0

    result = subprocess.run(command, cwd=root, text=True, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
