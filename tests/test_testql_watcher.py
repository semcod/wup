import asyncio
import json
import os
import signal
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import Mock

import pytest

from wup.testql_watcher import TestQLWatcher
from wup.models.config import (
    PlanfileConfig,
    ProjectConfig,
    ServiceConfig,
    TestStrategyConfig,
    TestQLConfig,
    VisualDiffConfig,
    WatchConfig,
    WupConfig,
)
from wup.planfile_reporter import PlanfileReporter


def test_process_changed_file_creates_track_on_failure():
    """Test that _write_track creates track files correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        failing_scenario = scenario_dir / "api-users-smoke.testql.toon.yaml"
        failing_scenario.write_text("name: failing\n", encoding="utf-8")

        # Pass config with service to prevent loading from temp dir
        from wup.models.config import TestQLConfig, WatchConfig, ServiceConfig
        service_config = ServiceConfig(name="app/users", paths=["app/users"])
        empty_config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            test_strategy=None,
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios")
        )
        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=empty_config,
        )

        # Test _write_track directly
        result = CompletedProcess(
            args=["testql", "run", str(failing_scenario)],
            returncode=1,
            stdout="",
            stderr="intentional failure"
        )

        track_path = watcher._write_track(
            service="app/users",
            stage="quick",
            scenario=failing_scenario,
            result=result
        )

        assert track_path.exists()
        track_payload = json.loads(track_path.read_text(encoding="utf-8"))
        assert track_payload["service"] == "app/users"
        assert track_payload["stage"] == "quick"
        assert "intentional failure" in track_payload["stderr_head"]


def test_browser_event_file_is_written_without_service_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        scenario_file = scenario_dir / "api-users-smoke.testql.toon.yaml"
        scenario_file.write_text("name: smoke\n", encoding="utf-8")

        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
        )

        result = CompletedProcess(args=["testql", "run"], returncode=1, stdout="", stderr="boom")
        track_path = watcher._write_track(
            service="app/users",
            stage="quick",
            scenario=scenario_file,
            result=result,
        )

        assert track_path.exists()
        event_file = root / ".wup" / "browser-events" / "latest.json"
        assert event_file.exists()
        event_payload = json.loads(event_file.read_text(encoding="utf-8"))
        assert event_payload["type"] == "wup_testql_error"
        assert event_payload["service"] == "app/users"


def test_config_endpoints_use_base_url_from_yaml_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="connect-config", paths=["connect-config/**"])],
            testql=TestQLConfig(
                base_url="http://localhost:8100",
                explicit_endpoints=["/connect-config"],
                endpoints_by_service={"connect-config": ["/connect-config-sitemap"]},
            ),
        )

        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )

        endpoints = watcher._get_config_endpoints_for_service("connect-config")
        assert "http://localhost:8100/connect-config" in endpoints
        assert "http://localhost:8100/connect-config-sitemap" in endpoints


def test_config_endpoints_use_base_url_from_env_when_yaml_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="connect-data", paths=["connect-data/**"])],
            testql=TestQLConfig(
                base_url="",
                base_url_env="WUP_BASE_URL",
                explicit_endpoints=["/connect-data"],
            ),
        )

        old_value = os.environ.get("WUP_BASE_URL")
        os.environ["WUP_BASE_URL"] = "http://localhost:8100"
        try:
            watcher = TestQLWatcher(
                project_root=str(root),
                deps_file=str(root / "deps.json"),
                scenarios_dir="testql-scenarios",
                track_dir=".wup/tracks",
                config=cfg,
            )

            endpoints = watcher._get_config_endpoints_for_service("connect-data")
            assert "http://localhost:8100/connect-data" in endpoints
        finally:
            if old_value is None:
                os.environ.pop("WUP_BASE_URL", None)
            else:
                os.environ["WUP_BASE_URL"] = old_value


def test_service_health_transitions_are_persisted():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        scenario_file = scenario_dir / "connect-config-smoke.testql.toon.yaml"
        scenario_file.write_text("name: smoke\n", encoding="utf-8")

        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
        )

        # 1) First quick run fails -> service goes down
        def failing_run(args, timeout):
            return CompletedProcess(args=args, returncode=1, stdout="", stderr="down")

        watcher._run_testql = failing_run  # type: ignore[method-assign]
        failed = asyncio.run(watcher.run_quick_test("connect-config", []))
        assert failed is False

        health_state_path = root / ".wup" / "service-health.json"
        health_events_path = root / ".wup" / "service-health-events.jsonl"
        assert health_state_path.exists()
        assert health_events_path.exists()

        state = json.loads(health_state_path.read_text(encoding="utf-8"))
        assert state["connect-config"]["status"] == "down"

        # 2) Next quick run succeeds -> service goes up
        def passing_run(args, timeout):
            return CompletedProcess(args=args, returncode=0, stdout="ok", stderr="")

        watcher._run_testql = passing_run  # type: ignore[method-assign]
        passed = asyncio.run(watcher.run_quick_test("connect-config", []))
        assert passed is True

        state = json.loads(health_state_path.read_text(encoding="utf-8"))
        assert state["connect-config"]["status"] == "up"

        events = []
        with health_events_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                events.append(json.loads(line))

        statuses = [event["data"].get("status") for event in events if event.get("type") == "ServiceHealthChanged" and event.get("data", {}).get("service") == "connect-config"]
        assert "down" in statuses
        assert "up" in statuses


def test_planfile_reporter_creates_deduped_ticket(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return CompletedProcess(cmd, returncode=0, stdout="Created PLF-999\n", stderr="")

        monkeypatch.setattr("wup.planfile_reporter.subprocess.run", fake_run)
        reporter = PlanfileReporter(
            root,
            PlanfileConfig(enabled=True, labels=["koru", "llm-ready", "wup"]),
        )

        first = reporter.report_failure(
            service="frontend",
            status="down",
            stage="quick",
            message="broken page",
            track_file=".wup/tracks/one.json",
        )
        second = reporter.report_failure(
            service="frontend",
            status="down",
            stage="quick",
            message="broken page",
            track_file=".wup/tracks/one.json",
        )

        assert first == "PLF-999"
        assert second == "PLF-999"
        # Recurrence check may `ticket show` the deduped id, but only ONE
        # ticket may ever be created for the same open fingerprint.
        create_calls = [c for c in calls if c[:3] == ["planfile", "ticket", "create"]]
        assert len(create_calls) == 1
        assert calls[0][:3] == ["planfile", "ticket", "create"]
        assert "--label" in calls[0]
        assert "llm-ready" in calls[0]
        assert "--files" in calls[0]
        assert ".wup/tracks/one.json" in calls[0]


def test_planfile_reporter_clears_dedupe_after_recovery(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            ticket_id = f"PLF-{999 + len(calls)}"
            return CompletedProcess(cmd, returncode=0, stdout=f"Created {ticket_id}\n", stderr="")

        monkeypatch.setattr("wup.planfile_reporter.subprocess.run", fake_run)
        reporter = PlanfileReporter(root, PlanfileConfig(enabled=True))

        first = reporter.report_failure(
            service="frontend",
            status="down",
            stage="quick",
            message="broken page",
        )
        reporter.clear_service_stage(service="frontend", stage="quick")
        second = reporter.report_failure(
            service="frontend",
            status="down",
            stage="quick",
            message="broken page",
        )

        assert first == "PLF-1000"
        assert second == "PLF-1001"


def test_planfile_reporter_retries_without_files_for_old_planfile_cli(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            if "--files" in cmd:
                return CompletedProcess(cmd, returncode=2, stdout="", stderr="Error: No such option: --files")
            return CompletedProcess(cmd, returncode=0, stdout="Created PLF-998\n", stderr="")

        monkeypatch.setattr("wup.planfile_reporter.subprocess.run", fake_run)
        reporter = PlanfileReporter(root, PlanfileConfig(enabled=True))

        ticket_id = reporter.report_failure(
            service="firmware",
            status="failed",
            stage="detail",
            message="detail failed",
            track_file=".wup/tracks/firmware_detail.json",
        )

        assert ticket_id == "PLF-998"
        assert len(calls) == 2
        assert "--files" in calls[0]
        assert "--files" not in calls[1]
        assert len(calls) == 2


def test_health_transition_creates_planfile_ticket(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="frontend", paths=["frontend/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(),
            planfile=PlanfileConfig(enabled=True),
        )
        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )
        report_failure = Mock(return_value="PLF-100")
        watcher.planfile_reporter.report_failure = report_failure

        watcher._record_health_transition(
            service="frontend",
            status="down",
            stage="visual",
            message="error_container_detected:.error-container",
            track_file=".wup/visual-diffs/frontend.jsonl",
        )

        report_failure.assert_called_once_with(
            service="frontend",
            status="down",
            stage="visual",
            message="error_container_detected:.error-container",
            track_file=".wup/visual-diffs/frontend.jsonl",
        )


def test_normalize_fleet_health_entry_down_to_degraded():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        health_path = root / ".wup" / "service-health.json"
        health_path.parent.mkdir(parents=True)
        health_path.write_text(
            json.dumps(
                {
                    "demo": {
                        "status": "down",
                        "stage": "health_scenario",
                        "message": "partial",
                    }
                }
            ),
            encoding="utf-8",
        )
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="frontend", paths=["frontend/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(health_scenario_strict=False),
        )
        TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )
        state = json.loads(health_path.read_text(encoding="utf-8"))
        assert state["demo"]["status"] == "degraded"


def test_fleet_health_scenario_non_strict_records_degraded_not_down():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "fleet.testql.toon.yaml").write_text("name: fleet\n", encoding="utf-8")

        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="frontend", paths=["frontend/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(
                scenario_dir="testql-scenarios",
                health_scenario="fleet.testql.toon.yaml",
                health_scenario_strict=False,
            ),
        )
        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )
        watcher._run_testql = lambda args, timeout: CompletedProcess(  # type: ignore[method-assign]
            args=args,
            returncode=1,
            stdout='{"passed": 1, "failed": 1, "errors": ["L1: bad"]}',
            stderr="",
        )
        assert asyncio.run(watcher._run_fleet_health_scenario()) is True
        state = json.loads((root / ".wup" / "service-health.json").read_text(encoding="utf-8"))
        assert state["demo"]["status"] == "degraded"
        assert state["demo"]["stage"] == "health_scenario"


def test_visual_differ_disabled_by_default():
    """visual_differ exists but is disabled (no-op) when visual_diff.enabled=False."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
            visual_diff=VisualDiffConfig(enabled=False),
        )

        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )

        # Differ is created but flagged disabled — run_for_service() must be a no-op
        assert watcher.visual_differ is not None
        assert watcher.visual_differ.cfg.enabled is False
        from wup.models.target import ServiceTestTarget

        results = asyncio.run(
            watcher.visual_differ.run_for_service(
                ServiceTestTarget(service="svc", endpoints=["/x"])
            )
        )
        assert results == []


