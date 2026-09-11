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
from dataclasses import dataclass
from typing import Deque, Dict, Optional


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

    Three gates keep the signal high on noisy dev hosts (containers, reverse
    proxies, builds running next to the fleet), where 50-150 ms blips on a
    ~1 ms idle endpoint are routine and a bare ratio test is pure noise
    amplification (e.g. ×71.5 for 74 ms vs 1 ms):

    - the ratio gate only applies when the baseline itself is meaningful
      (``baseline_floor_ms``);
    - endpoints with a trivial baseline still flag on sustained absolute
      slowness (``slow_absolute_ms``);
    - a violation needs ``confirm_samples`` consecutive offending samples and
      is reported once per sustained episode, then re-arms.
    """

    def __init__(
        self,
        window: int = 50,
        min_samples: int = 8,
        ratio_threshold: float = 3.0,
        absolute_floor_ms: float = 50.0,
        baseline_floor_ms: float = 10.0,
        slow_absolute_ms: float = 300.0,
        confirm_samples: int = 3,
    ):
        self._samples: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=window)
        )
        self._violation_streaks: Dict[str, int] = defaultdict(int)
        self.min_samples = min_samples
        self.ratio_threshold = ratio_threshold
        self.absolute_floor_ms = absolute_floor_ms
        self.baseline_floor_ms = baseline_floor_ms
        self.slow_absolute_ms = slow_absolute_ms
        self.confirm_samples = max(1, confirm_samples)

    def _violates(self, baseline: float, latency_ms: float) -> bool:
        """True when a sample invalidates the established baseline."""
        if latency_ms < self.absolute_floor_ms:
            return False
        if baseline < self.baseline_floor_ms:
            # Trivial baseline: the ratio amplifies host noise, not
            # regressions — require sustained absolute slowness instead.
            return latency_ms >= self.slow_absolute_ms
        return latency_ms / baseline >= self.ratio_threshold

    def record(self, endpoint: str, latency_ms: float) -> Optional[LatencyAnomaly]:
        """Record a sample; return an anomaly when the baseline is violated.

        A violation must persist for ``confirm_samples`` consecutive samples;
        the anomaly is reported once per sustained episode and the tracker
        re-arms after latency returns under the thresholds.
        """
        samples = self._samples[endpoint]
        anomaly: Optional[LatencyAnomaly] = None
        if len(samples) >= self.min_samples:
            baseline = statistics.median(samples)
            if self._violates(baseline, latency_ms):
                self._violation_streaks[endpoint] += 1
                if self._violation_streaks[endpoint] == self.confirm_samples:
                    anomaly = LatencyAnomaly(
                        endpoint=endpoint,
                        latency_ms=latency_ms,
                        baseline_p95_ms=baseline,
                        ratio=latency_ms / baseline,
                    )
            else:
                self._violation_streaks[endpoint] = 0
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
