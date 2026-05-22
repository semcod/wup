"""Live HTTP monitoring helpers for WUP + TestQL integration."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib import error, request
from urllib.parse import urlparse

import yaml

from .models.config import ServiceConfig, WupConfig
from .testql_discovery import TestQLEndpointDiscovery

_API_LINE = re.compile(
    r"^\s*(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s*,\s*([^\s,]+)(?:\s*,\s*(\d+))?",
    re.MULTILINE,
)
_HEALTH_HINT = re.compile(
    r"(/health|/healthz|/ready|/live|/status|/openapi\.json|/execution/status|/execution/logs)",
    re.IGNORECASE,
)
# Connect module APIs live on :8103+ — not valid health probes on frontend proxy :8100
_CONNECT_API_PREFIXES = (
    "/api/id",
    "/api/manager",
    "/api/scenario",
    "/api/test",
    "/api/template",
    "/api/cql",
    "/api/v1/data",
    "/api/v2/menu",
)
_PATH_TOKEN_BLOCKLIST = frozenset({"api", "app", "src", "lib", "bin", "dist", "out"})


@dataclass(frozen=True)
class ProbeTarget:
    """Single HTTP probe derived from TestQL scenarios or service maps."""

    url: str
    method: str = "GET"
    expected_status: int = 200
    source: str = ""

    def probe(self, timeout_s: float = 10.0) -> Tuple[bool, str]:
        """Execute probe; return (ok, detail message)."""
        req = request.Request(self.url, method=self.method.upper())
        try:
            with request.urlopen(req, timeout=timeout_s) as resp:
                if resp.status == self.expected_status:
                    return True, f"HTTP {resp.status}"
                return False, f"HTTP {resp.status} (expected {self.expected_status})"
        except error.HTTPError as exc:
            if exc.code == self.expected_status:
                return True, f"HTTP {exc.code}"
            return False, f"HTTP {exc.code} (expected {self.expected_status})"
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)


def _parse_api_lines(content: str, source: str) -> List[ProbeTarget]:
    probes: List[ProbeTarget] = []
    for method, target, status_text in _API_LINE.findall(content):
        expected = int(status_text) if status_text else 200
        probes.append(
            ProbeTarget(
                url=target.strip(),
                method=method.upper(),
                expected_status=expected,
                source=source,
            )
        )
    return probes


def parse_scenario_probes(scenario_path: Path) -> List[ProbeTarget]:
    """Extract API probe rows from a TestQL TOON scenario file."""
    try:
        content = scenario_path.read_text(encoding="utf-8")
    except OSError:
        return []
    return _parse_api_lines(content, source=str(scenario_path))


def _extract_base_url(data: Dict[str, Any]) -> str:
    """Read base_url / api_base_url from service map YAML header."""
    service = data.get("service")
    if isinstance(service, dict):
        return str(service.get("base_url") or service.get("api_base_url") or "").rstrip("/")
    return ""


def _parse_endpoint_row(row: Any, base_url: str, source: str) -> Optional[ProbeTarget]:
    """Convert a single endpoints list entry into a ProbeTarget."""
    if not isinstance(row, dict):
        return None
    path = str(row.get("path") or "").strip()
    if not path:
        return None
    method = str(row.get("method") or "GET").upper()
    expected = int(row.get("expected_status") or 200)
    url = path if path.startswith("http") else f"{base_url}{path}" if base_url else path
    return ProbeTarget(url=url, method=method, expected_status=expected, source=source)


def parse_service_map_probes(map_path: Path) -> List[ProbeTarget]:
    """Extract probes from c2004-style service map YAML (endpoints: list)."""
    try:
        data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []

    if not isinstance(data, dict):
        return []

    base_url = _extract_base_url(data)
    source = str(map_path)
    probes: List[ProbeTarget] = []
    for row in data.get("endpoints") or []:
        probe = _parse_endpoint_row(row, base_url, source)
        if probe is not None:
            probes.append(probe)
    return probes


def _connect_module_api_on_frontend_proxy(probe: ProbeTarget) -> bool:
    """True when a connect-* API path would be wrongly probed via :8100."""
    if not probe.url.startswith("http"):
        return False
    parsed = urlparse(probe.url)
    if parsed.port not in (None, 8100):
        return False
    path = (parsed.path or "").lower()
    return any(path.startswith(prefix) for prefix in _CONNECT_API_PREFIXES)


def _firmware_plugin_probe_without_runtime(probe: ProbeTarget) -> bool:
    """Plugin health on :8202 requires loaded plugins — skip for bare simulator live probes."""
    if not probe.url.startswith("http"):
        return False
    parsed = urlparse(probe.url)
    if parsed.port != 8202:
        return False
    path = (parsed.path or "").lower()
    return "/api/v1/plugins/" in path and path.endswith("/health")


def is_monitoring_probe(probe: ProbeTarget) -> bool:
    """True when this endpoint should be used for live service health checks."""
    if _connect_module_api_on_frontend_proxy(probe):
        return False
    if _firmware_plugin_probe_without_runtime(probe):
        return False
    if probe.url.startswith("http"):
        path = urlparse(probe.url).path or probe.url
    else:
        path = probe.url
    path_lower = path.lower()
    if any(path_lower.startswith(prefix) for prefix in _CONNECT_API_PREFIXES):
        return False
    if _HEALTH_HINT.search(path):
        return True
    # Short GET smoke paths (/, /health) without heavy write APIs
    return probe.method == "GET" and path in {"/", "/health", "/api/v1/health", "/api/v3/health"}


def _service_path_patterns(services: Sequence[ServiceConfig]) -> Dict[str, List[str]]:
    patterns: Dict[str, List[str]] = {}
    for svc in services:
        tokens: List[str] = [svc.name.lower().replace("_", "-")]
        for raw in svc.paths:
            part = raw.lower().replace("**", "").replace("*", "").strip("/")
            if part:
                tokens.append(part.split("/")[0])
        patterns[svc.name] = sorted(set(t for t in tokens if t))
    return patterns


def _find_service_by_name(services: Sequence[ServiceConfig], name: str) -> Optional[str]:
    """Find a service by case-insensitive name match."""
    name_lower = name.lower()
    for svc in services:
        if svc.name.lower() == name_lower:
            return svc.name
    return None


def _find_service_by_token(services: Sequence[ServiceConfig], token: str) -> Optional[str]:
    """Find a service by checking if token is in its name."""
    token_lower = token.lower()
    for svc in services:
        if token_lower in svc.name.lower():
            return svc.name
    return None


def _assign_by_port_8101(services: Sequence[ServiceConfig]) -> Optional[str]:
    """Assign probe to backend service for port 8101."""
    return _find_service_by_name(services, "backend")


def _assign_by_port_8202(services: Sequence[ServiceConfig]) -> Optional[str]:
    """Assign probe to firmware service for port 8202."""
    return _find_service_by_token(services, "firmware")


def _assign_by_port_8100(
    services: Sequence[ServiceConfig], path_lower: str
) -> Optional[str]:
    """Assign probe for port 8100 (frontend proxy)."""
    if path_lower.startswith("/firmware"):
        return _find_service_by_token(services, "firmware")
    return _find_service_by_name(services, "frontend")


def _assign_by_connect_backend(
    services: Sequence[ServiceConfig], path_lower: str
) -> Optional[str]:
    """Assign probe to connect-* backend services."""
    for svc in services:
        token = svc.name.lower().replace("_", "-")
        if token.startswith("connect-") and token.replace("connect-", "") in path_lower:
            return svc.name
    return None


def _assign_http_probe(
    probe: ProbeTarget, services: Sequence[ServiceConfig], path_lower: str
) -> Optional[str]:
    """Map an HTTP probe to a service based on port and path."""
    parsed = urlparse(probe.url)
    port = parsed.port

    if port == 8101:
        return _assign_by_port_8101(services)
    if port == 8202:
        return _assign_by_port_8202(services)
    if port == 8100:
        return _assign_by_port_8100(services, path_lower)
    
    return _assign_by_connect_backend(services, path_lower)


def _assign_by_longest_token(
    path_lower: str, services: Sequence[ServiceConfig]
) -> Optional[str]:
    """Match path to service with the longest token match."""
    best: Optional[str] = None
    best_len = -1
    for svc in services:
        for token in _service_path_patterns([svc]).get(svc.name, []):
            if len(token) < 4 or token in _PATH_TOKEN_BLOCKLIST:
                continue
            if token in path_lower and len(token) > best_len:
                best = svc.name
                best_len = len(token)
    return best


def _assign_by_path_prefix(
    path_lower: str, services: Sequence[ServiceConfig]
) -> Optional[str]:
    """Fallback mapping based on known path prefixes."""
    if path_lower.startswith("/connect-"):
        for svc in services:
            if svc.name.lower() == "frontend":
                return svc.name
    if path_lower.startswith("/firmware"):
        for svc in services:
            if "firmware" in svc.name.lower():
                return svc.name
    if path_lower.startswith("/api/v3"):
        for svc in services:
            if svc.name.lower() in {"backend", "api"}:
                return svc.name
    if path_lower in {"/", "/index.html"}:
        for svc in services:
            if svc.name.lower() == "frontend":
                return svc.name
    return None


def assign_probe_to_service(probe: ProbeTarget, services: Sequence[ServiceConfig]) -> Optional[str]:
    """Map a probe URL/path to a configured WUP service name."""
    path = urlparse(probe.url).path if probe.url.startswith("http") else probe.url
    path_lower = path.lower()

    if probe.url.startswith("http"):
        result = _assign_http_probe(probe, services, path_lower)
        if result:
            return result
        return None

    best = _assign_by_longest_token(path_lower, services)
    if best:
        return best

    return _assign_by_path_prefix(path_lower, services)


class _ProbeAccumulator:
    """Deduplicated probe collector for discover_probes_by_service."""

    def __init__(self, services: Sequence[ServiceConfig]):
        self.by_service: Dict[str, List[ProbeTarget]] = {
            svc.name: [] for svc in services
        }
        self._seen: Dict[str, set] = {name: set() for name in self.by_service}

    def add(self, service: str, probe: ProbeTarget) -> None:
        if service not in self.by_service:
            self.by_service[service] = []
            self._seen[service] = set()
        key = f"{probe.method}:{probe.url}"
        if key in self._seen[service]:
            return
        self._seen[service].add(key)
        self.by_service[service].append(probe)


class TestQLMonitor:
    """Build and run live probes from TestQL scenarios + WUP config."""

    __test__ = False

    def __init__(self, project_root: Path, config: WupConfig):
        self.project_root = project_root
        self.config = config
        tq = config.testql
        self.scenarios_dir = project_root / (tq.scenario_dir or "testql-scenarios")
        self.discovery = TestQLEndpointDiscovery(str(self.scenarios_dir))

    def _service_map_paths(self) -> List[Path]:
        globs = self.config.testql.service_map_globs or []
        paths: List[Path] = []
        for pattern in globs:
            paths.extend(sorted(self.project_root.glob(pattern)))
        return paths

    def _add_config_endpoints(
        self,
        accumulator: "_ProbeAccumulator",
    ) -> None:
        """Add config-declared endpoints (paths or full URLs) per-service base URL."""
        for svc_name, paths in (self.config.testql.endpoints_by_service or {}).items():
            base = self._resolve_base_url_for_service(svc_name)
            for path in paths:
                url = self._probeable_url(path, base)
                if not url:
                    continue
                probe = ProbeTarget(url=url, source="wup.yaml:endpoints_by_service")
                if is_monitoring_probe(probe):
                    accumulator.add(svc_name, probe)

        for path in self.config.testql.explicit_endpoints or []:
            probe = ProbeTarget(url=path, source="wup.yaml:explicit_endpoints")
            assigned = assign_probe_to_service(probe, self.config.services)
            if not assigned:
                continue
            base = self._resolve_base_url_for_service(assigned)
            url = self._probeable_url(path, base)
            if not url:
                continue
            probe = ProbeTarget(url=url, source="wup.yaml:explicit_endpoints")
            if is_monitoring_probe(probe):
                accumulator.add(assigned, probe)

    def _add_scenario_probes(
        self,
        accumulator: "_ProbeAccumulator",
    ) -> None:
        """Add TestQL scenario probes mapped to services."""
        for scenario in self.discovery.discover_scenarios():
            for probe in parse_scenario_probes(scenario):
                if not is_monitoring_probe(probe):
                    continue
                assigned = assign_probe_to_service(probe, self.config.services)
                if assigned:
                    accumulator.add(assigned, probe)

    def _add_service_map_probes(
        self,
        accumulator: "_ProbeAccumulator",
    ) -> None:
        """Add service-map TOON/YAML probes mapped to services."""
        for map_path in self._service_map_paths():
            for probe in parse_service_map_probes(map_path):
                if not is_monitoring_probe(probe):
                    continue
                assigned = assign_probe_to_service(probe, self.config.services)
                if assigned:
                    accumulator.add(assigned, probe)

    def discover_probes_by_service(self) -> Dict[str, List[ProbeTarget]]:
        """Discover monitoring probes grouped by WUP service name."""
        accumulator = _ProbeAccumulator(self.config.services)

        self._add_config_endpoints(accumulator)

        if self.config.testql.endpoint_discovery:
            self._add_scenario_probes(accumulator)
            self._add_service_map_probes(accumulator)

        return accumulator.by_service

    def _resolve_base_url_for_service(self, service: str) -> str:
        tq = self.config.testql
        overrides = getattr(tq, "service_base_urls", None) or {}
        if isinstance(overrides, dict):
            override = (overrides.get(service) or "").strip().rstrip("/")
            if override:
                return override
        if service.lower() in {"backend", "api"}:
            api_base = (getattr(tq, "api_base_url", None) or "").strip().rstrip("/")
            if api_base:
                return api_base
        return self._resolve_base_url()

    def _probeable_url(self, path: str, base: str) -> Optional[str]:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not base:
            return None
        return self._join_base(base, path)

    def probes_for_service(self, service: str, extra_paths: Iterable[str] = ()) -> List[ProbeTarget]:
        """Merged probe list for one service (discovery + config + caller extras)."""
        discovered = self.discover_probes_by_service().get(service, [])
        base = self._resolve_base_url_for_service(service)
        merged: List[ProbeTarget] = list(discovered)
        keys = {f"{p.method}:{p.url}" for p in merged}

        for path in extra_paths:
            url = self._probeable_url(path, base)
            if not url:
                continue
            probe = ProbeTarget(url=url, source="runtime")
            if not is_monitoring_probe(probe):
                continue
            key = f"{probe.method}:{probe.url}"
            if key in keys:
                continue
            keys.add(key)
            merged.append(probe)

        return [p for p in merged if p.url.startswith("http://") or p.url.startswith("https://")]

    @staticmethod
    def _sort_probes_for_live(probes: Sequence[ProbeTarget]) -> List[ProbeTarget]:
        """Prefer wup.yaml endpoints before scenario discovery for pass/fail."""

        def rank(probe: ProbeTarget) -> Tuple[int, str]:
            source = probe.source or ""
            if source.startswith("wup.yaml:endpoints_by_service"):
                return (0, probe.url)
            if source.startswith("wup.yaml:explicit_endpoints"):
                return (1, probe.url)
            return (2, probe.url)

        return sorted(probes, key=rank)

    def run_probes(
        self,
        service: str,
        probes: Sequence[ProbeTarget],
        *,
        max_count: int,
        timeout_s: float,
    ) -> Tuple[bool, str]:
        """Probe up to max_count targets; return overall pass and failure reason."""
        if not probes:
            return True, ""

        failed: List[str] = []
        ordered = self._sort_probes_for_live(probes)
        for probe in ordered[:max_count]:
            ok, detail = probe.probe(timeout_s=timeout_s)
            if ok:
                continue
            failed.append(f"{probe.method} {probe.url} → {detail}")

        if failed:
            return False, "; ".join(failed[:3])
        return True, "live probes passed"

    def suggested_endpoints_by_service(self) -> Dict[str, List[str]]:
        """Paths/URLs to merge into wup.yaml (for `wup sync-testql`)."""
        result: Dict[str, List[str]] = {}
        for service, probes in self.discover_probes_by_service().items():
            paths: List[str] = []
            for probe in probes:
                if probe.url.startswith("http"):
                    paths.append(probe.url)
                else:
                    paths.append(probe.url)
            if paths:
                result[service] = sorted(set(paths))
        return result

    def _resolve_base_url(self) -> str:
        import os

        base = (self.config.testql.base_url or "").strip().rstrip("/")
        if base:
            return base
        env_key = (self.config.testql.base_url_env or "WUP_BASE_URL").strip()
        env_url = os.getenv(env_key, "").strip().rstrip("/")
        return env_url

    @staticmethod
    def _join_base(base: str, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not base:
            return path
        if path.startswith("/"):
            return f"{base}{path}"
        return f"{base}/{path}"
