"""Tests for dsl2wup bus and schema."""

from __future__ import annotations

from pathlib import Path

from dsl2wup import dispatch
from dsl2wup.schema_registry import validate_schema_registry


def test_validate_schema_registry() -> None:
    assert validate_schema_registry() == []


def test_parity_text_vs_dict(tmp_path: Path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\n  description: test\nwatch:\n  paths: []\nservices: []\n",
        encoding="utf-8",
    )
    line = f"VALIDATE {config} PROJECT {tmp_path}"
    r1 = dispatch(line)
    r2 = dispatch({"verb": "VALIDATE", "path": str(config), "project": str(tmp_path)}, default_file=str(tmp_path / "app.doql.less"))
    assert r1.ok == r2.ok
    assert r1.action == r2.action


def test_health_query_offline(tmp_path: Path) -> None:
    result = dispatch({"verb": "HEALTH", "project": str(tmp_path)}, default_file=str(tmp_path / "app.doql.less"))
    assert result.ok
    assert result.action == "health"


def test_init_command(tmp_path: Path) -> None:
    result = dispatch(f"INIT {tmp_path} OUT wup.yaml", default_file=str(tmp_path / "app.doql.less"))
    assert result.ok
    assert (tmp_path / "wup.yaml").exists()
