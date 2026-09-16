"""Tests for the local, deduplicated refactoring-ticket planner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "plan_refactoring_ticket.py"
SPEC = importlib.util.spec_from_file_location("plan_refactoring_ticket", SCRIPT)
assert SPEC and SPEC.loader
planner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(planner)


def write_plan(root: Path, identifier: str = "sample-plan") -> Path:
    path = root / "docs" / "refactoring" / f"{identifier}.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "---\n"
        + json.dumps(
            {
                "schema": planner.DOCUMENT_SCHEMA,
                "id": identifier,
                "kind": planner.PLAN_KIND,
            }
        )
        + "\n---\n# plan\n",
        encoding="utf-8",
    )
    return path


def test_read_plan_requires_canonical_path_and_matching_metadata(tmp_path: Path) -> None:
    write_plan(tmp_path)
    relative, metadata = planner.read_plan(tmp_path, "sample-plan")
    assert relative == Path("docs/refactoring/sample-plan.md")
    assert metadata["id"] == "sample-plan"


def test_read_plan_rejects_mismatched_identifier(tmp_path: Path) -> None:
    write_plan(tmp_path, "other-plan")
    with pytest.raises(ValueError, match="missing"):
        planner.read_plan(tmp_path, "sample-plan")


def test_find_existing_ticket_uses_canonical_document_link() -> None:
    relative = Path("docs/refactoring/sample-plan.md")
    tickets = [
        {"id": "PLF-10", "description": "Canonical refactoring plan: docs/refactoring/sample-plan.md"},
        {"id": "PLF-11", "description": "unrelated"},
    ]
    assert planner.find_existing_ticket(tickets, relative) == "PLF-10"


def test_create_command_is_local_triage_without_integration_or_sync() -> None:
    command = planner.build_create_command(
        "planfile", "Improve planner", "acceptance", Path("docs/refactoring/sample-plan.md"), "high", ["wup/core.py"]
    )
    assert "--sync" not in command
    assert "--integration" not in command
    assert command.count("--label") == 2
    assert "triage" in command
    assert "docs/refactoring/sample-plan.md" in command[-3]
