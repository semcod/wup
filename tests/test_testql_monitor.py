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


def test_hardware_identify_and_peripheral_status_are_live_probes():
    assert is_monitoring_probe(
        ProbeTarget(url="http://localhost:8202/api/v1/hardware/identify")
    )
    assert is_monitoring_probe(
        ProbeTarget(url="http://localhost:8096/api/v3/hardware/peripheral-status/modbus-io")
    )


def test_firmware_plugin_health_catalog_not_periodic_live_probe():
    """Plugin health is listed for detail TestQL; live watch uses identify + peripheral-status."""
    probe = ProbeTarget(url="http://localhost:8202/api/v1/plugins/modbus-io/health")
    assert is_monitoring_probe(probe)
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[
                ServiceConfig(name="firmware", paths=["backend/firmware/**"]),
                ServiceConfig(name="connect-scenario", paths=["connect-scenario/**"]),
            ],
            watch=WatchConfig(),
            testql=TestQLConfig(
                hardware_usb_modules={
                    "oqlos_url": "http://localhost:8202",
                    "proxy_url": "http://localhost:8096",
                    "module_ids": ["modbus-io", "modbus-adc"],
                },
            ),
        )
        monitor = TestQLMonitor(root, cfg)
        firmware = {p.url for p in monitor.probes_for_service("firmware")}
        scenario = {p.url for p in monitor.probes_for_service("connect-scenario")}
    assert "http://localhost:8202/api/v1/hardware/identify" in firmware
    assert "http://localhost:8202/api/v1/plugins/modbus-io/health" not in firmware
    assert "http://localhost:8096/api/v3/hardware/identify" in scenario
    assert (
        "http://localhost:8096/api/v3/hardware/peripheral-status/modbus-io" in scenario
    )
    assert (
        "http://localhost:8096/api/v3/hardware/peripheral-status/modbus-adc" in scenario
    )


def test_connect_api_paths_on_8100_are_not_monitoring_probes():
    probe = ProbeTarget(url="http://localhost:8100/api/id/health")
    assert not is_monitoring_probe(probe)
    assert assign_probe_to_service(
        probe,
        [ServiceConfig(name="backend", paths=["backend/**", "api/**"])],
    ) != "backend"


def test_connect_health_on_8103_not_assigned_to_backend():
    services = [
        ServiceConfig(name="frontend", paths=["frontend/**"]),
        ServiceConfig(name="backend", paths=["backend/**"]),
    ]
    probe = ProbeTarget(url="http://localhost:8103/api/id/health")
    assert assign_probe_to_service(probe, services) is None


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
        # Execution telemetry is for fleet TestQL, not WUP live liveness probes.
        assert "http://localhost:8100/firmware/api/v1/execution/status" not in urls
        assert "http://localhost:8100/firmware/api/v1/execution/logs" not in urls


def test_firmware_live_probe_prefers_oqlos_8202():
    probes = [
        ProbeTarget(url="http://localhost:8100/firmware/api/v1/health"),
        ProbeTarget(url="http://localhost:8202/health"),
    ]
    ordered = TestQLMonitor._sort_probes_for_live(probes, service="firmware")
    assert ordered[0].url == "http://localhost:8202/health"


def test_probes_for_service_ignores_non_health_extra_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="backend", paths=["backend/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(
                base_url="http://localhost:8100",
                api_base_url="http://localhost:8101",
                endpoints_by_service={"backend": ["http://localhost:8101/api/v3/health"]},
            ),
        )
        monitor = TestQLMonitor(root, cfg)
        probes = monitor.probes_for_service(
            "backend",
            ["/connect-config", "http://localhost:8101/connect-config"],
        )
        urls = {p.url for p in probes}
        assert urls == {"http://localhost:8101/api/v3/health"}


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
