"""YAML structure anomaly detection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from .anomaly_models import AnomalyResult

console = Console()


class YAMLStructureDetector:
    """Detect structural changes in YAML files."""

    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir / 'yaml_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _load_yaml(self, file_path: Path) -> Optional[Dict]:
        try:
            import yaml
            return yaml.safe_load(file_path.read_text(encoding='utf-8'))
        except Exception:
            return None

    def _extract_structure(self, data: Any, depth: int = 0, max_depth: int = 5) -> Dict:
        if depth > max_depth:
            return {'type': type(data).__name__, 'truncated': True}
        if isinstance(data, dict):
            return {
                'type': 'dict',
                'keys': {
                    k: self._extract_structure(v, depth + 1, max_depth)
                    for k, v in list(data.items())[:50]
                },
            }
        if isinstance(data, list):
            return {
                'type': 'list',
                'length': len(data),
                'sample': self._extract_structure(data[0], depth + 1, max_depth) if data else None,
            }
        return {'type': type(data).__name__}

    def _snapshot_path(self, file_path: Path) -> Path:
        rel_path = str(file_path).replace('/', '_').replace('\\', '_')
        return self.snapshot_dir / f"{rel_path}.struct.json"

    def _compare_structures(self, old: Dict, new: Dict, path: str = "") -> List[Dict]:
        """Compare two structures and return differences."""
        diffs: List[Dict] = []

        if old.get('type') != new.get('type'):
            diffs.append({'path': path or 'root', 'change': 'type_changed',
                          'old': old.get('type'), 'new': new.get('type')})
            return diffs

        if old.get('type') == 'dict':
            diffs.extend(self._compare_dict_structures(old, new, path))
        elif old.get('type') == 'list':
            if old.get('length') != new.get('length'):
                diffs.append({'path': path or 'root', 'change': 'list_length_changed',
                              'old_length': old.get('length'), 'new_length': new.get('length')})
        return diffs

    def _compare_dict_structures(self, old: Dict, new: Dict, path: str) -> List[Dict]:
        diffs: List[Dict] = []
        old_keys = set(old.get('keys', {}).keys())
        new_keys = set(new.get('keys', {}).keys())

        for key in old_keys - new_keys:
            diffs.append({'path': f"{path}.{key}" if path else key, 'change': 'key_removed', 'key': key})
        for key in new_keys - old_keys:
            diffs.append({'path': f"{path}.{key}" if path else key, 'change': 'key_added', 'key': key})
        for key in old_keys & new_keys:
            diffs.extend(self._compare_structures(
                old['keys'][key], new['keys'][key],
                f"{path}.{key}" if path else key,
            ))
        return diffs

    def detect(self, file_path: Path) -> Optional[AnomalyResult]:
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
                    snap_path.write_text(json.dumps(new_struct, indent=2))
                    critical = [d for d in diffs if d['change'] in ['type_changed', 'key_removed']]
                    return AnomalyResult(
                        detector='structure',
                        file_path=str(file_path),
                        anomaly_type='drift',
                        severity='high' if critical else 'medium',
                        message=f"Struktura YAML zmieniona ({len(diffs)} zmian)",
                        details={'diffs': diffs[:10], 'total_diffs': len(diffs)},
                        suggestions=self._generate_suggestions(diffs),
                    )
            except Exception as e:
                console.print(f"[yellow]YAML structure error: {e}[/yellow]")

        snap_path.write_text(json.dumps(new_struct, indent=2))
        return None

    def _generate_suggestions(self, diffs: List[Dict]) -> List[str]:
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
                suggestions.append("Liczba elementów zmieniona - sprawdź czy wszystkie wymagane elementy są obecne")
        return suggestions[:5]
