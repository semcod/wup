"""Python AST-based anomaly detection."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional

from .anomaly_models import AnomalyResult


class ASTDetector:
    """Detect changes in Python files using AST comparison."""

    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir / 'ast_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _collect_import(node: ast.Import) -> List[str]:
        return [f"import {alias.name}" for alias in node.names]

    @staticmethod
    def _collect_import_from(node: ast.ImportFrom) -> str:
        module = node.module or ''
        names = ', '.join(a.name for a in node.names)
        return f"from {module} import {names}"

    @staticmethod
    def _collect_class(node: ast.ClassDef) -> Dict:
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        bases = [ast.unparse(b) for b in node.bases] if hasattr(ast, 'unparse') else []
        return {'name': node.name, 'methods': methods, 'bases': bases}

    @staticmethod
    def _collect_function(node: ast.FunctionDef) -> Dict:
        return {'name': node.name, 'args': len(node.args.args),
                'decorators': len(node.decorator_list)}

    def _extract_ast_info(self, tree: ast.AST) -> Dict:
        info: Dict = {'imports': [], 'classes': [], 'functions': [], 'top_level': []}
        _handlers = {
            ast.Import: lambda n: info['imports'].extend(self._collect_import(n)),
            ast.ImportFrom: lambda n: info['imports'].append(self._collect_import_from(n)),
            ast.ClassDef: lambda n: info['classes'].append(self._collect_class(n)),
            ast.FunctionDef: lambda n: info['functions'].append(self._collect_function(n)),
        }
        for node in ast.iter_child_nodes(tree):
            handler = _handlers.get(type(node))
            if handler:
                handler(node)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        info['top_level'].append(target.id)
        return info

    def _snapshot_path(self, file_path: Path) -> Path:
        rel_path = str(file_path).replace('/', '_').replace('\\', '_')
        return self.snapshot_dir / f"{rel_path}.ast.json"

    def _compute_changes(self, old_info: Dict, new_info: Dict) -> List[str]:
        changes: List[str] = []
        old_classes = {c['name']: c for c in old_info.get('classes', [])}
        new_classes = {c['name']: c for c in new_info.get('classes', [])}

        for name in set(old_classes) | set(new_classes):
            if name not in new_classes:
                changes.append(f"Klasa usunięta: {name}")
            elif name not in old_classes:
                changes.append(f"Nowa klasa: {name}")
            elif old_classes[name] != new_classes[name]:
                changes.append(f"Klasa zmieniona: {name}")

        old_funcs = {f['name'] for f in old_info.get('functions', [])}
        new_funcs = {f['name'] for f in new_info.get('functions', [])}
        for name in old_funcs - new_funcs:
            changes.append(f"Funkcja usunięta: {name}")
        for name in new_funcs - old_funcs:
            changes.append(f"Nowa funkcja: {name}")

        return changes

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
                changes = self._compute_changes(old_info, new_info)
                if changes:
                    snap_path.write_text(json.dumps(new_info, indent=2))
                    return AnomalyResult(
                        detector='ast',
                        file_path=str(file_path),
                        anomaly_type='changed',
                        severity='high',
                        message=f"Struktura Python zmieniona ({len(changes)} zmian)",
                        details={'changes': changes[:10]},
                        suggestions=["Przejrzyj zmiany w API przed deploymentem"],
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
                message=f"Błąd składni Python: {e}",
            )
        except Exception:
            return None
