"""Canonical WUP runtime paths under .wup/."""

from __future__ import annotations

from pathlib import Path

HEALTH_STATE_FILE = "service-health.json"
HEALTH_EVENTS_FILE = "service-health-events.jsonl"


def health_state_path(project: Path | str) -> Path:
    return Path(project) / ".wup" / HEALTH_STATE_FILE


def health_events_path(project: Path | str) -> Path:
    return Path(project) / ".wup" / HEALTH_EVENTS_FILE
