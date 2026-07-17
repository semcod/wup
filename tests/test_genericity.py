"""Tests for language-agnostic deps.json discovery and config-driven docker mapping."""

from __future__ import annotations

from pathlib import Path

from wup.config import validate_config
from wup.dependency_mapper import DependencyMapper
from wup.monitoring_manifest import DockerComposeService, _map_docker_to_wup_service


def _dc(compose: str, container: str = "") -> DockerComposeService:
    return DockerComposeService(compose_service=compose, container_name=container)


# --- deps.json genericity -------------------------------------------------

def test_express_ts_endpoints_discovered(tmp_path: Path) -> None:
    """A TypeScript Express project yields a non-empty deps map (regression: rglob brace bug)."""
    svc = tmp_path / "services" / "users"
    svc.mkdir(parents=True)
    (svc / "routes.ts").write_text('router.get("/api/users", h)\nrouter.post("/api/users", h)\n')

    mapper = DependencyMapper(str(tmp_path))
    result = mapper.build_from_codebase()

    assert mapper._detect_framework() == "express"
    assert "services/users" in result["services"]
    assert "/api/users" in result["services"]["services/users"]["endpoints"]


def test_infer_service_uses_services_dir(tmp_path: Path) -> None:
    mapper = DependencyMapper(str(tmp_path))
    assert mapper._infer_service("services/payments/handler.ts") == "services/payments"


def test_to_dict_handles_service_without_endpoints(tmp_path: Path) -> None:
    """Services with files but no endpoints must not corrupt the map (regression: fragile zip)."""
    mapper = DependencyMapper(str(tmp_path))
    mapper.service_to_files["orphan"].add("a.py")
    mapper.service_to_endpoints["web"].append("/x")

    d = mapper.to_dict()
    assert d["services"]["orphan"]["files"] == ["a.py"]
    assert d["services"]["orphan"]["endpoints"] == []
    assert d["services"]["web"]["endpoints"] == ["/x"]


# --- config-driven docker mapping ----------------------------------------

def test_docker_map_default_is_generic() -> None:
    """Without a profile, project-specific fleet literals do not auto-map."""
    services = ["backend", "frontend", "payments"]
    # 'connect-scenario' carries no generic token for these services -> unmapped.
    assert _map_docker_to_wup_service(_dc("connect-scenario"), services) is None


def test_docker_map_connect_profile_opt_in() -> None:
    services = ["backend", "frontend"]
    assert _map_docker_to_wup_service(_dc("connect-scenario"), services, profile="connect") == "backend"


def test_docker_map_user_rules() -> None:
    services = ["payments", "web"]
    got = _map_docker_to_wup_service(_dc("stripe-worker"), services, user_map={"stripe": "payments"})
    assert got == "payments"


def test_docker_map_generic_token_match() -> None:
    services = ["payments", "web"]
    assert _map_docker_to_wup_service(_dc("payments-api"), services) == "payments"


def test_config_roundtrips_docker_service_map() -> None:
    raw = {
        "project": {"name": "p"},
        "testql": {
            "docker_service_map": {"stripe": "payments"},
            "service_map_profile": "connect",
        },
    }
    cfg = validate_config(raw)
    assert cfg.testql.docker_service_map == {"stripe": "payments"}
    assert cfg.testql.service_map_profile == "connect"
