from dataclasses import dataclass
from typing import Optional
from wup.bus import Query

@dataclass
class GetServiceHealth(Query):
    service: Optional[str] = None
