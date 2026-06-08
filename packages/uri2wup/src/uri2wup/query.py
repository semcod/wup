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
    if not parts or parts[0] == "config":
        return raw
    if parts[0] == "project":
        return raw.get("project", {})
    if parts[0] == "watch":
        return raw.get("watch", {})
    if parts[0] == "services":
        return raw.get("services", [])
    if parts[0] == "testql":
        return raw.get("testql", {})
    if parts[0] == "test_strategy":
        return raw.get("test_strategy", {})
    if parts[0] == "status":
        deps_path = Path("deps.json")
        from wup.paths import health_state_path

        health_path = health_state_path(".")
        return {
            "deps_exists": deps_path.exists(),
            "health_exists": health_path.exists(),
        }
    if parts[0] == "deps":
        deps_file = parts[1] if len(parts) > 1 else "deps.json"
        path = Path(deps_file)
        if not path.exists():
            raise FileNotFoundError(deps_file)
        return json.loads(path.read_text(encoding="utf-8"))
    if parts[0] == "health":
        from wup.paths import health_state_path

        path = health_state_path(".")
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
    raise ValueError(f"unsupported block path: {'/'.join(parts)}")


def query_uri(
    uri: str,
    *,
    file: str | None = None,
    fmt: str | None = None,
    project: str = ".",
) -> QueryResult:
    parsed = parse_wup_uri(uri)
    source = str(parsed["source"])
    parts = list(parsed["parts"])  # type: ignore[arg-type]
    params = parsed["params"]
    assert isinstance(params, dict)
    file_param = file or str(parsed.get("file") or "")
    output_fmt = (fmt or str(parsed.get("format") or "json")).lower()
    project_path = str(parsed.get("project") or project)

    try:
        if source != "block":
            raise ValueError(f"unsupported wup source: {source}")

        if parts and parts[0] in {"status", "deps", "health"}:
            cwd = Path(project_path).expanduser().resolve()
            data = _extract_block({}, parts)
            if parts[0] == "deps":
                deps_file = parts[1] if len(parts) > 1 else "deps.json"
                path = cwd / deps_file
                data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            elif parts[0] == "health":
                from wup.paths import health_state_path

                path = health_state_path(cwd)
                data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            else:
                from wup.paths import health_state_path

                deps_exists = (cwd / "deps.json").exists()
                health_exists = health_state_path(cwd).exists()
                data = {"deps_exists": deps_exists, "health_exists": health_exists}
            rendered = yaml.safe_dump(data, sort_keys=False) if output_fmt == "yaml" else json.dumps(data, ensure_ascii=False, indent=2)
            return QueryResult(
                ok=True,
                uri=uri,
                selector="/".join(parts),
                file="",
                data=data,
                rendered=rendered,
                format=output_fmt,
                keys=sorted(data.keys()) if isinstance(data, dict) else [],
            )

        config_path = _resolve_config_path(project_path, file_param or None)
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        data = _extract_block(raw, parts)
        rendered = yaml.safe_dump(data, sort_keys=False) if output_fmt == "yaml" else json.dumps(data, ensure_ascii=False, indent=2)
        selector = "/".join(parts) if parts else "config"
        keys = sorted(data.keys()) if isinstance(data, dict) else []
        return QueryResult(
            ok=True,
            uri=uri,
            selector=selector,
            file=str(config_path),
            data=data,
            rendered=rendered,
            format=output_fmt,
            keys=keys,
        )
    except Exception as exc:
        return QueryResult(
            ok=False,
            uri=uri,
            selector="/".join(parts),
            file=file_param,
            format=output_fmt,
            error=str(exc),
        )
