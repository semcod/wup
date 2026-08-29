"""Tests for realtime anomaly helpers and their integration in the watch loop."""

import tempfile
from pathlib import Path

from wup.config import WupConfig, ProjectConfig, WatchConfig, ServiceConfig, ServiceTestConfig, TestStrategyConfig, TestQLConfig
from wup.core import WupWatcher
from wup.realtime_anomalies import BurstAnomaly, ChangeBurstDetector, LatencyTracker


class TestLatencyTracker:
    def test_no_anomaly_below_min_samples(self):
        tracker = LatencyTracker()
        for _ in range(7):
            assert tracker.record("/ep", 10.0) is None

    def test_flags_spike_over_baseline(self):
        tracker = LatencyTracker(min_samples=5, ratio_threshold=3.0, absolute_floor_ms=50.0)
        for _ in range(5):
            tracker.record("/ep", 20.0)
        anomaly = tracker.record("/ep", 200.0)
        assert anomaly is not None
        assert anomaly.endpoint == "/ep"
        assert anomaly.ratio >= 3.0

    def test_no_flag_when_latency_below_absolute_floor(self):
        tracker = LatencyTracker(min_samples=5, ratio_threshold=3.0, absolute_floor_ms=50.0)
        for _ in range(5):
            tracker.record("/ep", 5.0)
        # ratio is huge but latency (15ms) is under the 50ms floor
        assert tracker.record("/ep", 15.0) is None

    def test_baseline_unlearned_until_min_samples(self):
        tracker = LatencyTracker(min_samples=5)
        assert tracker.baseline("/ep") is None
        for _ in range(5):
            tracker.record("/ep", 10.0)
        assert tracker.baseline("/ep") == 10.0

    def test_slow_endpoint_never_flagged_when_consistently_slow(self):
        tracker = LatencyTracker(min_samples=5)
        for _ in range(10):
            assert tracker.record("/ep", 900.0) is None


class TestChangeBurstDetector:
    def test_no_burst_under_threshold(self):
        detector = ChangeBurstDetector(burst_threshold=5, window_s=10.0)
        for i in range(4):
            assert detector.record("svc", now=100.0 + i) is None

    def test_burst_reported_once_then_rearmed(self):
        detector = ChangeBurstDetector(burst_threshold=5, window_s=10.0)
        anomalies = [detector.record("svc", now=100.0 + i * 0.1) for i in range(6)]
        # 5th event (index 4) crosses the threshold -> reported once
        reported = [a for a in anomalies if a is not None]
        assert len(reported) == 1
        assert isinstance(reported[0], BurstAnomaly)
        assert reported[0].service == "svc"
        assert reported[0].events == 5
        # detector re-armed: next few events within window report nothing
        for i in range(3):
            assert detector.record("svc", now=100.5 + i * 0.1) is None

    def test_old_events_expire_out_of_window(self):
        detector = ChangeBurstDetector(burst_threshold=5, window_s=10.0)
        for _ in range(4):
            detector.record("svc", now=100.0)
        # long gap: window slides past previous events
        assert detector.record("svc", now=200.0) is None


class TestWatcherDebounce:
    def _make_watcher(self, tmpdir, service="users"):
        (Path(tmpdir) / "app" / service).mkdir(parents=True, exist_ok=True)
        config = WupConfig(
            project=ProjectConfig(name="test"),
            watch=WatchConfig(paths=["app/**"]),
            services=[ServiceConfig(
                name=service,
                root=f"app/{service}",
                paths=[f"app/{service}/**"],
                quick_tests=ServiceTestConfig(scope="all", max_endpoints=3),
            )],
            test_strategy=TestStrategyConfig(),
            testql=TestQLConfig(),
        )
        watcher = WupWatcher(tmpdir, config=config)
        watcher.dependency_mapper.service_to_endpoints[service] = ["/api/users"]
        return watcher

    def test_single_save_emits_one_quick_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = self._make_watcher(tmpdir)
            file_path = str(Path(tmpdir) / "app" / "users" / "routes.py")
            watcher.on_file_change(file_path)
            watcher.on_file_change(file_path)  # cascade: same save, second event
            watcher._pending_event_times["users"] = 0
            watcher._flush_pending_events()
            assert len(watcher.test_queue) == 1

    def test_burst_event_storm_still_emits_one_test(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = self._make_watcher(tmpdir)
            file_path = str(Path(tmpdir) / "app" / "users" / "routes.py")
            for _ in range(150):
                watcher.on_file_change(file_path)
            watcher._pending_event_times["users"] = 0
            watcher._flush_pending_events()
            assert len(watcher.test_queue) == 1

    def test_events_buffered_during_debounce_window(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = self._make_watcher(tmpdir)
            file_path = str(Path(tmpdir) / "app" / "users" / "routes.py")
            watcher.on_file_change(file_path)
            # window not elapsed: nothing scheduled, event stays buffered
            watcher._flush_pending_events()
            assert len(watcher.test_queue) == 0
            assert watcher._pending_events["users"]

    def test_cooldown_prevents_rescheduling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = self._make_watcher(tmpdir)
            file_path = str(Path(tmpdir) / "app" / "users" / "routes.py")
            watcher.on_file_change(file_path)
            watcher._pending_event_times["users"] = 0
            watcher._flush_pending_events()
            assert len(watcher.test_queue) == 1
            # immediately re-flush with fresh events: cooldown blocks a second test
            watcher.on_file_change(file_path)
            watcher._pending_event_times["users"] = 0
            watcher._flush_pending_events()
            assert len(watcher.test_queue) == 1
