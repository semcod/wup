"""Tests for wup.control shim."""

from __future__ import annotations

from pathlib import Path

from wup.control import dispatch_validate


def test_dispatch_validate_shim(tmp_path: Path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\n  description: test\nwatch:\n  paths: []\nservices: []\n",
        encoding="utf-8",
    )
    result = dispatch_validate(str(config), project=str(tmp_path))
    assert "ok" in result
    assert result["action"] == "validate"
