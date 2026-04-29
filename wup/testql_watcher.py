"""TestQL integration for WUP watcher."""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from urllib import error, request

from .config import load_config
from .core import WupWatcher
from .models.config import WupConfig, ServiceConfig


class BrowserNotifier:
    """Send watcher events to browser-facing service and local file."""

    def __init__(self, service_url: Optional[str], events_file: Path):
        self.service_url = service_url
        self.events_file = events_file
        self.events_file.parent.mkdir(parents=True, exist_ok=True)

    def notify(self, payload: Dict) -> None:
        payload_with_ts = {"timestamp": int(time.time()), **payload}
        self.events_file.write_text(json.dumps(payload_with_ts, indent=2), encoding="utf-8")

        if not self.service_url:
            return

        body = json.dumps(payload_with_ts).encode("utf-8")
        req = request.Request(
            self.service_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=5):
                return
        except (error.URLError, TimeoutError):
            return


class TestQLWatcher(WupWatcher):
    """WUP watcher running selective TestQL scenarios for changed services."""

    __test__ = False

    def __init__(
        self,
        project_root: str,
        scenarios_dir: str = "testql-scenarios",
        testql_bin: str = "testql",
        track_dir: str = ".wup/tracks",
        browser_service_url: Optional[str] = None,
        quick_limit: int = 3,
        config: Optional[WupConfig] = None,
        **kwargs,
    ):
        # Load config if not provided
        if config is None:
            config = load_config(Path(project_root))
        
        # Pass config to parent class
        super().__init__(project_root=project_root, config=config, **kwargs)
        
        # Use config values if available, otherwise use parameters
        if config.testql:
            self.scenarios_dir = self.project_root / config.testql.scenario_dir
            self.testql_bin = testql_bin  # CLI parameter takes precedence
            # Use extra_args from config if needed
            self.testql_extra_args = config.testql.extra_args
        else:
            self.scenarios_dir = self.project_root / scenarios_dir
            self.testql_bin = testql_bin
            self.testql_extra_args = []
        
        self.quick_limit = quick_limit
        self.track_dir = self.project_root / track_dir
        self.track_dir.mkdir(parents=True, exist_ok=True)
        self.browser_notifier = BrowserNotifier(
            service_url=browser_service_url,
            events_file=self.project_root / ".wup" / "browser-events" / "latest.json",
        )
        self.last_track_path: Optional[Path] = None
        self.config = config

    def _tokenize_service(self, service: str) -> List[str]:
        raw_tokens = re.split(r"[^a-zA-Z0-9]+", service.lower())
        return [token for token in raw_tokens if len(token) >= 3]

    def _discover_scenarios(self) -> List[Path]:
        if not self.scenarios_dir.exists():
            return []
        return sorted(self.scenarios_dir.rglob("*.testql.toon.yaml"))

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
    
    def _select_scenarios_for_service(self, service: str) -> List[Path]:
        all_scenarios = self._discover_scenarios()
        if not all_scenarios:
            return []

        tokens = self._tokenize_service(service)
        scored: List[tuple[int, Path]] = []

        for scenario in all_scenarios:
            name = scenario.name.lower()
            score = 0
            if any(token in name for token in tokens):
                score += 3
            if "api" in name or "endpoint" in name:
                score += 2
            if "infra" in name or "smoke" in name:
                score += 1
            scored.append((score, scenario))

        scored.sort(key=lambda item: (item[0], item[1].name), reverse=True)
        selected = [scenario for score, scenario in scored if score > 0]

        if selected:
            return selected

        # Fallback: return all scenarios up to limit if no matches found
        # Use service config for quick_limit if available
        svc_config = self.get_service_config(service)
        limit = self.quick_limit
        if svc_config and svc_config.quick_tests:
            limit = svc_config.quick_tests.max_endpoints
        
        # Return all scenarios if limit is larger than available scenarios
        if limit >= len(all_scenarios):
            return all_scenarios
        
        return all_scenarios[: limit]

    def _run_testql(self, args: Sequence[str], timeout: int) -> subprocess.CompletedProcess:
        cmd = [self.testql_bin, *args]
        try:
            return subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            fallback_cmd = ["python3", "-m", "testql.cli", *args]
            return subprocess.run(
                fallback_cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )

    def _write_track(self, *, service: str, stage: str, scenario: Optional[Path], result: subprocess.CompletedProcess) -> Path:
        ts = int(time.time())
        safe_service = service.replace("/", "_").replace("\\", "_")
        scenario_name = scenario.name if scenario else "unknown"
        stderr_line = (result.stderr or "").strip().splitlines()[:1]
        stdout_line = (result.stdout or "").strip().splitlines()[:1]

        payload = {
            "service": service,
            "stage": stage,
            "scenario": str(scenario) if scenario else None,
            "command": result.args,
            "returncode": result.returncode,
            "stderr_head": stderr_line[0] if stderr_line else "",
            "stdout_head": stdout_line[0] if stdout_line else "",
            "track": {
                "file": str(scenario) if scenario else "",
                "line": 1,
                "hint": scenario_name,
            },
        }

        track_path = self.track_dir / f"{ts}_{safe_service}_{stage}.json"
        track_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.last_track_path = track_path

        self.browser_notifier.notify(
            {
                "type": "wup_testql_error",
                "service": service,
                "stage": stage,
                "track_file": str(track_path),
                "scenario": str(scenario) if scenario else None,
                "message": payload["stderr_head"] or payload["stdout_head"] or "TestQL command failed",
            }
        )
        return track_path

    async def run_quick_test(self, service: str, endpoints: List[str]) -> bool:
        scenarios = self._select_scenarios_for_service(service)
        
        # Apply service-specific quick limit
        svc_config = self.get_service_config(service)
        if svc_config and svc_config.quick_tests:
            scenarios = scenarios[: svc_config.quick_tests.max_endpoints]
        else:
            scenarios = scenarios[: self.quick_limit]
        
        if not scenarios:
            self.console.print(f"[yellow]⚠ No TestQL scenarios found for {service}[/yellow]")
            return True

        self.console.print(
            f"[cyan]🧪 Quick TestQL for {service} ({len(scenarios)} scenarios / {len(endpoints)} endpoints)[/cyan]"
        )

        for scenario in scenarios:
            # Build args from config if available
            args = ["run", str(scenario), "--dry-run"]
            if self.testql_extra_args:
                args.extend(self.testql_extra_args)
            
            # Use timeout from config if available
            timeout = 60
            if self.config.test_strategy and self.config.test_strategy.quick:
                timeout = self.config.test_strategy.quick.get("timeout_s", 60)
            
            result = self._run_testql(args, timeout=timeout)
            if result.returncode != 0:
                track_path = self._write_track(
                    service=service,
                    stage="quick",
                    scenario=scenario,
                    result=result,
                )
                self.console.print(
                    f"[red]✗ Quick failed: {scenario.name} | track: {track_path}[/red]"
                )
                return False

        self.console.print(f"[green]✓ Quick TestQL passed for {service}[/green]")
        return True

    async def run_detail_test(self, service: str, endpoints: List[str]) -> Dict:
        scenarios = self._select_scenarios_for_service(service)
        results = {
            "service": service,
            "total_scenarios": len(scenarios),
            "passed": 0,
            "failed": 0,
            "failed_scenarios": [],
            "track_files": [],
        }

        self.console.print(
            f"[cyan]🔍 Detail TestQL for {service} ({len(scenarios)} scenarios / {len(endpoints)} endpoints)[/cyan]"
        )

        for scenario in scenarios:
            # Build args from config if available
            args = ["run", str(scenario), "--output", "json"]
            if self.testql_extra_args:
                args.extend(self.testql_extra_args)
            
            # Use timeout from config if available
            timeout = 180
            if self.config.test_strategy and self.config.test_strategy.detail:
                timeout = self.config.test_strategy.detail.get("timeout_s", 180)
            
            result = self._run_testql(args, timeout=timeout)
            if result.returncode == 0:
                results["passed"] += 1
                continue

            results["failed"] += 1
            results["failed_scenarios"].append(str(scenario))
            track_path = self._write_track(
                service=service,
                stage="detail",
                scenario=scenario,
                result=result,
            )
            results["track_files"].append(str(track_path))
            self.console.print(
                f"[red]✗ Detail failed: {scenario.name} | track: {track_path}[/red]"
            )

        if results["failed"] == 0:
            self.console.print(
                f"[green]✓ Detail TestQL passed for {service} ({results['passed']} scenarios)[/green]"
            )

        return results

    async def process_changed_file_once(self, file_path: str) -> Dict:
        self.on_file_change(file_path)

        processed = 0
        while self.test_queue and processed < 4:
            await self.process_test_queue_once()
            processed += 1
            await asyncio.sleep(0)

        return {
            "file": file_path,
            "processed_items": processed,
            "remaining_queue": len(self.test_queue),
            "last_track_path": str(self.last_track_path) if self.last_track_path else None,
        }
