"""Write command handlers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl2wup.result import DslResult


def _read_content(path: str) -> str:
    return Path(path).expanduser().read_text(encoding="utf-8")


def _project_root(cmd: dict[str, Any]) -> Path:
    return Path(cmd.get("project") or ".").expanduser().resolve()


def handle_map(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.config import load_config
    from wup.dependency_mapper import DependencyMapper

    project = _project_root(cmd)
    out = cmd.get("out") or "deps.json"
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = project / out_path
    framework = cmd.get("framework") or "auto"
    config = load_config(project)
    mapper = DependencyMapper(str(project))
    deps = mapper.build_from_codebase(framework)
    if config.services:
        for svc in config.services:
            if svc.name not in deps.get("services", {}):
                deps.setdefault("services", {})[svc.name] = {
                    "endpoints": [],
                    "files": svc.paths,
                }
    mapper.save(str(out_path))
    return DslResult(
        ok=True,
        command=line,
        action="map",
        output=json.dumps(deps, ensure_ascii=False, indent=2),
        data={
            "output": str(out_path),
            "services": len(deps.get("services", {})),
            "files": len(deps.get("files", {})),
        },
    )


def handle_init(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.config import get_default_config, save_config

    project = _project_root(cmd)
    out = cmd.get("out") or "wup.yaml"
    output_path = Path(out)
    if not output_path.is_absolute():
        output_path = project / output_path
    if output_path.exists():
        return DslResult(ok=False, command=line, action="init", error=f"config already exists: {output_path}")
    config = get_default_config(project)
    save_config(config, output_path)
    return DslResult(
        ok=True,
        command=line,
        action="init",
        output=str(output_path),
        data={"output": str(output_path)},
    )


def handle_generate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.generate import generate_wup_config

    project = _project_root(cmd)
    hint = cmd.get("text") or ""
    template = cmd.get("template")
    out = cmd.get("out") or default_file or "wup.yaml"
    payload = generate_wup_config(project, hint=hint, template=template, out=out)
    return DslResult(
        ok=bool(payload.get("ok")),
        command=line,
        action="generate",
        output=str(payload.get("output", "")),
        data=payload,
        error=payload.get("error"),
    )


def handle_patch(cmd: dict[str, Any], *, line: str, default_file: str | None, verb: str = "patch") -> DslResult:
    from uri2wup.patch import patch_uri

    with_path = cmd.get("with_path")
    if not with_path:
        raise ValueError(f"{verb.upper()} requires WITH <fragment-file>")
    content = _read_content(with_path)
    project = str(_project_root(cmd))
    result = patch_uri(
        cmd.get("target", ""),
        content=content,
        file=cmd.get("file") or default_file,
        project=project,
    )
    return DslResult(
        ok=result.ok,
        command=line,
        action=verb,
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_sync(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.sync import sync_testql_manifest

    project = _project_root(cmd)
    payload = sync_testql_manifest(
        project,
        config_file=cmd.get("file") or default_file,
        merge_endpoints=bool(cmd.get("merge_endpoints")),
        write=True,
    )
    if not payload.get("ok"):
        return DslResult(ok=False, command=line, action="sync", error=str(payload.get("error")))
    manifest = payload.get("manifest") or {}
    return DslResult(
        ok=True,
        command=line,
        action="sync",
        output=json.dumps(manifest, ensure_ascii=False, indent=2),
        data=payload,
    )


def handle_init_cli(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.init_cli import setup_cli_project

    project = _project_root(cmd)
    payload = setup_cli_project(
        project,
        output_config=cmd.get("out") or default_file or "wup.yaml",
        output_scenarios=cmd.get("scenarios") or "testql-scenarios",
        merge=bool(cmd.get("merge")),
        infer_args=cmd.get("infer_args", True) is not False,
    )
    return DslResult(
        ok=bool(payload.get("ok")),
        command=line,
        action="init_cli",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
        error=payload.get("error"),
    )


def handle_adopt(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from wup.cli_scanner import CLIScanner

    root = Path(cmd.get("root", ".")).expanduser().resolve()
    out = cmd.get("out") or default_file or "app.doql.less"
    scanner = CLIScanner(str(root))
    packages = scanner.scan()
    lines = [
        "// Auto-adopted CLI interfaces\n",
        'interface[type="cli"] {\n  framework: argparse;\n}\n',
    ]
    for pkg in packages:
        for cmd_entry in pkg.commands:
            name = cmd_entry.name or "cli"
            module = cmd_entry.entry_point or f"{cmd_entry.module}:{cmd_entry.function}"
            lines.append(f'interface[type="cli"] page[name="{name}"] {{\n  entry: {module};\n}}\n')
    buffer_path = Path(out)
    if not buffer_path.is_absolute():
        buffer_path = root / buffer_path
    buffer_path.write_text("".join(lines), encoding="utf-8")
    return DslResult(
        ok=True,
        command=line,
        action="adopt",
        output=str(buffer_path.resolve()),
        data={"root": str(root), "output": str(buffer_path.resolve()), "packages": len(packages)},
    )


def handle_from_tokens(line: str, tokens: list[str], *, default_file: str | None) -> DslResult:
    from dsl2wup.grammar import parse_line
    from dsl2wup.handlers.query import handle_health, handle_query, handle_resolve, handle_validate

    cmd = parse_line(line)
    if cmd is None:
        return DslResult(ok=True, command=line, action="noop")
    verb = cmd["verb"]
    try:
        if verb == "QUERY":
            from dsl2wup.handlers.query import handle_query
            return handle_query(cmd, line=line, default_file=default_file)
        if verb == "VALIDATE":
            from dsl2wup.handlers.query import handle_validate
            return handle_validate(cmd, line=line, default_file=default_file)
        if verb == "RESOLVE":
            from dsl2wup.handlers.query import handle_resolve
            return handle_resolve(cmd, line=line, default_file=default_file)
        if verb == "HEALTH":
            from dsl2wup.handlers.query import handle_health
            return handle_health(cmd, line=line, default_file=default_file)
        if verb == "STATUS":
            from dsl2wup.handlers.query import handle_status
            return handle_status(cmd, line=line, default_file=default_file)
        if verb == "MAP":
            return handle_map(cmd, line=line, default_file=default_file)
        if verb == "INIT":
            return handle_init(cmd, line=line, default_file=default_file)
        if verb == "GENERATE":
            return handle_generate(cmd, line=line, default_file=default_file)
        if verb in {"PATCH", "UPDATE", "REPLACE"}:
            return handle_patch(cmd, line=line, default_file=default_file, verb=verb.lower())
        if verb == "SYNC":
            return handle_sync(cmd, line=line, default_file=default_file)
        if verb == "ADOPT":
            return handle_adopt(cmd, line=line, default_file=default_file)
        if verb == "INIT_CLI":
            return handle_init_cli(cmd, line=line, default_file=default_file)
        if verb == "ENDPOINTS":
            from dsl2wup.handlers.query import handle_endpoints
            return handle_endpoints(cmd, line=line, default_file=default_file)
        return DslResult(ok=False, command=line, action=verb.lower(), error=f"unknown command: {verb}")
    except Exception as exc:
        return DslResult(ok=False, command=line, action=verb.lower(), error=str(exc))
