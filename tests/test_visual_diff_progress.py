"""Regression: visual_diff shows a progress bar for large scans."""

from __future__ import annotations

import io

from rich.console import Console

from wup.models.config import VisualDiffConfig
from wup.visual_diff import VisualDiffer


def _make_differ(tmp_path) -> VisualDiffer:
    cfg = VisualDiffConfig(
        enabled=True,
        base_url="http://localhost:8100",
        snapshot_dir=str(tmp_path / "snap"),
        diff_dir=str(tmp_path / "diff"),
        pages_from_endpoints=True,
        max_pages=200,
    )
    return VisualDiffer(str(tmp_path), cfg)


def test_progress_returned_for_big_scans(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("WUP_VISUAL_DIFF_PROGRESS", raising=False)
    differ = _make_differ(tmp_path)
    progress = differ._build_progress("frontend", total=20)
    assert progress is not None
    assert progress.live.transient is True


def test_progress_skipped_for_small_scans(tmp_path) -> None:
    differ = _make_differ(tmp_path)
    assert differ._build_progress("frontend", total=2) is None


def test_progress_can_be_disabled_via_env(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WUP_VISUAL_DIFF_PROGRESS", "0")
    differ = _make_differ(tmp_path)
    assert differ._build_progress("frontend", total=50) is None


def test_progress_uses_injected_console(tmp_path) -> None:
    custom = Console(file=io.StringIO(), width=80)
    cfg = VisualDiffConfig(
        enabled=True,
        base_url="http://localhost:8100",
        snapshot_dir=str(tmp_path / "snap"),
        diff_dir=str(tmp_path / "diff"),
    )
    differ = VisualDiffer(str(tmp_path), cfg, console=custom)
    progress = differ._build_progress("frontend", total=10)
    assert progress is not None
    assert progress.console is custom
