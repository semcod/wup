"""
Multi-project coordination for WUP.

Runs several :class:`~wup.core.WupWatcher` instances concurrently inside a
single process so ``wup watch proj-a proj-b ...`` (or a discovered monorepo)
tests many projects simultaneously.

Each watcher keeps its own config, dependency map, file observer and test
queue. This coordinator merely owns the shared main loop: it starts every
watcher's background tasks and observer, then round-robins their
``process_test_queue_once`` coroutines until interrupted.
"""

import asyncio
import time
from typing import List

from rich.console import Console

from .core import WupWatcher


class MultiProjectWatcher:
    """Drive multiple watchers from one loop, one observer per project."""

    def __init__(self, watchers: List[WupWatcher], console: Console = None):
        """
        Args:
            watchers: Already-constructed watchers, one per project.
            console: Optional shared Rich console (created if omitted).
        """
        self.watchers = watchers
        self.console = console or Console()

    def start_watching(self) -> bool:
        """
        Start every watcher and process their queues concurrently.

        Returns:
            False when no project yielded a valid path to watch (nothing was
            started); True after a graceful interrupt.
        """
        observers = []
        active: List[WupWatcher] = []

        for watcher in self.watchers:
            watcher.start_background_tasks()
            observer = watcher.prepare_observer()
            if observer is None:
                # prepare_observer already reported the reason for this project.
                continue
            observers.append(observer)
            active.append(watcher)

        if not active:
            self.console.print("[red]No valid paths to watch in any project[/red]")
            return False

        names = ", ".join(w.config.project.name for w in active)
        self.console.print(
            f"[bold green]▶ Watching {len(active)} project(s) simultaneously:[/bold green] "
            f"[dim]{names}[/dim]"
        )
        if len(active) < len(self.watchers):
            skipped = len(self.watchers) - len(active)
            self.console.print(
                f"[yellow]⚠️  Skipped {skipped} project(s) with no valid paths[/yellow]"
            )

        try:
            while True:
                for watcher in active:
                    asyncio.run(watcher.process_test_queue_once())
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in observers:
                observer.stop()

        for observer in observers:
            observer.join()
        return True
