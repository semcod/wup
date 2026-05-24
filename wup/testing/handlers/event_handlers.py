import asyncio
from typing import Any

from wup.testing.events.test_results import ScenarioFailed, ScenarioPassed

class TestResultEventHandler:
    """Handles test result events to update planfile reporter and web clients."""

    def __init__(self, planfile_reporter: Any, web_client: Any, console: Any):
        self.planfile_reporter = planfile_reporter
        self.web_client = web_client
        self.console = console

    def handle_test_failed(self, event: ScenarioFailed) -> None:
        """Handle scenario failure."""
        self.planfile_reporter.report_failure(
            service=event.service,
            status="down",
            stage=event.stage,
            message=event.reason,
            track_file=event.track_file,
        )

        if self.web_client.is_active:
            endpoint = event.endpoints[0] if event.endpoints else f"/{event.service}"
            # Need to wrap in task because send_regression is async and event handlers are sync
            # For simplicity, we just use create_task
            asyncio.create_task(
                self.web_client.send_regression(
                    service=event.service,
                    file="",
                    endpoint=endpoint,
                    reason=event.reason,
                    stage=event.stage,
                )
            )
            
        reason = (event.reason or "TestQL failed").strip().splitlines()[-1]
        if len(reason) > 160:
            reason = reason[:157] + "..."
        self.console.print(
            f"[red]✗ {event.stage.capitalize()} failed: {event.scenario.name} — {reason}[/red]\n"
            f"[dim]  track: {event.track_file}[/dim]"
        )

    def handle_test_passed(self, event: ScenarioPassed) -> None:
        """Handle scenario pass."""
        # Typically we might record up health transition when all scenarios pass,
        # not per scenario. But this handler is here for future expansion.
        pass

def register_testing_event_handlers(bus: Any, planfile_reporter: Any, web_client: Any, console: Any) -> None:
    handler = TestResultEventHandler(planfile_reporter, web_client, console)
    bus.subscribe(ScenarioFailed, handler.handle_test_failed)
    bus.subscribe(ScenarioPassed, handler.handle_test_passed)
