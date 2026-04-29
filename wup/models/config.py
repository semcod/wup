"""
Configuration dataclasses for WUP.

Defines the structure for wup.yaml configuration file.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NotifyConfig:
    """Notification configuration for a service."""
    type: str = "file"  # "http", "file", "http+file"
    url: Optional[str] = None
    file: Optional[str] = None


@dataclass
class ServiceTestConfig:
    """Test configuration for a service (quick or detail)."""
    scope: str = "all"  # "read", "write", "auth", "all", or comma-separated
    max_endpoints: int = 10


@dataclass
class ServiceConfig:
    """Configuration for a single service."""
    name: str
    root: str = ""  # Optional - auto-detected if empty
    paths: List[str] = field(default_factory=list)  # Optional - auto-detected if empty
    type: str = "auto"  # "web", "shell", "auto" - for coincidence detection
    quick_tests: ServiceTestConfig = field(default_factory=ServiceTestConfig)
    detail_tests: ServiceTestConfig = field(default_factory=ServiceTestConfig)
    cpu_throttle: float = 0.8
    notify: NotifyConfig = field(default_factory=NotifyConfig)


@dataclass
class WatchConfig:
    """Configuration for file watching."""
    paths: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.md", "*.txt"])
    file_types: List[str] = field(default_factory=list)  # e.g., [".py", ".ts", ".jsx"]


@dataclass
class TestStrategyConfig:
    """Global test strategy configuration."""
    quick: Dict = field(default_factory=lambda: {"debounce_s": 2, "max_queue": 5, "timeout_s": 10})
    detail: Dict = field(default_factory=lambda: {"debounce_s": 10, "max_queue": 1, "timeout_s": 30})


@dataclass
class TestQLConfig:
    """TestQL-specific configuration."""
    scenario_dir: str = "scenarios/tests"
    smoke_scenario: str = "smoke.testql.toon.yaml"
    output_format: str = "json"
    extra_args: List[str] = field(default_factory=lambda: ["--timeout 10s"])
    endpoint_discovery: bool = True  # Enable automatic endpoint discovery from scenarios
    base_url: str = ""
    base_url_env: str = "WUP_BASE_URL"
    explicit_endpoints: List[str] = field(default_factory=list)
    endpoints_by_service: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ProjectConfig:
    """Project metadata."""
    name: str
    description: str = ""


@dataclass
class WupConfig:
    """Main WUP configuration."""
    project: ProjectConfig
    watch: WatchConfig = field(default_factory=WatchConfig)
    services: List[ServiceConfig] = field(default_factory=list)
    test_strategy: TestStrategyConfig = field(default_factory=TestStrategyConfig)
    testql: TestQLConfig = field(default_factory=TestQLConfig)
