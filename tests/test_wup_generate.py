"""Tests for wup.generate."""

from __future__ import annotations

from pathlib import Path

from wup.generate import generate_wup_config


def test_generate_fastapi_config(tmp_path: Path) -> None:
    result = generate_wup_config(tmp_path, hint="fastapi project", out="wup.yaml")
    assert result["ok"]
    assert (tmp_path / "wup.yaml").exists()
    assert result["framework"] == "fastapi"
    assert result["services"] >= 1


def test_generate_refuses_existing_without_overwrite(tmp_path: Path) -> None:
    (tmp_path / "wup.yaml").write_text("project:\n  name: x\n", encoding="utf-8")
    result = generate_wup_config(tmp_path, hint="flask", out="wup.yaml")
    assert not result["ok"]
