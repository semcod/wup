"""
Configuration loader for WUP.

Handles loading and validation of wup.yaml configuration files.
"""

import os
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path

import yaml

from .models.config import (
    AnomalyDetectionConfig,
    IntentMonitoringConfig,
    NotifyConfig,
    PlanfileConfig,
    ProjectConfig,
    SemcodToolConfig,
    SemcodToolsConfig,
    ServiceConfig,
    ServiceTestConfig,
    TestQLConfig,
    TestStrategyConfig,
    VisualDiffConfig,
    WatchConfig,
    WebConfig,
    WupConfig,
)


def find_config_file(project_root: Path) -> Path | None:
    """
    Find wup.yaml or .wup.yaml in project root.

    Args:
        project_root: Path to project root directory

    Returns:
        Path to config file if found, None otherwise
    """
    config_names = ["wup.yaml", ".wup.yaml"]

    for name in config_names:
        found_path = project_root / name
        if found_path.exists():
            return found_path

    return None


def _read_dotenv(project_root: Path) -> dict[str, str]:
    """Read project dotenv files without changing the process environment."""
    values: dict[str, str] = {}
    for env_file in (".wup.env", ".env"):
        env_path = project_root / env_file
        if not env_path.exists():
            continue
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in values:
                    values[key] = value
        except OSError:
            pass
    return values


def _load_dotenv(
    project_root: Path, environ: dict[str, str] | None = None
) -> dict[str, str]:
    """Load dotenv values into *environ* without overwriting existing keys.

    The default keeps the historical public helper behaviour. ``load_config``
    uses a private mapping instead, so loading one project cannot leak its
    values into another watcher in the same process.
    """
    target = os.environ if environ is None else environ
    for key, value in _read_dotenv(project_root).items():
        target.setdefault(key, value)
    return target


def load_config(project_root: Path, config_path: Path | None = None) -> WupConfig:
    """
    Load and validate wup.yaml configuration.

    Args:
        project_root: Path to project root directory
        config_path: Optional explicit path to config file

    Returns:
        Validated WupConfig object

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config is invalid
    """
    project_environ = _read_dotenv(project_root)
    # Explicit process variables have precedence over project dotenv files.
    project_environ.update(os.environ)

    resolved_path = config_path
    if resolved_path is None:
        resolved_path = find_config_file(project_root)

    if resolved_path is None or not resolved_path.exists():
        # Return default config if no config file found
        return get_default_config(project_root)

    with open(resolved_path, "r") as f:
        raw_config = yaml.safe_load(f)

    if not raw_config:
        raise ValueError(f"Config file {resolved_path} is empty")

    return validate_config(raw_config, environ=project_environ)


def _parse_project_config(raw: dict) -> ProjectConfig:
    project_raw = raw.get("project", {})
    if not project_raw.get("name"):
        raise ValueError("Config must contain project.name")

    return ProjectConfig(
        name=project_raw["name"], description=project_raw.get("description", "")
    )


def _parse_watch_config(raw: dict) -> WatchConfig:
    watch_raw = raw.get("watch", {})
    return WatchConfig(
        paths=watch_raw.get("paths", []),
        exclude_patterns=watch_raw.get("exclude_patterns", ["*.md", "*.txt"]),
        file_types=watch_raw.get("file_types", []),
    )


