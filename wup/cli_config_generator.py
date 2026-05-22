"""Generator for wup.yaml configuration for CLI/shell services."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .cli_scanner import CLIScanner, CLIPackage, CLICommand
from .models.config import (
    ProjectConfig,
    ServiceConfig,
    ServiceTestConfig,
    TestQLConfig,
    TestStrategyConfig,
    WatchConfig,
    WupConfig,
)


class CLIConfigGenerator:
    """Generate wup.yaml configuration for CLI/shell services."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.scanner = CLIScanner(project_root)

    def generate(
        self,
        output_path: Optional[Path] = None,
        merge_existing: bool = False,
    ) -> WupConfig:
        """Generate wup.yaml configuration for CLI services.

        Args:
            output_path: Path to save the configuration (default: wup.yaml)
            merge_existing: If True, merge with existing wup.yaml

        Returns:
            Generated WupConfig object
        """
        # Scan for CLI commands
        packages = self.scanner.scan()

        if not packages:
            raise ValueError("No CLI packages found in project")

        # Load existing config if merging
        existing_config = None
        if merge_existing:
            from .config import load_config
            existing_config = load_config(self.project_root)

        # Generate configuration
        config = self._generate_config(packages, existing_config)

        # Save configuration
        if output_path is None:
            output_path = self.project_root / "wup.yaml"

        self._save_config(config, output_path)

        return config

    def _generate_config(
        self,
        packages: List[CLIPackage],
        existing_config: Optional[WupConfig] = None,
    ) -> WupConfig:
        """Generate WupConfig from scanned packages."""
        if existing_config:
            config = existing_config
        else:
            config = WupConfig(
                project=ProjectConfig(
                    name=self.project_root.name,
                    description=f"CLI testing for {self.project_root.name}",
                ),
                watch=WatchConfig(
                    paths=["**"],
                    exclude_patterns=["*.md", "tests/**", ".venv/**", "venv/**", "node_modules/**"],
                    file_types=[".py"],
                ),
                test_strategy=TestStrategyConfig(
                    quick={"debounce_s": 2, "max_queue": 5, "timeout_s": 30},
                    detail={"debounce_s": 10, "max_queue": 1, "timeout_s": 60},
                ),
                testql=TestQLConfig(
                    scenario_dir="testql-scenarios",
                    smoke_scenario="cli-smoke.testql.toon.yaml",
                    output_format="json",
                    probe_interval_s=60,
                ),
            )

        # Add shell services for each package
        for package in packages:
            service = self._create_shell_service(package)
            
            # Check if service already exists
            existing_service = next(
                (s for s in config.services if s.name == service.name),
                None,
            )
            
            if existing_service:
                # Update existing service
                existing_service.type = service.type
                existing_service.quick_tests = service.quick_tests
                existing_service.detail_tests = service.detail_tests
            else:
                # Add new service
                config.services.append(service)

        return config

    def _create_shell_service(self, package: CLIPackage) -> ServiceConfig:
        """Create a shell service configuration from a CLI package."""
        # Calculate max_endpoints based on number of commands
        command_count = len(package.commands)
        quick_max = min(command_count, 5)
        detail_max = min(command_count * 2, 20)

        service = ServiceConfig(
            name=f"{package.name}-shell",
            type="shell",
            paths=[],  # Auto-detect
            root=str(self.project_root),
            quick_tests=ServiceTestConfig(
                scope="all",
                max_endpoints=quick_max,
            ),
            detail_tests=ServiceTestConfig(
                scope="all",
                max_endpoints=detail_max,
            ),
        )

        return service

    def _save_config(self, config: WupConfig, output_path: Path) -> None:
        """Save configuration to YAML file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        config_dict = {
            "project": {
                "name": config.project.name,
                "description": config.project.description,
            },
            "watch": {
                "paths": config.watch.paths,
                "exclude_patterns": config.watch.exclude_patterns,
                "file_types": config.watch.file_types,
            },
            "services": [
                {
                    "name": svc.name,
                    "type": svc.type,
                    "paths": svc.paths,
                    "root": svc.root,
                    "quick_tests": {
                        "scope": svc.quick_tests.scope,
                        "max_endpoints": svc.quick_tests.max_endpoints,
                    },
                    "detail_tests": {
                        "scope": svc.detail_tests.scope,
                        "max_endpoints": svc.detail_tests.max_endpoints,
                    },
                }
                for svc in config.services
            ],
            "test_strategy": {
                "quick": config.test_strategy.quick,
                "detail": config.test_strategy.detail,
            },
            "testql": {
                "scenario_dir": config.testql.scenario_dir,
                "smoke_scenario": config.testql.smoke_scenario,
                "output_format": config.testql.output_format,
                "probe_interval_s": config.testql.probe_interval_s,
            },
        }

        # Add header
        header = f"""# WUP Configuration for CLI Testing
# Generated automatically by wup init-cli
# Project: {config.project.name}

"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header)
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    def print_summary(self, config: WupConfig) -> None:
        """Print summary of generated configuration."""
        from rich.console import Console
        from rich.table import Table

        console = Console()

        console.print("\n[bold green]✓ Generated wup.yaml configuration[/bold green]\n")

        table = Table(title="Shell Services")
        table.add_column("Service", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Quick Tests", style="yellow")
        table.add_column("Detail Tests", style="yellow")

        for svc in config.services:
            if svc.type == "shell":
                table.add_row(
                    svc.name,
                    svc.type,
                    str(svc.quick_tests.max_endpoints),
                    str(svc.detail_tests.max_endpoints),
                )

        console.print(table)
        console.print(f"\nTestQL scenarios directory: {config.testql.scenario_dir}")
        console.print(f"Smoke scenario: {config.testql.smoke_scenario}")
