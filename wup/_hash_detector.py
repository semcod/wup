"""Fast hash-based anomaly detection."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from .anomaly_models import AnomalyResult


class HashDetector:
    """Fast anomaly detection using file hashes."""

    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir / 'hash_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def _snapshot_path(self, file_path: Path) -> Path:
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
                    snap_path.write_text(current_hash)
                    return AnomalyResult(
                        detector='hash',
                        file_path=str(file_path),
                        anomaly_type='changed',
                        severity='medium',
                        message=f"Plik zmieniony (hash: {old_hash[:8]} → {current_hash[:8]})",
                        details={
                            'old_hash': old_hash,
                            'new_hash': current_hash,
                            'file_size': len(content),
                        },
                    )
            else:
                snap_path.write_text(current_hash)
                return AnomalyResult(
                    detector='hash',
                    file_path=str(file_path),
                    anomaly_type='added',
                    severity='low',
                    message=f"Nowy plik wykryty (hash: {current_hash[:8]})",
                    details={'new_hash': current_hash},
                )

            return None

        except Exception as e:
            return AnomalyResult(
                detector='hash',
                file_path=str(file_path),
                anomaly_type='error',
                severity='low',
                message=f"Błąd hash detection: {e}",
            )
