"""Tests for OQL — the Observability Query Language."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from wup.bus import EventBus
from wup.oql import Condition, OQLEngine, OQLError, RunOQL, parse, register_oql


def _project(tmp_path: Path) -> Path:
    now = int(time.time())
    wup = tmp_path / ".wup"
    wup.mkdir()
    (wup / "service-health.json").write_text(json.dumps({
        "api": {"status": "down", "updated_at": now, "stage": "probe", "message": "500 error"},
        "web": {"status": "up", "updated_at": now, "stage": "probe", "message": ""},
        "worker": {"status": "degraded", "updated_at": now - 500, "stage": "quick", "message": "slow"},
    }))
    (wup / "service-health-events.jsonl").write_text(
        json.dumps({"service": "api", "status": "down", "timestamp": now}) + "\n"
        + json.dumps({"service": "web", "status": "up", "timestamp": now - 4000}) + "\n"
    )
    return tmp_path


# --- parsing --------------------------------------------------------------

def test_parse_minimal() -> None:
    q = parse("services")
    assert q.source == "services" and q.conditions == [] and q.limit is None


def test_parse_full() -> None:
    q = parse("events where service = api and status != up since 1h limit 5")
    assert q.source == "events"
    assert q.conditions == [Condition("service", "=", "api"), Condition("status", "!=", "up")]
    assert q.since_seconds == 3600
    assert q.limit == 5


def test_parse_operator_without_spaces() -> None:
    q = parse("services where status=down")
    assert q.conditions == [Condition("status", "=", "down")]


@pytest.mark.parametrize("bad", [
    "", "widgets", "services where", "services where status", "services since",
    "services limit x", "services since 5x",
])
def test_parse_errors(bad: str) -> None:
    with pytest.raises(OQLError):
        parse(bad)


# --- execution ------------------------------------------------------------

def test_filter_equals(tmp_path: Path) -> None:
    engine = OQLEngine(_project(tmp_path))
    rows = engine.execute("services where status = down")
    assert [r["name"] for r in rows] == ["api"]


def test_filter_not_equals(tmp_path: Path) -> None:
    engine = OQLEngine(_project(tmp_path))
    assert {r["name"] for r in engine.execute("services where status != up")} == {"api", "worker"}


def test_contains_operator(tmp_path: Path) -> None:
    engine = OQLEngine(_project(tmp_path))
    assert [r["name"] for r in engine.execute("services where message ~ error")] == ["api"]


def test_since_filters_old_events(tmp_path: Path) -> None:
    engine = OQLEngine(_project(tmp_path))
    rows = engine.execute("events since 10m")
    assert [r["service"] for r in rows] == ["api"]  # web event (4000s old) excluded


def test_limit(tmp_path: Path) -> None:
    engine = OQLEngine(_project(tmp_path))
    assert len(engine.execute("services limit 1")) == 1


def test_numeric_comparison(tmp_path: Path) -> None:
    engine = OQLEngine(_project(tmp_path))
    now = int(time.time())
    rows = engine.execute(f"services where updated_at > {now - 100}")
    assert {r["name"] for r in rows} == {"api", "web"}  # worker is 500s old


def test_missing_files_return_empty(tmp_path: Path) -> None:
    assert OQLEngine(tmp_path).execute("services") == []


def test_bus_integration(tmp_path: Path) -> None:
    bus = EventBus()
    register_oql(bus, _project(tmp_path))
    rows = bus.query(RunOQL(query="services where status = down"))
    assert [r["name"] for r in rows] == ["api"]
