"""Shared data models for anomaly detection."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""

    detector: str
    file_path: str
    anomaly_type: str  # 'changed', 'added', 'removed', 'drift', 'error'
    severity: str      # 'low', 'medium', 'high', 'critical'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time()))
    suggestions: List[str] = field(default_factory=list)


@dataclass
class YAMLAnomalyConfig:
    """Configuration for YAML anomaly detection."""

    enabled: bool = True
    methods: List[str] = field(default_factory=lambda: ['hash', 'structure', 'keys'])
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '*.tmp', '*.bak', '*~', '.git/*', '__pycache__/*', '.venv/*', 'node_modules/*'
    ])
    max_key_depth: int = 5
    max_file_size_kb: int = 500
    strict_mode: bool = False
