"""
Configuration loader for WUP.

Handles loading and validation of wup.yaml configuration files.
"""

import os
from pathlib import Path
from typing import Optional, List

import yaml

from .models.config import (
    WupConfig,
    WatchConfig,
    ServiceConfig,
    TestStrategyConfig,
    TestQLConfig,
    ProjectConfig,
    NotifyConfig,
    PlanfileConfig,
    SemcodToolConfig,
    SemcodToolsConfig,
    ServiceTestConfig,
    VisualDiffConfig,
    WebConfig,
)


def find_config_file(project_root: Path) -> Optional[Path]:
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


def _load_dotenv(project_root: Path) -> None:
    """Load .env and .wup.env files into os.environ (existing vars are NOT overwritten)."""
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
                if key and key not in os.environ:
                    os.environ[key] = value
        except OSError:
            pass


def load_config(project_root: Path, config_path: Optional[Path] = None) -> WupConfig:
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
    _load_dotenv(project_root)

    resolved_path = config_path
    if resolved_path is None:
        resolved_path = find_config_file(project_root)
    
    if resolved_path is None or not resolved_path.exists():
        # Return default config if no config file found
        return get_default_config(project_root)
    
    with open(resolved_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    if not raw_config:
        raise ValueError(f"Config file {resolved_path} is empty")
    
    return validate_config(raw_config)


def _parse_project_config(raw: dict) -> ProjectConfig:
    project_raw = raw.get("project", {})
    if not project_raw.get("name"):
        raise ValueError("Config must contain project.name")
    
    return ProjectConfig(
        name=project_raw["name"],
        description=project_raw.get("description", "")
    )


def _parse_watch_config(raw: dict) -> WatchConfig:
    watch_raw = raw.get("watch", {})
    return WatchConfig(
        paths=watch_raw.get("paths", []),
        exclude_patterns=watch_raw.get("exclude_patterns", ["*.md", "*.txt"]),
        file_types=watch_raw.get("file_types", [])
    )


def _parse_services_config(raw: dict) -> List[ServiceConfig]:
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
                file=notify_raw.get("file")
            )
        )
        services.append(service)
    return services


def _parse_strategy_config(raw: dict) -> TestStrategyConfig:
    strategy_raw = raw.get("test_strategy", {})
    return TestStrategyConfig(
        quick=strategy_raw.get("quick", {"debounce_s": 2, "max_queue": 5, "timeout_s": 10}),
        detail=strategy_raw.get("detail", {"debounce_s": 10, "max_queue": 1, "timeout_s": 30})
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


def _parse_testql_extra_args(extra_args_raw) -> List[str]:
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


def _normalize_testql_extra_args(extra_args_raw: List[str]) -> List[str]:
    """Normalize extra args list (e.g. converting seconds to milliseconds)."""
    normalized_extra_args = []
    i = 0
    while i < len(extra_args_raw):
        arg = extra_args_raw[i]
        if arg == "--timeout" and i + 1 < len(extra_args_raw):
            val = _normalize_testql_timeout(extra_args_raw[i+1])
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


def _parse_testql_config(raw: dict) -> TestQLConfig:
    testql_raw = raw.get("testql", {})
    extra_args_raw = testql_raw.get("extra_args", ["--timeout", "10"])
    parsed_args = _parse_testql_extra_args(extra_args_raw)
    normalized_extra_args = _normalize_testql_extra_args(parsed_args)

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
        base_url=testql_raw.get("base_url", ""),
        api_base_url=testql_raw.get("api_base_url", ""),
        base_url_env=testql_raw.get("base_url_env", "WUP_BASE_URL"),
        service_base_urls=testql_raw.get("service_base_urls", {}),
        explicit_endpoints=testql_raw.get("explicit_endpoints", []),
        endpoints_by_service=testql_raw.get("endpoints_by_service", {}),
        hardware_usb_modules=testql_raw.get("hardware_usb_modules", {}),
    )



def _parse_visual_diff_config(raw: dict) -> VisualDiffConfig:
    vd_raw = raw.get("visual_diff", {})
    env_visual_enabled = os.environ.get("WUP_VISUAL_DIFF_ENABLED")
    env_visual_delay = os.environ.get("WUP_VISUAL_DIFF_DELAY_SECONDS")
    env_visual_depth = os.environ.get("WUP_VISUAL_DIFF_MAX_DEPTH")
    env_visual_max_pages = os.environ.get("WUP_VISUAL_DIFF_MAX_PAGES")
    env_visual_pages_from_endpoints = os.environ.get("WUP_VISUAL_DIFF_PAGES_FROM_ENDPOINTS")

    if env_visual_enabled is None:
        visual_enabled = vd_raw.get("enabled", False)
    else:
        visual_enabled = env_visual_enabled.strip().lower() in {"1", "true", "yes", "on"}

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
            env_visual_pages_from_endpoints.strip().lower() in {"1", "true", "yes", "on"}
        )

    return VisualDiffConfig(
        enabled=visual_enabled,
        base_url=vd_raw.get("base_url", ""),
        base_url_env=vd_raw.get("base_url_env", "WUP_BASE_URL"),
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
        error_selectors=vd_raw.get("error_selectors", [
            "#error-container",
            ".error-container",
            "[data-testid='error-container']",
            "[class*='error'][class*='container']",
        ]),
        headless=vd_raw.get("headless", True),
        run_on_periodic_probe=bool(vd_raw.get("run_on_periodic_probe", False)),
    )


