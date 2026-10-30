import asyncio
import json
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import wup.planfile_reporter as reporter_module
import wup.testql_monitor as monitor_module
from wup.models.config import PlanfileConfig
from wup.planfile_reporter import PlanfileReporter
from wup.realtime_anomalies import LatencyTracker
from wup.testql_monitor import TestQLMonitor
from wup.testql_watcher import TestQLWatcher


URL = "http://example.test/health"
OTHER = "http://other.test/health"


@pytest.fixture
def incident(tmp_path, monkeypatch):
    reporter = PlanfileReporter(tmp_path, PlanfileConfig(enabled=True, complete_on_recovery=True))
    tickets = {}
    completed = []

    def seed(ticket_id="PLF-1", url=URL, service="frontend", stage="probe-latency", summary=None):
        message = summary if summary is not None else f"{url} 200 ms vs baseline 20 ms (×10.0)"
        tickets[ticket_id] = {
            "id": ticket_id, "status": "open",
            "description": f"Failure summary:\n{message}\n\nInvestigate the failing probe.",
        }
        entries = reporter._load_dedupe()
        entries[ticket_id] = {"ticket_id": ticket_id, "service": service, "stage": stage}
        reporter._save_dedupe(entries)

    def run(cmd, **kwargs):
        if cmd[2] == "show":
            return SimpleNamespace(returncode=0, stdout=json.dumps({"ticket": tickets[cmd[3]]}), stderr="")
        assert cmd[2] == "complete"
        completed.append(cmd[3])
        tickets[cmd[3]]["status"] = "done"
        return SimpleNamespace(returncode=0, stdout="completed", stderr="")

    monkeypatch.setattr(reporter_module.subprocess, "run", run)
    seed()
    return SimpleNamespace(reporter=reporter, seed=seed, tickets=tickets, completed=completed)


def run_cycle(monkeypatch, incident, *, latency=20, ok=True, learned=True, extra=(), limit=1):
    # Real monitor/thread pool, deterministic elapsed time independent of host load.
    clock = threading.local()

    def monotonic():
        value = getattr(clock, "elapsed", 0)
        clock.elapsed = 0
        return value

    def probe(timeout_s):
        clock.elapsed = latency / 1000
        return ok, "fixture response"

    monkeypatch.setattr(monitor_module, "time", SimpleNamespace(monotonic=monotonic))
    targets = [SimpleNamespace(url=URL, method="GET", probe=probe), *extra]
    monitor = object.__new__(TestQLMonitor)
    monitor.probes_for_service = lambda service: targets
    monitor._sort_probes_for_live = lambda probes, service: list(probes)
    tracker = LatencyTracker(min_samples=8, confirm_samples=3)
    if learned:
        for target in targets:
            for _ in range(8):
                tracker.record(target.url, 20)
    watcher = object.__new__(TestQLWatcher)
    watcher.monitor = monitor
    watcher.latency_tracker = tracker
    watcher.planfile_reporter = incident.reporter
    watcher._quick_probe_limit = lambda service: limit
    watcher._quick_probe_timeout = lambda: 1
    watcher.console = Mock()
    watcher._record_health_transition = Mock()
    watcher.web_client = SimpleNamespace(is_active=False)
    result = asyncio.run(watcher._run_live_http_probes("frontend", []))
    return watcher, tracker, result


def test_fast_http_probe_completes_original_latency_stage(monkeypatch, incident):
    incident.seed("PLF-2", url=OTHER)
    incident.seed("PLF-3", service="backend")
    incident.seed("PLF-4", stage="quick")
    _, _, result = run_cycle(monkeypatch, incident)
    assert result is True
    assert incident.completed == ["PLF-1"]
    assert set(incident.reporter._load_dedupe()) == {"PLF-2", "PLF-3", "PLF-4"}


@pytest.mark.parametrize("latency,ok,learned", [(20, False, True), (20, True, False), (200, True, True)])
def test_failed_learning_or_still_slow_probe_keeps_incident(monkeypatch, incident, latency, ok, learned):
    run_cycle(monkeypatch, incident, latency=latency, ok=ok, learned=learned)
    assert incident.completed == []
    assert "PLF-1" in incident.reporter._load_dedupe()


def test_skipped_endpoint_cannot_be_resolved_by_its_old_fast_history(monkeypatch, incident):
    incident.seed("PLF-2", url=OTHER)
    skipped = SimpleNamespace(url=OTHER, method="GET", probe=Mock(side_effect=AssertionError("must be skipped")))
    _, tracker, _ = run_cycle(monkeypatch, incident, extra=[skipped])
    assert incident.completed == ["PLF-1"]
    assert "PLF-2" in incident.reporter._load_dedupe()
    assert tracker.baseline(OTHER) == 20


@pytest.mark.parametrize("summary", ["not a latency summary", "http://example.test/health 200 ms vs baseline 20 ms (×10.0); malformed"])
def test_malformed_original_evidence_does_not_complete(monkeypatch, incident, summary):
    incident.seed(summary=summary)
    run_cycle(monkeypatch, incident)
    assert incident.completed == []


def test_compound_incident_waits_until_all_original_urls_recover(monkeypatch, incident):
    incident.seed(summary=f"{URL} 200 ms vs baseline 20 ms (×10.0); {OTHER} 300 ms vs baseline 20 ms (×15.0)")
    run_cycle(monkeypatch, incident)
    assert incident.completed == []


def test_compound_incident_completes_when_both_urls_are_observed_healthy(monkeypatch, incident):
    incident.seed(summary=f"{URL} 200 ms vs baseline 20 ms (×10.0); {OTHER} 300 ms vs baseline 20 ms (×15.0)")
    other = SimpleNamespace(url=OTHER, method="GET", probe=lambda **kwargs: (True, "healthy"))
    run_cycle(monkeypatch, incident, extra=[other], limit=2)
    assert incident.completed == ["PLF-1"]


@pytest.mark.parametrize("payload", [None, [], {"description": None}, {"status": "open"}])
def test_missing_or_invalid_ticket_projection_is_preserved(monkeypatch, incident, payload):
    incident.tickets["PLF-1"] = payload
    run_cycle(monkeypatch, incident)
    assert incident.completed == []
    assert "PLF-1" in incident.reporter._load_dedupe()


def test_relearned_slow_baseline_is_not_recovery_from_original_incident(monkeypatch, incident):
    watcher, tracker, _ = run_cycle(monkeypatch, incident, learned=False, latency=200)
    for _ in range(12):
        tracker.record(URL, 200)
    asyncio.run(watcher._run_live_http_probes("frontend", []))
    assert incident.completed == []


def test_unknown_and_ongoing_episode_are_not_recovery():
    tracker = LatencyTracker(min_samples=8, confirm_samples=2)
    assert not tracker.is_recovered(URL, baseline_ms=20)
    for _ in range(8):
        tracker.record(URL, 20)
    tracker.record(URL, 200)
    assert tracker.record(URL, 220) is not None
    assert tracker.record(URL, 240) is None  # no second alert, still an active episode
    assert not tracker.is_recovered(URL, baseline_ms=20)
    tracker.record(URL, 20)
    assert tracker.is_recovered(URL, baseline_ms=20)


def test_missing_monitor_or_empty_probe_set_never_resolves(incident):
    watcher = object.__new__(TestQLWatcher)
    watcher.planfile_reporter = incident.reporter
    watcher.monitor = None
    assert asyncio.run(watcher._run_live_http_probes("frontend", []))
    watcher.monitor = SimpleNamespace(probes_for_service=lambda service: [])
    assert asyncio.run(watcher._run_live_http_probes("frontend", []))
    assert incident.completed == []
