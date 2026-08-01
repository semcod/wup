"""Planfile ticket sink for WUP failure signals."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

import yaml
from rich.console import Console

from .models.config import PlanfileConfig


class PlanfileReporter:
    """Create deduplicated planfile tickets for WUP-detected failures."""

    def __init__(self, project_root: Path, config: PlanfileConfig, console: Optional[Console] = None):
        self.project_root = Path(project_root)
        self.config = config
        self.console = console or Console()
        self.dedupe_path = self.project_root / config.dedupe_file

    @property
    def enabled(self) -> bool:
        return bool(self.config.enabled)

    def report_failure(
        self,
        *,
        service: str,
        status: str,
        stage: str,
        message: str,
        track_file: str = "",
    ) -> Optional[str]:
        """Create a ticket for a failure transition, returning its id when created."""
        if not self.enabled:
            return None

        fingerprint = self._fingerprint(service=service, status=status, stage=stage, message=message)
        dedupe = self._load_dedupe()
        existing = dedupe.get(fingerprint)
        if existing:
            # A registry entry only mutes the recurrence while its ticket is
            # still open — a regression after the ticket was closed (done or
            # canceled) must file a fresh ticket, otherwise the failure is
            # silently invisible forever (stale entries survive watcher
            # restarts, so clear_service_stage alone does not cover this).
            existing_id = existing.get("ticket_id")
            if existing_id and not self._ticket_is_closed(existing_id):
                return existing_id

        name = self._ticket_name(service=service, stage=stage, status=status)
        description = self._ticket_description(
            service=service,
            status=status,
            stage=stage,
            message=message,
            track_file=track_file,
        )
        result = self._create_ticket(name=name, description=description, track_file=track_file)
        if result is None:
            return None

        ticket_id, stdout = result
        dedupe[fingerprint] = {
            "ticket_id": ticket_id,
            "service": service,
            "status": status,
            "stage": stage,
            "track_file": track_file,
            "stdout": stdout,
        }
        self._save_dedupe(dedupe)
        self.console.print(f"[yellow]🧾 WUP created planfile ticket {ticket_id}: {name}[/yellow]")
        return ticket_id

    def _ticket_is_closed(self, ticket_id: str) -> bool:
        """True when the deduped ticket is done/canceled (regression may re-file).

        Conservative on any error (planfile missing, ticket gone, bad JSON):
        treat the ticket as still open so dedupe keeps muting — a wrong True
        would spam duplicate tickets, a wrong False only delays a re-file.
        """
        try:
            result = subprocess.run(
                [self.config.command, "ticket", "show", ticket_id, "--format", "json"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        if result.returncode != 0:
            return False
        try:
            payload = json.loads(result.stdout or "{}")
        except ValueError:
            return False
        ticket = payload.get("ticket", payload) if isinstance(payload, dict) else {}
        return str(ticket.get("status", "")).strip().lower() in {"done", "canceled", "cancelled"}

    def clear_service_stage(self, *, service: str, stage: str) -> None:
        """Allow a future recurrence to create a fresh ticket after recovery."""
        if not self.enabled or not self.dedupe_path.exists():
            return
        dedupe = self._load_dedupe()
        remaining = {
            key: value for key, value in dedupe.items()
            if value.get("service") != service or value.get("stage") != stage
        }
        if len(remaining) == len(dedupe):
            return
        self._save_dedupe(remaining)

    def _build_ticket_cmd(self, name: str, description: str, track_file: str) -> list[str]:
        """Assemble the `planfile ticket create` argv."""
        cmd = [
            self.config.command,
            "ticket",
            "create",
            name,
            "--priority",
            self.config.priority,
            "--sprint",
            self.config.sprint,
            "--source",
            self.config.source,
            "--description",
            description,
        ]
        for label in self.config.labels:
            cmd.extend(["--label", label])
        # Koru treats Planfile ``files`` as the agent's allowed edit scope.
        # WUP runtime evidence under .wup/.intent is not source code and must
        # remain a description link rather than constraining the agent to edit
        # diagnostics.json or a generated track file.
        if track_file and not self._is_runtime_artifact(track_file):
            cmd.extend(["--files", track_file])
        return cmd

    def _is_runtime_artifact(self, track_file: str) -> bool:
        path = Path(track_file)
        if path.is_absolute():
            try:
                path = path.resolve().relative_to(self.project_root.resolve())
            except ValueError:
                return False
        return bool(path.parts and path.parts[0] in {".wup", ".intent"})

    def _run_planfile(self, cmd: list[str]) -> Optional[tuple[int, str, str]]:
        """Run a planfile command; return (returncode, stdout, stderr) or None on OS/timeout error."""
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.console.print(f"[yellow]planfile ticket creation skipped: {exc} (cmd: {cmd[0]})[/yellow]")
            return None
        return result.returncode, (result.stdout or "").strip(), (result.stderr or "").strip()

    def _retry_without_files(self, cmd: list[str]) -> Optional[tuple[int, str, str]]:
        """Re-run a ticket command with the `--files <val>` option stripped."""
        stripped = [
            part
            for index, part in enumerate(cmd)
            if not (part == "--files" or (index > 0 and cmd[index - 1] == "--files"))
        ]
        return self._run_planfile(stripped)

    def _create_ticket(self, *, name: str, description: str, track_file: str = "") -> Optional[tuple[str, str]]:
        if not self._wait_for_planfile_store_ready():
            return None

        cmd = self._build_ticket_cmd(name, description, track_file)
        outcome = self._run_planfile(cmd)
        if outcome is None:
            return None
        returncode, stdout, stderr = outcome

        # Older planfile builds reject --files; retry once without it.
        if returncode != 0 and track_file and self._files_option_unsupported(stderr or stdout):
            outcome = self._retry_without_files(cmd)
            if outcome is None:
                return None
            returncode, stdout, stderr = outcome

        if returncode != 0:
            detail = stderr or stdout or f"rc={returncode}"
            self.console.print(f"[yellow]planfile ticket creation failed: {detail}[/yellow]")
            return None

        if not self._wait_for_planfile_store_ready(timeout_s=10.0):
            self.console.print("[yellow]planfile ticket created, but sprint YAML did not become readable[/yellow]")
            return None

        ticket_id = self._parse_ticket_id(stdout) or self._parse_ticket_id(stderr) or "unknown"
        return ticket_id, stdout

    def _wait_for_planfile_store_ready(self, timeout_s: float = 30.0) -> bool:
        """Wait until the current sprint YAML is readable and not mid-write."""
        sprint_path = self.project_root / ".planfile" / "sprints" / f"{self.config.sprint}.yaml"
        if not sprint_path.exists():
            return True

        deadline = time.time() + timeout_s
        last_signature: tuple[int, int] | None = None
        while time.time() < deadline:
            try:
                stat = sprint_path.stat()
                signature = (stat.st_size, stat.st_mtime_ns)
                yaml.safe_load(sprint_path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError):
                time.sleep(0.25)
                last_signature = None
                continue

            if signature == last_signature:
                return True
            last_signature = signature
            time.sleep(0.25)

        self.console.print(
            f"[yellow]planfile ticket creation skipped: {sprint_path} is not stable/readable[/yellow]"
        )
        return False

    def _load_dedupe(self) -> dict[str, dict[str, Any]]:
        if not self.dedupe_path.exists():
            return {}
        try:
            payload = json.loads(self.dedupe_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _save_dedupe(self, payload: dict[str, dict[str, Any]]) -> None:
        self.dedupe_path.parent.mkdir(parents=True, exist_ok=True)
        self.dedupe_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    @staticmethod
    def _fingerprint(*, service: str, status: str, stage: str, message: str) -> str:
        normalized_message = " ".join(message.split())[:500]
        raw = "\0".join([service, status, stage, normalized_message])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _parse_ticket_id(text: str) -> Optional[str]:
        # Planfile projects choose their own ticket prefix (for example PLF,
        # STARTER or API). Do not hard-code the default prefix: otherwise the
        # ticket is created successfully but WUP persists it as ``unknown`` and
        # can no longer inspect its lifecycle for recurrence deduplication.
        match = re.search(r"\b[A-Z][A-Z0-9_]*-\d+\b", text, re.IGNORECASE)
        return match.group(0) if match else None

    @staticmethod
    def _files_option_unsupported(text: str) -> bool:
        lowered = text.lower()
        return "--files" in lowered and ("no such option" in lowered or "unknown option" in lowered)

    @staticmethod
    def _ticket_name(*, service: str, stage: str, status: str) -> str:
        return f"[AUTO-DIAG] wup-{service} {stage} {status}"

    @staticmethod
    def _ticket_description(*, service: str, status: str, stage: str, message: str, track_file: str) -> str:
        track_line = f"\nTrack file: `{track_file}`" if track_file else ""
        return (
            f"WUP detected a `{status}` state for service `{service}` during `{stage}`.\n\n"
            f"Failure summary:\n{message[:4000] or 'No diagnostic message was provided.'}"
            f"{track_line}\n\n"
            "Investigate and fix the failing probe, TestQL scenario, visual diff, or stale diagnostic gate. "
            "After the fix, rerun the relevant WUP/TestQL check and mark this Planfile ticket done."
        )
