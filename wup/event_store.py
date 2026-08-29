import json
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, List

from wup.bus import Event


class EventStore:
    """Append-only store for domain events, with size-based rotation.

    The health event log is the shared state an LLM agent reads after its own
    change; unbounded growth (months of probes) makes ``read_all`` slow and
    the file unreadable. Rotate at ``max_bytes`` keeping one archive.
    """

    DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB live + 5 MB archive

    def __init__(self, log_path: Path, max_bytes: int = DEFAULT_MAX_BYTES):
        self.log_path = log_path
        self.max_bytes = max_bytes
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _rotate_if_needed(self) -> None:
        try:
            if self.log_path.stat().st_size < self.max_bytes:
                return
        except OSError:
            return
        archive = self.log_path.with_suffix(self.log_path.suffix + ".1")
        try:
            archive.unlink(missing_ok=True)
            self.log_path.replace(archive)
        except OSError:
            return

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
        self._rotate_if_needed()
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
