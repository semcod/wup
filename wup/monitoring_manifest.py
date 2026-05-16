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


def discover_docker_compose_services(project_root: Path) -> List[DockerComposeService]:
    """Parse docker-compose*.yml service definitions under project root."""
    patterns = ["docker-compose.yml", "docker-compose.*.yml", "docker-compose.*.yaml"]
    seen: set[str] = set()
    results: List[DockerComposeService] = []

    for pattern in patterns:
        for compose_path in sorted(project_root.glob(pattern)):
            key = str(compose_path.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                continue
            if not isinstance(data, dict):
                continue

            services = data.get("services") or {}
            if not isinstance(services, dict):
                continue

            for name, spec in services.items():
                if not isinstance(spec, dict):
                    continue
                hc = spec.get("healthcheck") or {}
                hc_test = ""
                if isinstance(hc, dict) and hc.get("test"):
                    parts = hc["test"]
                    if isinstance(parts, list):
                        hc_test = " ".join(str(p) for p in parts)
                    else:
                        hc_test = str(parts)

                profiles = spec.get("profiles") or []
                if isinstance(profiles, str):
                    profiles = [profiles]

                results.append(
                    DockerComposeService(
                        compose_service=name,
                        container_name=str(spec.get("container_name") or ""),
                        image=str(spec.get("image") or ""),
                        host_ports=_parse_port_mapping(spec.get("ports")),
                        profiles=[str(p) for p in profiles],
                        healthcheck_test=hc_test,
                        source_file=compose_path.name,
                    )
                )
    return results


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


def build_monitoring_manifest(project_root: Path, config: WupConfig) -> Dict[str, Any]:
    """Assemble full monitoring manifest for wup.yaml (documentation + audit)."""
    monitor = TestQLMonitor(project_root, config)
    wup_names = [s.name for s in config.services]
    docker_all = discover_docker_compose_services(project_root)

    by_wup: Dict[str, Dict[str, Any]] = {
        name: {
            "wup_paths": [],
            "docker": [],
            "live_probes": [],
            "testql_dry_run_scenarios": [],
        }
        for name in wup_names
    }

    for svc in config.services:
        by_wup[svc.name]["wup_paths"] = list(svc.paths)

    # Docker rows grouped under WUP services (+ unmapped bucket)
    unmapped_docker: List[Dict[str, Any]] = []
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
            unmapped_docker.append(row)

    # Live HTTP probes (exactly what WUP will call)
    for svc_name in wup_names:
        probes = monitor.probes_for_service(svc_name)
        by_wup[svc_name]["live_probes"] = [_probe_row(p) for p in probes]

    # Scenarios used for dry-run quick tests (informational)
    if monitor.discovery.scenarios_dir.exists():
        for scenario in monitor.discovery.discover_scenarios():
            rel = str(scenario.relative_to(project_root))
            tokens = scenario.stem.lower()
            for svc_name in wup_names:
                token = svc_name.lower().replace("_", "-")
                if token in tokens:
                    by_wup[svc_name]["testql_dry_run_scenarios"].append(rel)

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
        data = yaml.safe_load(text)
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    monitoring = data.get("monitoring")
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
    return "\n".join(lines)