def _parse_services_config(raw: dict) -> list[ServiceConfig]:
    services_raw = raw.get("services", [])
    services = []
    for svc_raw in services_raw:
        if not svc_raw.get("name"):
            continue

        quick_tests_raw = svc_raw.get("quick_tests", {})
        detail_tests_raw = svc_raw.get("detail_tests", {})
        notify_raw = svc_raw.get("notify", {})

        service = ServiceConfig(
            name=svc_raw["name"],
            root=svc_raw.get("root", ""),
            paths=svc_raw.get("paths", []),
            type=svc_raw.get("type", "auto"),
            quick_tests=ServiceTestConfig(
                scope=quick_tests_raw.get("scope", "all"),
                max_endpoints=quick_tests_raw.get("max_endpoints", 10),
                scenario=quick_tests_raw.get("scenario", ""),
            ),
            detail_tests=ServiceTestConfig(
                scope=detail_tests_raw.get("scope", "all"),
                max_endpoints=detail_tests_raw.get("max_endpoints", 10),
                scenario=detail_tests_raw.get("scenario", ""),
            ),
            cpu_throttle=svc_raw.get("cpu_throttle", 0.8),
            notify=NotifyConfig(
                type=notify_raw.get("type", "file"),
                url=notify_raw.get("url"),
                file=notify_raw.get("file"),
            ),
        )
        services.append(service)
    return services


def _parse_strategy_config(raw: dict) -> TestStrategyConfig:
    strategy_raw = raw.get("test_strategy", {})
    return TestStrategyConfig(
        quick=strategy_raw.get(
            "quick", {"debounce_s": 2, "max_queue": 5, "timeout_s": 10}
        ),
        detail=strategy_raw.get(
            "detail", {"debounce_s": 10, "max_queue": 1, "timeout_s": 30}
        ),
    )


def _normalize_testql_timeout(val: str) -> str:
    """Normalize timeout value to milliseconds if it ends with 's'."""
    if val.endswith("s"):
        try:
            seconds = float(val[:-1])
            return str(int(seconds * 1000))
        except ValueError:
            pass
    return val


def _parse_testql_extra_args(extra_args_raw) -> list[str]:
    """Parse raw extra args into a flat list of string tokens."""
    if isinstance(extra_args_raw, str):
        return extra_args_raw.split()
    if isinstance(extra_args_raw, list):
        temp = []
        for arg in extra_args_raw:
            if isinstance(arg, str):
                temp.extend(arg.split())
            else:
                temp.append(str(arg))
        return temp
    return ["--timeout", "10"]


def _normalize_testql_extra_args(extra_args_raw: list[str]) -> list[str]:
    """Normalize extra args list (e.g. converting seconds to milliseconds)."""
    normalized_extra_args = []
    i = 0
    while i < len(extra_args_raw):
        arg = extra_args_raw[i]
        if arg == "--timeout" and i + 1 < len(extra_args_raw):
            val = _normalize_testql_timeout(extra_args_raw[i + 1])
            normalized_extra_args.append(arg)
            normalized_extra_args.append(val)
            i += 2
        elif arg.startswith("--timeout="):
            val = _normalize_testql_timeout(arg.partition("=")[2])
            normalized_extra_args.append(f"--timeout={val}")
            i += 1
        else:
            normalized_extra_args.append(arg)
            i += 1
    return normalized_extra_args


def _parse_testql_config(raw: dict, environ: Mapping[str, str]) -> TestQLConfig:
    testql_raw = raw.get("testql", {})
    extra_args_raw = testql_raw.get("extra_args", ["--timeout", "10"])
    parsed_args = _parse_testql_extra_args(extra_args_raw)
    normalized_extra_args = _normalize_testql_extra_args(parsed_args)

    base_url_env = testql_raw.get("base_url_env", "WUP_BASE_URL")
    return TestQLConfig(
        scenario_dir=testql_raw.get("scenario_dir", "scenarios/tests"),
        smoke_scenario=testql_raw.get("smoke_scenario", "smoke.testql.toon.yaml"),
        output_format=testql_raw.get("output_format", "json"),
        extra_args=normalized_extra_args,
        endpoint_discovery=testql_raw.get("endpoint_discovery", True),
        probe_interval_s=int(testql_raw.get("probe_interval_s", 0) or 0),
        health_scenario=testql_raw.get("health_scenario", ""),
        health_scenario_strict=bool(testql_raw.get("health_scenario_strict", False)),
        quick_smoke_only=bool(testql_raw.get("quick_smoke_only", False)),
        service_map_globs=testql_raw.get("service_map_globs", []),
        docker_service_map=testql_raw.get("docker_service_map", {}),
        service_map_profile=testql_raw.get("service_map_profile", ""),
        monitoring_reject_prefixes=testql_raw.get("monitoring_reject_prefixes", []),
        service_name_prefixes=testql_raw.get("service_name_prefixes", []),
        base_url=testql_raw.get("base_url", "") or environ.get(base_url_env, ""),
        api_base_url=testql_raw.get("api_base_url", ""),
        base_url_env=base_url_env,
        service_base_urls=testql_raw.get("service_base_urls", {}),
        explicit_endpoints=testql_raw.get("explicit_endpoints", []),
        endpoints_by_service=testql_raw.get("endpoints_by_service", {}),
        hardware_usb_modules=testql_raw.get("hardware_usb_modules", {}),
    )


