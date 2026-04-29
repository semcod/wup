"""
CLI interface for WUP (What's Up) - Intelligent file watcher for regression testing.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .core import WupWatcher
from .dependency_mapper import DependencyMapper

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
    
    console.print(f"[bold cyan]🚀 WUP Watcher[/bold cyan]")
    console.print(f"[dim]Project: {project_path}[/dim]")
    console.print(f"[dim]CPU Throttle: {cpu_throttle * 100}%[/dim]")
    console.print(f"[dim]Debounce: {debounce}s[/dim]")
    console.print(f"[dim]Cooldown: {cooldown}s[/dim]")
    console.print()
    
    watcher = WupWatcher(
        project_root=str(project_path),
        deps_file=deps_file,
        cpu_throttle=cpu_throttle,
        debounce_seconds=debounce,
        test_cooldown_seconds=cooldown
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
):
    """
    Build dependency map by scanning the codebase.
    
    Maps files → endpoints → services for intelligent testing.
    """
    project_path = Path(project).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold cyan]🔍 Building dependency map[/bold cyan]")
    console.print(f"[dim]Project: {project_path}[/dim]")
    console.print(f"[dim]Framework: {framework}[/dim]")
    console.print()
    
    mapper = DependencyMapper(str(project_path))
    deps = mapper.build_from_codebase(framework)
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
):
    """
    Show dependency map status.
    """
    deps_path = Path(deps_file)
    
    if not deps_path.exists():
        console.print(f"[red]Error: Dependency file '{deps_file}' does not exist[/red]")
        console.print(f"[dim]Run 'wup map-deps' to create it[/dim]")
        raise typer.Exit(1)
    
    import json
    with open(deps_file) as f:
        deps = json.load(f)
    
    services = deps.get("services", {})
    files = deps.get("files", {})
    
    console.print(f"[bold cyan]📊 Dependency Map Status[/bold cyan]")
    console.print(f"[dim]File: {deps_file}[/dim]")
    console.print()
    console.print(f"[bold]Services:[/bold] {len(services)}")
    console.print(f"[bold]Files:[/bold] {len(files)}")
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
def version():
    """Show WUP version."""
    from . import __version__
    console.print(f"[bold cyan]WUP[/bold cyan] version [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
