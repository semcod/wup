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

ServiceType = str  # Type alias: 'web', 'shell', 'auto'

__all__ = [
    "AnomalyDetectionConfig",
    "NotifyConfig",
    "ProjectConfig",
    "ServiceConfig",
    "ServiceTestConfig",
    "ServiceType",
    "TestQLConfig",
    "TestStrategyConfig",
    "VisualDiffConfig",
    "WatchConfig",
    "WebConfig",
    "WupConfig",
]