def test_visual_differ_initialized_when_enabled():
    """When visual_diff.enabled=True, TestQLWatcher.visual_differ is a VisualDiffer."""
    from wup.visual_diff import VisualDiffer

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
            visual_diff=VisualDiffConfig(
                enabled=True,
                base_url="http://localhost:9000",
                pages=["/dashboard"],
            ),
        )

        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )

        assert isinstance(watcher.visual_differ, VisualDiffer)
        assert watcher.visual_differ.cfg.enabled is True
        assert watcher.visual_differ.base_url == "http://localhost:9000"


def test_get_config_endpoints_for_service_keeps_connect_pages_on_frontend():
    """Frontend page routes from explicit_endpoints must not be rebound to backend/api_base_url."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = WupConfig(
            project=ProjectConfig(name="c2004"),
            watch=WatchConfig(),
            services=[
                ServiceConfig(name="frontend", type="web", paths=["frontend/**"]),
                ServiceConfig(name="backend", type="web", paths=["backend/**"]),
            ],
            test_strategy=TestStrategyConfig(),
            testql=TestQLConfig(
                base_url="http://localhost:8100",
                api_base_url="http://localhost:8101",
                explicit_endpoints=["/connect-config-sitemap", "/connect-data"],
            ),
            visual_diff=VisualDiffConfig(enabled=True),
        )

        watcher = TestQLWatcher(tmpdir, config=config)

        frontend_endpoints = watcher._get_config_endpoints_for_service("frontend")
        backend_endpoints = watcher._get_config_endpoints_for_service("backend")

        assert "http://localhost:8100/connect-config-sitemap" in frontend_endpoints
        assert "http://localhost:8100/connect-data" in frontend_endpoints
        assert "http://localhost:8101/connect-config-sitemap" not in backend_endpoints
        assert "http://localhost:8101/connect-data" not in backend_endpoints


def test_quick_pass_actions_prefer_config_endpoints_for_visual_diff():
    """Visual diff should prefer config endpoints over merged mapper endpoints."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = WupConfig(
            project=ProjectConfig(name="c2004"),
            watch=WatchConfig(),
            services=[
                ServiceConfig(name="frontend", type="web", paths=["frontend/**"]),
                ServiceConfig(name="backend", type="web", paths=["backend/**"]),
            ],
            test_strategy=TestStrategyConfig(),
            testql=TestQLConfig(
                base_url="http://localhost:8100",
                api_base_url="http://localhost:8101",
                endpoints_by_service={"backend": ["http://localhost:8101/api/v3/health"]},
                explicit_endpoints=["/connect-config-sitemap", "/connect-data"],
            ),
            visual_diff=VisualDiffConfig(enabled=True),
        )

        watcher = TestQLWatcher(tmpdir, config=config)

        class RecordingDiffer:
            def __init__(self):
                self.cfg = VisualDiffConfig(enabled=True)
                self.calls = []

            async def run_for_service(self, target):
                self.calls.append((target.service, list(target.endpoints)))
                return []

        differ = RecordingDiffer()
        watcher.visual_differ = differ

        asyncio.run(
            watcher._quick_pass_actions(
                "backend",
                [
                    "http://localhost:8101/connect-config-sitemap",
                    "http://localhost:8101/connect-data",
                ],
            )
        )

        assert differ.calls == [("backend", ["http://localhost:8101/api/v3/health"])]


def test_quick_interrupt_does_not_create_failure_track():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "connect-config-smoke.testql.toon.yaml").write_text("name: smoke\n", encoding="utf-8")

        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="connect-config", paths=["connect-config/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=cfg,
        )

        watcher._run_testql = lambda args, timeout: CompletedProcess(  # type: ignore[method-assign]
            args=args,
            returncode=-signal.SIGINT,
            stdout="",
            stderr="",
        )

        with pytest.raises(KeyboardInterrupt):
            asyncio.run(watcher.run_quick_test("connect-config", []))

        tracks = list((root / ".wup" / "tracks").glob("*.json"))
        assert tracks == []
