"""Discover TestQL endpoints — domain logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wup.testql_discovery import TestQLEndpointDiscovery


def discover_testql_endpoints(
    scenarios_dir: str | Path,
    *,
    testql_bin: str = "testql",
    out: str | Path = "testql-deps.json",
) -> dict[str, Any]:
    """Discover endpoints from TestQL scenarios and optionally save deps map."""
    scenarios_path = Path(scenarios_dir).expanduser().resolve()
    if not scenarios_path.exists():
        return {"ok": False, "error": f"scenarios dir not found: {scenarios_path}"}

    discovery = TestQLEndpointDiscovery(str(scenarios_path), testql_bin)
    dependency_map = discovery.to_dependency_map()

    out_path = Path(out).expanduser()
    if not out_path.is_absolute():
        out_path = Path.cwd() / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dependency_map, indent=2), encoding="utf-8")

    services = dependency_map.get("services", {})
    total_endpoints = sum(len(info.get("endpoints", [])) for info in services.values())
    total_scenarios = sum(len(info.get("scenarios", [])) for info in services.values())

    return {
        "ok": True,
        "scenarios_dir": str(scenarios_path),
        "output": str(out_path),
        "services": len(services),
        "total_endpoints": total_endpoints,
        "total_scenarios": total_scenarios,
        "map": dependency_map,
    }
