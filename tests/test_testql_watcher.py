import asyncio
import json
import os
import tempfile
from pathlib import Path
from subprocess import CompletedProcess

from wup.testql_watcher import TestQLWatcher
from wup.models.config import WupConfig, ProjectConfig, TestQLConfig


def test_process_changed_file_creates_track_on_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        app_file = root / "app" / "users" / "routes.py"
        app_file.parent.mkdir(parents=True, exist_ok=True)
        app_file.write_text("print('x')\n", encoding="utf-8")

        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        failing_scenario = scenario_dir / "app-users.testql.toon.yaml"
        failing_scenario.write_text("name: failing\n", encoding="utf-8")

        # Pass empty config to prevent loading from temp dir
        from wup.models.config import TestQLConfig, WatchConfig
        empty_config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[],
            test_strategy=None,
            watch=WatchConfig(),  # Add watch config to avoid file filtering issues
            testql=TestQLConfig(scenario_dir="testql-scenarios")
        )
        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            track_dir=".wup/tracks",
            config=empty_config,
        )

        watcher.dependency_mapper.service_to_endpoints["app/users"] = ["/api/v1/users"]

        def fake_run_testql(args, timeout):
            if "--dry-run" in args:
                return CompletedProcess(args=args, returncode=1, stdout="", stderr="intentional failure")
            return CompletedProcess(args=args, returncode=0, stdout="{}", stderr="")

        watcher._run_testql = fake_run_testql  # type: ignore[method-assign]

        result = asyncio.run(watcher.process_changed_file_once(str(app_file)))

        assert result["processed_items"] >= 1
        assert result["last_track_path"] is not None

        track_path = Path(result["last_track_path"])
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

        statuses = [event.get("status") for event in events if event.get("service") == "connect-config"]
        assert "down" in statuses
        assert "up" in statuses
