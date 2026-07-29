"""
AQL — Assertion Query Language.

A declarative language for asserting facts about a file's data (JSON/YAML/text),
so an AI agent or a human can express checks as one-liners instead of Python:

    json .version exists
    json .services length > 0
    yaml .testql.probe_interval_s >= 0
    json .name = subactor
    text ~ "TODO"
    keys .testql missing

Grammar (keywords case-insensitive)::

    <selector> <predicate> [severity <sev>]

    selector  := (json | yaml | keys) <path> | text
    predicate := exists | missing
               | (= | != | > | < | >= | <=) <value>
               | (~ | !~) <value>            # contains / not-contains
               | matches <regex>
               | length (> | < | >= | <= | =) <int>
               | type (string|number|object|array|bool|null)
    path      := dotted path with optional [index], e.g. .a.b[0].c

Each failing rule yields an :class:`~wup.anomaly_models.AnomalyResult`, so AQL
plugs straight into the existing anomaly-reporting pipeline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Tuple

import yaml

from .anomaly_models import AnomalyResult
from .bus import EventBus, Query

_MISSING = object()  # sentinel: path resolved to nothing
_SELECTORS = ("json", "yaml", "keys", "text")
_COMPARATORS = ("!=", ">=", "<=", "==", "=", ">", "<", "!~", "~")
_TYPE_NAMES = {"string", "number", "object", "array", "bool", "boolean", "null"}
_SEVERITIES = ("low", "medium", "high", "critical")


class AQLError(ValueError):
    """Raised for malformed AQL rules."""


@dataclass
class AQLRule:
    selector: str
    path: str
    op: str
    value: Optional[str] = None
    length_op: Optional[str] = None
    severity: str = "medium"
    raw: str = ""


# --- path resolution ------------------------------------------------------

def _path_tokens(path: str) -> List[Any] | None:
    """Split ``.a.b[0].c`` into ``['a', 'b', 0, 'c']``."""
    tokens: List[Any] = []
    for part in path.lstrip(".").split("."):
        if not part:
            continue
        match = re.match(r"^([^\[\]]*)((?:\[\d+\])*)$", part)
        if not match:
            return None
        key, indices = match.group(1), match.group(2)
        if key:
            tokens.append(key)
        for idx in re.findall(r"\[(\d+)\]", indices):
            tokens.append(int(idx))
    return tokens


def _path_child(current: Any, token: Any) -> Any:
    if isinstance(token, int) and isinstance(current, (list, tuple)) and 0 <= token < len(current):
        return current[token]
    if isinstance(token, str) and isinstance(current, dict) and token in current:
        return current[token]
    return _MISSING


def _resolve_path(data: Any, path: str) -> Any:
    """Resolve a dotted/indexed path (e.g. ``.a.b[0]``) or return ``_MISSING``."""
    if path in ("", "."):
        return data
    tokens = _path_tokens(path)
    if tokens is None:
        return _MISSING
    current = data
    for token in tokens:
        current = _path_child(current, token)
        if current is _MISSING:
            return _MISSING
    return current


# --- parsing --------------------------------------------------------------

def _split_severity(tokens: List[str]) -> Tuple[List[str], str]:
    severity = "medium"
    if len(tokens) >= 2 and tokens[-2].lower() == "severity":
        severity = tokens[-1].lower()
        if severity not in _SEVERITIES:
            raise AQLError(f"invalid severity {severity!r}; expected {', '.join(_SEVERITIES)}")
        tokens = tokens[:-2]
    return tokens, severity


def _tokenize(rule: str) -> List[str]:
    # Honour quoted values as a single token; pad comparators otherwise.
    quoted = re.findall(r'"[^"]*"|\'[^\']*\'', rule)
    placeholder = {}
    tmp = rule
    for i, q in enumerate(quoted):
        key = f"\x00{i}\x00"
        placeholder[key] = q[1:-1]
        tmp = tmp.replace(q, key, 1)
    for op in _COMPARATORS:
        tmp = tmp.replace(op, f" {op} ")
    tmp = re.sub(r"!\s+=", "!=", tmp)
    tmp = re.sub(r">\s+=", ">=", tmp)
    tmp = re.sub(r"<\s+=", "<=", tmp)
    tmp = re.sub(r"=\s+=", "==", tmp)
    tmp = re.sub(r"!\s+~", "!~", tmp)
    tokens = tmp.split()
    return [placeholder.get(t, t) for t in tokens]


def _rule_selector(tokens: List[str]) -> Tuple[str, str]:
    selector = tokens.pop(0).lower()
    if selector not in _SELECTORS:
        raise AQLError(f"unknown selector {selector!r}; expected one of {', '.join(_SELECTORS)}")
    if selector == "text":
        return selector, ""
    if not tokens:
        raise AQLError(f"selector {selector!r} requires a path")
    return selector, tokens.pop(0)


def _predicate_value(tokens: List[str], message: str) -> str:
    if tokens:
        return tokens.pop(0)
    raise AQLError(message)


def _length_rule(selector: str, path: str, tokens: List[str], severity: str, raw: str) -> AQLRule:
    if len(tokens) < 2 or tokens[0] not in _COMPARATORS:
        raise AQLError("'length' requires an operator and number, e.g. length > 0")
    operator, number = tokens[0], tokens[1]
    if not number.lstrip("-").isdigit():
        raise AQLError(f"'length' expects an integer, got {number!r}")
    return AQLRule(selector, path, "length", number, length_op=operator, severity=severity, raw=raw)


def _type_rule(selector: str, path: str, tokens: List[str], severity: str, raw: str) -> AQLRule:
    value = _predicate_value(tokens, f"'type' requires one of {', '.join(sorted(_TYPE_NAMES))}").lower()
    if value not in _TYPE_NAMES:
        raise AQLError(f"'type' requires one of {', '.join(sorted(_TYPE_NAMES))}")
    return AQLRule(selector, path, "type", value, severity=severity, raw=raw)


def _predicate_rule(selector: str, path: str, keyword: str, tokens: List[str], severity: str, raw: str) -> AQLRule:
    lower = keyword.lower()
    if lower in ("exists", "missing"):
        return AQLRule(selector, path, lower, severity=severity, raw=raw)
    if lower == "matches":
        return AQLRule(selector, path, "matches", _predicate_value(tokens, "'matches' requires a regex"), severity=severity, raw=raw)
    if lower == "type":
        return _type_rule(selector, path, tokens, severity, raw)
    if lower == "length":
        return _length_rule(selector, path, tokens, severity, raw)
    if keyword in _COMPARATORS:
        return AQLRule(selector, path, keyword, _predicate_value(tokens, f"operator {keyword!r} requires a value"), severity=severity, raw=raw)
    raise AQLError(f"unknown predicate {keyword!r}")


def parse_rule(rule: str) -> AQLRule:
    """Parse a single AQL rule string into an :class:`AQLRule`."""
    tokens, severity = _split_severity(_tokenize(rule))
    if not tokens:
        raise AQLError("empty rule")

    selector, path = _rule_selector(tokens)

    if not tokens:
        raise AQLError("rule requires a predicate (exists, =, length, type, …)")

    keyword = tokens.pop(0)
    return _predicate_rule(selector, path, keyword, tokens, severity, rule)


# --- evaluation -----------------------------------------------------------

def _coerce_number(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compare(actual: Any, op: str, expected: str) -> bool:
    a_num, e_num = _coerce_number(actual), _coerce_number(expected)
    if a_num is not None and e_num is not None:
        left, right = a_num, e_num
    else:
        left, right = ("" if actual is None else str(actual)), expected
    return {
        "=": left == right, "==": left == right, "!=": left != right,
        ">": left > right, "<": left < right, ">=": left >= right, "<=": left <= right,
    }[op]


def _length_of(value: Any) -> Optional[int]:
    if isinstance(value, (str, list, tuple, dict)):
        return len(value)
    return None


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def _matches_value(rule: AQLRule, value: Any) -> bool:
    if rule.op == "matches":
        return re.search(rule.value, str(value)) is not None
    if rule.op == "type":
        wanted = "bool" if rule.value in ("bool", "boolean") else rule.value
        return _type_name(value) == wanted
    return False


def _collection_passes(rule: AQLRule, value: Any) -> bool | None:
    if rule.op == "length":
        length = _length_of(value)
        return length is not None and _compare(length, rule.length_op, rule.value)
    if rule.op in ("~", "!~"):
        contains = rule.value.lower() in str(value).lower()
        return contains if rule.op == "~" else not contains
    return None


def _passes(rule: AQLRule, value: Any) -> bool:
    present = value is not _MISSING
    if rule.op == "exists":
        return present
    if rule.op == "missing":
        return not present
    if not present:
        return False  # every other predicate needs the value to exist

    if rule.op in ("matches", "type"):
        return _matches_value(rule, value)
    if result := _collection_passes(rule, value):
        return result
    if rule.op in ("length", "~", "!~"):
        return False
    return _compare(value, rule.op, rule.value)


class AQLEngine:
    """Evaluates AQL rules against a file's data, producing AnomalyResults."""

    def __init__(self, project_root: Path | str = "."):
        self.project_root = Path(project_root)

    @staticmethod
    def _load(file_path: Path, selector: str) -> Any:
        text = file_path.read_text(encoding="utf-8")
        if selector == "text":
            return text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return yaml.safe_load(text)

    def _value_for_rule(self, file_path: Path, rule: AQLRule) -> Any:
        data = self._load(file_path, rule.selector)
        value = data if rule.selector == "text" else _resolve_path(data, rule.path)
        return sorted(value.keys()) if rule.selector == "keys" and isinstance(value, dict) else value

    @staticmethod
    def _violation(file_path: Path, rule: AQLRule, value: Any) -> AnomalyResult:
        shown = "(missing)" if value is _MISSING else repr(value)[:60]
        return AnomalyResult(
            detector="aql", file_path=str(file_path), anomaly_type="assertion", severity=rule.severity,
            message=f"assertion failed: {rule.raw.strip()} (actual: {shown})",
            details={"rule": rule.raw.strip(), "actual": None if value is _MISSING else value},
        )

    def check_file(self, file_path: Path | str, rules: List[str | AQLRule]) -> List[AnomalyResult]:
        """Evaluate rules against one file; return a violation per failing rule."""
        file_path = Path(file_path)
        violations: List[AnomalyResult] = []
        if not file_path.exists():
            return [AnomalyResult("aql", str(file_path), "error", "high", "file not found")]

        for rule in rules:
            parsed = rule if isinstance(rule, AQLRule) else parse_rule(rule)
            try:
                value = self._value_for_rule(file_path, parsed)
            except (OSError, yaml.YAMLError) as exc:
                violations.append(AnomalyResult("aql", str(file_path), "error", "high", f"could not read: {exc}"))
                continue

            if not _passes(parsed, value):
                violations.append(self._violation(file_path, parsed, value))
        return violations


# --- CQRS bus integration -------------------------------------------------

@dataclass
class CheckAQL(Query):
    """Query message: evaluate AQL rules against a file via the event bus."""
    file: str = ""
    rules: Optional[List[str]] = None


def register_aql(bus: EventBus, project_root: Path | str = ".") -> AQLEngine:
    """Register a :class:`CheckAQL` handler on the bus; return the engine."""
    engine = AQLEngine(project_root)
    bus.subscribe(CheckAQL, lambda m: engine.check_file(m.file, m.rules or []))
    return engine
