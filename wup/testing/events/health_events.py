from dataclasses import dataclass
from wup.bus import Event

@dataclass
class ServiceHealthChanged(Event):
    service: str
    status: str
    previous_status: str
    stage: str
    message: str
    track_file: str
