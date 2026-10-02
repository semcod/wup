import importlib
import json
from unittest.mock import Mock

import pytest

from wup.bus import EventBus
from wup.testql_watcher import TestQLWatcher


@pytest.fixture
def watcher(tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.import_module('wup.bus'), 'bus', EventBus())
    value = TestQLWatcher(project_root=str(tmp_path), deps_file=str(tmp_path / 'deps.json'))
    value.health_projection.planfile_reporter = Mock()
    value.health_projection.browser_notifier = Mock()
    value.health_projection.web_client = None
    return value


def events(watcher):
    path = watcher.health_projection.event_store.log_path
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_unchanged_probe_with_absent_track_path_refreshes_state_once(watcher, monkeypatch):
    import wup.testing.handlers.health_handlers as handlers
    monkeypatch.setattr(handlers.time, 'time', lambda: 100)
    watcher._record_health_transition(service='frontend', status='down', stage='probe', message='refused')
    monkeypatch.setattr(handlers.time, 'time', lambda: 200)
    watcher._record_health_transition(service='frontend', status='down', stage='probe', message='refused')
    assert len(events(watcher)) == 1
    assert watcher.health_projection.state['frontend']['updated_at'] == 200
    watcher.health_projection.planfile_reporter.report_failure.assert_called_once()


def test_new_track_receipt_does_not_repeat_failure_notification(watcher):
    for track in ['old.json', 'new.json']:
        watcher._record_health_transition(service='frontend', status='down', stage='quick',
                                         message='failed', track_file=track)
    assert len(events(watcher)) == 1
    assert watcher.health_projection.state['frontend']['track_file'] == 'new.json'
    saved = json.loads(watcher.health_projection.health_state_path.read_text())
    assert saved['frontend']['track_file'] == 'new.json'
    watcher.health_projection.browser_notifier.notify.assert_called_once()


@pytest.mark.parametrize('change', [{'status': 'up'}, {'stage': 'probe'}, {'message': 'different failure'}])
def test_real_health_changes_still_emit_events(watcher, change):
    initial = dict(service='frontend', status='down', stage='quick', message='failed')
    watcher._record_health_transition(**initial)
    watcher._record_health_transition(**{**initial, **change})
    assert len(events(watcher)) == 2
    assert watcher.health_projection.browser_notifier.notify.call_count == 2
