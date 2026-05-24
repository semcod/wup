"""Regression: fleet health treats all-pass summaries as success in non-strict mode."""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from subprocess import CompletedProcess

from wup.models.config import ProjectConfig, TestQLConfig, WatchConfig, WupConfig
from wup.testql_watcher import TestQLWatcher


def test_health_summary_all_passed_parser() -> None:
    assert TestQLWatcher._health_summary_all_passed("17/17 passed, 0 failed")
    assert not TestQLWatcher._health_summary_all_passed("16/17 passed, 1 failed")


def test_fleet_health_nonzero_exit_all_passed_counts_as_up() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "fleet.testql.toon.yaml").write_text("name: fleet\n", encoding="utf-8")
        (root / ".wup").mkdir(parents=True, exist_ok=True)

        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
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
            stdout='{"passed": 17, "failed": 0}',
            stderr="",
        )
        assert asyncio.run(watcher._run_fleet_health_scenario()) is True
        state = json.loads((root / ".wup" / "service-health.json").read_text(encoding="utf-8"))
        assert state["demo"]["status"] == "up"
        assert state["demo"]["stage"] == "health_scenario"
