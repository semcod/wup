"""Validate wup.yaml configuration — domain logic (core)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wup.assistant_validator import validate_config
from wup.config import find_config_file, load_config


def validate_wup_file(path: str | None = None, *, project: str = ".") -> dict[str, Any]:
    """Validate a wup.yaml file and return a structured result dict."""
    project_path = Path(project).expanduser().resolve()
    config_path = Path(path).expanduser() if path else find_config_file(project_path)
    if config_path is not None and not config_path.is_absolute():
        config_path = project_path / config_path
    try:
        config = load_config(project_path, config_path)
        issues = validate_config(config, project_path)
        return {
            "ok": not issues,
            "issues": issues,
            "path": str(config_path or ""),
            "project": str(project_path),
        }
    except Exception as exc:
        return {
            "ok": False,
            "issues": [str(exc)],
            "path": str(config_path or path or ""),
            "project": str(project_path),
            "error": str(exc),
        }
