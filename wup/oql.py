"""
OQL — Observability Query Language.

A tiny declarative language for querying WUP's observed state (service health and
health events) so an AI agent (or a human) can ask questions instead of reading
JSON files:

    services
    services where status = down
    services where status != up limit 5
    events since 10m
    events where service = api since 1h

Grammar (keywords case-insensitive)::

    <source> [WHERE <cond> [AND <cond>]...] [SINCE <duration>] [LIMIT <n>]

    source   := services | events
    cond     := <field> <op> <value>
    op       := =  ==  !=  >  <  >=  <=  ~ (contains)  !~ (not contains)
    duration := <int>(s|m|h|d)

Rows are plain dicts; `services` rows carry an injected ``name`` field. The engine
reads the same files the watcher writes (`.wup/service-health.json`,
`.wup/service-health-events.jsonl`), so it reflects live state.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bus import EventBus, Query
from .paths import health_events_path, health_state_path

SOURCES = ("services", "events")
_OPERATORS = ("!=", ">=", "<=", "==", "=", ">", "<", "!~", "~")
_DURATION_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


class OQLError(ValueError):
    """Raised for malformed OQL queries."""


@dataclass
class Condition:
    field: str
    op: str
    value: str

    def matches(self, row: Dict[str, Any]) -> bool:
        actual = row.get(self.field)
        return _compare(actual, self.op, self.value)


@dataclass
class OQLQuery:
    source: str
    conditions: List[Condition] = field(default_factory=list)
    since_seconds: Optional[int] = None
    limit: Optional[int] = None


# --- comparison -----------------------------------------------------------

def _coerce_number(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compare(actual: Any, op: str, expected: str) -> bool:
    if op in ("~", "!~"):
        contains = expected.lower() in str(actual if actual is not None else "").lower()
        return contains if op == "~" else not contains

    # Numeric comparison when both sides look numeric, else string comparison.
    expected_num = _coerce_number(expected)
    actual_num = _coerce_number(str(actual)) if actual is not None else None
    if expected_num is not None and actual_num is not None:
        left: Any = actual_num
        right: Any = expected_num
    else:
        left = "" if actual is None else str(actual)
        right = expected

    if op in ("=", "=="):
        return left == right
    if op == "!=":
        return left != right
    if op == ">":
        return left > right
    if op == "<":
        return left < right
    if op == ">=":
        return left >= right
    if op == "<=":
        return left <= right
    raise OQLError(f"unknown operator: {op}")


# --- parsing --------------------------------------------------------------

def _parse_duration(token: str) -> int:
    match = re.fullmatch(r"(\d+)\s*([smhd])", token.strip().lower())
    if not match:
        raise OQLError(f"invalid duration: {token!r} (use e.g. 30s, 5m, 2h, 1d)")
    return int(match.group(1)) * _DURATION_UNITS[match.group(2)]


def _tokenize(query: str) -> List[str]:
    # Pad operators so `status=down` and `status = down` both tokenize cleanly.
    padded = query
    for op in _OPERATORS:
        padded = padded.replace(op, f" {op} ")
    # Collapse operator fragments that got split (e.g. ! = -> !=).
    padded = re.sub(r"!\s+=", "!=", padded)
    padded = re.sub(r">\s+=", ">=", padded)
    padded = re.sub(r"<\s+=", "<=", padded)
    padded = re.sub(r"=\s+=", "==", padded)
    padded = re.sub(r"!\s+~", "!~", padded)
    return padded.split()


def parse(query: str) -> OQLQuery:
    """Parse an OQL string into an :class:`OQLQuery`."""
    tokens = _tokenize(query)
    if not tokens:
        raise OQLError("empty query")

    source = tokens.pop(0).lower()
    if source not in SOURCES:
        raise OQLError(f"unknown source {source!r}; expected one of {', '.join(SOURCES)}")

    parsed = OQLQuery(source=source)
    i = 0
    while i < len(tokens):
        keyword = tokens[i].lower()
        if keyword == "where":
            i = _parse_conditions(tokens, i + 1, parsed)
        elif keyword == "and":
            raise OQLError("'and' without a preceding 'where'")
        elif keyword == "since":
            if i + 1 >= len(tokens):
                raise OQLError("'since' requires a duration")
            parsed.since_seconds = _parse_duration(tokens[i + 1])
            i += 2
        elif keyword == "limit":
            if i + 1 >= len(tokens):
                raise OQLError("'limit' requires a number")
            try:
                parsed.limit = int(tokens[i + 1])
            except ValueError:
                raise OQLError(f"invalid limit: {tokens[i + 1]!r}")
            i += 2
        else:
            raise OQLError(f"unexpected token: {tokens[i]!r}")
    return parsed


def _parse_conditions(tokens: List[str], start: int, parsed: OQLQuery) -> int:
    """Consume `<field> <op> <value> [and ...]` conditions; return next index."""
    if start >= len(tokens):
        raise OQLError("'where' requires at least one condition")
    i = start
    while i < len(tokens):
        if i + 3 > len(tokens):
            raise OQLError("incomplete condition (expected: field op value)")
        field_name, op, value = tokens[i], tokens[i + 1], tokens[i + 2]
        if op not in _OPERATORS:
            raise OQLError(f"invalid operator {op!r} in condition")
        parsed.conditions.append(Condition(field_name, op, value))
        i += 3
        if i < len(tokens) and tokens[i].lower() == "and":
            i += 1
            continue
        break
    return i


# --- engine ---------------------------------------------------------------

class OQLEngine:
    """Executes OQL queries against a project's observed state."""

    def __init__(self, project_root: Path | str = "."):
        self.project_root = Path(project_root)

    def _service_rows(self) -> List[Dict[str, Any]]:
        path = health_state_path(self.project_root)
        if not path.exists():
            return []
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if not isinstance(state, dict):
            return []
        rows = []
        for name, info in state.items():
            row = {"name": name}
            if isinstance(info, dict):
                row.update(info)
            else:
                row["status"] = info
            rows.append(row)
        return rows

    def _event_rows(self) -> List[Dict[str, Any]]:
        path = health_events_path(self.project_root)
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    def execute(self, query: str | OQLQuery) -> List[Dict[str, Any]]:
        """Run a query (string or parsed) and return matching rows."""
        parsed = query if isinstance(query, OQLQuery) else parse(query)

        if parsed.source == "services":
            rows = self._service_rows()
            time_field = "updated_at"
        else:
            rows = self._event_rows()
            time_field = "timestamp"

        if parsed.since_seconds is not None:
            cutoff = int(time.time()) - parsed.since_seconds
            rows = [r for r in rows if int(r.get(time_field, 0) or 0) >= cutoff]

        for condition in parsed.conditions:
            rows = [r for r in rows if condition.matches(r)]

        if parsed.source == "events":
            rows.sort(key=lambda r: int(r.get("timestamp", 0) or 0), reverse=True)

        if parsed.limit is not None:
            rows = rows[: parsed.limit]
        return rows


# --- CQRS bus integration -------------------------------------------------

@dataclass
class RunOQL(Query):
    """Query message: run an OQL string over observed state via the event bus."""
    query: str = ""


def register_oql(bus: EventBus, project_root: Path | str = ".") -> OQLEngine:
    """Register a :class:`RunOQL` handler on the bus; return the engine."""
    engine = OQLEngine(project_root)
    bus.subscribe(RunOQL, lambda message: engine.execute(message.query))
    return engine
