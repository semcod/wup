import json
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, List

from wup.bus import Event


class EventStore:
    """Append-only store for domain events."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> None:
        """Append an event to the log."""
        if not is_dataclass(event):
            event_data = event.__dict__.copy()
        else:
            event_data = asdict(event)

        record = {
            "timestamp": int(time.time()),
            "type": event.__class__.__name__,
            "data": event_data,
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        """Read all events from the log."""
        if not self.log_path.exists():
            return []
        events = []
        with self.log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    events.append(json.loads(line))
        return events
