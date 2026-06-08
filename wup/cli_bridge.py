"""Bridge legacy Typer CLI commands → dsl2wup bus."""

from __future__ import annotations

from typing import Any

from wup.control import (
    dispatch_endpoints,
    dispatch_status,
    dispatch_generate,
    dispatch_init,
    dispatch_init_cli,
    dispatch_map,
    dispatch_sync,
    dispatch_validate,
)


def _fail(result: dict[str, Any]) -> str | None:
    if result.get("ok"):
        return None
    return str(result.get("error") or "command failed")


def run_map_deps(*, project: str, out: str = "deps.json", framework: str = "auto") -> dict[str, Any]:
    return dispatch_map(project=project, out=out, framework=framework)


def run_init(*, project: str, out: str = "wup.yaml") -> dict[str, Any]:
    return dispatch_init(project=project, out=out)


def run_sync(*, project: str, file: str = "wup.yaml", merge_endpoints: bool = False) -> dict[str, Any]:
    return dispatch_sync(project=project, file=file, merge_endpoints=merge_endpoints)


def run_generate(
    *,
    project: str,
    hint: str = "quick setup",
    out: str = "wup.yaml",
    template: str = "",
) -> dict[str, Any]:
    return dispatch_generate(hint, project=project, out=out, template=template)


def run_validate(*, path: str = "wup.yaml", project: str = ".") -> dict[str, Any]:
    return dispatch_validate(path, project=project)


def run_status(
    *,
    project: str = ".",
    deps_file: str = "deps.json",
    config_file: str = "",
    delta_seconds: int = 0,
    failed_only: bool = False,
) -> dict[str, Any]:
    return dispatch_status(
        project=project,
        deps_file=deps_file,
        config_file=config_file,
        delta_seconds=delta_seconds,
        failed_only=failed_only,
    )


def run_endpoints(*, scenarios_dir: str, out: str = "testql-deps.json", testql_bin: str = "testql") -> dict[str, Any]:
    return dispatch_endpoints(scenarios_dir, out=out, testql_bin=testql_bin)


def run_init_cli(
    *,
    project: str,
    out: str = "wup.yaml",
    scenarios: str = "testql-scenarios",
    merge: bool = False,
    infer_args: bool = True,
) -> dict[str, Any]:
    return dispatch_init_cli(project=project, out=out, scenarios=scenarios, merge=merge, infer_args=infer_args)
