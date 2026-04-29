"""
WUP Web Client.

Lightweight async HTTP client used by WUP agents to push events
(REGRESSION, ANOMALY, PASS, VISUAL_DIFF, HEALTH_TRANSITION) to the
optional `wupbro` FastAPI backend.

Design constraints:
  - **Soft-fail**: any network/HTTP error must NOT break the watcher.
  - **Optional dependency**: httpx is optional; without it the client
    becomes a no-op and logs a single warning.
  - **Short timeout**: configurable via WebConfig.timeout_s (default 2s).
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional

from rich.console import Console

from .models.config import WebConfig

_console = Console()
_HTTPX_AVAILABLE: Optional[bool] = None
_HTTPX_WARN_LOGGED: bool = False


def _httpx_available() -> bool:
    global _HTTPX_AVAILABLE, _HTTPX_WARN_LOGGED
    if _HTTPX_AVAILABLE is None:
        try:
            import httpx  # noqa: F401
            _HTTPX_AVAILABLE = True
        except ImportError:
            _HTTPX_AVAILABLE = False
            if not _HTTPX_WARN_LOGGED:
                _console.print(
                    "[yellow]wup.web_client: httpx not installed — events will not be sent[/yellow]"
                )
                _HTTPX_WARN_LOGGED = True
    return _HTTPX_AVAILABLE


def resolve_endpoint(cfg: WebConfig) -> str:
    """Return endpoint URL from cfg or env, with trailing slash stripped."""
    if cfg.endpoint:
        return cfg.endpoint.rstrip("/")
    env_var = cfg.endpoint_env or "WUP_WEB_ENDPOINT"
    return os.environ.get(env_var, "").rstrip("/")


def _normalize(payload: Any) -> Any:
    """Convert dataclasses to plain dicts for JSON serialization."""
    if is_dataclass(payload):
        return asdict(payload)
    if isinstance(payload, dict):
        return {k: _normalize(v) for k, v in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [_normalize(v) for v in payload]
    return payload


class WebClient:
    """
    Async event sink for the wupbro backend.

    Usage::

        client = WebClient(config.web)
        await client.send_event({
            "type": "REGRESSION",
            "service": "users-web",
            "file": "app/users/routes.py",
            "endpoint": "/api/users",
            "status": "fail",
            "reason": "TestQL exit code 1",
        })

    All public methods are coroutines and never raise — they swallow
    network errors and log them.
    """

    def __init__(self, cfg: Optional[WebConfig] = None) -> None:
        self.cfg = cfg or WebConfig()
        self.endpoint = resolve_endpoint(self.cfg)

    @property
    def is_active(self) -> bool:
        return bool(self.cfg.enabled and self.endpoint and _httpx_available())

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json", "User-Agent": "wupbro-client"}
        if self.cfg.api_key:
            h["Authorization"] = f"Bearer {self.cfg.api_key}"
        return h

    async def send_event(self, event: Dict[str, Any]) -> bool:
        """
        POST a single event to `<endpoint>/events`.

        Returns True on 2xx, False otherwise (including disabled / no httpx).
        Never raises.
        """
        if not self.is_active:
            return False

        payload = _normalize(event)
        payload.setdefault("timestamp", int(time.time()))

        url = f"{self.endpoint}/events"
        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.cfg.timeout_s) as client:
                resp = await client.post(url, json=payload, headers=self._headers())
                if 200 <= resp.status_code < 300:
                    return True
                _console.print(
                    f"[yellow]wup.web_client: {url} → HTTP {resp.status_code}[/yellow]"
                )
                return False
        except Exception as exc:  # noqa: BLE001 — soft-fail by design
            _console.print(f"[yellow]wup.web_client: send_event failed ({exc})[/yellow]")
            return False

    async def send_regression(
        self,
        service: str,
        file: str,
        endpoint: str,
        reason: str,
        stage: str = "quick",
    ) -> bool:
        return await self.send_event({
            "type": "REGRESSION",
            "service": service,
            "file": file,
            "endpoint": endpoint,
            "status": "fail",
            "stage": stage,
            "reason": reason,
        })

    async def send_pass(self, service: str, stage: str = "quick") -> bool:
        return await self.send_event({
            "type": "PASS",
            "service": service,
            "stage": stage,
            "status": "ok",
        })

    async def send_health_transition(
        self,
        service: str,
        from_status: str,
        to_status: str,
    ) -> bool:
        return await self.send_event({
            "type": "HEALTH_TRANSITION",
            "service": service,
            "from": from_status,
            "to": to_status,
        })

    async def send_visual_diff(
        self,
        service: str,
        url: str,
        diff: Dict[str, Any],
    ) -> bool:
        return await self.send_event({
            "type": "VISUAL_DIFF",
            "service": service,
            "url": url,
            "diff": diff,
        })
