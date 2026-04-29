"""
WUP (What's Up) - Intelligent file watcher for regression testing in large projects.

WUP monitors file changes and runs intelligent regression tests using a 3-layer approach:
1. Detection Layer: File watching with heuristics
2. Priority Layer: Quick tests of related services
3. Detail Layer: Full tests with blame reports (only on failure)
"""

__version__ = "0.2.16"
__author__ = "Tom Sapletta"

from .config import load_config, save_config, get_default_config
from .core import WupWatcher
from .dependency_mapper import DependencyMapper
from .models.config import (
    WupConfig,
    WatchConfig,
    ServiceConfig,
    TestStrategyConfig,
    TestQLConfig,
    NotifyConfig,
)
from .testql_watcher import TestQLWatcher

__all__ = [
    "WupWatcher",
    "DependencyMapper",
    "TestQLWatcher",
    "load_config",
    "save_config",
    "get_default_config",
    "WupConfig",
    "WatchConfig",
    "ServiceConfig",
    "TestStrategyConfig",
    "TestQLConfig",
    "NotifyConfig",
]
