"""
Pluggable endpoint-discovery adapters.

Each adapter knows how to (a) detect whether a project uses its ecosystem and
(b) extract HTTP endpoints from the source. `DependencyMapper` delegates to the
registry here so `deps.json` is language-agnostic: adding support for a new
framework means adding an adapter, not editing the mapper.

Adapters are deliberately regex-based (no imports of the target frameworks) so
discovery stays fast and dependency-free.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

# Source extensions grouped by ecosystem.
PY_EXTENSIONS = (".py",)
JS_EXTENSIONS = (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
GO_EXTENSIONS = (".go",)
OPENAPI_EXTENSIONS = (".yaml", ".yml", ".json")
ALL_SOURCE_EXTENSIONS = PY_EXTENSIONS + JS_EXTENSIONS + GO_EXTENSIONS


@dataclass
class Endpoint:
    """A discovered HTTP endpoint."""
    method: str
    path: str
    file: str
    framework: str

    def as_dict(self) -> Dict[str, str]:
        return {"method": self.method, "path": self.path, "file": self.file, "framework": self.framework}


class SourceIndex:
    """
    Reads and caches project source files once, so every adapter's detect() and
    scan() reuse the same content instead of re-walking the tree.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self._cache: Dict[str, List[Tuple[str, str]]] = {}

    def _read_ext(self, ext: str) -> List[Tuple[str, str]]:
        if ext in self._cache:
            return self._cache[ext]
        items: List[Tuple[str, str]] = []
        if self.project_root.exists():
            for path in self.project_root.rglob(f"*{ext}"):
                if not path.is_file():
                    continue
                try:
                    content = path.read_text()
                except (UnicodeDecodeError, PermissionError, OSError):
                    continue
                items.append((str(path.relative_to(self.project_root)), content))
        self._cache[ext] = items
        return items

    def files(self, extensions: Tuple[str, ...]) -> Iterator[Tuple[str, str]]:
        """Yield (relative_path, content) for every file with one of the extensions."""
        for ext in extensions:
            yield from self._read_ext(ext)

    def contains(self, marker: str, extensions: Tuple[str, ...]) -> bool:
        """True if any file with the given extensions contains the marker string."""
        return any(marker in content for _, content in self.files(extensions))


class DiscoveryAdapter:
    """Base adapter. Subclasses set name/extensions/markers or override scan()."""

    name: str = "generic"
    extensions: Tuple[str, ...] = ()
    detect_markers: Tuple[str, ...] = ()
    # (compiled regex, method-group index or None, path-group index)
    route_patterns: Tuple[Tuple[re.Pattern, Optional[int], int], ...] = ()
    default_method: str = "GET"
    # When True, a matching route pattern alone counts as detection (for
    # ecosystems whose route syntax is distinctive enough, e.g. Express
    # `router.get(`). Kept False where syntax is too generic (Hono, Fastify's
    # `url:`), which rely on import markers instead to avoid false positives.
    detect_via_routes: bool = False

    def detect(self, index: SourceIndex) -> bool:
        if any(index.contains(m, self.extensions) for m in self.detect_markers):
            return True
        if self.detect_via_routes:
            for _, content in index.files(self.extensions):
                if any(p.search(content) for p, _, _ in self.route_patterns):
                    return True
        return False

    def scan(self, index: SourceIndex) -> List[Endpoint]:
        endpoints: List[Endpoint] = []
        for rel_path, content in index.files(self.extensions):
            for pattern, method_group, path_group in self.route_patterns:
                for match in pattern.finditer(content):
                    method = match.group(method_group).upper() if method_group else self.default_method
                    endpoints.append(Endpoint(method, match.group(path_group), rel_path, self.name))
        return endpoints


# --- concrete adapters ----------------------------------------------------

