"""Base class for anomaly detectors."""

from pathlib import Path
from typing import Optional

from .anomaly_models import AnomalyResult


class BaseDetector:
    """Base anomaly detector."""

    def __init__(self, snapshot_dir: Path, snapshot_type: str):
        self.snapshot_dir = snapshot_dir / f'{snapshot_type}_snapshots'
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def detect(self, file_path: Path) -> Optional[AnomalyResult]:
        """Detect changes and return an AnomalyResult if an anomaly is found."""
        raise NotImplementedError
