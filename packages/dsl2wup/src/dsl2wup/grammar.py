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


def parse_line(line: str) -> dict[str, Any] | None:
    tokens = split_command(line)
    if not tokens:
        return None
    verb = tokens[0].upper()
    rest = tokens[1:]
    cmd: dict[str, Any] = {"verb": verb}

    if verb == "QUERY":
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if f := pick_flag(rest, "FORMAT"):
            cmd["format"] = f.lower()
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
    elif verb == "VALIDATE":
        cmd["path"] = rest[0] if rest else ""
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
    elif verb == "RESOLVE":
        cmd["text"] = " ".join(rest)
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
    elif verb == "HEALTH":
        if rest and rest[0] != "PROJECT":
            cmd["service"] = rest[0]
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
    elif verb in {"PATCH", "UPDATE", "REPLACE"}:
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "WITH"):
            cmd["with_path"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
    elif verb == "MAP":
        cmd["project"] = rest[0] if rest else "."
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
        if f := pick_flag(rest, "FRAMEWORK"):
            cmd["framework"] = f.lower()
    elif verb == "INIT":
        cmd["project"] = rest[0] if rest else "."
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
    elif verb == "GENERATE":
        cmd["text"] = rest[0].strip('"').strip("'") if rest else ""
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
        if f := pick_flag(rest, "TEMPLATE"):
            cmd["template"] = f.lower()
    elif verb == "SYNC":
        cmd["project"] = rest[0] if rest else "."
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if "MERGE" in rest:
            cmd["merge_endpoints"] = True
    elif verb == "ADOPT":
        cmd["root"] = rest[0] if rest else "."
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
    elif verb == "ENDPOINTS":
        cmd["scenarios_dir"] = rest[0] if rest else ""
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
        if f := pick_flag(rest, "TESTQL_BIN"):
            cmd["testql_bin"] = f
    elif verb == "STATUS":
        cmd["project"] = "."
        if rest and rest[0] not in {"PROJECT", "DEPS", "FILE", "DELTA", "FAILED_ONLY"}:
            cmd["project"] = rest[0]
        if f := pick_flag(rest, "PROJECT"):
            cmd["project"] = f
        if f := pick_flag(rest, "DEPS"):
            cmd["deps_file"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if f := pick_flag(rest, "DELTA"):
            cmd["delta_seconds"] = int(f)
        if "FAILED_ONLY" in rest:
            cmd["failed_only"] = True
    elif verb == "INIT_CLI":
        cmd["project"] = rest[0] if rest else "."
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
        if f := pick_flag(rest, "SCENARIOS"):
            cmd["scenarios"] = f
        if "MERGE" in rest:
            cmd["merge"] = True
        if f := pick_flag(rest, "INFER_ARGS"):
            cmd["infer_args"] = f.lower() not in {"false", "0", "no"}
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
