"""Runtime data models for WUP.

A :class:`ServiceTestTarget` bundles a service name with the endpoints to test
for it. It replaces the ``(service, endpoints)`` pair that was previously
passed together through every test-entry method on ``WupWatcher``,
``TestQLWatcher`` and ``VisualDiffer`` (a recurring data clump).
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ServiceTestTarget:
    """A service and the endpoints that should be exercised for it.

    Args:
        service: Name of the service under test.
        endpoints: Endpoint URLs (or page routes) to probe for the service.
    """

    service: str
    endpoints: List[str] = field(default_factory=list)
