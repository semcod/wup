import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from wup.models.config import ProjectConfig, ServiceConfig, TestQLConfig, WupConfig, WatchConfig
from wup.testql_monitor import (
    ProbeTarget,
    TestQLMonitor,
    assign_probe_to_service,
    is_monitoring_probe,
    parse_scenario_probes,
    parse_service_map_probes,
)
from wup.testql_watcher import TestQLWatcher


def test_parse_scenario_probes_full_url():
    content = """
API[1]{method, endpoint, expected_status}:
  GET, http://localhost:8100/firmware/api/v1/health, 200
"""
    with tempfile.NamedTemporaryFile("w", suffix=".testql.toon.yaml", delete=False) as handle:
        handle.write(content)
        handle.flush()
        path = Path(handle.name)

    probes = parse_scenario_probes(path)
    path.unlink(missing_ok=True)
    assert len(probes) == 1
    assert probes[0].url.endswith("/firmware/api/v1/health")
    assert probes[0].expected_status == 200
    assert is_monitoring_probe(probes[0])


def test_assign_firmware_service():
    services = [
        ServiceConfig(name="frontend", paths=["frontend/**"]),
        ServiceConfig(name="firmware", paths=["backend/firmware/**"]),
    ]
    probe = ProbeTarget(url="http://localhost:8100/firmware/api/v1/health")
    assert assign_probe_to_service(probe, services) == "firmware"


def test_monitor_merges_config_and_service_map():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scenario_dir = root / "testql-scenarios"
        scenario_dir.mkdir()
        scenario = scenario_dir / "fleet-health.testql.toon.yaml"
        scenario.write_text(
            "API[1]{method, endpoint, expected_status}:\n"
            "  GET, http://localhost:8100/firmware/api/v1/execution/status, 200\n",
            encoding="utf-8",
        )

        service_map = root / "service-map.yaml"
        service_map.write_text(
            "service:\n  base_url: http://localhost:8100\n"
            "endpoints:\n"
            "  - { method: GET, path: /firmware/api/v1/health }\n",
            encoding="utf-8",
        )

        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[
                ServiceConfig(name="firmware", paths=["backend/firmware/**"]),
            ],
            watch=WatchConfig(),
            testql=TestQLConfig(
                scenario_dir="testql-scenarios",
                base_url="http://localhost:8100",
                endpoint_discovery=True,
                service_map_globs=["service-map.yaml"],
                endpoints_by_service={
                    "firmware": ["/firmware/api/v1/execution/logs"],
                },
            ),
        )
        monitor = TestQLMonitor(root, cfg)
        probes = monitor.probes_for_service("firmware")
        urls = {p.url for p in probes}
        assert "http://localhost:8100/firmware/api/v1/health" in urls
        assert "http://localhost:8100/firmware/api/v1/execution/status" in urls
        assert "http://localhost:8100/firmware/api/v1/execution/logs" in urls


def test_live_probe_failure_updates_health():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="firmware", paths=["backend/firmware/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(
                scenario_dir="testql-scenarios",
                base_url="http://localhost:8100",
                endpoints_by_service={"firmware": ["/firmware/api/v1/health"]},
            ),
        )
        watcher = TestQLWatcher(
            project_root=str(root),
            deps_file=str(root / "deps.json"),
            scenarios_dir="testql-scenarios",
            config=cfg,
        )

        failing = ProbeTarget(url="http://localhost:8100/firmware/api/v1/health")

        def fake_probe(self, timeout_s=10.0):
            return False, "HTTP 500 (expected 200)"

        with patch.object(ProbeTarget, "probe", fake_probe):
            ok = asyncio.run(watcher._run_live_http_probes("firmware", []))

        assert ok is False
        state = json.loads((root / ".wup" / "service-health.json").read_text(encoding="utf-8"))
        assert state["firmware"]["status"] == "down"
        assert state["firmware"]["stage"] == "probe"
