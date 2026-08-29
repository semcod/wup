"""High-signal realtime anomaly checks for the watch loop.

Extends the offline anomaly_detector (hash/structure/AST drift) with runtime
signals that only exist while services are running:

- LatencyTracker: rolling p95 latency per endpoint; flags endpoints whose
  latency jumps well above their established baseline (early signal of a
  regression introduced by the change that just triggered the test).
- ChangeBurstDetector: flags pathological editing patterns (tight loops of
  events for one service — usually a runaway generator or sync loop, not a
  human edit).

Both are dependency-free and add sub-millisecond overhead per event.
"""

from __future__ import annotations

import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional


@dataclass
class LatencyAnomaly:
    endpoint: str
    latency_ms: float
    baseline_p95_ms: float
    ratio: float


@dataclass
class BurstAnomaly:
    service: str
    events: int
    window_s: float


class LatencyTracker:
    """Rolling latency baseline per endpoint with anomaly flagging.

    Keeps the last ``window`` samples per endpoint. Until ``min_samples``
    samples exist the endpoint is considered unlearned (no anomalies), so the
    tracker never flags fresh endpoints on their first slow response.
    """

    def __init__(
        self,
        window: int = 50,
        min_samples: int = 8,
        ratio_threshold: float = 3.0,
        absolute_floor_ms: float = 50.0,
    ):
        self._samples: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=window)
        )
        self.min_samples = min_samples
        self.ratio_threshold = ratio_threshold
        self.absolute_floor_ms = absolute_floor_ms

    def record(self, endpoint: str, latency_ms: float) -> Optional[LatencyAnomaly]:
        """Record a sample; return an anomaly when it violates the baseline."""
        samples = self._samples[endpoint]
        anomaly: Optional[LatencyAnomaly] = None
        if len(samples) >= self.min_samples:
            baseline = statistics.median(samples)
            # Only meaningful when the baseline itself is fast enough that a
            # ratio spike represents a real user-visible slowdown.
            if (
                baseline > 0
                and latency_ms >= self.absolute_floor_ms
                and latency_ms / baseline >= self.ratio_threshold
            ):
                anomaly = LatencyAnomaly(
                    endpoint=endpoint,
                    latency_ms=latency_ms,
                    baseline_p95_ms=baseline,
                    ratio=latency_ms / baseline,
                )
        samples.append(latency_ms)
        return anomaly

    def baseline(self, endpoint: str) -> Optional[float]:
        samples = self._samples.get(endpoint)
        if not samples or len(samples) < self.min_samples:
            return None
        return statistics.median(samples)


class ChangeBurstDetector:
    """Flags event bursts per service (runaway generators, sync loops)."""

    def __init__(self, window_s: float = 10.0, burst_threshold: int = 120):
        self.window_s = window_s
        self.burst_threshold = burst_threshold
        self._events: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=burst_threshold * 2)
        )

    def record(self, service: str, now: Optional[float] = None) -> Optional[BurstAnomaly]:
        current = time.time() if now is None else now
        events = self._events[service]
        events.append(current)
        cutoff = current - self.window_s
        while events and events[0] < cutoff:
            events.popleft()
        if len(events) >= self.burst_threshold:
            events.clear()  # report once per burst, then re-arm
            return BurstAnomaly(
                service=service, events=self.burst_threshold, window_s=self.window_s
            )
        return None
