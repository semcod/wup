"""TestQL integration for WUP watcher."""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from urllib import error, request

from .config import load_config
from .core import WupWatcher
from .models.config import WupConfig, ServiceConfig
from .visual_diff import VisualDiffer
from .web_client import WebClient


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

    _UNSET = object()

    def __init__(
        self,
        project_root: str,
        scenarios_dir=_UNSET,
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
        
        # Explicit constructor arg wins; otherwise use config; final fallback default
        if scenarios_dir is not self._UNSET:
            self.scenarios_dir = self.project_root / scenarios_dir
        elif config and config.testql and config.testql.scenario_dir:
            self.scenarios_dir = self.project_root / config.testql.scenario_dir
        else:
            self.scenarios_dir = self.project_root / "testql-scenarios"
        self.testql_bin = testql_bin
        self.testql_extra_args = config.testql.extra_args if config and config.testql else []
        
        self.quick_limit = quick_limit
        self.track_dir = self.project_root / track_dir
        self.track_dir.mkdir(parents=True, exist_ok=True)
        self.browser_notifier = BrowserNotifier(
            service_url=browser_service_url,
            events_file=self.project_root / ".wup" / "browser-events" / "latest.json",
        )
        self.last_track_path: Optional[Path] = None
        self.health_state_path = self.project_root / ".wup" / "service-health.json"
        self.health_events_path = self.project_root / ".wup" / "service-health-events.jsonl"
        self.health_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.service_health = self._load_service_health()
        self.config = config
        self.visual_differ = VisualDiffer(project_root, config.visual_diff) if config and config.visual_diff else None
        self.web_client = WebClient(config.web) if config and getattr(config, "web", None) else WebClient()

    def _load_service_health(self) -> Dict[str, Dict]:
        if not self.health_state_path.exists():
            return {}
        try:
            payload = json.loads(self.health_state_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except (json.JSONDecodeError, OSError):
            return {}
        return {}

    def _save_service_health(self) -> None:
        self.health_state_path.write_text(
            json.dumps(self.service_health, indent=2),
            encoding="utf-8",
        )

    def _record_health_transition(
        self,
        *,
        service: str,
        status: str,
        stage: str,
        message: str = "",
        track_file: Optional[str] = None,
    ) -> None:
        now = int(time.time())
        previous = self.service_health.get(service, {})
        previous_status = previous.get("status", "unknown")

        self.service_health[service] = {
            "status": status,
            "updated_at": now,
            "stage": stage,
            "message": message,
            "track_file": track_file or "",
        }
        self._save_service_health()

        changed = previous_status != status
        if not changed:
            return

        event = {
            "timestamp": now,
            "service": service,
            "status": status,
            "previous_status": previous_status,
            "stage": stage,
            "message": message,
            "track_file": track_file or "",
        }
        with self.health_events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

        self.browser_notifier.notify(
            {
                "type": "wup_service_health_change",
                "service": service,
                "status": status,
                "previous_status": previous_status,
                "stage": stage,
                "message": message,
                "track_file": track_file,
            }
        )

        # Fire-and-forget: forward event to wupbro backend if active
        if self.web_client.is_active:
            try:
                asyncio.ensure_future(
                    self.web_client.send_health_transition(
                        service=service,
                        from_status=previous_status,
                        to_status=status,
                    )
                )
            except RuntimeError:
                # No running event loop — skip silently
                pass

    def _tokenize_service(self, service: str) -> List[str]:
        raw_tokens = re.split(r"[^a-zA-Z0-9]+", service.lower())
        return [token for token in raw_tokens if len(token) >= 3]

    def _get_config_endpoints_for_service(self, service: str) -> List[str]:
        by_service = self.config.testql.endpoints_by_service or {}
        explicit = self.config.testql.explicit_endpoints or []

        service_specific = by_service.get(service, [])
        merged: List[str] = []
        for endpoint in [*service_specific, *explicit]:
            endpoint_url = self._to_full_url(endpoint)
            if endpoint_url not in merged:
                merged.append(endpoint_url)
        return merged

    def _resolve_base_url(self) -> str:
        base_url = (self.config.testql.base_url or "").strip()
        if base_url:
            return base_url.rstrip("/")

        env_key = (self.config.testql.base_url_env or "WUP_BASE_URL").strip()
        env_url = os.getenv(env_key, "").strip()
        if env_url:
            return env_url.rstrip("/")

        return ""

    def _to_full_url(self, endpoint: str) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint

        base_url = self._resolve_base_url()
        if not base_url:
            return endpoint

        if endpoint.startswith("/"):
            return f"{base_url}{endpoint}"
        return f"{base_url}/{endpoint}"

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
    
    def _score_scenario(self, scenario: Path, tokens: List[str]) -> int:
        """Score a scenario by relevance to service tokens."""
        name = scenario.name.lower()
        score = 0
        if any(token in name for token in tokens):
            score += 3
        if "api" in name or "endpoint" in name:
            score += 2
        if "infra" in name or "smoke" in name:
            score += 1
        return score

    def _select_scenarios_for_service(self, service: str) -> List[Path]:
        all_scenarios = self._discover_scenarios()
        if not all_scenarios:
            return []

        tokens = self._tokenize_service(service)
        scored = sorted(
            ((self._score_scenario(s, tokens), s) for s in all_scenarios),
            key=lambda item: (item[0], item[1].name),
            reverse=True,
        )
        selected = [s for score, s in scored if score > 0]
        if selected:
            return selected

        svc_config = self.get_service_config(service)
        limit = (svc_config.quick_tests.max_endpoints
                 if svc_config and svc_config.quick_tests else self.quick_limit)
        return all_scenarios if limit >= len(all_scenarios) else all_scenarios[:limit]

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

    def _quick_timeout(self) -> int:
        """Return timeout for quick tests from config or default."""
        if self.config.test_strategy and self.config.test_strategy.quick:
            return self.config.test_strategy.quick.get("timeout_s", 60)
        return 60

    def _merge_endpoints(self, service: str, endpoints: List[str]) -> List[str]:
        """Merge caller endpoints with config-declared endpoints for the service."""
        merged = list(endpoints)
        for ep in self._get_config_endpoints_for_service(service):
            if ep not in merged:
                merged.append(ep)
        return merged

    async def _run_scenario_quick(
        self, service: str, scenario: Path, merged_endpoints: List[str]
    ) -> bool:
        """Run a single scenario in quick (dry-run) mode. Returns False on failure."""
        args = ["run", str(scenario), "--dry-run", *self.testql_extra_args]
        result = self._run_testql(args, timeout=self._quick_timeout())
        if result.returncode == 0:
            return True

        reason = result.stderr.strip() or result.stdout.strip() or "Quick TestQL failed"
        track_path = self._write_track(service=service, stage="quick",
                                       scenario=scenario, result=result)
        self._record_health_transition(service=service, status="down", stage="quick",
                                       message=reason, track_file=str(track_path))
        if self.web_client.is_active:
            endpoint = merged_endpoints[0] if merged_endpoints else f"/{service}"
            await self.web_client.send_regression(
                service=service, file="", endpoint=endpoint, reason=reason, stage="quick"
            )
        self.console.print(f"[red]✗ Quick failed: {scenario.name} | track: {track_path}[/red]")
        return False

    async def _quick_pass_actions(self, service: str, merged_endpoints: List[str]) -> None:
        """Actions to perform after all quick scenarios pass."""
        self._record_health_transition(service=service, status="up", stage="quick",
                                       message="Quick TestQL passed")
        if self.web_client.is_active:
            await self.web_client.send_pass(service=service, stage="quick")
        self.console.print(f"[green]✓ Quick TestQL passed for {service}[/green]")
        if self.visual_differ and self.visual_differ.cfg.enabled:
            visual_results = await self.visual_differ.run_for_service(service, merged_endpoints)
            await self._publish_visual_events(service, visual_results)

    async def run_quick_test(self, service: str, endpoints: List[str]) -> bool:
        merged_endpoints = self._merge_endpoints(service, endpoints)

        scenarios = self._select_scenarios_for_service(service)
        svc_config = self.get_service_config(service)
        limit = (svc_config.quick_tests.max_endpoints
                 if svc_config and svc_config.quick_tests else self.quick_limit)
        scenarios = scenarios[:limit]

        if not scenarios:
            self.console.print(
                f"[yellow]⚠ No TestQL scenarios found for {service} — running visual diff only[/yellow]"
            )
            if self.visual_differ and self.visual_differ.cfg.enabled:
                visual_results = await self.visual_differ.run_for_service(service, merged_endpoints)
                await self._publish_visual_events(service, visual_results)
            return True

        self.console.print(
            f"[cyan]🧪 Quick TestQL for {service} "
            f"({len(scenarios)} scenarios / {len(merged_endpoints)} endpoints)[/cyan]"
        )

        for scenario in scenarios:
            if not await self._run_scenario_quick(service, scenario, merged_endpoints):
                return False

        await self._quick_pass_actions(service, merged_endpoints)
        return True

    async def _publish_visual_events(self, service: str, visual_results: List[Dict]) -> None:
        """Forward visual diff and page-issue findings to wupbro backend."""
        if not self.web_client.is_active:
            return

        for item in visual_results:
            url = item.get("url", "")
            diff = item.get("diff", {})
            status = diff.get("status")

            if status in {"changed", "issue"}:
                await self.web_client.send_visual_diff(
                    service=service,
                    url=url,
                    diff=diff,
                )

            if status == "issue":
                issues = diff.get("issues", [])
                await self.web_client.send_event(
                    {
                        "type": "ANOMALY",
                        "service": service,
                        "url": url,
                        "status": "fail",
                        "reason": "; ".join(issues) if issues else "visual page issue",
                        "stage": "visual",
                        "diff": diff,
                    }
                )

    async def run_detail_test(self, service: str, endpoints: List[str]) -> Dict:
        merged_endpoints = list(endpoints)
        for configured_endpoint in self._get_config_endpoints_for_service(service):
            if configured_endpoint not in merged_endpoints:
                merged_endpoints.append(configured_endpoint)

        scenarios = self._select_scenarios_for_service(service)
        results = {
            "service": service,
            "total_scenarios": len(scenarios),
            "total_endpoints": len(merged_endpoints),
            "passed": 0,
            "failed": 0,
            "failed_scenarios": [],
            "track_files": [],
        }

        self.console.print(
            f"[cyan]🔍 Detail TestQL for {service} ({len(scenarios)} scenarios / {len(merged_endpoints)} endpoints)[/cyan]"
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
