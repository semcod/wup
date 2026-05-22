"""Generator for TestQL scenarios for CLI testing."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .cli_scanner import CLIScanner, CLIPackage, CLICommand


class TestQLCLIGenerator:
    """Generate TestQL scenarios for CLI command testing."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.scanner = CLIScanner(project_root)

    def generate(
        self,
        output_dir: Optional[Path] = None,
        infer_args: bool = True,
    ) -> List[Path]:
        """Generate TestQL scenarios for CLI commands.

        Args:
            output_dir: Directory to save scenarios (default: testql-scenarios/)
            infer_args: If True, infer command arguments by inspection

        Returns:
            List of generated scenario file paths
        """
        # Scan for CLI commands
        packages = self.scanner.scan()

        if not packages:
            raise ValueError("No CLI packages found in project")

        # Set output directory
        if output_dir is None:
            output_dir = self.project_root / "testql-scenarios"

        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # Generate smoke test scenario
        smoke_file = self._generate_smoke_scenario(packages, output_dir)
        generated_files.append(smoke_file)

        # Generate individual command scenarios
        for package in packages:
            for command in package.commands:
                if infer_args:
                    command.args = self.scanner.infer_command_args(command)

                command_file = self._generate_command_scenario(
                    package, command, output_dir
                )
                generated_files.append(command_file)

        return generated_files

    def _generate_smoke_scenario(
        self, packages: List[CLIPackage], output_dir: Path
    ) -> Path:
        """Generate smoke test scenario for all commands."""
        output_path = output_dir / "cli-smoke.testql.toon.yaml"

        lines = [
            "# SCENARIO: CLI Smoke Tests",
            "# TYPE: cli",
            "# GENERATED: true",
            "",
            "CONFIG[2]{key, value}:",
            f"  cli_command, {packages[0].commands[0].name if packages and packages[0].commands else 'python -m'}",
            "  timeout_ms, 15000",
            "",
        ]

        # Add basic tests for each command
        for package in packages:
            for command in package.commands:
                lines.extend([
                    "",
                    f"# Test: {command.name} --help",
                    f'SHELL "{command.name} --help" 5000',
                    "ASSERT_EXIT_CODE 0",
                    "ASSERT_STDOUT_CONTAINS \"usage\"",
                ])

                lines.extend([
                    "",
                    f"# Test: {command.name} --version",
                    f'SHELL "{command.name} --version" 5000',
                    "ASSERT_EXIT_CODE 0",
                ])

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def _generate_command_scenario(
        self, package: CLIPackage, command: CLICommand, output_dir: Path
    ) -> Path:
        """Generate detailed test scenario for a single command."""
        safe_name = command.name.replace("-", "_").replace(" ", "_")
        output_path = output_dir / f"cli-{safe_name}.testql.toon.yaml"

        lines = [
            f"# SCENARIO: {command.name} Command Tests",
            "# TYPE: cli",
            "# GENERATED: true",
            "",
            "CONFIG[2]{key, value}:",
            f"  cli_command, {command.name}",
            "  timeout_ms, 30000",
            "",
            f"# Test 1: {command.name} --help",
            f'SHELL "{command.name} --help" 5000',
            "ASSERT_EXIT_CODE 0",
            "ASSERT_STDOUT_CONTAINS \"usage\"",
            "",
            f"# Test 2: {command.name} --version",
            f'SHELL "{command.name} --version" 5000',
            "ASSERT_EXIT_CODE 0",
            "",
        ]

        # Add tests for inferred arguments
        if command.args:
            lines.extend([
                f"# Test 3: {command.name} with arguments",
            ])
            
            # Test with first few arguments
            for arg in command.args[:3]:
                if arg.startswith("-"):
                    lines.extend([
                        f'SHELL "{command.name} {arg}" 10000',
                        "ASSERT_EXIT_CODE 0",
                    ])

        # Add test for invalid flag (should fail)
        lines.extend([
            "",
            f"# Test: {command.name} with invalid flag (should fail)",
            f'SHELL "{command.name} --invalid-flag-xyz123" 5000',
            "ASSERT_EXIT_CODE != 0",
        ])

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def generate_custom_scenario(
        self,
        commands: List[str],
        scenario_name: str = "custom-cli",
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Generate custom TestQL scenario for specific commands.

        Args:
            commands: List of command strings to test
            scenario_name: Name for the scenario file
            output_dir: Directory to save scenario

        Returns:
            Path to generated scenario file
        """
        if output_dir is None:
            output_dir = self.project_root / "testql-scenarios"

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{scenario_name}.testql.toon.yaml"

        lines = [
            f"# SCENARIO: {scenario_name}",
            "# TYPE: cli",
            "# GENERATED: true",
            "",
            "CONFIG[2]{key, value}:",
            "  cli_command, custom",
            "  timeout_ms, 30000",
            "",
        ]

        for i, cmd in enumerate(commands, 1):
            lines.extend([
                "",
                f"# Test {i}: {cmd}",
                f'SHELL "{cmd}" 15000',
                "ASSERT_EXIT_CODE 0",
            ])

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def print_summary(self, generated_files: List[Path]) -> None:
        """Print summary of generated scenarios."""
        from rich.console import Console
        from rich.table import Table

        console = Console()

        console.print("\n[bold green]✓ Generated TestQL scenarios[/bold green]\n")

        table = Table(title="Generated Scenarios")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="green")

        for file_path in generated_files:
            file_type = "Smoke" if "smoke" in file_path.name else "Command"
            table.add_row(file_path.name, file_type)

        console.print(table)
        console.print(f"\nOutput directory: {generated_files[0].parent if generated_files else 'N/A'}")
