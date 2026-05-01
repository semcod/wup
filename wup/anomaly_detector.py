"""Fast anomaly detection for YAML files without Playwright.

Provides lightweight alternatives to visual DOM diff for detecting
configuration drift and structural anomalies in YAML files.

Methods:
- AST diff: Compare Python AST trees for code changes
- YAML diff: Deep comparison of YAML structures
- Hash diff: Checksum-based change detection
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

from .anomaly_models import AnomalyResult, YAMLAnomalyConfig
from ._hash_detector import HashDetector
from ._yaml_detector import YAMLStructureDetector
from ._ast_detector import ASTDetector

__all__ = [
    "AnomalyResult",
    "YAMLAnomalyConfig",
    "HashDetector",
    "YAMLStructureDetector",
    "ASTDetector",
    "AnomalyDetector",
    "quick_scan",
    "scan_yaml_changes",
]

console = Console()


class AnomalyDetector:
    """Main anomaly detector combining multiple detection methods."""

    def __init__(self, project_root: Union[str, Path], config: Optional[YAMLAnomalyConfig] = None):
        self.project_root = Path(project_root)
        self.config = config or YAMLAnomalyConfig()
        self.snapshot_dir = self.project_root / '.wup' / 'anomaly_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self.detectors: Dict = {}
        if 'hash' in self.config.methods:
            self.detectors['hash'] = HashDetector(self.snapshot_dir)
        if 'structure' in self.config.methods or 'keys' in self.config.methods:
            self.detectors['structure'] = YAMLStructureDetector(self.snapshot_dir)
        if 'ast' in self.config.methods:
            self.detectors['ast'] = ASTDetector(self.snapshot_dir)

    def _should_scan(self, file_path: Path) -> bool:
        try:
            if file_path.stat().st_size / 1024 > self.config.max_file_size_kb:
                return False
        except Exception:
            return False

        path_str = str(file_path)
        for pattern in self.config.ignore_patterns:
            if pattern.endswith('/*'):
                if pattern.rstrip('/*') in path_str:
                    return False
            elif pattern in path_str:
                return False
        return True

    def scan_file(self, file_path: Union[str, Path]) -> List[AnomalyResult]:
        """Scan a single file with all enabled detectors."""
        file_path = Path(file_path)
        if not file_path.exists() or not self._should_scan(file_path):
            return []

        results = []
        for name, detector in self.detectors.items():
            try:
                result = detector.detect(file_path)
                if result:
                    results.append(result)
            except Exception as e:
                console.print(f"[red]Detector {name} failed: {e}[/red]")
        return results

    def scan_directory(
        self,
        directory: Union[str, Path],
        pattern: str = "*.yaml",
        recursive: bool = True,
    ) -> List[AnomalyResult]:
        """Scan directory for anomalies."""
        directory = Path(directory)
        if not directory.exists():
            return []

        files = list(directory.rglob(pattern) if recursive else directory.glob(pattern))
        if 'ast' in self.config.methods:
            py_files = list(directory.rglob('*.py') if recursive else directory.glob('*.py'))
            files.extend(py_files)

        console.print(f"[dim]Scanning {len(files)} files with {len(self.detectors)} detectors...[/dim]")

        results = []
        for file_path in files:
            results.extend(self.scan_file(file_path))
        return results

    def get_summary(self, results: List[AnomalyResult]) -> Dict:
        """Generate summary of results."""
        by_detector: Dict = {}
        by_severity: Dict = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        by_type: Dict = {}

        for r in results:
            by_detector[r.detector] = by_detector.get(r.detector, 0) + 1
            by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
            by_type[r.anomaly_type] = by_type.get(r.anomaly_type, 0) + 1

        return {'total': len(results), 'by_detector': by_detector,
                'by_severity': by_severity, 'by_type': by_type}

    def print_report(self, results: List[AnomalyResult]) -> None:
        """Print formatted report of anomalies."""
        if not results:
            console.print("[green]✓ No anomalies detected[/green]")
            return

        summary = self.get_summary(results)
        console.print(f"\n[bold]Anomaly Report[/bold] - {summary['total']} issues found")
        sev = summary['by_severity']
        console.print(
            f"Severity: critical={sev.get('critical', 0)}, high={sev.get('high', 0)}, "
            f"medium={sev.get('medium', 0)}, low={sev.get('low', 0)}"
        )

        table = Table(title="Detected Anomalies")
        table.add_column("Detector", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Message")

        severity_colors = {'critical': 'bold red', 'high': 'red', 'medium': 'yellow', 'low': 'dim'}
        _order = ['low', 'medium', 'high', 'critical']
        for r in sorted(results, key=lambda x: _order.index(x.severity), reverse=True):
            color = severity_colors.get(r.severity, 'white')
            file_short = str(r.file_path).replace(str(self.project_root), '.')
            table.add_row(r.detector, file_short[:50], r.anomaly_type,
                          f"[{color}]{r.severity}[/{color}]", r.message[:60])
        console.print(table)

        all_suggestions = [s for r in results for s in r.suggestions]
        if all_suggestions:
            console.print("\n[bold]Suggestions:[/bold]")
            for i, s in enumerate(set(all_suggestions)[:10], 1):
                console.print(f"  {i}. {s}")


def quick_scan(project_root: str, files: List[str]) -> List[AnomalyResult]:
    """Quick scan of specific files."""
    detector = AnomalyDetector(project_root)
    results = []
    for f in files:
        results.extend(detector.scan_file(f))
    return results


def scan_yaml_changes(project_root: str, yaml_dir: str = '.') -> List[AnomalyResult]:
    """Scan YAML directory for structural changes."""
    config = YAMLAnomalyConfig(methods=['hash', 'structure', 'keys'])
    detector = AnomalyDetector(project_root, config)
    return detector.scan_directory(yaml_dir, "*.yaml")
