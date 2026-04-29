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
    delta_seconds: int = typer.Option(0, "--delta-seconds", help="Show only service health transitions from last N seconds"),
    failed_only: bool = typer.Option(False, "--failed-only", help="Show only currently failing services"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Live mode: refresh display in real time"),
    interval: int = typer.Option(5, "--interval", "-i", help="Refresh interval in seconds for --watch mode"),
):
    """
    Show dependency map status and configuration.
    """
    import json
    import time

    project_path = Path(".").resolve()
    config_path = Path(config) if config else None
    wup_config = load_config(project_path, config_path)
    health_state_path = project_path / ".wup" / "service-health.json"
    health_events_path = project_path / ".wup" / "service-health-events.jsonl"

    deps_path = Path(deps_file)

    def _build_panel(ts: float) -> "Group":
        from rich.console import Group
        from rich.text import Text
        from rich.padding import Padding
        lines: list = []

        # header
        lines.append(Text.from_markup(
            f"[bold cyan]📊 WUP Status[/bold cyan]  "
            f"[dim]{wup_config.project.name}[/dim]  "
            f"[dim]updated {time.strftime('%H:%M:%S', time.localtime(ts))}[/dim]"
        ))

        # --- failing services ---
        health_state: dict = {}
        if health_state_path.exists():
            try:
                payload = json.loads(health_state_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    health_state = payload
            except json.JSONDecodeError:
                pass

        if failed_only or watch:
            failing = [
                (svc, data)
                for svc, data in sorted(health_state.items())
                if isinstance(data, dict) and data.get("status") == "down"
            ]
            lines.append(Text(""))
            lines.append(Text.from_markup("[bold]Currently failing services:[/bold]"))
            if not failing:
                lines.append(Text.from_markup("  [green]✓ None[/green]"))
            else:
                for svc, data in failing:
                    stage = data.get("stage", "")
                    message = data.get("message", "")
                    track_file = data.get("track_file", "")
                    lines.append(Text.from_markup(f"  [red]✗ {svc}[/red]  [dim]{stage}[/dim]"))
                    if message:
                        lines.append(Text.from_markup(f"    [dim]{message}[/dim]"))
                    if track_file:
                        lines.append(Text.from_markup(f"    [dim]track: {track_file}[/dim]"))

        # --- delta ---
        effective_delta = delta_seconds if delta_seconds > 0 else (30 if watch else 0)
        if effective_delta > 0:
            cutoff = int(ts) - effective_delta
            recent_events: list = []
            if health_events_path.exists():
                with health_events_path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if int(event.get("timestamp", 0)) >= cutoff:
                            recent_events.append(event)

            lines.append(Text(""))
            lines.append(Text.from_markup(f"[bold]Service health delta (last {effective_delta}s):[/bold]"))
            if not recent_events:
                lines.append(Text.from_markup("  [yellow]No health transitions in selected window[/yellow]"))
            else:
                recent_events.sort(key=lambda e: int(e.get("timestamp", 0)), reverse=True)
                for event in recent_events:
                    svc = event.get("service", "unknown")
                    prev = event.get("previous_status", "unknown")
                    curr = event.get("status", "unknown")
                    stage = event.get("stage", "")
                    message = event.get("message", "")
                    track_file = event.get("track_file", "")
                    arrow_color = "green" if curr == "up" else "red"
                    lines.append(Text.from_markup(
                        f"  [cyan]{svc}[/cyan]: {prev} [bold {arrow_color}]→ {curr}[/bold {arrow_color}] [dim]({stage})[/dim]"
                    ))
                    if message:
                        lines.append(Text.from_markup(f"    [dim]{message}[/dim]"))
                    if track_file:
                        lines.append(Text.from_markup(f"    [dim]track: {track_file}[/dim]"))

        return Group(*lines)

    if not watch:
        console.print(_build_panel(time.time()))
        return

    # --- live / watch mode ---
    from rich.live import Live
    try:
        with Live(_build_panel(time.time()), refresh_per_second=1, console=console) as live:
            while True:
                time.sleep(interval)
                live.update(_build_panel(time.time()))
    except KeyboardInterrupt:
        pass


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
def map_deps(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    output: str = typer.Option("deps.json", "--output", "-o", help="Output dependency map file path"),
    framework: str = typer.Option("auto", "--framework", "-f", help="Framework to detect (auto, fastapi, flask, django, express)"),
):
    """
    Build dependency map from codebase.
    """
    import json
    from .dependency_mapper import DependencyMapper
    
    project_path = Path(project).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]🔍 Building dependency map from codebase...[/cyan]")
    console.print(f"[dim]Project: {project_path}[/dim]")
    console.print()
    
    mapper = DependencyMapper(str(project_path))
    deps = mapper.build_from_codebase(framework=framework)
    
    # Save to file
    output_path = Path(output)
    with open(output_path, 'w') as f:
        json.dump(deps, f, indent=2)
    
    console.print(f"[green]✓ Dependency map saved to {output_path}[/green]")
    console.print(f"[dim]Services: {len(deps.get('services', {}))}[/dim]")
    console.print(f"[dim]Files: {len(deps.get('files', {}))}[/dim]")


@app.command()
def version():
    """Show WUP version."""
    from . import __version__
    console.print(f"[bold cyan]WUP[/bold cyan] version [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
