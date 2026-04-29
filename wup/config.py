"""
Configuration loader for WUP.

Handles loading and validation of wup.yaml configuration files.
"""

import os
from pathlib import Path
from typing import Optional

import yaml

from .models.config import (
    WupConfig,
    WatchConfig,
    ServiceConfig,
    TestStrategyConfig,
    TestQLConfig,
    ProjectConfig,
    NotifyConfig,
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
        config_path = project_root / name
        if config_path.exists():
            return config_path
    
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

    if config_path is None:
        config_path = find_config_file(project_root)
    
    if config_path is None or not config_path.exists():
        # Return default config if no config file found
        return get_default_config(project_root)
    
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    if not raw_config:
        raise ValueError(f"Config file {config_path} is empty")
    
    return validate_config(raw_config)


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
    # Parse project config
    project_raw = raw.get("project", {})
    if not project_raw.get("name"):
        raise ValueError("Config must contain project.name")
    
    project = ProjectConfig(
        name=project_raw["name"],
        description=project_raw.get("description", "")
    )
    
    # Parse watch config
    watch_raw = raw.get("watch", {})
    watch = WatchConfig(
        paths=watch_raw.get("paths", []),
        exclude_patterns=watch_raw.get("exclude_patterns", ["*.md", "*.txt"]),
        file_types=watch_raw.get("file_types", [])
    )
    
    # Parse services
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
                max_endpoints=quick_tests_raw.get("max_endpoints", 10)
            ),
            detail_tests=ServiceTestConfig(
                scope=detail_tests_raw.get("scope", "all"),
                max_endpoints=detail_tests_raw.get("max_endpoints", 10)
            ),
            cpu_throttle=svc_raw.get("cpu_throttle", 0.8),
            notify=NotifyConfig(
                type=notify_raw.get("type", "file"),
                url=notify_raw.get("url"),
                file=notify_raw.get("file")
            )
        )
        services.append(service)
    
    # Parse test strategy
    strategy_raw = raw.get("test_strategy", {})
    test_strategy = TestStrategyConfig(
        quick=strategy_raw.get("quick", {"debounce_s": 2, "max_queue": 5, "timeout_s": 10}),
        detail=strategy_raw.get("detail", {"debounce_s": 10, "max_queue": 1, "timeout_s": 30})
    )
    
    # Parse testql config
    testql_raw = raw.get("testql", {})
    testql = TestQLConfig(
        scenario_dir=testql_raw.get("scenario_dir", "scenarios/tests"),
        smoke_scenario=testql_raw.get("smoke_scenario", "smoke.testql.toon.yaml"),
        output_format=testql_raw.get("output_format", "json"),
        extra_args=testql_raw.get("extra_args", ["--timeout 10s"]),
        endpoint_discovery=testql_raw.get("endpoint_discovery", True),
        base_url=testql_raw.get("base_url", ""),
        base_url_env=testql_raw.get("base_url_env", "WUP_BASE_URL"),
        explicit_endpoints=testql_raw.get("explicit_endpoints", []),
        endpoints_by_service=testql_raw.get("endpoints_by_service", {})
    )

    # Parse visual_diff config
    vd_raw = raw.get("visual_diff", {})
    env_visual_enabled = os.environ.get("WUP_VISUAL_DIFF_ENABLED")
    env_visual_delay = os.environ.get("WUP_VISUAL_DIFF_DELAY_SECONDS")
    env_visual_depth = os.environ.get("WUP_VISUAL_DIFF_MAX_DEPTH")

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

    visual_diff = VisualDiffConfig(
        enabled=visual_enabled,
        base_url=vd_raw.get("base_url", ""),
        base_url_env=vd_raw.get("base_url_env", "WUP_BASE_URL"),
        delay_seconds=visual_delay,
        max_depth=visual_depth,
        snapshot_dir=vd_raw.get("snapshot_dir", ".wup/visual-snapshots"),
        diff_dir=vd_raw.get("diff_dir", ".wup/visual-diffs"),
        pages=vd_raw.get("pages", []),
        pages_from_endpoints=vd_raw.get("pages_from_endpoints", True),
        threshold_added=int(vd_raw.get("threshold_added", 3)),
        threshold_removed=int(vd_raw.get("threshold_removed", 3)),
        threshold_changed=int(vd_raw.get("threshold_changed", 5)),
        min_text_length=int(vd_raw.get("min_text_length", 200)),
        min_dom_nodes=int(vd_raw.get("min_dom_nodes", 20)),
        error_selectors=vd_raw.get("error_selectors", [
            "#error-container",
            ".error-container",
            "[data-testid='error-container']",
            "[class*='error'][class*='container']",
        ]),
        headless=vd_raw.get("headless", True),
    )

    # Parse web config (event sink)
    web_raw = raw.get("web", {})
    web = WebConfig(
        enabled=web_raw.get("enabled", False),
        endpoint=web_raw.get("endpoint", ""),
        endpoint_env=web_raw.get("endpoint_env", "WUPBRO_ENDPOINT"),
        timeout_s=float(web_raw.get("timeout_s", 2.0)),
        api_key=web_raw.get("api_key", ""),
    )

    return WupConfig(
        project=project,
        watch=watch,
        services=services,
        test_strategy=test_strategy,
        testql=testql,
        visual_diff=visual_diff,
        web=web,
    )


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
            paths=["app/**", "src/**", "routes/**"],
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
        f"# WUP (What's Up) Configuration",
        f"# Version: {__version__}",
        f"# Generated: {__import__('datetime').datetime.now().isoformat()}",
        f"#",
        f"# Documentation:",
        f"#   PyPI: https://pypi.org/project/wup/",
        f"#   GitHub: https://github.com/semcod/wup",
        f"#   Docs: https://github.com/semcod/wup/blob/main/README.md",
        f"#",
        f"# Dependencies:",
        f"#   wup=={__version__}",
        f"#   wupbro (optional dashboard): pip install wupbro",
        f"#",
        f"# Quick Start:",
        f"#   1. wup watch .                    # Start watching",
        f"#   2. wup watch . --dashboard        # With live dashboard",
        f"#   3. wup map-deps .                 # Build dependency map",
        f"#",
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
            "base_url": config.testql.base_url,
            "base_url_env": config.testql.base_url_env,
            "explicit_endpoints": config.testql.explicit_endpoints,
            "endpoints_by_service": config.testql.endpoints_by_service,
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
            "threshold_added": config.visual_diff.threshold_added,
            "threshold_removed": config.visual_diff.threshold_removed,
            "threshold_changed": config.visual_diff.threshold_changed,
            "min_text_length": config.visual_diff.min_text_length,
            "min_dom_nodes": config.visual_diff.min_dom_nodes,
            "error_selectors": config.visual_diff.error_selectors,
            "headless": config.visual_diff.headless,
        },
        "web": {
            "enabled": config.web.enabled,
            "endpoint": config.web.endpoint,
            "endpoint_env": config.web.endpoint_env,
            "timeout_s": config.web.timeout_s,
            "api_key": config.web.api_key,
        }
    }
    
    for svc in config.services:
        svc_dict = {
            "name": svc.name,
            "root": svc.root,
            "paths": svc.paths,
            "quick_tests": {
                "scope": svc.quick_tests.scope,
                "max_endpoints": svc.quick_tests.max_endpoints
            },
            "detail_tests": {
                "scope": svc.detail_tests.scope,
                "max_endpoints": svc.detail_tests.max_endpoints
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
