import tempfile
from pathlib import Path


from wup.models.config import ProjectConfig, ServiceConfig, TestQLConfig, WupConfig, WatchConfig
from wup.monitoring_manifest import (
    MANIFEST_BEGIN,
    MANIFEST_END,
    build_monitoring_manifest,
    discover_docker_compose_services,
    load_monitoring_manifest_from_yaml,
    patch_wup_yaml_monitoring,
)


def test_discover_docker_compose():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "docker-compose.yml").write_text(
            "services:\n"
            "  firmware:\n"
            "    container_name: test-simulator-firmware\n"
            "    ports:\n"
            "      - '8202:8202'\n"
            "    healthcheck:\n"
            "      test: ['CMD', 'curl', 'http://127.0.0.1:8202/health']\n",
            encoding="utf-8",
        )
        found = discover_docker_compose_services(root)
        assert len(found) == 1
        assert found[0].compose_service == "firmware"
        assert found[0].container_name == "test-simulator-firmware"


def test_patch_and_load_monitoring_block():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "docker-compose.yml").write_text(
            "services:\n  firmware:\n    container_name: test-simulator-firmware\n    ports:\n      - '8202:8202'\n",
            encoding="utf-8",
        )
        cfg_path = root / "wup.yaml"
        cfg_path.write_text(
            "project:\n  name: demo\n"
            "services:\n  - name: firmware\n    paths: ['backend/firmware/**']\n"
            "testql:\n  base_url: http://localhost:8100\n"
            "  endpoints_by_service:\n    firmware:\n      - /firmware/api/v1/health\n",
            encoding="utf-8",
        )
        wup_config = WupConfig(
            project=ProjectConfig(name="demo"),
            services=[ServiceConfig(name="firmware", paths=["backend/firmware/**"])],
            watch=WatchConfig(),
            testql=TestQLConfig(
                base_url="http://localhost:8100",
                endpoints_by_service={"firmware": ["/firmware/api/v1/health"]},
                probe_interval_s=60,
            ),
        )
        manifest = build_monitoring_manifest(root, wup_config)
        patch_wup_yaml_monitoring(cfg_path, manifest)

        text = cfg_path.read_text(encoding="utf-8")
        assert MANIFEST_BEGIN in text
        assert MANIFEST_END in text

        loaded = load_monitoring_manifest_from_yaml(cfg_path)
        assert loaded is not None
        assert loaded["wup_services"]["firmware"]["live_probes"]
        assert loaded["wup_services"]["firmware"]["live_probes"][0]["url"].endswith("/firmware/api/v1/health")
        assert loaded["wup_services"]["firmware"]["docker"][0]["compose_service"] == "firmware"