def _parse_web_config(raw: dict) -> WebConfig:
    web_raw = raw.get("web", {})
    return WebConfig(
        enabled=web_raw.get("enabled", False),
        endpoint=web_raw.get("endpoint", ""),
        endpoint_env=web_raw.get("endpoint_env", "WUPBRO_ENDPOINT"),
        timeout_s=float(web_raw.get("timeout_s", 2.0)),
        api_key=web_raw.get("api_key", ""),
    )


def _parse_planfile_config(raw: dict) -> PlanfileConfig:
    planfile_raw = raw.get("planfile", {})
    env_planfile_enabled = os.environ.get("WUP_PLANFILE_ENABLED")
    if env_planfile_enabled is None:
        planfile_enabled = bool(planfile_raw.get("enabled", False))
    else:
        planfile_enabled = env_planfile_enabled.strip().lower() in {"1", "true", "yes", "on"}

    labels_raw = planfile_raw.get("labels", ["koru", "llm-ready", "wup", "auto-diag"])
    labels = [str(label) for label in labels_raw] if isinstance(labels_raw, list) else []
    return PlanfileConfig(
        enabled=planfile_enabled,
        command=planfile_raw.get("command", "planfile"),
        sprint=planfile_raw.get("sprint", "current"),
        priority=planfile_raw.get("priority", "normal"),
        source=planfile_raw.get("source", "wup"),
        dedupe_file=planfile_raw.get("dedupe_file", ".wup/planfile-tickets.json"),
        labels=labels or ["koru", "llm-ready", "wup", "auto-diag"],
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
            commands=[str(cmd) for cmd in commands_raw] if isinstance(commands_raw, list) else [],
            artifacts=[str(path) for path in artifacts_raw] if isinstance(artifacts_raw, list) else [],
        )

    return SemcodToolsConfig(
        enabled=bool(semcod_raw.get("enabled", False)),
        tools=tools,
    )


def validate_config(raw: dict) -> WupConfig:
    """
    Validate raw config dict and convert to WupConfig object.
    
    Args:
        raw: Raw configuration dictionary from YAML
        
    Returns:
        Validated WupConfig object
        
    Raises:
        ValueError: If config is invalid
    """
    return WupConfig(
        project=_parse_project_config(raw),
        watch=_parse_watch_config(raw),
        services=_parse_services_config(raw),
        test_strategy=_parse_strategy_config(raw),
        testql=_parse_testql_config(raw),
        visual_diff=_parse_visual_diff_config(raw),
        web=_parse_web_config(raw),
        planfile=_parse_planfile_config(raw),
        semcod_tools=_parse_semcod_tools_config(raw),
    )


# Common source-directory names, in priority order, used to seed watch paths
# for an auto-generated config. Only directories that actually exist are kept,
# so the generated wup.yaml doesn't point at paths that were never there.
_DEFAULT_SOURCE_DIRS = [
    "app", "src", "routes", "services", "lib", "packages", "pkg", "internal", "cmd",
]


