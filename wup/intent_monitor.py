"""Continuous todo2code Intent-vs-Reality monitoring for WUP."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from rich.console import Console

from .config import _read_dotenv
from .models.config import IntentMonitoringConfig


@dataclass
class IntentAuditResult:
    """Normalized result consumed by WUP health projections."""

    status: str
    message: str
    diagnostics_path: str = ""
    run_directory: str = ""
    diagnostics: List[Dict] = field(default_factory=list)
    error: str = ""


class Todo2CodeIntentMonitor:
    """Run todo2code initially, periodically and after debounced file changes."""

    _VALID_MODES = {"deterministic", "prefer-llm", "require-llm"}

    def __init__(
        self,
        project_root: Path,
        config: IntentMonitoringConfig,
        on_result: Callable[[IntentAuditResult], None],
        console: Optional[Console] = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.config = config
        self.on_result = on_result
        self.console = console or Console()
        self.last_result: Optional[IntentAuditResult] = None
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_change = 0.0
        self._run_lock = threading.Lock()

    def start(self) -> None:
        """Start the daemon worker once when monitoring is enabled."""
        if not self.config.enabled or (self._thread and self._thread.is_alive()):
            return
        self._thread = threading.Thread(
            target=self._loop,
            name="wup-todo2code-intent-monitor",
            daemon=True,
        )
        self._thread.start()
        self.console.print(
            "[green]Intent monitoring enabled "
            f"(todo2code/{self.config.runner}, {self.config.mode})[/green]"
        )

    def stop(self) -> None:
        """Signal the daemon worker to stop."""
        self._stop.set()
        self._wake.set()

    def request_run(self) -> None:
        """Request a debounced audit after a file change."""
        if not self.config.enabled or not self.config.run_on_change:
            return
        self._last_change = time.monotonic()
        self._wake.set()

    def _loop(self) -> None:
        if self.config.run_on_start:
            self.run_once()

        interval = self.config.interval_s
        while not self._stop.is_set():
            triggered = self._wake.wait(interval if interval > 0 else None)
            self._wake.clear()
            if self._stop.is_set():
                return
            if triggered:
                self._wait_for_debounce()
                if self._stop.is_set():
                    return
            self.run_once()

    def _wait_for_debounce(self) -> None:
        while True:
            remaining = self.config.debounce_s - (time.monotonic() - self._last_change)
            if remaining <= 0:
                return
            self._wake.wait(remaining)
            self._wake.clear()
            if self._stop.is_set():
                return

    def run_once(self) -> IntentAuditResult:
        """Execute one audit and publish a normalized health result."""
        if not self._run_lock.acquire(blocking=False):
            return self.last_result or IntentAuditResult(
                status="degraded", message="todo2code audit already running"
            )
        try:
            self.console.print("[cyan]⟳ todo2code Intent-vs-Reality audit[/cyan]")
            try:
                payload = self._run_pipeline()
                result = self._result_from_payload(payload)
            except Exception as exc:  # noqa: BLE001
                result = IntentAuditResult(
                    status="down",
                    message=f"todo2code audit failed: {exc}",
                    error=str(exc),
                )
            self.last_result = result
            self.on_result(result)
            return result
        finally:
            self._run_lock.release()

    def _run_pipeline(self) -> Dict:
        runner = self.config.runner.strip().lower()
        if runner == "python":
            return self._run_python_pipeline()
        if runner != "cli":
            raise ValueError(f"Unsupported todo2code runner: {self.config.runner}")
        return self._run_cli_pipeline()

    def _run_cli_pipeline(self) -> Dict:
        command = [*self._resolved_cli_command(), *self._pipeline_arguments()]

        completed = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=self.config.timeout_s,
            check=False,
            env=self._subprocess_environment(),
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(detail or f"exit code {completed.returncode}")
        if not completed.stdout.strip():
            raise ValueError("todo2code pipeline returned no JSON output")
        payload = json.loads(completed.stdout)
        if not isinstance(payload, dict):
            raise ValueError("todo2code pipeline returned non-object JSON")
        return payload

    def _subprocess_environment(self) -> dict[str, str]:
        """Build a project-local environment without mutating ``os.environ``.

        This keeps concurrent project watchers isolated while allowing the
        todo2code CLI to receive model selection and an external env-file path
        from ``.wup.env``. Explicit process variables retain precedence.
        """
        environment = _read_dotenv(self.project_root)
        environment.update(os.environ)
        return environment

    def _resolved_cli_command(self) -> List[str]:
        """Resolve a one-part JavaScript launcher to a direct Node invocation.

        npm commonly exposes package binaries as symlinks. Some JavaScript CLIs
        compare ``import.meta.url`` with the unresolved ``argv[1]`` and then do
        nothing when entered through such a link. Calling the resolved script
        through Node preserves the normal behaviour while leaving native and
        explicitly multi-part commands untouched.
        """
        command = list(self.config.command)
        if len(command) != 1:
            return command
        executable = shutil.which(command[0])
        if not executable:
            return command
        resolved = Path(executable).resolve()
        if resolved.suffix.lower() in {".js", ".mjs", ".cjs"}:
            return ["node", str(resolved)]
        return command

    def _run_python_pipeline(self) -> Dict:
        try:
            from todo2code import TypeScriptRuntime
        except ImportError as exc:
            raise RuntimeError(
                "todo2code-sdk is not installed; install sdk/python or use runner: cli"
            ) from exc

        runtime = TypeScriptRuntime(
            self.project_root,
            cli_path=self.config.cli_path or None,
            timeout=float(self.config.timeout_s),
        )
        # The SDK's TypeScriptRuntime.pipeline convenience method did not pass
        # communication/task-mode flags in todo2code-sdk 0.5.1. Use its public
        # invoke bridge so Python and CLI runners execute the exact same safe,
        # explicit command without an accidental LLM requirement.
        completed = runtime.invoke(self._pipeline_arguments())
        payload = json.loads(completed.stdout)
        if not isinstance(payload, dict):
            raise ValueError("todo2code Python runtime returned non-object JSON")
        return payload

    def _pipeline_arguments(self) -> List[str]:
        arguments = ["pipeline", str(self.project_root)]
        arguments.extend(["--task", self.config.task_file or "none"])
        arguments.extend(["--todo", self.config.todo_file or "none"])
        arguments.extend(["--changelog", self.config.changelog_file or "none"])
        arguments.extend(["--docs", ",".join(self.config.docs)])
        arguments.extend(["--nl-mode", self._mode()])
        arguments.extend(["--markdown-mode", self._mode()])
        arguments.extend(["--task-mode", "disabled", "--no-communication"])
        if not self.config.docs_llm:
            arguments.append("--no-docs-llm")
        if not self.config.summary_llm:
            arguments.append("--no-summary-llm")
        arguments.extend(["--out", self.config.output_dir])
        return arguments

    def _mode(self) -> str:
        mode = self.config.mode.strip().lower()
        if mode not in self._VALID_MODES:
            raise ValueError(f"Unsupported todo2code mode: {self.config.mode}")
        return mode

    def _result_from_payload(self, payload: Dict) -> IntentAuditResult:
        diagnostics_path_raw = payload.get("diagnosticsPath")
        if not diagnostics_path_raw:
            raise ValueError("todo2code result does not contain diagnosticsPath")
        diagnostics_path = Path(str(diagnostics_path_raw))
        if not diagnostics_path.is_absolute():
            diagnostics_path = self.project_root / diagnostics_path
        document = json.loads(diagnostics_path.read_text(encoding="utf-8"))
        diagnostics = document if isinstance(document, list) else document.get("diagnostics", [])
        if not isinstance(diagnostics, list):
            raise ValueError("todo2code diagnostics are not a list")

        severities = {item.lower() for item in self.config.fail_severities}
        codes = set(self.config.fail_codes)
        failing = [
            item
            for item in diagnostics
            if isinstance(item, dict)
            and str(item.get("severity", "")).lower() in severities
            and (not codes or str(item.get("code", "")) in codes)
        ]
        blocking = sum(
            1 for item in failing if str(item.get("severity", "")).lower() == "blocking"
        )
        status = "down" if blocking else "degraded" if failing else "up"
        message = (
            f"todo2code found {len(failing)} intent issue(s), {blocking} blocking"
            if failing
            else "todo2code found no configured intent issues"
        )
        return IntentAuditResult(
            status=status,
            message=message,
            diagnostics_path=str(diagnostics_path),
            run_directory=str(payload.get("runDirectory", "")),
            diagnostics=failing,
        )
