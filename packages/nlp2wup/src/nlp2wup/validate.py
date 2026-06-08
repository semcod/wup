"""Validate wup.yaml — thin wrapper over wup core."""

from __future__ import annotations

from typing import Any

from wup.validate import validate_wup_file


def validate_wup_config(path: str | None = None, *, project: str = ".") -> dict[str, Any]:
    return validate_wup_file(path, project=project)
