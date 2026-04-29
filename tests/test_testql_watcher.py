import asyncio
import json
import tempfile
from pathlib import Path
from subprocess import CompletedProcess

from wup.testql_watcher import TestQLWatcher
from wup.models.config import WupConfig, ProjectConfig


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
        from wup.models.config import TestQLConfig
        empty_config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[],
            test_strategy=None,
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
