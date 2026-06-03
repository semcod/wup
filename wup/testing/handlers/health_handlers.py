import json
import time
from pathlib import Path
from typing import Any, Dict

from wup.testing.events.health_events import ServiceHealthChanged
from wup.testing.queries.health_queries import GetServiceHealth
from wup.event_store import EventStore


class ServiceHealthProjection:
    """Maintains the materialized view of service health."""

    def __init__(
        self,
        health_state_path: Path,
        event_store: EventStore,
        planfile_reporter: Any,
        browser_notifier: Any,
        web_client: Any,
    ):
        self.health_state_path = health_state_path
        self.event_store = event_store
        self.planfile_reporter = planfile_reporter
        self.browser_notifier = browser_notifier
        self.web_client = web_client
        self.state: Dict[str, Dict[str, Any]] = self._load_initial_state()

    def _load_initial_state(self) -> Dict[str, Dict[str, Any]]:
        if not self.health_state_path.exists():
            return {}
        try:
            return json.loads(self.health_state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_state(self) -> None:
        self.health_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.health_state_path.write_text(
            json.dumps(self.state, indent=2), encoding="utf-8"
        )

    def handle_health_changed(self, event: ServiceHealthChanged) -> None:
        """Update projection and notify external systems when health changes."""
        # Update projection state
        self.state[event.service] = {
            "status": event.status,
            "updated_at": int(time.time()),
            "stage": event.stage,
            "message": event.message,
            "track_file": event.track_file,
        }
        self._save_state()

        # Save to event store
        self.event_store.append(event)

        # Notify external systems
        if event.status in {"down", "degraded"}:
            # Non-strict fleet health uses status=degraded for optional probe gaps; do not spam planfile.
            if event.stage == "health_scenario" and event.status == "degraded":
                pass
            else:
                self.planfile_reporter.report_failure(
                    service=event.service,
                    status=event.status,
                    stage=event.stage,
                    message=event.message,
                    track_file=event.track_file,
                )
        elif event.status == "up":
            self.planfile_reporter.clear_service_stage(
                service=event.service, stage=event.stage
            )

        self.browser_notifier.notify(
            {
                "type": "wup_service_health_change",
                "service": event.service,
                "status": event.status,
                "previous_status": event.previous_status,
                "stage": event.stage,
                "message": event.message,
                "track_file": event.track_file,
                "timestamp": int(time.time()),
            }
        )
        
        # Fire-and-forget: forward event to wupbro backend if active
        if self.web_client and self.web_client.is_active:
            try:
                import asyncio
                asyncio.ensure_future(
                    self.web_client.send_health_transition(
                        service=event.service,
                        from_status=event.previous_status,
                        to_status=event.status,
                    )
                )
            except Exception:
                pass

    def handle_get_health(self, query: GetServiceHealth) -> Any:
        """Handle query for service health."""
        if query.service:
            return self.state.get(query.service, {})
        return self.state


def register_health_handlers(
    bus: Any,
    health_state_path: Path,
    event_store: EventStore,
    planfile_reporter: Any,
    browser_notifier: Any,
    web_client: Any,
) -> ServiceHealthProjection:
    projection = ServiceHealthProjection(
        health_state_path, event_store, planfile_reporter, browser_notifier, web_client
    )
    bus.subscribe(ServiceHealthChanged, projection.handle_health_changed)
    bus.subscribe(GetServiceHealth, projection.handle_get_health)
    return projection
