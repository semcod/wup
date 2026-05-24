"""Regression: nested test directories are ignored by the file watcher."""

from __future__ import annotations

from pathlib import Path

from wup.core import WupWatcher
from wup.models.config import ProjectConfig, WatchConfig, WupConfig


def _watcher() -> WupWatcher:
    cfg = WupConfig(
        project=ProjectConfig(name="t"),
        watch=WatchConfig(
            exclude_patterns=["**/tests/**", "*.md"],
            file_types=[".ts", ".py"],
        ),
    )
    return WupWatcher(project_root=".", config=cfg)


def test_nested_tests_directory_ignored() -> None:
    watcher = _watcher()
    assert watcher._is_file_ignored(Path("frontend/src/tests/setup.ts"))


def test_src_file_not_ignored() -> None:
    watcher = _watcher()
    assert not watcher._is_file_ignored(Path("frontend/src/services/foo.ts"))


def test_glob_exclude_pattern() -> None:
    watcher = _watcher()
    assert watcher._path_matches_exclude_pattern(Path("docs/readme.md"), "*.md")
