"""Tests for rest2wup FastAPI app."""

from __future__ import annotations

from fastapi.testclient import TestClient

from rest2wup.app import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_post_dsl_health() -> None:
    client = TestClient(create_app())
    resp = client.post("/v1/dsl", content="HEALTH", headers={"content-type": "text/plain"})
    assert resp.status_code == 200
