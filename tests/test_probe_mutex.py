"""Regression: periodic probes do not overlap file-change quick/visual cycles."""

from __future__ import annotations

import io
import threading
from unittest.mock import patch

from rich.console import Console

from wup.models.config import ProjectConfig, ServiceConfig, WupConfig
from wup.testql_watcher import TestQLWatcher


def _minimal_watcher() -> TestQLWatcher:
    watcher = TestQLWatcher.__new__(TestQLWatcher)
    watcher.console = Console(file=io.StringIO(), width=120)
    watcher.config = WupConfig(
        project=ProjectConfig(name="t"),
        services=[ServiceConfig(name="frontend", paths=["frontend"])],
    )
    watcher._watch_work_lock = threading.Lock()
    watcher._periodic_probe_in_progress = False
    return watcher


def test_periodic_probe_skipped_when_watch_lock_held() -> None:
    watcher = _minimal_watcher()
    watcher._watch_work_lock.acquire()
    try:
        with patch("asyncio.run"):
            watcher._run_periodic_probes_once()
    finally:
        watcher._watch_work_lock.release()

    output = watcher.console.file.getvalue()
    assert "skipped" in output.lower()
    assert watcher._periodic_probe_in_progress is False
