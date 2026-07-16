"""Regression: a watcher that never watched must not exit as a clean run.

`start_watching` used to bare-`return` when every configured watch path was
missing — under systemd (Restart=on-failure) the clean exit 0 meant the unit
silently died and never came back. It now returns False and the CLI turns
that into exit code 1.
"""

from __future__ import annotations

from wup.core import WupWatcher
from wup.models.config import ProjectConfig, WatchConfig, WupConfig


def _watcher_with_paths(paths: list[str]) -> WupWatcher:
    cfg = WupConfig(
        project=ProjectConfig(name="t"),
        watch=WatchConfig(paths=paths),
    )
    return WupWatcher(project_root="/nonexistent-wup-test-root", config=cfg)


def test_start_watching_returns_false_when_no_valid_paths() -> None:
    watcher = _watcher_with_paths(["does-not-exist/**"])
    assert watcher.start_watching() is False


def test_start_watching_returns_false_for_explicit_missing_paths() -> None:
    watcher = _watcher_with_paths([])
    assert watcher.start_watching(["/nonexistent-wup-test-root/a"]) is False
