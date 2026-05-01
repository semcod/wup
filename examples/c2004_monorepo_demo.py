#!/usr/bin/env python3
"""
Demo: WUP with c2004 Monorepo (Large Multi-Module Project)

This example shows how WUP handles a large monorepo with 20+ connect-* modules,
each having frontend (TypeScript) and backend (Python) components.

The c2004 project structure:
  connect-config/       - Configuration management
  connect-data/         - Data management
  connect-devtools/     - Developer tools
  connect-encoder/      - Encoder management
  connect-id/           - Identity/user management
  connect-live-protocol/- Live protocol handling
  connect-manager/      - Test manager
  connect-menu-editor/  - Menu editor
  connect-menu-tree/    - Menu tree
  connect-reports/      - Reports
  connect-router/       - Router
  connect-scenario/     - Scenario management
  connect-template/     - Templates
  connect-template2/    - Templates v2
  connect-test/         - Testing module
  connect-test-device/  - Device testing
  connect-test-full/    - Full testing
  connect-workshop/     - Workshop management

Usage:
  python3 examples/c2004_monorepo_demo.py
  python3 examples/c2004_monorepo_demo.py /path/to/c2004
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wup.config import load_config
from wup.core import WupWatcher


def _discover_modules(project_root: Path) -> list:
    """Step 1: Discover and print connect-* module names."""
    modules = sorted(
        item.name for item in project_root.iterdir()
        if item.is_dir() and item.name.startswith("connect-")
    )
    print(f"✓ Found {len(modules)} connect-* modules:")
    for mod in modules:
        print(f"  • {mod}")
    print()
    return modules


def _print_config_summary(config) -> None:
    """Step 2: Print WUP configuration summary."""
    print(f"✓ Project name: {config.project.name}")
    print(f"✓ Watch paths: {len(config.watch.paths)} patterns")
    for path in config.watch.paths[:5]:
        print(f"  • {path}")
    if len(config.watch.paths) > 5:
        print(f"  ... and {len(config.watch.paths) - 5} more")
    print()


def _analyze_module(module_path: Path) -> dict:
    """Return analysis dict for a single connect-* module."""
    analysis = {
        "has_frontend": (module_path / "frontend").exists(),
        "has_backend": (module_path / "backend").exists(),
        "has_tests": (module_path / "tests").exists(),
        "frontend_files": 0,
        "backend_files": 0,
    }
    if analysis["has_frontend"]:
        analysis["frontend_files"] = len(list((module_path / "frontend").rglob("*.ts*")))
    if analysis["has_backend"]:
        analysis["backend_files"] = len(list((module_path / "backend").rglob("*.py")))
    return analysis


def _analyze_module_structure(project_root: Path, modules: list) -> dict:
    """Step 3: Analyze and print structure of up to 5 modules."""
    module_analysis = {mod: _analyze_module(project_root / mod) for mod in modules[:5]}
    print(f"✓ Analyzed {len(module_analysis)} modules:")
    for mod, info in module_analysis.items():
        parts = []
        if info["has_frontend"]:
            parts.append(f"frontend ({info['frontend_files']} files)")
        if info["has_backend"]:
            parts.append(f"backend ({info['backend_files']} files)")
        if info["has_tests"]:
            parts.append("tests")
        print(f"  • {mod}: {', '.join(parts) if parts else 'no code files'}")
    print()
    return module_analysis


def _test_file_inference(project_root: Path, config) -> None:
    """Step 4: Test service inference for sample files."""
    watcher = WupWatcher(str(project_root), config=config)
    test_files = [
        "connect-config/backend/config_service.py",
        "connect-data/frontend/src/components/DataTable.tsx",
        "connect-test/backend/test_runner.py",
    ]
    for test_file in test_files:
        service = watcher.infer_service(str(project_root / test_file))
        print(f"  • {test_file}")
        print(f"    → Service: {service or 'None (no matching config)'}")
    print()


def _print_endpoints_summary(config) -> None:
    """Step 5: Print TestQL endpoint summary if configured."""
    if not (config.testql and config.testql.explicit_endpoints):
        return
    endpoints = config.testql.explicit_endpoints
    print(f"✓ {len(endpoints)} endpoints configured")
    for ep in endpoints[:5]:
        print(f"  • {ep}")
    if len(endpoints) > 5:
        print(f"  ... and {len(endpoints) - 5} more")
    print()


def _print_recommendations() -> None:
    """Steps 6–7: Print performance tips and CLI commands."""
    print("⚡ Performance Recommendations for Large Monorepo:")
    print("-" * 70)
    print("  1. Use specific file_types in wup.yaml (e.g., .py, .ts, .tsx)")
    print("  2. Set appropriate debounce (3-5s recommended)")
    print("  3. Use CPU throttle (0.5-0.7) to avoid impacting IDE")
    print("  4. Exclude node_modules, __pycache__, .git")
    print("  5. Consider excluding large auto-generated files")
    print("  6. Use visual_diff.pages_from_endpoints to limit DOM scans")
    print()
    print("🚀 CLI Commands for c2004:")
    print("-" * 70)
    print()
    print("   # Initialize WUP configuration")
    print("   cd /home/tom/github/maskservice/c2004")
    print("   wup init")
    print()
    print("   # Start watching with dashboard")
    print("   wup watch . --dashboard --cpu-throttle 0.6")
    print()
    print("   # Watch specific modules only")
    print("   wup watch . --config .wup-connect-config.yaml")
    print()
    print("   # Run with TestQL mode")
    print("   wup watch . --mode testql")
    print()


def analyze_monorepo(project_path: str):
    """Analyze c2004-style monorepo structure."""
    print("=" * 70)
    print("🏢 WUP + c2004 Monorepo Analysis")
    print("=" * 70)
    print()

    project_root = Path(project_path)
    if not project_root.exists():
        print(f"❌ Project path not found: {project_path}")
        print("Using simulation mode...")
        return simulate_monorepo()

    print(f"📁 Analyzing monorepo: {project_path}")
    print()

    print("🔍 Step 1: Discovering connect-* modules...")
    modules = _discover_modules(project_root)

    print("🔍 Step 2: Checking WUP configuration...")
    config = load_config(project_root)
    _print_config_summary(config)

    print("🔍 Step 3: Analyzing module structure...")
    _analyze_module_structure(project_root, modules)

    print("🔍 Step 4: Testing file change inference...")
    _test_file_inference(project_root, config)

    print("🔍 Step 5: TestQL endpoints configured:")
    _print_endpoints_summary(config)

    _print_recommendations()

    print("=" * 70)
    print("✅ Monorepo analysis complete!")
    print("=" * 70)


def simulate_monorepo():
    """Simulate monorepo analysis when path not available."""
    
    print("(Running in simulation mode)")
    print()
    
    # Simulated module list
    connect_modules = [
        "connect-config", "connect-data", "connect-devtools",
        "connect-encoder", "connect-id", "connect-live-protocol",
        "connect-manager", "connect-menu-editor", "connect-menu-tree",
        "connect-reports", "connect-router", "connect-scenario",
        "connect-template", "connect-template2", "connect-test",
        "connect-test-device", "connect-test-full", "connect-workshop",
    ]
    
    print(f"✓ Simulated {len(connect_modules)} connect-* modules")
    for mod in connect_modules:
        print(f"  • {mod}")
    print()
    
    print("✓ Simulated watch patterns:")
    print("  • connect-*/frontend/src/**")
    print("  • connect-*/backend/**/*.py")
    print("  • app/**")
    print("  • src/**")
    print()
    
    print("✓ Simulated test endpoints: 148 endpoints configured")
    print()
    
    print("=" * 70)
    print("✅ Simulation complete!")
    print("=" * 70)


def main():
    import sys
    
    # Default to c2004 directory
    project_path = sys.argv[1] if len(sys.argv) > 1 else "/home/tom/github/maskservice/c2004"
    
    analyze_monorepo(project_path)


if __name__ == "__main__":
    main()
