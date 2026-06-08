"""Parity across adapters: same DSL → same DslResult."""

from __future__ import annotations

import json
from pathlib import Path

from dsl2wup import dispatch
from dsl2wup.engine import execute_dsl_line
from fastapi.testclient import TestClient
from rest2wup.app import create_app
from uri2wup.decode import decode_uri
from uri2wup.uri import uri_for_block, uri_for_cmd


def _fixture_config(tmp_path: Path) -> Path:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\n  description: test\nwatch:\n  paths: []\nservices: []\n",
        encoding="utf-8",
    )
    return config


def test_parity_dispatch_vs_cli2wup_exec(tmp_path: Path) -> None:
    config = _fixture_config(tmp_path)
    line = f"VALIDATE {config} PROJECT {tmp_path}"
    r_bus = dispatch(line)
    r_cli = execute_dsl_line(line)
    assert r_bus.ok == r_cli.ok
    assert r_bus.action == r_cli.action


def test_parity_dispatch_vs_rest2wup(tmp_path: Path) -> None:
    config = _fixture_config(tmp_path)
    line = f"VALIDATE {config} PROJECT {tmp_path}"
    r_bus = dispatch(line)
    client = TestClient(create_app())
    r_rest = client.post(
        "/v1/dsl",
        json={"verb": "VALIDATE", "path": str(config), "project": str(tmp_path)},
    )
    assert r_rest.status_code == 200
    payload = r_rest.json()
    assert payload["ok"] == r_bus.ok
    assert payload["action"] == r_bus.action


def test_parity_dispatch_vs_uri2wup_run(tmp_path: Path) -> None:
    config = _fixture_config(tmp_path)
    uri = uri_for_cmd("VALIDATE", path=str(config), project=str(tmp_path))
    line = decode_uri(uri)
    r_uri = dispatch(line)
    r_bus = dispatch(f"VALIDATE {config} PROJECT {tmp_path}")
    assert r_uri.ok == r_bus.ok
    assert r_uri.action == r_bus.action


def test_parity_dispatch_vs_rest_json(tmp_path: Path) -> None:
    config = _fixture_config(tmp_path)
    body = {"verb": "VALIDATE", "path": str(config), "project": str(tmp_path)}
    r1 = dispatch(body)
    client = TestClient(create_app())
    r2 = client.post("/v1/dsl", json=body)
    assert r2.status_code == 200
    assert r2.json()["ok"] == r1.ok


def test_parity_query_via_uri_decode(tmp_path: Path) -> None:
    config = _fixture_config(tmp_path)
    block_uri = uri_for_block("project", file=str(config), project=str(tmp_path))
    line = decode_uri(block_uri)
    result = dispatch(line)
    assert result.ok
    data = json.loads(result.output) if result.output.startswith("{") else result.data
    assert data.get("name") == "demo" or result.data.get("data", {}).get("name") == "demo"