def _parse_visual_diff_config(
    raw: dict, environ: Mapping[str, str]
) -> VisualDiffConfig:
    vd_raw = raw.get("visual_diff", {})
    env_visual_enabled = environ.get("WUP_VISUAL_DIFF_ENABLED")
    env_visual_delay = environ.get("WUP_VISUAL_DIFF_DELAY_SECONDS")
    env_visual_depth = environ.get("WUP_VISUAL_DIFF_MAX_DEPTH")
    env_visual_max_pages = environ.get("WUP_VISUAL_DIFF_MAX_PAGES")
    env_visual_pages_from_endpoints = environ.get(
        "WUP_VISUAL_DIFF_PAGES_FROM_ENDPOINTS"
    )
    base_url_env = vd_raw.get("base_url_env", "WUP_BASE_URL")

    if env_visual_enabled is None:
        visual_enabled = vd_raw.get("enabled", False)
    else:
        visual_enabled = env_visual_enabled.strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    if env_visual_delay is None:
        visual_delay = float(vd_raw.get("delay_seconds", 5.0))
    else:
        visual_delay = float(env_visual_delay)

    if env_visual_depth is None:
        visual_depth = int(vd_raw.get("max_depth", 10))
    else:
        visual_depth = int(env_visual_depth)

    if env_visual_max_pages is None:
        visual_max_pages = int(vd_raw.get("max_pages", 5))
    else:
        visual_max_pages = int(env_visual_max_pages)

    if env_visual_pages_from_endpoints is None:
        visual_pages_from_endpoints = bool(vd_raw.get("pages_from_endpoints", True))
    else:
        visual_pages_from_endpoints = (
            env_visual_pages_from_endpoints.strip().lower()
            in {"1", "true", "yes", "on"}
        )

    return VisualDiffConfig(
        enabled=visual_enabled,
        base_url=vd_raw.get("base_url", "") or environ.get(base_url_env, ""),
        base_url_env=base_url_env,
        delay_seconds=visual_delay,
        max_depth=visual_depth,
        snapshot_dir=vd_raw.get("snapshot_dir", ".wup/visual-snapshots"),
        diff_dir=vd_raw.get("diff_dir", ".wup/visual-diffs"),
        pages=vd_raw.get("pages", []),
        pages_from_endpoints=visual_pages_from_endpoints,
        max_pages=visual_max_pages,
        threshold_added=int(vd_raw.get("threshold_added", 3)),
        threshold_removed=int(vd_raw.get("threshold_removed", 3)),
        threshold_changed=int(vd_raw.get("threshold_changed", 5)),
        min_text_length=int(vd_raw.get("min_text_length", 200)),
        min_dom_nodes=int(vd_raw.get("min_dom_nodes", 20)),
        page_settle_ms=int(vd_raw.get("page_settle_ms", 750)),
        issue_retry_count=int(vd_raw.get("issue_retry_count", 0)),
        issue_retry_delay_seconds=float(vd_raw.get("issue_retry_delay_seconds", 2.0)),
        error_selectors=vd_raw.get(
            "error_selectors",
            [
                "#error-container",
                ".error-container",
                "[data-testid='error-container']",
                "[class*='error'][class*='container']",
            ],
        ),
        headless=vd_raw.get("headless", True),
        run_on_periodic_probe=bool(vd_raw.get("run_on_periodic_probe", False)),
    )


