"""Decode wup://cmd/… URI → single DSL line."""

from __future__ import annotations

from uri2wup.uri import parse_wup_uri


def _dict_to_dsl(cmd: dict[str, str]) -> str:
    verb = cmd.get("verb", "").upper()
    parts = [verb]
    for key in ("target", "path", "text", "service", "root"):
        if val := cmd.get(key):
            parts.append(f'"{val}"' if " " in val else val)
    for key, flag in (
        ("file", "FILE"),
        ("format", "FORMAT"),
        ("with_path", "WITH"),
        ("out", "OUT"),
        ("framework", "FRAMEWORK"),
        ("project", "PROJECT"),
    ):
        if val := cmd.get(key):
            parts.extend([flag, f'"{val}"' if " " in val else val])
    return " ".join(parts)


def _command_from_params(parts: list[str], params: dict[str, str]) -> dict[str, str]:
    verb = (parts[0] if parts else params.get("verb", "")).upper()
    if not verb:
        raise ValueError("wup://cmd requires verb in path or ?verb=")
    cmd = {"verb": verb}
    for key in ("target", "path", "text", "service", "file", "project", "format", "out", "framework", "root"):
        if value := params.get(key):
            cmd[key] = value
    if value := params.get("with") or params.get("with_path"):
        cmd["with_path"] = value
    return cmd


def _block_query(uri: str, parsed: dict[str, object]) -> dict[str, str]:
    cmd = {"verb": "QUERY", "target": uri}
    for key in ("file", "project", "format"):
        if value := str(parsed.get(key) or ""):
            cmd[key] = value
    return cmd


def decode_uri(uri: str) -> str:
    """Convert wup:// URI to a canonical DSL command line."""
    parsed = parse_wup_uri(uri)
    source = str(parsed["source"])
    parts = list(parsed["parts"])  # type: ignore[arg-type]
    params = parsed["params"]
    assert isinstance(params, dict)

    if source == "cmd":
        return _dict_to_dsl(_command_from_params(parts, params))
    if source == "block":
        return _dict_to_dsl(_block_query(uri, parsed))

    raise ValueError(f"unsupported wup uri source for decode: {source}")
