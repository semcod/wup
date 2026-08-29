"""Tests for STATUS snapshot."""

from __future__ import annotations

import json
from pathlib import Path

from dsl2wup import dispatch
from wup.paths import health_state_path
from wup.status_data import collect_status_snapshot


def test_collect_status_snapshot(tmp_path: Path) -> None:
    (tmp_path / "wup.yaml").write_text(
        "project:\n  name: demo\n  description: t\nwatch:\n  paths: []\nservices:\n  - name: api\n    type: web\n",
        encoding="utf-8",
    )
    state = health_state_path(tmp_path)
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"api": {"status": "up"}}), encoding="utf-8")
    snap = collect_status_snapshot(tmp_path)
    assert snap["ok"]
    assert snap["project_name"] == "demo"
    assert "api" in snap["health"]


def test_status_via_bus(tmp_path: Path) -> None:
    (tmp_path / "wup.yaml").write_text(
        "project:\n  name: demo\nwatch:\n  paths: []\nservices:\n  - name: api\n    type: web\n",
        encoding="utf-8",
    )
    result = dispatch(
        f"STATUS PROJECT {tmp_path} FILE wup.yaml",
        default_file=str(tmp_path / "app.doql.less"),
    )
    assert result.ok
    assert result.data["project_name"] == "demo"