class FastAPIAdapter(DiscoveryAdapter):
    name = "fastapi"
    extensions = PY_EXTENSIONS
    detect_markers = ("FastAPI", "APIRouter", "from fastapi")
    detect_via_routes = True
    route_patterns = (
        (re.compile(r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'), 1, 2),
    )


class FlaskAdapter(DiscoveryAdapter):
    name = "flask"
    extensions = PY_EXTENSIONS
    detect_markers = ("from flask", "Flask(", "Blueprint(")
    detect_via_routes = True
    route_patterns = (
        (re.compile(r'@(?:app|bp)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'), 1, 2),
        (re.compile(r'@(?:app|bp)\.route\s*\(\s*["\']([^"\']+)["\']'), None, 1),
    )


class DjangoAdapter(DiscoveryAdapter):
    name = "django"
    extensions = PY_EXTENSIONS
    detect_markers = ("urlpatterns", "from django.urls")
    route_patterns = (
        (re.compile(r'(?:^|\W)(?:path|re_path|url)\s*\(\s*["\']([^"\']*)["\']'), None, 1),
    )


class ExpressAdapter(DiscoveryAdapter):
    name = "express"
    extensions = JS_EXTENSIONS
    detect_markers = ("express()", "require('express')", 'require("express")', "from 'express'", 'from "express"')
    detect_via_routes = True
    route_patterns = (
        (re.compile(r'(?:app|router)\.(get|post|put|delete|patch|all)\s*\(\s*["\'`]([^"\'`]+)["\'`]'), 1, 2),
    )


class FastifyAdapter(DiscoveryAdapter):
    name = "fastify"
    extensions = JS_EXTENSIONS
    detect_markers = ("require('fastify')", 'require("fastify")', "from 'fastify'", 'from "fastify"')
    route_patterns = (
        # Fastify instances take arbitrary names (fastify/app/server/f): match any
        # identifier. Safe because this adapter only scans files that import fastify.
        (re.compile(r'\b\w+\.(get|post|put|delete|patch)\s*\(\s*["\'`](/[^"\'`]*)["\'`]'), 1, 2),
        # fastify.route({ method: 'GET', url: '/x' })
        (re.compile(r'url\s*:\s*["\'`](/[^"\'`]*)["\'`]'), None, 1),
    )


class HonoAdapter(DiscoveryAdapter):
    name = "hono"
    extensions = JS_EXTENSIONS
    detect_markers = ("from 'hono'", 'from "hono"', "new Hono(")
    route_patterns = (
        (re.compile(r'\b\w+\.(get|post|put|delete|patch)\s*\(\s*["\'`](/[^"\'`]*)["\'`]'), 1, 2),
    )


class NestJSAdapter(DiscoveryAdapter):
    name = "nestjs"
    extensions = JS_EXTENSIONS
    detect_markers = ("@nestjs/common", "@Controller(")
    route_patterns = (
        (re.compile(r'@(Get|Post|Put|Delete|Patch)\s*\(\s*["\'`]?([^"\'`)]*)["\'`]?\s*\)'), 1, 2),
    )


class GoAdapter(DiscoveryAdapter):
    name = "go"
    extensions = GO_EXTENSIONS
    detect_markers = ("net/http", "gin-gonic/gin", "labstack/echo", "gorilla/mux")
    detect_via_routes = True
    route_patterns = (
        # gin/echo: r.GET("/x", ...), e.POST("/x", ...)
        (re.compile(r'\.\b(GET|POST|PUT|DELETE|PATCH)\s*\(\s*"([^"]+)"'), 1, 2),
        # net/http: http.HandleFunc("/x", ...) / mux.HandleFunc("/x", ...)
        (re.compile(r'\.HandleFunc\s*\(\s*"([^"]+)"'), None, 1),
    )


class OpenAPIAdapter(DiscoveryAdapter):
    """Extract paths from an OpenAPI/Swagger document (yaml or json)."""
    name = "openapi"
    extensions = OPENAPI_EXTENSIONS

    def _load_spec(self, content: str) -> Optional[dict]:
        text = content.lstrip()
        try:
            if text.startswith("{"):
                return json.loads(content)
            import yaml
            data = yaml.safe_load(content)
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def detect(self, index: SourceIndex) -> bool:
        for _, content in index.files(self.extensions):
            spec = self._load_spec(content)
            if spec and ("openapi" in spec or "swagger" in spec) and isinstance(spec.get("paths"), dict):
                return True
        return False

    def scan(self, index: SourceIndex) -> List[Endpoint]:
        endpoints: List[Endpoint] = []
        methods = {"get", "post", "put", "delete", "patch", "head", "options"}
        for rel_path, content in index.files(self.extensions):
            spec = self._load_spec(content)
            if not (spec and isinstance(spec.get("paths"), dict)):
                continue
            for path, ops in spec["paths"].items():
                if not isinstance(ops, dict):
                    continue
                for method in ops:
                    if str(method).lower() in methods:
                        endpoints.append(Endpoint(str(method).upper(), str(path), rel_path, self.name))
        return endpoints


# Order determines which framework wins attribution in auto mode (scanning still
# runs every matching adapter). Marker-specific JS frameworks come before Express,
# whose generic app.get/router.get syntax the others mimic.
ADAPTERS: Tuple[DiscoveryAdapter, ...] = (
    FastAPIAdapter(),
    FlaskAdapter(),
    DjangoAdapter(),
    NestJSAdapter(),
    HonoAdapter(),
    FastifyAdapter(),
    ExpressAdapter(),
    GoAdapter(),
    OpenAPIAdapter(),
)

ADAPTERS_BY_NAME: Dict[str, DiscoveryAdapter] = {a.name: a for a in ADAPTERS}


def detect_frameworks(index: SourceIndex) -> List[str]:
    """Return the names of every adapter whose ecosystem is present."""
    return [a.name for a in ADAPTERS if a.detect(index)]


def discover_endpoints(
    project_root: Path,
    framework: str = "auto",
    index: Optional[SourceIndex] = None,
) -> List[Endpoint]:
    """
    Discover endpoints across all matching adapters.

    framework="auto" runs every adapter that detects its ecosystem; an explicit
    framework name runs just that adapter.
    """
    index = index or SourceIndex(project_root)
    if framework and framework != "auto":
        adapter = ADAPTERS_BY_NAME.get(framework)
        return adapter.scan(index) if adapter else []

    endpoints: List[Endpoint] = []
    for adapter in ADAPTERS:
        if adapter.detect(index):
            endpoints.extend(adapter.scan(index))
    return endpoints
