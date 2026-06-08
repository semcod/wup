"""Init CLI testing setup — domain logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wup.cli_config_generator import CLIConfigGenerator
from wup.cli_scanner import CLIScanner
from wup.testql_cli_generator import TestQLCLIGenerator


def setup_cli_project(
    project_root: str | Path,
    *,
    output_config: str | Path | None = None,
    output_scenarios: str | Path | None = None,
    merge: bool = False,
    infer_args: bool = True,
) -> dict[str, Any]:
    """Scan CLI commands and generate wup.yaml + TestQL scenarios."""
    project = Path(project_root).expanduser().resolve()
    if not project.exists():
        return {"ok": False, "error": f"project not found: {project}"}

    scanner = CLIScanner(str(project))
    packages = scanner.scan()
    if not packages:
        return {
            "ok": False,
            "error": "no CLI packages found",
            "project": str(project),
        }

    config_path = Path(output_config) if output_config else project / "wup.yaml"
    if not config_path.is_absolute():
        config_path = project / config_path

    config_generator = CLIConfigGenerator(str(project))
    config = config_generator.generate(output_path=config_path, merge_existing=merge)

    scenarios_path = Path(output_scenarios) if output_scenarios else project / "testql-scenarios"
    if not scenarios_path.is_absolute():
        scenarios_path = project / scenarios_path

    testql_generator = TestQLCLIGenerator(str(project))
    generated_files = testql_generator.generate(output_dir=scenarios_path, infer_args=infer_args)

    commands = sum(len(pkg.commands) for pkg in packages)
    return {
        "ok": True,
        "project": str(project),
        "packages": len(packages),
        "commands": commands,
        "config_output": str(config_path),
        "scenarios_dir": str(scenarios_path),
        "scenario_files": [str(p) for p in generated_files],
        "services": len(config.services),
        "merge": merge,
    }
