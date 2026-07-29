"""Text DSL → dict."""

from __future__ import annotations

import shlex
from typing import Any


def split_command(line: str) -> list[str]:
    line = line.strip()
    if not line or line.startswith("#"):
        return []
    try:
        return shlex.split(line, posix=True)
    except ValueError:
        return line.split()


def pick_flag(tokens: list[str], flag: str) -> str | None:
    if flag in tokens:
        idx = tokens.index(flag)
        if idx + 1 < len(tokens):
            return tokens[idx + 1]
    return None


def _flag_values(cmd: dict[str, Any], tokens: list[str], *flags: tuple[str, str, object]) -> None:
    for key, flag, transform in flags:
        if value := pick_flag(tokens, flag):
            cmd[key] = transform(value)


def _parse_query(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["target"] = rest[0] if rest else ""
        _flag_values(cmd, rest, ("file", "FILE", str), ("format", "FORMAT", str.lower), ("project", "PROJECT", str))


def _parse_validate(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["path"] = rest[0] if rest else ""
        _flag_values(cmd, rest, ("project", "PROJECT", str))


def _parse_resolve(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["text"] = " ".join(rest)
        _flag_values(cmd, rest, ("file", "FILE", str), ("project", "PROJECT", str))


def _parse_health(rest: list[str], cmd: dict[str, Any]) -> None:
        if rest and rest[0] != "PROJECT":
            cmd["service"] = rest[0]
        _flag_values(cmd, rest, ("project", "PROJECT", str))


def _parse_patch(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["target"] = rest[0] if rest else ""
        _flag_values(cmd, rest, ("with_path", "WITH", str), ("file", "FILE", str), ("project", "PROJECT", str))


def _parse_map(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["project"] = rest[0] if rest else "."
        _flag_values(cmd, rest, ("out", "OUT", str), ("framework", "FRAMEWORK", str.lower))


def _parse_init(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["project"] = rest[0] if rest else "."
        _flag_values(cmd, rest, ("out", "OUT", str))


def _parse_generate(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["text"] = rest[0].strip('"').strip("'") if rest else ""
        _flag_values(cmd, rest, ("out", "OUT", str), ("project", "PROJECT", str), ("template", "TEMPLATE", str.lower))


def _parse_sync(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["project"] = rest[0] if rest else "."
        _flag_values(cmd, rest, ("file", "FILE", str))
        if "MERGE" in rest:
            cmd["merge_endpoints"] = True


def _parse_adopt(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["root"] = rest[0] if rest else "."
        _flag_values(cmd, rest, ("out", "OUT", str))


def _parse_endpoints(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["scenarios_dir"] = rest[0] if rest else ""
        _flag_values(cmd, rest, ("out", "OUT", str), ("testql_bin", "TESTQL_BIN", str))


def _parse_status(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["project"] = "."
        if rest and rest[0] not in {"PROJECT", "DEPS", "FILE", "DELTA", "FAILED_ONLY"}:
            cmd["project"] = rest[0]
        _flag_values(cmd, rest, ("project", "PROJECT", str), ("deps_file", "DEPS", str), ("file", "FILE", str), ("delta_seconds", "DELTA", int))
        if "FAILED_ONLY" in rest:
            cmd["failed_only"] = True


def _parse_init_cli(rest: list[str], cmd: dict[str, Any]) -> None:
        cmd["project"] = rest[0] if rest else "."
        _flag_values(cmd, rest, ("out", "OUT", str), ("scenarios", "SCENARIOS", str))
        if "MERGE" in rest:
            cmd["merge"] = True
        if f := pick_flag(rest, "INFER_ARGS"):
            cmd["infer_args"] = f.lower() not in {"false", "0", "no"}


_PARSERS = {"QUERY": _parse_query, "VALIDATE": _parse_validate, "RESOLVE": _parse_resolve, "HEALTH": _parse_health, "PATCH": _parse_patch, "UPDATE": _parse_patch, "REPLACE": _parse_patch, "MAP": _parse_map, "INIT": _parse_init, "GENERATE": _parse_generate, "SYNC": _parse_sync, "ADOPT": _parse_adopt, "ENDPOINTS": _parse_endpoints, "STATUS": _parse_status, "INIT_CLI": _parse_init_cli}


def parse_line(line: str) -> dict[str, Any] | None:
    tokens = split_command(line)
    if not tokens:
        return None
    verb, rest = tokens[0].upper(), tokens[1:]
    cmd: dict[str, Any] = {"verb": verb}
    parser = _PARSERS.get(verb)
    if parser:
        parser(rest, cmd)
    else:
        cmd["args"] = rest
    return cmd


def to_text(cmd: dict[str, Any]) -> str:
    verb = str(cmd.get("verb", "")).upper()
    parts = [verb]
    for key in ("target", "path", "text", "service", "root", "scenarios_dir"):
        if val := cmd.get(key):
            parts.append(f'"{val}"' if " " in str(val) else str(val))
    for key, flag in (
        ("file", "FILE"),
        ("format", "FORMAT"),
        ("with_path", "WITH"),
        ("out", "OUT"),
        ("framework", "FRAMEWORK"),
        ("project", "PROJECT"),
        ("template", "TEMPLATE"),
        ("testql_bin", "TESTQL_BIN"),
        ("scenarios", "SCENARIOS"),
        ("deps_file", "DEPS"),
        ("delta_seconds", "DELTA"),
    ):
        if val := cmd.get(key):
            parts.extend([flag, f'"{val}"' if " " in str(val) else str(val)])
    if cmd.get("merge_endpoints") or cmd.get("merge"):
        parts.append("MERGE")
    if cmd.get("infer_args") is False:
        parts.append("INFER_ARGS false")
    if cmd.get("failed_only"):
        parts.append("FAILED_ONLY")
    return " ".join(parts)
