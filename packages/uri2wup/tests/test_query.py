"""Tests for uri2wup query."""

from __future__ import annotations

from pathlib import Path

from uri2wup.query import query_uri


def test_query_config_block(tmp_path: Path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text("project:\n  name: demo\nwatch:\n  paths: []\nservices: []\n", encoding="utf-8")
    result = query_uri(
        "wup://block/project",
        file=str(config),
        project=str(tmp_path),
    )
    assert result.ok
    assert result.data["name"] == "demo"
