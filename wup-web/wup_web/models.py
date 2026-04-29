"""Pydantic models for wup-web events and driver requests."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


EventType = Literal[
    "REGRESSION",
    "PASS",
    "ANOMALY",
    "VISUAL_DIFF",
    "HEALTH_TRANSITION",
]


class Event(BaseModel):
    """Generic WUP event posted by an agent."""

    type: EventType
    service: Optional[str] = None
    file: Optional[str] = None
    endpoint: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    reason: Optional[str] = None
    diff: Optional[Dict[str, Any]] = None
    timestamp: int = Field(default_factory=lambda: int(time.time()))

    # Forward-compat: allow extra keys to land in `extra`
    model_config = {"extra": "allow"}


class EventList(BaseModel):
    items: List[Event]
    total: int


class DomDiffRequest(BaseModel):
    url: str
    service: str = "default"
    max_depth: int = 10


class ScreenshotRequest(BaseModel):
    url: str
    full_page: bool = True


class AnomalyReport(BaseModel):
    service: str
    metric: str
    value: float
    threshold: float
    timestamp: int = Field(default_factory=lambda: int(time.time()))
