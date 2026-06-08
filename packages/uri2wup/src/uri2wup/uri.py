"""wup:// URI builders and parsing."""

from __future__ import annotations

from urllib.parse import quote, unquote, urlparse

WUP_SCHEME = "wup"
_FILE_SOURCE = "file"
_BLOCK_SOURCE = "block"
_CMD_SOURCE = "cmd"


def _encode(value: str) -> str:
    return quote(value, safe="")


def _decode(value: str) -> str:
    return unquote(value or "")


def uri_for_cmd(
    verb: str,
    *,
    target: str | None = None,
    file: str | None = None,
    project: str | None = None,
    path: str | None = None,
    out: str | None = None,
) -> str:
    uri = f"{WUP_SCHEME}://{_CMD_SOURCE}/{_encode(verb.upper())}"
    params: list[str] = []
    if target:
        params.append(f"target={_encode(target)}")
    if file:
        params.append(f"file={_encode(file)}")
    if project:
        params.append(f"project={_encode(project)}")
    if path:
        params.append(f"path={_encode(path)}")
    if out:
        params.append(f"out={_encode(out)}")
    if params:
        uri += "?" + "&".join(params)
    return uri


def uri_for_block(
    *parts: str,
    file: str | None = None,
    project: str | None = None,
    fmt: str | None = None,
) -> str:
    encoded = "/".join(_encode(p) for p in parts if p)
    uri = f"{WUP_SCHEME}://{_BLOCK_SOURCE}/{encoded}"
    params: list[str] = []
    if file:
        params.append(f"file={_encode(file)}")
    if project:
        params.append(f"project={_encode(project)}")
    if fmt:
        params.append(f"format={_encode(fmt)}")
    if params:
        uri += "?" + "&".join(params)
    return uri


def is_wup_uri(uri: str) -> bool:
    return urlparse(uri).scheme.lower() == WUP_SCHEME


def parse_wup_uri(uri: str) -> dict[str, str | list[str]]:
    if not is_wup_uri(uri):
        raise ValueError(f"not a wup uri: {uri}")
    parsed = urlparse(uri)
    source = _decode(parsed.netloc)
    parts = [_decode(p) for p in parsed.path.split("/") if p]
    params: dict[str, str] = {}
    if parsed.query:
        for chunk in parsed.query.split("&"):
            if "=" in chunk:
                key, value = chunk.split("=", 1)
                params[key] = _decode(value)
    return {
        "source": source,
        "parts": parts,
        "params": params,
        "file": params.get("file", ""),
        "project": params.get("project", "."),
        "format": params.get("format", "json"),
        "target": params.get("target", ""),
        "verb": params.get("verb", ""),
    }
