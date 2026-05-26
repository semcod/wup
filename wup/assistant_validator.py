"""Configuration validation and suggestion generation for the WUP assistant."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .models.config import WupConfig


def validate_config(config: WupConfig, project_root: Path) -> List[str]:
    """Validate current WUP configuration and return a list of discovered issues."""
    issues = []
    
    # Check project name
    if not config.project.name:
        issues.append("Project name is required")
    
    # Check services
    if not config.services:
        issues.append("No services configured")
    
    for svc in config.services:
        if not svc.name:
            issues.append("Service with empty name found")
    
    # Check watch paths exist
    for path in config.watch.paths:
        resolved = project_root / path.replace('/**', '').replace('/*', '')
        if not resolved.exists():
            issues.append(f"Watch path does not exist: {path}")
    
    # Check TestQL
    if config.testql.scenario_dir:
        scenario_path = project_root / config.testql.scenario_dir
        if not scenario_path.exists():
            issues.append(f"TestQL scenario directory not found: {config.testql.scenario_dir}")
    
    return issues


def generate_suggestions(config: WupConfig) -> List[str]:
    """Generate helpful improvement suggestions based on current WUP configuration."""
    suggestions = []
    
    if len(config.services) == 1:
        suggestions.append("Consider splitting into multiple services for better granularity")
    
    if not config.watch.file_types:
        suggestions.append("Specify file types to avoid watching unnecessary files")
    
    if not config.web.enabled:
        suggestions.append("Enable web dashboard for real-time monitoring and notifications")
    
    if config.testql.scenario_dir and not config.testql.smoke_scenario:
        suggestions.append("Set a smoke test scenario for quick health checks")
    
    return suggestions
