"""Regression: dedupe registry must not mute recurrences of CLOSED tickets.

A stale `.wup/planfile-tickets.json` entry whose ticket was already
done/canceled used to suppress every future ticket for the same
failure fingerprint — a regression of an old outage became silently
invisible (found live: `docker stop connect-scenario` produced no ticket
because PLF-1950 from a month earlier still held the fingerprint).
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from wup import planfile_reporter as reporter_mod
from wup.models.config import PlanfileConfig
from wup.planfile_reporter import PlanfileReporter


def _reporter(tmp_path: Path) -> PlanfileReporter:
    cfg = PlanfileConfig(enabled=True, command="planfile")
    return PlanfileReporter(tmp_path, cfg)


def _seed_dedupe(rep: PlanfileReporter, fingerprint_kwargs: dict, ticket_id: str) -> None:
    fingerprint = rep._fingerprint(**fingerprint_kwargs)
    rep.dedupe_path.parent.mkdir(parents=True, exist_ok=True)
    rep.dedupe_path.write_text(
        json.dumps({fingerprint: {"ticket_id": ticket_id, "service": fingerprint_kwargs["service"], "stage": fingerprint_kwargs["stage"]}}),
        encoding="utf-8",
    )


FAIL = {"service": "svc", "status": "down", "stage": "probe", "message": "connection refused"}


def test_parse_ticket_id_supports_project_specific_prefixes(tmp_path):
    rep = _reporter(tmp_path)

    assert rep._parse_ticket_id("✓ Created STARTER-074: intent failure") == "STARTER-074"
    assert rep._parse_ticket_id("Created PLF-2") == "PLF-2"


def test_open_ticket_still_mutes_recurrence(tmp_path, monkeypatch):
    rep = _reporter(tmp_path)
    _seed_dedupe(rep, FAIL, "PLF-1")

    def fake_run(cmd, **kwargs):
        assert "show" in cmd
        return SimpleNamespace(returncode=0, stdout=json.dumps({"id": "PLF-1", "status": "open"}), stderr="")

    monkeypatch.setattr(reporter_mod.subprocess, "run", fake_run)
    assert rep.report_failure(**FAIL) == "PLF-1"


def test_closed_ticket_refiles_fresh_ticket(tmp_path, monkeypatch):
    rep = _reporter(tmp_path)
    _seed_dedupe(rep, FAIL, "PLF-1")
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        if "show" in cmd:
            return SimpleNamespace(returncode=0, stdout=json.dumps({"id": "PLF-1", "status": "done"}), stderr="")
        return SimpleNamespace(returncode=0, stdout="✓ Created PLF-2: [AUTO-DIAG] wup-svc probe down", stderr="")

    monkeypatch.setattr(reporter_mod.subprocess, "run", fake_run)
    monkeypatch.setattr(rep, "_wait_for_planfile_store_ready", lambda timeout_s=30.0: True)

    assert rep.report_failure(**FAIL) == "PLF-2"
    # registry now points at the fresh ticket
    dedupe = json.loads(rep.dedupe_path.read_text(encoding="utf-8"))
    assert [v["ticket_id"] for v in dedupe.values()] == ["PLF-2"]


def test_build_ticket_command_marks_configured_integrations(tmp_path):
    rep = PlanfileReporter(
        tmp_path,
        PlanfileConfig(enabled=True, integrations=["github"], labels=["wup"]),
    )

    cmd = rep._build_ticket_cmd("test", "description", "")

    assert cmd.count("--integration") == 1
    assert cmd[cmd.index("--integration") + 1] == "github"
    assert "--sync" not in cmd


def test_sync_on_change_adds_planfile_auto_sync_flag(tmp_path):
    rep = PlanfileReporter(
        tmp_path,
        PlanfileConfig(enabled=True, integrations=["github"], sync_on_change=True),
    )

    assert "--sync" in rep._build_ticket_cmd("test", "description", "")


def test_recovery_completes_open_ticket_when_enabled(tmp_path, monkeypatch):
    rep = PlanfileReporter(
        tmp_path,
        PlanfileConfig(enabled=True, integrations=["github"], sync_on_change=True, complete_on_recovery=True),
    )
    _seed_dedupe(rep, FAIL, "PLF-1")
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        if "show" in cmd:
            return SimpleNamespace(returncode=0, stdout=json.dumps({"id": "PLF-1", "status": "open"}), stderr="")
        return SimpleNamespace(returncode=0, stdout="Completed PLF-1", stderr="")

    monkeypatch.setattr(reporter_mod.subprocess, "run", fake_run)
    rep.clear_service_stage(service="svc", stage="probe")

    assert json.loads(rep.dedupe_path.read_text(encoding="utf-8")) == {}
    assert ["planfile", "ticket", "complete", "PLF-1"] == calls[-2][:4]
    assert calls[-1] == ["planfile", "sync", "github", ".", "--direction", "to"]


def test_recovery_keeps_dedupe_entry_when_completion_fails(tmp_path, monkeypatch):
    rep = PlanfileReporter(
        tmp_path,
        PlanfileConfig(enabled=True, complete_on_recovery=True),
    )
    _seed_dedupe(rep, FAIL, "PLF-1")

    def fake_run(cmd, **kwargs):
        if "show" in cmd:
            return SimpleNamespace(returncode=0, stdout=json.dumps({"id": "PLF-1", "status": "open"}), stderr="")
        return SimpleNamespace(returncode=1, stdout="", stderr="store unavailable")

    monkeypatch.setattr(reporter_mod.subprocess, "run", fake_run)
    rep.clear_service_stage(service="svc", stage="probe")

    assert [value["ticket_id"] for value in json.loads(rep.dedupe_path.read_text(encoding="utf-8")).values()] == ["PLF-1"]


def test_show_error_keeps_muting_conservatively(tmp_path, monkeypatch):
    rep = _reporter(tmp_path)
    _seed_dedupe(rep, FAIL, "PLF-1")

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="boom")

    monkeypatch.setattr(reporter_mod.subprocess, "run", fake_run)
    assert rep.report_failure(**FAIL) == "PLF-1"