def _parse_web_config(raw: dict, environ: Mapping[str, str]) -> WebConfig:
    web_raw = raw.get("web", {})
    endpoint_env = web_raw.get("endpoint_env", "WUPBRO_ENDPOINT")
    return WebConfig(
        enabled=web_raw.get("enabled", False),
        endpoint=web_raw.get("endpoint", "") or environ.get(endpoint_env, ""),
        endpoint_env=endpoint_env,
        timeout_s=float(web_raw.get("timeout_s", 2.0)),
        api_key=web_raw.get("api_key", ""),
    )


def _parse_planfile_config(raw: dict, environ: Mapping[str, str]) -> PlanfileConfig:
    planfile_raw = raw.get("planfile", {})
    env_planfile_enabled = environ.get("WUP_PLANFILE_ENABLED")
    if env_planfile_enabled is None:
        planfile_enabled = bool(planfile_raw.get("enabled", False))
    else:
        planfile_enabled = env_planfile_enabled.strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    labels_raw = planfile_raw.get("labels", ["koru", "llm-ready", "wup", "auto-diag"])
    labels = (
        [str(label) for label in labels_raw] if isinstance(labels_raw, list) else []
    )
    return PlanfileConfig(
        enabled=planfile_enabled,
        command=planfile_raw.get("command", "planfile"),
        sprint=planfile_raw.get("sprint", "current"),
        priority=planfile_raw.get("priority", "normal"),
        source=planfile_raw.get("source", "wup"),
        dedupe_file=planfile_raw.get("dedupe_file", ".wup/planfile-tickets.json"),
        labels=labels or ["koru", "llm-ready", "wup", "auto-diag"],
    )


def _parse_anomaly_detection_config(raw: dict) -> AnomalyDetectionConfig:
    anomaly_raw = raw.get("anomaly_detection", {})
    defaults = AnomalyDetectionConfig()
    return AnomalyDetectionConfig(
        enabled=bool(anomaly_raw.get("enabled", defaults.enabled)),
        methods=list(anomaly_raw.get("methods", defaults.methods)),
        ignore_patterns=list(
            anomaly_raw.get("ignore_patterns", defaults.ignore_patterns)
        ),
        max_key_depth=int(anomaly_raw.get("max_key_depth", defaults.max_key_depth)),
        max_file_size_kb=int(
            anomaly_raw.get("max_file_size_kb", defaults.max_file_size_kb)
        ),
        strict_mode=bool(anomaly_raw.get("strict_mode", defaults.strict_mode)),
        watch_paths=list(anomaly_raw.get("watch_paths", defaults.watch_paths)),
        severity_threshold=str(
            anomaly_raw.get("severity_threshold", defaults.severity_threshold)
        ),
    )


def _parse_semcod_tools_config(raw: dict) -> SemcodToolsConfig:
    semcod_raw = raw.get("semcod_tools", {})
    if not isinstance(semcod_raw, dict):
        return SemcodToolsConfig()

    tools: dict[str, SemcodToolConfig] = {}
    for name, tool_raw in (semcod_raw.get("tools") or {}).items():
        if not isinstance(tool_raw, dict):
            continue
        commands_raw = tool_raw.get("commands", [])
        artifacts_raw = tool_raw.get("artifacts", [])
        tools[str(name)] = SemcodToolConfig(
            enabled=bool(tool_raw.get("enabled", True)),
            repo_path=str(tool_raw.get("repo_path", "")),
            purpose=str(tool_raw.get("purpose", "")),
            commands=[str(cmd) for cmd in commands_raw]
            if isinstance(commands_raw, list)
            else [],
            artifacts=[str(path) for path in artifacts_raw]
            if isinstance(artifacts_raw, list)
            else [],
        )

    return SemcodToolsConfig(
        enabled=bool(semcod_raw.get("enabled", False)),
        tools=tools,
    )


