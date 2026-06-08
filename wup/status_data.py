"""Collect WUP status snapshot — domain logic for STATUS query."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from wup.config import find_config_file, load_config
from wup.paths import health_events_path, health_state_path


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _recent_health_events(events_path: Path, delta_seconds: int) -> list[dict[str, Any]]:
    if delta_seconds <= 0 or not events_path.exists():
        return []
    cutoff = int(time.time()) - delta_seconds
    recent: list[dict[str, Any]] = []
    with events_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if int(event.get("timestamp", 0)) >= cutoff:
                recent.append(event)
    recent.sort(key=lambda e: int(e.get("timestamp", 0)), reverse=True)
    return recent


def collect_status_snapshot(
    project_root: str | Path = ".",
    *,
    deps_file: str = "deps.json",
    config_file: str | None = None,
    delta_seconds: int = 0,
    failed_only: bool = False,
) -> dict[str, Any]:
    """Aggregate health, deps and config summary for STATUS / JSON output."""
    project = Path(project_root).expanduser().resolve()
    cfg_path = Path(config_file) if config_file else find_config_file(project)
    if cfg_path is not None and not cfg_path.is_absolute():
        cfg_path = project / cfg_path

    wup_config = load_config(project, cfg_path)
    health = _load_json(health_state_path(project))
    deps_path = Path(deps_file)
    if not deps_path.is_absolute():
        deps_path = project / deps_path

    deps_exists = deps_path.exists()
    deps_summary: dict[str, Any] = {}
    if deps_exists:
        try:
            raw = json.loads(deps_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                deps_summary = {
                    "services": len(raw.get("services", {})),
                    "files": len(raw.get("files", {})),
                }
        except json.JSONDecodeError:
            deps_summary = {"error": "invalid deps json"}

    failing = [
        svc
        for svc, data in health.items()
        if isinstance(data, dict) and data.get("status") == "down"
    ]
    if failed_only:
        health = {k: v for k, v in health.items() if k in failing}

    manifest: dict[str, Any] = {}
    if cfg_path and cfg_path.exists():
        from wup.monitoring_manifest import load_monitoring_manifest_from_yaml

        manifest = load_monitoring_manifest_from_yaml(cfg_path) or {}

    return {
        "ok": True,
        "project": str(project),
        "config_file": str(cfg_path) if cfg_path else "",
        "project_name": wup_config.project.name,
        "health": health,
        "failing_services": failing,
        "deps_file": str(deps_path),
        "deps_exists": deps_exists,
        "deps_summary": deps_summary,
        "monitoring_manifest": manifest,
        "recent_health_events": _recent_health_events(health_events_path(project), delta_seconds),
    }
