"""Project discovery and framework detection for the WUP assistant."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .models.config import ServiceConfig, ServiceType


FRAMEWORK_PATTERNS = {
    'fastapi': {
        'files': ['main.py', 'app/main.py'],
        'content': ['FastAPI', 'from fastapi', 'app = FastAPI'],
        'services': ['app/routers/*', 'app/routes/*', 'routes/*'],
        'default_services': ['web', 'api'],
    },
    'flask': {
        'files': ['app.py', 'wsgi.py', 'application.py'],
        'content': ['Flask', 'from flask', 'app = Flask'],
        'services': ['app/*/__init__.py', 'blueprints/*'],
        'default_services': ['web', 'admin'],
    },
    'django': {
        'files': ['manage.py', 'settings.py'],
        'content': ['Django', 'from django', 'INSTALLED_APPS'],
        'services': ['*/apps.py', '*/models.py'],
        'default_services': ['models', 'views', 'tasks'],
    },
    'express': {
        'files': ['server.js', 'app.js'],
        'content': ['express', 'require("express")', "require('express')"],
        'services': ['routes/*', 'controllers/*'],
        'default_services': ['api', 'web'],
    },
}


def detect_framework(project_root: Path) -> Optional[str]:
    """Auto-detect project framework based on characteristic files and contents."""
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for file in patterns['files']:
            target_file = project_root / file
            if target_file.exists():
                try:
                    content = target_file.read_text(encoding="utf-8")
                    if any(marker in content for marker in patterns['content']):
                        return framework
                except OSError:
                    pass
    return None


def auto_detect_services(project_root: Path, framework: str) -> List[ServiceConfig]:
    """Auto-detect services based on framework patterns."""
    services = []
    patterns = FRAMEWORK_PATTERNS.get(framework, {})
    
    for pattern in patterns.get('services', []):
        for path in project_root.rglob(pattern):
            if path.is_dir() or path.is_file():
                service_name = path.parent.name if path.name == '__init__.py' else path.stem
                
                # Detect service type
                svc_type = detect_service_type(service_name, path)
                
                services.append(ServiceConfig(
                    name=service_name,
                    type=svc_type,
                    paths=[str(path.parent if path.name == '__init__.py' else path)],
                ))
    
    return services


def detect_service_type(name: str, path: Path) -> ServiceType:
    """Detect service type from name and path."""
    name_lower = name.lower()
    
    # Web indicators
    if any(x in name_lower for x in ['web', 'api', 'http', 'rest', 'router', 'route']):
        return 'web'
    
    # Shell indicators
    if any(x in name_lower for x in ['shell', 'cli', 'cmd', 'command']):
        return 'shell'
    
    # Check directory contents
    if path.is_dir():
        try:
            files = list(path.iterdir())
            has_html = any(f.suffix in ['.html', '.htm'] for f in files)
            has_routes = any('route' in f.name.lower() for f in files)
            
            if has_html or has_routes:
                return 'web'
        except OSError:
            pass
    
    return 'auto'
