"""
Core module for WUP (What's Up) - Intelligent file watcher for regression testing.
"""

import asyncio
import json
import subprocess
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .dependency_mapper import DependencyMapper


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
        test_cooldown_seconds: int = 300
    ):
        """
        Initialize the WUP watcher.
        
        Args:
            project_root: Path to the project root directory
            deps_file: Path to the dependency map JSON file
            cpu_throttle: Maximum CPU usage threshold (0.0-1.0)
            debounce_seconds: Debounce time for file changes
            test_cooldown_seconds: Minimum time between tests for same service
        """
        self.project_root = Path(project_root)
        self.deps_file = deps_file
        self.cpu_throttle = cpu_throttle
        self.debounce_seconds = debounce_seconds
        self.test_cooldown_seconds = test_cooldown_seconds
        
        self.dependency_mapper = DependencyMapper(str(self.project_root))
        self.changed_services: Set[str] = set()
        self.test_queue: deque = deque()
        self.last_test_times: Dict[str, float] = defaultdict(float)
        self.console = Console()
        
        # Load or build dependency map
        if Path(deps_file).exists():
            self.dependency_mapper.load(deps_file)
        else:
            self.console.print(f"[yellow]Building dependency map...[/yellow]")
            self.dependency_mapper.build_from_codebase()
            self.dependency_mapper.save(deps_file)

    def _to_relative_path(self, file_path: str) -> Path:
        file_path_obj = Path(file_path)
        try:
            return file_path_obj.relative_to(self.project_root)
        except ValueError:
            return file_path_obj
    
    def infer_service(self, file_path: str) -> Optional[str]:
        """
        Infer service name from file path.
        
        Examples:
            app/users/routes.py → "app/users"
            src/components/auth.ts → "src/components"
        """
        rel_path = self._to_relative_path(file_path)
        parts = rel_path.parts
        
        # Use dependency mapper if available
        service = self.dependency_mapper.get_service_for_file(file_path)
        if service:
            return service
        
        # Fallback: use first two meaningful parts
        if len(parts) >= 2:
            return "/".join(parts[:2])
        
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
        self.test_queue.append(("quick", service, endpoints[:3]))
        self.last_test_times[service] = time.time()
    
    def schedule_detail_test(self, service: str):
        """
        Schedule a detailed test for a service.
        
        Args:
            service: Service name to test
        """
        endpoints = self.dependency_mapper.get_endpoints_for_service(service)
        self.test_queue.appendleft(("detail", service, endpoints))

    async def process_test_queue_once(self):
        if not self.test_queue or not await self.cpu_ok():
            return

        test_type, service, endpoints = self.test_queue.popleft()

        try:
            if test_type == "quick":
                passed = await self.run_quick_test(service, endpoints)
                if not passed:
                    self.schedule_detail_test(service)
            elif test_type == "detail":
                await self.run_detail_test(service, endpoints)
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
    
    async def run_quick_test(self, service: str, endpoints: List[str]) -> bool:
        """
        Run a quick test for a service (smoke test).
        
        Args:
            service: Service name
            endpoints: List of endpoints to test
            
        Returns:
            True if all tests passed, False otherwise
        """
        self.console.print(f"[cyan]🧪 Quick testing {service} ({len(endpoints)} endpoints)[/cyan]")
        
        # This is a placeholder - integrate with TestQL or your test framework
        # For now, simulate a test
        await asyncio.sleep(1)
        
        # Simulate random failure for demo (10% chance)
        import random
        passed = random.random() > 0.1
        
        if passed:
            self.console.print(f"[green]✓ Quick test passed for {service}[/green]")
        else:
            self.console.print(f"[red]✗ Quick test failed for {service}[/red]")
        
        return passed
    
    async def run_detail_test(self, service: str, endpoints: List[str]) -> Dict:
        """
        Run a detailed test for a service with blame report.
        
        Args:
            service: Service name
            endpoints: List of endpoints to test
            
        Returns:
            Dictionary with test results and blame information
        """
        self.console.print(f"[cyan]🔍 Detail testing {service} ({len(endpoints)} endpoints)[/cyan]")
        
        # This is a placeholder - integrate with TestQL or your test framework
        # For now, simulate a test
        await asyncio.sleep(3)
        
        # Simulate results
        results = {
            "service": service,
            "total_endpoints": len(endpoints),
            "passed": len(endpoints) - 1,
            "failed": 1,
            "failed_endpoint": endpoints[0] if endpoints else None,
            "blame": {
                "file": f"app/{service}/routes.py",
                "line": 42,
                "commit": "abc123",
                "author": "developer"
            }
        }
        
        if results["failed"] > 0:
            self.console.print(f"[red]✗ Detail test found {results['failed']} regression(s)[/red]")
            self.console.print(f"[red]  Blame: {results['blame']['file']}:{results['blame']['line']}[/red]")
        else:
            self.console.print(f"[green]✓ Detail test passed for {service}[/green]")
        
        return results
    
    async def test_loop(self):
        """Main test execution loop."""
        while True:
            await self.process_test_queue_once()
            await asyncio.sleep(self.debounce_seconds)
    
    def on_file_change(self, file_path: str):
        """
        Handle file change event.
        
        Args:
            file_path: Path to the changed file
        """
        # Only watch relevant directories
        rel_path = self._to_relative_path(file_path)
        parts = rel_path.parts
        
        # Skip certain directories
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}
        if any(part in skip_dirs for part in parts):
            return
        
        # Infer service from file path
        service = self.infer_service(file_path)
        
        if service and self.should_test(service):
            self.changed_services.add(service)
            self.console.print(f"[yellow]📝 Changed: {rel_path} → Service: {service}[/yellow]")
            self.schedule_quick_test(service)
    
    def start_watching(self, watch_paths: Optional[List[str]] = None):
        """
        Start watching for file changes.
        
        Args:
            watch_paths: List of paths to watch (default: common source directories)
        """
        if watch_paths is None:
            watch_paths = [
                str(self.project_root / "app"),
                str(self.project_root / "src"),
                str(self.project_root / "tests"),
            ]
        
        # Filter to existing paths
        watch_paths = [p for p in watch_paths if Path(p).exists()]
        
        if not watch_paths:
            self.console.print("[red]No valid paths to watch[/red]")
            return
        
        event_handler = WupEventHandler(self)
        observer = Observer()
        
        for path in watch_paths:
            observer.schedule(event_handler, path, recursive=True)
        
        observer.start()
        self.console.print(f"[green]🕵️  Watching: {', '.join(watch_paths)}[/green]")
        
        try:
            while True:
                asyncio.run(self.process_test_queue_once())
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()
    
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
        from watchdog.observers import Observer
        
        watch_paths = [
            str(self.project_root / "app"),
            str(self.project_root / "src"),
            str(self.project_root / "tests"),
        ]
        watch_paths = [p for p in watch_paths if Path(p).exists()]
        
        event_handler = WupEventHandler(self)
        observer = Observer()
        
        for path in watch_paths:
            observer.schedule(event_handler, path, recursive=True)
        
        observer.start()
        
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
