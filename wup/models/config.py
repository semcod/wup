"""
Configuration dataclasses for WUP.

Defines the structure for wup.yaml configuration file.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

ServiceType = Literal["web", "shell", "auto"]


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
    scenario: str = ""  # Optional pinned scenario path (relative to project root or scenarios_dir)


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
    __test__ = False
    quick: Dict = field(default_factory=lambda: {"debounce_s": 2, "max_queue": 5, "timeout_s": 10})
    detail: Dict = field(default_factory=lambda: {"debounce_s": 10, "max_queue": 1, "timeout_s": 30})


@dataclass
class TestQLConfig:
    """TestQL-specific configuration."""
    __test__ = False
    scenario_dir: str = "scenarios/tests"
    smoke_scenario: str = "smoke.testql.toon.yaml"
    output_format: str = "json"
    extra_args: List[str] = field(default_factory=lambda: ["--timeout", "10"])
    endpoint_discovery: bool = True  # Merge health probes from scenarios + service maps
    probe_interval_s: int = 0  # Periodic live probes for all services (0 = file-change only)
    health_scenario: str = ""  # Fleet TestQL scenario on each periodic probe cycle (live run)
    health_scenario_strict: bool = False  # If false, fleet scenario failure is logged but does not block per-service probes
    quick_smoke_only: bool = False  # Quick TestQL uses smoke_scenario only (skip auto-api scoring)
    service_map_globs: List[str] = field(default_factory=list)  # e.g. testql-testing/service-map/*.yaml
    base_url: str = ""
    api_base_url: str = ""  # Core API (c2004: http://localhost:8101) — used for backend probes
    base_url_env: str = "WUP_BASE_URL"
    service_base_urls: Dict[str, str] = field(default_factory=dict)  # optional per-service override
    explicit_endpoints: List[str] = field(default_factory=list)
    endpoints_by_service: Dict[str, List[str]] = field(default_factory=dict)
    # USB kit modules: expand HTTP API probes from module_ids (no /dev/* paths).
    hardware_usb_modules: Dict[str, object] = field(default_factory=dict)


@dataclass
class VisualDiffConfig:
    """Configuration for visual DOM diff after file changes."""
    enabled: bool = False
    base_url: str = ""
    base_url_env: str = "WUP_BASE_URL"
    delay_seconds: float = 5.0       # wait after file change before scanning
    max_depth: int = 10              # DOM depth for snapshot
    snapshot_dir: str = ".wup/visual-snapshots"
    diff_dir: str = ".wup/visual-diffs"
    pages: List[str] = field(default_factory=list)  # explicit page paths to scan
    pages_from_endpoints: bool = True
    max_pages: int = 5  # cap DOM scans per service per file change
    threshold_added: int = 3         # min added nodes to report
    threshold_removed: int = 3       # min removed nodes to report
    threshold_changed: int = 5       # min changed attrs to report
    min_text_length: int = 200       # anomaly if rendered text is too short
    min_dom_nodes: int = 20          # anomaly if DOM is suspiciously tiny
    page_settle_ms: int = 750        # wait after networkidle before snapshotting SPA DOM
    issue_retry_count: int = 0       # retry transient Vite/HMR/page-shell issues
    issue_retry_delay_seconds: float = 2.0
    error_selectors: List[str] = field(default_factory=lambda: [
        "#error-container",
        ".error-container",
        "[data-testid='error-container']",
        "[class*='error'][class*='container']",
    ])
    headless: bool = True
    # Run visual_diff during periodic probe cycles too. Default false: visual_diff
    # only runs when something on disk actually changed (or on first cycle).
    run_on_periodic_probe: bool = False


@dataclass
class WebConfig:
    """Configuration for sending events to wupbro backend."""
    enabled: bool = False
    endpoint: str = ""              # e.g. "http://localhost:8000/events"
    endpoint_env: str = "WUPBRO_ENDPOINT"
    timeout_s: float = 2.0          # short — must not block watcher
    api_key: str = ""               # optional bearer token


@dataclass
class PlanfileConfig:
    """Configuration for creating planfile tickets from WUP failures."""
    enabled: bool = False
    command: str = "planfile"
    sprint: str = "current"
    priority: str = "normal"
    source: str = "wup"
    dedupe_file: str = ".wup/planfile-tickets.json"
    labels: List[str] = field(default_factory=lambda: [
        "koru",
        "llm-ready",
        "wup",
        "auto-diag",
    ])


@dataclass
class AnomalyDetectionConfig:
    """Configuration for fast anomaly detection without Playwright."""
    enabled: bool = True
    methods: List[str] = field(default_factory=lambda: ['hash', 'structure'])  # 'hash', 'structure', 'keys', 'ast', 'text'
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '*.tmp', '*.bak', '*~', '.git/*', '__pycache__/*', '.venv/*', 'node_modules/*'
    ])
    max_key_depth: int = 5
    max_file_size_kb: int = 500
    strict_mode: bool = False  # True = detect minor changes
    watch_paths: List[str] = field(default_factory=list)
    severity_threshold: str = "medium"  # 'low', 'medium', 'high', 'critical'


@dataclass
class SemcodToolConfig:
    """Optional Semcod ecosystem tool attached to WUP monitoring audit."""
    enabled: bool = True
    repo_path: str = ""
    purpose: str = ""
    commands: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class SemcodToolsConfig:
    """Optional Semcod ecosystem integrations (deta/regres/regix)."""
    enabled: bool = False
    tools: Dict[str, SemcodToolConfig] = field(default_factory=dict)


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
    visual_diff: VisualDiffConfig = field(default_factory=VisualDiffConfig)
    web: WebConfig = field(default_factory=WebConfig)
    planfile: PlanfileConfig = field(default_factory=PlanfileConfig)
    anomaly_detection: AnomalyDetectionConfig = field(default_factory=AnomalyDetectionConfig)
    semcod_tools: SemcodToolsConfig = field(default_factory=SemcodToolsConfig)
