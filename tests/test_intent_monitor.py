"""Tests for continuous todo2code Intent-vs-Reality monitoring."""

from __future__ import annotations

import json
import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

from wup.config import load_config, save_config
from wup.intent_monitor import IntentAuditResult, Todo2CodeIntentMonitor
from wup.models.config import IntentMonitoringConfig, ProjectConfig, WupConfig
from wup.testql_watcher import TestQLWatcher


def _diagnostics(tmp_path: Path, items: list[dict]) -> Path:
    path = tmp_path / "diagnostics.json"
    path.write_text(json.dumps({"diagnostics": items}), encoding="utf-8")
    return path


def test_config_round_trip_preserves_intent_monitoring(tmp_path: Path) -> None:
    config = WupConfig(
        project=ProjectConfig(name="demo"),
        intent_monitoring=IntentMonitoringConfig(
            enabled=True,
            runner="python",
            cli_path="/opt/todo2code/dist/src/cli.js",
            interval_s=120,
            mode="require-llm",
            docs_llm=True,
            fail_codes=["PLANNED_NOT_IMPLEMENTED"],
        ),
    )
    save_config(config, tmp_path / "wup.yaml")

    loaded = load_config(tmp_path)

    assert loaded.intent_monitoring.enabled is True
    assert loaded.intent_monitoring.runner == "python"
    assert loaded.intent_monitoring.interval_s == 120
    assert loaded.intent_monitoring.mode == "require-llm"
    assert loaded.intent_monitoring.docs_llm is True
    assert loaded.intent_monitoring.fail_codes == ["PLANNED_NOT_IMPLEMENTED"]


def test_cli_monitor_maps_blocking_diagnostics_to_down(tmp_path: Path, monkeypatch) -> None:
    path = _diagnostics(
        tmp_path,
        [{"severity": "blocking", "code": "PLANNED_NOT_IMPLEMENTED"}],
    )
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        payload = {"diagnosticsPath": str(path), "runDirectory": str(tmp_path / "run")}
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr("wup.intent_monitor.subprocess.run", fake_run)
    results = []
    config = IntentMonitoringConfig(
        enabled=True,
        command=["node", "/opt/todo2code/cli.js"],
        mode="deterministic",
    )
    monitor = Todo2CodeIntentMonitor(tmp_path, config, results.append)

    result = monitor.run_once()

    assert result.status == "down"
    assert len(result.diagnostics) == 1
    assert results == [result]
    command, kwargs = calls[0]
    assert command[:3] == ["node", "/opt/todo2code/cli.js", "pipeline"]
    assert "--no-docs-llm" in command
    assert "--no-summary-llm" in command
    assert kwargs.get("shell", False) is False


def test_cli_monitor_resolves_single_javascript_launcher(tmp_path: Path, monkeypatch) -> None:
    path = _diagnostics(tmp_path, [])
    cli_path = tmp_path / "cli.js"
    cli_path.write_text("", encoding="utf-8")
    observed = {}

    monkeypatch.setattr("wup.intent_monitor.shutil.which", lambda command: str(cli_path))

    def fake_run(command, **kwargs):
        observed["command"] = command
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"diagnosticsPath": str(path)}),
            stderr="",
        )

    monkeypatch.setattr("wup.intent_monitor.subprocess.run", fake_run)
    monitor = Todo2CodeIntentMonitor(
        tmp_path,
        IntentMonitoringConfig(enabled=True, command=["t2c"]),
        lambda result: None,
    )

    result = monitor.run_once()

    assert result.status == "up"
    assert observed["command"][:2] == ["node", str(cli_path.resolve())]


