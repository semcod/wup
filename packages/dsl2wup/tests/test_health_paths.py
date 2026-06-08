"""HEALTH verb reads canonical service-health.json."""

from __future__ import annotations

import json
from pathlib import Path

from dsl2wup import dispatch
from wup.paths import health_state_path


def test_health_reads_service_health_json(tmp_path: Path) -> None:
    state = health_state_path(tmp_path)
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"api": {"status": "up"}}), encoding="utf-8")
    result = dispatch({"verb": "HEALTH", "project": str(tmp_path)})
    assert result.ok
    assert result.data["health"]["api"]["status"] == "up"
