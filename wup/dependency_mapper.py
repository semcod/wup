"""
Dependency Mapper - Maps files to endpoints to services.

This module builds a static dependency map that connects:
- Files → Endpoints
- Endpoints → Services
- Services → Related tests

This enables intelligent testing by only testing related services when files change.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from .testql_discovery import TestQLEndpointDiscovery
from .discovery import SourceIndex, detect_frameworks, discover_endpoints

# Directory names that commonly sit directly above a service/module. Used by
# _infer_service to derive a service name from a file path in a language-agnostic
# way (Python `app/`, Node `services/`, monorepo `packages/`, …).
SERVICE_ROOT_DIRS = (
    "app", "src", "services", "packages", "lib", "modules", "apps", "cmd", "internal", "pkg",
)


class DependencyMapper:
    """Maps project dependencies for intelligent testing."""
    
    def __init__(self, project_root: str):
        """
        Initialize the dependency mapper.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.file_to_endpoints: Dict[str, List[str]] = defaultdict(list)
        self.service_to_endpoints: Dict[str, List[str]] = defaultdict(list)
        self.service_to_files: Dict[str, Set[str]] = defaultdict(set)
        
    def build_from_codebase(self, framework: str = "auto") -> Dict:
        """
        Build dependency map by scanning the codebase.

        Discovery is delegated to pluggable adapters (see ``wup.discovery``), so
        every supported ecosystem — FastAPI, Flask, Django, Express, Fastify,
        Hono, NestJS, Go, OpenAPI — is covered without special-casing here.

        Args:
            framework: ``auto`` (run every adapter that detects its ecosystem)
                or an explicit adapter name.

        Returns:
            Dictionary containing the full dependency map.
        """
        index = SourceIndex(self.project_root)
        for ep in discover_endpoints(self.project_root, framework, index=index):
            service = self._infer_service(ep.file)
            # Membership checks keep the map free of duplicates when several
            # adapters (or HTTP methods) resolve to the same path.
            if ep.file and ep.path not in self.file_to_endpoints[ep.file]:
                self.file_to_endpoints[ep.file].append(ep.path)
            if service:
                if ep.path not in self.service_to_endpoints[service]:
                    self.service_to_endpoints[service].append(ep.path)
                self.service_to_files[service].add(ep.file)

        return self.to_dict()
    
    def _detect_framework(self) -> str:
        """Return the first detected framework/ecosystem, or "generic" if none."""
        detected = detect_frameworks(SourceIndex(self.project_root))
        return detected[0] if detected else "generic"

    def _infer_service(self, file_path: str) -> Optional[str]:
        """
        Infer service name from file path.
        
        Examples:
            app/users/routes.py → "users"
            app/api/v1/devices.py → "api/v1/devices"
            src/components/auth.ts → "components/auth"
        """
        parts = Path(file_path).parts

        # Derive the service from the segment following a known service-root dir
        # (app/, src/, services/, packages/, …) — language-agnostic.
        for root in SERVICE_ROOT_DIRS:
            if root in parts:
                idx = parts.index(root)
                if idx + 1 < len(parts):
                    return "/".join(parts[idx:idx + 2])

        # Fallback: use first two meaningful parts
        if len(parts) >= 2:
            return "/".join(parts[:2])

        return None
    
    def get_endpoints_for_file(self, file_path: str) -> List[str]:
        """Get all endpoints related to a specific file."""
        rel_path = str(Path(file_path).relative_to(self.project_root))
        return self.file_to_endpoints.get(rel_path, [])
    
    def get_endpoints_for_service(self, service: str) -> List[str]:
        """Get all endpoints belonging to a service."""
        return self.service_to_endpoints.get(service, [])
    
    def get_files_for_service(self, service: str) -> Set[str]:
        """Get all files belonging to a service."""
        return self.service_to_files.get(service, set())
    
    def get_service_for_file(self, file_path: str) -> Optional[str]:
        """Get the service name for a specific file."""
        rel_path = str(Path(file_path).relative_to(self.project_root))
        
        for service, files in self.service_to_files.items():
            if rel_path in files:
                return service
        
        return self._infer_service(file_path)
    
    def to_dict(self) -> Dict:
        """Convert the dependency map to a dictionary."""
        services = sorted(set(self.service_to_endpoints) | set(self.service_to_files))
        return {
            "services": {
                service: {
                    "endpoints": self.service_to_endpoints.get(service, []),
                    "files": sorted(self.service_to_files.get(service, set())),
                }
                for service in services
            },
            "files": dict(self.file_to_endpoints),
        }
    
    def save(self, output_path: str = "deps.json"):
        """Save the dependency map to a JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load(self, input_path: str = "deps.json"):
        """Load the dependency map from a JSON file."""
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        # Rebuild mappings
        for service, info in data.get("services", {}).items():
            self.service_to_endpoints[service] = info.get("endpoints", [])
            self.service_to_files[service] = set(info.get("files", []))
        
        self.file_to_endpoints = defaultdict(list, data.get("files", {}))
    
    def build_from_testql_scenarios(self, scenarios_dir: str, testql_bin: str = "testql") -> Dict:
        """
        Build dependency map from TestQL scenario files.
        
        Args:
            scenarios_dir: Path to TestQL scenarios directory
            testql_bin: TestQL executable name or path
            
        Returns:
            Dictionary containing the full dependency map
        """
        discovery = TestQLEndpointDiscovery(scenarios_dir, testql_bin)
        dependency_map = discovery.to_dependency_map()
        
        # Merge with existing mappings
        for service, info in dependency_map.get("services", {}).items():
            self.service_to_endpoints[service].extend(info["endpoints"])
            self.service_to_files[service].update(info["files"])
        
        for file_path, endpoints in dependency_map.get("files", {}).items():
            self.file_to_endpoints[file_path].extend(endpoints)
        
        return self.to_dict()