def _parse_intent_monitoring_config(raw: dict) -> IntentMonitoringConfig:
    intent_raw = raw.get("intent_monitoring", {})
    if not isinstance(intent_raw, dict):
        return IntentMonitoringConfig()

    defaults = IntentMonitoringConfig()
    command_raw = intent_raw.get("command", defaults.command)
    if isinstance(command_raw, str):
        command = [command_raw]
    elif isinstance(command_raw, list):
        command = [str(part) for part in command_raw if str(part)]
    else:
        command = defaults.command

    docs_raw = intent_raw.get("docs", defaults.docs)
    severities_raw = intent_raw.get("fail_severities", defaults.fail_severities)
    codes_raw = intent_raw.get("fail_codes", defaults.fail_codes)
    return IntentMonitoringConfig(
        enabled=bool(intent_raw.get("enabled", defaults.enabled)),
        runner=str(intent_raw.get("runner", defaults.runner)),
        command=command or defaults.command,
        cli_path=str(intent_raw.get("cli_path", defaults.cli_path)),
        interval_s=max(0, int(intent_raw.get("interval_s", defaults.interval_s))),
        debounce_s=max(0, int(intent_raw.get("debounce_s", defaults.debounce_s))),
        timeout_s=max(1, int(intent_raw.get("timeout_s", defaults.timeout_s))),
        run_on_start=bool(intent_raw.get("run_on_start", defaults.run_on_start)),
        run_on_change=bool(intent_raw.get("run_on_change", defaults.run_on_change)),
        mode=str(intent_raw.get("mode", defaults.mode)),
        docs_llm=bool(intent_raw.get("docs_llm", defaults.docs_llm)),
        summary_llm=bool(intent_raw.get("summary_llm", defaults.summary_llm)),
        task_file=str(intent_raw.get("task_file", defaults.task_file)),
        todo_file=str(intent_raw.get("todo_file", defaults.todo_file)),
        changelog_file=str(intent_raw.get("changelog_file", defaults.changelog_file)),
        docs=[str(item) for item in docs_raw]
        if isinstance(docs_raw, list)
        else defaults.docs,
        output_dir=str(intent_raw.get("output_dir", defaults.output_dir)),
        fail_severities=[str(item) for item in severities_raw]
        if isinstance(severities_raw, list)
        else defaults.fail_severities,
        fail_codes=[str(item) for item in codes_raw]
        if isinstance(codes_raw, list)
        else defaults.fail_codes,
    )


def validate_config(
    raw: dict, *, environ: Mapping[str, str] | None = None
) -> WupConfig:
    """
    Validate raw config dict and convert to WupConfig object.

    Args:
        raw: Raw configuration dictionary from YAML

    Returns:
        Validated WupConfig object

    Raises:
        ValueError: If config is invalid
    """
    effective_environ = os.environ if environ is None else environ
    return WupConfig(
        project=_parse_project_config(raw),
        watch=_parse_watch_config(raw),
        services=_parse_services_config(raw),
        test_strategy=_parse_strategy_config(raw),
        testql=_parse_testql_config(raw, effective_environ),
        visual_diff=_parse_visual_diff_config(raw, effective_environ),
        web=_parse_web_config(raw, effective_environ),
        planfile=_parse_planfile_config(raw, effective_environ),
        anomaly_detection=_parse_anomaly_detection_config(raw),
        semcod_tools=_parse_semcod_tools_config(raw),
        intent_monitoring=_parse_intent_monitoring_config(raw),
    )


# Common source-directory names, in priority order, used to seed watch paths
# for an auto-generated config. Only directories that actually exist are kept,
# so the generated wup.yaml doesn't point at paths that were never there.
_DEFAULT_SOURCE_DIRS = [
    "app",
    "src",
    "routes",
    "services",
    "backend",
    "frontend",
    "lib",
    "packages",
    "pkg",
    "internal",
    "cmd",
]

_WATCH_DISCOVERY_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}


