"""
Core module for WUP (What's Up) - Intelligent file watcher for regression testing.
"""

import asyncio
import errno
import fnmatch
import json
import subprocess
import time
import urllib.error
import urllib.request
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Set

import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .config import detect_watch_paths, load_config
from .dependency_mapper import DependencyMapper
from .models.config import WupConfig, ServiceConfig
from .models.target import ServiceTestTarget
from .planfile_reporter import PlanfileReporter


class WupWatcher:
    """
    Intelligent file watcher for regression testing.
    
    Implements 3-layer testing:
    1. Detection Layer: File watching with heuristics
    2. Priority Layer: Quick tests of related services
    3. Detail Layer: Full tests with blame reports (only on failure)
    """
    
    def __init__(
        self,
        project_root: str,
        deps_file: str = "deps.json",
        cpu_throttle: float = 0.8,
        debounce_seconds: int = 2,
        test_cooldown_seconds: int = 300,
        config: Optional[WupConfig] = None
    ):
        """
        Initialize the WUP watcher.
        
        Args:
            project_root: Path to the project root directory
            deps_file: Path to the dependency map JSON file
            cpu_throttle: Maximum CPU usage threshold (0.0-1.0)
            debounce_seconds: Debounce time for file changes
            test_cooldown_seconds: Minimum time between tests for same service
            config: Optional WupConfig object (loaded from wup.yaml if not provided)
        """
        self.project_root = Path(project_root)
        self.deps_file = deps_file
        
        # Load config if not provided
        if config is None:
            self.config = load_config(self.project_root)
        else:
            self.config = config
        
        # Use explicit parameters, fall back to config values if not explicitly set
        # Check if parameters were explicitly provided (not default values)
        # For now, use config values only if explicit parameters weren't provided
        # We'll use config as fallback for default values
        final_cpu_throttle = cpu_throttle
        final_debounce_seconds = debounce_seconds
        final_test_cooldown_seconds = test_cooldown_seconds
        
        if self.config.test_strategy:
            # Only use config values if parameters are at their defaults
            if cpu_throttle == 0.8:  # default value
                final_cpu_throttle = self.config.test_strategy.quick.get("cpu_throttle", cpu_throttle)
            if debounce_seconds == 2:  # default value
                final_debounce_seconds = self.config.test_strategy.quick.get("debounce_s", debounce_seconds)
            if test_cooldown_seconds == 300:  # default value
                final_test_cooldown_seconds = self.config.test_strategy.quick.get("cooldown_s", test_cooldown_seconds)
        
        self.cpu_throttle = final_cpu_throttle
        self.debounce_seconds = final_debounce_seconds
        self.test_cooldown_seconds = final_test_cooldown_seconds
        
        self.dependency_mapper = DependencyMapper(str(self.project_root))
        self.changed_services: Set[str] = set()
        self.test_queue: deque = deque()

        # Event-level debounce: a single editor save emits a cascade of
        # watchdog events (modify + create + close). Aggregate per service
        # within the debounce window instead of scheduling per event.
        self._pending_events: Dict[str, List[str]] = defaultdict(list)
        self._pending_event_times: Dict[str, float] = defaultdict(float)
        from .realtime_anomalies import ChangeBurstDetector, LatencyTracker
        self.burst_detector = ChangeBurstDetector()
        self.latency_tracker = LatencyTracker()

        # Offline drift detection (hash/AST) for changed files. Lazy import
        # keeps CLI startup unchanged when anomaly scanning is not exercised.
        self._anomaly_detector = None
        self.last_test_times: Dict[str, float] = defaultdict(float)
        self.console = Console()
        self.planfile_reporter = PlanfileReporter(
            project_root=self.project_root,
            config=self.config.planfile,
            console=self.console,
        )
        
        # Load or build dependency map
        if Path(deps_file).exists():
            self.dependency_mapper.load(deps_file)
        else:
            self.console.print("[yellow]Building dependency map...[/yellow]")
            self.dependency_mapper.build_from_codebase()
            self.dependency_mapper.save(deps_file)

    def _to_relative_path(self, file_path: str) -> Path:
        file_path_obj = Path(file_path)
        try:
            return file_path_obj.relative_to(self.project_root)
        except ValueError:
            return file_path_obj
    
    # Generic top-level directory prefixes that name a service on their own.
    _GENERIC_SERVICE_PREFIXES = ("backend", "frontend", "api", "app", "worker", "service")

    def _service_name_prefixes(self) -> List[str]:
        """Effective service-name prefixes: generic set + config + profile."""
        prefixes = list(self._GENERIC_SERVICE_PREFIXES)
        testql = getattr(self.config, "testql", None)
        prefixes.extend(getattr(testql, "service_name_prefixes", None) or [])
        if (getattr(testql, "service_map_profile", "") or "").lower() == "connect":
            prefixes.append("connect")
        return prefixes

    def infer_service(self, file_path: str) -> Optional[str]:
        """
        Infer service name from file path.

        Uses config services first, then dependency mapper, then heuristics.
        """
        rel_path = self._to_relative_path(file_path)
        parts = rel_path.parts
        
        # Try to match against configured services first
        if self.config.services:
            for svc in self.config.services:
                if svc.paths:
                    # Use explicit paths if provided
                    for svc_path in svc.paths:
                        if str(rel_path).startswith(svc_path.replace("**", "")):
                            return svc.name
                else:
                    # Auto-detect: check if service name appears in path
                    # Require the full service name to match as a complete segment
                    path_lower = str(rel_path).lower()
                    service_name_lower = svc.name.lower()
                    
                    # Check if service name appears as a complete segment (separated by /, -, _, or .)
                    import re
                    pattern = r'(?:[\/\-_.]|^)' + re.escape(service_name_lower) + r'(?:[\/\-_.]|$)'
                    if re.search(pattern, path_lower):
                        return svc.name
        
        # Heuristic: if the top-level directory starts with a known service prefix
        # (e.g. api-*, worker-*), use it directly — takes priority over stale
        # deps.json. Prefixes are generic by default; projects add their own via
        # testql.service_name_prefixes, and the "connect" profile adds connect-*.
        if parts:
            top = parts[0]
            import re as _re
            prefixes = "|".join(_re.escape(p) for p in self._service_name_prefixes())
            if prefixes and _re.match(rf'^({prefixes})[-_]', top):
                return top

        # Use dependency mapper if available
        service = self.dependency_mapper.get_service_for_file(file_path)
        if service:
            return service

        # Fallback: return None to let caller handle configured services
        # Don't construct fake service names from path parts
        return None
    
    def _is_coincident_pair(self, type_a: str, type_b: str) -> bool:
        """Return True when two service types form a coincident pair (shell↔web or auto↔explicit)."""
        if type_a != "auto" and type_b != "auto":
            return (type_a == "shell" and type_b == "web") or (type_a == "web" and type_b == "shell")
        return (type_a == "auto") != (type_b == "auto")

    def detect_service_coincidences(self, changed_service: str) -> List[str]:
        """
        Detect coincidences between services (e.g., shell <-> web).
        
        When a service changes, this finds related services that should also be tested.
        
        Args:
            changed_service: The service that changed
            
        Returns:
            List of related services that should also be tested
        """
        if not self.config.services:
            return []

        changed_svc_config = next(
            (svc for svc in self.config.services if svc.name == changed_service), None
        )
        if not changed_svc_config:
            return []

        return [
            svc.name
            for svc in self.config.services
            if svc.name != changed_service
            and self._is_coincident_pair(changed_svc_config.type, svc.type)
            and self._services_share_domain(changed_service, svc.name)
        ]
    
    def _services_share_domain(self, service1: str, service2: str) -> bool:
        """
        Check if two services share a common domain/base name.
        
        Examples:
            users-shell and users-web -> True
            api/auth and api/users -> False
            payments and payments-shell -> True
        """
        # Extract base names (remove type suffixes like -shell, -web)
        def extract_base(name: str) -> str:
            for suffix in ["-shell", "-web", "_shell", "_web"]:
                if name.endswith(suffix):
                    return name[:-len(suffix)]
            return name
        
        base1 = extract_base(service1)
        base2 = extract_base(service2)
        
        return base1 == base2
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """
        Get service configuration by name.
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceConfig if found, None otherwise
        """
        for svc in self.config.services:
            if svc.name == service_name:
                return svc
        return None
    
    def should_test(self, service: str) -> bool:
        """
        Check if a service should be tested based on cooldown.
        
        Args:
            service: Service name to check
            
        Returns:
            True if service should be tested, False otherwise
        """
        now = time.time()
        last_test = self.last_test_times.get(service, 0)
        return (now - last_test) >= self.test_cooldown_seconds
    
    def schedule_quick_test(self, service: str):
        """
        Schedule a quick test for a service.
        
        Args:
            service: Service name to test
        """
        endpoints = self.dependency_mapper.get_endpoints_for_service(service)
        
        # Use service config for max_endpoints if available
        svc_config = self.get_service_config(service)
        max_endpoints = 3
        if svc_config and svc_config.quick_tests:
            max_endpoints = svc_config.quick_tests.max_endpoints
        
        self.test_queue.append(("quick", service, endpoints[:max_endpoints]))
        self.last_test_times[service] = time.time()
    
    def schedule_detail_test(self, service: str):
        """
        Schedule a detailed test for a service.
        
        Args:
            service: Service name to test
        """
        endpoints = self.dependency_mapper.get_endpoints_for_service(service)
        self.test_queue.appendleft(("detail", service, endpoints))

    def _flush_pending_events(self) -> None:
        """Schedule quick tests for services whose debounce window elapsed."""
        now = time.time()
        for service in list(self._pending_events):
            last_seen = self._pending_event_times.get(service, 0)
            if now - last_seen < self.debounce_seconds:
                continue
            files = self._pending_events.pop(service)
            self._pending_event_times.pop(service, None)
            if self.should_test(service):
                self.console.print(
                    f"[yellow]📝 {len(files)} change(s) debounced → Service: {service}[/yellow]"
                )
                self.schedule_quick_test(service)
                self._scan_drift(files)

    def _scan_drift(self, files: List[str]) -> None:
        """Hash/AST drift scan for changed files; report high-severity findings."""
        try:
            if self._anomaly_detector is None:
                from .anomaly_detector import AnomalyDetector
                self._anomaly_detector = AnomalyDetector(self.project_root)
            for file_path in files:
                for result in self._anomaly_detector.scan_file(file_path):
                    if result.severity in ("high", "critical"):
                        self.console.print(
                            f"[red]🚨 Drift [{result.detector}] {result.file_path}: "
                            f"{result.message}[/red]"
                        )
                        self.planfile_reporter.report_failure(
                            service="drift",
                            status=result.severity,
                            stage="anomaly",
                            message=f"{result.file_path}: {result.message}",
                        )
        except Exception as exc:  # noqa: BLE001
            self.console.print(f"[dim]Drift scan skipped: {exc}[/dim]")

    async def process_test_queue_once(self):
        if not self.test_queue or not await self.cpu_ok():
            return

        test_type, service, endpoints = self.test_queue.popleft()
        target = ServiceTestTarget(service, endpoints)

        try:
            if test_type == "quick":
                passed = await self.run_quick_test(target)
                if not passed:
                    self.schedule_detail_test(service)
            elif test_type == "detail":
                await self.run_detail_test(target)
        except Exception as e:
            self.console.print(f"[red]Error testing {service}: {e}[/red]")
    
    async def cpu_ok(self) -> bool:
        """
        Check if CPU usage is below threshold.
        
        Returns:
            True if CPU usage is acceptable, False otherwise
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return cpu_percent < (self.cpu_throttle * 100)
        except Exception:
            return True
    
    def _probe_endpoint(self, endpoint: str):
        """Synchronous HEAD probe; returns (endpoint, ok, status, latency_ms, err)."""
        started = time.monotonic()
        try:
            req = urllib.request.Request(endpoint, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                latency_ms = (time.monotonic() - started) * 1000
                return endpoint, resp.status < 400, resp.status, latency_ms, None
        except urllib.error.HTTPError as http_err:
            latency_ms = (time.monotonic() - started) * 1000
            return endpoint, False, http_err.code, latency_ms, None
        except Exception as exc:  # noqa: BLE001
            latency_ms = (time.monotonic() - started) * 1000
            return endpoint, False, None, latency_ms, exc

    async def run_quick_test(self, target: ServiceTestTarget) -> bool:
        """
        Run a quick test for a service (smoke test).

        Args:
            target: Service and endpoints to test

        Returns:
            True if all tests passed, False otherwise
        """
        service, endpoints = target.service, target.endpoints
        self.console.print(f"[cyan]🧪 Quick testing {service} ({len(endpoints)} endpoints)[/cyan]")

        if not endpoints:
            self.console.print(f"[yellow]⚠ No endpoints configured for {service}, skipping quick test[/yellow]")
            return True

        loop = asyncio.get_running_loop()
        results = await asyncio.gather(*(
            loop.run_in_executor(None, self._probe_endpoint, endpoint)
            for endpoint in endpoints
        ))
        passed = True
        for endpoint, ok, status, latency_ms, err in results:
            if ok:
                self.console.print(f"[green]✓ {endpoint} → HTTP {status} ({latency_ms:.0f} ms)[/green]")
                anomaly = self.latency_tracker.record(endpoint, latency_ms)
                if anomaly is not None:
                    self.console.print(
                        f"[yellow]⏱ Latency anomaly: {endpoint} "
                        f"{anomaly.latency_ms:.0f} ms vs baseline "
                        f"{anomaly.baseline_p95_ms:.0f} ms "
                        f"(×{anomaly.ratio:.1f})[/yellow]"
                    )
                    self.planfile_reporter.report_failure(
                        service=service,
                        status="degraded",
                        stage="quick",
                        message=f"Latency regression on {endpoint}: "
                                f"{anomaly.latency_ms:.0f} ms vs baseline "
                                f"{anomaly.baseline_p95_ms:.0f} ms",
                    )
            else:
                detail = f"HTTP {status}" if status else str(err)
                self.console.print(f"[red]✗ {endpoint} → {detail}[/red]")
                passed = False

        if passed:
            self.console.print(f"[green]✓ Quick test passed for {service}[/green]")
        else:
            self.console.print(f"[red]✗ Quick test failed for {service}[/red]")
            self.planfile_reporter.report_failure(
                service=service,
                status="down",
                stage="quick",
                message="Quick HTTP smoke test failed",
            )

        return passed
    
    async def run_detail_test(self, target: ServiceTestTarget) -> Dict:
        """
        Run a detailed test for a service with blame report.

        Args:
            target: Service and endpoints to test

        Returns:
            Dictionary with test results and blame information
        """
        service, endpoints = target.service, target.endpoints
        self.console.print(f"[cyan]🔍 Detail testing {service} ({len(endpoints)} endpoints)[/cyan]")

        results = {
            "service": service,
            "total_endpoints": len(endpoints),
            "passed": 0,
            "failed": 0,
            "failed_endpoint": None,
            "blame": {},
        }

        for endpoint in endpoints:
            try:
                req = urllib.request.Request(endpoint, method="GET")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status >= 400:
                        results["failed"] += 1
                        self.console.print(f"[red]✗ {endpoint} → HTTP {resp.status}[/red]")
                    else:
                        results["passed"] += 1
                        self.console.print(f"[green]✓ {endpoint} → HTTP {resp.status}[/green]")
            except Exception as e:
                results["failed"] += 1
                self.console.print(f"[red]✗ {endpoint} → {e}[/red]")

        if results["failed"] > 0:
            results["failed_endpoint"] = endpoints[0] if endpoints else None
            try:
                blame_result = subprocess.run(
                    ["git", "log", "--oneline", "-5", "--", f"*/{service}/*"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                )
                if blame_result.returncode == 0:
                    lines = blame_result.stdout.strip().split("\n")
                    if lines and lines[0]:
                        results["blame"] = {"recent_commits": lines}
            except Exception:
                pass
            self.console.print(f"[red]✗ Detail test found {results['failed']} regression(s)[/red]")
            self.planfile_reporter.report_failure(
                service=service,
                status="down",
                stage="detail",
                message=json.dumps(results, ensure_ascii=False),
            )
        else:
            self.console.print(f"[green]✓ Detail test passed for {service}[/green]")

        return results
    
    async def test_loop(self):
        """Main test execution loop."""
        while True:
            await self.process_test_queue_once()
            await asyncio.sleep(self.debounce_seconds)
    
    def should_watch_file(self, file_path: str) -> bool:
        """
        Check if a file should be watched based on configured file types.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be watched, False otherwise
        """
        normalized = str(file_path).lower()
        if normalized.endswith(".testql.toon.yaml"):
            return True

        if not self.config.watch.file_types:
            return True
        
        file_suffix = Path(file_path).suffix.lower()
        return file_suffix in self.config.watch.file_types
    
    def _path_matches_exclude_pattern(self, rel_path: Path, pattern: str) -> bool:
        """Return True when *rel_path* matches a watch exclude pattern."""
        path_str = str(rel_path).replace("\\", "/")
        if pattern.startswith("*") and rel_path.suffix == pattern[1:]:
            return True
        if fnmatch.fnmatch(path_str, pattern):
            return True
        if fnmatch.fnmatch(path_str, f"**/{pattern}"):
            return True
        return pattern in path_str

    def _is_file_ignored(self, rel_path: Path) -> bool:
        """Check if a file should be ignored based on paths and types."""
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}
        if any(part in skip_dirs for part in rel_path.parts):
            return True
        if "tests" in rel_path.parts or "test" in rel_path.parts:
            return True

        for pattern in self.config.watch.exclude_patterns:
            if self._path_matches_exclude_pattern(rel_path, pattern):
                return True
        
        if self.config.watch.file_types:
            file_ext = rel_path.suffix if rel_path.suffix else ""
            if not file_ext.startswith("."):
                file_ext = f".{file_ext}"
            if file_ext not in self.config.watch.file_types:
                return True
        
        return False

    def _notify_all_configured_services(self, rel_path: Path):
        """Notify all configured services about a file change."""
        if not self.config.services:
            return
        for svc in self.config.services:
            if self.should_test(svc.name):
                self.changed_services.add(svc.name)
                self._pending_events[svc.name].append(str(rel_path))
                self._pending_event_times[svc.name] = time.time()

    def on_file_change(self, file_path: str):
        """
        Handle file change event.
        
        Args:
            file_path: Path to the changed file
        """
        if not self.should_watch_file(file_path):
            return
        
        rel_path = self._to_relative_path(file_path)
        if self._is_file_ignored(rel_path):
            return
        
        service = self.infer_service(file_path)
        
        service_matches_config = False
        if service and self.config.services:
            for svc in self.config.services:
                if service == svc.name:
                    service_matches_config = True
                    break
        
        if not service or not service_matches_config:
            self._notify_all_configured_services(rel_path)
            return

        burst = self.burst_detector.record(service)
        if burst is not None:
            self.console.print(
                f"[red]⚡ Change burst: {burst.events} events for "
                f"'{service}' in {burst.window_s:.0f}s — runaway generator "
                "or sync loop?[/red]"
            )

        self.changed_services.add(service)
        self._pending_events[service].append(str(rel_path))
        self._pending_event_times[service] = time.time()
    
    def build_watched_paths(self) -> List[str]:
        """
        Build list of paths to watch from config.
        
        Returns:
            List of absolute paths to watch
        """
        if self.config.watch.paths:
            # Use paths from config
            watch_paths = []
            configured_paths = []
            for pattern in self.config.watch.paths:
                # Handle exclusion patterns (starting with !)
                if pattern.startswith("!"):
                    continue
                configured_paths.append(pattern.rstrip("/"))
                # Convert to absolute path
                if "**" in pattern:
                    base_path = pattern.replace("**", "")
                else:
                    base_path = pattern
                
                abs_path = str(self.project_root / base_path)
                if Path(abs_path).exists():
                    watch_paths.append(abs_path)
            if watch_paths:
                return watch_paths

            # Older auto-generated configs always contained app/src/routes.
            # When the supplied root is a workspace and its projects live one
            # level down, all three paths are invalid. Re-detect at runtime so
            # ``wup watch .`` starts successfully without rewriting user config.
            # Preserve the configuration error for deliberate custom paths;
            # silently replacing a misspelled path with an unrelated detected
            # directory would hide the user's mistake.
            if set(configured_paths) != {"app/**", "src/**", "routes/**"}:
                return []

            detected_paths = []
            for pattern in detect_watch_paths(self.project_root):
                base_path = pattern.replace("**", "")
                abs_path = self.project_root / base_path
                if abs_path.exists():
                    detected_paths.append(str(abs_path))
            if detected_paths:
                self.console.print(
                    "[yellow]Configured watch paths do not exist; "
                    "using auto-detected project subfolders.[/yellow]"
                )
                return detected_paths
            return []
        
        # Fallback to default paths
        return [
            str(self.project_root / "app"),
            str(self.project_root / "src"),
            str(self.project_root / "tests"),
        ]
    
    def _create_and_start_observer(self, event_handler, watch_paths):
        """
        Create and start a file system observer, falling back to polling
        if the inotify watch limit is reached.
        """
        observer = Observer()
        for path in watch_paths:
            observer.schedule(event_handler, path, recursive=True)
        try:
            observer.start()
            return observer
        except OSError as exc:
            if exc.errno in (errno.ENOSPC, errno.EMFILE):
                self.console.print(
                    f"[yellow]⚠️  inotify limit reached ({exc.strerror}). "
                    "Falling back to polling observer (higher CPU usage).[/yellow]"
                )
                observer.stop()
                observer = PollingObserver()
                for path in watch_paths:
                    observer.schedule(event_handler, path, recursive=True)
                observer.start()
                return observer
            raise

    def start_background_tasks(self) -> None:
        """
        Hook for subclasses to start background threads before watching begins.

        The base watcher has nothing to start; TestQLWatcher overrides this to
        launch its periodic live-probe thread. Coordinators that run several
        watchers at once (see :class:`~wup.multi.MultiProjectWatcher`) call this
        on each watcher so background probes fire regardless of who owns the
        main loop.
        """

    def prepare_observer(self, watch_paths: Optional[List[str]] = None):
        """
        Set up and start the filesystem observer without entering a blocking loop.

        Splitting this out of :meth:`start_watching` lets a coordinator drive
        several watchers from a single loop (multi-project mode).

        Args:
            watch_paths: List of paths to watch (default: from config or common
                source directories)

        Returns:
            The started observer, or ``None`` when no valid paths could be
            watched (configuration error).
        """
        if watch_paths is None:
            watch_paths = self.build_watched_paths()

        # Filter to existing paths
        watch_paths = [p for p in watch_paths if Path(p).exists()]

        if not watch_paths:
            self.console.print(
                f"[red]No valid paths to watch[/red] "
                f"[dim](project: {self.config.project.name})[/dim]"
            )
            return None

        event_handler = WupEventHandler(self)
        observer = self._create_and_start_observer(event_handler, watch_paths)
        self.console.print(
            f"[green]🕵️  Watching ({self.config.project.name}): "
            f"{', '.join(watch_paths)}[/green]"
        )
        return observer

    def start_watching(self, watch_paths: Optional[List[str]] = None) -> bool:
        """
        Start watching for file changes.

        Args:
            watch_paths: List of paths to watch (default: from config or common source directories)

        Returns:
            False when no valid paths could be watched (configuration error —
            CLI turns this into a non-zero exit so supervisors notice instead
            of treating a watcher that never watched as a clean run),
            True after a graceful interrupt.
        """
        self.start_background_tasks()

        observer = self.prepare_observer(watch_paths)
        if observer is None:
            return False

        try:
            while True:
                self._flush_pending_events()
                asyncio.run(self.process_test_queue_once())
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
        return True
    
    def create_status_table(self) -> Table:
        """
        Create a status table for the dashboard.
        
        Returns:
            Rich Table object with current status
        """
        table = Table(title="🧪 WUP Watcher Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Last Test", style="yellow")
        table.add_column("Endpoints", style="blue")
        
        for service in sorted(self.changed_services):
            last_test = self.last_test_times.get(service, 0)
            if last_test > 0:
                time_ago = int(time.time() - last_test)
                last_test_str = f"{time_ago}s ago"
            else:
                last_test_str = "Never"
            
            endpoints = self.dependency_mapper.get_endpoints_for_service(service)
            table.add_row(
                service,
                "🟡 Testing",
                last_test_str,
                str(len(endpoints))
            )
        
        return table
    
    async def run_with_dashboard(self):
        """Run watcher with live dashboard."""
        self.start_background_tasks()

        watch_paths = self.build_watched_paths()
        watch_paths = [p for p in watch_paths if Path(p).exists()]

        event_handler = WupEventHandler(self)
        observer = self._create_and_start_observer(event_handler, watch_paths)
        
        with Live(self.create_status_table(), refresh_per_second=1) as live:
            try:
                while True:
                    await self.process_test_queue_once()
                    
                    live.update(self.create_status_table())
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
        
        observer.join()


class WupEventHandler(FileSystemEventHandler):
    """File system event handler for WUP watcher."""
    
    def __init__(self, watcher: WupWatcher):
        """
        Initialize the event handler.
        
        Args:
            watcher: WupWatcher instance
        """
        super().__init__()
        self.watcher = watcher
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self.watcher.on_file_change(event.src_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self.watcher.on_file_change(event.src_path)
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            self.watcher.on_file_change(event.src_path)