def detect_watch_paths(project_root: Path) -> list:
    """
    Pick watch-path globs for a project by probing for common source directories.

    Returns ``["<dir>/**", ...]`` for every well-known source directory that
    exists under ``project_root``. Falls back to the classic app/src/routes
    guess only when none are found, so a brand-new project still gets a config.
    """
    found = [f"{name}/**" for name in _DEFAULT_SOURCE_DIRS if (project_root / name).is_dir()]
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
            name=project_name,
            description=f"Auto-generated config for {project_name}"
        ),
        watch=WatchConfig(
            paths=detect_watch_paths(project_root),
            exclude_patterns=["*.md", "*.txt", "tests/**", "node_modules/**"]
        ),
        services=[],
        test_strategy=TestStrategyConfig(),
        testql=TestQLConfig()
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
        ""
    ]

    config_dict = {
        "project": {
            "name": config.project.name,
            "description": config.project.description
        },
        "watch": {
            "paths": config.watch.paths,
            "exclude_patterns": config.watch.exclude_patterns
        },
        "services": [],
        "test_strategy": {
            "quick": config.test_strategy.quick,
            "detail": config.test_strategy.detail
        },
        "testql": {
            "scenario_dir": config.testql.scenario_dir,
            "smoke_scenario": config.testql.smoke_scenario,
            "output_format": config.testql.output_format,
            "extra_args": config.testql.extra_args,
            "endpoint_discovery": config.testql.endpoint_discovery,
            "probe_interval_s": config.testql.probe_interval_s,
            "health_scenario": config.testql.health_scenario,
            "health_scenario_strict": config.testql.health_scenario_strict,
            "service_map_globs": config.testql.service_map_globs,
            "docker_service_map": config.testql.docker_service_map,
            "service_map_profile": config.testql.service_map_profile,
            "monitoring_reject_prefixes": config.testql.monitoring_reject_prefixes,
            "service_name_prefixes": config.testql.service_name_prefixes,
            "base_url": config.testql.base_url,
            "api_base_url": config.testql.api_base_url,
            "base_url_env": config.testql.base_url_env,
            "service_base_urls": config.testql.service_base_urls,
            "explicit_endpoints": config.testql.explicit_endpoints,
            "endpoints_by_service": config.testql.endpoints_by_service,
            "hardware_usb_modules": config.testql.hardware_usb_modules,
        },
        "visual_diff": {
            "enabled": config.visual_diff.enabled,
            "base_url": config.visual_diff.base_url,
            "base_url_env": config.visual_diff.base_url_env,
            "delay_seconds": config.visual_diff.delay_seconds,
            "max_depth": config.visual_diff.max_depth,
            "snapshot_dir": config.visual_diff.snapshot_dir,
            "diff_dir": config.visual_diff.diff_dir,
            "pages": config.visual_diff.pages,
            "pages_from_endpoints": config.visual_diff.pages_from_endpoints,
            "max_pages": config.visual_diff.max_pages,
            "threshold_added": config.visual_diff.threshold_added,
            "threshold_removed": config.visual_diff.threshold_removed,
            "threshold_changed": config.visual_diff.threshold_changed,
            "min_text_length": config.visual_diff.min_text_length,
            "min_dom_nodes": config.visual_diff.min_dom_nodes,
            "page_settle_ms": config.visual_diff.page_settle_ms,
            "issue_retry_count": config.visual_diff.issue_retry_count,
            "issue_retry_delay_seconds": config.visual_diff.issue_retry_delay_seconds,
            "error_selectors": config.visual_diff.error_selectors,
            "headless": config.visual_diff.headless,
        },
        "web": {
            "enabled": config.web.enabled,
            "endpoint": config.web.endpoint,
            "endpoint_env": config.web.endpoint_env,
            "timeout_s": config.web.timeout_s,
            "api_key": config.web.api_key,
        },
        "planfile": {
            "enabled": config.planfile.enabled,
            "command": config.planfile.command,
            "sprint": config.planfile.sprint,
            "priority": config.planfile.priority,
            "source": config.planfile.source,
            "dedupe_file": config.planfile.dedupe_file,
            "labels": config.planfile.labels,
        },
        "semcod_tools": {
            "enabled": config.semcod_tools.enabled,
            "tools": {
                name: {
                    "enabled": tool.enabled,
                    "repo_path": tool.repo_path,
                    "purpose": tool.purpose,
                    "commands": tool.commands,
                    "artifacts": tool.artifacts,
                }
                for name, tool in sorted(config.semcod_tools.tools.items())
            },
        }
    }
    
    for svc in config.services:
        svc_dict = {
            "name": svc.name,
            "root": svc.root,
            "paths": svc.paths,
            "quick_tests": {
                "scope": svc.quick_tests.scope,
                "max_endpoints": svc.quick_tests.max_endpoints,
                **({"scenario": svc.quick_tests.scenario} if svc.quick_tests.scenario else {}),
            },
            "detail_tests": {
                "scope": svc.detail_tests.scope,
                "max_endpoints": svc.detail_tests.max_endpoints,
                **({"scenario": svc.detail_tests.scenario} if svc.detail_tests.scenario else {}),
            },
            "cpu_throttle": svc.cpu_throttle,
            "notify": {
                "type": svc.notify.type,
                "url": svc.notify.url,
                "file": svc.notify.file
            }
        }
        config_dict["services"].append(svc_dict)

    with open(output_path, 'w') as f:
        # Write header comments
        f.write('\n'.join(header_lines))
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
        yaml_content = yaml_content.replace(
            "web:",
            f"{web_section_comment}web:"
        )

        f.write(yaml_content)
