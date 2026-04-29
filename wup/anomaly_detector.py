"""Fast anomaly detection for YAML files without Playwright.

Provides lightweight alternatives to visual DOM diff for detecting
configuration drift and structural anomalies in YAML files.

Methods:
- AST diff: Compare Python AST trees for code changes
- YAML diff: Deep comparison of YAML structures  
- Text diff: Line-by-line text comparison with context
- Hash diff: Checksum-based change detection
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    detector: str  # nazwa detektora użytego
    file_path: str
    anomaly_type: str  # 'changed', 'added', 'removed', 'drift', 'error'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time()))
    suggestions: List[str] = field(default_factory=list)


@dataclass
class YAMLAnomalyConfig:
    """Configuration for YAML anomaly detection."""
    enabled: bool = True
    methods: List[str] = field(default_factory=lambda: ['hash', 'structure', 'keys'])
    # 'hash' - szybkie porównanie hashy
    # 'structure' - porównanie struktury YAML  
    # 'keys' - porównanie kluczy
    # 'values' - porównanie wartości
    # 'ast' - analiza AST (dla plików Python)
    # 'text' - porównanie tekstowe
    
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '*.tmp', '*.bak', '*~', '.git/*', '__pycache__/*', '.venv/*', 'node_modules/*'
    ])
    
    # Progi dla różnych metryk
    max_key_depth: int = 5
    max_file_size_kb: int = 500
    
    # Czułość detekcji
    strict_mode: bool = False  # True = wykrywa nawet drobne zmiany


class HashDetector:
    """Fast anomaly detection using file hashes."""
    
    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir / 'hash_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _snapshot_path(self, file_path: Path) -> Path:
        """Get snapshot path for a file."""
        rel_path = str(file_path).replace('/', '_').replace('\\', '_')
        return self.snapshot_dir / f"{rel_path}.hash"
    
    def detect(self, file_path: Path) -> Optional[AnomalyResult]:
        """Detect changes using hash comparison."""
        try:
            if not file_path.exists():
                return None
                
            content = file_path.read_text(encoding='utf-8')
            current_hash = self._compute_hash(content)
            
            snap_path = self._snapshot_path(file_path)
            
            if snap_path.exists():
                old_hash = snap_path.read_text().strip()
                if old_hash != current_hash:
                    # Plik się zmienił
                    result = AnomalyResult(
                        detector='hash',
                        file_path=str(file_path),
                        anomaly_type='changed',
                        severity='medium',
                        message=f"Plik zmieniony (hash: {old_hash[:8]} → {current_hash[:8]})",
                        details={
                            'old_hash': old_hash,
                            'new_hash': current_hash,
                            'file_size': len(content)
                        }
                    )
                    # Aktualizuj snapshot
                    snap_path.write_text(current_hash)
                    return result
            else:
                # Nowy plik
                snap_path.write_text(current_hash)
                return AnomalyResult(
                    detector='hash',
                    file_path=str(file_path),
                    anomaly_type='added',
                    severity='low',
                    message=f"Nowy plik wykryty (hash: {current_hash[:8]})",
                    details={'new_hash': current_hash}
                )
            
            return None
            
        except Exception as e:
            return AnomalyResult(
                detector='hash',
                file_path=str(file_path),
                anomaly_type='error',
                severity='low',
                message=f"Błąd hash detection: {e}"
            )


class YAMLStructureDetector:
    """Detect structural changes in YAML files."""
    
    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir / 'yaml_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_yaml(self, file_path: Path) -> Optional[Dict]:
        """Load YAML file safely."""
        try:
            import yaml
            content = file_path.read_text(encoding='utf-8')
            return yaml.safe_load(content)
        except Exception:
            return None
    
    def _extract_structure(self, data: Any, depth: int = 0, max_depth: int = 5) -> Dict:
        """Extract structure (keys and types) from YAML data."""
        if depth > max_depth:
            return {'type': type(data).__name__, 'truncated': True}
        
        if isinstance(data, dict):
            return {
                'type': 'dict',
                'keys': {
                    k: self._extract_structure(v, depth + 1, max_depth) 
                    for k, v in list(data.items())[:50]  # Limit keys
                }
            }
        elif isinstance(data, list):
            return {
                'type': 'list',
                'length': len(data),
                'sample': self._extract_structure(data[0], depth + 1, max_depth) if data else None
            }
        else:
            return {'type': type(data).__name__}
    
    def _snapshot_path(self, file_path: Path) -> Path:
        """Get snapshot path for a file."""
        rel_path = str(file_path).replace('/', '_').replace('\\', '_')
        return self.snapshot_dir / f"{rel_path}.struct.json"
    
    def _compare_structures(
        self, 
        old: Dict, 
        new: Dict, 
        path: str = ""
    ) -> List[Dict]:
        """Compare two structures and return differences."""
        diffs = []
        
        if old.get('type') != new.get('type'):
            diffs.append({
                'path': path or 'root',
                'change': 'type_changed',
                'old': old.get('type'),
                'new': new.get('type')
            })
            return diffs
        
        if old.get('type') == 'dict' and new.get('type') == 'dict':
            old_keys = set(old.get('keys', {}).keys())
            new_keys = set(new.get('keys', {}).keys())
            
            # Usunięte klucze
            for key in old_keys - new_keys:
                diffs.append({
                    'path': f"{path}.{key}" if path else key,
                    'change': 'key_removed',
                    'key': key
                })
            
            # Nowe klucze
            for key in new_keys - old_keys:
                diffs.append({
                    'path': f"{path}.{key}" if path else key,
                    'change': 'key_added',
                    'key': key
                })
            
            # Zmienione struktury w istniejących kluczach
            for key in old_keys & new_keys:
                sub_diffs = self._compare_structures(
                    old['keys'][key],
                    new['keys'][key],
                    f"{path}.{key}" if path else key
                )
                diffs.extend(sub_diffs)
        
        elif old.get('type') == 'list' and new.get('type') == 'list':
            if old.get('length') != new.get('length'):
                diffs.append({
                    'path': path or 'root',
                    'change': 'list_length_changed',
                    'old_length': old.get('length'),
                    'new_length': new.get('length')
                })
        
        return diffs
    
    def detect(self, file_path: Path) -> Optional[AnomalyResult]:
        """Detect structural changes in YAML."""
        data = self._load_yaml(file_path)
        if data is None:
            return None
        
        snap_path = self._snapshot_path(file_path)
        new_struct = self._extract_structure(data)
        
        if snap_path.exists():
            try:
                old_struct = json.loads(snap_path.read_text())
                diffs = self._compare_structures(old_struct, new_struct)
                
                if diffs:
                    # Zaktualizuj snapshot
                    snap_path.write_text(json.dumps(new_struct, indent=2))
                    
                    # Określ wagę zmiany
                    critical_changes = [d for d in diffs if d['change'] in ['type_changed', 'key_removed']]
                    severity = 'high' if critical_changes else 'medium'
                    
                    # Generuj sugestie
                    suggestions = self._generate_suggestions(diffs)
                    
                    return AnomalyResult(
                        detector='structure',
                        file_path=str(file_path),
                        anomaly_type='drift',
                        severity=severity,
                        message=f"Struktura YAML zmieniona ({len(diffs)} zmian)",
                        details={
                            'diffs': diffs[:10],  # Limit w output
                            'total_diffs': len(diffs)
                        },
                        suggestions=suggestions
                    )
            except Exception as e:
                console.print(f"[yellow]YAML structure error: {e}[/yellow]")
        
        # Zapisz pierwszy snapshot
        snap_path.write_text(json.dumps(new_struct, indent=2))
        return None
    
    def _generate_suggestions(self, diffs: List[Dict]) -> List[str]:
        """Generate helpful suggestions based on diffs."""
        suggestions = []
        
        for diff in diffs:
            change_type = diff.get('change')
            if change_type == 'key_removed':
                suggestions.append(f"Sprawdź czy usunięcie klucza '{diff['key']}' nie zepsuje integracji")
            elif change_type == 'key_added':
                suggestions.append(f"Nowy klucz '{diff['key']}' - upewnij się że jest poprawnie skonfigurowany")
            elif change_type == 'type_changed':
                suggestions.append(f"Typ zmieniony w '{diff['path']}' - może to wpłynąć na parsing")
            elif change_type == 'list_length_changed':
                suggestions.append(f"Liczba elementów zmieniona - sprawdź czy wszystkie wymagane elementy są obecne")
        
        return suggestions[:5]  # Max 5 sugestii


class ASTDetector:
    """Detect changes in Python files using AST comparison."""
    
    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir / 'ast_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def _extract_ast_info(self, tree: ast.AST) -> Dict:
        """Extract relevant info from AST."""
        info = {
            'imports': [],
            'classes': [],
            'functions': [],
            'top_level': []
        }
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info['imports'].append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = [a.name for a in node.names]
                info['imports'].append(f"from {module} import {', '.join(names)}")
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                info['classes'].append({
                    'name': node.name,
                    'methods': methods,
                    'bases': [ast.unparse(b) for b in node.bases] if hasattr(ast, 'unparse') else []
                })
            elif isinstance(node, ast.FunctionDef):
                info['functions'].append({
                    'name': node.name,
                    'args': len(node.args.args),
                    'decorators': len(node.decorator_list)
                })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        info['top_level'].append(target.id)
        
        return info
    
    def _snapshot_path(self, file_path: Path) -> Path:
        rel_path = str(file_path).replace('/', '_').replace('\\', '_')
        return self.snapshot_dir / f"{rel_path}.ast.json"
    
    def detect(self, file_path: Path) -> Optional[AnomalyResult]:
        """Detect changes in Python file structure."""
        if not str(file_path).endswith('.py'):
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            new_info = self._extract_ast_info(tree)
            
            snap_path = self._snapshot_path(file_path)
            
            if snap_path.exists():
                old_info = json.loads(snap_path.read_text())
                
                changes = []
                
                # Porównaj klasy
                old_classes = {c['name']: c for c in old_info.get('classes', [])}
                new_classes = {c['name']: c for c in new_info.get('classes', [])}
                
                for name in set(old_classes.keys()) | set(new_classes.keys()):
                    if name not in new_classes:
                        changes.append(f"Klasa usunięta: {name}")
                    elif name not in old_classes:
                        changes.append(f"Nowa klasa: {name}")
                    elif old_classes[name] != new_classes[name]:
                        changes.append(f"Klasa zmieniona: {name}")
                
                # Porównaj funkcje
                old_funcs = {f['name'] for f in old_info.get('functions', [])}
                new_funcs = {f['name'] for f in new_info.get('functions', [])}
                
                for name in old_funcs - new_funcs:
                    changes.append(f"Funkcja usunięta: {name}")
                for name in new_funcs - old_funcs:
                    changes.append(f"Nowa funkcja: {name}")
                
                if changes:
                    snap_path.write_text(json.dumps(new_info, indent=2))
                    return AnomalyResult(
                        detector='ast',
                        file_path=str(file_path),
                        anomaly_type='changed',
                        severity='high',
                        message=f"Struktura Python zmieniona ({len(changes)} zmian)",
                        details={'changes': changes[:10]},
                        suggestions=["Przejrzyj zmiany w API przed deploymentem"]
                    )
            else:
                snap_path.write_text(json.dumps(new_info, indent=2))
            
            return None
            
        except SyntaxError as e:
            return AnomalyResult(
                detector='ast',
                file_path=str(file_path),
                anomaly_type='error',
                severity='critical',
                message=f"Błąd składni Python: {e}"
            )
        except Exception as e:
            return None


class AnomalyDetector:
    """Main anomaly detector combining multiple detection methods."""
    
    def __init__(self, project_root: Union[str, Path], config: Optional[YAMLAnomalyConfig] = None):
        self.project_root = Path(project_root)
        self.config = config or YAMLAnomalyConfig()
        self.snapshot_dir = self.project_root / '.wup' / 'anomaly_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicjalizacja detektorów
        self.detectors = {}
        if 'hash' in self.config.methods:
            self.detectors['hash'] = HashDetector(self.snapshot_dir)
        if 'structure' in self.config.methods or 'keys' in self.config.methods:
            self.detectors['structure'] = YAMLStructureDetector(self.snapshot_dir)
        if 'ast' in self.config.methods:
            self.detectors['ast'] = ASTDetector(self.snapshot_dir)
    
    def _should_scan(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        # Sprawdź rozmiar
        try:
            size_kb = file_path.stat().st_size / 1024
            if size_kb > self.config.max_file_size_kb:
                return False
        except:
            return False
        
        # Sprawdź patterns do ignorowania
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
        
        if not file_path.exists():
            return []
        
        if not self._should_scan(file_path):
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
        recursive: bool = True
    ) -> List[AnomalyResult]:
        """Scan directory for anomalies."""
        directory = Path(directory)
        
        if not directory.exists():
            return []
        
        results = []
        
        # YAML files
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        # Python files dla AST detector
        if 'ast' in self.config.methods:
            py_files = list(directory.rglob('*.py')) if recursive else list(directory.glob('*.py'))
            files.extend(py_files)
        
        console.print(f"[dim]Scanning {len(files)} files with {len(self.detectors)} detectors...[/dim]")
        
        for file_path in files:
            file_results = self.scan_file(file_path)
            results.extend(file_results)
        
        return results
    
    def get_summary(self, results: List[AnomalyResult]) -> Dict:
        """Generate summary of results."""
        by_detector = {}
        by_severity = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        by_type = {}
        
        for r in results:
            by_detector[r.detector] = by_detector.get(r.detector, 0) + 1
            by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
            by_type[r.anomaly_type] = by_type.get(r.anomaly_type, 0) + 1
        
        return {
            'total': len(results),
            'by_detector': by_detector,
            'by_severity': by_severity,
            'by_type': by_type
        }
    
    def print_report(self, results: List[AnomalyResult]) -> None:
        """Print formatted report of anomalies."""
        if not results:
            console.print("[green]✓ No anomalies detected[/green]")
            return
        
        summary = self.get_summary(results)
        
        # Header
        console.print(f"\n[bold]Anomaly Report[/bold] - {summary['total']} issues found")
        console.print(f"Severity: critical={summary['by_severity'].get('critical', 0)}, "
                     f"high={summary['by_severity'].get('high', 0)}, "
                     f"medium={summary['by_severity'].get('medium', 0)}, "
                     f"low={summary['by_severity'].get('low', 0)}")
        
        # Table
        table = Table(title="Detected Anomalies")
        table.add_column("Detector", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Message")
        
        severity_colors = {
            'critical': 'bold red',
            'high': 'red',
            'medium': 'yellow',
            'low': 'dim'
        }
        
        for r in sorted(results, key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.severity), reverse=True):
            color = severity_colors.get(r.severity, 'white')
            file_short = str(r.file_path).replace(str(self.project_root), '.')
            table.add_row(
                r.detector,
                file_short[:50],
                r.anomaly_type,
                f"[{color}]{r.severity}[/{color}]",
                r.message[:60]
            )
        
        console.print(table)
        
        # Sugestie
        all_suggestions = []
        for r in results:
            all_suggestions.extend(r.suggestions)
        
        if all_suggestions:
            console.print("\n[bold]Suggestions:[/bold]")
            for i, s in enumerate(set(all_suggestions)[:10], 1):
                console.print(f"  {i}. {s}")


# Convenience functions for CLI usage
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
