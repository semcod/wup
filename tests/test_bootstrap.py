"""Tests for the crash-safe console bootstrap."""

from __future__ import annotations

from unittest.mock import Mock

from wup import bootstrap


def test_watchdog_preflight_reports_signal(monkeypatch) -> None:
    monkeypatch.setattr(
        bootstrap.subprocess,
        "run",
        Mock(return_value=Mock(returncode=-11, stderr="")),
    )

    ok, detail = bootstrap._watchdog_preflight()

    assert ok is False
    assert "signal 11" in detail


def test_main_stops_before_importing_cli_on_failed_watch_preflight(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(bootstrap, "_watchdog_preflight", lambda: (False, "signal 11"))

    code = bootstrap.main(["watch", "."])

    assert code == 70
    assert "ABI preflight" in capsys.readouterr().err
