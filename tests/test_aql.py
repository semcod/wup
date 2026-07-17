"""Tests for AQL — the Assertion Query Language."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wup.aql import AQLEngine, AQLError, CheckAQL, parse_rule, register_aql
from wup.bus import EventBus


def _sample(tmp_path: Path) -> Path:
    f = tmp_path / "sample.json"
    f.write_text(json.dumps({
        "name": "subactor",
        "version": "1.2.0",
        "services": ["a", "b"],
        "testql": {"probe_interval_s": 60},
        "flag": True,
        "empty": None,
    }))
    return f


def _check(tmp_path: Path, rule: str) -> bool:
    """True when the rule passes (no violations)."""
    return not AQLEngine(tmp_path).check_file(_sample(tmp_path), [rule])


# --- parsing --------------------------------------------------------------

def test_parse_exists() -> None:
    r = parse_rule("json .version exists")
    assert (r.selector, r.path, r.op) == ("json", ".version", "exists")


def test_parse_length_and_severity() -> None:
    r = parse_rule("json .services length > 0 severity high")
    assert (r.op, r.length_op, r.value, r.severity) == ("length", ">", "0", "high")


@pytest.mark.parametrize("bad", [
    "", "widget .x exists", "json", "json .x", "json .x bogus",
    "json .x length foo", "json .x type banana", "json .x = ",
    "json .x severity nope",
])
def test_parse_errors(bad: str) -> None:
    with pytest.raises(AQLError):
        parse_rule(bad)


# --- evaluation -----------------------------------------------------------

@pytest.mark.parametrize("rule", [
    "json .version exists",
    "json .missing missing",
    "json .services length > 0",
    "json .services length = 2",
    "json .testql.probe_interval_s >= 60",
    "json .name = subactor",
    "json .name ~ sub",
    "json .name !~ zzz",
    "json .version matches ^\\d+\\.\\d+",
    "json .services type array",
    "json .testql type object",
    "json .flag type bool",
    "json .name type string",
    "json .testql.probe_interval_s type number",
    "keys .testql ~ probe_interval_s",
    "keys .testql length = 1",
    "text ~ subactor",
])
def test_passing_rules(tmp_path: Path, rule: str) -> None:
    assert _check(tmp_path, rule)


@pytest.mark.parametrize("rule", [
    "json .missing exists",
    "json .version missing",
    "json .services length > 5",
    "json .name = other",
    "json .name ~ zzz",
    "json .version matches ^zzz",
    "json .services type object",
    "json .missing type string",
    "keys .testql ~ nope",
    "text ~ nonexistent-token",
])
def test_failing_rules(tmp_path: Path, rule: str) -> None:
    assert not _check(tmp_path, rule)


def test_violation_carries_severity(tmp_path: Path) -> None:
    v = AQLEngine(tmp_path).check_file(_sample(tmp_path), ["json .missing exists severity critical"])
    assert len(v) == 1 and v[0].severity == "critical" and v[0].detector == "aql"


def test_nested_and_indexed_paths(tmp_path: Path) -> None:
    assert _check(tmp_path, "json .services[0] = a")
    assert _check(tmp_path, "json .services[1] = b")


def test_missing_file(tmp_path: Path) -> None:
    v = AQLEngine(tmp_path).check_file(tmp_path / "nope.json", ["json .x exists"])
    assert len(v) == 1 and v[0].anomaly_type == "error"


def test_yaml_file(tmp_path: Path) -> None:
    y = tmp_path / "wup.yaml"
    y.write_text("project:\n  name: demo\ntestql:\n  probe_interval_s: 0\n")
    assert not AQLEngine(tmp_path).check_file(y, ["yaml .project.name = demo", "yaml .testql.probe_interval_s >= 0"])


def test_bus_integration(tmp_path: Path) -> None:
    bus = EventBus()
    register_aql(bus, tmp_path)
    result = bus.query(CheckAQL(file=str(_sample(tmp_path)), rules=["json .version exists"]))
    assert result == []  # no violations
