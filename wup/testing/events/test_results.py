from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from wup.bus import Event


@dataclass
class ScenarioPassed(Event):
    service: str
    stage: str
    scenario: Path


@dataclass
class ScenarioFailed(Event):
    service: str
    stage: str
    scenario: Path
    reason: str
    track_file: str
    endpoints: list[str]
