"""Tests for wup.sync."""

from __future__ import annotations

from pathlib import Path

import yaml

from wup.sync import sync_testql_manifest


def _minimal_config(path: Path) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "project": {"name": "demo", "description": "test"},
                "watch": {"paths": [], "exclude_patterns": [], "file_types": []},
                "services": [{"name": "api", "type": "web"}],
                "testql": {"scenario_dir": "scenarios", "endpoints_by_service": {"api": ["/health"]}},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_sync_writes_manifest(tmp_path: Path) -> None:
    cfg = tmp_path / "wup.yaml"
    _minimal_config(cfg)
    result = sync_testql_manifest(tmp_path, config_file=str(cfg), write=True)
    assert result["ok"]
    text = cfg.read_text(encoding="utf-8")
    assert "BEGIN WUP MONITORING MANIFEST" in text


def test_sync_merge_endpoints_flag(tmp_path: Path) -> None:
    cfg = tmp_path / "wup.yaml"
    _minimal_config(cfg)
    result = sync_testql_manifest(tmp_path, config_file=str(cfg), merge_endpoints=True, write=True)
    assert result["ok"]
    assert "merge_endpoints" in result
