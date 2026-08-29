"""Tests for endpoints + init_cli domain and bus."""

from __future__ import annotations

from pathlib import Path

import yaml

from dsl2wup import dispatch
from wup.endpoints import discover_testql_endpoints
from wup.init_cli import setup_cli_project


def _write_scenario(dir_path: Path, name: str = "smoke.testql.toon.yaml") -> Path:
    dir_path.mkdir(parents=True, exist_ok=True)
    scenario = dir_path / name
    scenario.write_text(
        yaml.safe_dump(
            {
                "name": "smoke",
                "service": "api",
                "steps": [{"request": {"method": "GET", "url": "/health"}}],
            }
        ),
        encoding="utf-8",
    )
    return scenario


def test_discover_testql_endpoints(tmp_path: Path) -> None:
    scen = tmp_path / "scenarios"
    _write_scenario(scen)
    result = discover_testql_endpoints(scen, out=tmp_path / "deps.json")
    assert result["ok"]
    assert (tmp_path / "deps.json").exists()


def test_endpoints_via_bus(tmp_path: Path) -> None:
    scen = tmp_path / "scenarios"
    _write_scenario(scen)
    result = dispatch(
        f"ENDPOINTS {scen} OUT {tmp_path / 'out.json'}",
        default_file=str(tmp_path / "app.doql.less"),
    )
    assert result.ok
    assert (tmp_path / "out.json").exists()


def test_init_cli_via_bus(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n\n[project.scripts]\n demo = "demo:main"\n',
        encoding="utf-8",
    )
    (tmp_path / "demo").mkdir()
    (tmp_path / "demo" / "__init__.py").write_text("def main(): pass\n", encoding="utf-8")
    result = dispatch(
        f"INIT_CLI {tmp_path} OUT wup.yaml SCENARIOS testql-scenarios",
        default_file=str(tmp_path / "app.doql.less"),
    )
    assert result.ok
    assert (tmp_path / "wup.yaml").exists()
    assert (tmp_path / "testql-scenarios").is_dir()


def test_setup_cli_project_core(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n\n[project.scripts]\n demo = "demo:main"\n',
        encoding="utf-8",
    )
    (tmp_path / "demo").mkdir()
    (tmp_path / "demo" / "__init__.py").write_text("def main(): pass\n", encoding="utf-8")
    payload = setup_cli_project(tmp_path)
    assert payload["ok"]
    assert payload["commands"] >= 1
