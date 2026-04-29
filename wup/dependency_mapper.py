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
import re


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
        
        Args:
            framework: Framework to detect (auto, fastapi, flask, django, express)
            
        Returns:
            Dictionary containing the full dependency map
        """
        # Detect framework if auto
        if framework == "auto":
            framework = self._detect_framework()
        
        # Scan for endpoint definitions
        endpoints = self._scan_endpoints(framework)
        
        # Build mappings
        for ep in endpoints:
            file_path = ep.get("file", "")
            endpoint_path = ep.get("path", "")
            service = self._infer_service(file_path)
            
            if file_path:
                self.file_to_endpoints[file_path].append(endpoint_path)
            
            if service:
                self.service_to_endpoints[service].append(endpoint_path)
                self.service_to_files[service].add(file_path)
        
        return self.to_dict()
    
    def _detect_framework(self) -> str:
        """Detect the web framework used in the project."""
        # Check for common framework indicators
        indicators = {
            "fastapi": ["FastAPI", "APIRouter", "from fastapi"],
            "flask": ["Flask", "Blueprint", "from flask"],
            "django": ["urlpatterns", "path(", "from django.urls"],
            "express": ["express()", "app.get(", "router."],
        }
        
        for framework, patterns in indicators.items():
            for pattern in patterns:
                if self._search_codebase(pattern):
                    return framework
        
        return "generic"
    
    def _search_codebase(self, pattern: str) -> bool:
        """Search for a pattern in the codebase."""
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                if pattern in content:
                    return True
            except (UnicodeDecodeError, PermissionError):
                continue
        return False
    
    def _scan_endpoints(self, framework: str) -> List[Dict]:
        """Scan codebase for endpoint definitions."""
        endpoints = []
        
        if framework in ["fastapi", "flask", "django"]:
            endpoints.extend(self._scan_python_endpoints(framework))
        elif framework == "express":
            endpoints.extend(self._scan_js_endpoints())
        
        return endpoints
    
    def _scan_python_endpoints(self, framework: str) -> List[Dict]:
        """Scan Python files for endpoint definitions."""
        endpoints = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                rel_path = str(py_file.relative_to(self.project_root))
                
                # FastAPI: @app.get, @router.get, @router.post, etc.
                if framework == "fastapi":
                    matches = re.findall(r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
                    for method, path in matches:
                        endpoints.append({
                            "method": method.upper(),
                            "path": path,
                            "file": rel_path,
                            "framework": "fastapi"
                        })
                
                # Flask: @app.route, @bp.route
                elif framework == "flask":
                    matches = re.findall(r'@(?:app|bp)\.route\s*\(\s*["\']([^"\']+)["\']\s*,\s*methods=\[([^\]]+)\]', content)
                    for path, methods in matches:
                        for method in methods.strip('"\'').split(','):
                            endpoints.append({
                                "method": method.strip().strip('"\'').upper(),
                                "path": path,
                                "file": rel_path,
                                "framework": "flask"
                            })
                
                # Django: path(), url()
                elif framework == "django":
                    matches = re.findall(r'path\s*\(\s*["\']([^"\']+)["\']', content)
                    for path in matches:
                        endpoints.append({
                            "method": "GET",  # Django doesn't specify method in path
                            "path": path,
                            "file": rel_path,
                            "framework": "django"
                        })
            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return endpoints
    
    def _scan_js_endpoints(self) -> List[Dict]:
        """Scan JavaScript/TypeScript files for endpoint definitions."""
        endpoints = []
        
        for js_file in self.project_root.rglob("*.{js,ts,jsx,tsx}"):
            try:
                content = js_file.read_text()
                rel_path = str(js_file.relative_to(self.project_root))
                
                # Express: app.get, router.post, etc.
                matches = re.findall(r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
                for method, path in matches:
                    endpoints.append({
                        "method": method.upper(),
                        "path": path,
                        "file": rel_path,
                        "framework": "express"
                    })
            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return endpoints
    
    def _infer_service(self, file_path: str) -> Optional[str]:
        """
        Infer service name from file path.
        
        Examples:
            app/users/routes.py → "users"
            app/api/v1/devices.py → "api/v1/devices"
            src/components/auth.ts → "components/auth"
        """
        parts = Path(file_path).parts
        
        # Common patterns
        if "app" in parts:
            idx = parts.index("app")
            if idx + 1 < len(parts):
                return "/".join(parts[idx:idx+2])
        
        if "src" in parts:
            idx = parts.index("src")
            if idx + 1 < len(parts):
                return "/".join(parts[idx:idx+2])
        
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
        return {
            "services": {
                service: {
                    "endpoints": endpoints,
                    "files": list(files)
                }
                for service, (endpoints, files) in zip(
                    self.service_to_endpoints.keys(),
                    zip(self.service_to_endpoints.values(), self.service_to_files.values())
                )
            },
            "files": dict(self.file_to_endpoints)
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
