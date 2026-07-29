"""Minimal console bootstrap with a crash-safe watcher dependency preflight."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence

_WATCH_PREFLIGHT = """
try:
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
except (ImportError, OSError, ValueError):
    pass
import ctypes
from watchdog.observers import Observer
assert Observer
"""


def _watchdog_preflight() -> tuple[bool, str]:
    """Probe native/stdlib imports in a child so a segfault is reportable."""
    try:
        completed = subprocess.run(
            [sys.executable, "-c", _WATCH_PREFLIGHT],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if completed.returncode == 0:
        return True, ""
    if completed.returncode < 0:
        detail = f"child terminated by signal {-completed.returncode}"
    else:
        detail = completed.stderr.strip() or f"child exited with {completed.returncode}"
    return False, detail


def main(argv: Sequence[str] | None = None) -> int | None:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "watch" and not os.environ.get("WUP_SKIP_RUNTIME_PREFLIGHT"):
        ok, detail = _watchdog_preflight()
        if not ok:
            print(
                "WUP cannot start the file watcher because this Python environment "
                "failed its ctypes/watchdog ABI preflight. Recreate the virtualenv "
                f"with one interpreter ({sys.executable}). Details: {detail}",
                file=sys.stderr,
            )
            return 70

    from .cli import app

    app(args=args, prog_name="wup")
    return None
