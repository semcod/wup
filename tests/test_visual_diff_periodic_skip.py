"""Regression: visual_diff is skipped during periodic probe cycles by default."""

from __future__ import annotations

from unittest.mock import MagicMock

from wup.models.config import VisualDiffConfig
from wup.testql_watcher import TestQLWatcher


def _make_watcher(tmp_path, *, run_on_periodic_probe: bool) -> TestQLWatcher:
    watcher = TestQLWatcher.__new__(TestQLWatcher)
    differ = MagicMock()
    differ.cfg = VisualDiffConfig(enabled=True, run_on_periodic_probe=run_on_periodic_probe)
    watcher.visual_differ = differ
    watcher._periodic_probe_in_progress = False
    return watcher


def test_visual_diff_runs_on_file_change_cycles(tmp_path) -> None:
    watcher = _make_watcher(tmp_path, run_on_periodic_probe=False)
    assert watcher._should_run_visual_diff() is True


def test_visual_diff_skipped_on_periodic_probe_by_default(tmp_path) -> None:
    watcher = _make_watcher(tmp_path, run_on_periodic_probe=False)
    watcher._periodic_probe_in_progress = True
    assert watcher._should_run_visual_diff() is False


def test_visual_diff_runs_on_periodic_probe_when_opted_in(tmp_path) -> None:
    watcher = _make_watcher(tmp_path, run_on_periodic_probe=True)
    watcher._periodic_probe_in_progress = True
    assert watcher._should_run_visual_diff() is True


def test_visual_diff_skipped_when_disabled(tmp_path) -> None:
    watcher = _make_watcher(tmp_path, run_on_periodic_probe=True)
    watcher.visual_differ.cfg.enabled = False
    assert watcher._should_run_visual_diff() is False
