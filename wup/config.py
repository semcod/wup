"""
Configuration loader for WUP.

Handles loading and validation of wup.yaml configuration files.
"""

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
    
    return WupConfig(
        project=project,
        watch=watch,
        services=services,
        test_strategy=test_strategy,
        testql=testql
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
    Save configuration to YAML file.
    
    Args:
        config: WupConfig object to save
        output_path: Path where to save the config
    """
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
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
