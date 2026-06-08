"""Read-only query handlers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl2wup.result import DslResult


def _project_root(cmd: dict[str, Any], default_file: str | None) -> Path:
    project = cmd.get("project") or "."
    return Path(project).expanduser().resolve()


def handle_query(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2wup.query import query_uri

    uri = cmd.get("target", "")
    file_param = cmd.get("file") or default_file
    fmt = (cmd.get("format") or "json").lower()
    project = str(_project_root(cmd, default_file))
    result = query_uri(uri, file=file_param, fmt=fmt, project=project)
    return DslResult(
        ok=result.ok,
        command=line,
        action="query",
        output=result.rendered or json.dumps(result.data, ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_validate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.validate import validate_wup_file

    project = str(_project_root(cmd, default_file))
    path = cmd.get("path") or default_file
    payload = validate_wup_file(path, project=project)
    return DslResult(
        ok=bool(payload.get("ok")),
        command=line,
        action="validate",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
        error=None if payload.get("ok") else str(payload.get("error") or "; ".join(payload.get("issues") or [])),
    )


def handle_resolve(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2wup.nlp2uri import nlp2uri

    prompt = cmd.get("text", "")
    project = str(_project_root(cmd, default_file))
    hits = nlp2uri(prompt, file=cmd.get("file") or default_file, project=project)
    payload = [hit.to_dict() for hit in hits]
    return DslResult(
        ok=bool(hits),
        command=line,
        action="resolve",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data={"hits": payload},
        error=None if hits else "no URI matches",
    )


def handle_status(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.status_data import collect_status_snapshot

    project = str(_project_root(cmd, default_file))
    payload = collect_status_snapshot(
        project,
        deps_file=cmd.get("deps_file") or "deps.json",
        config_file=cmd.get("file") or default_file,
        delta_seconds=int(cmd.get("delta_seconds") or 0),
        failed_only=bool(cmd.get("failed_only")),
    )
    return DslResult(
        ok=True,
        command=line,
        action="status",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
    )


def handle_endpoints(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.endpoints import discover_testql_endpoints

    scenarios_dir = cmd.get("scenarios_dir", "")
    if not scenarios_dir:
        return DslResult(ok=False, command=line, action="endpoints", error="scenarios_dir required")
    payload = discover_testql_endpoints(
        scenarios_dir,
        testql_bin=cmd.get("testql_bin") or "testql",
        out=cmd.get("out") or "testql-deps.json",
    )
    return DslResult(
        ok=bool(payload.get("ok")),
        command=line,
        action="endpoints",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
        error=payload.get("error"),
    )


def handle_health(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    project = _project_root(cmd, default_file)
    from wup.paths import health_state_path

    health_path = health_state_path(project)
    data: dict[str, Any] = {}
    if health_path.exists():
        try:
            data = json.loads(health_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    service = cmd.get("service")
    if service:
        payload = data.get(service, {})
        return DslResult(
            ok=bool(payload),
            command=line,
            action="health",
            output=json.dumps(payload, ensure_ascii=False, indent=2),
            data={"service": service, "health": payload},
            error=None if payload else f"no health data for {service}",
        )
    return DslResult(
        ok=True,
        command=line,
        action="health",
        output=json.dumps(data, ensure_ascii=False, indent=2),
        data={"health": data},
    )
