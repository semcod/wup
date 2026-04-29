"""
TestQL endpoint discovery module.

Discovers API endpoints from TestQL scenario files (.testql.toon.yaml)
and maps them to services for intelligent testing.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


class TestQLEndpointDiscovery:
    """Discover endpoints from TestQL scenario files."""
    
    def __init__(self, scenarios_dir: str, testql_bin: str = "testql"):
        """
        Initialize TestQL endpoint discovery.
        
        Args:
            scenarios_dir: Path to TestQL scenarios directory
            testql_bin: TestQL executable name or path
        """
        self.scenarios_dir = Path(scenarios_dir)
        self.testql_bin = testql_bin
        self.endpoints_by_service: Dict[str, Set[str]] = {}
        self.scenarios_by_service: Dict[str, List[Path]] = {}
    
    def discover_scenarios(self) -> List[Path]:
        """
        Find all TestQL scenario files.
        
        Returns:
            List of paths to .testql.toon.yaml files
        """
        if not self.scenarios_dir.exists():
            return []
        
        return sorted(self.scenarios_dir.rglob("*.testql.toon.yaml"))
    
    def parse_scenario_endpoints(self, scenario_path: Path) -> List[str]:
        """
        Extract endpoints from a TestQL scenario file.
        
        Args:
            scenario_path: Path to scenario file
            
        Returns:
            List of endpoint paths found in the scenario
        """
        endpoints = []
        
        try:
            with open(scenario_path, 'r') as f:
                content = f.read()
            
            # Parse TestQL API blocks
            # Pattern: METHOD, /path
            api_pattern = re.compile(r'^\s*(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s*,\s*([^\s,]+)', re.MULTILINE)
            matches = api_pattern.findall(content)
            
            for method, path in matches:
                endpoints.append(f"{method.upper()} {path}")
            
            # Also try parsing as YAML to extract structured data
            try:
                data = yaml.safe_load(content)
                if data and isinstance(data, dict):
                    # Look for API sections
                    if 'API' in data:
                        api_data = data['API']
                        if isinstance(api_data, list):
                            for item in api_data:
                                if isinstance(item, (list, tuple)) and len(item) >= 2:
                                    method = item[0]
                                    path = item[1]
                                    endpoints.append(f"{method.upper()} {path}")
            except:
                pass
            
        except Exception as e:
            print(f"Warning: Could not parse {scenario_path}: {e}")
        
        return list(set(endpoints))  # Remove duplicates
    
    def infer_service_from_scenario(self, scenario_path: Path) -> Optional[str]:
        """
        Infer service name from scenario file path.
        
        Args:
            scenario_path: Path to scenario file
            
        Returns:
            Service name or None
        """
        # Extract service from path
        # e.g., scenarios/tests/users/users-api.testql.toon.yaml -> users
        rel_path = scenario_path.relative_to(self.scenarios_dir)
        parts = rel_path.parts
        
        # Look for service-like patterns in the path
        for part in parts:
            if part not in ['tests', 'scenarios', 'api', 'views']:
                # Clean up the name
                service = part.replace('-', '/').replace('_', '/')
                return service
        
        # Fallback to parent directory name
        if scenario_path.parent.name != self.scenarios_dir.name:
            return scenario_path.parent.name
        
        return None
    
    def discover_all_endpoints(self) -> Dict[str, Dict]:
        """
        Discover all endpoints from scenarios.
        
        Returns:
            Dictionary mapping service names to endpoint info:
            {
                "service_name": {
                    "endpoints": ["GET /api/users", ...],
                    "scenarios": [path1, path2, ...]
                }
            }
        """
        scenarios = self.discover_scenarios()
        
        for scenario in scenarios:
            endpoints = self.parse_scenario_endpoints(scenario)
            service = self.infer_service_from_scenario(scenario)
            
            if not service:
                continue
            
            if service not in self.endpoints_by_service:
                self.endpoints_by_service[service] = set()
                self.scenarios_by_service[service] = []
            
            self.endpoints_by_service[service].update(endpoints)
            self.scenarios_by_service[service].append(scenario)
        
        # Convert to output format
        result = {}
        for service in self.endpoints_by_service:
            result[service] = {
                "endpoints": sorted(list(self.endpoints_by_service[service])),
                "scenarios": [str(s) for s in self.scenarios_by_service[service]]
            }
        
        return result
    
    def discover_via_testql_cli(self, service: Optional[str] = None) -> List[str]:
        """
        Use TestQL CLI to discover endpoints.
        
        Args:
            service: Optional service name to filter
            
        Returns:
            List of discovered endpoints
        """
        try:
            cmd = [self.testql_bin, "endpoints", str(self.scenarios_dir)]
            if service:
                cmd.extend(["--service", service])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output - assuming one endpoint per line
                endpoints = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return endpoints
            else:
                print(f"TestQL CLI error: {result.stderr}")
                return []
                
        except FileNotFoundError:
            print(f"TestQL binary '{self.testql_bin}' not found. Using file-based discovery.")
            return []
        except subprocess.TimeoutExpired:
            print("TestQL CLI timeout. Using file-based discovery.")
            return []
        except Exception as e:
            print(f"TestQL CLI error: {e}")
            return []
    
    def to_dependency_map(self) -> Dict:
        """
        Convert discovered endpoints to dependency map format.
        
        Returns:
            Dictionary in dependency map format:
            {
                "services": {
                    "service_name": {
                        "endpoints": [...],
                        "files": [...]
                    }
                },
                "files": {...}
            }
        """
        discovery = self.discover_all_endpoints()
        
        dependency_map = {
            "services": {},
            "files": {}
        }
        
        for service, info in discovery.items():
            dependency_map["services"][service] = {
                "endpoints": info["endpoints"],
                "files": [str(s) for s in info["scenarios"]]
            }
            
            # Map files to endpoints
            for scenario in info["scenarios"]:
                dependency_map["files"][scenario] = info["endpoints"]
        
        return dependency_map
