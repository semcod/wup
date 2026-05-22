"""CLI scanner for detecting CLI commands and entry points."""

from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class CLICommand:
    """Represents a detected CLI command."""
    name: str
    entry_point: str
    module: str
    function: str
    description: str = ""
    args: List[str] = field(default_factory=list)


@dataclass
class CLIPackage:
    """Represents a detected CLI package."""
    name: str
    commands: List[CLICommand] = field(default_factory=list)
    entry_points: Dict[str, str] = field(default_factory=dict)
    setup_files: List[Path] = field(default_factory=list)


class CLIScanner:
    """Scanner for detecting CLI commands in a project."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.packages: List[CLIPackage] = []

    def scan(self) -> List[CLIPackage]:
        """Scan project for CLI packages and commands."""
        self.packages = []

        # Scan for setup.py
        setup_py = self.project_root / "setup.py"
        if setup_py.exists():
            self._scan_setup_py(setup_py)

        # Scan for setup.cfg
        setup_cfg = self.project_root / "setup.cfg"
        if setup_cfg.exists():
            self._scan_setup_cfg(setup_cfg)

        # Scan for pyproject.toml
        pyproject_toml = self.project_root / "pyproject.toml"
        if pyproject_toml.exists():
            self._scan_pyproject_toml(pyproject_toml)

        # Scan for package directory with __main__.py
        self._scan_main_modules()

        return self.packages

    def _scan_setup_py(self, setup_py: Path) -> None:
        """Scan setup.py for entry points."""
        try:
            content = setup_py.read_text(encoding="utf-8")
            
            # Extract entry_points from setup() call
            entry_points_match = re.search(
                r'entry_points\s*=\s*{([^}]+)}',
                content,
                re.DOTALL
            )
            if entry_points_match:
                self._parse_entry_points_dict(entry_points_match.group(1), setup_py)
        except Exception:
            pass

    def _scan_setup_cfg(self, setup_cfg: Path) -> None:
        """Scan setup.cfg for entry points."""
        try:
            content = setup_cfg.read_text(encoding="utf-8")
            
            # Parse [options.entry_points] section
            in_entry_points = False
            current_section = None
            
            for line in content.splitlines():
                line = line.strip()
                
                if line.startswith("[options.entry_points"):
                    in_entry_points = True
                    continue
                
                if in_entry_points:
                    if line.startswith("[") and not line.startswith("[options.entry_points"):
                        in_entry_points = False
                        continue
                    
                    if "=" in line and not line.startswith("#"):
                        entry_point, value = line.split("=", 1)
                        entry_point = entry_point.strip()
                        value = value.strip()
                        
                        if current_section is None:
                            current_section = "console_scripts"
                        
                        self._add_entry_point(entry_point, value, current_section, setup_cfg)
        except Exception:
            pass

    def _scan_pyproject_toml(self, pyproject_toml: Path) -> None:
        """Scan pyproject.toml for entry points."""
        try:
            content = pyproject_toml.read_text(encoding="utf-8")
            
            # Parse [project.scripts] section (PEP 621)
            scripts_match = re.search(
                r'\[project\.scripts\](.*?)(?=\n\[|\Z)',
                content,
                re.DOTALL
            )
            if scripts_match:
                scripts_section = scripts_match.group(1)
                for line in scripts_section.splitlines():
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        name, value = line.split("=", 1)
                        name = name.strip()
                        value = value.strip().strip('"').strip("'")
                        self._add_entry_point(name, value, "console_scripts", pyproject_toml)

            # Also check for [tool.setuptools.dynamic] dependencies
            # This handles newer setuptools configurations
        except Exception:
            pass

    def _scan_main_modules(self) -> None:
        """Scan for packages with __main__.py files."""
        for pkg_dir in self.project_root.iterdir():
            if pkg_dir.is_dir() and not pkg_dir.name.startswith("_"):
                main_py = pkg_dir / "__main__.py"
                if main_py.exists():
                    # This package can be run as python -m package
                    self._add_entry_point(
                        pkg_dir.name,
                        f"{pkg_dir.name}.__main__:main",
                        "console_scripts",
                        main_py
                    )

    def _parse_entry_points_dict(self, dict_str: str, source: Path) -> None:
        """Parse entry points dictionary string."""
        try:
            # Simple parsing for entry points like:
            # 'console_scripts': ['cmd1 = module:function', 'cmd2 = module2:function']
            
            # Extract console_scripts section
            console_match = re.search(
                r'["\']console_scripts["\']\s*:\s*\[([^\]]+)\]',
                dict_str,
                re.DOTALL
            )
            if console_match:
                entries = console_match.group(1)
                for entry in re.findall(r'["\']([^"\']+)["\']\s*=\s*["\']([^"\']+)["\']', entries):
                    name, value = entry
                    self._add_entry_point(name, value, "console_scripts", source)
        except Exception:
            pass

    def _add_entry_point(self, name: str, value: str, section: str, source: Path) -> None:
        """Add an entry point to the packages list."""
        if section != "console_scripts":
            return

        # Parse module:function
        if ":" in value:
            module, function = value.rsplit(":", 1)
        else:
            module = value
            function = "main"

        # Find or create package
        package_name = self.project_root.name
        package = next((p for p in self.packages if p.name == package_name), None)
        
        if package is None:
            package = CLIPackage(name=package_name)
            package.setup_files.append(source)
            self.packages.append(package)

        # Add command
        command = CLICommand(
            name=name,
            entry_point=value,
            module=module,
            function=function
        )
        package.commands.append(command)
        package.entry_points[name] = value

    def infer_command_args(self, command: CLICommand) -> List[str]:
        """Infer command arguments by inspecting the module."""
        try:
            module_path = self._find_module_path(command.module)
            if not module_path:
                return []

            # Try to parse the module and extract function arguments
            content = module_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == command.function:
                    args = []
                    for arg in node.args.args:
                        args.append(arg.arg)
                    return args

            # Try running --help to get arguments
            return self._get_help_arguments(command.name)
        except Exception:
            return []

    def _find_module_path(self, module: str) -> Optional[Path]:
        """Find the Python file for a given module."""
        parts = module.replace(".", "/")
        
        # Try .py file
        py_path = self.project_root / f"{parts}.py"
        if py_path.exists():
            return py_path

        # Try __init__.py in package
        init_path = self.project_root / parts / "__init__.py"
        if init_path.exists():
            return init_path

        # Try in package directories
        for pkg_dir in self.project_root.iterdir():
            if pkg_dir.is_dir() and not pkg_dir.name.startswith("_"):
                py_path = pkg_dir / f"{parts}.py"
                if py_path.exists():
                    return py_path

                init_path = pkg_dir / parts / "__init__.py"
                if init_path.exists():
                    return init_path

        return None

    def _get_help_arguments(self, command_name: str) -> List[str]:
        """Get command arguments by running --help."""
        try:
            result = subprocess.run(
                [command_name, "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                # Parse help output for arguments
                args = []
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line.startswith("--") or line.startswith("-"):
                        # Extract argument name
                        arg_match = re.match(r'^(-{1,2}[\w-]+)', line)
                        if arg_match:
                            args.append(arg_match.group(1))
                return args
        except Exception:
            pass

        return []

    def to_dict(self) -> Dict:
        """Convert scan results to dictionary."""
        return {
            "packages": [
                {
                    "name": pkg.name,
                    "commands": [
                        {
                            "name": cmd.name,
                            "entry_point": cmd.entry_point,
                            "module": cmd.module,
                            "function": cmd.function,
                            "args": cmd.args,
                        }
                        for cmd in pkg.commands
                    ],
                    "entry_points": pkg.entry_points,
                }
                for pkg in self.packages
            ]
        }
