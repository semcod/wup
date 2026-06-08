"""Tests for wup.cli_bridge → bus delegation."""

from __future__ import annotations

from pathlib import Path

from wup.cli_bridge import run_init, run_map_deps, run_validate


def test_bridge_init(tmp_path: Path) -> None:
    result = run_init(project=str(tmp_path), out="wup.yaml")
    assert result["ok"]
    assert (tmp_path / "wup.yaml").exists()


def test_bridge_map_deps(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
    (tmp_path / "wup.yaml").write_text(
        "project:\n  name: demo\nwatch:\n  paths: []\nservices: []\n",
        encoding="utf-8",
    )
    result = run_map_deps(project=str(tmp_path), out="deps.json", framework="auto")
    assert result["ok"]
    assert (tmp_path / "deps.json").exists()


def test_bridge_validate(tmp_path: Path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\n  description: test\nwatch:\n  paths: []\n"
        "services:\n  - name: api\n    type: web\n",
        encoding="utf-8",
    )
    result = run_validate(path=str(config), project=str(tmp_path))
    assert "ok" in result
