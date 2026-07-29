"""Stable Typer CLI bridge implemented by WUP's local domain services.

The base ``wup`` wheel must not require the optional DSL workspace merely to
run its documented CLI commands. The DSL package can still call the same
domain services through its own handlers.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _result(
    action: str,
    data: dict[str, Any],
    *,
    output: str = "",
) -> dict[str, Any]:
    ok = bool(data.get("ok", True))
    return {
        "ok": ok,
        "command": "",
        "action": action,
        "output": output,
        "data": data,
        "error": None if ok else str(data.get("error") or "command failed"),
        "event_id": None,
    }


def _guard(
    action: str, operation: Callable[[], dict[str, Any]], *, output_key: str = ""
) -> dict[str, Any]:
    try:
        data = operation()
        output = str(data.get(output_key, "")) if output_key else ""
        return _result(action, data, output=output)
    except Exception as exc:  # noqa: BLE001 - CLI boundary returns structured failures.
        return _result(action, {"ok": False, "error": str(exc)})


def run_map_deps(
    *, project: str, out: str = "deps.json", framework: str = "auto"
) -> dict[str, Any]:
    def operation() -> dict[str, Any]:
        from wup.config import load_config
        from wup.dependency_mapper import DependencyMapper

        root = Path(project).expanduser().resolve()
        output_path = Path(out)
        if not output_path.is_absolute():
            output_path = root / output_path
        config = load_config(root)
        mapper = DependencyMapper(str(root))
        deps = mapper.build_from_codebase(framework)
        for service in config.services:
            deps.setdefault("services", {}).setdefault(
                service.name,
                {"endpoints": [], "files": service.paths},
            )
        mapper.save(str(output_path))
        return {
            "ok": True,
            "output": str(output_path),
            "services": len(deps.get("services", {})),
            "files": len(deps.get("files", {})),
            "deps": deps,
        }

    result = _guard("map", operation)
    if result["ok"]:
        result["output"] = json.dumps(
            result["data"].pop("deps"), ensure_ascii=False, indent=2
        )
    return result


def run_init(*, project: str, out: str = "wup.yaml") -> dict[str, Any]:
    def operation() -> dict[str, Any]:
        from wup.config import get_default_config, save_config

        root = Path(project).expanduser().resolve()
        output_path = Path(out)
        if not output_path.is_absolute():
            output_path = root / output_path
        if output_path.exists():
            return {"ok": False, "error": f"config already exists: {output_path}"}
        save_config(get_default_config(root), output_path)
        return {"ok": True, "output": str(output_path)}

    return _guard("init", operation, output_key="output")


def run_sync(
    *, project: str, file: str = "wup.yaml", merge_endpoints: bool = False
) -> dict[str, Any]:
    from wup.sync import sync_testql_manifest

    return _guard(
        "sync",
        lambda: sync_testql_manifest(
            project,
            config_file=file,
            merge_endpoints=merge_endpoints,
            write=True,
        ),
    )


def run_generate(
    *,
    project: str,
    hint: str = "quick setup",
    out: str = "wup.yaml",
    template: str = "",
) -> dict[str, Any]:
    from wup.generate import generate_wup_config

    return _guard(
        "generate",
        lambda: generate_wup_config(
            project, hint=hint, template=template or None, out=out
        ),
        output_key="output",
    )


def run_validate(*, path: str = "wup.yaml", project: str = ".") -> dict[str, Any]:
    from wup.validate import validate_wup_file

    return _guard("validate", lambda: validate_wup_file(path, project=project))


def run_status(
    *,
    project: str = ".",
    deps_file: str = "deps.json",
    config_file: str = "",
    delta_seconds: int = 0,
    failed_only: bool = False,
) -> dict[str, Any]:
    from wup.status_data import collect_status_snapshot

    result = _guard(
        "status",
        lambda: collect_status_snapshot(
            project,
            deps_file=deps_file,
            config_file=config_file or None,
            delta_seconds=delta_seconds,
            failed_only=failed_only,
        ),
    )
    if result["ok"]:
        result["output"] = json.dumps(result["data"], ensure_ascii=False, indent=2)
    return result


def run_endpoints(
    *, scenarios_dir: str, out: str = "testql-deps.json", testql_bin: str = "testql"
) -> dict[str, Any]:
    from wup.endpoints import discover_testql_endpoints

    return _guard(
        "endpoints",
        lambda: discover_testql_endpoints(
            scenarios_dir, testql_bin=testql_bin, out=out
        ),
    )


def run_init_cli(
    *,
    project: str,
    out: str = "wup.yaml",
    scenarios: str = "testql-scenarios",
    merge: bool = False,
    infer_args: bool = True,
) -> dict[str, Any]:
    from wup.init_cli import setup_cli_project

    return _guard(
        "init_cli",
        lambda: setup_cli_project(
            project,
            output_config=out,
            output_scenarios=scenarios,
            merge=merge,
            infer_args=infer_args,
        ),
    )
