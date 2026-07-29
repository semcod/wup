"""Query addressed blocks from wup.yaml and project state."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from uri2wup.uri import parse_wup_uri


@dataclass
class QueryResult:
    ok: bool
    uri: str
    selector: str
    file: str
    data: Any = None
    rendered: str = ""
    format: str = "json"
    error: str | None = None
    keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "selector": self.selector,
            "file": self.file,
            "data": self.data,
            "rendered": self.rendered,
            "format": self.format,
            "keys": self.keys,
            "error": self.error,
        }


def _resolve_config_path(project: str, file_param: str | None) -> Path:
    project_path = Path(project).expanduser().resolve()
    if file_param:
        path = Path(file_param).expanduser()
        return path if path.is_absolute() else project_path / path
    from wup.config import find_config_file

    found = find_config_file(project_path)
    return found or (project_path / "wup.yaml")


def _extract_block(raw: dict[str, Any], parts: list[str]) -> Any:
    if not parts:
        return raw
    if parts[0] == "config":
        parts = parts[1:]

    node: Any = raw
    for part in parts:
        if isinstance(node, dict):
            if part not in node:
                raise KeyError(part)
            node = node[part]
        elif isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError) as exc:
                raise KeyError(part) from exc
        else:
            raise KeyError(part)
    return node


def _runtime_block(parts: list[str], project: str) -> Any:
    cwd = Path(project).expanduser().resolve()
    kind = parts[0]
    if kind == "deps":
        path = cwd / (parts[1] if len(parts) > 1 else "deps.json")
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    from wup.paths import health_state_path

    health_path = health_state_path(cwd)
    if kind == "health":
        return (
            json.loads(health_path.read_text(encoding="utf-8"))
            if health_path.exists()
            else {}
        )
    return {
        "deps_exists": (cwd / "deps.json").exists(),
        "health_exists": health_path.exists(),
    }


def _success(
    uri: str, parts: list[str], data: Any, output_fmt: str, file: str = ""
) -> QueryResult:
    return QueryResult(
        ok=True,
        uri=uri,
        selector="/".join(parts) or "config",
        file=file,
        data=data,
        rendered=yaml.safe_dump(data, sort_keys=False)
        if output_fmt == "yaml"
        else json.dumps(data, ensure_ascii=False, indent=2),
        format=output_fmt,
        keys=sorted(data.keys()) if isinstance(data, dict) else [],
    )


def _query_context(uri: str, file: str | None, fmt: str | None, project: str) -> tuple[list[str], str, str, str]:
    parsed = parse_wup_uri(uri)
    source = str(parsed["source"])
    if source != "block":
        raise ValueError(f"unsupported wup source: {source}")
    parts = list(parsed["parts"])  # type: ignore[arg-type]
    file_param = file or str(parsed.get("file") or "")
    output_fmt = (fmt or str(parsed.get("format") or "json")).lower()
    return parts, file_param, output_fmt, str(parsed.get("project") or project)


def _query_data(parts: list[str], project: str, file_param: str) -> tuple[Any, str]:
    if parts and parts[0] in {"status", "deps", "health"}:
        return _runtime_block(parts, project), ""
    config_path = _resolve_config_path(project, file_param or None)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return _extract_block(raw, parts), str(config_path)


def query_uri(
    uri: str,
    *,
    file: str | None = None,
    fmt: str | None = None,
    project: str = ".",
) -> QueryResult:
    parts: list[str] = []
    file_param = file or ""
    output_fmt = (fmt or "json").lower()
    try:
        parts, file_param, output_fmt, project_path = _query_context(uri, file, fmt, project)
        data, config_file = _query_data(parts, project_path, file_param)
        return _success(uri, parts, data, output_fmt, config_file)
    except Exception as exc:  # noqa: BLE001 - public API returns QueryResult failures.
        return QueryResult(
            ok=False,
            uri=uri,
            selector="/".join(parts),
            file=file_param,
            format=output_fmt,
            error=str(exc),
        )
