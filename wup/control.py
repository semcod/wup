"""Thin shim — delegate legacy/SDK callers to dsl2wup bus."""

from __future__ import annotations

from typing import Any


def _result_dict(line: str, *, default_file: str | None = None) -> dict[str, Any]:
    try:
        from dsl2wup import dispatch
    except ModuleNotFoundError as exc:
        if exc.name == "dsl2wup":
            raise RuntimeError(
                "WUP control DSL is optional; install it with `pip install 'wup[control]'`"
            ) from exc
        raise

    return dispatch(line, default_file=default_file).to_dict()


def dispatch_validate(
    path: str = "wup.yaml", *, project: str = ".", default_file: str | None = None
) -> dict[str, Any]:
    return _result_dict(f"VALIDATE {path} PROJECT {project}", default_file=default_file)


def dispatch_query(
    target: str, *, file: str = "", project: str = ".", fmt: str = "json"
) -> dict[str, Any]:
    parts = [f"QUERY {target}"]
    if file:
        parts.append(f"FILE {file}")
    if fmt:
        parts.append(f"FORMAT {fmt}")
    parts.append(f"PROJECT {project}")
    return _result_dict(" ".join(parts))


def dispatch_health(*, service: str = "", project: str = ".") -> dict[str, Any]:
    line = (
        f"HEALTH {service} PROJECT {project}".strip()
        if service
        else f"HEALTH PROJECT {project}"
    )
    return _result_dict(line)


def dispatch_map(
    *, project: str = ".", out: str = "deps.json", framework: str = "auto"
) -> dict[str, Any]:
    return _result_dict(f"MAP {project} OUT {out} FRAMEWORK {framework}")


def dispatch_init(*, project: str = ".", out: str = "wup.yaml") -> dict[str, Any]:
    return _result_dict(f"INIT {project} OUT {out}")


def dispatch_sync(
    *, project: str = ".", file: str = "wup.yaml", merge_endpoints: bool = False
) -> dict[str, Any]:
    line = f"SYNC {project} FILE {file}"
    if merge_endpoints:
        line += " MERGE"
    return _result_dict(line)


def dispatch_generate(
    hint: str = "",
    *,
    project: str = ".",
    out: str = "wup.yaml",
    template: str = "",
) -> dict[str, Any]:
    text = hint or "quick setup"
    line = f'GENERATE "{text}" OUT {out} PROJECT {project}'
    if template:
        line += f" TEMPLATE {template}"
    return _result_dict(line)


def dispatch_status(
    *,
    project: str = ".",
    deps_file: str = "deps.json",
    config_file: str = "",
    delta_seconds: int = 0,
    failed_only: bool = False,
) -> dict[str, Any]:
    line = f"STATUS PROJECT {project} DEPS {deps_file}"
    if config_file:
        line += f" FILE {config_file}"
    if delta_seconds:
        line += f" DELTA {delta_seconds}"
    if failed_only:
        line += " FAILED_ONLY"
    return _result_dict(line)


def dispatch_endpoints(
    scenarios_dir: str,
    *,
    out: str = "testql-deps.json",
    testql_bin: str = "testql",
) -> dict[str, Any]:
    return _result_dict(f"ENDPOINTS {scenarios_dir} OUT {out} TESTQL_BIN {testql_bin}")


def dispatch_init_cli(
    *,
    project: str = ".",
    out: str = "wup.yaml",
    scenarios: str = "testql-scenarios",
    merge: bool = False,
    infer_args: bool = True,
) -> dict[str, Any]:
    line = f"INIT_CLI {project} OUT {out} SCENARIOS {scenarios}"
    if merge:
        line += " MERGE"
    if not infer_args:
        line += " INFER_ARGS false"
    return _result_dict(line)


def dispatch_command(
    command: str, *, default_file: str | None = None
) -> dict[str, Any]:
    return _result_dict(command, default_file=default_file)