def test_cli_monitor_passes_project_dotenv_without_global_leakage(
    tmp_path: Path, monkeypatch
) -> None:
    path = _diagnostics(tmp_path, [])
    (tmp_path / ".wup.env").write_text(
        "T2C_ENV_FILE=/secure/todo2code.env\n"
        "OPENROUTER_MODEL=mistralai/codestral-2508\n",
        encoding="utf-8",
    )
    observed = {}

    def fake_run(command, **kwargs):
        observed["env"] = kwargs["env"]
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"diagnosticsPath": str(path)}),
            stderr="",
        )

    monkeypatch.delenv("T2C_ENV_FILE", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    monkeypatch.setattr("wup.intent_monitor.subprocess.run", fake_run)
    monitor = Todo2CodeIntentMonitor(
        tmp_path,
        IntentMonitoringConfig(enabled=True, command=["t2c"]),
        lambda result: None,
    )

    result = monitor.run_once()

    assert result.status == "up"
    assert observed["env"]["T2C_ENV_FILE"] == "/secure/todo2code.env"
    assert observed["env"]["OPENROUTER_MODEL"] == "mistralai/codestral-2508"
    assert "T2C_ENV_FILE" not in os.environ
    assert "OPENROUTER_MODEL" not in os.environ


def test_cli_monitor_process_environment_overrides_project_dotenv(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / ".wup.env").write_text(
        "OPENROUTER_MODEL=mistralai/codestral-2508\n", encoding="utf-8"
    )
    monkeypatch.setenv("OPENROUTER_MODEL", "process/model")
    monitor = Todo2CodeIntentMonitor(
        tmp_path, IntentMonitoringConfig(enabled=True), lambda result: None
    )

    environment = monitor._subprocess_environment()

    assert environment["OPENROUTER_MODEL"] == "process/model"


def test_monitor_filters_codes_and_maps_review_required_to_degraded(tmp_path: Path) -> None:
    path = _diagnostics(
        tmp_path,
        [
            {"severity": "review_required", "code": "CHANGELOG_WITHOUT_IMPLEMENTATION"},
            {"severity": "blocking", "code": "UNRELATED"},
        ],
    )
    config = IntentMonitoringConfig(
        fail_codes=["CHANGELOG_WITHOUT_IMPLEMENTATION"]
    )
    monitor = Todo2CodeIntentMonitor(tmp_path, config, lambda result: None)

    result = monitor._result_from_payload({"diagnosticsPath": str(path)})

    assert result.status == "degraded"
    assert [item["code"] for item in result.diagnostics] == [
        "CHANGELOG_WITHOUT_IMPLEMENTATION"
    ]


def test_monitor_reports_runner_failure_as_down(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "wup.intent_monitor.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2, stdout="", stderr="structured output invalid"
        ),
    )
    results = []
    monitor = Todo2CodeIntentMonitor(
        tmp_path, IntentMonitoringConfig(enabled=True), results.append
    )

    result = monitor.run_once()

    assert result.status == "down"
    assert "structured output invalid" in result.message
    assert results == [result]


def test_python_runner_uses_todo2code_sdk_bridge(tmp_path: Path, monkeypatch) -> None:
    path = _diagnostics(tmp_path, [])
    observed = {}

    class FakeRuntime:
        def __init__(self, root, **kwargs):
            observed["root"] = root
            observed["init"] = kwargs

        def invoke(self, arguments):
            observed["arguments"] = arguments
            payload = {"diagnosticsPath": str(path), "runDirectory": "python-run"}
            return SimpleNamespace(stdout=json.dumps(payload))

    module = types.ModuleType("todo2code")
    module.TypeScriptRuntime = FakeRuntime
    monkeypatch.setitem(sys.modules, "todo2code", module)
    config = IntentMonitoringConfig(
        enabled=True,
        runner="python",
        cli_path="/opt/todo2code/dist/src/cli.js",
        mode="prefer-llm",
        docs_llm=True,
    )
    monitor = Todo2CodeIntentMonitor(tmp_path, config, lambda result: None)

    result = monitor.run_once()

    assert result.status == "up"
    assert observed["root"] == tmp_path.resolve()
    assert observed["init"]["cli_path"] == config.cli_path
    assert observed["arguments"][:2] == ["pipeline", str(tmp_path.resolve())]
    assert observed["arguments"][observed["arguments"].index("--markdown-mode") + 1] == "prefer-llm"
    assert "--no-docs-llm" not in observed["arguments"]
    assert "--no-communication" in observed["arguments"]


def test_testql_watcher_projects_intent_result_as_project_health() -> None:
    watcher = object.__new__(TestQLWatcher)
    watcher.config = SimpleNamespace(project=SimpleNamespace(name="workspace"))
    transitions = []
    watcher._record_health_transition = lambda **values: transitions.append(values)
    result = IntentAuditResult(
        status="down",
        message="todo2code found 3 intent issue(s), 1 blocking",
        diagnostics_path="/tmp/diagnostics.json",
    )

    watcher._record_intent_audit(result)

    assert transitions == [
        {
            "service": "workspace:intent",
            "status": "down",
            "stage": "intent",
            "message": result.message,
            "track_file": result.diagnostics_path,
        }
    ]