def detect_watch_paths(project_root: Path) -> list:
    """
    Pick watch-path globs for a project by probing for common source directories.

    Returns ``["<dir>/**", ...]`` for every well-known source directory that
    exists directly under ``project_root``. For a directory containing several
    projects, the same probe is also performed one level down (for example,
    ``api/src/**`` and ``worker/app/**``). Hidden and vendor/build directories
    are skipped. Falls back to the classic app/src/routes guess only when none
    are found, so a brand-new project still gets a config.
    """
    found = [
        f"{name}/**" for name in _DEFAULT_SOURCE_DIRS if (project_root / name).is_dir()
    ]

    # A common workspace layout is ``root/project/src``.  WUP used to only
    # inspect ``root/src``, producing an unusable app/src/routes config for such
    # workspaces. Limit discovery to one project level so we do not accidentally
    # select vendored source trees deep inside dependencies.
    try:
        children = sorted(project_root.iterdir(), key=lambda path: path.name)
    except OSError:
        children = []

    for child in children:
        if (
            not child.is_dir()
            or child.name.startswith(".")
            or child.name in _WATCH_DISCOVERY_SKIP_DIRS
        ):
            continue
        for name in _DEFAULT_SOURCE_DIRS:
            if (child / name).is_dir():
                found.append(f"{child.name}/{name}/**")

    return found or ["app/**", "src/**", "routes/**"]


def get_default_config(project_root: Path) -> WupConfig:
    """
    Get default configuration when no config file exists.

    Args:
        project_root: Path to project root directory

    Returns:
        Default WupConfig object
    """
    project_name = project_root.name

    return WupConfig(
        project=ProjectConfig(
            name=project_name, description=f"Auto-generated config for {project_name}"
        ),
        watch=WatchConfig(
            paths=detect_watch_paths(project_root),
            exclude_patterns=["*.md", "*.txt", "tests/**", "node_modules/**"],
        ),
        services=[],
        test_strategy=TestStrategyConfig(),
        testql=TestQLConfig(),
    )


def save_config(config: WupConfig, output_path: Path):
    """
    Save configuration to YAML file with metadata header.

    Args:
        config: WupConfig object to save
        output_path: Path where to save the config
    """
    from . import __version__

    # Build metadata header
    header_lines = [
        "# WUP (What's Up) Configuration",
        f"# Version: {__version__}",
        f"# Generated: {__import__('datetime').datetime.now().isoformat()}",
        "#",
        "# Documentation:",
        "#   PyPI: https://pypi.org/project/wup/",
        "#   GitHub: https://github.com/semcod/wup",
        "#   Docs: https://github.com/semcod/wup/blob/main/README.md",
        "#",
        "# Dependencies:",
        f"#   wup=={__version__}",
        "#   wupbro (optional dashboard): pip install wupbro",
        "#",
        "# Quick Start:",
        "#   1. wup watch .                    # TestQL + live probes every 60s",
        "#   2. wup watch . --dashboard        # With live dashboard",
        "#   3. wup map-deps .                 # Build dependency map",
        "#",
        "",
    ]

    # Dataclasses are the schema. Serializing them directly prevents fields
    # added to the model from silently disappearing during load/save round-trips.
    config_dict = asdict(config)

    with open(output_path, "w") as f:
        # Write header comments
        f.write("\n".join(header_lines))
        # Write YAML content to string first
        import io

        yaml_buffer = io.StringIO()
        yaml.dump(config_dict, yaml_buffer, default_flow_style=False, sort_keys=False)
        yaml_content = yaml_buffer.getvalue()

        # Add wupbro comments before web section
        web_section_comment = """# wupbro dashboard integration - optional web UI for viewing events
# Install: pip install wupbro
# Run: wupbro --reload --port 8000
# Docs: https://github.com/semcod/wup/tree/main/wupbro
"""
        yaml_content = yaml_content.replace("web:", f"{web_section_comment}web:")

        f.write(yaml_content)
