"""Interactive configuration assistant for wup.yaml.

Provides guided setup with intelligent suggestions, validation,
and auto-detection of project structure.

Usage:
    wup assistant              # Interactive mode
    wup assistant --quick    # Non-interactive with defaults
    wup assistant --template fastapi  # Use framework template
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.tree import Tree

from .models.config import (
    AnomalyDetectionConfig,
    NotifyConfig,
    ProjectConfig,
    ServiceConfig,
    ServiceType,
    TestQLConfig,
    TestStrategyConfig,
    VisualDiffConfig,
    WatchConfig,
    WebConfig,
    WupConfig,
)

# Import ServiceType for type checking
if False:  # TYPE_CHECKING
    from .models.config import ServiceType as ServiceTypeLiteral

console = Console()


class WupAssistant:
    """Interactive configuration assistant."""
    
    # Framework detection patterns
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
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config = WupConfig()
        self.draft_path = self.project_root / '.wup.yaml.draft'
        
    def run(self, quick: bool = False, template: Optional[str] = None):
        """Run the assistant."""
        console.print(Panel.fit(
            "[bold blue]WUP Configuration Assistant[/bold blue]\n"
            "Interactive setup for wup.yaml",
            border_style="blue"
        ))
        
        if quick:
            return self._quick_setup(template)
        
        # Load existing draft if present
        if self.draft_path.exists():
            if Confirm.ask("📝 Found existing draft. Load it?", default=True):
                self._load_draft()
        
        # Main loop
        while True:
            console.print("\n[bold]Main Menu:[/bold]")
            console.print("  1. Initialize project")
            console.print("  2. Configure services")
            console.print("  3. Setup file watching")
            console.print("  4. Configure TestQL")
            console.print("  5. Setup web dashboard")
            console.print("  6. Setup visual diff")
            console.print("  7. Setup anomaly detection")
            console.print("  8. Review & validate")
            console.print("  9. Save configuration")
            console.print("  0. Exit")
            
            choice = Prompt.ask(
                "Select option",
                choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                default="1"
            )
            
            if choice == "0":
                if Confirm.ask("Save draft before exiting?"):
                    self._save_draft()
                break
            elif choice == "1":
                self._init_project(template)
            elif choice == "2":
                self._configure_services()
            elif choice == "3":
                self._setup_watch()
            elif choice == "4":
                self._configure_testql()
            elif choice == "5":
                self._setup_web_dashboard()
            elif choice == "6":
                self._setup_visual_diff()
            elif choice == "7":
                self._setup_anomaly_detection()
            elif choice == "8":
                self._review_and_validate()
            elif choice == "9":
                self._save_configuration()
    
    def _init_project(self, template: Optional[str] = None):
        """Initialize project configuration."""
        console.print("\n[bold]🔧 Project Initialization[/bold]")
        
        # Detect or use template
        if template:
            framework = template
        else:
            framework = self._detect_framework()
            if framework:
                console.print(f"[green]✓ Detected framework: {framework}[/green]")
            else:
                framework = Prompt.ask(
                    "Framework",
                    choices=['fastapi', 'flask', 'django', 'express', 'other'],
                    default='fastapi'
                )
        
        # Project metadata
        self.config.project.name = Prompt.ask(
            "Project name",
            default=self.project_root.name
        )
        self.config.project.description = Prompt.ask(
            "Description",
            default=f"{framework.capitalize()} project"
        )
        
        # Auto-detect services based on framework
        if framework != 'other':
            services = self._auto_detect_services(framework)
            if services and Confirm.ask(
                f"Found {len(services)} potential services. Add them?",
                default=True
            ):
                for svc in services:
                    self.config.services.append(svc)
                console.print(f"[green]✓ Added {len(services)} services[/green]")
        
        console.print("[green]✓ Project initialized[/green]")
    
    def _detect_framework(self) -> Optional[str]:
        """Auto-detect project framework."""
        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            # Check for characteristic files
            for file in patterns['files']:
                if (self.project_root / file).exists():
                    # Verify content
                    content = (self.project_root / file).read_text()
                    if any(marker in content for marker in patterns['content']):
                        return framework
        return None
    
    def _auto_detect_services(self, framework: str) -> List[ServiceConfig]:
        """Auto-detect services based on framework patterns."""
        services = []
        patterns = self.FRAMEWORK_PATTERNS.get(framework, {})
        
        for pattern in patterns.get('services', []):
            for path in self.project_root.rglob(pattern):
                if path.is_dir() or path.is_file():
                    service_name = path.parent.name if path.name == '__init__.py' else path.stem
                    
                    # Detect service type
                    svc_type = self._detect_service_type(service_name, path)
                    
                    services.append(ServiceConfig(
                        name=service_name,
                        type=svc_type,
                        paths=[str(path.parent if path.name == '__init__.py' else path)],
                    ))
        
        return services
    
    def _detect_service_type(self, name: str, path: Path) -> ServiceType:
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
            files = list(path.iterdir())
            has_html = any(f.suffix in ['.html', '.htm'] for f in files)
            has_routes = any('route' in f.name.lower() for f in files)
            
            if has_html or has_routes:
                return 'web'
        
        return 'auto'
    
    def _configure_services(self):
        """Interactive service configuration."""
        console.print("\n[bold]📦 Service Configuration[/bold]")
        
        while True:
            console.print(f"\nCurrent services: {len(self.config.services)}")
            for i, svc in enumerate(self.config.services, 1):
                coinc = f" → {svc.coincidence_with}" if svc.coincidence_with else ""
                console.print(f"  {i}. {svc.name} [{svc.type}]{coinc}")
            
            action = Prompt.ask(
                "\nAction",
                choices=['add', 'edit', 'remove', 'detect', 'back'],
                default='back'
            )
            
            if action == 'back':
                break
            elif action == 'add':
                self._add_service_interactive()
            elif action == 'edit':
                idx = IntPrompt.ask("Service number to edit", min=1, max=len(self.config.services)) - 1
                self._edit_service(idx)
            elif action == 'remove':
                idx = IntPrompt.ask("Service number to remove", min=1, max=len(self.config.services)) - 1
                removed = self.config.services.pop(idx)
                console.print(f"[yellow]Removed: {removed.name}[/yellow]")
            elif action == 'detect':
                framework = self._detect_framework() or 'fastapi'
                services = self._auto_detect_services(framework)
                console.print(f"[dim]Detected {len(services)} potential services[/dim]")
                for svc in services:
                    if not any(s.name == svc.name for s in self.config.services):
                        if Confirm.ask(f"Add {svc.name}?", default=True):
                            self.config.services.append(svc)
    
    def _add_service_interactive(self):
        """Add a new service interactively."""
        name = Prompt.ask("Service name")
        
        # Suggest type based on name
        suggested_type = 'web' if any(x in name.lower() for x in ['web', 'api']) else 'auto'
        
        type_ = Prompt.ask(
            "Type",
            choices=['web', 'shell', 'auto'],
            default=suggested_type
        )
        
        # Paths
        use_auto = Confirm.ask("Auto-detect paths by service name?", default=True)
        paths = [] if use_auto else [Prompt.ask("Path pattern (e.g., app/service/**)")]
        
        # Coincidence detection
        coincidence = None
        if self.config.services and type_ in ('web', 'auto'):
            web_services = [s for s in self.config.services if s.type in ('web', 'auto')]
            if web_services and Confirm.ask("Link with existing web service?", default=False):
                options = [s.name for s in web_services]
                coincidence = Prompt.ask("Coincidence with", choices=options)
        
        self.config.services.append(ServiceConfig(
            name=name,
            type=type_,
            paths=paths,
            coincidence_with=coincidence
        ))
        console.print(f"[green]✓ Added service: {name}[/green]")
    
    def _edit_service(self, idx: int):
        """Edit existing service."""
        svc = self.config.services[idx]
        
        console.print(f"\n[bold]Editing: {svc.name}[/bold]")
        svc.name = Prompt.ask("Name", default=svc.name)
        svc.type = Prompt.ask("Type", choices=['web', 'shell', 'auto'], default=svc.type)
        
        if svc.paths:
            console.print(f"Current paths: {', '.join(svc.paths)}")
            if Confirm.ask("Modify paths?", default=False):
                paths_str = Prompt.ask("Paths (comma-separated)", default=','.join(svc.paths))
                svc.paths = [p.strip() for p in paths_str.split(',') if p.strip()]
        
        console.print(f"[green]✓ Updated: {svc.name}[/green]")
    
    def _setup_watch(self):
        """Setup file watching configuration."""
        console.print("\n[bold]👁️ File Watching Configuration[/bold]")
        
        # Paths
        console.print("\nWatch paths (current):")
        for i, path in enumerate(self.config.watch.paths, 1):
            console.print(f"  {i}. {path}")
        
        if Confirm.ask("\nAdd watch path?", default=False):
            new_path = Prompt.ask("Path pattern (e.g., src/**, app/*)")
            self.config.watch.paths.append(new_path)
        
        # File types
        current_types = self.config.watch.file_types
        console.print(f"\nFile types: {', '.join(current_types) if current_types else 'All files'}")
        
        if Confirm.ask("Change file types?", default=False):
            types_str = Prompt.ask("File extensions (comma-separated, e.g., .py,.ts)")
            self.config.watch.file_types = [t.strip() for t in types_str.split(',') if t.strip()]
        
        # Debounce
        console.print(f"\nCurrent debounce: {self.config.test_strategy.quick.debounce_s}s")
        new_debounce = IntPrompt.ask(
            "Debounce time (seconds)",
            default=self.config.test_strategy.quick.debounce_s
        )
        self.config.test_strategy.quick.debounce_s = new_debounce
        
        console.print("[green]✓ Watch configuration updated[/green]")
    
    def _configure_testql(self):
        """Configure TestQL integration."""
        console.print("\n[bold]🧪 TestQL Configuration[/bold]")
        
        # Scenario directory
        current_dir = self.config.testql.scenario_dir
        console.print(f"Current scenario directory: {current_dir}")
        
        new_dir = Prompt.ask("Scenario directory", default=current_dir)
        self.config.testql.scenario_dir = new_dir
        
        # Check for scenarios
        scenario_path = self.project_root / new_dir
        if scenario_path.exists():
            scenarios = list(scenario_path.rglob('*.testql.*'))
            console.print(f"[dim]Found {len(scenarios)} scenarios[/dim]")
        
        # Smoke scenario
        if Confirm.ask("Set smoke test scenario?", default=True):
            smoke = Prompt.ask("Smoke scenario file", default="smoke.testql.toon.yaml")
            self.config.testql.smoke_scenario = smoke
        
        # Output format
        self.config.testql.output_format = Prompt.ask(
            "Output format",
            choices=['json', 'yaml'],
            default=self.config.testql.output_format
        )
        
        console.print("[green]✓ TestQL configured[/green]")
    
    def _setup_web_dashboard(self):
        """Setup web dashboard (wupbro) configuration."""
        console.print("\n[bold]🌐 Web Dashboard (wupbro) Configuration[/bold]")
        
        enabled = Confirm.ask("Enable web dashboard?", default=self.config.web.enabled)
        self.config.web.enabled = enabled
        
        if enabled:
            self.config.web.endpoint = Prompt.ask(
                "Dashboard endpoint",
                default=self.config.web.endpoint or "http://localhost:8000"
            )
            
            self.config.web.timeout_s = IntPrompt.ask(
                "Timeout (seconds)",
                default=int(self.config.web.timeout_s)
            )
            
            console.print("\n[dim]Notification settings can be configured in the dashboard UI[/dim]")
            console.print("  - Navigate to http://localhost:8000")
            console.print("  - Click '🔔 Włącz powiadomienia'")
            console.print("  - Configure notification types in settings panel")
        
        console.print("[green]✓ Web dashboard configured[/green]")
    
    def _setup_visual_diff(self):
        """Setup visual diff configuration."""
        console.print("\n[bold]👁️ Visual Diff Configuration[/bold]")
        
        enabled = Confirm.ask(
            "Enable visual DOM diff? (requires Playwright)",
            default=self.config.visual_diff.enabled
        )
        self.config.visual_diff.enabled = enabled
        
        if enabled:
            self.config.visual_diff.base_url = Prompt.ask(
                "Base URL",
                default=self.config.visual_diff.base_url or "http://localhost:8100"
            )
            
            # Pages
            console.print("\nPages to scan:")
            for i, page in enumerate(self.config.visual_diff.pages, 1):
                console.print(f"  {i}. {page}")
            
            if Confirm.ask("Add page?", default=False):
                new_page = Prompt.ask("Page path (e.g., /health, /dashboard)")
                self.config.visual_diff.pages.append(new_page)
            
            # Thresholds
            console.print("\nCurrent thresholds:")
            console.print(f"  Added nodes: {self.config.visual_diff.threshold_added}")
            console.print(f"  Removed nodes: {self.config.visual_diff.threshold_removed}")
            console.print(f"  Changed attrs: {self.config.visual_diff.threshold_changed}")
            
            if Confirm.ask("Modify thresholds?", default=False):
                self.config.visual_diff.threshold_added = IntPrompt.ask(
                    "Added nodes threshold",
                    default=self.config.visual_diff.threshold_added
                )
        
        console.print("[green]✓ Visual diff configured[/green]")
    
    def _setup_anomaly_detection(self):
        """Setup anomaly detection configuration."""
        console.print("\n[bold]🔍 Anomaly Detection Configuration[/bold]")
        
        if not hasattr(self.config, 'anomaly_detection'):
            self.config.anomaly_detection = AnomalyDetectionConfig()
        
        enabled = Confirm.ask(
            "Enable anomaly detection?",
            default=getattr(self.config.anomaly_detection, 'enabled', True)
        )
        self.config.anomaly_detection.enabled = enabled
        
        if enabled:
            console.print("\nDetection methods:")
            console.print("  [✓] hash - Fast checksum comparison")
            console.print("  [✓] structure - YAML structure analysis")
            console.print("  [ ] ast - Python AST analysis")
            console.print("  [ ] text - Text diff")
            
            methods = []
            if Confirm.ask("Enable hash detection?", default=True):
                methods.append('hash')
            if Confirm.ask("Enable structure detection?", default=True):
                methods.append('structure')
            if Confirm.ask("Enable AST detection (Python files)?", default=False):
                methods.append('ast')
            
            self.config.anomaly_detection.methods = methods
            
            # Watch paths
            console.print("\nPaths to watch for anomalies:")
            watch_paths = getattr(self.config.anomaly_detection, 'watch_paths', [])
            for path in watch_paths:
                console.print(f"  - {path}")
            
            if Confirm.ask("Add watch path?", default=False):
                new_path = Prompt.ask("Path pattern")
                watch_paths.append(new_path)
                self.config.anomaly_detection.watch_paths = watch_paths
        
        console.print("[green]✓ Anomaly detection configured[/green]")
    
    def _review_and_validate(self):
        """Review and validate configuration."""
        console.print("\n[bold]📋 Configuration Review[/bold]\n")
        
        # Project info
        console.print(f"[cyan]Project:[/cyan] {self.config.project.name}")
        console.print(f"[cyan]Description:[/cyan] {self.config.project.description}")
        
        # Services table
        if self.config.services:
            console.print("\n[bold]Services:[/bold]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name")
            table.add_column("Type")
            table.add_column("Paths")
            table.add_column("Coincidence")
            
            for svc in self.config.services:
                paths = ', '.join(svc.paths) if svc.paths else 'Auto-detect'
                coin = svc.coincidence_with or '-'
                table.add_row(svc.name, svc.type, paths, coin)
            
            console.print(table)
        
        # Watch configuration
        console.print("\n[bold]Watch Configuration:[/bold]")
        console.print(f"  Paths: {', '.join(self.config.watch.paths) or 'None'}")
        console.print(f"  File types: {', '.join(self.config.watch.file_types) or 'All'}")
        console.print(f"  Debounce: {self.config.test_strategy.quick.debounce_s}s")
        
        # Validation
        issues = self._validate_config()
        
        if issues:
            console.print("\n[bold red]⚠️ Issues found:[/bold red]")
            for issue in issues:
                console.print(f"  • {issue}")
        else:
            console.print("\n[green]✓ Configuration is valid[/green]")
        
        # Suggestions
        suggestions = self._generate_suggestions()
        if suggestions:
            console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
            for sug in suggestions:
                console.print(f"  • {sug}")
    
    def _validate_config(self) -> List[str]:
        """Validate current configuration."""
        issues = []
        
        # Check project name
        if not self.config.project.name:
            issues.append("Project name is required")
        
        # Check services
        if not self.config.services:
            issues.append("No services configured")
        
        for svc in self.config.services:
            if not svc.name:
                issues.append("Service with empty name found")
        
        # Check watch paths exist
        for path in self.config.watch.paths:
            resolved = self.project_root / path.replace('/**', '').replace('/*', '')
            if not resolved.exists():
                issues.append(f"Watch path does not exist: {path}")
        
        # Check TestQL
        if self.config.testql.scenario_dir:
            scenario_path = self.project_root / self.config.testql.scenario_dir
            if not scenario_path.exists():
                issues.append(f"TestQL scenario directory not found: {self.config.testql.scenario_dir}")
        
        return issues
    
    def _generate_suggestions(self) -> List[str]:
        """Generate helpful suggestions."""
        suggestions = []
        
        if len(self.config.services) == 1:
            suggestions.append("Consider splitting into multiple services for better granularity")
        
        if not self.config.watch.file_types:
            suggestions.append("Specify file types to avoid watching unnecessary files")
        
        if not self.config.web.enabled:
            suggestions.append("Enable web dashboard for real-time monitoring and notifications")
        
        if self.config.testql.scenario_dir and not self.config.testql.smoke_scenario:
            suggestions.append("Set a smoke test scenario for quick health checks")
        
        return suggestions
    
    def _save_configuration(self):
        """Save configuration to wup.yaml."""
        target_path = self.project_root / 'wup.yaml'
        
        # Backup existing
        if target_path.exists():
            backup = self.project_root / f'wup.yaml.bak.{int(__import__("time").time())}'
            backup.write_text(target_path.read_text())
            console.print(f"[dim]Backup created: {backup.name}[/dim]")
        
        # Convert to dict and clean up
        config_dict = self._config_to_dict(self.config)
        
        # Write
        target_path.write_text(
            yaml.dump(config_dict, default_flow_style=False, sort_keys=False, allow_unicode=True)
        )
        
        console.print(f"\n[bold green]✓ Configuration saved to wup.yaml[/bold green]")
        
        # Clean up draft
        if self.draft_path.exists():
            self.draft_path.unlink()
    
    def _save_draft(self):
        """Save draft configuration."""
        config_dict = self._config_to_dict(self.config)
        self.draft_path.write_text(yaml.dump(config_dict, allow_unicode=True))
        console.print(f"[dim]Draft saved to {self.draft_path.name}[/dim]")
    
    def _load_draft(self):
        """Load draft configuration."""
        try:
            content = self.draft_path.read_text()
            data = yaml.safe_load(content)
            self.config = WupConfig(**data)
            console.print("[green]✓ Draft loaded[/green]")
        except Exception as e:
            console.print(f"[red]Failed to load draft: {e}[/red]")
    
    def _config_to_dict(self, config: WupConfig) -> Dict:
        """Convert config to clean dict for YAML output."""
        # Use asdict and clean None/empty values
        data = asdict(config)
        
        def clean(d):
            if isinstance(d, dict):
                return {k: clean(v) for k, v in d.items() if v not in (None, [], {}, '')}
            elif isinstance(d, list):
                return [clean(i) for i in d if i not in (None, [], {}, '')]
            return d
        
        return clean(data)
    
    def _quick_setup(self, template: Optional[str]):
        """Quick non-interactive setup."""
        framework = template or self._detect_framework() or 'fastapi'
        
        self.config.project.name = self.project_root.name
        self.config.project.description = f"{framework.capitalize()} project"
        
        # Auto-detect services
        services = self._auto_detect_services(framework)
        self.config.services = services if services else [
            ServiceConfig(name='main', type='auto')
        ]
        
        # Default watch paths
        self.config.watch.paths = ['app/**', 'src/**']
        self.config.watch.file_types = ['.py']
        
        # Enable web dashboard
        self.config.web.enabled = True
        self.config.web.endpoint = 'http://localhost:8000'
        
        # Save
        self._save_configuration()
        console.print(f"[green]✓ Quick setup complete with {len(self.config.services)} services[/green]")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WUP Configuration Assistant")
    parser.add_argument('--quick', action='store_true', help='Non-interactive mode')
    parser.add_argument('--template', help='Framework template (fastapi/flask/django)')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    
    args = parser.parse_args()
    
    assistant = WupAssistant(args.project_root)
    assistant.run(quick=args.quick, template=args.template)


if __name__ == '__main__':
    main()
