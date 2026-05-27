"""Build and patch the auto-generated ``monitoring:`` block in wup.yaml."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

from .models.config import WupConfig
from .testql_monitor import ProbeTarget, TestQLMonitor

MANIFEST_BEGIN = "# BEGIN WUP MONITORING MANIFEST (auto-generated — do not edit; run: wup sync-testql --write)"
MANIFEST_END = "# END WUP MONITORING MANIFEST"


@dataclass
class DockerComposeService:
    compose_service: str
    container_name: str = ""
    image: str = ""
    host_ports: List[str] = field(default_factory=list)
    profiles: List[str] = field(default_factory=list)
    healthcheck_test: str = ""
    source_file: str = ""


def _parse_port_mapping(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, (int, str)):
        return [str(raw)]
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return []


def _load_compose_yaml(compose_path: Path) -> Optional[Dict[str, Any]]:
    """Load and validate a docker-compose YAML file."""
    try:
        compose_data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(compose_data, dict):
        return None
    services = compose_data.get("services") or {}
    if not isinstance(services, dict):
        return None
    return services


def _extract_healthcheck_test(spec: Dict[str, Any]) -> str:
    """Extract healthcheck test command from service spec."""
    hc = spec.get("healthcheck") or {}
    if not isinstance(hc, dict) or not hc.get("test"):
        return ""
    test_parts = hc["test"]
    if isinstance(test_parts, list):
        return " ".join(str(p) for p in test_parts)
    return str(test_parts)


def _extract_service_from_spec(
    name: str, spec: Dict[str, Any], source_file: str
) -> Optional[DockerComposeService]:
    """Build a DockerComposeService from compose spec."""
    if not isinstance(spec, dict):
        return None
    profiles = spec.get("profiles") or []
    if isinstance(profiles, str):
        profiles = [profiles]
    return DockerComposeService(
        compose_service=name,
        container_name=str(spec.get("container_name") or ""),
        image=str(spec.get("image") or ""),
        host_ports=_parse_port_mapping(spec.get("ports")),
        profiles=[str(p) for p in profiles],
        healthcheck_test=_extract_healthcheck_test(spec),
        source_file=source_file,
    )


def discover_docker_compose_services(project_root: Path) -> List[DockerComposeService]:
    """Parse docker-compose*.yml service definitions under project root."""
    patterns = ["docker-compose.yml", "docker-compose.*.yml", "docker-compose.*.yaml"]
    seen: set[str] = set()
    discovered_services: List[DockerComposeService] = []

    for pattern in patterns:
        for compose_path in sorted(project_root.glob(pattern)):
            key = str(compose_path.resolve())
            if key in seen:
                continue
            seen.add(key)
            compose_services = _load_compose_yaml(compose_path)
            if compose_services is None:
                continue
            for name, spec in compose_services.items():
                discovered_svc = _extract_service_from_spec(name, spec, compose_path.name)
                if discovered_svc is not None:
                    discovered_services.append(discovered_svc)
    return discovered_services


def _host_port_from_mapping(mapping: str) -> Optional[int]:
    """Extract host port from '8100:8100' or '8100:80'."""
    text = mapping.strip().strip("'\"")
    if ":" not in text:
        return None
    host = text.split(":")[0]
    try:
        return int(host)
    except ValueError:
        return None


def _map_docker_to_wup_service(
    docker: DockerComposeService,
    wup_services: Sequence[str],
) -> Optional[str]:
    name = docker.compose_service.lower()
    container = docker.container_name.lower()

    rules = [
        (lambda: "firmware" in name or "firmware" in container, "firmware"),
        (lambda: name == "frontend" or "frontend" in container, "frontend"),
        (lambda: name == "backend" or container == "identification-backend", "backend"),
        (lambda: name.endswith("-backend") and "connect" in name, name.replace("-backend", "")),
    ]
    for predicate, target in rules:
        if predicate() and target in wup_services:
            return target

    for svc in wup_services:
        token = svc.lower().replace("_", "-")
        if token in name or token in container:
            return svc
    return None


def _probe_row(probe: ProbeTarget) -> Dict[str, Any]:
    return {
        "url": probe.url,
        "method": probe.method,
        "expected_status": probe.expected_status,
        "source": probe.source or "discovered",
    }


def _build_wup_service_dicts(config: WupConfig) -> Dict[str, Dict[str, Any]]:
    """Initialize per-service manifest buckets."""
    return {
        name: {
            "wup_paths": list(svc.paths),
            "docker": [],
            "live_probes": [],
            "testql_dry_run_scenarios": [],
        }
        for name, svc in {s.name: s for s in config.services}.items()
    }


def _build_docker_rows(
    docker_all: List[DockerComposeService],
    wup_names: List[str],
    by_wup: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Group docker-compose rows under WUP services; return unmapped leftovers."""
    unmapped: List[Dict[str, Any]] = []
    for d in docker_all:
        row = {
            "compose_service": d.compose_service,
            "container_name": d.container_name or "(default)",
            "host_ports": d.host_ports,
            "profiles": d.profiles,
            "compose_file": d.source_file,
        }
        if d.healthcheck_test:
            row["compose_healthcheck"] = d.healthcheck_test

        mapped = _map_docker_to_wup_service(d, wup_names)
        if mapped:
            by_wup[mapped]["docker"].append(row)
        else:
            unmapped.append(row)
    return unmapped


