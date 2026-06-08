"""Sync TestQL monitoring manifest into wup.yaml — domain logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from wup.config import find_config_file, load_config
from wup.monitoring_manifest import build_monitoring_manifest, patch_wup_yaml_monitoring
from wup.testql_monitor import TestQLMonitor


def _merge_endpoints(config_path: Path, wup_config, suggested: dict, project_path: Path) -> dict[str, Any]:
    merged = dict(wup_config.testql.endpoints_by_service or {})
    for service, paths in suggested.items():
        existing = set(merged.get(service, []))
        existing.update(paths)
        merged[service] = sorted(existing)

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    raw.setdefault("testql", {})["endpoints_by_service"] = merged
    wup_config.testql.endpoints_by_service = merged

    manifest = build_monitoring_manifest(project_path, wup_config)
    body = yaml.safe_dump(
        {k: v for k, v in raw.items() if k != "monitoring"},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    config_path.write_text(body.rstrip() + "\n\n", encoding="utf-8")
    return manifest


def sync_testql_manifest(
    project_root: str | Path,
    *,
    config_file: str | None = None,
    merge_endpoints: bool = False,
    write: bool = True,
) -> dict[str, Any]:
    """Build (and optionally write) monitoring manifest for wup.yaml."""
    project = Path(project_root).expanduser().resolve()
    config_path = Path(config_file) if config_file else find_config_file(project)
    if config_path is not None and not config_path.is_absolute():
        config_path = project / config_path
    if config_path is None or not config_path.exists():
        return {"ok": False, "error": "wup.yaml not found", "project": str(project)}

    wup_config = load_config(project, config_path)
    monitor = TestQLMonitor(project, wup_config)
    suggested = monitor.suggested_endpoints_by_service()
    manifest = build_monitoring_manifest(project, wup_config)

    if merge_endpoints and suggested:
        manifest = _merge_endpoints(config_path, wup_config, suggested, project)

    if write:
        patch_wup_yaml_monitoring(config_path, manifest)

    return {
        "ok": True,
        "file": str(config_path),
        "manifest": manifest,
        "suggested_endpoints": suggested,
        "merge_endpoints": merge_endpoints,
        "project": str(project),
    }
