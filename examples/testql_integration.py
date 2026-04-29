"""
Integration example: WUP + TestQL

This example shows how to integrate WUP watcher with TestQL framework
to monitor TestQL codebase and run intelligent regression tests.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from wup.core import WupWatcher


class TestQLWatcher(WupWatcher):
    """
    Custom WUP watcher integrated with TestQL test framework.
    
    Overrides test methods to run actual TestQL tests instead of simulated ones.
    """
    
    def __init__(self, testql_project_root: str, **kwargs):
        super().__init__(testql_project_root, **kwargs)
        self.testql_root = Path(testql_project_root)
        self.scenarios_dir = self.testql_root / "scenarios"
        
    async def run_quick_test(self, service: str, endpoints: List[str]) -> bool:
        """
        Run quick smoke test using TestQL CLI.
        Tests only 3 scenarios max for speed.
        """
        self.console.print(f"[cyan]🧪 Quick TestQL test for {service}[/cyan]")
        
        # Find relevant test scenarios
        scenarios = self._find_scenarios_for_service(service)
        if not scenarios:
            self.console.print(f"[yellow]⚠ No scenarios found for {service}[/yellow]")
            return True
        
        # Limit to 3 scenarios for quick test
        test_scenarios = scenarios[:3]
        
        try:
            for scenario in test_scenarios:
                cmd = [
                    "python", "-m", "testql.cli", "run",
                    str(scenario),
                    "--dry-run"  # Fast validation without execution
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=str(self.testql_root),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.console.print(f"[red]✗ Scenario failed: {scenario.name}[/red]")
                    return False
            
            self.console.print(f"[green]✓ Quick test passed ({len(test_scenarios)} scenarios)[/green]")
            return True
            
        except (subprocess.TimeoutExpired, Exception) as e:
            self.console.print(f"[red]✗ Test error: {e}[/red]")
            return False
    
    async def run_detail_test(self, service: str, endpoints: List[str]) -> Dict:
        """
        Run detailed TestQL test with full coverage and blame reporting.
        """
        self.console.print(f"[cyan]🔍 Detail TestQL test for {service}[/cyan]")
        
        scenarios = self._find_scenarios_for_service(service)
        
        results = {
            "service": service,
            "total_scenarios": len(scenarios),
            "passed": 0,
            "failed": 0,
            "failed_scenarios": [],
            "blame": {}
        }
        
        try:
            # Run all scenarios for this service
            for scenario in scenarios:
                cmd = [
                    "python", "-m", "testql.cli", "run",
                    str(scenario),
                    "--output", "json"
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=str(self.testql_root),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["failed_scenarios"].append(str(scenario))
            
            # Generate blame report if failures found
            if results["failed"] > 0:
                results["blame"] = self._generate_blame_report(service, results["failed_scenarios"])
                self.console.print(f"[red]✗ Found {results['failed']} regression(s)[/red]")
            else:
                self.console.print(f"[green]✓ All {results['passed']} scenarios passed[/green]")
            
            return results
            
        except Exception as e:
            self.console.print(f"[red]✗ Detail test error: {e}[/red]")
            results["failed"] = len(scenarios)
            return results
    
    def _find_scenarios_for_service(self, service: str) -> List[Path]:
        """
        Find TestQL scenarios related to a service.
        
        Heuristic: scenarios in scenarios/tests/ or scenarios/views/
        matching service name patterns.
        """
        scenarios = []
        
        if not self.scenarios_dir.exists():
            return scenarios
        
        service_parts = service.lower().split('/')
        
        # Search in scenarios directory
        for scenario_file in self.scenarios_dir.rglob("*.testql.toon.yaml"):
            scenario_name = scenario_file.stem.lower()
            
            # Check if scenario name matches any part of service
            for part in service_parts:
                if part in scenario_name:
                    scenarios.append(scenario_file)
                    break
        
        return sorted(scenarios)
    
    def _generate_blame_report(self, service: str, failed_scenarios: List[str]) -> Dict:
        """Generate blame report using git."""
        import subprocess
        
        blame = {
            "service": service,
            "files": [],
            "recent_commits": []
        }
        
        try:
            # Get recent changes in service directory
            cmd = [
                "git", "log",
                "--oneline",
                "-10",
                "--", f"*/{service.replace('/', '/*/')}/*"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.testql_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                blame["recent_commits"] = result.stdout.strip().split('\n')
            
        except Exception:
            pass
        
        return blame


def main():
    """Run WUP + TestQL integration demo."""
    import sys
    
    # Default to testql directory or use provided path
    testql_path = sys.argv[1] if len(sys.argv) > 1 else "/home/tom/github/oqlos/testql"
    
    print(f"🚀 Starting WUP + TestQL integration")
    print(f"📁 TestQL project: {testql_path}")
    print()
    
    # Initialize watcher with TestQL-specific settings
    watcher = TestQLWatcher(
        testql_project_root=testql_path,
        cpu_throttle=0.7,  # Be gentle with CPU
        debounce_seconds=3,
        test_cooldown_seconds=180  # 3 minutes between tests
    )
    
    # Build dependency map for TestQL
    print("🔍 Building dependency map for TestQL...")
    watcher.dependency_mapper.build_from_codebase(framework="auto")
    watcher.dependency_mapper.save("testql-deps.json")
    
    deps = watcher.dependency_mapper.to_dict()
    print(f"✓ Found {len(deps['services'])} services")
    print(f"✓ Found {len(deps['files'])} files with endpoints")
    print()
    
    # Show services
    if deps['services']:
        print("📋 Services detected:")
        for service, info in sorted(deps['services'].items()):
            print(f"  • {service}: {len(info['endpoints'])} endpoints, {len(info['files'])} files")
        print()
    
    # Start watching
    print("🕵️  Starting file watcher...")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        watcher.start_watching()
    except KeyboardInterrupt:
        print("\n👋 Stopped.")


if __name__ == "__main__":
    main()
