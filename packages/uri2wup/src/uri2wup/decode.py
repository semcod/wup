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


def decode_uri(uri: str) -> str:
    """Convert wup:// URI to a canonical DSL command line."""
    parsed = parse_wup_uri(uri)
    source = str(parsed["source"])
    parts = list(parsed["parts"])  # type: ignore[arg-type]
    params = parsed["params"]
    assert isinstance(params, dict)

    if source == "cmd":
        verb = (parts[0] if parts else params.get("verb", "")).upper()
        if not verb:
            raise ValueError("wup://cmd requires verb in path or ?verb=")
        cmd: dict[str, str] = {"verb": verb}
        if target := params.get("target"):
            cmd["target"] = target
        if path := params.get("path"):
            cmd["path"] = path
        if text := params.get("text"):
            cmd["text"] = text
        if service := params.get("service"):
            cmd["service"] = service
        if with_path := params.get("with") or params.get("with_path"):
            cmd["with_path"] = with_path
        for key, param in (
            ("file", "file"),
            ("project", "project"),
            ("format", "format"),
            ("out", "out"),
            ("framework", "framework"),
            ("root", "root"),
        ):
            if val := params.get(param):
                cmd[key] = val
        return _dict_to_dsl(cmd)

    if source == "block":
        cmd = {"verb": "QUERY", "target": uri}
        if file := str(parsed.get("file") or ""):
            cmd["file"] = file
        if project := str(parsed.get("project") or ""):
            cmd["project"] = project
        if fmt := str(parsed.get("format") or ""):
            cmd["format"] = fmt
        return _dict_to_dsl(cmd)

    raise ValueError(f"unsupported wup uri source for decode: {source}")