def _build_scenario_rows(
    monitor: TestQLMonitor,
    project_root: Path,
    wup_names: List[str],
    by_wup: Dict[str, Dict[str, Any]],
) -> None:
    """Attach scenario file paths to the matching WUP service entries."""
    if not monitor.discovery.scenarios_dir.exists():
        return
    for scenario in monitor.discovery.discover_scenarios():
        rel = str(scenario.relative_to(project_root))
        tokens = scenario.stem.lower()
        for svc_name in wup_names:
            token = svc_name.lower().replace("_", "-")
            if token in tokens:
                by_wup[svc_name]["testql_dry_run_scenarios"].append(rel)


def _artifact_row(repo_path: Path, artifact: str) -> Dict[str, Any]:
    artifact_path = Path(artifact)
    if not artifact_path.is_absolute():
        artifact_path = repo_path / artifact_path
    exists = artifact_path.exists()
    row: Dict[str, Any] = {
        "path": str(artifact_path),
        "exists": exists,
    }
    if exists:
        try:
            row["size_bytes"] = artifact_path.stat().st_size
        except OSError:
            pass
    return row


def _semcod_tool_row(name: str, tool: Any) -> Dict[str, Any]:
    repo_path = Path(tool.repo_path).expanduser() if tool.repo_path else Path()
    repo_exists = bool(tool.repo_path) and repo_path.exists()
    return {
        "enabled": bool(tool.enabled),
        "purpose": tool.purpose,
        "repo_path": str(repo_path) if tool.repo_path else "",
        "repo_exists": repo_exists,
        "commands": list(tool.commands),
        "artifacts": [_artifact_row(repo_path, artifact) for artifact in tool.artifacts],
        "status": "ready" if bool(tool.enabled) and repo_exists else "missing_or_disabled",
    }


def discover_semcod_tools(config: WupConfig) -> Dict[str, Any]:
    """Summarize optional deta/regres/regix integrations for monitoring audit."""
    semcod = getattr(config, "semcod_tools", None)
    if not semcod or not getattr(semcod, "enabled", False):
        return {"enabled": False, "tools": {}}

    tools = {
        name: _semcod_tool_row(name, tool)
        for name, tool in sorted((semcod.tools or {}).items())
    }
    ready = [name for name, info in tools.items() if info.get("status") == "ready"]
    return {
        "enabled": True,
        "ready_count": len(ready),
        "tools": tools,
        "notes": (
            "WUP records these Semcod tools in the monitoring manifest for infra audit. "
            "Commands are not auto-run during file-change probes."
        ),
    }


def build_monitoring_manifest(project_root: Path, config: WupConfig) -> Dict[str, Any]:
    """Assemble full monitoring manifest for wup.yaml (documentation + audit)."""
    monitor = TestQLMonitor(project_root, config)
    wup_names = [s.name for s in config.services]
    docker_all = discover_docker_compose_services(project_root)

    by_wup = _build_wup_service_dicts(config)
    unmapped_docker = _build_docker_rows(docker_all, wup_names, by_wup)

    # Live HTTP probes (exactly what WUP will call)
    for svc_name in wup_names:
        probes = monitor.probes_for_service(svc_name)
        by_wup[svc_name]["live_probes"] = [_probe_row(p) for p in probes]

    _build_scenario_rows(monitor, project_root, wup_names, by_wup)

    tq = config.testql
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "wup sync-testql --write (or wup watch startup)",
        "how_to_refresh": "wup sync-testql . --write",
        "probe_interval_s": int(tq.probe_interval_s or 0),
        "health_scenario": tq.health_scenario or "",
        "base_url": monitor._resolve_base_url() or "(set testql.base_url or WUP_BASE_URL)",
        "endpoint_discovery": bool(tq.endpoint_discovery),
        "scenario_dir": str(tq.scenario_dir),
        "service_map_globs": list(tq.service_map_globs or []),
        "docker_compose_files": sorted({d.source_file for d in docker_all}),
        "semcod_tools": discover_semcod_tools(config),
        "wup_services": by_wup,
        "docker_not_mapped_to_wup": unmapped_docker,
        "troubleshooting": {
            "probe_failed_check": [
                "Czy kontener z sekcji docker jest uruchomiony (docker ps)?",
                "Czy host_ports mapuje na URL w live_probes (np. 8100 vs 8202)?",
                "Czy błąd dotyczy proxy frontendu (/firmware na :8100) vs bezpośredniego :8202?",
                "Czy endpoint jest w live_probes — jeśli nie, uruchom: wup sync-testql . --write",
            ],
            "config_vs_runtime": (
                "Pole live_probes to faktyczne żądania HTTP WUP. "
                "Jeśli endpointu tu nie ma, WUP go nie sprawdza — to błąd konfiguracji, nie aplikacji."
            ),
        },
    }


