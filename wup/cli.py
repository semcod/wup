"""
CLI interface for WUP (What's Up) - Intelligent file watcher for regression testing.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .config import find_config_file, load_config
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


def _load_watch_config(
    project_path: Path,
    config_path: Optional[Path],
    probe_interval: Optional[int],
    mode: str,
) -> WupConfig:
    """Load wup.yaml config and apply CLI probe_interval override."""
    loaded_wup_config = load_config(project_path, config_path)
    if probe_interval is not None:
        loaded_wup_config.testql.probe_interval_s = int(probe_interval)
    elif mode.lower() == "testql" and not loaded_wup_config.testql.probe_interval_s:
        loaded_wup_config.testql.probe_interval_s = 60
    return loaded_wup_config


def _print_watch_header(
    wup_config: WupConfig,
    cpu_throttle: float,
    debounce: int,
    cooldown: int,
    config_path: Optional[Path],
) -> None:
    """Print watcher startup banner."""
    console.print(f"[bold cyan]🚀 WUP Watcher[/bold cyan]")
    console.print(f"[dim]Project: {wup_config.project.name}[/dim]")
    console.print(f"[dim]Description: {wup_config.project.description}[/dim]")
    console.print(f"[dim]CPU Throttle: {cpu_throttle * 100}%[/dim]")
    console.print(f"[dim]Debounce: {debounce}s[/dim]")
    console.print(f"[dim]Cooldown: {cooldown}s[/dim]")
    if wup_config.testql.probe_interval_s:
        console.print(f"[dim]Live probes: every {wup_config.testql.probe_interval_s}s[/dim]")
    console.print(f"[dim]Config: {config_path or 'auto-detected'}[/dim]")
    console.print()


def _refresh_monitoring_manifest(
    project_path: Path,
    wup_config: WupConfig,
    cfg_path: Optional[Path],
) -> None:
    """Rebuild and patch monitoring manifest into wup.yaml when possible."""
    if not cfg_path:
        return
    from .monitoring_manifest import build_monitoring_manifest, patch_wup_yaml_monitoring
    try:
        manifest = build_monitoring_manifest(project_path, wup_config)
        patch_wup_yaml_monitoring(cfg_path, manifest)
        console.print("[dim]Refreshed monitoring manifest in wup.yaml[/dim]")
    except OSError as exc:
        console.print(f"[yellow]Could not refresh monitoring manifest: {exc}[/yellow]")


def _create_watcher(
    mode: str,
    project_path: Path,
    deps_file: str,
    cpu_throttle: float,
    debounce: int,
    cooldown: int,
    scenarios_dir: Optional[str],
    testql_bin: str,
    browser_service_url: Optional[str],
    track_dir: str,
    quick_limit: int,
    config: WupConfig,
) -> WupWatcher:
    """Instantiate the correct watcher class for the chosen mode."""
    if mode.lower() == "testql":
        tq_watcher = TestQLWatcher(
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
            config=config,
        )
        console.print("[green]TestQL mode enabled[/green]")
        return tq_watcher

    return WupWatcher(
        project_root=str(project_path),
        deps_file=deps_file,
        cpu_throttle=cpu_throttle,
        debounce_seconds=debounce,
        test_cooldown_seconds=cooldown,
        config=config,
    )


@app.command()
def watch(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    deps_file: str = typer.Option("deps.json", "--deps", "-d", help="Path to dependency map file"),
    cpu_throttle: float = typer.Option(0.8, "--cpu-throttle", "-c", help="CPU usage threshold (0.0-1.0)"),
    debounce: int = typer.Option(2, "--debounce", "-b", help="Debounce time in seconds"),
    cooldown: int = typer.Option(300, "--cooldown", "-t", help="Test cooldown in seconds"),
    dashboard: bool = typer.Option(False, "--dashboard", help="Enable live dashboard"),
    mode: str = typer.Option(
        "testql",
        "--mode",
        help="Watcher mode: testql (default) or default (HTTP-only, no TestQL)",
    ),
    scenarios_dir: Optional[str] = typer.Option(
        None,
        "--scenarios-dir",
        help="TestQL scenarios directory (default: testql.scenario_dir from wup.yaml)",
    ),
    testql_bin: str = typer.Option("testql", "--testql-bin", help="TestQL executable name/path"),
    browser_service_url: Optional[str] = typer.Option(None, "--browser-service-url", help="HTTP endpoint for browser notifications"),
    track_dir: str = typer.Option(".wup/tracks", "--track-dir", help="Directory where error track JSON files are written"),
    quick_limit: int = typer.Option(3, "--quick-limit", help="Maximum TestQL scenarios used in quick pass"),
    probe_interval: Optional[int] = typer.Option(
        None,
        "--probe-interval",
        help="Periodic live HTTP probes in seconds (default: 60 in testql mode, or testql.probe_interval_s from wup.yaml; use 0 to disable)",
    ),
    config: Optional[str] = typer.Option(None, "--config", "-C", help="Path to wup.yaml config file"),
):
    """
    Watch project for file changes and run regression tests.

    Defaults (no extra flags): ``--mode testql`` and live probes every **60s**
    (unless ``testql.probe_interval_s`` is set in wup.yaml). Use
    ``--mode default`` for the legacy HTTP-only watcher without TestQL.

    If wup.yaml doesn't exist, it will be auto-generated based on project detection.
    """
    project_path = Path(project).resolve()

    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)

    config_path = Path(config) if config else None

    # Auto-generate config if it doesn't exist
    if not find_config_file(project_path):
        console.print("[cyan]🔍 No wup.yaml found - auto-detecting project type...[/cyan]")
        _auto_generate_config(project_path, mode)
        console.print("[green]✓ Auto-generated wup.yaml configuration[/green]")
        console.print()

    wup_config = _load_watch_config(project_path, config_path, probe_interval, mode)
    effective_scenarios_dir = scenarios_dir or wup_config.testql.scenario_dir

    _print_watch_header(wup_config, cpu_throttle, debounce, cooldown, config_path)

    cfg_path = config_path if config_path and config_path.exists() else find_config_file(project_path)
    _refresh_monitoring_manifest(project_path, wup_config, cfg_path)

    watcher = _create_watcher(
        mode=mode,
        project_path=project_path,
        deps_file=deps_file,
        cpu_throttle=cpu_throttle,
        debounce=debounce,
        cooldown=cooldown,
        scenarios_dir=effective_scenarios_dir,
        testql_bin=testql_bin,
        browser_service_url=browser_service_url,
        track_dir=track_dir,
        quick_limit=quick_limit,
        config=wup_config,
    )

    if dashboard:
        console.print("[green]Starting watcher with live dashboard...[/green]")
        asyncio.run(watcher.run_with_dashboard())
    else:
        console.print("[green]Starting watcher...[/green]")
        watcher.start_watching()


def _auto_generate_config(project_path: Path, mode: str):
    """Auto-generate wup.yaml based on project detection."""
    from .cli_scanner import CLIScanner
    from .cli_config_generator import CLIConfigGenerator
    from .config import save_config, get_default_config

    # Try CLI detection first
    scanner = CLIScanner(str(project_path))
    packages = scanner.scan()

    if packages:
        console.print("[cyan]📦 Detected CLI package(s)[/cyan]")
        for pkg in packages:
            console.print(f"  - {pkg.name}: {len(pkg.commands)} command(s)")
        console.print()

        # Use CLI config generator
        generator = CLIConfigGenerator(str(project_path))
        generator.generate()
    else:
        # Use default config for web/mixed projects
        console.print("[cyan]🌐 Using default configuration for web/mixed projects[/cyan]")
        config = get_default_config(project_path)
        save_config(config, project_path / "wup.yaml")


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
    
    from .cli_bridge import run_map_deps

    result = run_map_deps(project=str(project_path), out=output, framework=framework)
    if not result.get("ok"):
        console.print(f"[red]Error: {result.get('error', 'map-deps failed')}[/red]")
        raise typer.Exit(1)

    data = result.get("data") or {}
    services_count = data.get("services", 0)
    files_count = data.get("files", 0)
    services = {}
    files = {}
    try:
        import json
        deps_payload = json.loads(result.get("output") or "{}")
        services = deps_payload.get("services", {})
        files = deps_payload.get("files", {})
    except json.JSONDecodeError:
        services = {}
        files = {}
    
    console.print(f"[green]✓ Dependency map saved to {output}[/green]")
    console.print(f"[dim]Services found: {services_count or len(services)}[/dim]")
    console.print(f"[dim]Files mapped: {files_count or len(files)}[/dim]")
    console.print()
    
    if services:
        console.print("[bold]Services:[/bold]")
        for service, info in sorted(services.items()):
            console.print(f"  [cyan]{service}[/cyan]: {len(info.get('endpoints', []))} endpoints, {len(info.get('files', []))} files")


def _add_failing_services_lines(lines: list, health_state_path: Path, failed_only: bool, watch: bool) -> None:
    """Read failing services from health state and add display lines."""
    import json
    from rich.text import Text
    
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


def _add_delta_events_lines(lines: list, health_events_path: Path, delta_seconds: int, watch: bool, ts: float) -> None:
    """Read recent health transition events and add display lines."""
    import json
    from rich.text import Text

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


def _add_monitoring_manifest_lines(lines: list, config_path: Optional[Path], project_path: Path) -> None:
    """Load monitoring manifest and add display lines."""
    from rich.text import Text
    
    manifest_path = config_path if config_path and config_path.exists() else find_config_file(project_path)
    if manifest_path:
        from .monitoring_manifest import load_monitoring_manifest_from_yaml

        manifest = load_monitoring_manifest_from_yaml(manifest_path)
        if manifest:
            lines.append(Text(""))
            lines.append(Text.from_markup("[bold]Configured monitoring (wup.yaml):[/bold]"))
            lines.append(Text.from_markup(
                f"  [dim]manifest {manifest.get('generated_at', '?')} · "
                f"probe {manifest.get('probe_interval_s', 0)}s[/dim]"
            ))
            for svc, info in sorted((manifest.get("wup_services") or {}).items()):
                probes = info.get("live_probes") or []
                dockers = info.get("docker") or []
                lines.append(Text.from_markup(
                    f"  [cyan]{svc}[/cyan]: {len(probes)} probe(s), docker: "
                    + ", ".join(
                        d.get("compose_service", "?") for d in dockers[:4]
                    )
                    + ("…" if len(dockers) > 4 else "")
                ))
            lines.append(Text.from_markup(
                "  [dim]Pełna lista: sekcja monitoring: w wup.yaml (BEGIN WUP MONITORING MANIFEST)[/dim]"
            ))


def _add_visual_diff_lines(lines: list, wup_config: WupConfig, project_path: Path, delta_seconds: int, watch: bool) -> None:
    """Read recent visual diff records and add display lines."""
    from rich.text import Text

    if wup_config.visual_diff and wup_config.visual_diff.enabled:
        from .visual_diff import VisualDiffer
        differ = VisualDiffer(str(project_path), wup_config.visual_diff)
        effective_delta = delta_seconds if delta_seconds > 0 else (30 if watch else 0)
        vd_seconds = effective_delta if effective_delta > 0 else 300
        recent_vd = differ.get_recent_diffs(vd_seconds)
        lines.append(Text(""))
        lines.append(Text.from_markup(f"[bold]Visual DOM diffs (last {vd_seconds}s):[/bold]"))
        if not recent_vd:
            lines.append(Text.from_markup("  [dim]No DOM changes detected[/dim]"))
        else:
            for entry in recent_vd[:10]:
                url = entry.get("url", "?")
                diff = entry.get("diff", {})
                counts = diff.get("counts", {})
                status = diff.get("status", "?")
                color = "yellow" if status == "changed" else "dim green"
                lines.append(Text.from_markup(
                    f"  [{color}]{url}[/{color}]  "
                    f"+{counts.get('added', 0)} -{counts.get('removed', 0)} ~{counts.get('changed_attrs', 0)}"
                ))


def _build_status_panel(
    ts: float,
    project_path: Path,
    wup_config: WupConfig,
    config_path: Optional[Path],
    health_state_path: Path,
    health_events_path: Path,
    delta_seconds: int,
    failed_only: bool,
    watch: bool,
) -> "Group":
    """Construct status Rich Panel content by delegating to specialized helper functions."""
    import time
    from rich.console import Group
    from rich.text import Text
    
    lines: list = []

    # header
    lines.append(Text.from_markup(
        f"[bold cyan]📊 WUP Status[/bold cyan]  "
        f"[dim]{wup_config.project.name}[/dim]  "
        f"[dim]updated {time.strftime('%H:%M:%S', time.localtime(ts))}[/dim]"
    ))

    _add_failing_services_lines(lines, health_state_path, failed_only, watch)
    _add_delta_events_lines(lines, health_events_path, delta_seconds, watch, ts)
    _add_monitoring_manifest_lines(lines, config_path, project_path)
    _add_visual_diff_lines(lines, wup_config, project_path, delta_seconds, watch)

    return Group(*lines)


@app.command()
def status(
    deps_file: str = typer.Option("deps.json", "--deps", "-d", help="Path to dependency map file"),
    config: Optional[str] = typer.Option(None, "--config", "-C", help="Path to wup.yaml config file"),
    delta_seconds: int = typer.Option(0, "--delta-seconds", help="Show only service health transitions from last N seconds"),
    failed_only: bool = typer.Option(False, "--failed-only", help="Show only currently failing services"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Live mode: refresh display in real time"),
    interval: int = typer.Option(5, "--interval", "-i", help="Refresh interval in seconds for --watch mode"),
    json_out: bool = typer.Option(False, "--json", help="Emit STATUS snapshot as JSON via dsl2wup bus"),
):
    """
    Show dependency map status and configuration.
    """
    import time

    project_path = Path(".").resolve()
    config_path = Path(config) if config else None

    if json_out:
        import json as json_mod
        from .cli_bridge import run_status

        result = run_status(
            project=str(project_path),
            deps_file=deps_file,
            config_file=str(config_path) if config_path else "",
            delta_seconds=delta_seconds,
            failed_only=failed_only,
        )
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        raise typer.Exit(0 if result.get("ok") else 1)

    wup_config = load_config(project_path, config_path)
    from .paths import health_events_path as _health_events_path
    from .paths import health_state_path as _health_state_path

    state_path = _health_state_path(project_path)
    events_path = _health_events_path(project_path)

    if not watch:
        console.print(_build_status_panel(
            time.time(),
            project_path,
            wup_config,
            config_path,
            state_path,
            events_path,
            delta_seconds,
            failed_only,
            watch,
        ))
        return

    # --- live / watch mode ---
    from rich.live import Live
    try:
        with Live(
            _build_status_panel(
                time.time(),
                project_path,
                wup_config,
                config_path,
                state_path,
                events_path,
                delta_seconds,
                failed_only,
                watch,
            ),
            refresh_per_second=1,
            console=console,
        ) as live:
            while True:
                time.sleep(interval)
                live.update(
                    _build_status_panel(
                        time.time(),
                        project_path,
                        wup_config,
                        config_path,
                        state_path,
                        events_path,
                        delta_seconds,
                        failed_only,
                        watch,
                    )
                )
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
    from .cli_bridge import run_init

    init_project_path = Path(project).resolve()

    if not init_project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)

    result = run_init(project=str(init_project_path), out=output)
    if not result.get("ok"):
        console.print(f"[red]Error: {result.get('error', 'init failed')}[/red]")
        raise typer.Exit(1)

    output_path = Path((result.get("data") or {}).get("output") or output)
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
    from rich.table import Table
    
    scenarios_path = Path(scenarios_dir)
    
    if not scenarios_path.exists():
        console.print(f"[red]Error: Scenarios directory '{scenarios_dir}' does not exist[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]🔍 Discovering endpoints from TestQL scenarios...[/cyan]")
    console.print(f"[dim]Scenarios directory: {scenarios_dir}[/dim]")
    console.print()
    
    from .cli_bridge import run_endpoints

    result = run_endpoints(scenarios_dir=scenarios_dir, out=output, testql_bin=testql_bin)
    if not result.get("ok"):
        console.print(f"[red]Error: {result.get('error', 'endpoints discovery failed')}[/red]")
        raise typer.Exit(1)

    data = result.get("data") or {}
    dependency_map = data.get("map") or {}

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
    
    console.print(f"[green]✓ Dependency map saved to {data.get('output', output)}[/green]")


@app.command("sync-testql")
def sync_testql(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    write: bool = typer.Option(False, "--write", "-w", help="Write monitoring manifest block into wup.yaml"),
    merge_endpoints: bool = typer.Option(
        False,
        "--merge-endpoints",
        help="Also merge discovered paths into testql.endpoints_by_service (rewrites YAML body)",
    ),
    config: Optional[str] = typer.Option(None, "--config", "-C", help="Path to wup.yaml config file"),
):
    """
    Discover monitoring targets and document them in wup.yaml.

    With ``--write``, appends/updates the auto-generated ``monitoring:`` block
    (Docker Compose services, live HTTP probes, sources). Use this to verify
    whether a failure is a WUP config gap vs a down container.

    Use ``--merge-endpoints`` cautiously — it re-serializes wup.yaml (may drop comments).
    """
    import json

    from .config import find_config_file, load_config
    from .monitoring_manifest import (
        MANIFEST_BEGIN,
        build_monitoring_manifest,
        format_manifest_summary,
        patch_wup_yaml_monitoring,
    )
    from .testql_monitor import TestQLMonitor

    project_path = Path(project).resolve()
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)

    config_path = Path(config) if config else find_config_file(project_path)
    wup_config = load_config(project_path, config_path)
    monitor = TestQLMonitor(project_path, wup_config)
    suggested = monitor.suggested_endpoints_by_service()
    manifest = build_monitoring_manifest(project_path, wup_config)

    console.print("[bold]Monitoring manifest (preview):[/bold]")
    console.print(format_manifest_summary(manifest))

    if suggested:
        console.print()
        console.print("[bold]Suggested testql.endpoints_by_service additions:[/bold]")
        console.print(json.dumps(suggested, indent=2))

    if not write:
        console.print()
        console.print("[dim]Run: wup sync-testql . --write  → dokumentacja w wup.yaml[/dim]")
        return

    if config_path is None:
        console.print("[red]No wup.yaml found — run `wup init` first[/red]")
        raise typer.Exit(1)

    from .cli_bridge import run_sync

    if merge_endpoints and suggested:
        console.print("[yellow]Merging endpoints_by_service (review git diff for comment loss)[/yellow]")

    result = run_sync(
        project=str(project_path),
        file=str(config_path),
        merge_endpoints=merge_endpoints and bool(suggested),
    )
    if not result.get("ok"):
        console.print(f"[red]Error: {result.get('error', 'sync failed')}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ monitoring manifest written to {config_path}[/green]")
    console.print(f"[dim]Szukaj w pliku: {MANIFEST_BEGIN}[/dim]")


@app.command()
def assistant(
    quick: bool = typer.Option(False, "--quick", "-q", help="Non-interactive mode with auto-detected values"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Framework template (fastapi, flask, django, express)"),
    project: str = typer.Argument(".", help="Path to the project root directory"),
):
    """
    Interactive configuration assistant for wup.yaml.
    
    Guides you through setting up services, file watching, TestQL integration,
    web dashboard, and visual diff with intelligent suggestions.
    
    Examples:
        wup assistant                    # Interactive mode
        wup assistant --quick            # Auto-detect and save
        wup assistant --template fastapi # Use FastAPI defaults
    """
    project_path = Path(project).resolve()
    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)

    if quick or template:
        from .cli_bridge import run_generate

        hint = template or "quick setup"
        result = run_generate(
            project=str(project_path),
            hint=hint,
            out="wup.yaml",
            template=template or "",
        )
        if not result.get("ok"):
            console.print(f"[red]Error: {result.get('error', 'generate failed')}[/red]")
            raise typer.Exit(1)
        data = result.get("data") or {}
        console.print(
            f"[green]✓ Quick setup complete — {data.get('services', '?')} service(s), "
            f"framework {data.get('framework', '?')}[/green]"
        )
        return

    from .assistant import WupAssistant

    assistant = WupAssistant(str(project_path))
    assistant.run(quick=False, template=template)


@app.command()
def version():
    """Show WUP version."""
    from . import __version__
    console.print(f"[bold cyan]WUP[/bold cyan] version [green]{__version__}[/green]")


@app.command("init-cli")
def init_cli(
    project: str = typer.Argument(".", help="Path to the project root directory"),
    output_config: Optional[str] = typer.Option(None, "--output-config", "-c", help="Path for wup.yaml output"),
    output_scenarios: Optional[str] = typer.Option(None, "--output-scenarios", "-s", help="Path for testql-scenarios directory"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merge with existing wup.yaml"),
    infer_args: bool = typer.Option(True, "--infer-args/--no-infer-args", help="Infer command arguments by inspection"),
):
    """
    Automatically generate wup.yaml configuration and TestQL scenarios for CLI/shell services.

    Scans the project for CLI commands (entry points, setup.py, pyproject.toml) and generates:
    - wup.yaml with shell service configuration
    - TestQL scenarios in testql-scenarios/ directory

    Example:
        wup init-cli ./my-project
        wup init-cli ./my-project --merge
    """
    project_path = Path(project).resolve()

    if not project_path.exists():
        console.print(f"[red]Error: Project path '{project}' does not exist[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]🔍 Scanning project for CLI commands...[/cyan]")
    console.print(f"[dim]Project: {project_path}[/dim]\n")

    from .cli_bridge import run_init_cli

    try:
        result = run_init_cli(
            project=str(project_path),
            out=output_config or "wup.yaml",
            scenarios=output_scenarios or "testql-scenarios",
            merge=merge,
            infer_args=infer_args,
        )
        if not result.get("ok"):
            err = result.get("error", "init-cli failed")
            if "no CLI packages" in str(err).lower():
                console.print("[yellow]⚠ No CLI packages found in project[/yellow]")
                console.print("[dim]Looking for: setup.py, pyproject.toml, or packages with __main__.py[/dim]")
            else:
                console.print(f"[red]Error: {err}[/red]")
            raise typer.Exit(1)

        data = result.get("data") or {}
        console.print(f"[green]✓ Found {data.get('packages', 0)} package(s), {data.get('commands', 0)} command(s)[/green]")
        console.print(f"[green]✓ Config: {data.get('config_output')}[/green]")
        console.print(f"[green]✓ Scenarios: {len(data.get('scenario_files', []))} file(s) in {data.get('scenarios_dir')}[/green]")
        console.print()
        console.print("[bold green]✅ CLI testing setup complete![/bold green]")
        console.print()
        console.print("[dim]Next steps:[/dim]")
        console.print("  1. Review generated wup.yaml")
        console.print("  2. Review testql-scenarios/*.testql.toon.yaml")
        console.print("  3. Run: wup watch . --mode testql")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
