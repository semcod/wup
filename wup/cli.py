"""
CLI interface for WUP (What's Up) - Intelligent file watcher for regression testing.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .config import load_config
from .core import WupWatcher
from .dependency_mapper import DependencyMapper
from .models.config import WupConfig
from .testql_watcher import TestQLWatcher

app = typer.Typer(
    name="wup",
    help="WUP (What's Up) - Intelligent file watcher for regression testing in large projects",
    add_completion=False
)
console = Console()


@app.command()
def watch(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    deps_file: str = typer.Option("deps.json", "--deps", "-d", help="Path to dependency map file"),
    cpu_throttle: float = typer.Option(0.8, "--cpu-throttle", "-c", help="CPU usage threshold (0.0-1.0)"),
    debounce: int = typer.Option(2, "--debounce", "-b", help="Debounce time in seconds"),
    cooldown: int = typer.Option(300, "--cooldown", "-t", help="Test cooldown in seconds"),
    dashboard: bool = typer.Option(False, "--dashboard", help="Enable live dashboard"),
    mode: str = typer.Option("default", "--mode", help="Watcher mode: default or testql"),
    scenarios_dir: str = typer.Option("testql-scenarios", "--scenarios-dir", help="Directory with TestQL scenario files"),
    testql_bin: str = typer.Option("testql", "--testql-bin", help="TestQL executable name/path"),
    browser_service_url: Optional[str] = typer.Option(None, "--browser-service-url", help="HTTP endpoint for browser notifications"),
    track_dir: str = typer.Option(".wup/tracks", "--track-dir", help="Directory where error track JSON files are written"),
    quick_limit: int = typer.Option(3, "--quick-limit", help="Maximum TestQL scenarios used in quick pass"),
    config: Optional[str] = typer.Option(None, "--config", "-C", help="Path to wup.yaml config file"),
):
    """
    Watch project for file changes and run intelligent regression tests.
    
    Uses a 3-layer approach:
    1. Detection: File watching with heuristics
    2. Priority: Quick tests of related services (3 endpoints max)
    3. Detail: Full tests with blame reports (only on failure)
    """
    project_path = Path(project).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)
    
    # Load configuration
    config_path = Path(config) if config else None
    wup_config = load_config(project_path, config_path)
    
    console.print(f"[bold cyan]🚀 WUP Watcher[/bold cyan]")
    console.print(f"[dim]Project: {wup_config.project.name}[/dim]")
    console.print(f"[dim]Description: {wup_config.project.description}[/dim]")
    console.print(f"[dim]CPU Throttle: {cpu_throttle * 100}%[/dim]")
    console.print(f"[dim]Debounce: {debounce}s[/dim]")
    console.print(f"[dim]Cooldown: {cooldown}s[/dim]")
    console.print(f"[dim]Config: {config_path or 'auto-detected'}[/dim]")
    console.print()
    
    if mode.lower() == "testql":
        watcher = TestQLWatcher(
            project_root=str(project_path),
            deps_file=deps_file,
            cpu_throttle=cpu_throttle,
            debounce_seconds=debounce,
            test_cooldown_seconds=cooldown,
            scenarios_dir=scenarios_dir,
            testql_bin=testql_bin,
            browser_service_url=browser_service_url,
            track_dir=track_dir,
            quick_limit=quick_limit,
            config=wup_config,
        )
        console.print("[green]TestQL mode enabled[/green]")
    else:
        watcher = WupWatcher(
            project_root=str(project_path),
            deps_file=deps_file,
            cpu_throttle=cpu_throttle,
            debounce_seconds=debounce,
            test_cooldown_seconds=cooldown,
            config=wup_config,
        )
    
    if dashboard:
        console.print("[green]Starting watcher with live dashboard...[/green]")
        asyncio.run(watcher.run_with_dashboard())
    else:
        console.print("[green]Starting watcher...[/green]")
        watcher.start_watching()


@app.command()
def map_deps(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    output: str = typer.Option("deps.json", "--output", "-o", help="Output file path"),
    framework: str = typer.Option("auto", "--framework", "-f", help="Framework to detect (auto, fastapi, flask, django, express)"),
    config: Optional[str] = typer.Option(None, "--config", "-C", help="Path to wup.yaml config file"),
):
    """
    Build dependency map by scanning the codebase.
    
    Maps files → endpoints → services for intelligent testing.
    """
    project_path = Path(project).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)
    
    # Load configuration
    config_path = Path(config) if config else None
    wup_config = load_config(project_path, config_path)
    
    console.print(f"[bold cyan]🔍 Building dependency map[/bold cyan]")
    console.print(f"[dim]Project: {wup_config.project.name}[/dim]")
    console.print(f"[dim]Framework: {framework}[/dim]")
    if wup_config.services:
        console.print(f"[dim]Services from config: {len(wup_config.services)}[/dim]")
    console.print()
    
    mapper = DependencyMapper(str(project_path))
    deps = mapper.build_from_codebase(framework)
    
    # Enhance deps with service information from config
    if wup_config.services:
        for svc in wup_config.services:
            if svc.name not in deps.get("services", {}):
                deps.setdefault("services", {})[svc.name] = {
                    "endpoints": [],
                    "files": svc.paths,
                    "config": {
                        "quick_tests": {
                            "scope": svc.quick_tests.scope,
                            "max_endpoints": svc.quick_tests.max_endpoints
                        },
                        "detail_tests": {
                            "scope": svc.detail_tests.scope,
                            "max_endpoints": svc.detail_tests.max_endpoints
                        }
                    }
                }
    
    mapper.save(output)
    
    # Print summary
    services = deps.get("services", {})
    files = deps.get("files", {})
    
    console.print(f"[green]✓ Dependency map saved to {output}[/green]")
    console.print(f"[dim]Services found: {len(services)}[/dim]")
    console.print(f"[dim]Files mapped: {len(files)}[/dim]")
    console.print()
    
    if services:
        console.print("[bold]Services:[/bold]")
        for service, info in sorted(services.items()):
            console.print(f"  [cyan]{service}[/cyan]: {len(info.get('endpoints', []))} endpoints, {len(info.get('files', []))} files")


@app.command()
def status(
    deps_file: str = typer.Option("deps.json", "--deps", "-d", help="Path to dependency map file"),
    config: Optional[str] = typer.Option(None, "--config", "-C", help="Path to wup.yaml config file"),
):
    """
    Show dependency map status and configuration.
    """
    project_path = Path(".").resolve()
    
    # Load configuration
    config_path = Path(config) if config else None
    wup_config = load_config(project_path, config_path)
    
    console.print(f"[bold cyan]📊 WUP Status[/bold cyan]")
    console.print(f"[dim]Project: {wup_config.project.name}[/dim]")
    console.print(f"[dim]Description: {wup_config.project.description}[/dim]")
    console.print()
    
    # Show watch configuration
    console.print("[bold]Watch Configuration:[/bold]")
    console.print(f"  Paths: {', '.join(wup_config.watch.paths) if wup_config.watch.paths else 'default'}")
    console.print(f"  Excludes: {', '.join(wup_config.watch.exclude_patterns)}")
    console.print()
    
    # Show services
    if wup_config.services:
        console.print(f"[bold]Services ({len(wup_config.services)}):[/bold]")
        for svc in wup_config.services:
            console.print(f"  [cyan]{svc.name}[/cyan]")
            console.print(f"    Root: {svc.root}")
            console.print(f"    Quick: scope={svc.quick_tests.scope}, max={svc.quick_tests.max_endpoints}")
            console.print(f"    Detail: scope={svc.detail_tests.scope}, max={svc.detail_tests.max_endpoints}")
        console.print()
    
    # Show dependency map status
    deps_path = Path(deps_file)
    
    if not deps_path.exists():
        console.print(f"[yellow]Warning: Dependency file '{deps_file}' does not exist[/yellow]")
        console.print(f"[dim]Run 'wup map-deps' to create it[/dim]")
        console.print()
        return
    
    import json
    with open(deps_file) as f:
        deps = json.load(f)
    
    services = deps.get("services", {})
    files = deps.get("files", {})
    
    console.print(f"[bold]Dependency Map:[/bold]")
    console.print(f"  Services: {len(services)}")
    console.print(f"  Files: {len(files)}")
    console.print()
    
    if services:
        console.print("[bold]Service Details:[/bold]")
        for service, info in sorted(services.items()):
            endpoints = info.get("endpoints", [])
            service_files = info.get("files", [])
            console.print(f"  [cyan]{service}[/cyan]")
            console.print(f"    Endpoints: {len(endpoints)}")
            console.print(f"    Files: {len(service_files)}")
            if endpoints:
                console.print(f"    Sample endpoints: {', '.join(endpoints[:3])}")


@app.command()
def init(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    output: str = typer.Option("wup.yaml", "--output", "-o", help="Output config file path"),
):
    """
    Initialize a new wup.yaml configuration file.
    """
    from .config import save_config, get_default_config
    
    project_path = Path(project).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)
    
    output_path = Path(output)
    if output_path.exists():
        console.print(f"[red]Error: Config file '{output}' already exists[/red]")
        raise typer.Exit(1)
    
    config = get_default_config(project_path)
    save_config(config, output_path)
    
    console.print(f"[green]✓ Created wup.yaml configuration at {output_path}[/green]")
    console.print(f"[dim]Edit this file to customize your WUP setup[/dim]")


@app.command()
def testql_endpoints(
    scenarios_dir: str = typer.Argument(..., help="Path to TestQL scenarios directory"),
    output: str = typer.Option("testql-deps.json", "--output", "-o", help="Output dependency map file path"),
    testql_bin: str = typer.Option("testql", "--testql-bin", help="TestQL executable name or path"),
):
    """
    Discover endpoints from TestQL scenario files and build dependency map.
    """
    from .testql_discovery import TestQLEndpointDiscovery
    from rich.table import Table
    
    scenarios_path = Path(scenarios_dir)
    
    if not scenarios_path.exists():
        console.print(f"[red]Error: Scenarios directory '{scenarios_dir}' does not exist[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]🔍 Discovering endpoints from TestQL scenarios...[/cyan]")
    console.print(f"[dim]Scenarios directory: {scenarios_dir}[/dim]")
    console.print()
    
    discovery = TestQLEndpointDiscovery(scenarios_dir, testql_bin)
    dependency_map = discovery.to_dependency_map()
    
    # Display results
    table = Table(title="Discovered Endpoints")
    table.add_column("Service", style="cyan")
    table.add_column("Endpoints", style="green")
    table.add_column("Scenarios", style="yellow")
    
    total_endpoints = 0
    total_scenarios = 0
    
    for service, info in sorted(dependency_map.get("services", {}).items()):
        endpoints_count = len(info.get("endpoints", []))
        scenarios_count = len(info.get("scenarios", []))
        total_endpoints += endpoints_count
        total_scenarios += scenarios_count
        
        table.add_row(
            service,
            str(endpoints_count),
            str(scenarios_count)
        )
    
    console.print(table)
    console.print()
    console.print(f"[bold]Summary:[/bold]")
    console.print(f"  Services: {len(dependency_map.get('services', {}))}")
    console.print(f"  Total endpoints: {total_endpoints}")
    console.print(f"  Total scenarios: {total_scenarios}")
    console.print()
    
    # Save to file
    import json
    output_path = Path(output)
    with open(output_path, 'w') as f:
        json.dump(dependency_map, f, indent=2)
    
    console.print(f"[green]✓ Dependency map saved to {output_path}[/green]")


@app.command()
def version():
    """Show WUP version."""
    from . import __version__
    console.print(f"[bold cyan]WUP[/bold cyan] version [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
