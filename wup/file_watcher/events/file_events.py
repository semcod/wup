from dataclasses import dataclass
from typing import Optional

from wup.bus import Event


@dataclass
class FileChanged(Event):
    file_path: str
    inferred_service: Optional[str]
