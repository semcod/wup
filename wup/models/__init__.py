"""
Configuration models for WUP.
"""

from .config import (
    AnomalyDetectionConfig,
    NotifyConfig,
    ProjectConfig,
    ServiceConfig,
    ServiceTestConfig,
    TestQLConfig,
    TestStrategyConfig,
    VisualDiffConfig,
    WatchConfig,
    WebConfig,
    WupConfig,
)
from .target import ServiceTestTarget

ServiceType = str  # Type alias: 'web', 'shell', 'auto'

__all__ = [
    "AnomalyDetectionConfig",
    "NotifyConfig",
    "ProjectConfig",
    "ServiceConfig",
    "ServiceTestConfig",
    "ServiceType",
    "ServiceTestTarget",
    "TestQLConfig",
    "TestStrategyConfig",
    "VisualDiffConfig",
    "WatchConfig",
    "WebConfig",
    "WupConfig",
]
