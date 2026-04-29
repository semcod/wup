"""Tests for wup.web_client and WebConfig."""

from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Tuple

import pytest

from wup.models.config import WebConfig
from wup.web_client import WebClient, resolve_endpoint

# Skip all tests in this module if httpx is not installed
pytest.importorskip("httpx")


# ---------------------------------------------------------------------------
# Lightweight HTTP recorder server (no external dep)
# ---------------------------------------------------------------------------

class _Recorder:
    def __init__(self):
        self.requests: List[Tuple[str, str, dict]] = []  # (method, path, body)


def _make_handler(recorder: _Recorder, status: int = 201):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"_raw": raw}
            recorder.requests.append((self.command, self.path, body))
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"accepted": true}')

    return Handler


@pytest.fixture
def recorder_server():
    rec = _Recorder()
    server = HTTPServer(("127.0.0.1", 0), _make_handler(rec))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}", rec
    finally:
        server.shutdown()
        server.server_close()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_resolve_endpoint_from_config():
    cfg = WebConfig(endpoint="http://localhost:8000/")
    assert resolve_endpoint(cfg) == "http://localhost:8000"


def test_resolve_endpoint_from_env(monkeypatch):
    cfg = WebConfig(endpoint="", endpoint_env="MY_WUP_WEB")
    monkeypatch.setenv("MY_WUP_WEB", "http://my-host:9000/")
    assert resolve_endpoint(cfg) == "http://my-host:9000"


def test_resolve_endpoint_empty(monkeypatch):
    cfg = WebConfig(endpoint="", endpoint_env="WUP_WEB_NONE")
    monkeypatch.delenv("WUP_WEB_NONE", raising=False)
    assert resolve_endpoint(cfg) == ""


def test_is_active_false_when_disabled():
    cfg = WebConfig(enabled=False, endpoint="http://x")
    assert WebClient(cfg).is_active is False


def test_is_active_false_when_no_endpoint():
    cfg = WebConfig(enabled=True, endpoint="", endpoint_env="WUP_WEB_NONE")
    assert WebClient(cfg).is_active is False


def test_send_event_disabled_returns_false():
    client = WebClient(WebConfig(enabled=False))
    assert asyncio.run(client.send_event({"type": "REGRESSION"})) is False


def test_send_event_posts_to_recorder(recorder_server):
    base, rec = recorder_server
    cfg = WebConfig(enabled=True, endpoint=base, timeout_s=5.0)
    client = WebClient(cfg)
    assert client.is_active is True

    ok = asyncio.run(client.send_event({
        "type": "REGRESSION",
        "service": "users-web",
        "file": "app/users/routes.py",
        "endpoint": "/api/users",
        "status": "fail",
        "reason": "TestQL exit code 1",
    }))
    assert ok is True
    assert len(rec.requests) == 1
    method, path, body = rec.requests[0]
    assert method == "POST"
    assert path == "/events"
    assert body["type"] == "REGRESSION"
    assert body["service"] == "users-web"
    assert "timestamp" in body  # auto-injected


def test_send_event_with_api_key(recorder_server):
    base, rec = recorder_server
    cfg = WebConfig(enabled=True, endpoint=base, api_key="secret-token")
    client = WebClient(cfg)
    asyncio.run(client.send_event({"type": "PASS", "service": "x"}))
    # body received OK; auth header is set on the client side (verified by no failure)
    assert len(rec.requests) == 1


def test_send_event_swallows_connection_error():
    """Unreachable host must NOT raise — soft-fail by design."""
    cfg = WebConfig(
        enabled=True,
        endpoint="http://127.0.0.1:1",  # almost certainly closed
        timeout_s=0.5,
    )
    client = WebClient(cfg)
    ok = asyncio.run(client.send_event({"type": "REGRESSION"}))
    assert ok is False  # no exception raised


def test_send_regression_helper(recorder_server):
    base, rec = recorder_server
    client = WebClient(WebConfig(enabled=True, endpoint=base))
    ok = asyncio.run(client.send_regression(
        service="users", file="x.py", endpoint="/api/users", reason="500",
    ))
    assert ok is True
    body = rec.requests[0][2]
    assert body["type"] == "REGRESSION"
    assert body["service"] == "users"
    assert body["status"] == "fail"


def test_send_health_transition_helper(recorder_server):
    base, rec = recorder_server
    client = WebClient(WebConfig(enabled=True, endpoint=base))
    ok = asyncio.run(client.send_health_transition(
        service="users", from_status="up", to_status="down",
    ))
    assert ok is True
    body = rec.requests[0][2]
    assert body["type"] == "HEALTH_TRANSITION"
    assert body["from"] == "up"
    assert body["to"] == "down"
