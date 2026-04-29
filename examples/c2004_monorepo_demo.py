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
from wup.dependency_mapper import DependencyMapper


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
    
    # Step 1: Discover connect-* modules
    print("🔍 Step 1: Discovering connect-* modules...")
    connect_modules = []
    for item in project_root.iterdir():
        if item.is_dir() and item.name.startswith("connect-"):
            connect_modules.append(item.name)
    
    connect_modules.sort()
    print(f"✓ Found {len(connect_modules)} connect-* modules:")
    for mod in connect_modules:
        print(f"  • {mod}")
    print()
    
    # Step 2: Check for wup.yaml configuration
    print("🔍 Step 2: Checking WUP configuration...")
    config = load_config(project_root)
    
    print(f"✓ Project name: {config.project.name}")
    print(f"✓ Watch paths: {len(config.watch.paths)} patterns")
    for path in config.watch.paths[:5]:
        print(f"  • {path}")
    if len(config.watch.paths) > 5:
        print(f"  ... and {len(config.watch.paths) - 5} more")
    print()
    
    # Step 3: Analyze module structure
    print("🔍 Step 3: Analyzing module structure...")
    module_analysis = {}
    
    for module in connect_modules[:5]:  # Analyze first 5 for demo
        module_path = project_root / module
        analysis = {
            "has_frontend": (module_path / "frontend").exists(),
            "has_backend": (module_path / "backend").exists(),
            "has_tests": (module_path / "tests").exists(),
            "frontend_files": 0,
            "backend_files": 0,
        }
        
        if analysis["has_frontend"]:
            frontend_path = module_path / "frontend"
            analysis["frontend_files"] = len(list(frontend_path.rglob("*.ts*")))
        
        if analysis["has_backend"]:
            backend_path = module_path / "backend"
            analysis["backend_files"] = len(list(backend_path.rglob("*.py")))
        
        module_analysis[module] = analysis
    
    print(f"✓ Analyzed {len(module_analysis)} modules:")
    for mod, analysis in module_analysis.items():
        parts = []
        if analysis["has_frontend"]:
            parts.append(f"frontend ({analysis['frontend_files']} files)")
        if analysis["has_backend"]:
            parts.append(f"backend ({analysis['backend_files']} files)")
        if analysis["has_tests"]:
            parts.append("tests")
        print(f"  • {mod}: {', '.join(parts) if parts else 'no code files'}")
    print()
    
    # Step 4: Simulate file change detection
    print("🔍 Step 4: Testing file change inference...")
    watcher = WupWatcher(str(project_root), config=config)
    
    test_files = [
        "connect-config/backend/config_service.py",
        "connect-data/frontend/src/components/DataTable.tsx",
        "connect-test/backend/test_runner.py",
    ]
    
    for test_file in test_files:
        full_path = str(project_root / test_file)
        service = watcher.infer_service(full_path)
        print(f"  • {test_file}")
        print(f"    → Service: {service or 'None (no matching config)'}")
    print()
    
    # Step 5: Show test endpoints from config
    if config.testql and config.testql.explicit_endpoints:
        print("🔍 Step 5: TestQL endpoints configured:")
        print(f"✓ {len(config.testql.explicit_endpoints)} endpoints configured")
        for ep in config.testql.explicit_endpoints[:5]:
            print(f"  • {ep}")
        if len(config.testql.explicit_endpoints) > 5:
            print(f"  ... and {len(config.testql.explicit_endpoints) - 5} more")
        print()
    
    # Step 6: Performance recommendations
    print("⚡ Performance Recommendations for Large Monorepo:")
    print("-" * 70)
    print("  1. Use specific file_types in wup.yaml (e.g., .py, .ts, .tsx)")
    print("  2. Set appropriate debounce (3-5s recommended)")
    print("  3. Use CPU throttle (0.5-0.7) to avoid impacting IDE")
    print("  4. Exclude node_modules, __pycache__, .git")
    print("  5. Consider excluding large auto-generated files")
    print("  6. Use visual_diff.pages_from_endpoints to limit DOM scans")
    print()
    
    # Step 7: CLI commands
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