def manifest_to_yaml_block(manifest: Dict[str, Any]) -> str:
    body = yaml.safe_dump(
        {"monitoring": manifest},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).rstrip()
    return f"{MANIFEST_BEGIN}\n{body}\n{MANIFEST_END}\n"


def patch_wup_yaml_monitoring(config_path: Path, manifest: Dict[str, Any]) -> None:
    """Insert or replace the auto-generated monitoring block in wup.yaml."""
    block = manifest_to_yaml_block(manifest)
    path = Path(config_path)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = ""

    pattern = re.compile(
        re.escape(MANIFEST_BEGIN) + r".*?" + re.escape(MANIFEST_END) + r"\n?",
        re.DOTALL,
    )
    if pattern.search(text):
        text = pattern.sub(block, text)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n" + block

    path.write_text(text, encoding="utf-8")


def load_monitoring_manifest_from_yaml(config_path: Path) -> Optional[Dict[str, Any]]:
    """Read monitoring section from wup.yaml if present."""
    if not config_path.exists():
        return None
    text = config_path.read_text(encoding="utf-8")

    block_match = re.search(
        re.escape(MANIFEST_BEGIN) + r"\nmonitoring:\n(.*?)\n" + re.escape(MANIFEST_END),
        text,
        re.DOTALL,
    )
    if block_match:
        try:
            parsed = yaml.safe_load("monitoring:\n" + block_match.group(1))
            if isinstance(parsed, dict):
                monitoring = parsed.get("monitoring")
                if isinstance(monitoring, dict):
                    return monitoring
        except yaml.YAMLError:
            pass

    try:
        yaml_data = yaml.safe_load(text)
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(yaml_data, dict):
        return None
    monitoring = yaml_data.get("monitoring")
    return monitoring if isinstance(monitoring, dict) else None


def format_manifest_summary(manifest: Dict[str, Any]) -> str:
    """Short human-readable summary for CLI."""
    lines: List[str] = []
    lines.append(f"generated: {manifest.get('generated_at', '?')}")
    lines.append(f"probe every: {manifest.get('probe_interval_s', 0)}s")
    if manifest.get("health_scenario"):
        lines.append(f"fleet scenario: {manifest['health_scenario']}")

    wup_services = manifest.get("wup_services") or {}
    for svc, info in sorted(wup_services.items()):
        probes = info.get("live_probes") or []
        dockers = info.get("docker") or []
        lines.append(f"  [cyan]{svc}[/cyan]: {len(probes)} HTTP probe(s), {len(dockers)} docker(s)")
        for probe in probes[:6]:
            lines.append(f"    • {probe.get('method', 'GET')} {probe.get('url')}  ({probe.get('source', '?')})")
        if len(probes) > 6:
            lines.append(f"    … +{len(probes) - 6} more")

    unmapped = manifest.get("docker_not_mapped_to_wup") or []
    if unmapped:
        lines.append(f"  [yellow]docker not mapped to wup:[/yellow] {len(unmapped)} service(s)")

    semcod = manifest.get("semcod_tools") or {}
    if semcod.get("enabled"):
        tools = semcod.get("tools") or {}
        ready = semcod.get("ready_count", 0)
        lines.append(f"  [cyan]semcod tools[/cyan]: {ready}/{len(tools)} ready")
        for name, info in sorted(tools.items()):
            marker = "ready" if info.get("status") == "ready" else "missing/disabled"
            lines.append(f"    {name}: {marker} ({info.get('repo_path', '')})")
    return "\n".join(lines)
